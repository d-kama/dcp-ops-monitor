from aws_lambda_powertools.utilities.typing import LambdaContext

from src.application import CollectAssetDailyUseCase
from src.config import AssetFetchConfig, get_logger, get_settings
from src.domain import IFinancialAssetRepository
from src.infrastructure import (
    GoogleSheetFinancialAssetRepository,
    S3ErrorArtifactRepository,
    SeleniumAssetFetcher,
    get_ssm_json_parameter,
)
from src.presentation import Main

logger = get_logger()
settings = get_settings()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda handler エントリーポイント"""
    return Main(build_usecase()).run().model_dump()


def build_usecase() -> CollectAssetDailyUseCase:
    config = _build_fetch_config()
    return CollectAssetDailyUseCase(
        fetcher=SeleniumAssetFetcher(config=config),
        repository=_build_financial_asset_repository(),
        error_repo=S3ErrorArtifactRepository(settings.data_bucket_name),
        config=config,
    )


def _build_fetch_config() -> AssetFetchConfig:
    param = get_ssm_json_parameter(name=settings.asset_fetch_config_parameter_name, decrypt=True)
    return AssetFetchConfig(
        login_user_id=param["login_user_id"],
        login_password=param["login_password"],
        login_birthdate=param["login_birthdate"],
        start_url=param["start_url"],
        user_agent=settings.user_agent,
    )


def _build_financial_asset_repository() -> IFinancialAssetRepository:
    param = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
    return GoogleSheetFinancialAssetRepository(
        spreadsheet_id=param["spreadsheet_id"],
        sheet_name=param["sheet_name"],
        credentials=param["credentials"],
    )
