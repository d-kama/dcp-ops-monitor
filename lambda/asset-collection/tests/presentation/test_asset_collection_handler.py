import os
from datetime import date

import pytest

from src.domain import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)


def list_s3_objects(local_stack_container, prefix: str) -> list[str]:
    """指定されたプレフィックスのS3オブジェクトキーを取得する"""
    client = local_stack_container.get_client("s3")
    response = client.list_objects_v2(
        Bucket=os.environ["DATA_BUCKET_NAME"],
        Prefix=prefix,
    )
    return [obj["Key"] for obj in response.get("Contents", [])]


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


def test_main_e2e_with_mocks(valid_history):
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
    assert repo.saved_history is not None
    assert len(repo.saved_history.assets) == 3
    product_names = {a.product_name for a in repo.saved_history.assets}
    assert product_names == {"プロダクト_1", "プロダクト_2", "プロダクト_3"}


def test_main_e2e_with_scraping_error(local_stack_container):
    """スクレイピングエラー時のE2Eテスト

    スクレイピングが失敗した場合、例外が発生することを確認する
    また、エラー画像が S3 の errors/ プレフィックスにアップロードされることを確認する
    """
    # given
    from src.domain import ScrapingFailed
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockFinancialAssetRepository, MockSeleniumAssetFetcher

    fetcher = MockSeleniumAssetFetcher(should_fail=True)
    repo = MockFinancialAssetRepository()

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(fetcher=fetcher, financial_asset_repository=repo)

    assert exc_info.value.error_screenshot_key is not None
    assert exc_info.value.error_screenshot_key.startswith("errors/")
    assert fetcher.fetch_called is True
    assert repo.saved_history is None

    object_keys = list_s3_objects(local_stack_container, "errors/")
    assert any(key.endswith(".png") for key in object_keys)


def test_main_e2e_with_extraction_error(local_stack_container):
    """抽出エラー時のE2Eテスト

    資産情報の抽出に失敗した場合、例外が発生することを確認する
    また、エラー HTML ファイルが S3 の errors/ プレフィックスにアップロードされることを確認する
    """
    # given
    from src.domain import ScrapingFailed
    from src.presentation.asset_collection_handler import main
    from tests.fixtures.mocks import MockFinancialAssetRepository, MockSeleniumAssetFetcher

    fetcher = MockSeleniumAssetFetcher(should_fail_extraction=True)
    repo = MockFinancialAssetRepository()

    # when, then
    with pytest.raises(ScrapingFailed) as exc_info:
        main(fetcher=fetcher, financial_asset_repository=repo)

    assert exc_info.value.error_html_key is not None
    assert exc_info.value.error_html_key.startswith("errors/")
    assert fetcher.fetch_called is True
    assert repo.saved_history is None

    object_keys = list_s3_objects(local_stack_container, "errors/")
    assert any(key.endswith(".html") for key in object_keys)
