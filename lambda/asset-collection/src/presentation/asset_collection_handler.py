from typing import Literal

from src.application import CollectAssetDailyUseCase


class Main:
    def __init__(self, usecase: CollectAssetDailyUseCase):
        self.usecase = usecase

    def run(self) -> Literal["Success"]:
        self.usecase.execute()
        return "Success"
