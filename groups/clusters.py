#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from math import sqrt
from PIL import Image,ImageDraw
import random

def readfile(filename):
    lines = [line for line in file(filename)]

    # 最初の行は列タイトル
    colnames = lines[0].strip().split('\t')[1:]
    rownames = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # それぞれの行の最初の列は行の名前
        rownames.append(p[0])
        # 行の残りの部分がその行のデータ
        data.append([float(x) for x in p[1:]])
    return rownames, colnames, data

# 距離計算
def pearson(v1, v2):
    # 単純な合計
    sum1 = sum(v1)
    sum2 = sum(v2)

    # 平方の合計
    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])
    
    # 積の合計
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    # ピアソンによるスコアを算出
    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
    if den == 0 : return 0

    return 1.0 - num / den

# クラスタ型
class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1

    # クラスタたちは最初の行たち
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # すべての組をループし、もっとも距離の近い組を探す
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                # 距離をキャッシュしてあればそれを使う
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # 2つのクラスタの平均を計算する
        mergevec = [
                (clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
                for i in range(len(clust[0].vec))]

        # 新たなクラスタを作る
        newcluster = bicluster(mergevec, left = clust[lowestpair[0]],
                right = clust[lowestpair[1]],
                distance = closest, id = currentclustid)

        # もとのセットではないクラスタのIDは負にする
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]


def printclust(clust,labels=None,n=0):
    # 階層型のレイアウトにするためにインデントする
    for i in range(n): print ' ',
    if clust.id < 0:
        # 負のidはこれが枝であることを示している
        print '-'
    else:
        # 正のidはこれが終盤だということを示している
        if labels==None: print clust.id
        else: print labels[clust.id]
    
    # 右と左の枝を表示する
    if clust.left != None: printclust(clust.left,labels=labels,n=n+1)
    if clust.right != None: printclust(clust.right,labels=labels,n=n+1)


def getheight(clust):
    # 終端であれば高さは1にする
    if clust.left == None and clust.right == None: return 1
    
    # そうでなければ高さはそれぞれの枝の高さの合計
    return getheight(clust.left) + getheight(clust.right)


def getdepth(clust):
    # 終端への距離は0.0
    if clust.left == None and clust.right == None: return 0

    # 枝の距離は2つの方向の大きい方にそれ自身の距離を足したもの
    return max(getdepth(clust.left),getdepth(clust.right)) + clust.distance


def drawdendrogram(clust,labels,jpeg='clusters.jpg'):
    # 高さと幅
    h=getheight(clust)*20
    w=1200
    depth=getdepth(clust)

    # 幅は固定されているため、適宜縮尺する
    scaling=float(w-150)/depth

    # 白を背景とする新しい画像を作る
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))    

    # 最初のノードを描く
    drawnode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')


def drawnode(draw,clust,x,y,scaling,labels):
    if clust.id<0:
        h1=getheight(clust.left)*20
        h2=getheight(clust.right)*20
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        # 直線の長さ
        ll=clust.distance*scaling
        # クラスタから子への垂直な直線
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))    
        
        # 左側のアイテムへの水平な直線
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=(255,0,0))    

        # 右側のアイテムへの水平な直線
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=(255,0,0))        

        # 左右のノードたちを描く関数を呼び出す
        drawnode(draw,clust.left,x+ll,top+h1/2,scaling,labels)
        drawnode(draw,clust.right,x+ll,bottom-h2/2,scaling,labels)
    else:   
        # 終点であればアイテムのラベルを描く
        draw.text((x+5,y-7),labels[clust.id],(0,0,0))


def rotatematrix(data):
    newdata=[]
    for i in range(len(data[0])):
        newrow=[data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata


def kcluster(rows,distance=pearson,k=4):
    # それぞれのポイントの最小値と最大値を決める
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) 
    for i in range(len(rows[0]))]

    # 重心をランダムにk個配置する
    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] 
    for i in range(len(rows[0]))] for j in range(k)]
  
    lastmatches = None

    for t in range(100):
        print 'Iteration %d' % t
        bestmatches = [[] for i in range(k)]
    
        # それぞれの行に対して、最も近い重心を探しだす
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d=distance(clusters[i],row)
                if d < distance(clusters[bestmatch],row): bestmatch = i
            bestmatches[bestmatch].append(j)

        print bestmatches
        # 結果が前回と同じであれば終了
        if bestmatches == lastmatches: break
        lastmatches = bestmatches
        
        # 重心をそのメンバーの平均に移動する
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
                clusters[i]=avgs
      
    return bestmatches


def tanimoto(v1,v2):
    c1, c2, shr = 0, 0, 0

    for i in range(len(v1)):
        if v1[i] != 0: c1 += 1 # v1に存在
        if v2[i] != 0: c2 += 1 # v2に存在
        if v1[i] != 0 and v2[i] != 0: shr += 1 # 両者に存在
  
    return 1.0 - (float(shr)/(c1+c2-shr))


def scaledown(data, distance=pearson, rate=0.01):
    n = len(data)

    # アイテムのすべての組の実際の距離
    realdist = [[distance(data[i],data[j]) for j in range(n)] 
            for i in range(0,n)]

    # 2次元上にランダムに配置するように初期化する
    loc = [[random.random(),random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]
    
    lasterror = None
    for m in range(0,1000):
        # 予測距離を測る
        for i in range(n):
            for j in range(n):
                fakedist[i][j] = sqrt(sum([pow(loc[i][x]-loc[j][x],2) 
                        for x in range(len(loc[i]))]))
  
        # ポイントの移動
        grad = [[0.0,0.0] for i in range(n)]
    
        totalerror = 0
        for k in range(n):
            for j in range(n):
                if j == k: continue
                # 誤差は距離の差の百分率
                errorterm = (fakedist[j][k]-realdist[j][k])/realdist[j][k]
                
                # 他のポイントへの誤差に比例してそれぞれのポイントを
                # 近づけたり遠ざけたりする必要がある
                grad[k][0] += ((loc[k][0]-loc[j][0])/fakedist[j][k]) * errorterm
                grad[k][1] += ((loc[k][1]-loc[j][1])/fakedist[j][k]) * errorterm

                # 誤差の合計を記録
                totalerror += abs(errorterm)
        print totalerror

        # ポイントを移動することで誤差が悪化したら終了
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror
    
        # 学習率と傾斜を掛けあわせてそれぞれのポイントを移動
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    return loc


def draw2d(data, labels, jpeg='mds2d.jpg'):
    img = Image.new('RGB',(2000,2000),(255,255,255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0]+0.5) * 1000
        y = (data[i][1]+0.5) * 1000
        draw.text((x,y),labels[i],(0,0,0))
    img.save(jpeg,'JPEG')  

