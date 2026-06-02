from functools import lru_cache

from shared.config.base_settings import BaseEnvSettings


class EnvSettings(BaseEnvSettings):
    """サマリ通知関数の設定"""

    # Systems Manager Parameter Store のパラメータ名
    line_message_parameter_name: str
    spreadsheet_parameter_name: str


@lru_cache()
def get_settings() -> EnvSettings:
    return EnvSettings()  # type: ignore[call-arg]
