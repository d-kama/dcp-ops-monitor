def parse_yen_amount(yen_str: str) -> int:
    """円表記の文字列を整数に変換する

    Args:
        yen_str: 円表記の文字列（例: "1,234,567円"）

    Returns:
        int: 整数値
    """
    cleaned = yen_str.replace(",", "").replace("円", "").replace(" ", "").strip()
    cleaned = cleaned.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    cleaned = cleaned.replace("−", "-").replace("ー", "-").replace("－", "-")
    return int(cleaned)
