from src.application.notifier import INotifier


class NotifySummaryUseCase:
    def __init__(self, notifier: INotifier) -> None:
        self.notifier = notifier

    def execute(self, message: str) -> None:
        self.notifier.notify([message])
