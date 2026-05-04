from datetime import date

from shared.domain.asset_record import AssetRecord


class TestToEvaluationMap:
    def test_to_evaluation_map__single_record_returns_single_mapping(self):
        """1 件入力で 1 件のマッピングが返る"""
        records = [
            AssetRecord(
                date=date(2026, 1, 1),
                product="国内株式",
                asset_valuation=300_000,
                cumulative_contributions=200_000,
                gains_or_losses=100_000,
            )
        ]
        result = AssetRecord.to_evaluation_map(records)
        assert len(result) == 1
        assert "国内株式" in result
        assert result["国内株式"].asset_valuation == 300_000
        assert result["国内株式"].cumulative_contributions == 200_000
        assert result["国内株式"].gains_or_losses == 100_000

    def test_to_evaluation_map__multiple_products_returns_mapping_per_product(self):
        """複数商品の入力で全件マッピングが返る"""
        records = [
            AssetRecord(
                date=date(2026, 1, 1),
                product="国内株式",
                asset_valuation=300_000,
                cumulative_contributions=200_000,
                gains_or_losses=100_000,
            ),
            AssetRecord(
                date=date(2026, 1, 1),
                product="外国株式",
                asset_valuation=500_000,
                cumulative_contributions=400_000,
                gains_or_losses=100_000,
            ),
        ]
        result = AssetRecord.to_evaluation_map(records)
        assert len(result) == 2
        assert result["国内株式"].asset_valuation == 300_000
        assert result["外国株式"].asset_valuation == 500_000

    def test_to_evaluation_map__empty_returns_empty_dict(self):
        """空入力で空 dict が返る"""
        result = AssetRecord.to_evaluation_map([])
        assert result == {}

    def test_to_evaluation_map__duplicate_product_keeps_last(self):
        """同一 product 重複時に最後の値が残る"""
        records = [
            AssetRecord(
                date=date(2026, 1, 1),
                product="国内株式",
                asset_valuation=300_000,
                cumulative_contributions=200_000,
                gains_or_losses=100_000,
            ),
            AssetRecord(
                date=date(2026, 1, 1),
                product="国内株式",
                asset_valuation=350_000,
                cumulative_contributions=210_000,
                gains_or_losses=140_000,
            ),
        ]
        result = AssetRecord.to_evaluation_map(records)
        assert len(result) == 1
        assert result["国内株式"].asset_valuation == 350_000
        assert result["国内株式"].cumulative_contributions == 210_000
        assert result["国内株式"].gains_or_losses == 140_000
