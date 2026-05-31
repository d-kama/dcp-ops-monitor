from abc import ABC, abstractmethod
from typing import Literal


class ICollectDailyAssetUseCase(ABC):
    @abstractmethod
    def execute(self) -> Literal["Success"]:
        """資産運用状況ページからアセット情報を収集し、データストアへ保存する"""
