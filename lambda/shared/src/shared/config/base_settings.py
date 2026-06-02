from functools import lru_cache

from aws_lambda_powertools import Logger
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache()
def get_logger() -> Logger:
    """Loggerのインスタンスをキャッシュして返す関数"""
    return Logger()


class BaseEnvSettings(BaseSettings):
    """共通設定の基底クラス"""

    powertools_log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
