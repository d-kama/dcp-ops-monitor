from datetime import date

import pytest

from src.application import SummaryNotificationService
from src.domain import AssetRecord, AssetRetrievalFailed
from tests.fixtures.mocks import MockAssetRecordReader, MockNotifier


@pytest.fixture
def sample_records() -> list[AssetRecord]:
    """テスト用資産レコード"""
    return [
        AssetRecord(
            date=date(2026, 2, 14),
            product="商品A",
            cumulative_contributions=450_000,
            gains_or_losses=150_000,
            asset_valuation=600_000,
        ),
        AssetRecord(
            date=date(2026, 2, 14),
            product="商品B",
            cumulative_contributions=450_000,
            gains_or_losses=150_000,
            asset_valuation=600_000,
        ),
    ]


def _make_weekly_records() -> list[AssetRecord]:
    """テスト用の週次資産レコードを生成"""
    return [
        AssetRecord(
            date=date(2026, 2, 12),
            product="商品A",
            cumulative_contributions=450_000,
            gains_or_losses=147_000,
            asset_valuation=597_000,
        ),
        AssetRecord(
            date=date(2026, 2, 13),
            product="商品A",
            cumulative_contributions=450_000,
            gains_or_losses=145_000,
            asset_valuation=595_000,
        ),
        AssetRecord(
            date=date(2026, 2, 14),
            product="商品A",
            cumulative_contributions=450_000,
            gains_or_losses=150_000,
            asset_valuation=600_000,
        ),
    ]


class TestSummaryNotificationService:
    def test_send_summary__success(self, sample_records):
        """正常にサマリ通知を送信できる"""
        # given
        repo = MockAssetRecordReader(latest_records=sample_records)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        assert repo.get_latest_called
        assert notifier.notify_called
        assert len(notifier.messages_sent) == 1
        assert "確定拠出年金 運用状況通知Bot" in notifier.messages_sent[0]
        assert "900,000円" in notifier.messages_sent[0]

    def test_send_summary__empty_records_raises_no_assets(self):
        """レコードが空の場合 AssetRetrievalFailed.no_assets_in_spreadsheet が発生する"""
        # given
        repo = MockAssetRecordReader(latest_records=[])
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when, then
        with pytest.raises(AssetRetrievalFailed) as exc_info:
            service.send_summary()

        assert "スプレッドシートに資産情報が見つかりません" in str(exc_info.value)
        assert not notifier.notify_called

    def test_send_summary__reader_failure_raises_during_fetching(self):
        """読み取り失敗時 AssetRetrievalFailed.during_fetching が発生する"""
        # given
        repo = MockAssetRecordReader(should_fail=True)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when, then
        with pytest.raises(AssetRetrievalFailed) as exc_info:
            service.send_summary()

        assert "資産情報の取得中にエラーが発生しました" in str(exc_info.value)
        assert not notifier.notify_called

    def test_send_summary__message_contains_indicators(self, sample_records):
        """送信メッセージに運用指標が含まれる"""
        # given
        repo = MockAssetRecordReader(latest_records=sample_records)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        message_text = notifier.messages_sent[0]
        assert "運用年数:" in message_text
        assert "運用利回り:" in message_text
        assert "想定受取額(60歳):" in message_text

    def test_send_summary__message_contains_weekly_valuations(self, sample_records):
        """送信メッセージに資産評価額推移が含まれる"""
        # given
        weekly_records = _make_weekly_records()
        repo = MockAssetRecordReader(latest_records=sample_records, weekly_records=weekly_records)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        message_text = notifier.messages_sent[0]
        assert "資産評価額推移（直近1週間）" in message_text
        assert "2026-02-14: 600,000円 +5,000円" in message_text
        assert "2026-02-13: 595,000円 -2,000円" in message_text
        assert "2026-02-12: 597,000円 -" in message_text

    def test_send_summary__get_records_within_days_called_with_7(self, sample_records):
        """get_records_within_days が days=7 で呼ばれる"""
        # given
        repo = MockAssetRecordReader(latest_records=sample_records)
        notifier = MockNotifier()
        service = SummaryNotificationService(asset_repository=repo, notifier=notifier)

        # when
        service.send_summary()

        # then
        assert repo.get_weekly_called
        assert repo.last_days_arg == 7


class TestCalculateWeeklyValuations:
    def test_calculate_weekly_valuations__returns_descending_order(self):
        """新しい日付順で返される"""
        weekly_records = _make_weekly_records()

        result = SummaryNotificationService._calculate_weekly_valuations(weekly_records)

        assert result[0] == (date(2026, 2, 14), 600_000, 5_000)
        assert result[1] == (date(2026, 2, 13), 595_000, -2_000)
        assert result[2] == (date(2026, 2, 12), 597_000, None)

    def test_calculate_weekly_valuations__empty_returns_empty(self):
        """空の場合は空リストを返す"""
        result = SummaryNotificationService._calculate_weekly_valuations([])

        assert result == []

    def test_calculate_weekly_valuations__single_day(self):
        """1日分のデータの場合、前日比はNone"""
        weekly_records = [
            AssetRecord(
                date=date(2026, 2, 14),
                product="商品A",
                cumulative_contributions=450_000,
                gains_or_losses=150_000,
                asset_valuation=600_000,
            ),
        ]

        result = SummaryNotificationService._calculate_weekly_valuations(weekly_records)

        assert result == [(date(2026, 2, 14), 600_000, None)]
