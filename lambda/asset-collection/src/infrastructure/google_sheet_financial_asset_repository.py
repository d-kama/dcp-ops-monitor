import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption

from src.config import get_logger
from src.domain import AssetSaveError, FinancialAssetHistory, IFinancialAssetRepository

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetFinancialAssetRepository(IFinancialAssetRepository):
    """Google Spreadsheet を使った IFinancialAssetRepository 実装"""

    def __init__(self, spreadsheet_id: str, sheet_name: str, credentials: dict) -> None:
        creds = Credentials.from_service_account_info(credentials, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.worksheet(sheet_name)

    def save_daily(self, daily_assets: FinancialAssetHistory) -> None:
        """1日分の金融資産履歴をスプレッドシートに保存する

        Raises:
            AssetSaveError: 保存失敗時
        """
        if not daily_assets.assets:
            return

        try:
            # TODO: 複数日付チェックは FinancialAssetHistory のメソッドに移動する
            base_dates = {asset.base_date for asset in daily_assets.assets}
            if len(base_dates) > 1:
                raise AssetSaveError(f"save_daily に複数日付の資産が含まれています: {base_dates}")

            target_date = str(daily_assets.assets[0].base_date)
            self._delete_existing_rows(target_date)
            self._append_assets(daily_assets)
            logger.info("金融資産履歴を保存しました", extra={"date": target_date, "count": len(daily_assets.assets)})
        except AssetSaveError:
            raise
        except Exception as e:
            raise AssetSaveError(f"金融資産履歴の保存に失敗しました: {e}") from e

    def _delete_existing_rows(self, target_date: str) -> None:
        """対象日付の既存行を削除する"""
        date_column = self.worksheet.col_values(1)
        rows_to_delete = [i + 1 for i, val in enumerate(date_column) if val == target_date]

        for row_index in reversed(rows_to_delete):
            self.worksheet.delete_rows(row_index)

        if rows_to_delete:
            logger.info("既存行を削除しました", extra={"date": target_date, "count": len(rows_to_delete)})

    def retrieve_from_with_days(self, days: int) -> FinancialAssetHistory:
        raise NotImplementedError("asset-collection は読み取りをサポートしません")

    def _append_assets(self, daily_assets: FinancialAssetHistory) -> None:
        """資産レコードを末尾に追記する"""
        rows = [
            [
                str(asset.base_date),
                asset.product_name,
                asset.asset_valuation.value,
                asset.cumulative_contributions.value,
                asset.gains_or_losses.value,
            ]
            for asset in daily_assets.assets
        ]
        self.worksheet.append_rows(rows, value_input_option=ValueInputOption.raw)
