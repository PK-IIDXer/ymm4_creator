import os
import sys

from utils import load_ymmp_project, save_ymmp_project

from .latex_to_png import latex_to_png

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def add_latex_scene(
    project_file_path: str, latex_formula: str, output_file_path: str
) -> None:
    """
    YMM4プロジェクトに数式のシーンを追加する関数

    Args:
        project_file_path (str): 元のYMM4プロジェクトファイルのパス
        latex_formula (str): LaTeX形式の数式
        output_file_path (str): 出力するYMM4プロジェクトファイルのパス
    """
    # 出力ディレクトリとファイル名を設定
    output_dir = os.path.join(os.path.dirname(output_file_path), "formulas")
    formula_image_path = os.path.join(output_dir, "formula.png")

    # LaTeX数式をPNG画像に変換
    try:
        latex_to_png(latex_formula, formula_image_path)
    except Exception as e:
        print(f"数式の画像変換に失敗しました: {str(e)}")
        return

    # プロジェクトファイルを読み込む
    project_data = load_ymmp_project(project_file_path)
    if project_data is None:
        return

    # タイムラインの最後尾の時間を取得
    last_time = 0
    if "Timelines" in project_data and project_data["Timelines"]:
        timeline = project_data["Timelines"][0]
        if "Items" in timeline and timeline["Items"]:
            last_item = timeline["Items"][-1]
            last_time = last_item["Frame"] + last_item["Length"]

    # 画像アイテムのテンプレート
    image_item_template = {
        "Frame": last_time + 60,  # 1秒後から開始
        "Length": 300,  # 5秒間表示
        "Layer": 1,
        "FilePath": formula_image_path,  # 変換された画像のパスを設定
        "X": 0.0,
        "Y": 100.0,
        "Zoom": 100.0,
        "Alpha": 100.0,
        "ItemType": "Image",
    }

    # プロジェクトデータに新しいアイテムを追加
    if "Timelines" not in project_data:
        project_data["Timelines"] = []
    if not project_data["Timelines"]:
        project_data["Timelines"].append({"Items": []})
    project_data["Timelines"][0]["Items"].append(image_item_template)

    # 新しいプロジェクトファイルとして保存
    if not save_ymmp_project(project_data, output_file_path):
        return
    print(f"シーンを追加し、{output_file_path} に保存しました。")


# --- スクリプトの実行 ---
if __name__ == "__main__":
    base_project = (
        r"D:\mimi\動画\project\シリーズ連続性\連続性022\連続性022 - コピー.ymmp"
    )
    latex_formula = r"$\frac{1}{2} + \frac{1}{3} = \frac{5}{6}$"
    output_project = "自動生成されたプロジェクト.ymmp"

    add_latex_scene(base_project, latex_formula, output_project)
