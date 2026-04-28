#!/bin/bash
set -euo pipefail

# root ユーザーでマウントされる為、書き込み可能に権限を上書き
sudo chown -R "$(id -u):$(id -g)" \
  "$HOME/.config" \
  "$HOME/.claude"

# mise インストール
curl https://mise.run | sh

# フルパスで mise を使う
MISE="$HOME/.local/bin/mise"

# bashrc に追加
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc

# mise install もフルパスで実行
export MISE_PYTHON_GITHUB_ATTESTATIONS=false
$MISE trust && $MISE install

# mise経由でnpmが使えるようにactivate
eval "$($MISE activate bash)"

# Node 依存関係 + pre-commit フック
npm ci && npx lefthook install

# Python 依存関係（uv workspace）
uv sync --directory lambda

# 環境変数（Docker Compose 用）
[ -f .env.local ] || cp .env.example .env.local

# git が SSH 形式の URL を HTTPS にリダイレクトするよう設定
git config --global --add url."https://github.com/".insteadOf "git@github.com:"
git config --global --add url."https://github.com/".insteadOf "ssh://git@github.com/"

cat <<'EOF'
============================================================
DevContainer セットアップ完了

初回のみ Fine-grained PAT で GitHub 認証を行ってください:

  1. GitHub Web で Fine-grained PAT を発行
     - Repository access: kamaD-y/dcp-ops-monitor のみ
     - Permissions: Contents (R/W), Pull requests (R/W), Issues (R/W), Metadata (R)
                    必要に応じて Workflows (R/W)
     - Expiration: 90 日推奨

  2. コンテナ内で認証
     gh auth login -h github.com -p https --with-token
       → プロンプトに PAT を貼り付け → Ctrl+D
     gh auth setup-git

認証情報は named volume (dcp-gh-config) に保存されるため、
次回以降のコンテナ再作成では再ログイン不要です。
PAT 期限切れ時は再発行して同じコマンドで上書き認証してください。
============================================================
EOF
