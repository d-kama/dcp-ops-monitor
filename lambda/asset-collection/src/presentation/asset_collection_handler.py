from typing import Optional

from shared.domain.financial_asset_repository import IFinancialAssetRepository

from src.application import CollectAssetUseCase, IAssetFetcher, SaveAssetUseCase
from src.config import AssetFetchConfig
from src.config.settings import get_logger, get_settings
from src.infrastructure import (
    GoogleSheetFinancialAssetRepository,
    S3ErrorArtifactRepository,
    SeleniumAssetFetcher,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    fetcher: Optional[IAssetFetcher] = None,
    financial_asset_repository: Optional[IFinancialAssetRepository] = None,
) -> None:
    """メイン処理

    Args:
        fetcher (Optional[IAssetFetcher]): フェッチャー（テスト時にMockを注入可能）
        financial_asset_repository (Optional[IFinancialAssetRepository]): 金融資産リポジトリ（テスト時にMockを注入可能）

    Raises:
        ScrapingFailed: スクレイピングまたは資産情報抽出処理失敗時
        ArtifactUploadError: エラーアーティファクトの S3 保存失敗時
        AssetRecordError: 資産レコードの保存失敗時
    """
    if fetcher is None:
        asset_fetch_config_param = get_ssm_json_parameter(name=settings.asset_fetch_config_parameter_name, decrypt=True)
        config = AssetFetchConfig(
            login_user_id=asset_fetch_config_param["login_user_id"],
            login_password=asset_fetch_config_param["login_password"],
            login_birthdate=asset_fetch_config_param["login_birthdate"],
            start_url=asset_fetch_config_param["start_url"],
            user_agent=settings.user_agent,
        )
        fetcher = SeleniumAssetFetcher(config=config)

    if financial_asset_repository is None:
        spreadsheet_param = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
        financial_asset_repository = GoogleSheetFinancialAssetRepository(
            spreadsheet_id=spreadsheet_param["spreadsheet_id"],
            sheet_name=spreadsheet_param["sheet_name"],
            credentials=spreadsheet_param["credentials"],
        )

    error_repository = S3ErrorArtifactRepository(settings.data_bucket_name)

    asset_collection_usecase = CollectAssetUseCase(
        fetcher=fetcher,
        error_artifact_repository=error_repository,
    )
    save_asset_usecase = SaveAssetUseCase(repository=financial_asset_repository)

    history = asset_collection_usecase.collect()
    save_asset_usecase.save(history)
