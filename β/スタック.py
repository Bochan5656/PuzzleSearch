import copy


class Step:
    def __init__(self, FirstField, X, Y):
        self.field = FirstField
        self.X = X
        self.Y = Y
        self.height = len(FirstField)
        self.width = len(FirstField[0])
        self.judge = [[0] * self.width for _ in range(self.height)]
        self.comboN = 0
        self.Route = [[X, Y]]
        self.ElseDrop = 6

    def __repr__(self):
        return str(self.Route)

    def operation(self, direction):
        '''
        ドロップ移動方向
           0
        3     1
           2
        '''
        if direction == 0 and self.Y != 0:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y - 1][self.X]
            self.field[self.Y - 1][self.X] = hoge
            self.Y -= 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 2 and self.Y != self.height - 1:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y + 1][self.X]
            self.field[self.Y + 1][self.X] = hoge
            self.Y += 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 3 and self.X != 0:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y][self.X - 1]
            self.field[self.Y][self.X - 1] = hoge
            self.X -= 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 1 and self.X != self.width - 1:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y][self.X + 1]
            self.field[self.Y][self.X + 1] = hoge
            self.X += 1
            self.Route.append([self.X, self.Y])
            return 1

        return 0

    def disp(self):
        for row in self.field:
            print(row)

    def combo(self):
        self.n = 0
        self.judge = [[0] * self.width for _ in range(self.height)]
        # 横列つながり
        for j in range(self.height):
            for i in range(1, self.width - 1):
                if self.field[j][i] == self.field[j][i - 1] and self.field[j][i] == self.field[j][i + 1]:
                    hoge = max(self.judge[j][i - 1], self.judge[j][i], self.judge[j][i + 1])
                    if hoge != 0:
                        self.judge[j][i - 1] = hoge
                        self.judge[j][i] = hoge
                        self.judge[j][i + 1] = hoge
                    else:
                        self.n += 1
                        self.judge[j][i - 1] = self.n
                        self.judge[j][i] = self.n
                        self.judge[j][i + 1] = self.n

        # 縦列つながり
        for j in range(1, self.height - 1):
            for i in range(self.width):
                if self.field[j][i] == self.field[j - 1][i] and self.field[j][i] == self.field[j + 1][i]:
                    hoge = max(self.judge[j - 1][i], self.judge[j][i], self.judge[j + 1][i])
                    if hoge != 0:
                        self.judge[j - 1][i] = hoge
                        self.judge[j][i] = hoge
                        self.judge[j + 1][i] = hoge
                    else:
                        self.n += 1
                        self.judge[j - 1][i] = self.n
                        self.judge[j][i] = self.n
                        self.judge[j + 1][i] = self.n

        self.comboN += self.n

    def fall(self):
        for j in range(self.height):
            for i in range(self.width):
                if self.judge[j][i] != 0:
                    k = j
                    while k > 0:
                        self.field[k][i] = self.field[k - 1][i]
                        k -= 1
                    self.field[0][i] = self.ElseDrop
                    self.ElseDrop += 1


# 初期フィールドの設定（例として4x3のフィールド）
firstField = [
    [0, 1, 2, 3],
    [1, 2, 3, 0],
    [2, 3, 0, 1]
]

# 最良のコンボ数とそのルートを保存する変数
best_comboN = 0
best_route = []
MAX_DEPTH = 10  # 再帰の最大深さを設定


# 再帰的に全探索を行う関数
def recursive_search(step, depth):
    global best_comboN, best_route

    # 深さ制限を確認
    if depth >= MAX_DEPTH:
        return

    # 現在の状態でコンボ数を計算
    m = 0
    while True:
        step.combo()
        if step.comboN == m:
            break
        m = step.comboN
        step.fall()

    # 最良のコンボ数を更新
    if step.comboN > best_comboN:
        best_comboN = step.comboN
        best_route = step.Route

    # 4方向への移動を試みる
    for direction in range(4):
        new_step = copy.deepcopy(step)
        if new_step.operation(direction) != 0:
            recursive_search(new_step, depth + 1)


# 初期位置からスタートして全探索を開始
for j in range(len(firstField)):
    for i in range(len(firstField[0])):
        initial_step = Step(copy.deepcopy(firstField), i, j)
        recursive_search(initial_step, 0)

# 最良値を出力
print("最良のコンボ数:", best_comboN)
print("最良のルート:", best_route)
