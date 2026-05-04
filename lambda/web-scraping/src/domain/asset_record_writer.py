"""web-scraping 用 IAssetRecordWriter（write 専用）"""

from abc import ABC, abstractmethod

from shared.domain.asset_record import AssetRecord


class IAssetRecordWriter(ABC):
    """資産レコードライター（write 専用）

    web-scraping Lambda が日次の資産レコードを Spreadsheet に保存するための I/O 契約。
    read 側の責務は持たない（read は summary-notification/domain/IAssetRecordReader が担う）。
    """

    @abstractmethod
    def save_daily_records(self, records: list[AssetRecord]) -> None:
        """日次の資産レコードを保存する

        冪等性を保証する。同一日付のレコードが既に存在する場合は
        既存レコードを削除してから保存する（upsert セマンティクス）。

        Raises:
            AssetRecordError: レコード保存失敗時
        """
