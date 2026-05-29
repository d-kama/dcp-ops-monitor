"""サマリ通知ハンドラー"""

from shared.domain.financial_asset_repository import IFinancialAssetRepository

from src.application import (
    FormatMessageUseCase,
    INotifier,
    NotifySummaryUseCase,
    RetrieveAssetUseCase,
    SummariseAssetUseCase,
)
from src.config.settings import get_logger, get_settings
from src.infrastructure import (
    GoogleSheetFinancialAssetRepository,
    LineNotifier,
    get_ssm_json_parameter,
)

settings = get_settings()
logger = get_logger()


def main(
    asset_repository: IFinancialAssetRepository | None = None,
    notifier: INotifier | None = None,
) -> None:
    """メイン処理

    Args:
        asset_repository: 金融資産リポジトリ (テスト時に Mock 注入可能)
        notifier: 通知クライアント (テスト時に Mock 注入可能)
    """
    if asset_repository is None:
        spreadsheet_parameter = get_ssm_json_parameter(name=settings.spreadsheet_parameter_name, decrypt=True)
        asset_repository = GoogleSheetFinancialAssetRepository(
            spreadsheet_id=spreadsheet_parameter["spreadsheet_id"],
            sheet_name=spreadsheet_parameter["sheet_name"],
            credentials=spreadsheet_parameter["credentials"],
        )

    if notifier is None:
        line_message_parameter = get_ssm_json_parameter(name=settings.line_message_parameter_name, decrypt=True)
        notifier = LineNotifier(
            url=line_message_parameter["url"],
            token=line_message_parameter["token"],
        )

    history = RetrieveAssetUseCase(repository=asset_repository).retrieve()
    summary = SummariseAssetUseCase().summarise(history)
    message = FormatMessageUseCase().format(summary)
    NotifySummaryUseCase(notifier=notifier).notify(message)
    logger.info("サマリ通知処理が完了しました")
