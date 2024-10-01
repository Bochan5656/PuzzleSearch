import random
import copy

# 定数定義
ROW = 3
COL = 3
MAX_TURN = 10
BEAM_WIDTH = 50

# グローバル変数
field = [
    [5, 3, 3],
    [4, 4, 5],
    [4, 3, 5]
]

route = [[-1, -1] for _ in range(100)]  # routeを初期化


# ランダムドロップ生成のための関数
def rnd(mini, maxi):
    return random.randint(mini, maxi)


def fill_empty_spaces():
    for i in range(ROW):
        for j in range(COL):
            if field[i][j] == 0:
                field[i][j] = rnd(1, 6)


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

        # ドロップの入れ替えをシンプルに行う
        field[now_row][now_col], field[next_row][next_col] = field[next_row][next_col], field[now_row][now_col]

        # 更新後の位置を追跡
        now_row, now_col = next_row, next_col

        # 各移動後のフィールド状態を表示
        print("Field after move:")
        show_field()

    print("Final field after all operations:")
    show_field()


def evaluate():
    print("evaluate() called")  # 関数が呼び出されたかを確認するためのデバッグ出力
    judge = [[0] * COL for _ in range(ROW)]
    combo_count = 0

    # 横方向のコンボ判定
    for row in range(ROW):
        for col in range(1, COL - 1):
            if field[row][col] == field[row][col - 1] and field[row][col] == field[row][col + 1]:
                max_val = max(judge[row][col - 1], judge[row][col], judge[row][col + 1])
                if max_val != 0:
                    judge[row][col - 1] = judge[row][col] = judge[row][col + 1] = max_val
                else:
                    combo_count += 1
                    judge[row][col - 1] = judge[row][col] = judge[row][col + 1] = combo_count
                print(f"Horizontal combo found at row {row}, columns {col - 1} to {col + 1}")

    # 縦方向のコンボ判定
    for col in range(COL):
        for row in range(1, ROW - 1):
            if field[row][col] == field[row - 1][col] and field[row][col] == field[row + 1][col]:
                max_val = max(judge[row - 1][col], judge[row][col], judge[row + 1][col])
                if max_val != 0:
                    judge[row - 1][col] = judge[row][col] = judge[row + 1][col] = max_val
                else:
                    combo_count += 1
                    judge[row - 1][col] = judge[row][col] = judge[row + 1][col] = combo_count
                print(f"Vertical combo found at column {col}, rows {row - 1} to {row + 1}")

    print(f"Combo count: {combo_count}")
    print("Judge matrix:")
    for row in judge:
        print(row)

    return combo_count, judge


def fall(judge):
    for col in range(COL):
        for row in range(ROW - 1, -1, -1):
            if judge[row][col] != 0:  # 消去されたドロップがあれば
                for k in range(row, 0, -1):
                    field[k][col] = field[k - 1][col]
                field[0][col] = rnd(1, 6)  # 一番上に新しいドロップを生成


def sum_e():
    combo = 0
    while True:
        print("Calling evaluate()")  # evaluate()関数が呼び出されているか確認
        a, judge = evaluate()  # judge を受け取る
        if a == 0:
            break
        fall(judge)  # judge を渡す
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
    global route, field, f_field
    route = [[-1, -1] for _ in range(100)]  # routeを初期化
    fill_empty_spaces()  # 空マスを埋める
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
