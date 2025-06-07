def latex_to_png(formula: str, output_path: str, dpi: int = 300) -> str:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        formula (str): LaTeX形式の数式
        output_path (str): 出力するPNG画像のパス
        dpi (int, optional): 画像のDPI. Defaults to 300.
    """
    ...

def get_latex_env() -> dict[str, str]: ...
def get_latex_env_path() -> str | None: ...
