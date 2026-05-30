from src.domain import FinancialAssetHistory, IFinancialAssetRepository


class MockFinancialAssetRepository(IFinancialAssetRepository):
    """IFinancialAssetRepository の Mock 実装（テスト用）"""

    def __init__(self) -> None:
        self.saved_history: FinancialAssetHistory | None = None

    def save_daily(self, history: FinancialAssetHistory) -> None:
        self.saved_history = history

    def retrieve_from_with_days(self, days: int) -> FinancialAssetHistory:
        raise NotImplementedError("asset-collection は読み取りをサポートしません")
