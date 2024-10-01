import cv2
import numpy as np

# 画像を読み込む
img = cv2.imread('./ScreenShot/IMG_0019.PNG')

# 画像のサイズを取得する
height, width = img.shape[:2]

# 縦方向のトリミング範囲を計算 (下4割)
start_y = int(height * 0.58)  # 画像の上から58%の位置が開始点
finish_y = int(height * 0.96)
# 下4割をトリミングする
img_trimmed = img[start_y:finish_y, 0:width]

# デバッグ用にトリミング後の画像を保存する
cv2.imwrite('./ScreenShot/IMG_0019_trimmed.PNG', img_trimmed)

# トリミングされた画像の新しいサイズを取得
trimmed_height, trimmed_width = img_trimmed.shape[:2]

# 横6列、縦5列に分割する
num_cols = 6
num_rows = 5

# 各領域の幅と高さを計算する
col_width = trimmed_width // num_cols
row_height = trimmed_height // num_rows

# 判別したい色とそのRGB値
colors = {
    "赤": np.array([75, 116, 255]),
    "緑": np.array([102, 227, 82]),
    "青": np.array([75, 116, 255]),
    "黄": np.array([158, 255, 255]),
    "紫": np.array([121, 38, 86]),
    "ピンク": np.array([128, 35, 216])
}


# 最も近い色を判別する関数
def classify_color(bgr_color):
    """BGR形式の色を指定された色に分類する関数"""
    min_distance = float('inf')
    closest_color = "不明"

    for color_name, rgb_value in colors.items():
        # BGRをRGBに変換してから距離を計算
        distance = np.linalg.norm(np.array([bgr_color[2], bgr_color[1], bgr_color[0]]) - rgb_value)
        if distance < min_distance:
            min_distance = distance
            closest_color = color_name

    return closest_color


# 6x5の配列を初期化
color_matrix = []

# 各領域をトリミングして保存し、中央の色を判別
for row in range(num_rows):
    row_colors = []
    for col in range(num_cols):
        start_x = col * col_width
        finish_x = (col + 1) * col_width
        start_y = row * row_height
        finish_y = (row + 1) * row_height

        img_trimmed_part = img_trimmed[start_y:finish_y, start_x:finish_x]
        save_path = f'./ScreenShot/IMG_0019_trimmed_part_{row}_{col}.PNG'
        cv2.imwrite(save_path, img_trimmed_part)

        # 中央周囲の5x5ピクセルの平均色を計算
        center_x = col_width // 2
        center_y = row_height // 2
        neighborhood = img_trimmed_part[
                       center_y - 2:center_y + 3,
                       center_x - 2:center_x + 3
                       ]
        avg_color = np.mean(neighborhood, axis=(0, 1)).astype(int)

        classified_color = classify_color(avg_color)

        # 平均RGB値と判別結果を表示
        print(f'位置 ({row}, {col}) の中央色の平均RGB: {avg_color} -> 判別結果: {classified_color}')

        # 判別した色を行に追加
        row_colors.append(classified_color)

    # 各行を配列に追加
    color_matrix.append(row_colors)

# 結果の6x5の配列を表示
for row in color_matrix:
    print(row)
