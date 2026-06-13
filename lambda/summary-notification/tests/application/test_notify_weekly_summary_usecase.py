from datetime import date

import pytest

from src.application import NotifyWeeklySummaryUseCase
from src.application.notifier_interface import INotifier, NotificationError
from src.domain import (
    AssetRetrievalError,
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)
from tests.fixtures.mocks import MockFinancialAssetRepository, MockNotifier


def _make_asset(d: date, product: str, av: int, cc: int, gl: int) -> FinancialAsset:
    return FinancialAsset(
        base_date=d,
        product_name=product,
        asset_valuation=AssetValuation(value=av),
        cumulative_contributions=CumulativeContributions(value=cc),
        gains_or_losses=GainsOrLosses(value=gl),
    )


@pytest.fixture
def sample_history() -> FinancialAssetHistory:
    """直近2日分の資産データ（複数商品）"""
    return FinancialAssetHistory(
        assets=[
            _make_asset(date(2026, 1, 10), "商品A", 600_000, 500_000, 100_000),
            _make_asset(date(2026, 1, 10), "商品B", 400_000, 350_000, 50_000),
            _make_asset(date(2026, 1, 9), "商品A", 590_000, 500_000, 90_000),
            _make_asset(date(2026, 1, 9), "商品B", 395_000, 350_000, 45_000),
        ]
    )


@pytest.fixture
def notifier() -> MockNotifier:
    return MockNotifier()


@pytest.fixture
def repository(sample_history: FinancialAssetHistory) -> MockFinancialAssetRepository:
    return MockFinancialAssetRepository(history=sample_history)


@pytest.fixture
def usecase(
    repository: MockFinancialAssetRepository,
    notifier: MockNotifier,
) -> NotifyWeeklySummaryUseCase:
    return NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)


@pytest.fixture
def executed_message(usecase: NotifyWeeklySummaryUseCase, notifier: MockNotifier) -> str:
    """usecase.execute() を呼び出した後の通知メッセージ"""
    usecase.execute()
    return notifier.messages_sent[0]


@pytest.fixture
def exact_match_history() -> FinancialAssetHistory:
    """完全一致テスト用の固定5日分データ"""
    return FinancialAssetHistory(
        assets=[
            _make_asset(date(2025, 12, 1), "商品A", 2_720_000, 2_280_000, 440_000),
            _make_asset(date(2025, 12, 2), "商品A", 2_725_000, 2_280_000, 445_000),
            _make_asset(date(2025, 12, 3), "商品A", 2_730_000, 2_280_000, 450_000),
            _make_asset(date(2025, 12, 4), "商品A", 2_736_000, 2_280_000, 456_000),
            _make_asset(date(2025, 12, 5), "商品A", 2_736_000, 2_280_000, 456_000),
        ]
    )


class TestNotifyWeeklySummaryUseCase:
    def test_execute__contains_header(self, executed_message: str):
        """通知メッセージにヘッダー文字列が含まれる"""
        assert "確定拠出年金 運用状況通知Bot" in executed_message

    def test_execute__contains_cumulative_contributions(self, executed_message: str):
        """通知メッセージに最新日の合計拠出金額が含まれる"""
        # 最新日(2026-01-10): 商品A(500,000) + 商品B(350,000) = 850,000
        assert "拠出金額累計: 850,000円" in executed_message

    def test_execute__contains_gains_or_losses(self, executed_message: str):
        """通知メッセージに最新日の合計評価損益が含まれる"""
        # 最新日(2026-01-10): 商品A(100,000) + 商品B(50,000) = 150,000
        assert "評価損益: 150,000円" in executed_message

    def test_execute__contains_asset_valuation(self, executed_message: str):
        """通知メッセージに最新日の合計資産評価額が含まれる"""
        # 最新日(2026-01-10): 商品A(600,000) + 商品B(400,000) = 1,000,000
        assert "資産評価額: 1,000,000円" in executed_message

    def test_execute__contains_weekly_section(self, executed_message: str):
        """通知メッセージに週次推移セクションが含まれる"""
        assert "資産評価額推移（直近1週間）" in executed_message

    def test_execute__weekly_section_contains_latest_date_and_value(self, executed_message: str):
        """週次セクションに最新日の日付と資産評価額が含まれる"""
        # 最新日(2026-01-10): 合計 1,000,000円
        assert "2026-01-10: 1,000,000円" in executed_message

    def test_execute__weekly_section_contains_previous_date_with_no_diff(self, executed_message: str):
        """週次セクションの最古日（前日比なし）は "-" で終わる"""
        # 前日(2026-01-09): 合計 985,000円、最初の日なので -
        assert "2026-01-09: 985,000円 -" in executed_message

    def test_execute__weekly_section_contains_latest_date_with_diff(self, executed_message: str):
        """週次セクションの最新日行に前日比（符号付き・カンマ区切り）が含まれる"""
        # 最新日(2026-01-10): 1,000,000 - 985,000 = +15,000
        assert "2026-01-10: 1,000,000円 +15,000円" in executed_message

    def test_execute__calls_notify_exactly_once(
        self,
        usecase: NotifyWeeklySummaryUseCase,
        notifier: MockNotifier,
    ):
        """notifier.notify() がちょうど1回呼ばれる"""
        usecase.execute()

        assert len(notifier.messages_sent) == 1

    def test_execute__calls_repository_with_7_days(
        self,
        usecase: NotifyWeeklySummaryUseCase,
        repository: MockFinancialAssetRepository,
    ):
        """repository.retrieve_within_days(7, 実行日) が呼ばれる"""
        usecase.execute()

        assert repository.retrieve_called
        assert repository.last_days_arg == 7

    def test_execute__calls_repository_with_jst_today_as_base_date(
        self,
        usecase: NotifyWeeklySummaryUseCase,
        repository: MockFinancialAssetRepository,
    ):
        """retrieve_within_days の基準日が JST の実行日になる"""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        # 日付境界をまたいでも before/after のどちらかに一致するため決定的
        before = datetime.now(ZoneInfo("Asia/Tokyo")).date()
        usecase.execute()
        after = datetime.now(ZoneInfo("Asia/Tokyo")).date()

        assert repository.last_base_date_arg in {before, after}

    def test_execute__empty_history_notifies_no_data_message(self):
        """空履歴の場合はデータなし通知を送信して正常終了する"""
        expected = (
            "確定拠出年金 運用状況通知Bot\n"
            "\n"
            "直近7日間の資産データがありません。\n"
            "資産収集処理が失敗している可能性があります。"
        )
        repository = MockFinancialAssetRepository(history=FinancialAssetHistory(assets=[]))
        notifier = MockNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        usecase.execute()

        assert notifier.messages_sent == [expected]

    def test_execute__repository_failure_raises_asset_retrieval_error(self):
        """リポジトリ失敗時は AssetRetrievalError を伝播させる"""
        repository = MockFinancialAssetRepository(should_fail=True)
        notifier = MockNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        with pytest.raises(AssetRetrievalError):
            usecase.execute()

    def test_execute__notification_failure_propagates(self, sample_history: FinancialAssetHistory):
        """notifier が NotificationError を送出した場合は伝播する"""

        class FailingNotifier(INotifier):
            def notify(self, messages: list[str]) -> None:
                raise NotificationError.during_request()

        repository = MockFinancialAssetRepository(history=sample_history)
        notifier = FailingNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        with pytest.raises(NotificationError):
            usecase.execute()

    def test_execute__output_matches_expected_exactly(self, exact_match_history: FinancialAssetHistory):
        """メッセージ全体が期待する文字列と完全一致する"""
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
        repository = MockFinancialAssetRepository(history=exact_match_history)
        notifier = MockNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        usecase.execute()

        assert notifier.messages_sent[0] == expected


class TestMain:
    """presentation.Main クラスの E2E テスト"""

    def _make_history(self, *days_and_products: tuple[date, str, int, int, int]) -> FinancialAssetHistory:
        return FinancialAssetHistory(
            assets=[
                FinancialAsset(
                    base_date=d,
                    product_name=product,
                    asset_valuation=AssetValuation(value=av),
                    cumulative_contributions=CumulativeContributions(value=cc),
                    gains_or_losses=GainsOrLosses(value=gl),
                )
                for d, product, av, cc, gl in days_and_products
            ]
        )

    def test_main__run_delegates_to_usecase(self):
        """Main.run() が usecase.execute() に委譲する"""
        from src.presentation import Main

        history = self._make_history(
            (date(2026, 2, 14), "商品A", 600_000, 450_000, 150_000),
            (date(2026, 2, 14), "商品B", 600_000, 450_000, 150_000),
            (date(2026, 2, 13), "商品A", 590_000, 450_000, 140_000),
        )
        repository = MockFinancialAssetRepository(history=history)
        notifier = MockNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        main = Main(usecase=usecase)
        result = main.run()

        assert result.status == "Success"
        assert repository.retrieve_called
        assert notifier.notify_called
        assert len(notifier.messages_sent) == 1
        message = notifier.messages_sent[0]
        assert "確定拠出年金 運用状況通知Bot" in message
        assert "1,200,000円" in message

    def test_main__empty_history_notifies_no_data_and_succeeds(self):
        """空の資産履歴の場合はデータなし通知を送信して正常終了する"""
        from src.presentation import Main

        repository = MockFinancialAssetRepository(history=FinancialAssetHistory(assets=[]))
        notifier = MockNotifier()
        usecase = NotifyWeeklySummaryUseCase(repository=repository, notifier=notifier)

        main = Main(usecase=usecase)
        result = main.run()

        assert result.status == "Success"
        assert len(notifier.messages_sent) == 1
        assert "直近7日間の資産データがありません。" in notifier.messages_sent[0]
