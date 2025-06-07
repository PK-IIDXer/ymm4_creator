import platform
import subprocess
from pathlib import Path
from typing import Optional

from pdf2image import convert_from_path

from .build_latex import get_latex_env_path


def get_pdflatex_command() -> Path:
    """
    プラットフォームに応じたpdflatexコマンドを取得する関数

    Returns:
        Path: pdflatexコマンドのパス
    """
    system = platform.system().lower()
    latex_env_path = get_latex_env_path()

    if system == "windows":
        return latex_env_path / "miktex" / "bin" / "x64" / "pdflatex.exe"
    else:
        return latex_env_path / "texlive" / "bin" / system / "pdflatex"


def create_latex_document(text: str) -> str:
    """
    LaTeXドキュメントを作成する関数

    Args:
        text (str): LaTeX数式

    Returns:
        str: LaTeXドキュメントの内容
    """
    return f"""\\documentclass[12pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{color}}
\\pagestyle{{empty}}
\\begin{{document}}
\\begin{{math}}
{text}
\\end{{math}}
\\end{{document}}"""


def run_pdflatex(pdflatex_cmd: Path, tex_file: Path) -> None:
    """
    pdflatexコマンドを実行する関数

    Args:
        pdflatex_cmd (Path): pdflatexコマンドのパス
        tex_file (Path): 入力TeXファイルのパス
    """
    subprocess.run(
        [str(pdflatex_cmd), "-interaction=nonstopmode", str(tex_file)], check=True
    )


def convert_pdf_to_png(pdf_file: Path, output_file: Path, dpi: int) -> None:
    """
    PDFをPNGに変換する関数

    Args:
        pdf_file (Path): 入力PDFファイルのパス
        output_file (Path): 出力PNGファイルのパス
        dpi (int): 出力画像のDPI
    """
    # PDFを画像に変換
    images = convert_from_path(str(pdf_file), dpi=dpi)

    # 最初のページを保存
    if images:
        images[0].save(str(output_file), "PNG")


def cleanup_files(base_path: Path) -> None:
    """
    一時ファイルを削除する関数

    Args:
        base_path (Path): ファイルの基本パス (拡張子なし)
    """
    for ext in [".aux", ".log", ".pdf"]:
        try:
            (base_path.with_suffix(ext)).unlink()
        except FileNotFoundError:
            pass


def latex_to_png(
    text: str,
    output_path: Optional[str] = None,
    dpi: int = 300,
    background_color: Optional[str] = None,
    foreground_color: Optional[str] = None,
) -> str:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        text (str): LaTeX数式
        output_path (Optional[str]): 出力ファイルのパス (デフォルト: None)
        dpi (int): 出力画像のDPI (デフォルト: 300)
        background_color (Optional[str]): 背景色 (デフォルト: None)
        foreground_color (Optional[str]): 前景色 (デフォルト: None)

    Returns:
        str: 出力ファイルのパス
    """
    # 出力パスが指定されていない場合は一時ファイルを作成
    if output_path is None:
        output_path = f"formula_{hash(text)}.png"

    # パスをPathオブジェクトに変換
    output_path = Path(output_path)
    base_path = output_path.with_suffix("")
    tex_file = base_path.with_suffix(".tex")
    pdf_file = base_path.with_suffix(".pdf")

    try:
        # LaTeXドキュメントを作成
        tex_file.write_text(create_latex_document(text), encoding="utf-8")

        # pdflatexコマンドを実行
        run_pdflatex(get_pdflatex_command(), tex_file)

        # PDFをPNGに変換
        convert_pdf_to_png(pdf_file, output_path, dpi)

        return str(output_path)

    finally:
        # 一時ファイルを削除
        cleanup_files(base_path)


if __name__ == "__main__":
    # テスト用の数式
    test_formula = r"$\frac{d}{dx}e^x = e^x$"
    output_path = "./formulas/test_formula.png"

    try:
        # 数式をPNGに変換
        result = latex_to_png(test_formula, output_path)
        print(f"数式を {result} に保存しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e!s}")
