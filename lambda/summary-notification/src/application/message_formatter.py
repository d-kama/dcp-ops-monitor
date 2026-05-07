"""サマリ通知メッセージのフォーマット"""

from datetime import date
from string import Template

from src.domain import AssetEvaluation, OpsIndicators

_SUMMARY_TEMPLATE = Template(
    "確定拠出年金 運用状況通知Bot\n"
    "\n"
    "拠出金額累計: ${cumulative_contributions}円\n"
    "評価損益: ${gains_or_losses}円\n"
    "資産評価額: ${asset_valuation}円\n"
    "\n"
    "運用年数: ${operation_years}年\n"
    "運用利回り: ${actual_yield_rate}\n"
    "想定受取額(60歳): ${total_amount_at_60age}円\n"
    "\n"
    "${weekly_section}"
)

_WEEKLY_HEADER = "資産評価額推移（直近1週間）\n"


def _build_weekly_section(weekly_valuations: list[tuple[date, int, int | None]]) -> str:
    if not weekly_valuations:
        return ""
    lines = [_WEEKLY_HEADER]
    for d, valuation, diff in weekly_valuations:
        diff_str = f" {diff:+,}円" if diff is not None else " -"
        lines.append(f"{d}: {valuation:,}円{diff_str}\n")
    return "".join(lines)


def format_summary_message(
    total: AssetEvaluation,
    indicators: OpsIndicators,
    weekly_valuations: list[tuple[date, int, int | None]],
) -> str:
    """資産情報と運用指標からサマリメッセージをフォーマット

    Args:
        total: 全商品合計の資産情報
        indicators: 運用指標
        weekly_valuations: (日付, 資産評価額, 前日比 or None) のリスト（新しい日付順）

    Returns:
        str: フォーマットされたメッセージ
    """
    weekly_section = _build_weekly_section(weekly_valuations)
    return _SUMMARY_TEMPLATE.substitute(
        cumulative_contributions=f"{total.cumulative_contributions:,}",
        gains_or_losses=f"{total.gains_or_losses:,}",
        asset_valuation=f"{total.asset_valuation:,}",
        operation_years=indicators.operation_years,
        actual_yield_rate=indicators.actual_yield_rate,
        total_amount_at_60age=f"{indicators.total_amount_at_60age:,}",
        weekly_section=weekly_section,
    )
