from typing import Literal

from src.application import ICollectAssetDailyUseCase


class Main:
    def __init__(self, usecase: ICollectAssetDailyUseCase):
        self.usecase = usecase

    def run(self) -> Literal["Success"]:
        self.usecase.execute()
        return "Success"
