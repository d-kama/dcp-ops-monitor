from datetime import datetime
from pathlib import Path

from src.config import AssetFetchConfig, get_logger
from src.domain import IFinancialAssetRepository

from .asset_fetcher_interface import ExtractError, IAssetFetcher, LoginError, NavigatePageError
from .collect_asset_daily_interface import ICollectAssetDailyUseCase
from .error_artifact_repository_interface import IErrorArtifactRepository

logger = get_logger()


class CollectAssetDailyUseCase(ICollectAssetDailyUseCase):
    def __init__(
        self,
        fetcher: IAssetFetcher,
        repository: IFinancialAssetRepository,
        error_repo: IErrorArtifactRepository,
        config: AssetFetchConfig,
    ) -> None:
        self.fetcher = fetcher
        self.repository = repository
        self.error_repo = error_repo
        self.config = config

    def execute(self) -> None:
        try:
            self.fetcher.open_start_page(self.config.start_url)

            try:
                self.fetcher.login(self.config)
            except Exception as e:
                logger.error("ログイン処理に失敗しました。", extra={"error": str(e)})
                self._store_artifact(self.fetcher.capture_screenshot())
                raise LoginError() from e

            try:
                self.fetcher.navigate_to_asset_page()
            except Exception as e:
                logger.error("資産評価額照会ページへの遷移に失敗しました。", extra={"error": str(e)})
                self._store_artifact(self.fetcher.capture_screenshot())
                raise NavigatePageError() from e

            try:
                daily_assets = self.fetcher.extract()
            except Exception as e:
                logger.error("資産情報の抽出に失敗しました。", extra={"error": str(e)})
                self._store_artifact(self.fetcher.get_page_source())
                raise ExtractError() from e

            self.repository.save_daily(daily_assets)
        finally:
            self.fetcher.logout()
            self.fetcher.close()

    def _store_artifact(self, file_path: str) -> None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = Path(file_path).suffix
        key = f"errors/{timestamp}{ext}"
        try:
            self.error_repo.store(key=key, file_path=file_path)
        except Exception as e:
            logger.warning("エラーアーティファクトの保存に失敗しました。", extra={"error": str(e)})
