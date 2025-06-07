import json
import sys
from pathlib import Path
from typing import Any, Optional

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent.absolute()))

# isort: off
from utils import (
    get_last_frame,
    load_ymmp_project,
    save_ymmp_project,
)
from utils.ymmp_templates import create_image_item_template
from formula.latex_to_png import latex_to_png

# isort: on


def create_latex_item(
    latex_formula: str,
    frame: int = 0,
    length: int = 300,  # 5秒 * 60fps
    layer: int = 1,
) -> dict[str, Any]:
    """数式アイテムを生成します。

    Args:
        latex_formula (str): LaTeX形式の数式
        frame (int, optional): 開始フレーム. デフォルトは0.
        length (int, optional): 表示フレーム数. デフォルトは300.
        layer (int, optional): レイヤー番号. デフォルトは1.

    Returns:
        dict: 生成された数式アイテム
    """
    # 出力先のディレクトリが存在しない場合は作成
    output_dir = Path("output") / "formulas"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 衝突を避けるためにファイル名にハッシュ値などを使うとより安全
    formula_image_filename = f"formula_{hash(latex_formula)}.png"
    formula_image_path = output_dir / formula_image_filename

    # LaTeX数式をPNG画像に変換
    try:
        # YMM4が確実にパスを解決できるよう、絶対パスに変換する
        abs_formula_image_path = str(formula_image_path.absolute())
        latex_to_png(latex_formula, abs_formula_image_path)
    except Exception as e:
        raise RuntimeError(f"数式の画像変換に失敗しました: {e}") from e

    # 画像アイテムをテンプレートから作成
    new_image_item = create_image_item_template()

    # パラメータを設定
    new_image_item["Frame"] = frame
    new_image_item["Length"] = length
    new_image_item["Layer"] = layer
    new_image_item["FilePath"] = abs_formula_image_path
    new_image_item["Remark"] = latex_formula

    return new_image_item


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
    # プロジェクトファイルを読み込む
    project_data = load_ymmp_project(project_file_path)
    if project_data is None:
        return

    # FPSを取得
    fps = project_data.get("Timelines", [{}])[0].get("VideoInfo", {}).get("FPS", 60)

    # タイムラインの最後尾のフレームを取得
    last_frame = get_last_frame(project_data)

    # 開始フレームと表示時間を計算
    start_frame = int(last_frame + fps * time_margin_sec)
    duration_frames = int(fps * duration_sec)

    # 新しい数式アイテムを生成
    new_image_item = create_latex_item(
        latex_formula=latex_formula,
        frame=start_frame,
        length=duration_frames,
    )

    # プロジェクトデータに新しいアイテムを追加
    project_data["Timelines"][0]["Items"].append(new_image_item)

    # 新しいプロジェクトファイルとして保存
    if not save_ymmp_project(project_data, str(output_file_path)):
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
        ymmp_path_obj = Path(ymmp_path)
        ymmp_data = json.loads(ymmp_path_obj.read_text(encoding="utf-8"))

        # LaTeX数式をPNGに変換
        png_path = latex_to_png(
            latex_text,
            output_path=str(
                ymmp_path_obj.parent / "formulas" / f"formula_{hash(latex_text)}.png"
            ),
        )

        # 画像アイテムのテンプレートを作成
        image_item = create_image_item_template()
        image_item["FilePath"] = str(png_path)  # Pathオブジェクトを文字列に変換
        image_item["Position"] = {"X": position[0], "Y": position[1]}
        image_item["Scale"] = scale

        # 画像アイテムをYMMPファイルに追加
        ymmp_data["tracks"]["image_track"]["items"].append(image_item)

        # 変更を保存
        if output_path is not None:
            save_path = Path(output_path)
        else:
            save_path = ymmp_path_obj

        save_path.write_text(
            json.dumps(ymmp_data, ensure_ascii=False, indent=4), encoding="utf-8"
        )

    except Exception as e:
        raise RuntimeError(f"LaTeX数式の追加中にエラーが発生しました: {e!s}") from e


if __name__ == "__main__":
    # ご自身の環境に合わせてパスを修正してください
    base_project = "./連続性022 - コピー.ymmp"
    latex_formula = r"$e^{i\pi} + 1 = 0$"
    output_project = "自動生成プロジェクト_v4.ymmp"

    add_latex_scene(base_project, latex_formula, output_project)
