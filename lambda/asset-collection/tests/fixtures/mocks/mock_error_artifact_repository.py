from src.application.error_artifact_repository_interface import (
    ErrorArtifactUploadError,
    IErrorArtifactRepository,
)


class MockErrorArtifactRepository(IErrorArtifactRepository):
    """IErrorArtifactRepository の Mock 実装（テスト用）"""

    def __init__(self, should_fail: bool = False) -> None:
        self.stored_keys: list[str] = []
        self.should_fail = should_fail

    def store(self, key: str, file_path: str) -> None:
        if self.should_fail:
            raise ErrorArtifactUploadError("mock upload failed")
        self.stored_keys.append(key)
