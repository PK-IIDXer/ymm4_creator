import uuid
from typing import Any, Dict, TypedDict


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


def create_voice_item_template(
    speaker_name: str = "ずんだもん",
    frame: int = 0,
    length: int = 60,
    file_path: str = "",
) -> Dict[str, Any]:
    """
    YMM4のボイスアイテムの基本的なテンプレートをゼロから生成する関数
    """
    # 正常なymmpファイルから抽出した、ボイスアイテムに必要な全フィールドの構造
    template: Dict[str, Any] = {
        "$type": "YukkuriMovieMaker.Project.Items.VoiceItem, YukkuriMovieMaker",
        "CharacterName": speaker_name,
        "Serif": "（セリフ）",
        "Pronounce": None,
        "Hatsuon": "（セリフ）",
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


def create_image_item_template() -> Dict[str, Any]:
    """
    YMM4の画像アイテムの基本的なテンプレートをゼロから生成する関数
    """
    template: Dict[str, Any] = {
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
