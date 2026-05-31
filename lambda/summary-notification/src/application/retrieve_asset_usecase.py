from shared.domain.financial_asset import FinancialAssetHistory
from shared.domain.financial_asset_repository import IFinancialAssetRepository


class RetrieveAssetUseCase:
    DAYS = 7

    def __init__(self, repository: IFinancialAssetRepository) -> None:
        self.repository = repository

    def execute(self) -> FinancialAssetHistory:
        return self.repository.retrieve_from_with_days(self.DAYS)
