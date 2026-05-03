from datetime import date

import pytest

from src.domain import AssetRecord, AssetRetrievalFailed
from tests.fixtures.mocks import MockAssetRecordReader, MockNotifier


@pytest.fixture
def sample_records() -> list[AssetRecord]:
    """テスト用の資産レコード"""
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


def test_main__e2e_with_mocks(sample_records):
    """main 関数の E2E テスト（Mock を使用）

    資産取得→指標計算→通知送信の全フローが正常に完了することを確認する
    """
    # given
    from src.presentation.summary_notification_handler import main

    repo = MockAssetRecordReader(latest_records=sample_records)
    notifier = MockNotifier()

    # when
    main(asset_repository=repo, notifier=notifier)

    # then
    assert repo.get_latest_called
    assert notifier.notify_called
    assert len(notifier.messages_sent) == 1

    message = notifier.messages_sent[0]
    assert "確定拠出年金 運用状況通知Bot" in message
    assert "900,000円" in message
    assert "運用年数:" in message
    assert "想定受取額(60歳):" in message


def test_main__asset_not_found_raises():
    """資産情報が見つからない場合 AssetRetrievalFailed が発生する"""
    # given
    from src.presentation.summary_notification_handler import main

    repo = MockAssetRecordReader(latest_records=[])
    notifier = MockNotifier()

    # when, then
    with pytest.raises(AssetRetrievalFailed):
        main(asset_repository=repo, notifier=notifier)
