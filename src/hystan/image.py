import pandas as pd
import matplotlib.pyplot as plt
import io
from typing import Tuple, List
import matplotlib.image as mpimg
import base64
import os
from PIL import Image
from io import BytesIO


def plot_chart(
    data_df: pd.DataFrame,
    x_column: str = "H(kOe)",
    y_column1: str = "Rh(Ω)",
    y_column2: str = "dRh/dH(mΩ/Oe)",
    figsize: Tuple[int, int] = (8, 8),
    title: str = None,
) -> plt.Figure:
    """
    実験データを基に H(kOe) に対する Rh(Ω) と dRh/dH(mΩ/Oe) のグラフを作成し、Figureオブジェクトを返す。

    グラフは以下の構成で描画される：
    - X軸: 磁場 H(kOe)
    - 左Y軸: 抵抗 Rh(Ω)（スチールブルーでプロット）
    - 右Y軸: 抵抗の微分 dRh/dH(mΩ/Oe)（ダークオレンジでプロット）

    Args:
        data_df (pd.DataFrame): グラフ作成の元となるデータフレーム。
        x_column (str, optional): X軸のデータ列名（デフォルトは "H(kOe)"）。
        y_column1 (str, optional): 左Y軸のデータ列名（デフォルトは "Rh(Ω)"）。
        y_column2 (str, optional): 右Y軸のデータ列名（デフォルトは "dRh/dH(mΩ/Oe)"）。
        figsize (Tuple[int, int], optional): グラフのサイズ (幅, 高さ)（デフォルトは (8, 8)）。
        title (str, optional): グラフのタイトル（デフォルトは None）。

    Returns:
        plt.Figure: 作成したグラフの Figure オブジェクト。
    """
    rh_color = "#4682B4"  # スチールブルー
    drh_color = "#FF8C00"  # ダークオレンジ

    # グラフを描画
    fig, ax1 = plt.subplots(figsize=figsize)  # 正方形の画像サイズ

    # 左側のY軸: Rh(Ω)
    ax1.plot(data_df[x_column], data_df[y_column1], color=rh_color, linewidth=1)
    ax1.set_xlabel(x_column, fontsize=16)
    ax1.set_ylabel(y_column1, color=rh_color, fontsize=16)
    ax1.tick_params(axis="y", labelcolor=rh_color, labelsize=16)
    ax1.tick_params(axis="x", labelsize=16)
    ax1.grid(visible=True, which="major", linestyle="--", linewidth=0.5)

    # 右側のY軸: dRh/dH列
    ax2 = ax1.twinx()
    ax2.plot(data_df[x_column], data_df[y_column2], color=drh_color, linewidth=1)
    ax2.set_ylabel(y_column2, color=drh_color, fontsize=16)
    ax2.tick_params(axis="y", labelcolor=drh_color, labelsize=16)

    # タイトルの設定
    if title:
        ax1.set_title(title, fontsize=22, pad=20)  # タイトルを追加

    # レイアウト調整
    plt.tight_layout()

    # Figureオブジェクトを返す
    return fig


def create_empty_figure(figsize=(8, 8)) -> plt.Figure:
    """
    Create an empty Figure object.

    Returns:
        Figure: Empty Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")  # Hide axes

    return fig


def combine_figures(
    fig_list: List[plt.Figure],
    nrows: int = 3,
    ncols: int = 3,
    figsize: Tuple[int, int] = (12, 12),
) -> plt.Figure:
    """
    複数のFigureを受け取り、それらを1つの Figure にまとめる関数。
    外側の軸線は残しつつ目盛りだけを非表示にする。

    Args:
        fig_list (List[Figure]): 結合したいMatplotlib Figureのリスト
        nrows (int, optional): 行数. Defaults to 3.
        ncols (int, optional): 列数. Defaults to 3.
        figsize (Tuple[int, int], optional): 作成するFigureのサイズ. Defaults to (12, 12).

    Returns:
        Figure: 指定された行列レイアウトでまとめたMatplotlib Figure
    """
    # 期待する枚数を計算
    expected_count = nrows * ncols

    # 実際の枚数が足りない or 多い場合はエラー
    if len(fig_list) != expected_count:
        raise ValueError(
            f"fig_list must contain exactly {expected_count} figures, "
            f"but got {len(fig_list)}."
        )

    # 新しいFigureを作成（nrows×ncolsのサブプロット）
    combined_fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

    # axesが1次元配列になる場合や2次元になる場合に備えてフラット化
    if nrows == 1 and ncols == 1:
        axes = [[axes]]  # 両方1なら軸は1つ
    elif nrows == 1 or ncols == 1:
        axes = [axes] if nrows == 1 else [[ax] for ax in axes]

    # サブプロットそれぞれに元のFigureを画像として配置
    for i, fig in enumerate(fig_list):
        # 元のFigureをメモリ上にPNG形式で保存
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)

        # 保存した画像を読み込み
        img = mpimg.imread(buf)

        # サブプロットに画像を表示
        row = i // ncols
        col = i % ncols
        axes[row][col].imshow(img)

        # 外側の軸線を残して目盛りだけ消す
        axes[row][col].set_xticks([])
        axes[row][col].set_yticks([])

    # レイアウトを整える
    plt.tight_layout()

    return combined_fig


def generate_html_from_images(
    input_dir: str, output_html: str, columns: int = 3, max_size: int = 800
) -> None:
    """
    指定したフォルダ内の画像をHTMLに埋め込み、グリッド状に表示し、クリックでアスペクト比を維持したまま拡大可能にする。

    Args:
        input_dir (str): 画像が保存されているディレクトリのパス。
        output_html (str): 生成するHTMLファイルのパス。
        columns (int, optional): 1行あたりの画像数（デフォルト: 3）。
        max_size (int, optional): 画像の最大サイズ（デフォルト: 800px）。

    Returns:
        None: HTMLファイルを作成するが、戻り値はなし。
    """

    # 画像リストを取得（ソートして並び順を統一）
    image_list: List[str] = sorted(os.listdir(input_dir))

    # HTMLをストリーム書き込み（メモリ節約）
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                .grid-container {{
                    display: grid;
                    grid-template-columns: repeat({columns}, 1fr);
                    gap: 10px;
                    padding: 10px;
                }}
                .grid-container img {{
                    width: 100%;
                    height: auto;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: transform 0.2s;
                }}
                .grid-container img:hover {{
                    transform: scale(1.05);
                }}
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.8);
                    justify-content: center;
                    align-items: center;
                }}
                .modal img {{
                    max-width: 90%;
                    max-height: 90%;
                    object-fit: contain;  /* 元のアスペクト比を維持して拡大 */
                    border-radius: 10px;
                }}
                .modal:target {{
                    display: flex;
                }}
                .close {{
                    position: absolute;
                    top: 10px;
                    right: 20px;
                    font-size: 30px;
                    color: white;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <div class="grid-container">
        """)

        for idx, img_file in enumerate(image_list):
            img_path: str = os.path.join(input_dir, img_file)

            try:
                # 画像を開いて縮小処理（メモリ節約）
                with Image.open(img_path) as img:
                    img.thumbnail((max_size, max_size))  # 指定サイズ以下に縮小

                    # Base64エンコード（メモリに保持しない）
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=80)  # WebPで軽量化
                    encoded_string: str = base64.b64encode(buffer.getvalue()).decode(
                        "utf-8"
                    )

                    # HTMLにBase64データを書き込む（クリックで拡大）
                    f.write(f"""
                    <a href="#img{idx}">
                        <img src="data:image/webp;base64,{encoded_string}" id="thumb{idx}">
                    </a>
                    <div id="img{idx}" class="modal">
                        <a href="#" class="close">&times;</a>
                        <img src="data:image/webp;base64,{encoded_string}">
                    </div>
                    """)

            except Exception as e:
                print(f"エラー（{img_file}）: {e}")

        f.write("""
            </div>
        </body>
        </html>
        """)

    print(f"HTMLファイルが作成されました: {output_html}")
