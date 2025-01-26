import os
import glob
from typing import Tuple, Set, Optional
import re


def get_existing_elm_nos(csv_dir: str, max_elm_no=900) -> Tuple[Set[int], Set[int]]:
    """指定ディレクトリ内のCSVファイルから elm_no を取得し、存在しない elm_no を特定する"""
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    elm_nos = {extract_elm_no_from_path(csv_file) for csv_file in csv_files}
    missing_elm_nos = set(range(1, max_elm_no + 1)) - elm_nos
    return elm_nos, missing_elm_nos


def extract_elm_no_from_path(file_path: str) -> Optional[int]:
    """
    ファイルパスから ElmNo の値を抽出する関数

    Args:
        file_path (str): ファイルパス

    Returns:
        Optional[int]: 抽出された ElmNo の値（存在しない場合は None）
    """
    try:
        # ファイル名を取得
        file_name = os.path.basename(file_path)
        # ElmNo=の後の数字を抽出
        match = re.search(r"ElmNo=(\d+)", file_name)
        if match:
            return int(match.group(1))  # 抽出された数字を整数に変換
        return None
    except Exception as e:
        print(f"Error extracting ElmNo: {e}")
        return None
