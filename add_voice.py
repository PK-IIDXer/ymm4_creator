import os
from ymmp_templates import create_voice_item_template
from ymmp_utils import load_ymmp_project, get_last_frame, save_ymmp_project, get_wav_duration_and_frames
from generate_voice import generate_voice

def add_voice_scene(project_file, text, output_file, speaker_name="ずんだもん", speed=1.0, time_margin=1.0):
    """ 
    YMM4プロジェクトに音声のシーンを追加する関数（テンプレート生成方式）
    """

    # プロジェクトファイルを読み込む
    project_data = load_ymmp_project(project_file)
    if project_data is None:
        return

    # 音声ファイルを生成
    voice_file_path = generate_voice(speaker_name, text, speed)
    if not voice_file_path or not os.path.exists(voice_file_path):
        print("音声ファイルの生成に失敗したか、ファイルが見つかりません。")
        return

    # 音声の長さを取得
    fps = project_data.get('Timelines', [{}])[0].get('VideoInfo', {}).get('FPS', 60)
    duration_frames, voice_length_str = get_wav_duration_and_frames(voice_file_path, fps)

    # タイムラインの最後尾の時間を取得
    last_frame = get_last_frame(project_data)
    
    # 間隔を空ける
    start_frame = last_frame + 60 * time_margin

    # 新しいボイスアイテムをテンプレートから作成し、パラメータを設定
    new_voice_item = create_voice_item_template(speaker_name)
    
    # 基本情報
    new_voice_item['Frame'] = start_frame
    new_voice_item['Length'] = duration_frames
    new_voice_item['Serif'] = text
    new_voice_item['Hatsuon'] = text
    new_voice_item['Remark'] = text
    
    # 音声情報
    new_voice_item['VoiceLength'] = voice_length_str

    # プロジェクトデータに新しいアイテムを追加
    project_data['Timelines'][0]['Items'].append(new_voice_item)

    # 新しいプロジェクトファイルとして保存
    if not save_ymmp_project(project_data, output_file):
        return
    print(f"音声シーンを追加しました: {output_file}")


if __name__ == '__main__':
    # テスト用
    base_project = '連続性022 - コピー.json' 
    serif_text = "テンプレートからアイテムを生成するのだ！"
    output_project = '自動生成プロジェクト_v2.ymmp'
    character = "ずんだもん"

    add_voice_scene(base_project, serif_text, output_project, speaker_name=character)

