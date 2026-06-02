# IAssetFetcher をスクレイピングステップ単位に分解し、エラー処理を Application 層に移譲する

以前の `IAssetFetcher` は `fetch_asset_valuation()` 1 メソッドですべてのステップ（ページ遷移・ログイン・抽出・ログアウト）とエラー処理（スクリーンショット取得・S3 保存・例外変換）を担っていた。これは Infrastructure 実装（`SeleniumAssetFetcher`）が `IErrorArtifactRepository` に依存することを強制し、テストと責務分離を困難にしていた。

`IAssetFetcher` をステップ単位（`open_start_page` / `login` / `navigate_to_asset_page` / `extract` / `logout` / `close`）に分解し、エラー処理の制御（アーティファクト取得・保存・例外変換）を `CollectAssetDailyUseCase`（Application 層）に移した。Infrastructure 実装は Selenium 操作のみを行い、失敗時は生の例外をそのまま raise する。これによりクリーンアーキテクチャの依存方向（`Application → Infrastructure`）が守られ、各ステップを独立してテスト可能になる。

## Considered Options

**却下: Infrastructure がエラー処理を継続する（現状維持）** — `SeleniumAssetFetcher` が `IErrorArtifactRepository` を直接保持する形は、インフラ実装に application 層の関心事（どのステップでどのアーティファクトを取るか）が混在し、ユースケースの変更に伴う修正範囲が拡大する。
