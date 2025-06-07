import os
from dataclasses import dataclass

from .voicevox_client import VoicevoxClient

# 定数の定義
MIN_PITCH = 0.5
MAX_PITCH = 2.0


@dataclass
class VoiceConfig:
    """音声設定を保持するデータクラス"""

    text: str
    speaker_id: int
    emotion: str = "normal"
    style: str = "normal"
    pitch: float = 0.0
    volume: float = 1.0
    intonation: float = 1.0
    speed: float = 1.0


def generate_voice(config: VoiceConfig, output_path: str) -> str:
    """
    音声を生成する関数

    Args:
        config (VoiceConfig): 音声設定
        output_path (str): 出力ファイルのパス

    Returns:
        str: 生成された音声ファイルのパス
    """
    # 出力ディレクトリの作成
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
    with open(output_path, "wb") as f:
        f.write(audio_data)

    return output_path


def main() -> None:
    """メイン関数"""
    # 出力ディレクトリの作成
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # テキストの入力
    text = input("テキストを入力してください: ")

    # 話者IDの入力
    speaker_id = int(input("話者IDを入力してください: "))

    # 音声設定の作成
    config = VoiceConfig(
        text=text,
        speaker_id=speaker_id,
        speed=1.0,  # デフォルト値
    )

    # 出力ファイル名を生成
    output_path = os.path.join(
        output_dir, f"voice_{speaker_id}_speed{config.speed}.wav"
    )

    # 音声生成
    generate_voice(config, output_path)


if __name__ == "__main__":
    main()
