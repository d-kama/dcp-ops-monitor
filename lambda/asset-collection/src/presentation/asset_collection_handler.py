from typing import Literal

from pydantic import BaseModel

from src.application import CollectAssetDailyUseCase


class AssetCollectionResult(BaseModel):
    status: Literal["Success"]


class Main:
    def __init__(self, usecase: CollectAssetDailyUseCase):
        self.usecase = usecase

    def run(self) -> AssetCollectionResult:
        self.usecase.execute()
        return AssetCollectionResult(status="Success")
