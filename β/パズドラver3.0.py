import numpy as np
import random
import time
from queue import PriorityQueue

# 定数
ROW = 5  # 縦
COL = 6  # 横
MAX_TURN = 40  # 最大40手
BEAM_WIDTH = 50  # ビーム幅

# 盤面
field = np.array([
    [5, 3, 6, 1, 3, 2],
    [6, 4, 5, 6, 1, 4],
    [6, 4, 5, 4, 6, 4],
    [1, 6, 4, 6, 2, 5],
    [4, 3, 4, 6, 2, 5]
])

# 連結ドロップ数
max_count = 0

# 未探索ドロップか否か格納する配列
chainflag = np.zeros((ROW, COL), dtype=int)

# 消去ドロップがありうるか格納する配列
dummy = np.zeros((ROW, COL), dtype=int)

# 消去ドロップか否か格納する配列
t_erase = np.zeros((ROW, COL), dtype=int)

# スワイプで移動する座標を格納する配列
route = np.full((100, 2), -1, dtype=int)

# スワイプ前の盤面
f_field = np.copy(field)


def show_field():
    for row in field:
        print(" | ".join(map(str, row)))
        print("-" * (COL * 4 - 1))



def fall():
    for i in range(ROW-1, -1, -1):
        for j in range(COL):
            check = i
            while check < ROW-1 and field[check+1, j] == 0:
                field[check+1, j], field[check, j] = field[check, j], 0
                check += 1


def fill_empty_spaces():
    for i in range(ROW):
        for j in range(COL):
            if field[i, j] == 0:
                field[i, j] = rnd(1, 6)


def chain(now_row, now_col, d, count):
    global max_count

    if not (0 <= now_row < ROW and 0 <= now_col < COL):
        return

    if field[now_row, now_col] == d and chainflag[now_row, now_col] == 0:
        chainflag[now_row, now_col] = -1
        max_count = max(max_count, count)
        dummy[now_row, now_col] = -1

        chain(now_row - 1, now_col, d, count + 1)
        chain(now_row + 1, now_col, d, count + 1)
        chain(now_row, now_col - 1, d, count + 1)
        chain(now_row, now_col + 1, d, count + 1)


def evaluate():
    value = 0
    global max_count

    chainflag.fill(0)

    for row in range(ROW):
        for col in range(COL):
            if chainflag[row, col] == 0 and field[row, col] != 0:
                max_count = 0
                dummy.fill(0)
                chain(row, col, field[row, col], 1)
                if max_count >= 3:
                    if check():
                        value += 1

    return value

'''
def sum_evaluate():
    combo = 0

    while True:
        t_erase.fill(0)
        a = evaluate()

        if a == 0:
            break

        for row in range(ROW):
            for col in range(COL):
                if t_erase[row, col] == -1:
                    field[row, col] = 0

        fall()
        fill_empty_spaces()
        combo += a

    return combo
'''

def sum_e():
    combo = 0

    while True:
        t_erase.fill(0)
        a = evaluate()

        if a == 0:
            break

        for row in range(ROW):
            for col in range(COL):
                if t_erase[row, col] == -1:
                    field[row, col] = 0

        fall()
        combo += a

    return combo


def check():
    v = 0

    for row in range(ROW):
        for col in range(COL - 2):
            if dummy[row, col] == -1 and dummy[row, col + 1] == -1 and dummy[row, col + 2] == -1:
                if field[row, col] == field[row, col + 1] == field[row, col + 2]:
                    t_erase[row, col] = t_erase[row, col + 1] = t_erase[row, col + 2] = -1
                    v = 1

    for col in range(COL):
        for row in range(ROW - 2):
            if dummy[row, col] == -1 and dummy[row + 1, col] == -1 and dummy[row + 2, col] == -1:
                if field[row, col] == field[row + 1, col] == field[row + 2, col]:
                    t_erase[row, col] = t_erase[row + 1, col] = t_erase[row + 2, col] = -1
                    v = 1

    return v


def operation():
    now_col, now_row = route[0, 1], route[0, 0]

    for i in range(1, MAX_TURN):
        if route[i, 0] == -1 or route[i, 1] == -1:
            break
        swap(field, now_row, now_col, route[i, 0], route[i, 1])
        now_col, now_row = route[i, 1], route[i, 0]


def swap(matrix, x1, y1, x2, y2):
    matrix[x1, y1], matrix[x2, y2] = matrix[x2, y2], matrix[x1, y1]


def rnd(mini, maxi):
    return random.randint(mini, maxi)


class Member:
    def __init__(self):
        self.movei = np.full((100, 2), -1, dtype=int)
        self.score = 0
        self.nowC = 0
        self.nowR = 0
        self.prev = -1

    def __lt__(self, other):
        return self.score < other.score


class Action:
    def __init__(self):
        self.score = 0
        self.moving = np.full((100, 2), -1, dtype=int)


def BEAM_SEARCH():
    que = []

    for i in range(ROW):
        for j in range(COL):
            cand = Member()
            cand.nowC = j
            cand.nowR = i
            cand.movei[0] = [i, j]
            que.append(cand)

    dx = [-1, 0, 0, 1]
    dy = [0, -1, 1, 0]

    bestAction = Action()
    maxValue = 0

    for i in range(1, MAX_TURN):
        pque = PriorityQueue()

        while que:
            temp = que.pop(0)
            for j in range(4):
                field[:] = f_field
                cand = Member()
                cand.__dict__.update(temp.__dict__)
                if 0 <= cand.nowC + dx[j] < COL and 0 <= cand.nowR + dy[j] < ROW:
                    if cand.prev + j == 3:
                        continue
                    cand.nowC += dx[j]
                    cand.nowR += dy[j]
                    cand.movei[i] = [cand.nowR, cand.nowC]
                    route[:] = cand.movei
                    operation()
                    cand.score = sum_e()
                    cand.prev = j
                    pque.put(cand)

        for j in range(BEAM_WIDTH):
            if pque.empty():
                break
            temp = pque.get()
            if maxValue < temp.score:
                maxValue = temp.score
                bestAction.score = maxValue
                bestAction.moving[:] = temp.movei
            if i < MAX_TURN - 1:
                que.append(temp)

    return bestAction


if __name__ == "__main__":

    fill_empty_spaces()
    show_field()
    f_field[:] = field
    tmp = BEAM_SEARCH()
    route[:] = tmp.moving

    print(f"(x,y)=({route[0][1]},{route[0][0]})")
    for j in range(1, MAX_TURN):
        if route[j][1] == -1 or route[j][0] == -1:
            break
        if route[j][1] == route[j - 1][1] + 1:
            print("RIGHT")
        if route[j][1] == route[j - 1][1] - 1:
            print("LEFT")
        if route[j][0] == route[j - 1][0] + 1:
            print("DOWN")
        if route[j][0] == route[j - 1][0] - 1:
            print("UP")
        print()

    field[:] = f_field
    operation()
    combo = sum_e()
    print(f"{combo}コンボ")


