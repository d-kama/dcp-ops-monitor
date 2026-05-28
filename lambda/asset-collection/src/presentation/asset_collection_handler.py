from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from src.application import AssetCollectionUseCase, IAssetFetcher
from src.config import AssetFetchConfig
from src.config.settings import get_logger, get_settings
from src.domain import AssetRecord, IAssetRecordWriter
from src.infrastructure import (
    GoogleSheetAssetRecordRepository,
    S3ErrorArtifactRepository,
    SeleniumAssetFetcher,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    fetcher: Optional[IAssetFetcher] = None,
    asset_record_repository: Optional[IAssetRecordWriter] = None,
) -> None:
    """メイン処理

    Args:
        fetcher (Optional[IAssetFetcher]): フェッチャー（テスト時にMockを注入可能）
        asset_record_repository (Optional[IAssetRecordWriter]): 資産レコードライター（テスト時にMockを注入可能）

    Raises:
        ScrapingFailed: スクレイピングまたは資産情報抽出処理失敗時
        ArtifactUploadError: エラーアーティファクトの S3 保存失敗時
        AssetRecordError: 資産レコードの保存失敗時
    """
    # scraperが指定されていない場合のみ実装を使用
    if fetcher is None:
        scraping_parameter = get_ssm_json_parameter(name=settings.scraping_parameter_name, decrypt=True)
        config = AssetFetchConfig(
            login_user_id=scraping_parameter["login_user_id"],
            login_password=scraping_parameter["login_password"],
            login_birthdate=scraping_parameter["login_birthdate"],
            start_url=scraping_parameter["start_url"],
            user_agent=settings.user_agent,
        )
        fetcher = SeleniumAssetFetcher(config=config)

    if asset_record_repository is None:
        spreadsheet_param = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
        asset_record_repository = GoogleSheetAssetRecordRepository(
            spreadsheet_id=spreadsheet_param["spreadsheet_id"],
            sheet_name=spreadsheet_param["sheet_name"],
            credentials=spreadsheet_param["credentials"],
        )

    error_repository = S3ErrorArtifactRepository(settings.data_bucket_name)

    asset_collection_usecase = AssetCollectionUseCase(
        fetcher=fetcher,
        error_artifact_repository=error_repository,
    )
    products = asset_collection_usecase.collect()

    today = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    records = AssetRecord.from_asset_evaluations(target_date=today, products=products)
    asset_record_repository.save_daily_records(records)
