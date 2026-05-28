from datetime import date, timedelta

from pydantic import BaseModel
from shared.domain.asset_evaluation import AssetEvaluation

OPERATION_START_DATE = date(2016, 10, 1)
RETIREMENT_DATE = date(2046, 10, 1)
ANNUAL_CONTRIBUTION = 240_000


class OpsIndicators(BaseModel):
    """運用指標を扱う値クラス

    Attributes:
        operation_years (float): 運用年数
        actual_yield_rate (float): 運用利回り
        total_amount_at_60age (int): 想定受取額（60歳）
    """

    operation_years: float
    actual_yield_rate: float
    total_amount_at_60age: int

    @classmethod
    def from_asset_evaluation(cls, total_assets: AssetEvaluation, today: date | None = None) -> "OpsIndicators":
        """資産情報から運用指標を生成する"""
        if today is None:
            today = date.today()

        operation_years = cls._calculate_year_diff(start_dt=OPERATION_START_DATE, end_dt=today)
        actual_yield_rate = cls._calculate_annual_yield_rate(
            cumulative_contributions=total_assets.cumulative_contributions,
            gains_or_losses=total_assets.gains_or_losses,
            operation_years=operation_years,
        )
        total_amount_at_60age = cls._calculate_total_amount_at_60age(
            yield_rate=actual_yield_rate,
            asset_valuation=total_assets.asset_valuation,
            today=today,
        )
        return cls(
            operation_years=operation_years,
            actual_yield_rate=actual_yield_rate,
            total_amount_at_60age=total_amount_at_60age,
        )

    @staticmethod
    def _calculate_year_diff(start_dt: date, end_dt: date) -> float:
        return round((end_dt - start_dt) / timedelta(days=365), 2)

    @staticmethod
    def _calculate_annual_yield_rate(
        cumulative_contributions: int,
        gains_or_losses: int,
        operation_years: float,
    ) -> float:
        if cumulative_contributions <= 0 or operation_years <= 0:
            return 0.0
        return round(gains_or_losses / cumulative_contributions / operation_years, 3)

    @staticmethod
    def _calculate_total_amount_at_60age(
        yield_rate: float,
        asset_valuation: int,
        today: date,
    ) -> int:
        years_to_60age = OpsIndicators._calculate_year_diff(start_dt=today, end_dt=RETIREMENT_DATE)
        if years_to_60age <= 0:
            return asset_valuation
        if yield_rate == 0:
            future_contributions = ANNUAL_CONTRIBUTION * years_to_60age
        else:
            future_contributions = ANNUAL_CONTRIBUTION * (((1 + yield_rate) ** years_to_60age - 1) / yield_rate)
        return int(future_contributions) + asset_valuation
