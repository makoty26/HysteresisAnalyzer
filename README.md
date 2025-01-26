# HysteresisAnalyzer

## 概要
HysteresisAnalyzerは、磁気ヒステリシス測定データを処理し、グラフを生成してHTMLファイルにまとめるライブラリです．本ライブラリを使用すると、Google Colab上で簡単に実験データの可視化が実施できます．

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

### 1.実行用のnotebookをGoogle Drive上に配置する(初回のみ)
当レポジトリのcli/example.ipynb をダウンロードしGoogle Driveの任意の場所に配置する．

### 2.ファイルを開く
1で配置したファイルをGoogle Drive上でGoogle Colaboratoryを用いて開く．

### 3.パスの設定
2で開いたnotebookの「パラメータの設定」部分で対象となるcsvファイルが格納されているディレクトリ(CAV_PATH)パスや、出力先の場所・ファイルパス(SAVE_PATH)を入力する．

### 4.処理実行
notebookの上のタブ「ランタイム」→「全てのセルを実行」をクリックし、処理を実行．
一番上のセルのドライブのマウント部分でGoogleアカウントへのログイン・許諾が求められるため、これらを実施する．

### 5.出力結果の確認
処理時間はGoogle Colabの仕組み上、時間帯・混雑具合によって左右されるため、5分〜30分目安．
自身で設定したパスにファイルが配置されているため適切に作成できているか確認する．

---

## 出力結果
- `A1_output2.html` というHTMLファイルが生成され、CSVデータのグラフが埋め込まれます．
- `CHARTS_PER_IMAGE=9` に設定されているため、9つのグラフが1枚の画像としてまとめられます．
- 画像は`10×10`のグリッドで並べられます．

---

## 注意点
- Google Drive 内の `CSV_DIR` に正しくCSVファイルを配置してください。

---
