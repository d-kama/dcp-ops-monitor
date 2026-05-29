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


class DailyAssetTotal(BaseModel):
    """1日分の全商品合算資産（FinancialAsset から product_name を除いた DTO）"""

    model_config = ConfigDict(frozen=True)

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

    def sum_latest_day(self) -> DailyAssetTotal:
        """最新日付の全商品資産を合算して DailyAssetTotal を返す"""
        latest_date = max(asset.base_date for asset in self.assets)
        latest_assets = [a for a in self.assets if a.base_date == latest_date]
        return DailyAssetTotal(
            base_date=latest_date,
            cumulative_contributions=CumulativeContributions(
                value=sum(a.cumulative_contributions.value for a in latest_assets)
            ),
            gains_or_losses=GainsOrLosses(value=sum(a.gains_or_losses.value for a in latest_assets)),
            asset_valuation=AssetValuation(value=sum(a.asset_valuation.value for a in latest_assets)),
        )
