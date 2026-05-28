from abc import ABC, abstractmethod
from typing import Self


class INotifier(ABC):
    """通知インターフェース（LINE非依存）"""

    @abstractmethod
    def notify(self, messages: list[str]) -> None:
        """通知を送信

        Args:
            messages: 通知メッセージリスト

        Raises:
            NotificationFailed: 通知送信失敗時
        """
        pass


class NotificationFailed(Exception):
    """通知送信エラー"""

    @classmethod
    def during_request(cls) -> Self:
        """通知送信中にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信中にエラーが発生しました")

    @classmethod
    def before_request(cls) -> Self:
        """通知送信前にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            NotificationFailed: 生成された例外インスタンス
        """
        return cls("通知送信前にエラーが発生しました")
