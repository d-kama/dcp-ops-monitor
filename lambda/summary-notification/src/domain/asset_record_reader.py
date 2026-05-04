"""summary-notification 用 IAssetRecordReader（read 専用）"""

from abc import ABC, abstractmethod

from shared.domain.asset_record import AssetRecord


class IAssetRecordReader(ABC):
    """資産レコードリーダ（read 専用）

    summary-notification Lambda が Spreadsheet から AssetRecord を読み取るための I/O 契約。
    write 側の責務は持たない（write は web-scraping/domain/IAssetRecordWriter が担う）。
    """

    @abstractmethod
    def get_latest_records(self) -> list[AssetRecord]:
        """シート内最新日付の資産レコードを取得する

        実装は API 効率のため、最新日付の特定後に該当行のみを batch_get する。
        全件取得後にクライアント側でフィルタする実装は禁止。

        Returns:
            list[AssetRecord]: 最新日付の資産レコード（商品ごとに 1 件）。
                              シートが空の場合は空リストを返す（呼び出し側で空判定し例外送出する責務）。

        Raises:
            AssetRetrievalFailed: 取得中に下位エラー（gspread 例外など）が発生した場合
        """

    @abstractmethod
    def get_records_within_days(self, days: int) -> list[AssetRecord]:
        """直近 N 日分の資産レコードを取得する

        最新日付を基準に、(最新日 - days) より新しい日付のレコードを返す。
        実装は API 効率のため、対象日付の特定後に該当行のみを batch_get する。

        Args:
            days: 直近何日分を取得するか（正の整数）

        Returns:
            list[AssetRecord]: 該当期間の資産レコード（日付順は保証しない、呼び出し側で必要ならソート）。
                              シートが空の場合は空リストを返す。

        Raises:
            AssetRetrievalFailed: 取得中に下位エラーが発生した場合
            ValueError: days が 0 以下の場合
        """
