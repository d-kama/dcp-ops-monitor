from pydantic import BaseModel


class ScrapingParameters(BaseModel):
    """Web スクレイピング接続情報の設定 DTO

    SSM Parameter Store の値と環境変数（user_agent）から構築される。
    """

    login_user_id: str
    login_password: str
    login_birthdate: str

    start_url: str
    user_agent: str
