from datetime import date
from unittest.mock import MagicMock

from src.domain import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)


def _make_usecase():
    from src.application import CollectAssetDailyUseCase
    from tests.fixtures.mocks import (
        MockAssetFetcher,
        MockErrorArtifactRepository,
        MockFinancialAssetRepository,
    )

    history = FinancialAssetHistory(
        assets=[
            FinancialAsset(
                product_name="プロダクト_1",
                base_date=date.today(),
                cumulative_contributions=CumulativeContributions(value=100_000),
                gains_or_losses=GainsOrLosses(value=11_111),
                asset_valuation=AssetValuation(value=111_111),
            ),
        ]
    )
    config = MagicMock()
    config.start_url = "http://example.com"
    return CollectAssetDailyUseCase(
        fetcher=MockAssetFetcher(mock_history=history),
        repository=MockFinancialAssetRepository(),
        error_repo=MockErrorArtifactRepository(),
        config=config,
    )


def test_main__run_returns_success_result():
    """Main.run() が status=Success の結果を返す"""
    from src.presentation import AssetCollectionResult, Main

    result = Main(_make_usecase()).run()

    assert isinstance(result, AssetCollectionResult)
    assert result.status == "Success"
