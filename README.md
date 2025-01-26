# HysteresisAnalyzer

## 概要
HysteresisAnalyzerは、磁気ヒステリシス測定データを処理し、グラフを生成してHTMLファイルにまとめるライブラリです。本ライブラリを使用すると、Google Colab上で簡単に実験データの可視化が実施できます。

---

## インストール方法
Google Colab 上で以下のコマンドを実行してください。

```python
from google.colab import drive
drive.mount('/content/drive')

!rm -rf HysteresisAnalyzer/
!git clone https://github.com/shogo-hs/HysteresisAnalyzer.git
!pip install HysteresisAnalyzer/
```

---

## 使用方法

### 1. 必要なモジュールのインポート
```python
from hystan.raw_data_processor import process_csv
from hystan.image import plot_chart, create_empty_figure, combine_figures, generate_html_from_images
from hystan.utils import get_existing_elm_nos

import glob
import os
import gc
from tqdm import tqdm
import matplotlib.pyplot as plt
import tempfile
```

### 2. 設定値の指定
```python
CSV_DIR = "/path/to/csv_data/"  # CSVファイルがあるディレクトリ
X_COLUMN = "H(kOe)"  # x軸に使うカラム名
Y_COLUMN1 = "Rh(Ω)"  # y軸に使うカラム名
Y_COLUMN2 = "dRh/dH(mΩ/Oe)"  # y軸に使うカラム名
FIGSIZE = (8, 8)  # 画像のサイズ
SAVE_PATH = f"/path/to/output/output.html"  # 画像を保存するパス

CHARTS_PER_IMAGE = 9  # 1枚の画像に表示するチャートの数（変更不要）
ELM_NO_MAX = 900  # ELM番号の最大値（変更不要）
```

### 3. ELM番号の取得
```python
csv_files = glob.glob(os.path.join(CSV_DIR, "*.csv"))  # CSVファイル一覧を取得
elm_nos, missing_elm_nos = get_existing_elm_nos(CSV_DIR, ELM_NO_MAX)  # ELM番号を取得
```

### 4. データ処理とグラフ生成
```python
with tempfile.TemporaryDirectory() as tmpdir:
    img_no = 1
    charts = []
    for elm_no in tqdm(range(1, ELM_NO_MAX + 1)):
        csv_path = os.path.join(CSV_DIR, f"RcpNo=1(Hp-R)_ElmNo={elm_no}.csv")

        # elm_noが存在しない場合は空のグラフを作成
        if elm_no in missing_elm_nos:
            fig = create_empty_figure(FIGSIZE)
        else:
            a2_value, df = process_csv(csv_path)
            title = f"X={a2_value['X']}, Y={a2_value['Y']}, CAD={a2_value['CAD']} (elm_no={elm_no})"
            fig = plot_chart(
                data_df=df,
                x_column=X_COLUMN,
                y_column1=Y_COLUMN1,
                y_column2=Y_COLUMN2,
                title=title,
                figsize=FIGSIZE,
            )
        charts.append(fig)
        plt.close(fig)
        del fig
        gc.collect()

        # 9枚の画像を作成したら結合して保存
        if len(charts) == 9:
            combined_fig = combine_figures(charts)
            combined_fig.savefig(os.path.join(tmpdir, f"{str(img_no).zfill(5)}.png"))
            plt.close(combined_fig)
            charts = []
            img_no += 1

            del combined_fig
            gc.collect()

    # 画像をHTMLファイルに変換
    generate_html_from_images(
        input_dir=tmpdir,
        output_html=SAVE_PATH,
        columns=10,
        max_size=1000,
    )
```

---

## 出力結果
- `A1_output2.html` というHTMLファイルが生成され、CSVデータのグラフが埋め込まれます。
- `CHARTS_PER_IMAGE=9` に設定されているため、9つのグラフが1枚の画像としてまとめられます。
- 画像は`10×10`のグリッドで並べられます。

---

## 注意点
- Google Drive 内の `CSV_DIR` に正しくCSVファイルを配置してください。

---
