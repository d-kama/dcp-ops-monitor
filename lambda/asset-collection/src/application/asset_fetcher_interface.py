from abc import ABC, abstractmethod

from shared.domain.financial_asset import FinancialAssetHistory


class IAssetFetcher(ABC):
    """スクレイピングドライバー抽象クラス"""

    @abstractmethod
    def fetch_asset_valuation(self) -> FinancialAssetHistory:
        """資産評価情報を取得するメソッド

        ページ遷移（ログイン → 資産評価ページ → ログアウト）と
        要素抽出を一括で行う。

        Returns:
            FinancialAssetHistory: 商品別の資産評価情報

        Raises:
            ScrapingFailed: スクレイピングまたは資産情報抽出に失敗した場合
        """
        pass
