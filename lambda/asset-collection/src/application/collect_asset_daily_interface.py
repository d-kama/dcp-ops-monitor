from abc import ABC, abstractmethod


class ICollectAssetDailyUseCase(ABC):
    @abstractmethod
    def execute(self) -> None:
        """資産運用状況ページからアセット情報を収集し、データストアへ保存する"""
