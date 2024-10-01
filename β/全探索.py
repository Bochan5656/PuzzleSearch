'''
配置変数　field[x][y]
左上　0

赤0
青1
緑2
黄3
紫4
回復5
落ちコン6以降
トスル


インスタンスをどんどん増やす形でいいかな？

クラス関数-------------------
移動によってどう配置が変化するか
ドロップ消去、コンボ数評価関数
落ちコン関数
状態グラフィック表示関数
'''
import copy

class Step:
    def __init__(self, FirstField, X, Y):
        self.field = FirstField
        self.X = X
        self.Y = Y
        self.height = len(FirstField)  # フィールドの高さを取得
        self.width = len(FirstField[0])  # フィールドの幅を取得
        self.judge = [[0]*self.width for _ in range(self.height)]
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
            self.field[self.Y][self.X] = self.field[self.Y-1][self.X]
            self.field[self.Y-1][self.X] = hoge
            self.Y -= 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 2 and self.Y != self.height - 1:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y+1][self.X]
            self.field[self.Y+1][self.X] = hoge
            self.Y += 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 3 and self.X != 0:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y][self.X-1]
            self.field[self.Y][self.X-1] = hoge
            self.X -= 1
            self.Route.append([self.X, self.Y])
            return 1

        if direction == 1 and self.X != self.width - 1:
            hoge = self.field[self.Y][self.X]
            self.field[self.Y][self.X] = self.field[self.Y][self.X+1]
            self.field[self.Y][self.X+1] = hoge
            self.X += 1
            self.Route.append([self.X, self.Y])
            return 1

        return 0

    def disp(self):
        for row in self.field:
            print(row)

    def combo(self):
        self.n = 0
        self.judge = [[0]*self.width for _ in range(self.height)]
        # 横列つながり
        for j in range(self.height):
            for i in range(1, self.width-1):
                if self.field[j][i] == self.field[j][i-1] and self.field[j][i] == self.field[j][i+1]:
                    hoge = max(self.judge[j][i-1], self.judge[j][i], self.judge[j][i+1])
                    if hoge != 0:
                        self.judge[j][i-1] = hoge
                        self.judge[j][i] = hoge
                        self.judge[j][i+1] = hoge
                    else:
                        self.n += 1
                        self.judge[j][i-1] = self.n
                        self.judge[j][i] = self.n
                        self.judge[j][i+1] = self.n

        # 縦列つながり
        for j in range(1, self.height-1):
            for i in range(self.width):
                if self.field[j][i] == self.field[j-1][i] and self.field[j][i] == self.field[j+1][i]:
                    hoge = max(self.judge[j-1][i], self.judge[j][i], self.judge[j+1][i])
                    if hoge != 0:
                        self.judge[j-1][i] = hoge
                        self.judge[j][i] = hoge
                        self.judge[j+1][i] = hoge
                    else:
                        self.n += 1
                        self.judge[j-1][i] = self.n
                        self.judge[j][i] = self.n
                        self.judge[j+1][i] = self.n

        self.comboN += self.n

    def fall(self):
        for j in range(self.height):
            for i in range(self.width):
                if self.judge[j][i] != 0:
                    k = j
                    while k > 0:
                        self.field[k][i] = self.field[k-1][i]
                        k -= 1
                    self.field[0][i] = self.ElseDrop
                    self.ElseDrop += 1

# 初期フィールドの設定（例として4x3のフィールド）
firstField = [
    [0, 1, 2, 3],
    [1, 2, 3, 0],
    [2, 3, 0, 1]
]

print('初期配置')
for i in firstField:
    print(i)

height = len(firstField)
width = len(firstField[0])

Allway = []
NextStep = []  # 次のステップで動作させるインスタンスのインデックス

for j in range(height):
    for i in range(width):
        Allway.append(copy.deepcopy(Step(firstField, i, j)))
        Allway[-1].combo()
        Allway[-1].fall()
        NextStep.append(i + j * width)

# 動作させた場合を増やしていく
for loop in range(10):
    f = len(NextStep)
    for k in range(f):
        for m in range(4):
            Allway.append(copy.deepcopy(Allway[NextStep[k]]))  # 追加
            end = len(Allway) - 1  # 追加したインスタンスに対し操作する
            hoge = Allway[end].operation(m)
            if hoge != 0:
                NextStep.append(end)  # 新しく発生したものをNextStepに追加する
            else:  # 移動しなかった場合削除する
                del Allway[end]
    del NextStep[0:f]

# 生成したインスタンスに対し、コンボ判定、落ちコンを計算
for k in range(len(Allway)):
    m = 0
    while True:
        Allway[k].combo()
        if Allway[k].comboN == m:
            break
        m = Allway[k].comboN
        Allway[k].fall()

# 最良値を出力
hogeMax = Allway[0].comboN
maxIndex = 0
for a in range(len(Allway)):
    if hogeMax < Allway[a].comboN:
        hogeMax = Allway[a].comboN
        maxIndex = a

print(maxIndex)
print(hogeMax)
print(Allway[maxIndex].Route)
