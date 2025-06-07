from typing import Any

from formula.add_latex import create_latex_item
from utils.ymmp_utils import load_ymmp_project, save_ymmp_project
from voice.add_voice import create_voice_item


def _add_voice_item(
    project_data: dict[str, Any], instruction: dict[str, Any]
) -> dict[str, Any]:
    """音声アイテムを追加するロジック (ファイルI/Oはしない)

    Args:
        project_data (dict): プロジェクトデータ
        instruction (dict): 音声アイテムの設定
            - text (str): 読み上げるセリフ
            - speaker_name (str, optional): 話者名. デフォルトは"ずんだもん".
            - frame (int, optional): 開始フレーム. デフォルトは0.
            - length (int, optional): 表示フレーム数. デフォルトは60.
            - speed (float, optional): 話速. デフォルトは1.0.

    Returns:
        dict: 更新されたプロジェクトデータ
    """
    new_item = create_voice_item(
        text=instruction["text"],
        speaker_name=instruction.get("speaker_name", "ずんだもん"),
        frame=instruction.get("frame", 0),
        length=instruction.get("length", 60),
        speed=instruction.get("speed", 1.0),
    )
    project_data["Timelines"][0]["Items"].append(new_item)
    return project_data


def _add_latex_item(
    project_data: dict[str, Any], instruction: dict[str, Any]
) -> dict[str, Any]:
    """数式アイテムを追加するロジック (ファイルI/Oはしない)

    Args:
        project_data (dict): プロジェクトデータ
        instruction (dict): 数式アイテムの設定
            - formula (str): LaTeX形式の数式
            - frame (int, optional): 開始フレーム. デフォルトは0.
            - length (int, optional): 表示フレーム数. デフォルトは300.
            - layer (int, optional): レイヤー番号. デフォルトは1.

    Returns:
        dict: 更新されたプロジェクトデータ
    """
    new_item = create_latex_item(
        latex_formula=instruction["formula"],
        frame=instruction.get("frame", 0),
        length=instruction.get("length", 300),
        layer=instruction.get("layer", 1),
    )
    project_data["Timelines"][0]["Items"].append(new_item)
    return project_data


def add_scenes_from_instructions(
    base_project_path: str, instructions: list[dict[str, Any]], output_project_path: str
) -> None:
    """指示リストを元に、YMM4プロジェクトに複数のシーンを追加する

    Args:
        base_project_path (str): ベースとなる.ymmpファイルのパス
        instructions (List[dict]): 追加するシーンの指示リスト
            各指示は以下の形式:
            - type (str): "voice" または "latex"
            - その他のパラメータは _add_voice_item または _add_latex_item のドキュメントを参照
        output_project_path (str): 出力先の.ymmpファイルのパス
    """
    project_data = load_ymmp_project(base_project_path)
    if not project_data:
        return

    for instruction in instructions:
        if instruction["type"] == "voice":
            project_data = _add_voice_item(project_data, instruction)
        elif instruction["type"] == "latex":
            project_data = _add_latex_item(project_data, instruction)
        # elif instruction["type"] == "telop": ... 将来の拡張

    save_ymmp_project(project_data, output_project_path)
    print(f"指示リストに基づいてシーンを追加し、{output_project_path}に保存しました。")
