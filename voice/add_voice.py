import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent.absolute()))

# isort: off
from utils import (
    get_last_frame,
    load_ymmp_project,
    save_ymmp_project,
)
from utils.ymmp_templates import create_voice_item_template
from voice.generate_voice import generate_voice, VoiceConfig
from voice.voicevox_client import VoicevoxClient

# isort: on


@dataclass
class VoiceSceneConfig:
    """
    音声シーン設定を保持するデータクラス

    Attributes:
        project_file (str): プロジェクトファイルのパス
        text (str): 音声化するテキスト
        output_file (str): 出力ファイルのパス
        speaker_name (str): 話者名
        speed (float): 話速
        time_margin (float): 時間マージン
    """

    project_file: str
    text: str
    output_file: str
    speaker_name: str = "ずんだもん"
    speed: float = 1.0
    time_margin: float = 1.0


def create_voice_item(
    text: str,
    speaker_name: str = "ずんだもん",
    frame: int = 0,
    length: int = 60,
    speed: float = 1.0,
) -> dict[str, Any]:
    """音声アイテムを生成します。

    Args:
        text (str): 読み上げるセリフ
        speaker_name (str, optional): 話者名. デフォルトは"ずんだもん".
        frame (int, optional): 開始フレーム. デフォルトは0.
        length (int, optional): 表示フレーム数. デフォルトは60.
        speed (float, optional): 話速. デフォルトは1.0.

    Returns:
        dict: 生成された音声アイテム
    """
    # 音声ファイルを生成
    voice_config = VoiceConfig(
        text=text,
        speaker_id=1,  # ずんだもんのデフォルトID
        speed=speed,
    )
    voice_file_path = generate_voice(voice_config, "output/voice.wav")
    if not voice_file_path or not Path(voice_file_path).exists():
        raise RuntimeError("音声ファイルの生成に失敗したか、ファイルが見つかりません。")

    # 音声アイテムを生成
    new_voice_item = create_voice_item_template(
        speaker_name=speaker_name,
        frame=frame,
        length=length,
        file_path=str(voice_file_path),
    )

    # 基本情報を設定
    new_voice_item["Serif"] = text
    new_voice_item["Hatsuon"] = text
    new_voice_item["Remark"] = text

    return new_voice_item


def add_voice_scene(config: VoiceSceneConfig) -> None:
    """
    YMM4プロジェクトに音声のシーンを追加する関数 (テンプレート生成方式)

    Args:
        config (VoiceSceneConfig): 音声シーン設定
    """
    # プロジェクトファイルを読み込む
    project_data = load_ymmp_project(config.project_file)
    if project_data is None:
        return

    # FPSを取得
    fps = project_data.get("Timelines", [{}])[0].get("VideoInfo", {}).get("FPS", 60)

    # タイムラインの最後尾の時間を取得
    last_frame = get_last_frame(project_data)

    # 間隔を空ける (計算結果を整数に変換)
    start_frame = int(last_frame + fps * config.time_margin)

    # 新しいボイスアイテムを生成
    new_voice_item = create_voice_item(
        text=config.text,
        speaker_name=config.speaker_name,
        frame=start_frame,
        speed=config.speed,
    )

    # プロジェクトデータに新しいアイテムを追加
    project_data["Timelines"][0]["Items"].append(new_voice_item)

    # 新しいプロジェクトファイルとして保存
    if not save_ymmp_project(project_data, config.output_file):
        return
    print(f"音声シーンを追加しました: {config.output_file}")


def add_voice(config: VoiceConfig, output_path: str) -> None:
    """
    YMMPファイルに音声を追加する関数

    Args:
        config (VoiceConfig): 音声設定
        output_path (str): 出力ファイルのパス
    """
    # 音声生成
    client = VoicevoxClient()

    # 音声合成クエリの取得
    audio_query = client.get_audio_query_with_emotion_and_style(
        text=config.text,
        speaker_id=config.speaker_id,
        emotion=config.emotion,
        style=config.style,
    )

    # クエリのパラメータを設定
    audio_query["speedScale"] = config.speed
    audio_query["volumeScale"] = config.volume
    audio_query["intonationScale"] = config.intonation
    audio_query["pitchScale"] = config.pitch

    # 音声の合成
    audio_data = client.synthesize_audio(audio_query, config.speaker_id)

    # 音声ファイルの保存
    Path(output_path).write_bytes(audio_data)


if __name__ == "__main__":
    # テスト用
    config = VoiceSceneConfig(
        project_file="連続性022 - コピー.ymmp",
        text="整数フレームで正しく配置されるのだ!",
        output_file="自動生成プロジェクト_v3.ymmp",
        speaker_name="ずんだもん",
    )
    add_voice_scene(config)
