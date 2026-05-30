from src.application import AssetFetchFailed, IAssetFetcher
from src.domain import FinancialAssetHistory


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
            print("[Mock] Scraping failed (simulated)")
            raise AssetFetchFailed("ログイン処理に失敗しました")

        if self.should_fail_extraction:
            print("[Mock] Extraction failed (simulated)")
            raise AssetFetchFailed("資産情報の抽出に失敗しました")

        if self.mock_history is None:
            msg = "mock_history must be provided when should_fail=False and should_fail_extraction=False"
            raise ValueError(msg)

        print(f"[Mock] Scraping succeeded (products={len(self.mock_history.assets)})")
        return self.mock_history
