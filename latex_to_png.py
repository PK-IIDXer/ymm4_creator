import os
import shutil
import subprocess
import tempfile

from pylatex import Command, Document
from pylatex.utils import NoEscape


def latex_to_png(formula, output_path, dpi=300):
    """
    LaTeX数式を透過PNG画像に変換する関数

    Args:
        formula (str): LaTeX形式の数式
        output_path (str): 出力PNGファイルのパス
        dpi (int): 出力画像のDPI（デフォルト: 300）
    """
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # LaTeXドキュメントを作成
        doc = Document(documentclass="standalone")
        doc.packages.append(Command("usepackage", "amsmath"))
        doc.packages.append(Command("usepackage", "amssymb"))

        # 数式を追加
        doc.append(NoEscape(formula))

        # LaTeXファイルを生成
        tex_path = os.path.join(temp_dir, "formula.tex")

        # 直接LaTeXファイルを書き込む
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(r"\documentclass{standalone}" + "\n")
            f.write(r"\usepackage{amsmath}" + "\n")
            f.write(r"\usepackage{amssymb}" + "\n")
            f.write(r"\begin{document}" + "\n")
            f.write(formula + "\n")
            f.write(r"\end{document}")

        # PDFを生成
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path], cwd=temp_dir, check=True
        )

        # PDFをPNGに変換（透過背景）
        pdf_path = os.path.join(temp_dir, "formula.pdf")

        # ImageMagickのパスを確認
        magick_path = shutil.which("magick")
        if magick_path is None:
            # Windowsの場合、一般的なインストール場所を確認
            possible_paths = [
                r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
                r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe",
                r"C:\Program Files (x86)\ImageMagick-7.1.1-Q16\magick.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    magick_path = path
                    break

            if magick_path is None:
                raise FileNotFoundError(
                    "ImageMagickが見つかりません。インストールされているか確認してください。"
                )

        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # PDFをPNGに変換
        subprocess.run(
            [
                magick_path,
                "convert",
                "-density",
                str(dpi),
                "-background",
                "none",
                pdf_path,
                output_path,
            ],
            check=True,
        )


if __name__ == "__main__":
    # テスト用の数式
    test_formula = r"$\frac{d}{dx}e^x = e^x$"
    output_path = "./formulas/test_formula.png"

    try:
        # 数式をPNGに変換
        latex_to_png(test_formula, output_path)
        print(f"数式を {output_path} に保存しました。")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
