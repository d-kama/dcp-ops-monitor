from functools import lru_cache

from shared.config.base_settings import BaseEnvSettings


class EnvSettings(BaseEnvSettings):
    """スクレイピング関数の設定"""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    # Systems Manager Parameter Store のパラメータ名
    asset_fetch_config_parameter_name: str
    spreadsheet_parameter_name: str

    # データ保存用 S3 バケット名
    data_bucket_name: str


@lru_cache()
def get_settings() -> EnvSettings:
    """環境変数の設定を取得する関数

    Returns:
        EnvSettings: 環境変数の設定
    """
    return EnvSettings()  # ty: ignore[missing-argument] # pyright: ignore[reportCallIssue]
