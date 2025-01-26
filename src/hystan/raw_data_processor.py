import pandas as pd
import matplotlib.pyplot as plt
import io
from typing import Dict, Optional, Tuple
from hystan.image import plot_chart


def process_a2_value(a2_text: str) -> Optional[Dict[str, float]]:
    """csvのメタデータ行(A2)からCAD, Y, X, R[Front], R[Rear]の値を抽出する関数.

    Args:
        a2_text(str): 抽出対象のメタデータが含まれる行(csvのA2)

    Returns:
        Optional[Dict[str, float]]: A2の情報（CAD, Y, X, R[Front], R[Rear]）
    """
    try:
        # CAD, Y, X, R[Front], R[Rear]を抽出
        cad_part = a2_text.split(" ")[0]
        y_value = int(a2_text.split("Y=")[1].split(" ")[0])  # Y=10
        x_value = int(a2_text.split("X=")[1].split(" ")[0])  # X=10
        front_value = float(
            a2_text.split("R[Front]:")[1].split(" ")[0].replace("kΩ", "")
        )  # R[Front]
        rear_value = float(a2_text.split("R[Rear]:")[1].replace("kΩ", ""))  # R[Rear]

        return {
            "CAD": cad_part.replace("CAD", ""),
            "Y": y_value,
            "X": x_value,
            "R[Front]": front_value,
            "R[Rear]": rear_value,
        }
    except Exception as e:
        print(f"A2行の値から各項目が抽出できません: {e}")
        return None


def process_csv(file_path: str) -> Optional[Tuple[Dict[str, float], pd.DataFrame]]:
    """
    CSVファイルを処理し、メタデータ（A2情報）とデータフレームを取得する関数

    Args:
        file_path (str): CSVファイルのパス

    Returns:
        Optional[Tuple[Dict[str, float], pd.DataFrame]]:
            - A2の情報（CAD, Y, X, R[Front], R[Rear]）
            - データフレーム
    """
    with open(file_path, "r", encoding="cp932") as file:
        lines = file.readlines()

    # メタデータ取得（2行目）
    meta_data_line = lines[1].strip()
    a2_values = process_a2_value(meta_data_line)

    # 実データ取得（9行目以降）
    data_text = "\n".join(lines[8:])
    data_df = pd.read_csv(io.StringIO(data_text), encoding="shift_jis")

    # `-∞` や `∞` を含む全カラムのデータを数値に変換し、変換できない値は NaN にする
    data_df = data_df.map(lambda x: pd.to_numeric(x, errors="coerce"))

    # NaN を含む行を全て削除
    data_df = data_df.dropna()

    # H(kOe)カラムの追加
    data_df = (
        data_df.copy()
    )  # SettingWithCopyWarning対策でDataFrame のスライスを新しい DataFrame にする
    data_df["H(kOe)"] = data_df["H(Oe)"] / 1000

    # [*Clip]という文字列がカラム内にあれば削除
    data_df.columns = data_df.columns.str.replace(r"\[.*\]", "", regex=True)

    return a2_values, data_df


def process_csv_and_visualize(
    file_path: str,
) -> Optional[Tuple[Dict[str, float], plt.Figure]]:
    """
    CSVファイルを処理し、グラフを可視化する関数

    Args:
        file_path (str): CSVファイルのパス

    Returns:
        Optional[Tuple[Dict[str, float], plt.Figure]]:
            - A2の情報（CAD, Y, X, R[Front], R[Rear]）
            - グラフのFigureオブジェクト
    """
    result = process_csv(file_path)
    if result is None:
        return None

    a2_values, data_df = result
    title = f"X={a2_values['X']}, Y={a2_values['Y']}, CAD={a2_values['CAD']}"
    fig = plot_chart(data_df, title=title)

    return a2_values, fig
