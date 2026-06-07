from datetime import date
from unittest.mock import MagicMock

import pytest

from src.application import CollectAssetDailyUseCase, ExtractError, LoginError, NavigatePageError
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


def make_usecase(fetcher, repo=None, error_repo=None, config=None):
    """テスト用 UseCase を生成するヘルパー"""
    from tests.fixtures.mocks import MockErrorArtifactRepository, MockFinancialAssetRepository

    if repo is None:
        repo = MockFinancialAssetRepository()
    if error_repo is None:
        error_repo = MockErrorArtifactRepository()
    if config is None:
        config = MagicMock()
        config.start_url = "http://example.com"

    return CollectAssetDailyUseCase(
        fetcher=fetcher,
        repository=repo,
        error_repo=error_repo,
        config=config,
    )


def test_execute__all_steps_succeed__saves_assets(valid_history):
    """全ステップ成功時に save_daily が呼ばれる"""
    from tests.fixtures.mocks import MockAssetFetcher, MockFinancialAssetRepository

    fetcher = MockAssetFetcher(mock_history=valid_history)
    repo = MockFinancialAssetRepository()
    usecase = make_usecase(fetcher=fetcher, repo=repo)

    usecase.execute()

    assert repo.saved_daily_assets is not None
    assert len(repo.saved_daily_assets.assets) == 3
    product_names = {a.product_name for a in repo.saved_daily_assets.assets}
    assert product_names == {"プロダクト_1", "プロダクト_2", "プロダクト_3"}


def test_execute__login_fails__stores_screenshot_and_raises():
    """login 失敗時にスクリーンショット保存 + LoginError を raise する"""
    from tests.fixtures.mocks import MockAssetFetcher, MockErrorArtifactRepository

    fetcher = MockAssetFetcher(fail_at="login")
    error_repo = MockErrorArtifactRepository()
    usecase = make_usecase(fetcher=fetcher, error_repo=error_repo)

    with pytest.raises(LoginError):
        usecase.execute()

    assert len(error_repo.stored_keys) == 1
    assert error_repo.stored_keys[0].endswith(".png")


def test_execute__login_fails__calls_logout_and_close():
    """login 失敗時でも finally で logout / close が呼ばれる"""
    from tests.fixtures.mocks import MockAssetFetcher

    fetcher = MockAssetFetcher(fail_at="login")
    usecase = make_usecase(fetcher=fetcher)

    with pytest.raises(LoginError):
        usecase.execute()

    assert fetcher.logout_called
    assert fetcher.close_called


def test_execute__navigate_fails__stores_screenshot_and_raises():
    """navigate 失敗時にスクリーンショット保存 + NavigatePageError を raise する"""
    from tests.fixtures.mocks import MockAssetFetcher, MockErrorArtifactRepository

    fetcher = MockAssetFetcher(fail_at="navigate")
    error_repo = MockErrorArtifactRepository()
    usecase = make_usecase(fetcher=fetcher, error_repo=error_repo)

    with pytest.raises(NavigatePageError):
        usecase.execute()

    assert len(error_repo.stored_keys) == 1
    assert error_repo.stored_keys[0].endswith(".png")


def test_execute__extract_fails__stores_page_source_and_raises():
    """extract 失敗時にページソース保存 + ExtractError を raise する"""
    from tests.fixtures.mocks import MockAssetFetcher, MockErrorArtifactRepository

    fetcher = MockAssetFetcher(fail_at="extract")
    error_repo = MockErrorArtifactRepository()
    usecase = make_usecase(fetcher=fetcher, error_repo=error_repo)

    with pytest.raises(ExtractError):
        usecase.execute()

    assert len(error_repo.stored_keys) == 1
    assert error_repo.stored_keys[0].endswith(".html")


def test_execute__artifact_store_fails__does_not_raise_artifact_error():
    """エラーアーティファクト保存失敗時は警告ログのみで例外を握りつぶす"""
    from tests.fixtures.mocks import MockAssetFetcher, MockErrorArtifactRepository

    fetcher = MockAssetFetcher(fail_at="login")
    error_repo = MockErrorArtifactRepository(should_fail=True)
    usecase = make_usecase(fetcher=fetcher, error_repo=error_repo)

    # LoginError は raise されるが ErrorArtifactUploadError は伝播しない
    with pytest.raises(LoginError):
        usecase.execute()


def test_execute__success__calls_logout_and_close(valid_history):
    """成功時も finally で logout / close が呼ばれる"""
    from tests.fixtures.mocks import MockAssetFetcher

    fetcher = MockAssetFetcher(mock_history=valid_history)
    usecase = make_usecase(fetcher=fetcher)

    usecase.execute()

    assert fetcher.logout_called
    assert fetcher.close_called
