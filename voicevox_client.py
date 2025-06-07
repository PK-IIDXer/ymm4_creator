import json
import os
import subprocess
import time

import requests

from config import API_ENDPOINT, VOICEVOX_PATH


class VoicevoxClient:
    def __init__(self, host=API_ENDPOINT):
        """
        VOICEVOX APIクライアントの初期化

        Args:
            host (str): VOICEVOX APIのホストURL
        """
        self.host = host
        self.speaker_id = 1  # デフォルトの話者ID（ずんだもん）
        self._ensure_voicevox_running()

    def _ensure_voicevox_running(self):
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
            except FileNotFoundError:
                raise Exception(
                    f"VOICEVOXが見つかりません。パスを確認してください: {VOICEVOX_PATH}"
                )
            except Exception as e:
                raise Exception(f"VOICEVOXの起動に失敗しました: {str(e)}")

    def text_to_speech(self, text, output_path, speaker_id=None, speed=1.0):
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
        query_params = {"text": text, "speaker": self.speaker_id}

        # 音声クエリの取得
        query_response = requests.post(f"{self.host}/audio_query", params=query_params)
        query_response.raise_for_status()

        # 音声クエリのパラメータを設定
        query_data = query_response.json()
        query_data["speedScale"] = speed

        # 音声合成
        synthesis_params = {"speaker": self.speaker_id}
        synthesis_response = requests.post(
            f"{self.host}/synthesis",
            params=synthesis_params,
            data=json.dumps(query_data),
        )
        synthesis_response.raise_for_status()

        # 音声ファイルの保存
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(synthesis_response.content)

        return output_path

    def get_speakers(self):
        """
        利用可能な話者の一覧を取得する

        Returns:
            list: 話者情報のリスト
        """
        response = requests.get(f"{self.host}/speakers")
        response.raise_for_status()
        return response.json()
