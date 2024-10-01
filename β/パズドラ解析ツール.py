import cv2
import random
import copy

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
img = cv2.imread('./ScreenShot/IMG_0028.PNG')


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

    # 各行を配列に追加
    most_similar_colors.append(row_colors)
    field.append(row_values)

# 数値配列の表示
print("対応する数値の配列 (field):")
for row in field:
    print(row)

# ルート解析
print("-----ルート解析-----")

# 定数定義
ROW = 5  # 行数を5に拡張
COL = 6  # 列数を6に拡張
MAX_TURN = 20
BEAM_WIDTH = 2000

# グローバル変数
route = [[-1, -1] for _ in range(100)]  # スワイプ操作の軌跡を保存する変数を初期化
next_value = 7  # 次に0を埋める数字の初期値

def rnd(mini, maxi):
    return random.randint(mini, maxi)

def fill_empty_spaces():
    global next_value
    for i in range(ROW):
        for j in range(COL):
            if field[i][j] == 0:
                field[i][j] = next_value
                next_value += 1

def show_field():
    for row in field:
        print(" ".join(map(str, row)))

def operation(route):
    now_col = route[0][1]
    now_row = route[0][0]
    for i in range(1, MAX_TURN):
        if route[i][0] == -1 or route[i][1] == -1:
            break
        next_row = route[i][0]
        next_col = route[i][1]
        field[now_row][now_col], field[next_row][next_col] = field[next_row][next_col], field[now_row][now_col]
        now_row, now_col = next_row, next_col

def evaluate():
    judge = [[0] * COL for _ in range(ROW)]
    combo_count = 0
    current_combo_id = 1  # ユニークなコンボグループを追跡

    # 横方向のコンボ判定
    for row in range(ROW):
        col = 0
        while col < COL - 2:
            if 1 <= field[row][col] <= 6 and field[row][col] == field[row][col + 1] and field[row][col] == field[row][col + 2]:
                valid_combo = True
                start_col = col
                while col < COL and field[row][col] == field[row][start_col]:
                    if field[row][col] == 0:
                        valid_combo = False
                    col += 1
                if valid_combo:
                    for c in range(start_col, col):
                        judge[row][c] = current_combo_id
                    combo_count += 1
                    current_combo_id += 1
            else:
                col += 1

    # 縦方向のコンボ判定
    for col in range(COL):
        row = 0
        while row < ROW - 2:
            if 1 <= field[row][col] <= 6 and field[row][col] == field[row + 1][col] and field[row][col] == field[row + 2][col]:
                valid_combo = True
                start_row = row
                while row < ROW and field[row][col] == field[start_row][col]:
                    if field[row][col] == 0:
                        valid_combo = False
                    row += 1
                if valid_combo:
                    for r in range(start_row, row):
                        judge[r][col] = current_combo_id
                    combo_count += 1
                    current_combo_id += 1
            else:
                row += 1

    return combo_count, judge

def fall(judge):
    global next_value
    for col in range(COL):
        empty_slots = 0
        for row in range(ROW - 1, -1, -1):
            if judge[row][col] != 0:
                empty_slots += 1
            elif empty_slots > 0:
                field[row + empty_slots][col] = field[row][col]
                field[row][col] = 0

        for i in range(empty_slots):
            field[i][col] = next_value
            next_value += 1

def sum_e():
    combo = 0
    while True:
        a, judge = evaluate()
        if a == 0:
            break
        fall(judge)
        combo += a
    return combo

def BEAM_SEARCH():
    que = []

    for i in range(ROW):
        for j in range(COL):
            cand = Member()
            cand.nowC = j
            cand.nowR = i
            cand.prev = -1
            cand.movei[0][1] = j
            cand.movei[0][0] = i
            que.append(cand)

    dx = [-1, 0, 0, 1]
    dy = [0, -1, 1, 0]

    bestAction = Action()
    maxValue = 0

    for i in range(1, MAX_TURN):
        pque = []

        while que:
            temp = que.pop(0)
            for j in range(4):
                field[:] = copy.deepcopy(f_field)
                cand = copy.deepcopy(temp)
                if 0 <= cand.nowC + dx[j] < COL and 0 <= cand.nowR + dy[j] < ROW:
                    if cand.prev + j == 3:
                        continue
                    cand.nowC += dx[j]
                    cand.nowR += dy[j]
                    cand.movei[i][0] = cand.nowR
                    cand.movei[i][1] = cand.nowC
                    route[:] = copy.deepcopy(cand.movei)
                    operation(route)
                    cand.score = sum_e()
                    cand.prev = j
                    pque.append(cand)
        pque.sort(reverse=True)

        for j in range(min(BEAM_WIDTH, len(pque))):
            temp = pque[j]
            if maxValue < temp.score:
                maxValue = temp.score
                bestAction.score = maxValue
                for m in range(MAX_TURN):
                    bestAction.moving[m][0] = temp.movei[m][0]
                    bestAction.moving[m][1] = temp.movei[m][1]
            if i < MAX_TURN - 1:
                que.append(temp)
    return bestAction

class Member:
    def __init__(self):
        self.movei = [[-1, -1] for _ in range(100)]
        self.score = 0
        self.nowC = 0
        self.nowR = 0
        self.prev = -1

    def __lt__(self, other):
        return self.score < other.score

class Action:
    def __init__(self):
        self.score = 0
        self.moving = [[-1, -1] for _ in range(100)]

def main():
    global route, field, f_field, next_value
    route = [[-1, -1] for _ in range(100)]
    next_value = 7
    fill_empty_spaces()
    show_field()
    f_field = copy.deepcopy(field)
    tmp = BEAM_SEARCH()
    route[:] = tmp.moving
    print(f"(x,y)=({route[0][1]},{route[0][0]})")
    for j in range(1, MAX_TURN):
        if route[j][1] == -1 or route[j][0] == -1:
            break
        if route[j][1] == route[j - 1][1] + 1:
            print("RIGHT")
        elif route[j][1] == route[j - 1][1] - 1:
            print("LEFT")
        elif route[j][0] == route[j - 1][0] + 1:
            print("DOWN")
        elif route[j][0] == route[j - 1][0] - 1:
            print("UP")
    field[:] = copy.deepcopy(f_field)
    operation(route)
    combo = sum_e()
    print(f"{combo}コンボ")


if __name__ == "__main__":
    main()