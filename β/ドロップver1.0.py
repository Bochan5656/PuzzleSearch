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

# 各領域をトリミングして保存する
for row in range(num_rows):
    for col in range(num_cols):
        start_x = col * col_width
        finish_x = (col + 1) * col_width
        start_y = row * row_height
        finish_y = (row + 1) * row_height

        img_trimmed_part = img_trimmed[start_y:finish_y, start_x:finish_x]
        save_path = f'./ScreenShot/IMG_0019_trimmed_part_{row}_{col}.PNG'
        cv2.imwrite(save_path, img_trimmed_part)


