"""SeleniumAssetFetcher の単体テスト

SeleniumWebDriver 自体は pytest-mock でパッチし、
S3 アップロード失敗時のエラーハンドリングを検証する。
"""

from unittest.mock import MagicMock, patch

import pytest

from src.application.error_artifact_repository import ArtifactUploadError, IErrorArtifactRepository
from src.infrastructure.selenium_asset_fetcher import SeleniumAssetFetcher, SeleniumAssetFetchFailed


class AlwaysFailArtifactRepository(IErrorArtifactRepository):
    """store() が常に ArtifactUploadError を raise するスタブ"""

    def store(self, key: str, file_path: str) -> None:
        raise ArtifactUploadError("S3 upload failed (test stub)")


class AlwaysSucceedArtifactRepository(IErrorArtifactRepository):
    """store() が常に成功するスタブ"""

    def __init__(self) -> None:
        self.stored_keys: list[str] = []

    def store(self, key: str, file_path: str) -> None:
        self.stored_keys.append(key)


def _make_fetcher(error_repo: IErrorArtifactRepository) -> SeleniumAssetFetcher:
    """SeleniumAssetFetcher を driver 初期化なしで生成するヘルパー"""
    config = MagicMock()
    config.user_agent = "test-agent"
    config.login_user_id.get_secret_value.return_value = "user"
    config.login_password.get_secret_value.return_value = "pass"
    config.login_birthdate.get_secret_value.return_value = "19900101"
    config.start_url = "http://example.com"

    with patch.object(SeleniumAssetFetcher, "_get_driver", return_value=MagicMock()):
        fetcher = SeleniumAssetFetcher(config=config, error_repo=error_repo)

    return fetcher


# ---------- _login ----------


def test_login__artifact_upload_fails__raises_selenium_fetch_failed():
    """_login で S3 アップロードが失敗しても SeleniumAssetFetchFailed が raise される"""
    fetcher = _make_fetcher(AlwaysFailArtifactRepository())

    # driver.find_element が例外を raise → except ブロックに入る
    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(SeleniumAssetFetchFailed):
        fetcher._login()


def test_login__artifact_upload_succeeds__raises_selenium_fetch_failed():
    """_login で元の処理が失敗した場合、S3 成功でも SeleniumAssetFetchFailed が raise される"""
    repo = AlwaysSucceedArtifactRepository()
    fetcher = _make_fetcher(repo)

    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(SeleniumAssetFetchFailed):
        fetcher._login()

    assert len(repo.stored_keys) == 1


# ---------- _navigate_to_asset_page ----------


def test_navigate_to_asset_page__artifact_upload_fails__raises_selenium_fetch_failed():
    """_navigate_to_asset_page で S3 アップロードが失敗しても SeleniumAssetFetchFailed が raise される"""
    fetcher = _make_fetcher(AlwaysFailArtifactRepository())

    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(SeleniumAssetFetchFailed):
        fetcher._navigate_to_asset_page()


def test_navigate_to_asset_page__artifact_upload_succeeds__raises_selenium_fetch_failed():
    """_navigate_to_asset_page で元の処理が失敗した場合、S3 成功でも SeleniumAssetFetchFailed が raise される"""
    repo = AlwaysSucceedArtifactRepository()
    fetcher = _make_fetcher(repo)

    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(SeleniumAssetFetchFailed):
        fetcher._navigate_to_asset_page()

    assert len(repo.stored_keys) == 1
