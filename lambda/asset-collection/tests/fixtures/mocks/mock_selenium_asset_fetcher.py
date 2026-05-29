from src.application import IAssetFetcher
from src.domain import FinancialAssetHistory, ScrapingFailed


class MockSeleniumAssetFetcher(IAssetFetcher):
    """Selenium WebDriver の Mock 実装（テスト用）

    実際にブラウザを起動せず、事前に用意した金融資産履歴を返す Mock オブジェクト
    """

    def __init__(
        self,
        mock_history: FinancialAssetHistory | None = None,
        should_fail: bool = False,
        should_fail_extraction: bool = False,
    ) -> None:
        self.mock_history = mock_history
        self.should_fail = should_fail
        self.should_fail_extraction = should_fail_extraction
        self.fetch_called = False

    def fetch_asset_valuation(self) -> FinancialAssetHistory:
        self.fetch_called = True

        if self.should_fail:
            screenshot_path = "/tmp/mock_error.png"
            with open(screenshot_path, "wb") as f:
                f.write(b"Mock error image content")
            print("[Mock] Scraping failed (simulated)")
            raise ScrapingFailed.during_login(tmp_screenshot_path=screenshot_path)

        if self.should_fail_extraction:
            html_path = "/tmp/mock_error_extraction.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("<html>invalid</html>")
            print("[Mock] Extraction failed (simulated)")
            raise ScrapingFailed.during_extraction(tmp_html_path=html_path)

        if self.mock_history is None:
            msg = "mock_history must be provided when should_fail=False and should_fail_extraction=False"
            raise ValueError(msg)

        print(f"[Mock] Scraping succeeded (products={len(self.mock_history.assets)})")
        return self.mock_history
