"""サマリ通知サービス"""

from datetime import date

from src.config.settings import get_logger
from src.domain import (
    AssetEvaluation,
    AssetRecord,
    AssetRetrievalFailed,
    IAssetRecordReader,
    INotifier,
    calculate_ops_indicators,
)

from .message_formatter import format_summary_message

logger = get_logger()


class SummaryNotificationService:
    """サマリ通知サービス"""

    def __init__(
        self,
        asset_repository: IAssetRecordReader,
        notifier: INotifier,
    ) -> None:
        """サマリ通知サービスを初期化

        Args:
            asset_repository: 資産レコードリーダ
            notifier: 通知クライアント
        """
        self.asset_repository = asset_repository
        self.notifier = notifier

    def send_summary(self) -> None:
        """サマリ通知を送信

        最新の資産情報を取得し、運用指標を計算してメッセージを生成・送信する。

        Raises:
            AssetRetrievalFailed: 資産情報が見つからない場合
            NotificationFailed: 通知送信失敗時
        """
        latest_records = self.asset_repository.get_latest_records()
        products = AssetRecord.to_evaluation_map(latest_records)
        if not products:
            raise AssetRetrievalFailed.no_assets_in_spreadsheet()

        total = AssetEvaluation.aggregate(products.values())
        logger.info("資産情報を取得しました")

        indicators = calculate_ops_indicators(total)
        logger.info("運用指標を計算しました", indicators=indicators.model_dump())

        weekly_records = self.asset_repository.get_records_within_days(days=7)
        weekly_valuations = self._calculate_weekly_valuations(weekly_records)

        message_text = format_summary_message(total, indicators, weekly_valuations)

        self.notifier.notify([message_text])
        logger.info("サマリ通知を送信しました")

    @staticmethod
    def _calculate_weekly_valuations(
        weekly_records: list[AssetRecord],
    ) -> list[tuple[date, int, int | None]]:
        """週次レコードから日毎の資産評価額と前日比を算出する

        1. 日付単位にグルーピング
        2. 各日について AssetRecord.to_evaluation_map → aggregate で日次合計を取得
        3. 日付昇順で前日比を計算し、最後に降順に反転して返す

        Args:
            weekly_records: 週次の資産レコードリスト

        Returns:
            (日付, 資産評価額, 前日比 or None) のリスト（新しい日付順）
        """
        records_by_date: dict[date, list[AssetRecord]] = {}
        for record in weekly_records:
            records_by_date.setdefault(record.date, []).append(record)

        valuations: dict[date, int] = {}
        for d in sorted(records_by_date.keys()):
            day_products = AssetRecord.to_evaluation_map(records_by_date[d])
            valuations[d] = AssetEvaluation.aggregate(day_products.values()).asset_valuation

        result: list[tuple[date, int, int | None]] = []
        prev_valuation: int | None = None
        for d, valuation in valuations.items():
            diff = None if prev_valuation is None else valuation - prev_valuation
            result.append((d, valuation, diff))
            prev_valuation = valuation
        return list(reversed(result))
