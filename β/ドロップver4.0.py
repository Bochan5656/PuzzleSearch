import cv2
import numpy as np

# 基準画像を読み込む
reference_images = {
    '赤': cv2.imread('./ScreenShot/赤.PNG'),
    '緑': cv2.imread('./ScreenShot/緑.PNG'),
    '青': cv2.imread('./ScreenShot/青.PNG'),
    '黄': cv2.imread('./ScreenShot/黄.PNG'),
    '紫': cv2.imread('./ScreenShot/紫.PNG'),
    'ピンク': cv2.imread('./ScreenShot/ピンク.PNG')
}

# 処理する画像を読み込む
img = cv2.imread('./ScreenShot/IMG_0024.PNG')


# ヒストグラムを計算する関数
def calculate_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()


# 画像のサイズを取得する
height, width = img.shape[:2]

# 縦方向のトリミング範囲を計算
start_y = int(height * 0.58)
finish_y = int(height * 0.96)
img_trimmed = img[start_y:finish_y, 0:width]

# トリミング後の画像を保存
cv2.imwrite('./ScreenShot/IMG_trimmed.PNG', img_trimmed)

# トリミング後の画像の新しいサイズを取得
trimmed_height, trimmed_width = img_trimmed.shape[:2]

# 横6列、縦5列に分割
num_cols = 6
num_rows = 5
col_width = trimmed_width // num_cols
row_height = trimmed_height // num_rows

# 6x5の配列を初期化して、各領域で最も類似度が高い色を格納
most_similar_colors = []
field = []

# 色と数字の対応関係を定義
color_to_value = {
    '赤': 1,
    '緑': 2,
    '青': 3,
    '黄': 4,
    '紫': 5,
    'ピンク': 6
}

# 各領域をトリミングして基準画像との類似度を計算
for row in range(num_rows):
    row_colors = []
    row_values = []
    for col in range(num_cols):
        start_x = col * col_width
        finish_x = (col + 1) * col_width
        start_y = row * row_height
        finish_y = (row + 1) * row_height

        img_trimmed_part = img_trimmed[start_y:finish_y, start_x:finish_x]
        save_path = f'./ScreenShot/IMG_trimmed_part_{row}_{col}.PNG'
        cv2.imwrite(save_path, img_trimmed_part)

        part_hist = calculate_histogram(img_trimmed_part)

        # 各基準画像との類似度を計算
        best_similarity = -1
        best_color = None
        for color, reference_image in reference_images.items():
            reference_hist = calculate_histogram(reference_image)
            similarity = cv2.compareHist(reference_hist, part_hist, cv2.HISTCMP_CORREL)

            # 最も類似度が高い色を選択
            if similarity > best_similarity:
                best_similarity = similarity
                best_color = color

        # 最も類似度が高い色を行に追加
        row_colors.append(best_color)
        row_values.append(color_to_value[best_color])
        print(f'位置 ({row}, {col}) の最も類似度が高い色: {best_color} (類似度: {best_similarity:.4f})')

    # 各行を配列に追加
    most_similar_colors.append(row_colors)
    field.append(row_values)

# 結果の6x5の配列を表示
print("最も類似度が高い色の配列:")
for row in most_similar_colors:
    print(row)

# 数値配列の表示
print("対応する数値の配列 (field):")
for row in field:
    print(row)
