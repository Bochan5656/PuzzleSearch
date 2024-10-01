import copy
import queue

import numpy as np

from 幅優先探索 import Candidate, sum_e

ROW = 5
COL = 6
MAX_TURN = 40
BEAM_WIDTH = 5000

# 盤面
field = [[0] * COL for _ in range(ROW)]
f_field = [[0] * COL for _ in range(ROW)]
route = [[-1, -1] for _ in range(100)]
max_count = 0
chainflag = [[0] * COL for _ in range(ROW)]
dummy = [[0] * COL for _ in range(ROW)]
t_erase = [[0] * COL for _ in range(ROW)]


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
    for i in range(ROW):
        for j in range(COL):
            print(field[i][j], end=' ')
        print()
    print()


def fall():
    for i in range(ROW - 1, -1, -1):
        for j in range(COL):
            check = i
            while True:
                if check == ROW - 1:
                    break
                if field[check + 1][j] == 0:
                    field[check + 1][j] = field[check][j]
                    field[check][j] = 0
                check += 1


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
    global max_count
    value = 0
    for row in range(ROW):
        for col in range(COL):
            if chainflag[row][col] == 0 and field[row][col] != 0:
                max_count = 0
                for i in range(ROW):
                    for j in range(COL):
                        dummy[i][j] = 0
                chain(row, col, field[row][col], 1)
                if max_count >= 3:
                    if check() == 1:
                        value += 1
    return value


def sum_evaluate():
    combo = 0
    while True:
        for i in range(ROW):
            for j in range(COL):
                t_erase[i][j] = 0

        a = evaluate()

        if a == 0:
            break

        for row in range(ROW):
            for col in range(COL):
                if t_erase[row][col] == -1:
                    field[row][col] = 0

        fall()
        combo += a

    return combo


def check():
    v = 0
    for row in range(ROW):
        for col in range(COL - 2):
            if dummy[row][col] == -1 and dummy[row][col + 1] == -1 and dummy[row][col + 2] == -1 and field[row][col] == field[row][col + 1] and field[row][col] == field[row][col + 2]:
                t_erase[row][col] = -1
                t_erase[row][col + 1] = -1
                t_erase[row][col + 2] = -1
                v = 1

    for col in range(COL):
        for row in range(ROW - 2):
            if dummy[row][col] == -1 and dummy[row + 1][col] == -1 and dummy[row + 2][col] == -1 and field[row][col] == field[row + 1][col] and field[row][col] == field[row + 2][col]:
                t_erase[row][col] = -1
                t_erase[row + 1][col] = -1
                t_erase[row + 2][col] = -1
                v = 1

    return v


def operation():
    now_col = route[0][1]
    now_row = route[0][0]
    for i in range(1, MAX_TURN):
        if route[i][0] == -1 or route[i][1] == -1:
            break
        field[now_row][now_col], field[route[i][0]][route[i][1]] = field[route[i][0]][route[i][1]], field[now_row][now_col]
        now_col = route[i][1]
        now_row = route[i][0]


def BEAM_SEARCH():
    global field, f_field
    que = queue.Queue()
    for i in range(ROW):
        for j in range(COL):
            movei = np.full((MAX_TURN, 2), -1)
            movei[0] = [i, j]
            cand = Candidate(movei, 0, j, i, -1)
            que.put(cand)
    dx = [-1, 0, 0, 1]
    dy = [0, -1, 1, 0]
    best_action = Candidate(np.full((MAX_TURN, 2), -1), 0, 0, 0, -1)
    max_value = 0
    for i in range(1, MAX_TURN):
        pque = queue.PriorityQueue()
        while not que.empty():
            temp = que.get()
            for j in range(4):
                field = f_field.copy()
                cand = Candidate(temp.movei.copy(), temp.score, temp.nowC, temp.nowR, temp.prev)
                if 0 <= cand.nowC + dx[j] < COL and 0 <= cand.nowR + dy[j] < ROW:
                    if cand.prev + j == 3:
                        continue
                    cand.nowC += dx[j]
                    cand.nowR += dy[j]
                    cand.movei[i] = [cand.nowR, cand.nowC]
                    route = cand.movei.copy()
                    operation(route)
                    cand.score = sum_e()

                    # デバッグ用プリント
                    print(f"Route: {route}")
                    print(f"Score: {cand.score}")

                    cand.prev = j
                    pque.put(cand)
        for _ in range(BEAM_WIDTH):
            if pque.empty():
                break
            temp = pque.get()
            if max_value < temp.score:
                max_value = temp.score
                best_action = temp
            if i < MAX_TURN - 1:
                que.put(temp)
    return best_action



def main():
    global t_erase
    t_erase = [[0] * COL for _ in range(ROW)]

    # ここで手動で盤面を設定
    field[0] = [1, 2, 3, 4, 5, 6]
    field[1] = [2, 3, 4, 5, 6, 1]
    field[2] = [3, 4, 5, 6, 1, 2]
    field[3] = [4, 5, 6, 1, 2, 3]
    field[4] = [5, 6, 1, 2, 3, 4]

    show_field()
    for r in range(ROW):
        for c in range(COL):
            f_field[r][c] = field[r][c]
    tmp = BEAM_SEARCH()
    for k in range(100):
        route[k][0] = tmp.moving[k][0]
        route[k][1] = tmp.moving[k][1]
    print(f"(x,y)=({route[0][0] + 1},{route[0][1] + 1})")
    operation()
    t_score = sum_evaluate()
    print(f"スコア: {t_score}")


if __name__ == "__main__":
    main()
