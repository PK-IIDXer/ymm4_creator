import argparse
from pathlib import Path

from add_voice import add_voice_scene
from config import DEFAULT_OUTPUT_DIR
from formula.add_latex import add_latex_scene


def main() -> None:
    r"""メイン関数
    # 音声を追加
    python main.py ./base.ymmp voice --text "これはテストなのだ"

    # 数式を追加
    python main.py ./base.ymmp latex --formula "$e^{i\pi}=-1$"
    """

    parser = argparse.ArgumentParser(
        description="YMM4プロジェクトにアイテムを自動で追加します。"
    )
    parser.add_argument("base_project", help="ベースとなる.ymmpファイルのパス")

    # サブコマンドで機能を選択できるようにする
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 音声追加コマンド
    parser_voice = subparsers.add_parser("voice", help="音声アイテムを追加します。")
    parser_voice.add_argument("-t", "--text", required=True, help="読み上げるセリフ")
    parser_voice.add_argument("-s", "--speaker", default="ずんだもん", help="話者名")

    # 数式追加コマンド
    parser_latex = subparsers.add_parser("latex", help="数式アイテムを追加します。")
    parser_latex.add_argument("-f", "--formula", required=True, help="LaTeX形式の数式")

    args = parser.parse_args()

    base_project_path = Path(args.base_project)
    output_project_path = (
        Path(DEFAULT_OUTPUT_DIR) / f"{base_project_path.stem}_output.ymmp"
    )

    if args.command == "voice":
        print(f"音声アイテムを追加中: {args.text}")
        add_voice_scene(
            str(base_project_path),
            args.text,
            str(output_project_path),
            speaker_name=args.speaker,
        )
    elif args.command == "latex":
        print(f"数式アイテムを追加中: {args.formula}")
        add_latex_scene(str(base_project_path), args.formula, str(output_project_path))


if __name__ == "__main__":
    main()
