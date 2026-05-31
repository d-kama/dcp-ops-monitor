from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class CumulativeContributions:
    value: int


@dataclass(frozen=True)
class GainsOrLosses:
    value: int


@dataclass(frozen=True)
class AssetValuation:
    value: int


@dataclass(frozen=True)
class FinancialAsset:
    product_name: str
    base_date: date
    cumulative_contributions: CumulativeContributions
    gains_or_losses: GainsOrLosses
    asset_valuation: AssetValuation


@dataclass(frozen=True)
class LatestPortfolioTotal:
    """1日分の全商品合算資産を表す Value Object"""

    base_date: date
    cumulative_contributions: CumulativeContributions
    gains_or_losses: GainsOrLosses
    asset_valuation: AssetValuation


@dataclass(frozen=True)
class FinancialAssetHistory:
    assets: list[FinancialAsset] = field(default_factory=list)

    def add(self, asset: FinancialAsset) -> "FinancialAssetHistory":
        return FinancialAssetHistory(assets=[*self.assets, asset])

    def asset_valuation_by_date(self) -> dict[date, AssetValuation]:
        totals: defaultdict[date, int] = defaultdict(int)
        for asset in self.assets:
            totals[asset.base_date] += asset.asset_valuation.value
        return {d: AssetValuation(value=v) for d, v in totals.items()}

    def sum_latest_day(self) -> LatestPortfolioTotal:
        """最新日付の全商品資産を合算して LatestPortfolioTotal を返す"""
        if not self.assets:
            raise ValueError("asset is empty")

        latest_date = max(asset.base_date for asset in self.assets)
        latest_assets = [a for a in self.assets if a.base_date == latest_date]
        return LatestPortfolioTotal(
            base_date=latest_date,
            cumulative_contributions=CumulativeContributions(
                value=sum(a.cumulative_contributions.value for a in latest_assets)
            ),
            gains_or_losses=GainsOrLosses(value=sum(a.gains_or_losses.value for a in latest_assets)),
            asset_valuation=AssetValuation(value=sum(a.asset_valuation.value for a in latest_assets)),
        )
