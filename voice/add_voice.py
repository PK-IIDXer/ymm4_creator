import os
import sys
from dataclasses import dataclass
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent.absolute()))

# isort: off
from utils import (
    get_last_frame,
    get_wav_duration_and_frames,
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

    # 音声ファイルを生成
    voice_config = VoiceConfig(
        text=config.text,
        speaker_id=1,  # ずんだもんのデフォルトID
        speed=config.speed,
    )
    voice_file_path = generate_voice(voice_config, "output/voice.wav")
    if not voice_file_path or not Path(voice_file_path).exists():
        print("音声ファイルの生成に失敗したか、ファイルが見つかりません。")
        return

    # 音声の長さを取得
    fps = project_data.get("Timelines", [{}])[0].get("VideoInfo", {}).get("FPS", 60)
    duration_frames, voice_length_str = get_wav_duration_and_frames(
        voice_file_path, fps
    )

    # タイムラインの最後尾の時間を取得
    last_frame = get_last_frame(project_data)

    # 間隔を空ける (計算結果を整数に変換)
    start_frame = int(last_frame + fps * config.time_margin)

    # 新しいボイスアイテムをテンプレートから作成し、パラメータを設定
    new_voice_item = create_voice_item_template(
        speaker_name=config.speaker_name,
        frame=start_frame,
        length=duration_frames,
        file_path=voice_file_path,
    )

    # 基本情報
    new_voice_item["Frame"] = start_frame
    new_voice_item["Length"] = duration_frames
    new_voice_item["Serif"] = config.text
    new_voice_item["Hatsuon"] = config.text
    new_voice_item["Remark"] = config.text

    # 音声情報
    new_voice_item["VoiceLength"] = voice_length_str

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
