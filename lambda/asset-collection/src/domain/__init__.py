"""Domain レイヤー: モデル、インターフェース、例外"""

from shared.domain.exceptions import AssetRecordError
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)
from shared.domain.financial_asset_repository import IFinancialAssetRepository

from .exceptions import (
    AssetCollectionFailed,
    ScrapingFailed,
)

__all__ = [
    # Models
    "AssetValuation",
    "CumulativeContributions",
    "FinancialAsset",
    "FinancialAssetHistory",
    "GainsOrLosses",
    # Interfaces
    "IFinancialAssetRepository",
    # Exceptions
    "ScrapingFailed",
    "AssetCollectionFailed",
    "AssetRecordError",
]
