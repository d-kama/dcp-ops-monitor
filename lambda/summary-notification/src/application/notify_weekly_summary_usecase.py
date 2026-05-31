from datetime import date
from string import Template

from shared.domain.financial_asset import AssetValuation, DailyAssetTotal, FinancialAssetHistory
from shared.domain.financial_asset_repository import IFinancialAssetRepository

from .notifier import INotifier
from .notify_weekly_summary_interface import INotifyWeeklySummaryUseCase

_TEMPLATE = Template(
    "確定拠出年金 運用状況通知Bot\n"
    "\n"
    "拠出金額累計: ${cumulative_contributions}円\n"
    "評価損益: ${gains_or_losses}円\n"
    "資産評価額: ${asset_valuation}円\n"
    "\n"
    "${weekly_section}"
)

_WEEKLY_HEADER = "資産評価額推移（直近1週間）\n"


class NotifyWeeklySummaryUseCase(INotifyWeeklySummaryUseCase):
    DAYS = 7

    def __init__(self, repository: IFinancialAssetRepository, notifier: INotifier) -> None:
        self.repository = repository
        self.notifier = notifier

    def execute(self) -> None:
        history = self.repository.retrieve_from_with_days(self.DAYS)
        message = self._format(self._summarise(history))
        self.notifier.notify([message])

    def _summarise(self, history: FinancialAssetHistory) -> tuple[DailyAssetTotal, dict[date, AssetValuation]]:
        latest_day_total = history.sum_latest_day()
        valuations_by_date = history.asset_valuation_by_date()
        return latest_day_total, valuations_by_date

    def _format(self, summary: tuple[DailyAssetTotal, dict[date, AssetValuation]]) -> str:
        latest_day_total, valuations_by_date = summary
        weekly_section = self._build_weekly_section(valuations_by_date)
        total = latest_day_total
        return _TEMPLATE.substitute(
            cumulative_contributions=f"{total.cumulative_contributions.value:,}",
            gains_or_losses=f"{total.gains_or_losses.value:,}",
            asset_valuation=f"{total.asset_valuation.value:,}",
            weekly_section=weekly_section,
        )

    def _build_weekly_section(self, valuations_by_date: dict[date, AssetValuation]) -> str:
        if not valuations_by_date:
            return ""

        sorted_dates = sorted(valuations_by_date.keys())
        rows: list[tuple[date, int, int | None]] = []
        prev: int | None = None
        for d in sorted_dates:
            v = valuations_by_date[d].value
            rows.append((d, v, None if prev is None else v - prev))
            prev = v

        lines = [_WEEKLY_HEADER]
        for d, valuation, diff in reversed(rows):
            diff_str = f" {diff:+,}円" if diff is not None else " -"
            lines.append(f"{d}: {valuation:,}円{diff_str}\n")
        return "".join(lines)
