"""テスト用 Mock IAssetRecordReader"""

from src.domain import AssetRecord, AssetRetrievalFailed, IAssetRecordReader


class MockAssetRecordReader(IAssetRecordReader):
    """summary-notification 用 Mock IAssetRecordReader

    get_latest_records / get_records_within_days の呼び出しを記録し、テストで検証可能にする。
    """

    def __init__(
        self,
        latest_records: list[AssetRecord] | None = None,
        weekly_records: list[AssetRecord] | None = None,
        should_fail: bool = False,
    ) -> None:
        self.latest_records = latest_records if latest_records is not None else []
        self.weekly_records = weekly_records or []
        self.should_fail = should_fail
        self.get_latest_called = False
        self.get_weekly_called = False
        self.last_days_arg: int | None = None

    def get_latest_records(self) -> list[AssetRecord]:
        self.get_latest_called = True
        if self.should_fail:
            raise AssetRetrievalFailed.during_fetching()
        return self.latest_records

    def get_records_within_days(self, days: int) -> list[AssetRecord]:
        self.get_weekly_called = True
        self.last_days_arg = days
        if self.should_fail:
            raise AssetRetrievalFailed.during_fetching()
        return self.weekly_records
