from datetime import date

import pytest
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)

from src.domain import AssetRetrievalFailed
from tests.fixtures.mocks import MockFinancialAssetRepository, MockNotifier


def _make_history(*days_and_products: tuple[date, str, int, int, int]) -> FinancialAssetHistory:
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


def test_main__e2e_with_mocks():
    """Use Case を通じた E2E フローが正常に完了する"""
    from src.presentation.summary_notification_handler import main

    history = _make_history(
        (date(2026, 2, 14), "商品A", 600_000, 450_000, 150_000),
        (date(2026, 2, 14), "商品B", 600_000, 450_000, 150_000),
        (date(2026, 2, 13), "商品A", 590_000, 450_000, 140_000),
    )
    repository = MockFinancialAssetRepository(history=history)
    notifier = MockNotifier()

    main(asset_repository=repository, notifier=notifier)

    assert repository.retrieve_called
    assert notifier.notify_called
    assert len(notifier.messages_sent) == 1
    message = notifier.messages_sent[0]
    assert "確定拠出年金 運用状況通知Bot" in message
    assert "1,200,000円" in message


def test_main__empty_history_raises_asset_retrieval_failed():
    """資産情報が空の場合 AssetRetrievalFailed が発生する"""
    from src.presentation.summary_notification_handler import main

    repository = MockFinancialAssetRepository(history=FinancialAssetHistory(assets=[]))
    notifier = MockNotifier()

    with pytest.raises(AssetRetrievalFailed):
        main(asset_repository=repository, notifier=notifier)
