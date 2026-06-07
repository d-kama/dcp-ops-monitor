"""domain パッケージの再エクスポートを検証するテスト."""


def test_domain_exports_financial_asset_models() -> None:
    """domain __init__ から shared の FinancialAsset 系モデルをインポートできる."""
    from src.domain import (
        AssetValuation,
        CumulativeContributions,
        FinancialAsset,
        FinancialAssetHistory,
        GainsOrLosses,
        LatestPortfolioTotal,
    )

    assert AssetValuation is not None
    assert CumulativeContributions is not None
    assert FinancialAsset is not None
    assert FinancialAssetHistory is not None
    assert GainsOrLosses is not None
    assert LatestPortfolioTotal is not None


def test_domain_exports_financial_asset_repository_interface() -> None:
    """domain __init__ から IFinancialAssetRepository をインポートできる."""
    from src.domain import IFinancialAssetRepository

    assert IFinancialAssetRepository is not None


def test_domain_exports_exceptions() -> None:
    """domain __init__ から例外クラスをインポートできる（既存動作の回帰確認）."""
    from src.domain import AssetRetrievalError, SummaryNotificationError

    assert AssetRetrievalError is not None
    assert SummaryNotificationError is not None


def test_domain_all_contains_expected_symbols() -> None:
    """domain __all__ に必要なシンボルがすべて含まれる."""
    import src.domain as domain_module

    expected = {
        "AssetValuation",
        "CumulativeContributions",
        "FinancialAsset",
        "FinancialAssetHistory",
        "GainsOrLosses",
        "LatestPortfolioTotal",
        "IFinancialAssetRepository",
        "AssetRetrievalError",
        "SummaryNotificationError",
    }

    assert set(domain_module.__all__) == expected
