from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from shared.domain.asset_record import AssetRecord


class AssetEvaluation(BaseModel):
    """確定拠出年金の資産評価を扱う値クラス

    Attributes:
        cumulative_contributions (int): 拠出金額累計
        gains_or_losses (int): 評価損益
        asset_valuation (int): 資産評価額
    """

    cumulative_contributions: int
    gains_or_losses: int
    asset_valuation: int

    @classmethod
    def aggregate(cls, evaluations: Iterable["AssetEvaluation"]) -> "AssetEvaluation":
        """複数の AssetEvaluation を合算して単一の AssetEvaluation を生成する"""
        items = list(evaluations)
        return cls(
            cumulative_contributions=sum(e.cumulative_contributions for e in items),
            gains_or_losses=sum(e.gains_or_losses for e in items),
            asset_valuation=sum(e.asset_valuation for e in items),
        )

    @classmethod
    def from_html_strings(
        cls,
        cumulative_contributions_str: str,
        gains_or_losses_str: str,
        asset_valuation_str: str,
    ) -> "AssetEvaluation":
        """HTML から取得した文字列から AssetEvaluation を生成

        Args:
            cumulative_contributions_str: 拠出金額累計の文字列（例: "1,234,567円"）
            gains_or_losses_str: 評価損益の文字列
            asset_valuation_str: 資産評価額の文字列

        Returns:
            AssetEvaluation: 変換済みの資産情報
        """
        return cls(
            cumulative_contributions=cls._parse_yen_amount(cumulative_contributions_str),
            gains_or_losses=cls._parse_yen_amount(gains_or_losses_str),
            asset_valuation=cls._parse_yen_amount(asset_valuation_str),
        )

    @classmethod
    def from_records(cls, records: Iterable[AssetRecord]) -> dict[str, AssetEvaluation]:
        """AssetRecord のリストから商品名 → AssetEvaluation のマッピングを生成する

        前提:
        - 入力されるレコードは同一日付のものとする（日付チェックは行わない、呼び出し側責務）
        - 商品名（product）が重複する場合は最後のレコードで上書きされる
          （実運用上は write 側の日付単位 upsert により重複は発生しない）
        - 空入力の場合は空 dict を返す（呼び出し側で空を判定し例外送出する）

        Args:
            records: AssetRecord の iterable

        Returns:
            dict[str, AssetEvaluation]: 商品名 → 資産評価のマッピング
        """
        return {
            r.product: cls(
                cumulative_contributions=r.cumulative_contributions,
                gains_or_losses=r.gains_or_losses,
                asset_valuation=r.asset_valuation,
            )
            for r in records
        }

    @staticmethod
    def _parse_yen_amount(yen_str: str) -> int:
        """円表記の文字列を整数に変換

        Args:
            yen_str: 円表記の文字列（例: "1,234,567円"）

        Returns:
            int: 整数値
        """
        # カンマ、円記号、空白を除去
        cleaned = yen_str.replace(",", "").replace("円", "").replace(" ", "").strip()

        # 全角数字を半角に変換
        cleaned = cleaned.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

        # マイナス記号の処理（全角・半角対応）
        cleaned = cleaned.replace("−", "-").replace("ー", "-").replace("－", "-")

        return int(cleaned)
