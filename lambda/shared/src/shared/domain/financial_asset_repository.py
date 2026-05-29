from abc import ABC, abstractmethod

from shared.domain.financial_asset import FinancialAssetHistory


class IFinancialAssetRepository(ABC):
    """金融資産リポジトリ"""

    @abstractmethod
    def save_daily(self, history: FinancialAssetHistory) -> None:
        """1日分の金融資産履歴を保存する

        冪等性を保証する。同一日付のレコードが既に存在する場合は
        既存レコードを削除してから保存する（upsert セマンティクス）。

        Raises:
            AssetRecordError: レコード保存失敗時
        """
