"""サマリ通知ハンドラー"""

from src.application import INotifyWeeklySummaryUseCase


class Main:
    def __init__(self, usecase: INotifyWeeklySummaryUseCase) -> None:
        self.usecase = usecase

    def run(self) -> None:
        self.usecase.execute()
