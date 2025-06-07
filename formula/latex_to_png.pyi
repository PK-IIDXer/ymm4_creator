from typing import Optional

def latex_to_png(
    latex_formula: str,
    output_path: str,
    dpi: Optional[int] = None,
    background_color: Optional[str] = None,
    foreground_color: Optional[str] = None,
) -> None:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        latex_formula (str): LaTeX形式の数式
        output_path (str): 出力するPNG画像のパス
        dpi (Optional[int], optional): 画像のDPI. Defaults to None.
        background_color (Optional[str], optional): 背景色. Defaults to None.
        foreground_color (Optional[str], optional): 前景色. Defaults to None.
    """
    ...
