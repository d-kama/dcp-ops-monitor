from abc import ABC, abstractmethod


class IErrorArtifactRepository(ABC):
    """エラー結果保存抽象クラス"""

    @abstractmethod
    def store(self, key: str, file_path: str) -> None:
        """エラーアーティファクトを保存する
        Args:
            key (str): オブジェクトのキー
            file_path (str): 保存するファイルのパス
        Raises:
            ArtifactUploadError: 保存失敗時
        """
        pass


class ArtifactUploadError(Exception):
    """エラーアーティファクトのアップロード失敗"""

    pass
