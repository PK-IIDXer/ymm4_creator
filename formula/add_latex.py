import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# isort: off
from utils import (
    get_last_frame,
    load_ymmp_project,
    save_ymmp_project,
)
from utils.ymmp_templates import create_image_item_template
from formula.latex_to_png import latex_to_png, get_latex_env_path

# isort: on


def ensure_latex_env() -> None:
    """
    LaTeX環境が存在しない場合、自動的にビルドする
    """
    env_path = get_latex_env_path()
    if env_path is None:
        raise RuntimeError("LaTeX環境のパスを取得できませんでした。")

    latex_env_path = Path(env_path)
    if not latex_env_path.exists():
        print("LaTeX環境が見つかりません。自動的にビルドを開始します...")

        # build_latex.pyのパスを取得
        build_script = os.path.join(os.path.dirname(__file__), "build_latex.py")

        # build_latex.pyを実行
        try:
            subprocess.run([sys.executable, build_script], check=True)
            print("LaTeX環境のビルドが完了しました。")
        except subprocess.CalledProcessError as e:
            print(f"LaTeX環境のビルドに失敗しました: {e}")
            raise RuntimeError("LaTeX環境のビルドに失敗しました。") from e

        # ビルド後の環境を確認
        if not latex_env_path.exists():
            raise RuntimeError(
                "LaTeX環境のビルドは完了しましたが、環境が見つかりません。"
            )


def add_latex_scene(
    project_file_path: str,
    latex_formula: str,
    output_file_path: str,
    duration_sec: float = 5.0,
    time_margin_sec: float = 1.0,
) -> None:
    """
    YMM4プロジェクトに数式のシーンを追加する関数
    """
    # LaTeX環境の確認と自動ビルド
    ensure_latex_env()

    # プロジェクトファイルを読み込む
    project_data = load_ymmp_project(project_file_path)
    if project_data is None:
        return

    # 出力先のディレクトリが存在しない場合は作成
    output_dir = os.path.join(os.path.dirname(output_file_path), "formulas")
    os.makedirs(output_dir, exist_ok=True)

    # 衝突を避けるためにファイル名にハッシュ値などを使うとより安全
    formula_image_filename = f"formula_{hash(latex_formula)}.png"
    formula_image_path = os.path.join(output_dir, formula_image_filename)

    # LaTeX数式をPNG画像に変換
    try:
        # YMM4が確実にパスを解決できるよう、絶対パスに変換する
        abs_formula_image_path = os.path.abspath(formula_image_path)
        latex_to_png(latex_formula, abs_formula_image_path)
    except Exception as e:
        print(f"数式の画像変換に失敗しました: {e}")
        return

    # FPSを取得
    fps = project_data.get("Timelines", [{}])[0].get("VideoInfo", {}).get("FPS", 60)

    # タイムラインの最後尾のフレームを取得
    last_frame = get_last_frame(project_data)

    # 開始フレームと表示時間を計算
    start_frame = int(last_frame + fps * time_margin_sec)
    duration_frames = int(fps * duration_sec)

    # 画像アイテムをテンプレートから作成
    new_image_item = create_image_item_template()

    # パラメータを設定
    new_image_item["Frame"] = start_frame
    new_image_item["Length"] = duration_frames
    new_image_item["Layer"] = 1  # 必要に応じてレイヤーを調整
    new_image_item["FilePath"] = abs_formula_image_path  # 絶対パスを設定
    new_image_item["Remark"] = latex_formula  # 備考に数式を入れておくと便利

    # プロジェクトデータに新しいアイテムを追加
    project_data["Timelines"][0]["Items"].append(new_image_item)

    # 新しいプロジェクトファイルとして保存
    if not save_ymmp_project(project_data, output_file_path):
        return
    print(f"LaTeXシーンを追加し、{output_file_path} に保存しました。")


def add_latex(
    ymmp_path: str,
    latex_text: str,
    output_path: Optional[str] = None,
    position: tuple[int, int] = (0, 0),
    scale: float = 1.0,
) -> None:
    """
    YMMPファイルにLaTeX数式を追加する関数

    Args:
        ymmp_path (str): YMMPファイルのパス
        latex_text (str): LaTeX数式のテキスト
        output_path (str | None): 出力パス (デフォルト: None)
        position (tuple[int, int]): 数式の位置 (デフォルト: (0, 0))
        scale (float): 数式のスケール (デフォルト: 1.0)
    """
    try:
        # YMMPファイルのデータを取得
        with open(ymmp_path, encoding="utf-8") as f:
            ymmp_data = json.load(f)

        # LaTeX数式をPNGに変換
        png_path = latex_to_png(
            latex_text,
            output_path=os.path.join(
                os.path.dirname(ymmp_path),
                "formulas",
                f"formula_{hash(latex_text)}.png",
            ),
        )

        # 画像アイテムのテンプレートを作成
        image_item = create_image_item_template()
        image_item["FilePath"] = png_path
        image_item["Position"] = {"X": position[0], "Y": position[1]}
        image_item["Scale"] = scale

        # 画像アイテムをYMMPファイルに追加
        ymmp_data["tracks"]["image_track"]["items"].append(image_item)

        # 変更を保存
        output_path = output_path or ymmp_path
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ymmp_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        raise RuntimeError(f"LaTeX数式の追加中にエラーが発生しました: {e!s}") from e


if __name__ == "__main__":
    # ご自身の環境に合わせてパスを修正してください
    base_project = "./連続性022 - コピー.ymmp"
    latex_formula = r"$e^{i\pi} + 1 = 0$"
    output_project = "自動生成プロジェクト_v4.ymmp"

    add_latex_scene(base_project, latex_formula, output_project)
