"""
YMM4プロジェクト操作用の共通ユーティリティ関数を提供するパッケージ
"""

from .ymmp_templates import create_voice_item_template
from .ymmp_utils import (
    get_last_frame,
    get_wav_duration_and_frames,
    load_ymmp_project,
    save_ymmp_project,
)

__all__ = [
    "get_last_frame",
    "get_wav_duration_and_frames",
    "load_ymmp_project",
    "save_ymmp_project",
    "create_voice_item_template",
]

# 型チェック用のマーカー
__py_typed__ = True
