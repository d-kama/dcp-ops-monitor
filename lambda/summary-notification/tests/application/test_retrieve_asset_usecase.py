from datetime import date

import pytest
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)

from src.application import RetrieveAssetUseCase
from src.domain import AssetRetrievalFailed
from tests.fixtures.mocks import MockFinancialAssetRepository


@pytest.fixture
def sample_history() -> FinancialAssetHistory:
    return FinancialAssetHistory(
        assets=[
            FinancialAsset(
                base_date=date(2026, 2, 14),
                product_name="商品A",
                asset_valuation=AssetValuation(value=600_000),
                cumulative_contributions=CumulativeContributions(value=450_000),
                gains_or_losses=GainsOrLosses(value=150_000),
            ),
        ]
    )


class TestRetrieveAssetUseCase:
    def test_retrieve__returns_financial_asset_history(self, sample_history):
        """直近 7 日分の FinancialAssetHistory が返る"""
        repository = MockFinancialAssetRepository(history=sample_history)
        usecase = RetrieveAssetUseCase(repository=repository)

        result = usecase.execute()

        assert result == sample_history

    def test_retrieve__calls_repository_with_7_days(self, sample_history):
        """repository.retrieve_from_with_days(7) が呼ばれる"""
        repository = MockFinancialAssetRepository(history=sample_history)
        usecase = RetrieveAssetUseCase(repository=repository)

        usecase.execute()

        assert repository.retrieve_called
        assert repository.last_days_arg == 7

    def test_retrieve__empty_history_returned_as_is(self):
        """データが空の場合も空の FinancialAssetHistory をそのまま返す"""
        repository = MockFinancialAssetRepository(history=FinancialAssetHistory(assets=[]))
        usecase = RetrieveAssetUseCase(repository=repository)

        result = usecase.execute()

        assert result == FinancialAssetHistory(assets=[])

    def test_retrieve__propagates_asset_retrieval_failed(self):
        """リポジトリ失敗時は AssetRetrievalFailed を伝播させる"""
        repository = MockFinancialAssetRepository(should_fail=True)
        usecase = RetrieveAssetUseCase(repository=repository)

        with pytest.raises(AssetRetrievalFailed):
            usecase.execute()
