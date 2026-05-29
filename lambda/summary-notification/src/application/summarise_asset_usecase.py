from datetime import date

from pydantic import BaseModel
from shared.domain.financial_asset import AssetValuation, DailyAssetTotal, FinancialAssetHistory

from src.domain import AssetRetrievalFailed


class AssetSummary(BaseModel):
    """SummariseAssetUseCase の実行結果"""

    latest_day_total: DailyAssetTotal
    valuations_by_date: dict[date, AssetValuation]


class SummariseAssetUseCase:
    def summarise(self, history: FinancialAssetHistory) -> AssetSummary:
        if not history.assets:
            raise AssetRetrievalFailed.no_assets_in_spreadsheet()

        return AssetSummary(
            latest_day_total=history.sum_latest_day(),
            valuations_by_date=history.asset_valuation_by_date(),
        )
