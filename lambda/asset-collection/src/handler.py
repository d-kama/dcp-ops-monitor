from aws_lambda_powertools.utilities.typing import LambdaContext
from shared.domain.financial_asset_repository import IFinancialAssetRepository

from src.application import CollectAssetDailyUseCase, IAssetFetcher
from src.config import AssetFetchConfig, get_logger, get_settings
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
def handler(event: dict, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント"""
    return Main(build_usecase()).run()


def build_usecase():
    return CollectAssetDailyUseCase(
        fetcher=_build_fetcher(),
        repository=_build_financial_asset_repository(),
    )


def _build_fetcher() -> IAssetFetcher:
    param = get_ssm_json_parameter(name=settings.asset_fetch_config_parameter_name, decrypt=True)
    config = AssetFetchConfig(
        login_user_id=param["login_user_id"],
        login_password=param["login_password"],
        login_birthdate=param["login_birthdate"],
        start_url=param["start_url"],
        user_agent=settings.user_agent,
    )
    error_repository = S3ErrorArtifactRepository(settings.data_bucket_name)
    return SeleniumAssetFetcher(config=config, error_repo=error_repository)


def _build_financial_asset_repository() -> IFinancialAssetRepository:
    param = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
    return GoogleSheetFinancialAssetRepository(
        spreadsheet_id=param["spreadsheet_id"],
        sheet_name=param["sheet_name"],
        credentials=param["credentials"],
    )
