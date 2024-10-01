import random
import copy

# 定数定義
ROW = 3
COL = 3
MAX_TURN = 10
BEAM_WIDTH = 10

# グローバル変数
field = [
    [5, 3, 6],
    [4, 4, 5],
    [4, 3, 5]
]

# 連結ドロップ数
max_count = 0

# 未探索ドロップか否か格納する配列
chainflag = [[0] * COL for _ in range(ROW)]

# 消去ドロップがありうるか格納する配列
dummy = [[0] * COL for _ in range(ROW)]

# 消去ドロップか否か格納する配列
t_erase = [[0] * COL for _ in range(ROW)]

# スワイプで移動する座標を格納する配列
route = [[-1, -1] for _ in range(100)]

# スワイプ前の盤面
f_field = copy.deepcopy(field)


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


def show_field():
    for row in field:
        print(" ".join(map(str, row)))


def fall():
    for i in range(ROW - 1, -1, -1):
        for j in range(COL):
            check = i
            while check < ROW - 1:
                if field[check + 1][j] == 0:
                    field[check + 1][j] = field[check][j]
                    field[check][j] = 0
                check += 1


def fill_empty_spaces():
    for i in range(ROW):
        for j in range(COL):
            if field[i][j] == 0:
                field[i][j] = rnd(1, 6)


def chain(now_row, now_col, d, count):
    global max_count
    if now_row < 0 or now_row >= ROW or now_col < 0 or now_col >= COL:
        return

    if field[now_row][now_col] == d and chainflag[now_row][now_col] == 0:
        chainflag[now_row][now_col] = -1
        if max_count < count:
            max_count = count
        dummy[now_row][now_col] = -1

        chain(now_row - 1, now_col, d, count + 1)
        chain(now_row + 1, now_col, d, count + 1)
        chain(now_row, now_col - 1, d, count + 1)
        chain(now_row, now_col + 1, d, count + 1)


def evaluate():
    value = 0
    global max_count
    global chainflag

    chainflag = [[0] * COL for _ in range(ROW)]

    for row in range(ROW):
        for col in range(COL):
            if chainflag[row][col] == 0 and field[row][col] != 0:
                max_count = 0
                dummy = [[0] * COL for _ in range(ROW)]
                chain(row, col, field[row][col], 1)
                if max_count >= 3:
                    if check() == 1:
                        value += 1
    return value


def sum_e():
    combo = 0
    while True:
        global t_erase
        t_erase = [[0] * COL for _ in range(ROW)]
        a = evaluate()
        if a == 0:
            break
        for row in range(ROW):
            for col in range(COL):
                if t_erase[row][col] == -1:
                    field[row][col] = 0
        fall()
        fill_empty_spaces()
        combo += a
    return combo


def check():
    v = 0
    for row in range(ROW):
        for col in range(COL - 2):
            if (dummy[row][col] == -1 and dummy[row][col + 1] == -1 and dummy[row][col + 2] == -1 and
                    field[row][col] == field[row][col + 1] and field[row][col] == field[row][col + 2]):
                t_erase[row][col] = -1
                t_erase[row][col + 1] = -1
                t_erase[row][col + 2] = -1
                v = 1

    for col in range(COL):
        for row in range(ROW - 2):
            if (dummy[row][col] == -1 and dummy[row + 1][col] == -1 and dummy[row + 2][col] == -1 and
                    field[row][col] == field[row + 1][col] and field[row][col] == field[row + 2][col]):
                t_erase[row][col] = -1
                t_erase[row + 1][col] = -1
                t_erase[row + 2][col] = -1
                v = 1
    return v


def operation(route):
    now_col = route[0][1]
    now_row = route[0][0]
    print("Initial position:", now_row, now_col)  # 初期位置の確認
    for i in range(1, MAX_TURN):
        if route[i][0] == -1 or route[i][1] == -1:
            break
        print(f"Move from ({now_row}, {now_col}) to ({route[i][0]}, {route[i][1]})")  # 移動の追跡
        # ここで入れ替え操作を行う
        field[now_row][now_col], field[route[i][0]][route[i][1]] = field[route[i][0]][route[i][1]], field[now_row][now_col]
        now_col = route[i][1]
        now_row = route[i][0]
        print("Field after move:")
        show_field()  # 各移動後の盤面を表示
    print("Final field after all operations:")
    show_field()


def rnd(mini, maxi):
    return random.randint(mini, maxi)


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


def main():
    global route, field, f_field
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
    operation(route)  # 盤面をスワイプ後に表示
    combo = sum_e()
    print(f"{combo}コンボ")

if __name__ == "__main__":
    main()
