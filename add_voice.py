import json
import copy

def add_voice_scene(project_file_path, voice_file_path, output_file_path):
    """ 
    YMM4プロジェクトに音声のシーンを追加する関数
    """
    # プロジェクトファイルを読み込む
    with open(project_file_path, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    # タイムラインの最後尾の時間を取得
    last_time = 0
    if project_data['Items']:
        last_item = project_data['Items'][-1]
        last_time = last_item['Frame'] + last_item['PlayTime']

    # 音声アイテムのテンプレート
    voice_item_template = {
      "Frame": last_time + 60,
      "PlayTime": 240, # 音声の長さに合わせるのが理想
      "Layer": 2,
      "FilePath": voice_file_path, # 引数で受け取ったパスを設定
      "VoiceVolume": 100.0,
      "ItemType": "Voice"
    }

    # プロジェクトデータに新しいアイテムを追加
    project_data['Items'].append(voice_item_template)

    # 新しいプロジェクトファイルとして保存
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    print(f"シーンを追加し、{output_file_path} に保存しました。")


# --- スクリプトの実行 ---
if __name__ == '__main__':
    base_project = 'D:\mimi\動画\project\シリーズ連続性\連続性022\連続性022 - コピー.ymmp'
    voice_wav = './voices/voice_01.wav'
    output_project = '自動生成されたプロジェクト.ymmp'

    add_voice_scene(base_project, voice_wav, output_project)