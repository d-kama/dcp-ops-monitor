from abc import ABC, abstractmethod

from shared.domain.financial_asset import FinancialAssetHistory


class IFinancialAssetRepository(ABC):
    """金融資産リポジトリ"""

    @abstractmethod
    def save_daily(self, daily_assets: FinancialAssetHistory) -> None:
        """1日分の金融資産履歴を保存する

        冪等性を保証する。同一日付のレコードが既に存在する場合は
        既存レコードを削除してから保存する（upsert セマンティクス）。

        Raises:
            AssetSaveError: 保存失敗時
        """

    @abstractmethod
    def retrieve_from_with_days(self, days: int) -> FinancialAssetHistory:
        """直近 N 日分の金融資産履歴を取得する

        最新日付を基準に、(最新日 - days) より新しい日付の資産を返す。

        Args:
            days: 直近何日分を取得するか（正の整数）

        Returns:
            FinancialAssetHistory: 該当期間の金融資産履歴（空の場合は空の History を返す）

        Raises:
            ValueError: days が 0 以下の場合
            AssetRetrievalError: 取得失敗時
        """
