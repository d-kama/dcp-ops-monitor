"""Lambda handler エントリーポイント"""

from aws_lambda_powertools.utilities.typing import LambdaContext
from shared.domain.financial_asset_repository import IFinancialAssetRepository

from src.application import INotifier, INotifyWeeklySummaryUseCase, NotifyWeeklySummaryUseCase
from src.config.settings import EnvSettings, get_logger, get_settings
from src.infrastructure import (
    GoogleSheetFinancialAssetRepository,
    LineNotifier,
    get_ssm_json_parameter,
)
from src.presentation import Main

logger = get_logger()


def _build_financial_asset_repository(settings: EnvSettings) -> IFinancialAssetRepository:
    spreadsheet_parameter = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
    return GoogleSheetFinancialAssetRepository(
        spreadsheet_id=spreadsheet_parameter["spreadsheet_id"],
        sheet_name=spreadsheet_parameter["sheet_name"],
        credentials=spreadsheet_parameter["credentials"],
    )


def _build_notifier(settings: EnvSettings) -> INotifier:
    line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
    return LineNotifier(
        url=line_message_parameter["url"],
        token=line_message_parameter["token"],
    )


def build_usecase() -> INotifyWeeklySummaryUseCase:
    settings = get_settings()
    return NotifyWeeklySummaryUseCase(
        repository=_build_financial_asset_repository(settings),
        notifier=_build_notifier(settings),
    )


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント

    Args:
        event: Lambda イベント（EventBridge から空の dict）
        context: Lambda コンテキスト

    Returns:
        str | None: 成功時は "Success"
    """
    Main(build_usecase()).run()
    return "Success"
