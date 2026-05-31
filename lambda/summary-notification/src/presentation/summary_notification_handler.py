from typing import Literal

from src.application import INotifyWeeklySummaryUseCase


class Main:
    def __init__(self, usecase: INotifyWeeklySummaryUseCase) -> None:
        self.usecase = usecase

    def run(self) -> Literal["Success"]:
        self.usecase.execute()
        return "Success"
