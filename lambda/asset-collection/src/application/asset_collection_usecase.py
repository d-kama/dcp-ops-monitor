from datetime import datetime

from shared.domain.financial_asset import FinancialAssetHistory

from src.config.settings import get_logger
from src.domain import ScrapingFailed

from .asset_fetcher_interface import IAssetFetcher
from .error_artifact_repository import IErrorArtifactRepository

logger = get_logger()


class AssetCollectionUseCase:
    def __init__(
        self,
        fetcher: IAssetFetcher,
        error_artifact_repository: IErrorArtifactRepository,
    ) -> None:
        self.fetcher: IAssetFetcher = fetcher
        self.error_artifact_repository: IErrorArtifactRepository = error_artifact_repository

    def collect(self) -> FinancialAssetHistory:
        try:
            return self.fetcher.fetch_asset_valuation()
        except ScrapingFailed as e:
            self._upload_error_artifacts(e)
            raise

    def _upload_error_artifacts(self, e: ScrapingFailed) -> None:
        """エラーアーティファクトを S3 にアップロードする"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if e.tmp_screenshot_path:
            logger.info("エラー画像のアップロード開始")
            key = f"errors/{timestamp}.png"
            self.error_artifact_repository.store(key=key, file_path=e.tmp_screenshot_path)
            logger.info("エラー画像をアップロードしました。", extra={"error_screenshot_key": key})
            e.error_screenshot_key = key

        if e.tmp_html_path:
            logger.info("エラーになった資産情報 HTML ファイルのアップロード開始")
            key = f"errors/{timestamp}.html"
            self.error_artifact_repository.store(key=key, file_path=e.tmp_html_path)
            logger.info("資産情報 HTML ファイルをアップロードしました。", extra={"error_html_key": key})
            e.error_html_key = key
