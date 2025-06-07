import json
import wave
from typing import Any, Dict, Optional, Tuple


def load_ymmp_project(project_file: str) -> Optional[Dict[str, Any]]:
    """
    YMM4プロジェクトファイルを読み込む関数

    Args:
        project_file (str): プロジェクトファイルのパス

    Returns:
        dict: プロジェクトデータ。エラーの場合はNone
    """
    try:
        with open(project_file, "r", encoding="utf-8-sig") as f:
            project_data: Dict[str, Any] = json.load(f)
        return project_data
    except FileNotFoundError:
        print(f"エラー: プロジェクトファイル '{project_file}' が見つかりません。")
        return None
    except json.JSONDecodeError as e:
        print(
            f"エラー: プロジェクトファイル '{project_file}' のJSON解析に失敗しました: {e}"
        )
        return None


def get_last_frame(project_data: Dict[str, Any]) -> int:
    """
    プロジェクトのタイムラインの最後尾のフレーム位置を取得する関数

    Args:
        project_data (dict): YMM4プロジェクトデータ

    Returns:
        int: 最後尾のフレーム位置
    """
    last_frame = 0
    if "Timelines" in project_data and project_data.get("Timelines"):
        for item in project_data["Timelines"][0]["Items"]:
            end_frame = item.get("Frame", 0) + item.get("Length", 0)
            if end_frame > last_frame:
                last_frame = end_frame
    return last_frame


def save_ymmp_project(project_data: Dict[str, Any], output_file: str) -> bool:
    """
    YMM4プロジェクトファイルを保存する関数

    Args:
        project_data (dict): 保存するプロジェクトデータ
        output_file (str): 出力ファイルのパス

    Returns:
        bool: 保存が成功した場合はTrue、失敗した場合はFalse
    """
    try:
        with open(output_file, "w", encoding="utf-8-sig") as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        print(f"プロジェクトファイルを保存しました: {output_file}")
        return True
    except Exception as e:
        print(f"エラー: ファイルの書き込みに失敗しました: {e}")
        return False


def get_wav_duration_and_frames(wav_path: str, fps: int = 60) -> Tuple[int, str]:
    """
    wavファイルの再生時間をフレーム数と秒数で取得する関数
    """
    try:
        with wave.open(wav_path, "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration_sec = frames / float(rate)
            duration_frames = int(duration_sec * fps)
            # YMM4用のタイムコード形式 "00:00:00.0000000" を作成
            time_str = f"00:00:{duration_sec:09.7f}"
            return duration_frames, time_str
    except Exception as e:
        print(f"Error reading WAV file {wav_path}: {e}")
        return 0, "00:00:00.0000000"
