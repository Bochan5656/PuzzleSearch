import random
import copy

# 定数定義
ROW = 5  # 行数を5に拡張
COL = 6  # 列数を6に拡張
MAX_TURN = 20
BEAM_WIDTH = 500

# グローバル変数
field = [
    [1, 2, 3, 4, 5, 6],
    [2, 3, 4, 5, 6, 1],
    [3, 4, 5, 6, 1, 2],
    [4, 5, 6, 1, 2, 3],
    [5, 6, 1, 2, 3, 4]
]

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
        print(f"Move from ({now_row}, {now_col}) to ({next_row}, {next_col})")

        field[now_row][now_col], field[next_row][next_col] = field[next_row][next_col], field[now_row][now_col]

        now_row, now_col = next_row, next_col

        print("Field after move:")
        show_field()

    print("Final field after all operations:")
    show_field()


def evaluate():
    print("evaluate() called")
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

    print(f"コンボ数: {combo_count}")
    print("ジャッジ行列:")
    for row in judge:
        print(row)

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

    print("Field after fall:")
    show_field()


def sum_e():
    combo = 0
    while True:
        print("Calling evaluate()")
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
