import os
import platform
import tempfile

from formula.build_latex import build_latex_env

# VOICEVOXの実行ファイルのパス
# 環境変数から取得、なければデフォルトのインストール場所を使用
VOICEVOX_PATH = os.getenv(
    "VOICEVOX_PATH",
    os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Local",
        "Programs",
        "VOICEVOX",
        "VOICEVOX.exe",
    ),
)

# APIのエンドポイント
API_ENDPOINT = "http://localhost:50021"


def get_latex_env_path() -> str:
    """
    TeX Live環境のパスを取得
    """
    # TeX Liveの標準的なインストールパスを確認
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "formula", "texlive"),
        os.path.join(os.path.dirname(__file__), "formula", "latex_bin", "texlive"),
        "/usr/local/texlive/2023",  # Linux/Mac
        "C:\\texlive\\2023",  # Windows
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # TeX Live環境が見つからない場合、インストールを実行
    print("TeX Live環境が見つかりません。インストールを開始します...")
    build_latex_env()

    # インストール後のパスを再確認
    for path in possible_paths:
        if os.path.exists(path):
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
        bin_path = os.path.join(latex_env_path, "bin", "win32")
    else:
        bin_path = os.path.join(latex_env_path, "bin", platform.system().lower())

    env["PATH"] = bin_path + os.pathsep + env["PATH"]

    # TeX Liveの標準的な環境変数を設定
    env["TEXMFHOME"] = os.path.join(latex_env_path, "texmf-local")
    env["TEXMFVAR"] = os.path.join(tempfile.gettempdir(), "texmf-var")
    env["TEXMFCONFIG"] = os.path.join(tempfile.gettempdir(), "texmf-config")
    env["TEXMFSYSCONFIG"] = os.path.join(latex_env_path, "texmf-config")
    env["TEXMFLOCAL"] = os.path.join(latex_env_path, "texmf-local")
    env["TEXMFMAIN"] = os.path.join(latex_env_path, "texmf-dist")
    env["TEXMFDIST"] = os.path.join(latex_env_path, "texmf-dist")

    return env
