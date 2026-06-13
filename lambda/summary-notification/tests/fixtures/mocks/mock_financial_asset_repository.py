from datetime import date

from src.domain import AssetRetrievalError, FinancialAssetHistory, IFinancialAssetRepository


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
        self.last_base_date_arg: date | None = None

    def save_daily(self, history: FinancialAssetHistory) -> None:
        raise NotImplementedError("summary-notification は書き込みをサポートしません")

    def retrieve_within_days(self, days: int, base_date: date) -> FinancialAssetHistory:
        self.retrieve_called = True
        self.last_days_arg = days
        self.last_base_date_arg = base_date
        if self.should_fail:
            raise AssetRetrievalError("資産情報の取得中にエラーが発生しました")
        return self.history
