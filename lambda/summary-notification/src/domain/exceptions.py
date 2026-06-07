from typing import Self


class SummaryNotificationError(Exception):
    """サマリ通知機能のベース例外"""

    pass


# TODO: Repositoryと同様のファイルに移動する
class AssetRetrievalError(SummaryNotificationError):
    """資産情報の取得エラー"""

    @classmethod
    def no_assets_in_spreadsheet(cls) -> Self:
        """スプレッドシートに資産情報が存在しない場合の例外を生成

        Returns:
            AssetRetrievalError: 生成された例外インスタンス
        """
        return cls("スプレッドシートに資産情報が見つかりません")

    @classmethod
    def during_fetching(cls) -> Self:
        """資産情報の取得中にエラーが発生した場合の例外インスタンスを生成する名前付きコンストラクタ

        Returns:
            AssetRetrievalError: 生成された例外インスタンス
        """
        return cls("資産情報の取得中にエラーが発生しました")
