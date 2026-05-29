from collections import defaultdict
from datetime import date

from pydantic import BaseModel, ConfigDict


class CumulativeContributions(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int


class GainsOrLosses(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int


class AssetValuation(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int


class FinancialAsset(BaseModel):
    product_name: str
    base_date: date
    cumulative_contributions: CumulativeContributions
    gains_or_losses: GainsOrLosses
    asset_valuation: AssetValuation


class FinancialAssetHistory(BaseModel):
    assets: list[FinancialAsset]

    def asset_valuation_by_date(self) -> dict[date, AssetValuation]:
        totals: defaultdict[date, int] = defaultdict(int)
        for asset in self.assets:
            totals[asset.base_date] += asset.asset_valuation.value
        return {d: AssetValuation(value=v) for d, v in totals.items()}
