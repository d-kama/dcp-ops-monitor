from shared.domain.financial_asset import FinancialAssetHistory
from shared.domain.financial_asset_repository import IFinancialAssetRepository


class SaveAssetUseCase:
    def __init__(self, repository: IFinancialAssetRepository) -> None:
        self.repository = repository

    def save(self, history: FinancialAssetHistory) -> None:
        self.repository.save_daily(history)
