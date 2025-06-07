import json
import uuid
from typing import Any, Optional, TypedDict


class VoiceItemTemplate(TypedDict):
    Frame: int
    Length: int
    Layer: int
    FilePath: str
    X: float
    Y: float
    Zoom: float
    Alpha: float
    ItemType: str
    Serif: str
    Hatsuon: str
    Remark: str
    VoiceLength: str


class YMMPTemplate(TypedDict):
    project_name: str
    project_path: str
    template_data: dict[str, Any]


def create_voice_item_template(
    speaker_name: str = "ずんだもん",
    frame: int = 0,
    length: int = 60,
    file_path: str = "",
) -> dict[str, Any]:
    """
    YMM4のボイスアイテムの基本的なテンプレートをゼロから生成する関数
    """
    # 正常なymmpファイルから抽出した、ボイスアイテムに必要な全フィールドの構造
    template: dict[str, Any] = {
        "$type": "YukkuriMovieMaker.Project.Items.VoiceItem, YukkuriMovieMaker",
        "CharacterName": speaker_name,
        "Serif": "(セリフ)",
        "Pronounce": None,
        "Hatsuon": "(セリフ)",
        "VoiceLength": "00:00:00.0000000",
        "VoiceCache": None,
        "PlaySpeed": 100.0,
        "VoiceVolume": 100.0,
        "Pan": 0.0,
        "IsSplit": False,
        "SplitGap": 5.0,
        "SplitSerif": True,
        "ContinueSerif": False,
        "Frame": frame,
        "Length": length,
        "FilePath": file_path,
        "Layer": 2,  # デフォルトのレイヤー
        "Guid": str(uuid.uuid4()),
        "IsLocked": False,
        "IsHidden": False,
        "Remark": "",
        "Group": 0,
        "X": {"Values": [{"Value": 0.0}], "Span": 0.0, "Centering": "None"},
        "Y": {
            "Values": [{"Value": 400.0}],
            "Span": 0.0,
            "Centering": "None",
        },  # 字幕のデフォルトY座標
        "Z": {"Values": [{"Value": 0.0}], "Span": 0.0, "Centering": "None"},
        "Zoom": {"Values": [{"Value": 100.0}], "Span": 0.0},
        "Alpha": {"Values": [{"Value": 100.0}], "Span": 0.0},
        "RotationX": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "RotationY": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "RotationZ": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "Effects": [],
        "Transitions": [],
    }
    return template


def create_image_item_template() -> dict[str, Any]:
    """
    YMM4の画像アイテムの基本的なテンプレートをゼロから生成する関数
    """
    template: dict[str, Any] = {
        "$type": "YukkuriMovieMaker.Project.Items.ImageItem, YukkuriMovieMaker",
        "FilePath": "",
        "X": {"Values": [{"Value": 0.0}], "Span": 0.0, "Centering": "None"},
        "Y": {"Values": [{"Value": 0.0}], "Span": 0.0, "Centering": "None"},
        "Z": {"Values": [{"Value": 0.0}], "Span": 0.0, "Centering": "None"},
        "Zoom": {"Values": [{"Value": 100.0}], "Span": 0.0},
        "Alpha": {"Values": [{"Value": 100.0}], "Span": 0.0},
        "RotationX": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "RotationY": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "RotationZ": {"Values": [{"Value": 0.0}], "Span": 0.0},
        "Clipping": {
            "IsEnabled": False,
            "X": 0.0,
            "Y": 0.0,
            "Width": 100.0,
            "Height": 100.0,
            "IsRounded": False,
        },
        "Frame": 0,
        "Length": 300,  # デフォルトで5秒
        "Layer": 1,
        "Guid": str(uuid.uuid4()),
        "IsLocked": False,
        "IsHidden": False,
        "Remark": "",
        "Group": 0,
        "Effects": [],
        "Transitions": [],
    }
    return template


def create_ymmp_template(
    project_name: str,
    project_path: str,
    template_data: dict[str, Any],
    output_path: Optional[str] = None,
) -> None:
    """
    YMMPテンプレートを作成する関数

    Args:
        project_name (str): プロジェクト名
        project_path (str): プロジェクトのパス
        template_data (dict[str, Any]): テンプレートデータ
        output_path (Optional[str]): 出力パス (デフォルト: None)
    """
    template: YMMPTemplate = {
        "project_name": project_name,
        "project_path": project_path,
        "template_data": template_data,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=4)


def create_ymmp_template_from_json(
    json_path: str, output_path: Optional[str] = None
) -> None:
    """
    JSONファイルからYMMPテンプレートを作成する関数

    Args:
        json_path (str): JSONファイルのパス
        output_path (Optional[str]): 出力パス (デフォルト: None)
    """
    with open(json_path, encoding="utf-8") as f:
        template_data = json.load(f)

    create_ymmp_template(
        template_data["project_name"],
        template_data["project_path"],
        template_data["template_data"],
        output_path,
    )


def create_ymmp_template_from_dict(
    project_name: str,
    project_path: str,
    template_data: dict[str, Any],
    output_path: Optional[str] = None,
) -> str:
    """
    辞書データからYMMPテンプレートを作成する関数

    Args:
        project_name (str): プロジェクト名
        project_path (str): プロジェクトのパス
        template_data (dict[str, Any]): テンプレートデータ
        output_path (Optional[str]): 出力パス (デフォルト: None)

    Returns:
        str: 作成されたテンプレートのJSON文字列
    """
    template: YMMPTemplate = {
        "project_name": project_name,
        "project_path": project_path,
        "template_data": template_data,
    }

    json_str = json.dumps(template, ensure_ascii=False, indent=4)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_str
