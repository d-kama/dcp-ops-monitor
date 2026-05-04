from collections.abc import Iterable
from datetime import date
from typing import Self

from pydantic import BaseModel

from shared.domain.asset_evaluation import AssetEvaluation


class AssetRecord(BaseModel):
    """商品別のフラットな資産レコード"""

    date: date
    product: str
    asset_valuation: int
    cumulative_contributions: int
    gains_or_losses: int

    @classmethod
    def to_evaluation_map(cls, records: Iterable[Self]) -> dict[str, AssetEvaluation]:
        """AssetRecord の iterable から 商品名 → AssetEvaluation のマッピングを生成する

        前提:
        - 入力されるレコードは同一日付のものとする（日付チェックは行わない、呼び出し側責務）
        - 商品名（product）が重複する場合は最後のレコードで上書きされる
          （実運用上は write 側の日付単位 upsert により重複は発生しない）
        - 空入力の場合は空 dict を返す（呼び出し側で空を判定し例外送出する）
        """
        return {
            r.product: AssetEvaluation(
                cumulative_contributions=r.cumulative_contributions,
                gains_or_losses=r.gains_or_losses,
                asset_valuation=r.asset_valuation,
            )
            for r in records
        }

    @classmethod
    def from_asset_evaluations(
        cls,
        target_date: date,
        products: dict[str, AssetEvaluation],
    ) -> list[Self]:
        """商品別 AssetEvaluation から AssetRecord のリストを生成する"""
        return [
            cls(
                date=target_date,
                product=product_name,
                asset_valuation=info.asset_valuation,
                cumulative_contributions=info.cumulative_contributions,
                gains_or_losses=info.gains_or_losses,
            )
            for product_name, info in products.items()
        ]
