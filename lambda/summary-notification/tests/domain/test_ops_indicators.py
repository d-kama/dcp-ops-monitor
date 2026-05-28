from datetime import date

from src.domain import AssetEvaluation, OpsIndicators


class TestOpsIndicators:
    def test_create__valid_values(self):
        """正常な値で OpsIndicators を生成できる"""
        indicators = OpsIndicators(
            operation_years=9.34,
            actual_yield_rate=0.036,
            total_amount_at_60age=15_000_000,
        )
        assert indicators.operation_years == 9.34
        assert indicators.actual_yield_rate == 0.036
        assert indicators.total_amount_at_60age == 15_000_000

    def test_create__zero_yield_rate(self):
        """利回りが 0 の場合も生成できる"""
        indicators = OpsIndicators(
            operation_years=1.0,
            actual_yield_rate=0.0,
            total_amount_at_60age=0,
        )
        assert indicators.actual_yield_rate == 0.0

    def test_create__negative_yield_rate(self):
        """利回りがマイナスの場合も生成できる"""
        indicators = OpsIndicators(
            operation_years=5.0,
            actual_yield_rate=-0.02,
            total_amount_at_60age=5_000_000,
        )
        assert indicators.actual_yield_rate == -0.02


class TestFromAssetEvaluation:
    def test_from_asset_evaluation__positive_yield(self):
        """正の利回りで運用指標を計算できる"""
        total_assets = AssetEvaluation(
            cumulative_contributions=900_000,
            gains_or_losses=300_000,
            asset_valuation=1_200_000,
        )
        result = OpsIndicators.from_asset_evaluation(total_assets, today=date(2026, 2, 5))

        assert result.operation_years > 9.0
        assert result.actual_yield_rate > 0
        assert result.total_amount_at_60age > 1_200_000
        assert isinstance(result.total_amount_at_60age, int)

    def test_from_asset_evaluation__negative_gains_yields_negative_rate(self):
        """評価損益がマイナスのとき利回りもマイナスになる"""
        total_assets = AssetEvaluation(
            cumulative_contributions=1_000_000,
            gains_or_losses=-100_000,
            asset_valuation=900_000,
        )
        result = OpsIndicators.from_asset_evaluation(total_assets, today=date(2026, 2, 5))

        assert result.actual_yield_rate < 0

    def test_from_asset_evaluation__zero_cumulative_contributions_yields_zero_rate(self):
        """拠出金額累計が 0 のとき利回りは 0 になる"""
        total_assets = AssetEvaluation(
            cumulative_contributions=0,
            gains_or_losses=0,
            asset_valuation=0,
        )
        result = OpsIndicators.from_asset_evaluation(total_assets, today=date(2026, 2, 5))

        assert result.actual_yield_rate == 0.0

    def test_from_asset_evaluation__operation_start_date_yields_zero_rate(self):
        """運用開始日当日（運用年数=0）のとき利回りは 0 になる"""
        total_assets = AssetEvaluation(
            cumulative_contributions=1_000_000,
            gains_or_losses=300_000,
            asset_valuation=1_000_000,
        )
        # OPERATION_START_DATE = date(2016, 10, 1)
        result = OpsIndicators.from_asset_evaluation(total_assets, today=date(2016, 10, 1))

        assert result.operation_years == 0.0
        assert result.actual_yield_rate == 0.0

    def test_from_asset_evaluation__zero_yield_total_amount_uses_simple_multiplication(self):
        """利回りが 0 のとき想定受取額が年間積立額 × 残年数 + 現在評価額になる"""
        from datetime import timedelta

        total_assets = AssetEvaluation(
            cumulative_contributions=0,
            gains_or_losses=0,
            asset_valuation=1_000_000,
        )
        today = date(2026, 10, 1)
        retirement = date(2046, 10, 1)
        years_to_retirement = round((retirement - today) / timedelta(days=365), 2)
        expected = int(240_000 * years_to_retirement) + 1_000_000

        result = OpsIndicators.from_asset_evaluation(total_assets, today=today)

        assert result.actual_yield_rate == 0.0
        assert result.total_amount_at_60age == expected

    def test_from_asset_evaluation__after_retirement_total_amount_equals_asset_valuation(self):
        """退職日以降のとき想定受取額が現在の資産評価額と等しい"""
        total_assets = AssetEvaluation(
            cumulative_contributions=3_000_000,
            gains_or_losses=500_000,
            asset_valuation=3_500_000,
        )
        result = OpsIndicators.from_asset_evaluation(total_assets, today=date(2050, 1, 1))

        assert result.total_amount_at_60age == 3_500_000
