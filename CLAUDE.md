# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 環境

- パッケージマネージャー: [mise](https://mise.jdx.dev/installing-mise.html)

## セットアップ

セットアップ手順は [CONTRIBUTING.md](CONTRIBUTING.md#セットアップ) を参照。

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
npm run type-check    # asset-collection の型チェック（summary-notification は未対応）
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

### ローカル実行（Docker Compose）

asset-collection Lambda を LocalStack と組み合わせて動かす:

```bash
docker compose up          # LocalStack + asset-collection コンテナ起動
docker compose up --build  # イメージ再ビルドして起動
```

LocalStack 起動時に `localstack/ready.sh` が S3 バケットと SSM パラメータを自動作成する（`.env.local` の値を使用）。

## ドキュメント管理

基本設計を記述し、大きな設計変更時のみ更新する。

| ファイル | 内容 |
|---------|------|
| @CONTEXT.md | ドメイン用語集（正式名称・避けるべき表現） |
| @ARCHITECTURE.md | アーキテクチャ概要（概要、コードマップ、不変条件） |
| @CONTRIBUTING.md | セットアップ手順・Lambda アーキテクチャ方針・shared の背景・asset-collection のローカル検証手順 |
