import json
from pathlib import Path

import requests

from config import API_ENDPOINT

# HTTPステータスコード
HTTP_STATUS_OK = 200


def add_voice_scene(
    base_project_path: str,
    text: str,
    output_project_path: str,
    speaker_name: str = "ずんだもん",
) -> None:
    """YMM4プロジェクトに音声アイテムを追加します。

    Args:
        base_project_path (str): ベースとなる.ymmpファイルのパス
        text (str): 読み上げるセリフ
        output_project_path (str): 出力先の.ymmpファイルのパス
        speaker_name (str, optional): 話者名. デフォルトは"ずんだもん".
    """
    # プロジェクトファイルを読み込む
    with open(base_project_path, encoding="utf-8") as f:
        project = json.load(f)

    # 音声ファイルを生成
    voice_file_path = generate_voice(text, speaker_name)

    # 音声アイテムを追加
    voice_item = {
        "type": "audio",
        "file_path": str(voice_file_path),
        "name": text[:20],  # テキストの最初の20文字をアイテム名として使用
        "start_time": 0,  # 開始時間 (秒)
        "duration": 0,  # 音声の長さ (秒)- 後で更新
    }

    # アイテムリストに追加
    if "items" not in project:
        project["items"] = []
    project["items"].append(voice_item)

    # プロジェクトファイルを保存
    with open(output_project_path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)


def generate_voice(text: str, speaker_name: str) -> Path:
    """VOICEVOXを使用して音声ファイルを生成します。

    Args:
        text (str): 読み上げるセリフ
        speaker_name (str): 話者名

    Returns:
        Path: 生成された音声ファイルのパス
    """
    # 話者IDを取得
    response = requests.get(f"{API_ENDPOINT}/speakers")
    speakers = response.json()
    speaker_id = None
    for speaker in speakers:
        if speaker["name"] == speaker_name:
            speaker_id = speaker["speaker_id"]
            break

    if speaker_id is None:
        raise ValueError(f"話者 '{speaker_name}' が見つかりません")

    # 音声合成のパラメータを設定
    params = {
        "text": text,
        "speaker": speaker_id,
    }

    # 音声合成を実行
    response = requests.post(f"{API_ENDPOINT}/synthesis", params=params)
    if response.status_code != HTTP_STATUS_OK:
        raise Exception("音声合成に失敗しました")

    # 音声ファイルを保存
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{text[:10]}.wav"
    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
