import os
import platform
import shutil
import tempfile
from pathlib import Path

# 出力ディレクトリの設定
DEFAULT_OUTPUT_DIR = Path("output")

# VOICEVOXの実行ファイルのパス
# 環境変数から取得、なければデフォルトのインストール場所を使用
VOICEVOX_PATH = os.getenv(
    "VOICEVOX_PATH",
    str(Path.home() / "AppData" / "Local" / "Programs" / "VOICEVOX" / "VOICEVOX.exe"),
)

# APIのエンドポイント
API_ENDPOINT = "http://localhost:50021"


def get_latex_env_path() -> Path:
    """
    TeX Live環境のパスを取得
    """
    # TeX Liveの標準的なインストールパスを確認
    possible_paths = [
        Path(__file__).parent / "formula" / "texlive",
        Path(__file__).parent / "formula" / "latex_bin" / "texlive",
        Path("/usr/local/texlive/2023"),  # Linux/Mac
        Path("C:/texlive/2023"),  # Windows
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # TeX Live環境が見つからない場合、インストールを実行
    print("TeX Live環境が見つかりません。インストールを開始します...")
    # 動的にインポート
    from formula.build_latex import build_latex_env

    build_latex_env()

    # インストール後のパスを再確認
    for path in possible_paths:
        if path.exists():
            return path

    raise Exception(
        "TeX Live環境のインストールに失敗しました。手動でインストールしてください。"
    )


def get_latex_env() -> dict[str, str]:
    """
    TeX Live環境の環境変数を取得
    """
    latex_env_path = get_latex_env_path()

    # 環境変数を設定
    env = os.environ.copy()

    # TeX LiveのbinディレクトリをPATHに追加
    if platform.system().lower() == "windows":
        bin_path = latex_env_path / "bin" / "win32"
    else:
        bin_path = latex_env_path / "bin" / platform.system().lower()

    env["PATH"] = f"{bin_path}{os.pathsep}{env['PATH']}"

    # TeX Liveの標準的な環境変数を設定
    env["TEXMFHOME"] = str(latex_env_path / "texmf-local")
    env["TEXMFVAR"] = str(Path(tempfile.gettempdir()) / "texmf-var")
    env["TEXMFCONFIG"] = str(Path(tempfile.gettempdir()) / "texmf-config")
    env["TEXMFSYSCONFIG"] = str(latex_env_path / "texmf-config")
    env["TEXMFLOCAL"] = str(latex_env_path / "texmf-local")
    env["TEXMFMAIN"] = str(latex_env_path / "texmf-dist")
    env["TEXMFDIST"] = str(latex_env_path / "texmf-dist")

    return env


def get_imagemagick_path() -> str:
    """
    ImageMagickのパスを取得する関数
    """
    # まず環境変数PATHから探す
    magick_path = shutil.which("magick")
    if magick_path is not None:
        return magick_path

    # Windowsの場合、一般的なインストール場所を確認
    if platform.system().lower() == "windows":
        possible_paths = [
            Path(r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"),
            Path(r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe"),
            Path(r"C:\Program Files (x86)\ImageMagick-7.1.1-Q16\magick.exe"),
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)

    raise FileNotFoundError(
        "ImageMagickが見つかりません。インストールされているか確認してください。"
    )
