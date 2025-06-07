import platform
import subprocess
from pathlib import Path
from typing import Optional
import os
import shutil

from pdf2image import convert_from_path


def get_pdflatex_command() -> str:
    """
    プラットフォームに応じたpdflatexコマンドを取得する関数

    Returns:
        str: pdflatexコマンド
    """
    system = platform.system().lower()
    if system == "windows":
        return "pdflatex"
    else:
        return "pdflatex"


def create_latex_document(text: str, font_size: int = 12, text_color: str = "white") -> str:
    """
    LaTeXドキュメントを作成する関数

    Args:
        text (str): LaTeX数式
        font_size (int): フォントサイズ (デフォルト: 12)
        text_color (str): 文字色 (デフォルト: white)

    Returns:
        str: LaTeXドキュメントの内容
    """
    color_command = f"\\color{{{text_color}}}"
    return f"""\\documentclass[{font_size}pt]{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{color}}
\\usepackage[paperwidth=100mm,paperheight=100mm,margin=0pt]{{geometry}}
\\pagestyle{{empty}}
\\begin{{document}}
{color_command}
{text}
\\end{{document}}"""


def run_pdflatex(pdflatex_cmd: str, tex_file: Path) -> Path:
    """
    pdflatexコマンドを実行する関数

    Args:
        pdflatex_cmd (str): pdflatexコマンド
        tex_file (Path): 入力TeXファイルのパス

    Returns:
        Path: 生成されたPDFファイルのパス
    """
    print(f"実行コマンド: {pdflatex_cmd} -interaction=nonstopmode {tex_file}")
    try:
        # カレントディレクトリを保存
        original_dir = Path.cwd()
        # TeXファイルのあるディレクトリに移動
        os.chdir(tex_file.parent)
        
        result = subprocess.run(
            [pdflatex_cmd, "-interaction=nonstopmode", tex_file.name],
            capture_output=True,
            text=True
        )
        print("コマンドの出力:")
        print(result.stdout)
        if result.stderr:
            print("警告/エラー出力:")
            print(result.stderr)
        
        # PDFファイルが生成されているか確認
        pdf_file = tex_file.with_suffix(".pdf")
        if not pdf_file.exists():
            raise RuntimeError("PDFファイルが生成されませんでした。")
            
        # 元のディレクトリに戻る
        os.chdir(original_dir)
        return pdf_file
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # 元のディレクトリに戻る
        os.chdir(original_dir)
        raise


def convert_pdf_to_png(pdf_file: Path, output_file: Path, dpi: int) -> None:
    """
    PDFをPNGに変換する関数

    Args:
        pdf_file (Path): 入力PDFファイルのパス
        output_file (Path): 出力PNGファイルのパス
        dpi (int): 出力画像のDPI
    """
    try:
        # PDFファイルの存在確認
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_file}")

        print(f"PDFファイルのサイズ: {pdf_file.stat().st_size} バイト")

        # ImageMagickのパスを確認
        magick_path = shutil.which('magick')
        if magick_path is None:
            # Windowsの場合、一般的なインストール場所を確認
            possible_paths = [
                r'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe',
                r'C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe',
                r'C:\Program Files (x86)\ImageMagick-7.1.1-Q16\magick.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    magick_path = path
                    break
            
            if magick_path is None:
                raise FileNotFoundError('ImageMagickが見つかりません。インストールされているか確認してください。')

        print(f"ImageMagickのパス: {magick_path}")

        # 出力ディレクトリが存在しない場合は作成
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # PDFをPNGに変換
        print("PDFの変換を開始します...")
        subprocess.run([
            magick_path, 'convert',
            '-density', str(dpi),
            '-background', 'none',
            '-trim',  # 余白を自動的に削除
            str(pdf_file),
            str(output_file)
        ], check=True)
        print("PDFの変換が完了しました")

    except Exception as e:
        print(f"PDF変換エラー: {e}")
        # より詳細なエラー情報を出力
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"エラーの詳細: {type(e.__cause__).__name__}: {str(e.__cause__)}")
        raise


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
    font_size: int = 12,
    text_color: str = "white",
) -> str:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        text (str): LaTeX数式
        output_path (Optional[str]): 出力ファイルのパス (デフォルト: None)
        dpi (int): 出力画像のDPI (デフォルト: 300)
        background_color (Optional[str]): 背景色 (デフォルト: None)
        foreground_color (Optional[str]): 前景色 (デフォルト: None)
        font_size (int): フォントサイズ (デフォルト: 12)
        text_color (str): 文字色 (デフォルト: white)

    Returns:
        str: 出力ファイルのパス
    """
    # デバッグ情報の出力
    print("=== デバッグ情報 ===")
    pdflatex_cmd = get_pdflatex_command()
    print(f"pdflatexコマンド: {pdflatex_cmd}")
    
    # 出力パスが指定されていない場合は一時ファイルを作成
    if output_path is None:
        output_path = f"formula_{hash(text)}.png"

    # パスをPathオブジェクトに変換
    output_path = Path(output_path)
    base_path = output_path.with_suffix("")
    tex_file = base_path.with_suffix(".tex")
    pdf_file = base_path.with_suffix(".pdf")

    print(f"TeXファイルのパス: {tex_file}")
    print(f"PDFファイルのパス: {pdf_file}")
    print(f"出力ファイルのパス: {output_path}")

    try:
        # LaTeXドキュメントを作成
        tex_content = create_latex_document(text, font_size, text_color)
        print(f"生成されたTeXドキュメント:\n{tex_content}")
        tex_file.write_text(tex_content, encoding="utf-8")
        print("TeXファイルの作成完了")

        # pdflatexコマンドを実行
        print("pdflatexコマンドを実行中...")
        pdf_file = run_pdflatex(pdflatex_cmd, tex_file)
        print("pdflatexコマンドの実行完了")

        # PDFをPNGに変換
        print("PDFをPNGに変換中...")
        convert_pdf_to_png(pdf_file, output_path, dpi)
        print("PDFの変換完了")

        return str(output_path)

    except Exception as e:
        print(f"エラーの詳細: {type(e).__name__}: {str(e)}")
        raise
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
