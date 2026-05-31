from typing import Literal

from src.application import ICollectDailyAssetUseCase


class Main:
    def __init__(self, usecase: ICollectDailyAssetUseCase):
        self.usecase = usecase

    def run(self) -> Literal["Success"]:
        self.usecase.execute()
        return "Success"
