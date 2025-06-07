import os
import platform
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import requests

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def get_latex_env_path() -> Path:
    """
    LaTeX環境のパスを取得する関数

    Returns:
        Path: LaTeX環境のパス
    """
    return Path(__file__).parent / "latex_bin"


def download_file(url: str, output_path: Path) -> None:
    """
    ファイルをダウンロードする関数

    Args:
        url (str): ダウンロードURL
        output_path (Path): 出力ファイルのパス
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with output_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def extract_zip(zip_path: str, extract_path: str) -> None:
    """
    ZIPファイルを展開する

    Args:
        zip_path (str): 展開するZIPファイルのパス
        extract_path (str): 展開先のディレクトリパス
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)


def create_latex_env_structure(bin_dir: str) -> None:
    """
    LaTeX環境のディレクトリ構造を作成

    Args:
        bin_dir (str): LaTeX環境のベースディレクトリパス
    """
    # 必要なディレクトリを作成
    dirs = [
        os.path.join(bin_dir, "bin"),
        os.path.join(bin_dir, "texmf", "tex", "latex"),
        os.path.join(bin_dir, "texmf", "fonts"),
        os.path.join(bin_dir, "texmf", "doc"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # README.mdを作成
    readme_path = os.path.join(bin_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(
            """# 埋め込みLaTeX環境

このディレクトリには、アプリケーション用の最小限のLaTeX環境が含まれています。
以下のコンポーネントが含まれています:

- pdflatex: PDF生成エンジン
- amsmath: 数式用パッケージ
- amssymb: 数学記号用パッケージ
- 必要なフォント

この環境は完全に自己完結しており、システムのLaTeX環境に依存しません。
"""
        )


def download_miktex() -> Path:
    """
    MiKTeXをダウンロードする関数

    Returns:
        Path: ダウンロードしたファイルのパス
    """
    url = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/miktexsetup-x64-5.0.0.exe"
    output_path = get_latex_env_path() / "miktex-setup.exe"
    download_file(url, output_path)
    return output_path


def install_miktex(setup_path: Path) -> None:
    """
    MiKTeXをインストールする関数

    Args:
        setup_path (Path): セットアップファイルのパス
    """
    subprocess.run(
        [str(setup_path), "--unattended", "--install-actions=install"], check=True
    )


def download_texlive() -> Path:
    """
    TeX Liveをダウンロードする関数

    Returns:
        Path: ダウンロードしたファイルのパス
    """
    url = "https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
    output_path = get_latex_env_path() / "texlive.tar.gz"
    download_file(url, output_path)
    return output_path


def install_texlive(archive_path: Path) -> None:
    """
    TeX Liveをインストールする関数

    Args:
        archive_path (Path): アーカイブファイルのパス
    """
    # アーカイブを展開
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=get_latex_env_path())

    # インストールスクリプトを実行
    install_script = next(get_latex_env_path().glob("install-tl-*/install-tl"))
    subprocess.run([str(install_script), "--no-interaction"], check=True)


def build_latex_env() -> None:
    """
    LaTeX環境を構築する関数
    """
    # LaTeX環境のディレクトリを作成
    latex_env_path = get_latex_env_path()
    latex_env_path.mkdir(parents=True, exist_ok=True)

    # プラットフォームに応じたインストール処理
    if platform.system().lower() == "windows":
        setup_path = download_miktex()
        install_miktex(setup_path)
    else:
        archive_path = download_texlive()
        install_texlive(archive_path)


def get_latex_env() -> dict[str, str]:
    """
    LaTeX環境の環境変数を取得する関数

    Returns:
        dict[str, str]: 環境変数の辞書
    """
    latex_env_path = get_latex_env_path()
    env = os.environ.copy()

    if platform.system().lower() == "windows":
        env["PATH"] = f"{latex_env_path / 'miktex' / 'bin' / 'x64'};{env['PATH']}"
    else:
        env["PATH"] = f"{latex_env_path / 'texlive' / 'bin'}:{env['PATH']}"

    return env


def build_latex(
    formula: str,
    output_path: str,
    dpi: int = 300,
) -> str:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        formula (str): LaTeX形式の数式
        output_path (str): 出力するPNG画像のパス
        dpi (int, optional): 画像のDPI. Defaults to 300.

    Returns:
        str: 出力ファイルのパス
    """
    from .latex_to_png import latex_to_png

    # LaTeX数式をPNGに変換
    return latex_to_png(
        formula=formula,
        output_path=output_path,
        dpi=dpi,
    )


if __name__ == "__main__":
    build_latex_env()
