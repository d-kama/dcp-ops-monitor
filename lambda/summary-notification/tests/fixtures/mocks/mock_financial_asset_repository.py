from src.domain import AssetRetrievalFailed, FinancialAssetHistory, IFinancialAssetRepository


class MockFinancialAssetRepository(IFinancialAssetRepository):
    """IFinancialAssetRepository の Mock 実装（テスト用）"""

    def __init__(
        self,
        history: FinancialAssetHistory | None = None,
        should_fail: bool = False,
    ) -> None:
        self.history = history if history is not None else FinancialAssetHistory(assets=[])
        self.should_fail = should_fail
        self.retrieve_called = False
        self.last_days_arg: int | None = None

    def save_daily(self, history: FinancialAssetHistory) -> None:
        raise NotImplementedError("summary-notification は書き込みをサポートしません")

    def retrieve_from_with_days(self, days: int) -> FinancialAssetHistory:
        self.retrieve_called = True
        self.last_days_arg = days
        if self.should_fail:
            raise AssetRetrievalFailed.during_fetching()
        return self.history
