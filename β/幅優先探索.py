import random
import numpy as np
import queue

ROW = 5  # 縦
COL = 6  # 横
MAX_TURN = 40  # 最大40手
BEAM_WIDTH = 5000  # ビーム幅

# 初期配置生成関数
def init():
    global field
    field = np.random.randint(0, 7, size=(ROW, COL))

# ドロップの落下処理関数
def fall():
    global field
    for j in range(COL):
        for i in range(ROW-2, -1, -1):
            if field[i, j] != 0:
                for k in range(i, ROW-1):
                    if field[k+1, j] == 0:
                        field[k+1, j], field[k, j] = field[k, j], field[k+1, j]
                    else:
                        break

# 空マスを埋める関数
def set_field():
    global field
    for i in range(ROW):
        for j in range(COL):
            if field[i, j] == 0:
                field[i, j] = random.randint(1, 6)

# 盤面表示関数
def show_field():
    global field
    for i in range(ROW):
        print(" ".join(map(str, field[i])))

# 連結ドロップ数をカウントする関数
def chain(now_row, now_col, d, count):
    global field, chainflag, max_count, dummy
    if now_row < 0 or now_row >= ROW or now_col < 0 or now_col >= COL:
        return
    if field[now_row, now_col] == d and chainflag[now_row, now_col] == 0:
        chainflag[now_row, now_col] = -1
        if max_count < count:
            max_count = count
        dummy[now_row, now_col] = -1
        chain(now_row - 1, now_col, d, count + 1)
        chain(now_row + 1, now_col, d, count + 1)
        chain(now_row, now_col - 1, d, count + 1)
        chain(now_row, now_col + 1, d, count + 1)

# コンボ数判定関数
def evaluate():
    global field, chainflag, dummy, max_count
    value = 0
    chainflag.fill(0)
    for row in range(ROW):
        for col in range(COL):
            if chainflag[row, col] == 0 and field[row, col] != 0:
                max_count = 0
                dummy.fill(0)
                chain(row, col, field[row, col], 1)
                if max_count >= 3 and check():
                    value += 1
    return value

# 落としも落ちコンも考慮したコンボ数判定関数
def sum_evaluate():
    global field, t_erase
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
        set_field()
        combo += a
    return combo

# 落としを考慮して、落ちコンを考慮しないコンボ数判定関数
def sum_e():
    global field, t_erase
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

# 最終的にコンボが発生したか、さらにどのドロップが消えるのか判定する関数
def check():
    global dummy, t_erase, field
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

# スワイプ処理関数
def operation(route):
    global field
    now_col, now_row = route[0]
    for i in range(1, MAX_TURN):
        if route[i][0] == -1 or route[i][1] == -1:
            break
        # インデックスの範囲チェック
        if 0 <= now_row < ROW and 0 <= now_col < COL and 0 <= route[i][0] < ROW and 0 <= route[i][1] < COL:
            field[now_row, now_col], field[route[i][0], route[i][1]] = field[route[i][0], route[i][1]], field[now_row, now_col]
            now_col, now_row = route[i][1], route[i][0]
        else:
            print(f"Error: Invalid index (now_row, now_col)=({now_row},{now_col}), (route[{i}][0], route[{i}][1])=({route[i][0]},{route[i][1]})")
            break



class Candidate:
    def __init__(self, movei, score, nowC, nowR, prev):
        self.movei = movei
        self.score = score
        self.nowC = nowC
        self.nowR = nowR
        self.prev = prev

    def __lt__(self, other):
        return self.score > other.score  # Reverse order for max-heap behavior in PriorityQueue

# ルート探索関数
def beam_search():
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
    global field, f_field, chainflag, dummy, t_erase
    chainflag = np.zeros((ROW, COL), dtype=int)
    dummy = np.zeros((ROW, COL), dtype=int)
    t_erase = np.zeros((ROW, COL), dtype=int)
    avg = 0.0
    for _ in range(1000):
        init()
        set_field()
        show_field()
        f_field = field.copy()
        best_action = beam_search()
        route = best_action.movei
        print(f"(x,y)=({route[0][1]},{route[0][0]})")
        for j in range(1, MAX_TURN):
            if route[j][1] == -1 or route[j][0] == -1:
                break
            print("UDLR"[best_action.prev], end="")
            if j % 5 == 0:
                print()
        print()
        if best_action.score == 0:
            print("UP")
        print(best_action.score)
        avg += best_action.score
        print(f"average = {avg / (_ + 1)}")

if __name__ == "__main__":
    main()
