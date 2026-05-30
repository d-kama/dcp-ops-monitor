from datetime import date

import pytest

from src.application import AssetFetchFailed
from src.domain import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)


@pytest.fixture
def valid_history() -> FinancialAssetHistory:
    """テスト用の正常な金融資産履歴を生成する"""
    today = date.today()
    return FinancialAssetHistory(
        assets=[
            FinancialAsset(
                product_name="プロダクト_1",
                base_date=today,
                cumulative_contributions=CumulativeContributions(value=100_000),
                gains_or_losses=GainsOrLosses(value=11_111),
                asset_valuation=AssetValuation(value=111_111),
            ),
            FinancialAsset(
                product_name="プロダクト_2",
                base_date=today,
                cumulative_contributions=CumulativeContributions(value=200_000),
                gains_or_losses=GainsOrLosses(value=22_222),
                asset_valuation=AssetValuation(value=222_222),
            ),
            FinancialAsset(
                product_name="プロダクト_3",
                base_date=today,
                cumulative_contributions=CumulativeContributions(value=300_000),
                gains_or_losses=GainsOrLosses(value=33_333),
                asset_valuation=AssetValuation(value=333_333),
            ),
        ]
    )


def test_main__all_mocks_succeed__saves_assets(valid_history):
    """main関数のE2Eテスト（Mockを使用）

    エンドツーエンドで処理が正常に完了することを確認する
    """
    # given
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockFinancialAssetRepository, MockSeleniumAssetFetcher

    fetcher = MockSeleniumAssetFetcher(mock_history=valid_history)
    repo = MockFinancialAssetRepository()

    # when
    main(fetcher=fetcher, financial_asset_repository=repo)

    # then
    assert fetcher.fetch_called is True
    assert repo.saved_daily_assets is not None
    assert len(repo.saved_daily_assets.assets) == 3
    product_names = {a.product_name for a in repo.saved_daily_assets.assets}
    assert product_names == {"プロダクト_1", "プロダクト_2", "プロダクト_3"}


def test_main__scraping_fails__raises_asset_fetch_failed(valid_history):
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、AssetFetchFailed 例外が伝播することを確認する
    """
    # given
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockFinancialAssetRepository, MockSeleniumAssetFetcher

    fetcher = MockSeleniumAssetFetcher(should_fail=True)
    repo = MockFinancialAssetRepository()

    # when, then
    with pytest.raises(AssetFetchFailed):
        main(fetcher=fetcher, financial_asset_repository=repo)

    assert fetcher.fetch_called is True
    assert repo.saved_daily_assets is None


def test_main__extraction_fails__raises_asset_fetch_failed(valid_history):
    """抽出エラー時のE2Eテスト

    資産情報の抽出に失敗した場合、AssetFetchFailed 例外が伝播することを確認する
    """
    # given
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockFinancialAssetRepository, MockSeleniumAssetFetcher

    fetcher = MockSeleniumAssetFetcher(should_fail_extraction=True)
    repo = MockFinancialAssetRepository()

    # when, then
    with pytest.raises(AssetFetchFailed):
        main(fetcher=fetcher, financial_asset_repository=repo)

    assert fetcher.fetch_called is True
    assert repo.saved_daily_assets is None
