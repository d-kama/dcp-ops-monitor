import pytest

from src.application import NotifySummaryUseCase
from src.application.notifier import NotificationFailed
from tests.fixtures.mocks import MockNotifier


class TestNotifySummaryUseCase:
    def test_notify__calls_notifier(self):
        """notifier.notify() が呼ばれる"""
        notifier = MockNotifier()
        usecase = NotifySummaryUseCase(notifier=notifier)

        usecase.notify("テストメッセージ")

        assert notifier.notify_called

    def test_notify__sends_single_message(self):
        """notifier に渡されるメッセージはちょうど1件"""
        notifier = MockNotifier()
        usecase = NotifySummaryUseCase(notifier=notifier)

        usecase.notify("テストメッセージ")

        assert len(notifier.messages_sent) == 1

    def test_notify__passes_message_as_is(self):
        """受け取ったメッセージをそのまま notifier に渡す"""
        notifier = MockNotifier()
        usecase = NotifySummaryUseCase(notifier=notifier)

        usecase.notify("確定拠出年金 運用状況通知Bot")

        assert notifier.messages_sent[0] == "確定拠出年金 運用状況通知Bot"

    def test_notify__propagates_notification_failed(self):
        """notifier が NotificationFailed を送出した場合は伝播する"""

        class FailingNotifier(MockNotifier):
            def notify(self, messages):
                raise NotificationFailed.during_request()

        usecase = NotifySummaryUseCase(notifier=FailingNotifier())

        with pytest.raises(NotificationFailed):
            usecase.notify("テストメッセージ")
