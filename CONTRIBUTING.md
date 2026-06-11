# CONTRIBUTING.md

## セットアップ

### devpod + Zed SSH 接続を使う場合（推奨）

devpod（プロバイダー: docker）でワークスペースを作成し、Zed の「Connect SSH Server」機能で接続する運用を想定しています。

#### 初回セットアップ

1. ホストで Docker を起動した状態で、リポジトリルートで devpod ワークスペースを作成

   ```bash
   devpod up . --ide none
   ```

   コンテナ作成時に `.devcontainer/devcontainer.json` の `postCreateCommand` が実行され、依存関係のインストールまで自動で行われます。

2. Zed の「Connect SSH Server」で devpod が払い出した SSH ホスト（`<workspace>.devpod`）に接続

3. コンテナ内ターミナルで GitHub 認証

   コンテナ権限を絞った Fine-grained PAT で認証します。デバイスフロー（`gh auth login -w`）はアカウント全体に対する広い OAuth スコープを取得するため使用しません。

   1. GitHub Web で Fine-grained PAT を発行
      - Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token
      - Repository access: **Only select repositories** → `d-kama/dcp-ops-monitor`
      - Repository permissions:
        - Contents: Read and write（`git push` / `git pull`）
        - Pull requests: Read and write（`gh pr create` 等）
        - Issues: Read and write（`gh issue` 等）
        - Metadata: Read-only（必須）
        - Workflows: Read and write（`.github/workflows/*` を変更する場合のみ）
      - Expiration: 90 日推奨

   2. 認証コマンドを実行

      ```bash
      gh auth login -h github.com -p https --with-token   # プロンプトに PAT を貼り付け → Ctrl+D
      gh auth setup-git                                    # git の credential helper として gh を登録
      ```

   認証情報は named volume (`dcp-gh-config`) に保存されるため、コンテナを作り直しても保持されます。PAT の期限切れ時は再発行して同じコマンドで上書き認証してください。

#### 2 回目以降

1. ホストで Docker を起動
2. Zed の「Connect SSH Server」で接続

   devpod ワークスペースが自動起動し、依存関係・認証情報は保持されています。`postCreateCommand` はコンテナ作成時のみ実行されるため再度走りません。

### ホストに直接セットアップする場合

```bash
# ツールインストール
mise trust && mise install

# Node 依存関係 + pre-commit フック
npm ci && npx lefthook install

# Python 依存関係（uv workspace）
uv sync --directory lambda

# 環境変数（Docker Compose 用）
cp .env.example .env.local
```

CDK 初回ブートストラップ（初回のみ）: `cdk bootstrap aws://ACCOUNT-NUMBER/REGION`

---

## 開発コマンド

### Lint / Format

```bash
npm run lint          # TypeScript + Python lint（auto-fix）
npm run lint:ci       # lint（fix なし、CI 用）
npm run format        # TypeScript + Python format（auto-fix）
npm run format:ci     # format（check only、CI 用）
```

### 型チェック

```bash
npm run type-check 
```

### テスト

```bash
# CDK スナップショットテスト
npm run test:cdk

# Lambda テスト（全体）
npm run test:asset-collection
npm run test:summary-notification

# Lambda テスト（単一ファイル）
cd lambda/asset-collection && ENV=test uv run pytest tests/domain/test_asset_record_object.py -v
cd lambda/summary-notification && ENV=test uv run pytest tests/domain/test_asset_object.py -v

# Lambda テスト（単一関数）
cd lambda/asset-collection && ENV=test uv run pytest tests/domain/test_asset_record_object.py::test_function_name -v
```

---

## asset-collection

### ECR ライフサイクルポリシー

この Lambda は Docker イメージを使用しており、デプロイのたびに CDK ブートストラップ用の ECR リポジトリにイメージがプッシュされます。コスト削減のため、初回セットアップ時に保持イメージを 1 つに制限するポリシーを設定します。

```bash
aws ecr put-lifecycle-policy \
  --repository-name cdk-hnb659fds-container-assets-{ACCOUNT_ID}-{REGION} \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": { "type": "expire" }
    }]
  }'
```

> `cdk bootstrap` を再実行するとリセットされるため、再設定が必要です。

### ローカルでのスクレイピング動作確認

#### Python インタプリタから Selenium をインタラクティブに操作する

> スクレイピングの接続先は本物を使用します。

1. `selenium/standalone-chrome` を起動

```bash
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome:latest
```

2. http://localhost:7900 にブラウザで接続（パスワード: `secret`）

3. Python インタプリタから操作

```python
import os
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), ".env.local"))
options = webdriver.ChromeOptions()
options.add_argument(f'--user-agent={os.environ["USER_AGENT"]}')
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=options)
driver.get(os.environ["START_URL"])
# localhost:7900 でブラウザが操作されていることを確認

driver.quit()  # 終了時
```

#### Docker Compose で Lambda コンテナを実行する

> Lambda コンテナでスクレイピングが正常に動作するか確認します。AWS リソースは LocalStack を使用し、スクレイピング先は本物を使用します。

1. `.env.local` の `ASSET_FETCH_CONFIG_PARAMETER_VALUE` に実際の認証情報を入力

2. コンテナを起動

```bash
docker compose up -d --build
```

   LocalStack 起動時に `localstack/ready.sh` が S3 バケットと SSM パラメータを自動作成する（`.env.local` の値を使用）。

3. Lambda を呼び出す

```bash
curl -d "{}" http://localhost:8080/2015-03-31/functions/function/invocations
```

4. 終了

```bash
docker compose down
```
