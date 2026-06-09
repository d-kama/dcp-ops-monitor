# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 環境

- パッケージマネージャー: [mise](https://mise.jdx.dev/installing-mise.html)

## セットアップ

セットアップ手順は [CONTRIBUTING.md](CONTRIBUTING.md#セットアップ) を参照。

## 開発コマンド

Lint / Format・型チェック・テスト・ローカル実行（Docker Compose）のコマンドは [CONTRIBUTING.md](CONTRIBUTING.md#開発コマンド) を参照。

## ドキュメント管理

基本設計を記述し、大きな設計変更時のみ更新する。

| ファイル | 内容 |
|---------|------|
| @CONTEXT.md | ドメイン用語集（正式名称・避けるべき表現） |
| @ARCHITECTURE.md | アーキテクチャ概要（概要、コードマップ、不変条件、設計判断） |
| @CONTRIBUTING.md | セットアップ手順・開発コマンド・asset-collection の運用/ローカル検証手順 |
| docs/adr/ | 個別の設計判断の記録（ADR） |
