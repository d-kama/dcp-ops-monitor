"""SeleniumAssetFetcher の単体テスト

SeleniumWebDriver 自体は pytest-mock でパッチし、
新インターフェース（open_start_page / login / navigate_to_asset_page /
extract / logout / close / capture_screenshot / get_page_source）の
動作を検証する。

エラーハンドリングは Infrastructure 層では行わないため、
Selenium 例外がそのまま伝播することを確認する。
"""

from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.selenium_asset_fetcher import SeleniumAssetFetcher


def _make_fetcher() -> SeleniumAssetFetcher:
    """SeleniumAssetFetcher を driver 初期化なしで生成するヘルパー"""
    config = MagicMock()
    config.user_agent = "test-agent"
    config.login_user_id.get_secret_value.return_value = "user"
    config.login_password.get_secret_value.return_value = "pass"
    config.login_birthdate.get_secret_value.return_value = "19900101"
    config.start_url = "http://example.com"

    with patch.object(SeleniumAssetFetcher, "_get_driver", return_value=MagicMock()):
        fetcher = SeleniumAssetFetcher(config=config)

    return fetcher


# ---------- open_start_page ----------


def test_open_start_page__calls_driver_get():
    """open_start_page は driver.get(url) を呼ぶ"""
    fetcher = _make_fetcher()
    fetcher.open_start_page("http://example.com")
    fetcher.driver.get.assert_called_once_with("http://example.com")


# ---------- login ----------


def test_login__calls_driver_operations():
    """login() が WebDriver の find_element / send_keys / submit を正しく呼ぶ"""
    fetcher = _make_fetcher()
    config = MagicMock()
    config.login_user_id.get_secret_value.return_value = "user"
    config.login_password.get_secret_value.return_value = "pass"
    config.login_birthdate.get_secret_value.return_value = "19900101"

    fetcher.login(config)

    assert fetcher.driver.find_element.called


def test_login__selenium_fails__raises_raw_exception():
    """login で Selenium 操作が失敗した場合、生の例外がそのまま raise される"""
    fetcher = _make_fetcher()
    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(Exception, match="element not found"):
        fetcher.login(config=MagicMock())


# ---------- navigate_to_asset_page ----------


def test_navigate_to_asset_page__selenium_fails__raises_raw_exception():
    """navigate_to_asset_page で Selenium 操作が失敗した場合、生の例外がそのまま raise される"""
    fetcher = _make_fetcher()
    fetcher.driver.find_element.side_effect = Exception("element not found")

    with pytest.raises(Exception, match="element not found"):
        fetcher.navigate_to_asset_page()


# ---------- logout ----------


def test_logout__selenium_fails__does_not_raise():
    """logout はベストエフォート: Selenium 例外が発生しても raise しない"""
    fetcher = _make_fetcher()
    fetcher.driver.find_element.side_effect = Exception("logout element not found")

    # 例外が raise されないことを確認
    fetcher.logout()


# ---------- close ----------


def test_close__calls_driver_quit():
    """close は driver.quit() を呼ぶ"""
    fetcher = _make_fetcher()
    fetcher.close()
    fetcher.driver.quit.assert_called_once()


# ---------- capture_screenshot ----------


def test_capture_screenshot__returns_file_path():
    """capture_screenshot は /tmp/screenshot_*.png のパスを返す"""
    fetcher = _make_fetcher()
    fetcher.driver.save_screenshot = MagicMock()

    path = fetcher.capture_screenshot()

    assert path.startswith("/tmp/screenshot_")
    assert path.endswith(".png")
    fetcher.driver.save_screenshot.assert_called_once_with(path)


# ---------- get_page_source ----------


def test_get_page_source__returns_file_path(tmp_path, monkeypatch):
    """get_page_source は /tmp/page_source_*.html のパスを返す"""
    fetcher = _make_fetcher()
    fetcher.driver.page_source = "<html><body>test</body></html>"

    # /tmp への実際の書き込みを避けるため monkeypatch で open を置換
    written_paths = []
    original_open = open

    def mock_open(path, *args, **kwargs):
        written_paths.append(path)
        return original_open(str(tmp_path / "page_source.html"), *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    path = fetcher.get_page_source()

    assert path.startswith("/tmp/page_source_")
    assert path.endswith(".html")
    assert len(written_paths) == 1


# ---------- SeleniumAssetFetchFailed は存在しない ----------


def test_selenium_asset_fetch_failed__not_exported():
    """SeleniumAssetFetchFailed は削除されており import できない"""
    import importlib

    import src.infrastructure.selenium_asset_fetcher as module

    assert not hasattr(module, "SeleniumAssetFetchFailed")
