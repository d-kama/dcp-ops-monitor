"""Domain レイヤー: モデル、インターフェース、例外"""

from shared.domain.asset_evaluation import AssetEvaluation
from shared.domain.asset_record import AssetRecord
from shared.domain.asset_record_repository import IAssetRecordRepository
from shared.domain.exceptions import AssetRecordError

from .artifact_repository import IArtifactRepository
from .exceptions import (
    ArtifactUploadError,
    ScrapingFailed,
    WebScrapingFailed,
)
from .scraper import IScraper

__all__ = [
    # Models
    "AssetEvaluation",
    "AssetRecord",
    # Interfaces
    "IScraper",
    "IArtifactRepository",
    "IAssetRecordRepository",
    # Exceptions
    "ArtifactUploadError",
    "ScrapingFailed",
    "WebScrapingFailed",
    "AssetRecordError",
]
