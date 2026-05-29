from datetime import date

from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    DailyAssetTotal,
    GainsOrLosses,
)

from src.application import AssetSummary, FormatMessageUseCase


def _make_summary(
    base_date: date,
    cc: int,
    gl: int,
    av: int,
    valuations_by_date: dict[date, AssetValuation] | None = None,
) -> AssetSummary:
    return AssetSummary(
        latest_day_total=DailyAssetTotal(
            base_date=base_date,
            cumulative_contributions=CumulativeContributions(value=cc),
            gains_or_losses=GainsOrLosses(value=gl),
            asset_valuation=AssetValuation(value=av),
        ),
        valuations_by_date=valuations_by_date or {},
    )


class TestFormatMessageUseCase:
    def test_format__contains_header(self):
        """メッセージにヘッダーが含まれる"""
        summary = _make_summary(date(2026, 1, 10), 900_000, 300_000, 1_200_000)

        result = FormatMessageUseCase().format(summary)

        assert "確定拠出年金 運用状況通知Bot" in result

    def test_format__contains_latest_day_total(self):
        """メッセージに最新日の合計資産情報が含まれる"""
        summary = _make_summary(date(2026, 1, 10), 900_000, 300_000, 1_200_000)

        result = FormatMessageUseCase().format(summary)

        assert "拠出金額累計: 900,000円" in result
        assert "評価損益: 300,000円" in result
        assert "資産評価額: 1,200,000円" in result

    def test_format__contains_weekly_section(self):
        """valuations_by_date があれば推移セクションが含まれる"""
        summary = _make_summary(
            date(2026, 1, 10),
            900_000,
            300_000,
            1_200_000,
            valuations_by_date={
                date(2026, 1, 10): AssetValuation(value=1_200_000),
                date(2026, 1, 9): AssetValuation(value=1_195_000),
            },
        )

        result = FormatMessageUseCase().format(summary)

        assert "資産評価額推移（直近1週間）" in result
        assert "2026-01-10: 1,200,000円 +5,000円" in result
        assert "2026-01-09: 1,195,000円 -" in result

    def test_format__empty_valuations_by_date_omits_weekly_section(self):
        """valuations_by_date が空なら推移セクションは表示されない"""
        summary = _make_summary(date(2026, 1, 10), 900_000, 300_000, 1_200_000)

        result = FormatMessageUseCase().format(summary)

        assert "資産評価額推移" not in result

    def test_format__weekly_section_displayed_in_descending_order(self):
        """推移セクションは新しい日付順（降順）で表示される"""
        summary = _make_summary(
            date(2026, 1, 10),
            900_000,
            300_000,
            1_200_000,
            valuations_by_date={
                date(2026, 1, 8): AssetValuation(value=1_180_000),
                date(2026, 1, 10): AssetValuation(value=1_200_000),
                date(2026, 1, 9): AssetValuation(value=1_195_000),
            },
        )

        result = FormatMessageUseCase().format(summary)

        idx_10 = result.index("2026-01-10")
        idx_9 = result.index("2026-01-09")
        idx_8 = result.index("2026-01-08")
        assert idx_10 < idx_9 < idx_8

    def test_format__output_matches_expected_exactly(self):
        """メッセージ全体が期待する文字列と完全一致する"""
        summary = AssetSummary(
            latest_day_total=DailyAssetTotal(
                base_date=date(2025, 12, 5),
                cumulative_contributions=CumulativeContributions(value=2_280_000),
                gains_or_losses=GainsOrLosses(value=456_000),
                asset_valuation=AssetValuation(value=2_736_000),
            ),
            valuations_by_date={
                date(2025, 12, 1): AssetValuation(value=2_720_000),
                date(2025, 12, 2): AssetValuation(value=2_725_000),
                date(2025, 12, 3): AssetValuation(value=2_730_000),
                date(2025, 12, 4): AssetValuation(value=2_736_000),
                date(2025, 12, 5): AssetValuation(value=2_736_000),
            },
        )
        expected = (
            "確定拠出年金 運用状況通知Bot\n"
            "\n"
            "拠出金額累計: 2,280,000円\n"
            "評価損益: 456,000円\n"
            "資産評価額: 2,736,000円\n"
            "\n"
            "資産評価額推移（直近1週間）\n"
            "2025-12-05: 2,736,000円 +0円\n"
            "2025-12-04: 2,736,000円 +6,000円\n"
            "2025-12-03: 2,730,000円 +5,000円\n"
            "2025-12-02: 2,725,000円 +5,000円\n"
            "2025-12-01: 2,720,000円 -\n"
        )

        result = FormatMessageUseCase().format(summary)

        assert result == expected
