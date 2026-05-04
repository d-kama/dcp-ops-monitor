"""Google Spreadsheet 資産レコード読み取り実装（summary-notification 用）"""

from datetime import date, timedelta

import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
from shared.domain.asset_record import AssetRecord

from src.config.settings import get_logger
from src.domain import AssetRetrievalFailed, IAssetRecordReader

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class GoogleSheetAssetRecordReader(IAssetRecordReader):
    """Google Spreadsheet から資産レコードを取得する読み取り実装"""

    HEADER_ROW = 1

    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.worksheet(sheet_name)

    def get_latest_records(self) -> list[AssetRecord]:
        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                return []

            latest_date = max(data_dates)
            logger.info("最新の資産レコードを取得します", extra={"date": latest_date})

            target_rows = [i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d == latest_date]
            return self._batch_get_records(headers, target_rows)
        except Exception as e:
            raise AssetRetrievalFailed.during_fetching() from e

    def get_records_within_days(self, days: int) -> list[AssetRecord]:
        if days <= 0:
            raise ValueError(f"days must be positive: {days}")

        try:
            headers = self.worksheet.row_values(self.HEADER_ROW)
            date_col = headers.index("date") + 1
            date_values = self.worksheet.col_values(date_col)
            data_dates = date_values[self.HEADER_ROW :]

            if not data_dates:
                return []

            latest_dt = date.fromisoformat(max(data_dates))
            cutoff_dt = latest_dt - timedelta(days=days)
            target_rows = [
                i + self.HEADER_ROW + 1 for i, d in enumerate(data_dates) if d and date.fromisoformat(d) > cutoff_dt
            ]
            return self._batch_get_records(headers, target_rows)
        except Exception as e:
            raise AssetRetrievalFailed.during_fetching() from e

    def _batch_get_records(self, headers: list[str], target_rows: list[int]) -> list[AssetRecord]:
        if not target_rows:
            return []
        num_cols = len(headers)
        ranges = [f"{rowcol_to_a1(row, 1)}:{rowcol_to_a1(row, num_cols)}" for row in target_rows]
        results = self.worksheet.batch_get(ranges)
        rows = [dict(zip(headers, row[0])) for row in results if row and row[0]]
        records = []
        for r in rows:
            try:
                records.append(
                    AssetRecord(
                        date=date.fromisoformat(r["date"]),
                        product=r["product"],
                        asset_valuation=int(r["asset_valuation"]),
                        cumulative_contributions=int(r["cumulative_contributions"]),
                        gains_or_losses=int(r["gains_or_losses"]),
                    )
                )
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid data format in row {r}: {e}") from e
        return records
