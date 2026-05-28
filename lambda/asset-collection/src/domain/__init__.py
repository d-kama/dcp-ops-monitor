"""Domain レイヤー: モデル、インターフェース、例外"""

from shared.domain.asset_evaluation import AssetEvaluation
from shared.domain.asset_record import AssetRecord
from shared.domain.exceptions import AssetRecordError

from .asset_record_writer import IAssetRecordWriter
from .exceptions import (
    AssetCollectionFailed,
    ScrapingFailed,
)
from .scraper import IScraper

__all__ = [
    # Models
    "AssetEvaluation",
    "AssetRecord",
    # Interfaces
    "IScraper",
    "IAssetRecordWriter",
    # Exceptions
    "ScrapingFailed",
    "AssetCollectionFailed",
    "AssetRecordError",
]
