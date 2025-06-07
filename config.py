import os

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
