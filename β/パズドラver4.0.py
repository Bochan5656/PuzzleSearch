import random
import copy

# Define constants
ROW = 3  # 縦
COL = 3  # 横
MAX_TURN = 10  # 最大10手
BEAM_WIDTH = 10  # ビーム幅

# Initialize the game field (small size)
field = [
    [4, 4, 4],  # 横に3つ並べる
    [5, 6, 5],
    [3, 3, 5],
]


# Variables used for tracking
max_count = 0
chainflag = [[0] * COL for _ in range(ROW)]
dummy = [[0] * COL for _ in range(ROW)]
t_erase = [[0] * COL for _ in range(ROW)]
route = [[-1, -1] for _ in range(100)]
f_field = copy.deepcopy(field)  # Copy of the initial field


def fall():
    """C++ 'fall()' function equivalent"""
    global field
    for i in range(ROW - 1, -1, -1):
        for j in range(COL):
            check = i
            while True:
                if check == ROW - 1:
                    break  # 底に到達
                if field[check + 1][j] == 0:  # 下が空マスだったら
                    field[check + 1][j] = field[check][j]  # 落ちる
                    field[check][j] = 0  # 落ちると、上が空マスになる。
                check += 1


def fill_empty_spaces():
    """C++ 'fill_empty_spaces()' function equivalent"""
    global field
    for i in range(ROW):
        for j in range(COL):
            if field[i][j] == 0:  # 空マスだったら埋める
                field[i][j] = rnd(1, 6)  # 1-6の整数乱数


def show_field():
    """C++ 'show_field()' function equivalent"""
    global field
    for i in range(ROW):
        for j in range(COL):
            print(field[i][j], end="")
        print("")
    print("")


def rnd(mini, maxi):
    """C++ 'rnd()' function equivalent"""
    return random.randint(mini, maxi)


def chain(now_row, now_col, d, count):
    global max_count, chainflag, dummy, field
    if now_row < 0 or now_row >= ROW or now_col < 0 or now_col >= COL:
        return  # 範囲外ならreturn

    if field[now_row][now_col] == d and chainflag[now_row][now_col] == 0:
        chainflag[now_row][now_col] = -1  # 探索済みにする
        if max_count < count:
            max_count = count  # 連結ドロップ数の更新

        dummy[now_row][now_col] = -1  # コンボがつながる可能性があるので、-1に設定
        print(f"Chaining at ({now_row}, {now_col}), drop: {d}, count: {count}")  # チェインの出力

        # 再帰的に上下左右を探索
        chain(now_row - 1, now_col, d, count + 1)  # 上
        chain(now_row + 1, now_col, d, count + 1)  # 下
        chain(now_row, now_col - 1, d, count + 1)  # 左
        chain(now_row, now_col + 1, d, count + 1)  # 右


def evaluate():
    global max_count, chainflag, dummy, field
    value = 0
    for row in range(ROW):
        for col in range(COL):
            if chainflag[row][col] == 0 and field[row][col] != 0:
                max_count = 0
                for r in range(ROW):
                    for c in range(COL):
                        dummy[r][c] = 0
                chain(row, col, field[row][col], 1)

                # チェインが3つ以上あるか確認
                if max_count >= 3:
                    if check() == 1:
                        value += 1  # コンボ発生
                        print(f"Combo found: {value} at ({row}, {col})")

    return value


def sum_e():
    """C++ 'sum_e()' function equivalent"""
    global field, t_erase
    combo = 0
    while True:
        for r in range(ROW):
            for c in range(COL):
                t_erase[r][c] = 0

        a = evaluate()  # コンボ発生
        if a == 0:
            break  # コンボが発生しなかったら終了

        for row in range(ROW):
            for col in range(COL):
                if t_erase[row][col] == -1:
                    field[row][col] = 0  # コンボになったドロップは空になる。

        fall()  # 落下処理発生
        combo += a

    return combo


def check():
    global t_erase, dummy, field
    v = 0
    # 横のチェック
    for row in range(ROW):
        for col in range(COL - 2):
            if (dummy[row][col] == -1 and dummy[row][col + 1] == -1 and
                    dummy[row][col + 2] == -1 and field[row][col] == field[row][col + 1] and
                    field[row][col] == field[row][col + 2]):
                t_erase[row][col] = -1
                t_erase[row][col + 1] = -1
                t_erase[row][col + 2] = -1
                v = 1
                print(f"Horizontal match at ({row}, {col})")

    # 縦のチェック
    for col in range(COL):
        for row in range(ROW - 2):
            if (dummy[row][col] == -1 and dummy[row + 1][col] == -1 and
                    dummy[row + 2][col] == -1 and field[row][col] == field[row + 1][col] and
                    field[row][col] == field[row + 2][col]):
                t_erase[row][col] = -1
                t_erase[row + 1][col] = -1
                t_erase[row + 2][col] = -1
                v = 1
                print(f"Vertical match at ({row}, {col})")

    return v




def operation():
    """C++ 'operation()' function equivalent"""
    global field, route
    now_col = route[0][1]
    now_row = route[0][0]

    for i in range(1, MAX_TURN):
        if route[i][0] == -1 or route[i][1] == -1:
            break
        # Swap the positions of the two elements
        field[now_row][now_col], field[route[i][0]][route[i][1]] = field[route[i][0]][route[i][1]], field[now_row][now_col]
        now_col = route[i][1]
        now_row = route[i][0]




class Action:
    """C++ 'Action' structure equivalent"""
    def __init__(self):
        self.score = 0
        self.moving = [[-1, -1] for _ in range(100)]


def BEAM_SEARCH():
    """C++ 'BEAM_SEARCH()' function equivalent"""
    global f_field, route, field
    que = []
    # 1手目を全通り探索する
    for i in range(ROW):
        for j in range(COL):
            cand = {
                'movei': [[-1, -1] for _ in range(100)],
                'score': 0,
                'nowC': j,
                'nowR': i,
                'prev': -1
            }
            cand['movei'][0] = [i, j]
            que.append(cand)

    dx = [-1, 0, 0, 1]
    dy = [0, -1, 1, 0]

    bestAction = Action()
    maxValue = 0

    # 2手目以降をビームサーチで探索
    for i in range(1, MAX_TURN):
        pque = []
        while que:
            temp = que.pop(0)
            for j in range(4):
                cand = copy.deepcopy(temp)
                if 0 <= cand['nowC'] + dx[j] < COL and 0 <= cand['nowR'] + dy[j] < ROW:
                    if cand['prev'] + j == 3:
                        continue
                    cand['nowC'] += dx[j]
                    cand['nowR'] += dy[j]
                    cand['movei'][i] = [cand['nowR'], cand['nowC']]
                    for k in range(len(cand['movei'])):
                        route[k] = cand['movei'][k]
                    # Copy the original field state
                    field = copy.deepcopy(f_field)
                    operation()
                    cand['score'] = sum_e()
                    print(f"Evaluated score: {cand['score']} for move {cand['movei'][:i+1]}")  # スコアの出力
                    cand['prev'] = j
                    pque.append(cand)

        pque.sort(key=lambda x: -x['score'])
        for j in range(min(BEAM_WIDTH, len(pque))):
            temp = pque[j]
            if maxValue < temp['score']:
                maxValue = temp['score']
                bestAction.score = maxValue
                bestAction.moving = copy.deepcopy(temp['movei'])
            if i < MAX_TURN - 1:
                que.append(temp)

    return bestAction


def main():
    fill_empty_spaces()  # 初期盤面生成
    show_field()  # 盤面表示
    global f_field, route, field
    f_field = copy.deepcopy(field)  # 初期盤面を記憶
    tmp = BEAM_SEARCH()  # ビームサーチしてtmpに最善手を保存
    route = copy.deepcopy(tmp.moving)
    print(f"(x,y)=({route[0][1]},{route[0][0]})")  # y座標は下にいくほど大きくなる
    for j in range(1, MAX_TURN):
        if route[j][1] == -1 or route[j][0] == -1:
            break
        if route[j][1] == route[j-1][1] + 1:
            print("RIGHT")
        elif route[j][1] == route[j-1][1] - 1:
            print("LEFT")
        elif route[j][0] == route[j-1][0] + 1:
            print("DOWN")
        elif route[j][0] == route[j-1][0] - 1:
            print("UP")
    field = copy.deepcopy(f_field)
    operation()
    combo = sum_e()
    print(f"{combo}コンボ")


if __name__ == "__main__":
    main()
