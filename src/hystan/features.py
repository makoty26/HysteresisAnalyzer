import numpy as np
import pandas as pd
from hystan.preprocess import merge_dataframes, interpolate_and_fill


def compute_pseudo_area_random_sampling(df_upper, df_lower, y_column) -> float:
    """
    Y 軸の最小値を 0 に正規化し、データ数が少ない側に合わせてランダムサンプリングでデータ数を揃え、
    擬似的な面積を計算し、その差を取る関数。

    Parameters:
        df_upper (DataFrame): 上のグラフのデータ (x_column, y_column を含む)。
        df_lower (DataFrame): 下のグラフのデータ (x_column, y_column を含む)。
        x_column (str): X 軸のカラム名（例: "H_kOe"）。

    Returns:
        float: 2つのグラフの間の面積（擬似的な積算値から求めた面積）。
    """

    # Y 軸の最小値を取得して正規化
    y_min = min(df_upper[y_column].min(), df_lower[y_column].min())
    df_upper_norm = df_upper.copy()
    df_lower_norm = df_lower.copy()
    df_upper_norm[y_column] -= y_min
    df_lower_norm[y_column] -= y_min

    # データ数の少ない側を基準にデータをランダムサンプリングで揃える
    N_upper = len(df_upper_norm)
    N_lower = len(df_lower_norm)
    N_min = min(N_upper, N_lower)

    if N_upper > N_lower:
        df_upper_sampled = df_upper_norm.sample(
            N_min, random_state=42
        )  # 上側をランダムサンプリング
        df_lower_sampled = df_lower_norm
    else:
        df_upper_sampled = df_upper_norm
        df_lower_sampled = df_lower_norm.sample(
            N_min, random_state=42
        )  # 下側をランダムサンプリング

    # Y値を足し合わせる（擬似的な面積を取得）
    sum_upper = np.sum(df_upper_sampled[y_column])
    sum_lower = np.sum(df_lower_sampled[y_column])

    # 面積の差分を計算（擬似的な面積差）
    pseudo_area = np.abs(sum_upper - sum_lower)
    return pseudo_area


def compute_change_rate_stats(
    df: pd.DataFrame, column_name: str
) -> tuple[float, float]:
    """
    データフレームの前の値からの変化率の平均と分散を算出する関数。

    Parameters:
        df (DataFrame): 計算対象のデータフレーム。
        column_name (str): 変化率を計算するカラム名。

    Returns:
        dict: 変化率の平均と分散を含む辞書。
    """
    # 変化率を計算（前の値との差分の割合）
    df["change_rate"] = df[column_name].pct_change()

    # 変化率の統計量を計算
    mean_change_rate = df["change_rate"].mean()
    var_change_rate = df["change_rate"].var()

    return mean_change_rate, var_change_rate


def compute_zero_crossings(df1: pd.DataFrame, df2: pd.DataFrame, y_column: str) -> int:
    """
    df1 と df2 それぞれに対してゼロ交差回数を計算し、その合計を返す関数。

    Parameters:
        df1 (DataFrame): 折り返し前のデータ。
        df2 (DataFrame): 折り返し後のデータ。
        y_column (str): ゼロ交差を計算するカラム名（例: "Rh(Ω)"）。

    Returns:
        int: df1 と df2 のゼロ交差回数の合計。
    """

    def compute(df):
        zero_crossings = np.where(np.diff(np.sign(df[y_column])))[0]
        return len(zero_crossings)

    zero_df1 = compute(df1)
    zero_df2 = compute(df2)
    return zero_df1 + zero_df2


def compute_range(df1, df2, y_column) -> float:
    """
    df1 と df2 を統合したデータに対して、指定したカラムの範囲（最大値 - 最小値）を計算する関数。

    Parameters:
        df1 (DataFrame): 折り返し前のデータ。
        df2 (DataFrame): 折り返し後のデータ。
        y_column (str): 範囲を計算するカラム名（例: "Rh(Ω)"）。

    Returns:
        float: 統合データの最大値 - 最小値の範囲。
    """
    df = merge_dataframes(df1, df2)
    return df[y_column].max() - df[y_column].min()


def get_gradient_at_fraction(df, fraction, x_col="H_kOe", y_col="Rh") -> float:
    """
    指定したデータの縦幅（割合）に基づいて勾配を計算する関数。
    データの先頭を0、末尾を1とし、指定した割合に最も近いデータ点の勾配を返す。
    NaN を除外した状態で y_col の値がすべて同じ場合、勾配は 0 を返す。

    Parameters:
        df (DataFrame): 入力データフレーム。
        fraction (float): 取得したい位置の割合（0: 先頭, 1: 末尾）。
        x_col (str): x 軸のカラム名（デフォルト: "H_kOe"）。
        y_col (str): y 軸のカラム名（デフォルト: "Rh(Ω)"）。

    Returns:
        float: 指定した割合での勾配。
    """
    # NaN を除外した y の値がすべて同じ場合、勾配は常に 0
    if df[y_col].dropna().nunique() == 1:
        return 0.0

    # インデックスの範囲を取得
    index = int(round(fraction * (len(df) - 1)))

    # x, y 値のリストを取得
    x = df[x_col].to_numpy()
    y = df[y_col].to_numpy()

    # 中央差分を用いた勾配計算
    dy_dx = np.gradient(y, x)

    # 指定インデックスの勾配を返す
    return float(dy_dx[index])


def compute_y_deviation(df1, df2, x_col="H_kOe", y_col="Rh(Ω)", fraction=0.5):
    """
    2つの DataFrame に対し、指定した x 軸の割合における y 値の乖離を算出する関数。
    内部で x 軸を補完し、y 軸の NaN を補間後に計算する。

    Parameters:
        df1 (pd.DataFrame): 1つ目の DataFrame（補完前）。
        df2 (pd.DataFrame): 2つ目の DataFrame（補完前）。
        x_col (str): x 軸のカラム名（デフォルト: "H_kOe"）。
        y_col (str): y 軸のカラム名（デフォルト: "Rh(Ω)"）。
        fraction (float): 計算する x 軸の割合（0.0 から 1.0）。

    Returns:
        float: 指定割合の y 値の乖離（絶対値）。
    """

    # df1, df2 の補完を実行（元データを上書きしない）
    df1_filled, df2_filled = interpolate_and_fill(df1.copy(), df2.copy(), x_col, y_col)

    # インデックスの取得（データフレームの縦幅に基づく位置）
    index_df1 = int(round(fraction * (len(df1_filled) - 1)))
    index_df2 = int(round(fraction * (len(df2_filled) - 1)))

    # 対応する y 値を取得
    y_df1 = df1_filled.iloc[index_df1][y_col]
    y_df2 = df2_filled.iloc[index_df2][y_col]

    # y 値の乖離を計算（絶対差）
    deviation = abs(y_df1 - y_df2)

    return float(deviation)


def compute_y_ratio(df1, df2, x_col="H_kOe", y_col="Rh(Ω)", fraction=0.5):
    df1_filled, df2_filled = interpolate_and_fill(df1.copy(), df2.copy(), x_col, y_col)

    # y 軸の最小値を 0 にシフト
    y_min = min(df1_filled[y_col].min(), df2_filled[y_col].min())
    df1_filled[y_col] -= y_min
    df2_filled[y_col] -= y_min

    # インデックスの取得
    index_df1 = int(round(fraction * (len(df1_filled) - 1)))
    index_df2 = int(round(fraction * (len(df2_filled) - 1)))

    # y 値の取得
    y_df1 = df1_filled.iloc[index_df1][y_col]
    y_df2 = df2_filled.iloc[index_df2][y_col]

    # ゼロや極小値による inf を防ぐ
    epsilon = 1e-10
    if abs(y_df2) < epsilon:
        y_df2 = epsilon  # 0 なら小さい値に置き換える

    ratio = y_df1 / y_df2

    return float(ratio)
