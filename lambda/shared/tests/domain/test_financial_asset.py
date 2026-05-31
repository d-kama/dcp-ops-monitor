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


def _make_asset(d: date, product: str, av: int, cc: int, gl: int) -> FinancialAsset:
    return FinancialAsset(
        base_date=d,
        product_name=product,
        asset_valuation=AssetValuation(value=av),
        cumulative_contributions=CumulativeContributions(value=cc),
        gains_or_losses=GainsOrLosses(value=gl),
    )


class TestAdd:
    def test_add__empty_history_returns_single_asset(self):
        """空の履歴にassetを追加すると1件の履歴になる"""
        history = FinancialAssetHistory(assets=[])
        asset = _make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000)

        result = history.add(asset)

        assert result == FinancialAssetHistory(assets=[asset])

    def test_add__returns_new_instance(self):
        """addは元のインスタンスを変更せず新しいインスタンスを返す"""
        history = FinancialAssetHistory(assets=[])
        asset = _make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000)

        result = history.add(asset)

        assert result is not history
        assert history.assets == []

    def test_add__multiple_assets_accumulated(self):
        """addを連続して呼ぶと順序を保って蓄積される"""
        asset_a = _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000)
        asset_b = _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000)

        result = FinancialAssetHistory(assets=[]).add(asset_a).add(asset_b)

        assert result.assets == [asset_a, asset_b]


class TestSumLatestDay:
    def test_sum_latest_day__single_product_returns_same_values(self):
        """1商品のみの場合はその値をそのまま返す"""
        history = FinancialAssetHistory(assets=[_make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000)])

        result = history.sum_latest_day()

        assert result == DailyAssetTotal(
            base_date=date(2026, 1, 10),
            cumulative_contributions=CumulativeContributions(value=900_000),
            gains_or_losses=GainsOrLosses(value=100_000),
            asset_valuation=AssetValuation(value=1_000_000),
        )

    def test_sum_latest_day__multiple_products_summed(self):
        """複数商品の値が合算される"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000),
                _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000),
            ]
        )

        result = history.sum_latest_day()

        assert result.base_date == date(2026, 1, 10)
        assert result.asset_valuation == AssetValuation(value=1_000_000)
        assert result.cumulative_contributions == CumulativeContributions(value=850_000)
        assert result.gains_or_losses == GainsOrLosses(value=150_000)

    def test_sum_latest_day__only_latest_date_included(self):
        """複数日付がある場合、最新日のみが合算対象になる"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 1_000_000, 900_000, 100_000),
                _make_asset(date(2026, 1, 9), "商品A", 990_000, 900_000, 90_000),
                _make_asset(date(2026, 1, 8), "商品A", 980_000, 900_000, 80_000),
            ]
        )

        result = history.sum_latest_day()

        assert result.base_date == date(2026, 1, 10)
        assert result.asset_valuation == AssetValuation(value=1_000_000)

    def test_sum_latest_day__gains_or_losses_can_be_negative(self):
        """評価損益が負の場合も正しく合算される"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 800_000, 900_000, -100_000),
                _make_asset(date(2026, 1, 10), "商品B", 300_000, 350_000, -50_000),
            ]
        )

        result = history.sum_latest_day()

        assert result.gains_or_losses == GainsOrLosses(value=-150_000)


class TestAssetValuationByDate:
    def test_asset_valuation_by_date__multiple_products_on_same_date_are_summed(self):
        """同一日付の複数商品の資産評価額が合算される"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000),
                _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000),
            ]
        )

        result = history.asset_valuation_by_date()

        assert result == {date(2026, 1, 10): AssetValuation(value=1_000_000)}

    def test_asset_valuation_by_date__multiple_dates_are_grouped_separately(self):
        """複数日付が混在した場合に日付ごとに分けられる"""
        history = FinancialAssetHistory(
            assets=[
                _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000),
                _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000),
                _make_asset(date(2026, 1, 9), "商品A", 590_000, 500_000, 90_000),
                _make_asset(date(2026, 1, 9), "商品B", 390_000, 350_000, 40_000),
            ]
        )

        result = history.asset_valuation_by_date()

        assert result == {
            date(2026, 1, 10): AssetValuation(value=1_000_000),
            date(2026, 1, 9): AssetValuation(value=980_000),
        }

    def test_asset_valuation_by_date__empty_history_returns_empty_dict(self):
        """空の履歴の場合は空の dict を返す"""
        result = FinancialAssetHistory().asset_valuation_by_date()

        assert result == {}
