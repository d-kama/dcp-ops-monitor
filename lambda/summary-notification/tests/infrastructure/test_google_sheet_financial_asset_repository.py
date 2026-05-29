"""GoogleSheetFinancialAssetRepository のテスト"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from shared.domain.financial_asset import (
    AssetValuation,
    CumulativeContributions,
    FinancialAsset,
    FinancialAssetHistory,
    GainsOrLosses,
)

from src.domain import AssetRetrievalFailed
from src.infrastructure import GoogleSheetFinancialAssetRepository

SPREADSHEET_ID = "test-spreadsheet-id"
SHEET_NAME = "test-sheet"
CREDENTIALS = {"type": "service_account", "project_id": "test"}

HEADERS = ["date", "product", "asset_valuation", "cumulative_contributions", "gains_or_losses"]


def _make_row(d: str, product: str, av: int, cc: int, gl: int) -> list[str]:
    return [d, product, str(av), str(cc), str(gl)]


@pytest.fixture
def mock_worksheet():
    return MagicMock()


@pytest.fixture
def repository(mock_worksheet):
    with (
        patch("src.infrastructure.google_sheet_financial_asset_repository.gspread") as mock_gspread,
        patch("src.infrastructure.google_sheet_financial_asset_repository.Credentials"),
    ):
        mock_gspread.authorize.return_value.open_by_key.return_value.worksheet.return_value = mock_worksheet
        repo = GoogleSheetFinancialAssetRepository(
            spreadsheet_id=SPREADSHEET_ID,
            sheet_name=SHEET_NAME,
            credentials=CREDENTIALS,
        )
        repo.worksheet = mock_worksheet
        yield repo


class TestRetrieveFromWithDays:
    def test_retrieve_from_with_days__returns_assets_within_range(self, repository, mock_worksheet):
        """直近 N 日以内の資産レコードが FinancialAssetHistory として返る"""
        mock_worksheet.row_values.return_value = HEADERS
        mock_worksheet.col_values.return_value = ["date", "2025-01-10", "2025-01-09", "2025-01-05"]
        mock_worksheet.batch_get.return_value = [
            [_make_row("2025-01-10", "Product A", 1_000_000, 900_000, 100_000)],
            [_make_row("2025-01-09", "Product A", 990_000, 900_000, 90_000)],
        ]

        result = repository.retrieve_from_with_days(days=7)

        assert isinstance(result, FinancialAssetHistory)
        assert len(result.assets) == 2
        asset = result.assets[0]
        assert asset.base_date == date(2025, 1, 10)
        assert asset.product_name == "Product A"
        assert asset.asset_valuation == AssetValuation(value=1_000_000)
        assert asset.cumulative_contributions == CumulativeContributions(value=900_000)
        assert asset.gains_or_losses == GainsOrLosses(value=100_000)

    def test_retrieve_from_with_days__empty_sheet_returns_empty_history(self, repository, mock_worksheet):
        """シートが空の場合は空の FinancialAssetHistory を返す"""
        mock_worksheet.row_values.return_value = HEADERS
        mock_worksheet.col_values.return_value = ["date"]

        result = repository.retrieve_from_with_days(days=7)

        assert result == FinancialAssetHistory(assets=[])
        mock_worksheet.batch_get.assert_not_called()

    def test_retrieve_from_with_days__no_rows_in_range_returns_empty_history(self, repository, mock_worksheet):
        """指定日数内にデータがない場合は空の FinancialAssetHistory を返す"""
        mock_worksheet.row_values.return_value = HEADERS
        mock_worksheet.col_values.return_value = ["date", "2025-01-01"]
        mock_worksheet.batch_get.return_value = []

        result = repository.retrieve_from_with_days(days=1)

        assert result == FinancialAssetHistory(assets=[])

    def test_retrieve_from_with_days__days_zero_raises_value_error(self, repository):
        """days=0 は ValueError を送出する"""
        with pytest.raises(ValueError, match="days must be positive"):
            repository.retrieve_from_with_days(days=0)

    def test_retrieve_from_with_days__days_negative_raises_value_error(self, repository):
        """days が負の値の場合も ValueError を送出する"""
        with pytest.raises(ValueError, match="days must be positive"):
            repository.retrieve_from_with_days(days=-1)

    def test_retrieve_from_with_days__gspread_error_raises_asset_retrieval_failed(self, repository, mock_worksheet):
        """gspread 例外発生時は AssetRetrievalFailed を送出する"""
        import gspread

        mock_worksheet.row_values.side_effect = gspread.exceptions.GSpreadException("API error")

        with pytest.raises(AssetRetrievalFailed):
            repository.retrieve_from_with_days(days=7)

    def test_retrieve_from_with_days__multiple_products_per_date(self, repository, mock_worksheet):
        """同一日付に複数商品がある場合もすべて返る"""
        mock_worksheet.row_values.return_value = HEADERS
        mock_worksheet.col_values.return_value = ["date", "2025-01-10", "2025-01-10"]
        mock_worksheet.batch_get.return_value = [
            [_make_row("2025-01-10", "Product A", 600_000, 500_000, 100_000)],
            [_make_row("2025-01-10", "Product B", 400_000, 350_000, 50_000)],
        ]

        result = repository.retrieve_from_with_days(days=3)

        assert len(result.assets) == 2
        product_names = {a.product_name for a in result.assets}
        assert product_names == {"Product A", "Product B"}


class TestSaveDaily:
    def test_save_daily__raises_not_implemented_error(self, repository):
        """save_daily は NotImplementedError を送出する"""
        history = FinancialAssetHistory(
            assets=[
                FinancialAsset(
                    base_date=date(2025, 1, 10),
                    product_name="Product A",
                    asset_valuation=AssetValuation(value=1_000_000),
                    cumulative_contributions=CumulativeContributions(value=900_000),
                    gains_or_losses=GainsOrLosses(value=100_000),
                )
            ]
        )
        with pytest.raises(NotImplementedError):
            repository.save_daily(history)
