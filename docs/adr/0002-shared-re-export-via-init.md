# shared モジュールは各機能モジュールの __init__.py 経由でのみ参照する

`asset-collection` / `summary-notification` の各ファイルが `shared` パッケージを直接インポートすると、インポート経路が分散し「どこから取るか」がファイルごとにばらつく。層の `__init__.py` を唯一の窓口にすることで、`shared` への依存を一箇所で管理し、将来的なシンボルの移動・名前変更の影響範囲を限定する。

各層（`domain` / `application` / `infrastructure` / `config`）の `__init__.py` で `shared` から必要なシンボルを再エクスポートし、同一機能モジュール内の他ファイルは `from src.<layer> import ...` のみを使う。テストファイルも同規則に従う。

## Considered Options

**却下: 直接インポートを許容する（現状）** — 各ファイルが `from shared.domain.financial_asset import ...` を直接書く形は、シンボルの出所が自明でシンプルだが、`shared` の内部構造変更時に修正箇所が全ファイルに散らばる。

## 例外

`config/settings.py`（両 Lambda）は `BaseEnvSettings` を **継承**するためにインポートしている。`config/__init__.py` が `settings.py` を読み込む際に循環インポートが発生するため、`settings.py` に限り `shared.config.base_settings` からの直接インポートを許容する。
