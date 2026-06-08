# asset-collection は Docker コンテナイメージで Lambda をデプロイする

asset-collection は Selenium で Chrome を操作するため、Chrome / ChromeDriver のバイナリと Python パッケージの依存関係を Lambda 実行環境に揃える必要がある。zip パッケージ方式ではこの依存解決が煩雑になるため、Docker コンテナイメージ方式でデプロイし、依存をイメージ内に閉じ込める。

## Considered Options

**却下: zip パッケージ方式でデプロイする** — Lambda Layer や同梱で Chrome / ChromeDriver と Selenium の依存を持ち込む形は、バイナリのバージョン整合・配置・サイズ制限の調整が煩雑で、ローカル実行環境との差異も生まれやすい。
