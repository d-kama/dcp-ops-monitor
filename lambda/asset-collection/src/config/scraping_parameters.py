from pydantic import BaseModel, SecretStr


class ScrapingParameters(BaseModel):
    """Web スクレイピング接続情報の設定 DTO

    SSM Parameter Store の値と環境変数（user_agent）から構築される。
    認証情報フィールドは SecretStr で保持し、平文化は明示的な
    .get_secret_value() 呼び出しに限定する。
    """

    login_user_id: SecretStr
    login_password: SecretStr
    login_birthdate: SecretStr

    start_url: str
    user_agent: str
