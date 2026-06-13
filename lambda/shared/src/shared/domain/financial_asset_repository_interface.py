from abc import ABC, abstractmethod
from datetime import date

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
    def retrieve_within_days(self, days: int, base_date: date) -> FinancialAssetHistory:
        """基準日から N 日以内の金融資産履歴を取得する

        (base_date - days) より後かつ base_date 以前の基準日を持つ資産を返す。
        base_date より未来の日付は含まない。

        Args:
            days: 直近何日分を取得するか（正の整数）
            base_date: 取得の基準日（通常は実行日）

        Returns:
            FinancialAssetHistory: 該当期間の金融資産履歴（空の場合は空の History を返す）

        Raises:
            ValueError: days が 0 以下の場合
            AssetRetrievalError: 取得失敗時
        """
