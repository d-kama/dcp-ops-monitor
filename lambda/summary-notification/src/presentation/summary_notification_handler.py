from typing import Literal

from pydantic import BaseModel

from src.application import NotifyWeeklySummaryUseCase


class SummaryNotificationResult(BaseModel):
    status: Literal["Success"]


class Main:
    def __init__(self, usecase: NotifyWeeklySummaryUseCase) -> None:
        self.usecase = usecase

    def run(self) -> SummaryNotificationResult:
        self.usecase.execute()
        return SummaryNotificationResult(status="Success")
