"""IAssetRecordWriter インターフェースのテスト"""

from abc import ABC
from inspect import isabstract

import pytest

from src.domain import AssetRecord, IAssetRecordWriter


class TestIAssetRecordWriter:
    def test_IAssetRecordWriter__is_abstract_class(self) -> None:
        """IAssetRecordWriter が ABC であること"""
        assert issubclass(IAssetRecordWriter, ABC)

    def test_IAssetRecordWriter__cannot_be_instantiated_directly(self) -> None:
        """IAssetRecordWriter を直接インスタンス化できないこと"""
        assert isabstract(IAssetRecordWriter)

    def test_IAssetRecordWriter__concrete_subclass_can_be_instantiated(self) -> None:
        """save_daily_records を実装したサブクラスはインスタンス化できること"""

        class ConcreteWriter(IAssetRecordWriter):
            def save_daily_records(self, records: list[AssetRecord]) -> None:
                pass

        writer = ConcreteWriter()
        assert isinstance(writer, IAssetRecordWriter)

    def test_IAssetRecordWriter__has_abstract_save_daily_records(self) -> None:
        """save_daily_records メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(IAssetRecordWriter, "save_daily_records")
        assert getattr(IAssetRecordWriter.save_daily_records, "__isabstractmethod__", False)

    def test_IAssetRecordWriter__no_read_methods_mixed_in(self) -> None:
        """IAssetRecordWriter に read 系メソッドが混入していないこと（ISP 準拠）"""
        writer_methods = dir(IAssetRecordWriter)
        assert "get_latest_records" not in writer_methods
        assert "get_records_within_days" not in writer_methods
        assert "get_records" not in writer_methods
