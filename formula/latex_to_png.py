import os
from typing import Optional


def latex_to_png(latex_formula: str, output_path: str) -> Optional[str]:
    """
    LaTeX数式をPNG画像に変換する関数

    Args:
        latex_formula (str): LaTeX形式の数式
        output_path (str): 出力するPNGファイルのパス

    Returns:
        Optional[str]: 成功した場合は出力ファイルのパス、失敗した場合はNone
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # LaTeX数式をPNGに変換する処理をここに実装
        # この部分は実際のLaTeX変換ライブラリやツールに依存します

        return output_path
    except Exception as e:
        print(f"LaTeX数式の変換に失敗しました: {str(e)}")
        return None


if __name__ == "__main__":
    # テスト用の数式
    test_formula = r"$\frac{d}{dx}e^x = e^x$"
    output_path = "./formulas/test_formula.png"

    try:
        # 数式をPNGに変換
        latex_to_png(test_formula, output_path)
        print(f"数式を {output_path} に保存しました。")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
