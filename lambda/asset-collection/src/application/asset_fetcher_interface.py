from abc import ABC, abstractmethod

from src.config import AssetFetchConfig
from src.domain import FinancialAssetHistory


class IAssetFetcher(ABC):
    """スクレイピングドライバー抽象クラス"""

    @abstractmethod
    def open_start_page(self, url: str) -> None: ...

    @abstractmethod
    def login(self, config: AssetFetchConfig) -> None: ...

    @abstractmethod
    def navigate_to_asset_page(self) -> None: ...

    @abstractmethod
    def extract(self) -> FinancialAssetHistory: ...

    @abstractmethod
    def logout(self) -> None:
        """logout 失敗時は例外を投げず、ログアウトできなかったことをログに記録する"""

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def capture_screenshot(self) -> str:
        """/tmp/ に保存したスクリーンショットのファイルパスを返す"""

    @abstractmethod
    def get_page_source(self) -> str:
        """/tmp/ に保存したページソース（HTML）のファイルパスを返す"""


class LoginError(Exception):
    pass


class NavigatePageError(Exception):
    pass


class ExtractError(Exception):
    pass
