import json

def add_latex_scene(project_file_path, formula_image_path, output_file_path):
    """
    YMM4プロジェクトに数式のシーンを追加する関数
    """
    # プロジェクトファイルを読み込む
    with open(project_file_path, 'r', encoding='utf-8') as f:
        project_data = json.load(f)

    # タイムラインの最後尾の時間を取得
    last_time = 0
    if project_data['Items']:
        last_item = project_data['Items'][-1]
        last_time = last_item['Frame'] + last_item['PlayTime']

    # 画像アイテムのテンプレート
    image_item_template = {
      "Frame": last_time + 60, # 1秒後から開始
      "PlayTime": 300, # 5秒間表示
      "Layer": 1,
      "FilePath": formula_image_path, # 引数で受け取ったパスを設定
      "X": 0.0,
      "Y": 100.0,
      "Zoom": 100.0,
      "Alpha": 100.0,
      "ItemType": "Image"
    }

    # プロジェクトデータに新しいアイテムを追加
    project_data['Items'].append(image_item_template)

    # 新しいプロジェクトファイルとして保存
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    print(f"シーンを追加し、{output_file_path} に保存しました。")


# --- スクリプトの実行 ---
if __name__ == '__main__':
    base_project = 'D:\mimi\動画\project\シリーズ連続性\連続性022\連続性022 - コピー.ymmp'
    formula_png = './formulas/formula_01.png'
    output_project = '自動生成されたプロジェクト.ymmp'

    add_latex_scene(base_project, formula_png, output_project)