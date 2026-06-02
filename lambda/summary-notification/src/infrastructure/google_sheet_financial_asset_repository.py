from datetime import date, timedelta

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

from src.config import get_logger
from src.domain import (
    AssetRetrievalFailed,
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
    IFinancialAssetRepository,
)

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleSheetFinancialAssetRepository(IFinancialAssetRepository):
    """Google Spreadsheet から金融資産履歴を取得する読み取り実装"""

    HEADER_ROW = 1

    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.worksheet(sheet_name)

    def save_daily(self, daily_assets: FinancialAssetHistory) -> None:
        raise NotImplementedError("summary-notification は書き込みをサポートしません")

    # TODO: Repository内の最新日付からN日以内のデータを取得するようになっている。
    # 実行日付からN日以内のデータとするか、検討。併せて、結果が空配列になるケースも考える。
    def retrieve_from_with_days(self, days: int) -> FinancialAssetHistory:
        if days <= 0:
            raise ValueError(f"days must be positive: {days}")

        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                return FinancialAssetHistory(assets=[])

            latest_dt = date.fromisoformat(max(data_dates))
            cutoff_dt = latest_dt - timedelta(days=days)
            target_rows = [
                i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d and date.fromisoformat(d) > cutoff_dt
            ]
            history = self._batch_get_assets(headers, target_rows)
            logger.info("金融資産履歴を取得しました", extra={"days": days, "count": len(history.assets)})
            return history
        except (AssetRetrievalFailed, ValueError):
            raise
        except Exception as e:
            raise AssetRetrievalFailed.during_fetching() from e

    def _batch_get_assets(self, headers: list[str], target_rows: list[int]) -> FinancialAssetHistory:
        if not target_rows:
            return FinancialAssetHistory(assets=[])
        num_cols = len(headers)
        ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
        results = self.worksheet.batch_get(ranges)
        rows = [dict(zip(headers, row[0])) for row in results if row and row[0]]
        history = FinancialAssetHistory(assets=[])
        for r in rows:
            try:
                history = history.add(
                    FinancialAsset(
                        base_date=date.fromisoformat(r["date"]),
                        product_name=r["product"],
                        asset_valuation=AssetValuation(value=int(r["asset_valuation"])),
                        cumulative_contributions=CumulativeContributions(value=int(r["cumulative_contributions"])),
                        gains_or_losses=GainsOrLosses(value=int(r["gains_or_losses"])),
                    )
                )
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid data format in row {r}: {e}") from e
        return history
