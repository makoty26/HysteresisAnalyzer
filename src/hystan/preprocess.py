import pandas as pd

def split_dataframe_at_turning_point(df: pd.DataFrame, target_col: str = "H_Oe") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    H(kOe) の折り返し点を検出し、折り返し前後で DataFrame を2つに分割してソートする関数。
    
    Parameters:
        df (DataFrame): CSVデータを含むPandas DataFrame。
    
    Returns:
        df1 (DataFrame): 折り返し前のデータ (H(kOe) の降順でソート)
        df2 (DataFrame): 折り返し後のデータ (H(kOe) の昇順でソート)
    """
    # H(kOe) の最小値のインデックスを取得（折り返し点）
    turning_index = df[target_col].idxmin()

    # 折り返し前後でデータを分割
    df1 = df.iloc[:turning_index + 1].copy()  # 折り返し前 (Hが減少する部分)
    df2 = df.iloc[turning_index + 1:].copy()  # 折り返し後 (Hが増加する部分)

    # H(kOe) でソート
    df1 = df1.sort_values(by=target_col, ascending=True).reset_index(drop=True)
    df2 = df2.sort_values(by=target_col, ascending=True).reset_index(drop=True)

    return df1, df2

def apply_moving_average(df, column_name, window_size=10) -> pd.DataFrame:
    """
    指定したカラムに対して移動平均を適用し、新しいカラムを追加する関数。

    Parameters:
        df (DataFrame): 対象のデータフレーム。
        column_name (str): 移動平均を適用するカラム名。
        window_size (int): 移動平均のウィンドウサイズ (デフォルトは10)。

    Returns:
        df (DataFrame): 移動平均が適用された新しいカラムを追加した DataFrame。
    """
    df = df.copy()  # 元のデータを変更しないようにコピー
    new_column_name = f"{column_name}_MA"
    df[new_column_name] = df[column_name].rolling(window=window_size, center=True).mean()
    return df

def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):
    """
    df1 と df2 を統合し、一つのデータセットとして扱う関数。
    
    Parameters:
        df1 (DataFrame): 折り返し前のデータ。
        df2 (DataFrame): 折り返し後のデータ。

    Returns:
        DataFrame: 統合されたデータフレーム。
    """
    return pd.concat([df1, df2], ignore_index=True).sort_values(by="H_kOe").reset_index(drop=True)

def interpolate_and_fill(df1, df2, x_col="H_kOe", y_col="Rh(Ω)"):
    """
    2つの DataFrame を受け取り、それぞれの x 軸の値を補完し、
    y 軸の値で発生した NaN を前後の値で補完する関数。

    Parameters:
        df1 (pd.DataFrame): 1つ目の DataFrame。
        df2 (pd.DataFrame): 2つ目の DataFrame。
        x_col (str): x 軸のカラム名（デフォルト: "H_kOe"）。
        y_col (str): y 軸のカラム名（デフォルト: "Rh(Ω)"）。

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: 補完された df1 と df2。
    """
    # x 軸の補完のため、共通の x 値を作成
    common_x_values = pd.Series(sorted(set(df1[x_col]).union(set(df2[x_col]))))

    def interpolate_and_fill_df(df):
        """
        指定した DataFrame を x 軸で補完し、y 軸の NaN を前後の値で補完する。
        """
        # x 軸の補完
        df_interp = df.set_index(x_col).reindex(common_x_values).reset_index().rename(columns={"index": x_col})

        # y 軸の補間（線形補間）
        df_interp[y_col] = df_interp[y_col].interpolate(method="nearest", limit_direction="both")

        # y 軸の NaN を前後の値で埋める（前方埋め + 後方埋め）
        df_interp[y_col] = df_interp[y_col].ffill().bfill()

        return df_interp

    # df1, df2 の補完を実行
    df1_filled = interpolate_and_fill_df(df1)
    df2_filled = interpolate_and_fill_df(df2)

    return df1_filled, df2_filled