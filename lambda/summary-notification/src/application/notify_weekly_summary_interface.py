from abc import ABC, abstractmethod


class INotifyWeeklySummaryUseCase(ABC):
    @abstractmethod
    def execute(self) -> None:
        """直近1週間の資産運用サマリを整形し通知する"""
