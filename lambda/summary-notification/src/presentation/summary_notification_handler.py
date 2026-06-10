from typing import Literal

from src.application import NotifyWeeklySummaryUseCase


class Main:
    def __init__(self, usecase: NotifyWeeklySummaryUseCase) -> None:
        self.usecase = usecase

    def run(self) -> Literal["Success"]:
        self.usecase.execute()
        return "Success"
