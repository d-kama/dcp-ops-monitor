from src.application import IAssetFetcher
from src.domain import FinancialAssetHistory


class MockAssetFetcher(IAssetFetcher):
    """IAssetFetcher の Mock 実装（テスト用）

    実際にブラウザを起動せず、事前に用意した金融資産履歴を返す Mock オブジェクト。
    fail_at を指定することで任意のステップで失敗させることができる。
    """

    def __init__(
        self,
        mock_history: FinancialAssetHistory | None = None,
        fail_at: str | None = None,
    ) -> None:
        # fail_at: "login" | "navigate" | "extract" | None
        self.mock_history = mock_history
        self.fail_at = fail_at
        self.steps_called: list[str] = []
        self.logout_called = False
        self.close_called = False
        self.screenshot_path = "/tmp/mock_screenshot.png"
        self.page_source_path = "/tmp/mock_page_source.html"

    def open_start_page(self, url: str) -> None:
        self.steps_called.append("open_start_page")

    def login(self, config) -> None:
        self.steps_called.append("login")
        if self.fail_at == "login":
            raise Exception("mock login failed")

    def navigate_to_asset_page(self) -> None:
        self.steps_called.append("navigate_to_asset_page")
        if self.fail_at == "navigate":
            raise Exception("mock navigate failed")

    def extract(self) -> FinancialAssetHistory:
        self.steps_called.append("extract")
        if self.fail_at == "extract":
            raise Exception("mock extract failed")
        if self.mock_history is None:
            raise ValueError("mock_history must be provided")
        return self.mock_history

    def logout(self) -> None:
        self.logout_called = True

    def close(self) -> None:
        self.close_called = True

    def capture_screenshot(self) -> str:
        return self.screenshot_path

    def get_page_source(self) -> str:
        return self.page_source_path
