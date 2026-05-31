from typing import Literal

from shared.domain.financial_asset_repository import IFinancialAssetRepository

from .asset_fetcher_interface import IAssetFetcher
from .collect_asset_interface import ICollectDailyAssetUseCase


class CollectAssetDailyUseCase(ICollectDailyAssetUseCase):
    def __init__(
        self,
        fetcher: IAssetFetcher,
        repository: IFinancialAssetRepository,
    ) -> None:
        self.fetcher = fetcher
        self.repository = repository

    def execute(self) -> Literal["Success"]:
        daily_assets = self.fetcher.fetch_asset_valuation()
        self.repository.save_daily(daily_assets)
        return "Success"
