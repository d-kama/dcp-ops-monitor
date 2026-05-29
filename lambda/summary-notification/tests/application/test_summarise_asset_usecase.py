from datetime import date

import pytest
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    DailyAssetTotal,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)

from src.application import AssetSummary, SummariseAssetUseCase
from src.domain import AssetRetrievalFailed


def _make_asset(d: date, product: str, av: int, cc: int, gl: int) -> FinancialAsset:
    return FinancialAsset(
        base_date=d,
        product_name=product,
        asset_valuation=AssetValuation(value=av),
        cumulative_contributions=CumulativeContributions(value=cc),
        gains_or_losses=GainsOrLosses(value=gl),
    )


@pytest.fixture
def usecase() -> SummariseAssetUseCase:
    return SummariseAssetUseCase()


class TestSummariseAssetUseCase:
    def test_summarise__returns_asset_summary(self, usecase):
        """有効な履歴から AssetSummary が返る"""
        history = FinancialAssetHistory(assets=[_make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000)])

        result = usecase.summarise(history)

        assert isinstance(result, AssetSummary)

    def test_summarise__latest_day_total_aggregates_latest_date(self, usecase):
        """latest_day_total は最新日の全商品合算値を保持する"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000),
                _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000),
                _make_asset(date(2026, 1, 9), "商品A", 590_000, 500_000, 90_000),
            ]
        )

        result = usecase.summarise(history)

        assert result.latest_day_total == DailyAssetTotal(
            base_date=date(2026, 1, 10),
            asset_valuation=AssetValuation(value=1_000_000),
            cumulative_contributions=CumulativeContributions(value=850_000),
            gains_or_losses=GainsOrLosses(value=150_000),
        )

    def test_summarise__valuations_by_date_covers_all_dates(self, usecase):
        """valuations_by_date は全日付の合計資産評価額を保持する"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000),
                _make_asset(date(2026, 1, 9), "商品A", 990_000, 900_000, 90_000),
            ]
        )

        result = usecase.summarise(history)

        assert result.valuations_by_date == {
            date(2026, 1, 10): AssetValuation(value=1_000_000),
            date(2026, 1, 9): AssetValuation(value=990_000),
        }

    def test_summarise__empty_history_raises_asset_retrieval_failed(self, usecase):
        """空履歴の場合は AssetRetrievalFailed を送出する"""
        history = FinancialAssetHistory(assets=[])

        with pytest.raises(AssetRetrievalFailed):
            usecase.summarise(history)
