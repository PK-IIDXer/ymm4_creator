import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Optional, Union

import requests

from config import VOICEVOX_PATH


class VoicevoxClient:
    def __init__(self, host: str = "http://localhost:50021"):
        """
        VOICEVOX APIクライアントの初期化

        Args:
            host (str): VOICEVOX APIのホストURL
        """
        self.host = host
        self.speaker_id = 1  # デフォルトの話者ID (ずんだもん)
        self._ensure_voicevox_running()

    def _ensure_voicevox_running(self) -> None:
        """
        VOICEVOXが起動していない場合は起動する
        """
        try:
            # APIが応答するか確認
            requests.get(f"{self.host}/version")
        except requests.exceptions.ConnectionError:
            print("VOICEVOXを起動しています...")
            try:
                # VOICEVOXを起動
                subprocess.Popen([VOICEVOX_PATH])
                # 起動を待機
                for _ in range(30):  # 最大30秒待機
                    try:
                        requests.get(f"{self.host}/version")
                        print("VOICEVOXが起動しました")
                        return
                    except requests.exceptions.ConnectionError:
                        time.sleep(1)
                raise Exception("VOICEVOXの起動がタイムアウトしました")
            except FileNotFoundError as e:
                raise Exception(
                    f"VOICEVOXが見つかりません。パスを確認してください: {VOICEVOX_PATH}"
                ) from e
            except Exception as e:
                raise Exception(f"VOICEVOXの起動に失敗しました: {e!s}") from e

    def text_to_speech(
        self,
        text: str,
        output_path: str,
        speaker_id: Optional[int] = None,
        speed: float = 1.0,
    ) -> str:
        """
        テキストを音声に変換して保存する

        Args:
            text (str): 変換するテキスト
            output_path (str): 出力する音声ファイルのパス
            speaker_id (int, optional): 話者ID。指定しない場合はデフォルト値を使用
            speed (float, optional): 話速。0.5から2.0の範囲。デフォルトは1.0
        """
        if speaker_id is not None:
            self.speaker_id = speaker_id

        # テキストを音声クエリに変換
        query_params: dict[str, Union[str, int]] = {
            "text": text,
            "speaker": self.speaker_id,
        }

        # 音声クエリの取得
        query_response = requests.post(f"{self.host}/audio_query", params=query_params)
        query_response.raise_for_status()

        # 音声クエリのパラメータを設定
        query_data = query_response.json()
        query_data["speedScale"] = speed

        # 音声合成
        synthesis_params: dict[str, int] = {"speaker": self.speaker_id}
        synthesis_response = requests.post(
            f"{self.host}/synthesis",
            params=synthesis_params,
            data=json.dumps(query_data),
        )
        synthesis_response.raise_for_status()

        # 音声ファイルの保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_bytes(synthesis_response.content)

        return str(output_path)

    def get_speakers(self) -> list[dict[str, Any]]:
        """
        利用可能な話者の一覧を取得する

        Returns:
            list[dict[str, Any]]: 話者の一覧
        """
        try:
            response = requests.get(f"{self.host}/speakers")
            response.raise_for_status()
            return list[dict[str, Any]](response.json())
        except requests.RequestException as e:
            raise Exception(f"話者の取得に失敗しました: {e}") from e

    def get_audio_query(self, text: str, speaker_id: int) -> dict[str, Any]:
        """
        音声合成用のクエリを取得する

        Args:
            text (str): 変換するテキスト
            speaker_id (int): 話者ID

        Returns:
            dict[str, Any]: 音声合成用のクエリ
        """
        try:
            query_params: dict[str, Union[str, int]] = {
                "text": text,
                "speaker": speaker_id,
            }
            response = requests.post(
                f"{self.host}/audio_query",
                params=query_params,
            )
            response.raise_for_status()
            return dict[str, Any](response.json())
        except requests.RequestException as e:
            raise Exception(f"音声合成クエリの取得に失敗しました: {e}") from e

    def synthesize_audio(self, audio_query: dict[str, Any], speaker_id: int) -> bytes:
        """
        音声を合成する

        Args:
            audio_query (dict[str, Any]): 音声合成用のクエリ
            speaker_id (int): 話者ID

        Returns:
            bytes: 音声データ
        """
        try:
            synthesis_params: dict[str, int] = {"speaker": speaker_id}
            response = requests.post(
                f"{self.host}/synthesis",
                params=synthesis_params,
                json=audio_query,
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise Exception(f"音声の合成に失敗しました: {e}") from e

    def get_audio_query_with_emotion(
        self, text: str, speaker_id: int, emotion: str
    ) -> dict[str, Any]:
        """
        感情を指定して音声合成用のクエリを取得する

        Args:
            text (str): 変換するテキスト
            speaker_id (int): 話者ID
            emotion (str): 感情

        Returns:
            dict[str, Any]: 音声合成用のクエリ
        """
        audio_query = self.get_audio_query(text, speaker_id)
        audio_query["emotion"] = emotion
        return audio_query

    def get_audio_query_with_emotion_and_style(
        self, text: str, speaker_id: int, emotion: str, style: str
    ) -> dict[str, Any]:
        """
        感情とスタイルを指定して音声合成用のクエリを取得する

        Args:
            text (str): 変換するテキスト
            speaker_id (int): 話者ID
            emotion (str): 感情
            style (str): スタイル

        Returns:
            dict[str, Any]: 音声合成用のクエリ
        """
        audio_query = self.get_audio_query_with_emotion(text, speaker_id, emotion)
        audio_query["style"] = style
        return audio_query
