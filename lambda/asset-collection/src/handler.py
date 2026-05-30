from aws_lambda_powertools.utilities.typing import LambdaContext

from src.config.settings import get_logger
from src.presentation.asset_collection_handler import main

logger = get_logger()


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext) -> str | None:
    """Lambda handler エントリーポイント"""
    main()
    return "Success"
