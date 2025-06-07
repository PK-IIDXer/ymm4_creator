from voicevox_client import VoicevoxClient
import os
import json

def generate_voice(speaker_name, text, speed=1.0):
    """
    指定された話者とテキストで音声を生成する関数
    
    Args:
        speaker_name (str): 話者名
        text (str): 読み上げるテキスト
        speed (float): 話速（0.5-2.0）
    
    Returns:
        str: 生成された音声ファイルのパス
    """
    # VOICEVOXクライアントの初期化
    client = VoicevoxClient()
    
    # 出力ディレクトリの作成
    output_dir = "voices"
    os.makedirs(output_dir, exist_ok=True)
    
    # 話者名からIDを取得
    speakers = client.get_speakers()
    speaker_id = None
    for speaker in speakers:
        if speaker['name'] == speaker_name:
            speaker_id = speaker['styles'][0]['id']  # デフォルトスタイルを使用
            break
    
    if speaker_id is None:
        raise ValueError(f"話者 '{speaker_name}' が見つかりません")
    
    # 出力ファイル名を生成
    output_path = os.path.join(output_dir, f"voice_{speaker_id}_speed{speed}.wav")
    
    # 音声の生成
    client.text_to_speech(text, output_path, speaker_id=speaker_id, speed=speed)
    return output_path

def main():
    # VOICEVOXクライアントの初期化
    client = VoicevoxClient()
    
    # 出力ディレクトリの作成
    output_dir = "voices"
    os.makedirs(output_dir, exist_ok=True)
    
    # 利用可能な話者の一覧を表示
    speakers = client.get_speakers()
    print("\n利用可能な話者:")
    for speaker in speakers:
        print(f"\n話者: {speaker['name']}")
        print("スタイル:")
        for style in speaker['styles']:
            print(f"  - ID: {style['id']}, 名前: {style['name']}")
    
    # 標準入力からテキストと話者IDを取得
    text = input("\n音声に変換するテキストを入力してください: ")
    speaker_id = int(input("話者IDを入力してください: "))
    
    # 話速の設定（0.5-2.0の範囲）
    while True:
        try:
            speed = float(input("話速を入力してください（0.5-2.0、1.0が通常速度）: "))
            if 0.5 <= speed <= 2.0:
                break
            print("話速は0.5から2.0の範囲で入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")
    
    # 出力ファイル名を生成
    output_path = os.path.join(output_dir, f"voice_{speaker_id}_speed{speed}.wav")
    
    try:
        # 音声の生成（話者IDと話速を指定）
        client.text_to_speech(text, output_path, speaker_id=speaker_id, speed=speed)
        print(f"音声ファイルを生成しました: {output_path}")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 