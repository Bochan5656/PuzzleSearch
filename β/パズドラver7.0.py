import random
import copy

# 定数定義
ROW = 5  # 行数を5に拡張
COL = 6  # 列数を6に拡張
MAX_TURN = 30
BEAM_WIDTH = 1000

# グローバル変数
field = [
    [1, 2, 3, 4, 5, 6],
    [2, 3, 4, 5, 6, 1],
    [3, 4, 5, 6, 1, 2],
    [4, 5, 6, 1, 2, 3],
    [5, 6, 1, 2, 3, 4]
]

route = [[-1, -1] for _ in range(100)]  # スワイプ操作の軌跡を保存する変数を初期化


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
        for col in range(1, COL - 1):
            if (field[row][col] != 0 and
                    field[row][col] == field[row][col - 1] and
                    field[row][col] == field[row][col + 1]):

                if judge[row][col - 1] == 0 and judge[row][col] == 0 and judge[row][col + 1] == 0:
                    combo_count += 1
                    judge[row][col - 1] = current_combo_id
                    judge[row][col] = current_combo_id
                    judge[row][col + 1] = current_combo_id
                    print(f"横方向のコンボ発見: 行 {row}, 列 {col - 1} から {col + 1} まで")
                    current_combo_id += 1

    # 縦方向のコンボ判定
    for col in range(COL):
        for row in range(1, ROW - 1):
            if (field[row][col] != 0 and
                    field[row][col] == field[row - 1][col] and
                    field[row][col] == field[row + 1][col]):

                if judge[row - 1][col] == 0 and judge[row][col] == 0 and judge[row + 1][col] == 0:
                    combo_count += 1
                    judge[row - 1][col] = current_combo_id
                    judge[row][col] = current_combo_id
                    judge[row + 1][col] = current_combo_id
                    print(f"縦方向のコンボ発見: 列 {col}, 行 {row - 1} から {row + 1} まで")
                    current_combo_id += 1

    print(f"コンボ数: {combo_count}")
    print("ジャッジ行列:")
    for row in judge:
        print(row)

    return combo_count, judge



def fall(judge):
    for col in range(COL):
        # 現在の列で上から順に確認し、空いたスペースを埋める
        empty_slots = 0  # 空のスロット数をカウント
        for row in range(ROW - 1, -1, -1):
            if judge[row][col] != 0:
                empty_slots += 1  # コンボが発生した位置をカウント
            elif empty_slots > 0:
                # ドロップを空いたスペースに落とす
                field[row + empty_slots][col] = field[row][col]
                field[row][col] = 0  # 元の位置を空にする

        # 残った上の部分に新しいドロップを補充する（ここでは0にしているが、fill_empty_spacesで埋める）
        for i in range(empty_slots):
            field[i][col] = 0

    print("Field after fall:")
    show_field()  # ドロップが落ちた後の盤面を表示



def sum_e():
    combo = 0
    while True:
        print("Calling evaluate()")
        a, judge = evaluate()
        if a == 0:
            break
        fall(judge)
        combo += a
        fill_empty_spaces()  # 空白を埋めて新しいドロップを追加
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
                    if cand.prev + j == 3:  # 逆方向には移動しないようにする
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
    route = [[-1, -1] for _ in range(100)]
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
