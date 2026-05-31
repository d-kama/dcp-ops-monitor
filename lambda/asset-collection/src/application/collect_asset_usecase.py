from shared.domain.financial_asset import FinancialAssetHistory

from .asset_fetcher_interface import IAssetFetcher


class CollectAssetUseCase:
    def __init__(
        self,
        fetcher: IAssetFetcher,
    ) -> None:
        self.fetcher: IAssetFetcher = fetcher

    def execute(self) -> FinancialAssetHistory:
        return self.fetcher.fetch_asset_valuation()
