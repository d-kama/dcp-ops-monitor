# DCP Ops Monitor

確定拠出年金の運用状況を自動監視するシステム。平日に Web ページをスクレイピングして資産情報を収集し、週次で LINE に通知する。

## Language

### スクレイピング

**Asset Fetcher**:
スクレイピングドライバーの Application 層抽象。`open_start_page` / `login` / `navigate_to_asset_page` / `extract` / `logout` / `close` の各スクレイピングステップを公開する。Selenium 等の具体的な実装知識を持たない。
_Avoid_: スクレイパー、クローラー

**スクレイピングステップ**:
スクレイピングシーケンスを構成する 1 フェーズ（open_start_page / login / navigate_to_asset_page / extract のいずれか）。各ステップは独立して失敗でき、失敗時には Application 層が個別にエラーアーティファクトを記録する。
_Avoid_: フェーズ、プロセス

**エラーアーティファクト**:
スクレイピングステップが失敗した瞬間に取得するスクリーンショット（PNG）またはページソース（HTML）。障害後の診断用に S3 へ保存される。
_Avoid_: エラーログ、デバッグデータ

### 資産情報

**Financial Asset**:
1 商品・1 基準日の資産評価情報（拠出金額累計・評価損益・資産評価額）。
_Avoid_: 資産レコード、運用商品情報

**Financial Asset History**:
同一基準日における複数商品の Financial Asset の集合。
_Avoid_: 資産一覧、資産データ
