# -*- coding: UTF-8 -*-
import numpy as np
import Tkinter as tk
#from Tkinter import ttk
import ttk
from Tkinter import *
import threading
import time
import random
import copy
import Demo
# import VirtualCar


class sillycar:
    # 下左上右 -> 下左上右 的动作
    table = [
        [0, 2, 3, 1],
        [1, 0, 2, 3],
        [3, 1, 0, 2],
        [2, 3, 1, 0]
    ]

    action = ["直走", "左转", "右转", "后退"]

    # 整个画布的长、宽，哪个点是可以走的，[(x,y,info), ...]
    def __init__(self, length, width, list_of_tuples, now, orientation):
        self.length = length
        self.width = width
        self.Map = np.zeros((length, width), dtype='int32')
        self.pos2info = dict()
        self.info2pos = dict()
        for i in range(len(list_of_tuples)):
            self.Map[list_of_tuples[i][0]][list_of_tuples[i][1]] = i + 1
            self.pos2info[i + 1] = list_of_tuples[i][2]
            self.info2pos[list_of_tuples[i][2]] = (list_of_tuples[i][0], list_of_tuples[i][1])
        # 上一个位置
        self.pre = -1
        # 当前位置
        self.now = now
        # 目标位置
        self.target = -1
        # 开始一次寻路后已经走过的位置 用来画已经走过的路
        self.pres = []
        # 当前朝向
        self.orientation = orientation

    # 更新现在的位置 获得下一个位置和动作
    def updatePosition(self, newposition):
        if self.now != newposition:
            bestway = self.dfs(self.now, newposition)
            temp = []
            for i in range(len(bestway)):
                temp.append(self.pos2info[self.Map[bestway[i][0]][bestway[i][1]]])
            self.pre = temp[-2]
            #print("pre:",self.pre)
            self.now = newposition
            self.pres.extend(temp[:-1])
            self.orientation = self.getOrientation()
        if self.target == -1:
            return -1, -1
        if self.now == self.target:
            return -1, -1
        bestway = self.dfs(self.now, self.target)
        nextpoint = self.pos2info[self.Map[bestway[1][0]][bestway[1][1]]]
        nextaction = self.table[bestway[0][2]][bestway[1][2]]
        print(nextpoint, nextaction)
        return nextpoint, nextaction

    # 获得小车当前朝向
    def getOrientation(self):
        if self.pre == -1 or self.now == -1:
            return 0
        prex, prey = self.info2pos[self.pre]
        nowx, nowy = self.info2pos[self.now]
        nowx -= prex
        nowy -= prey
        if nowx == 0:
            if nowy == 1:
                return 3
            else:
                return 1
        elif nowx == -1:
            return 2
        else:
            return 0

    def getOrientation2(self, pre, now):
        if pre == -1 or now == -1:
            return 0
        prex, prey = self.info2pos[pre]
        nowx, nowy = self.info2pos[now]
        nowx -= prex
        nowy -= prey
        if nowx == 0:
            if nowy == 1:
                return 3
            else:
                return 1
        elif nowx == -1:
            return 2
        else:
            return 0

    def dfs(self, start, end):
        visited = self.Map.copy()
        direction = [(1, 0), (0, -1), (-1, 0), (0, 1)]  # 下 左 上 右
        xs, ys = self.info2pos[start]
        xe, ye = self.info2pos[end]

        bestway = []
        currentway = []
        bestcnt = 999999
        lastd = -1

        currentway.append([xs, ys, self.orientation, 0])
        # print(self.getOrientation())
        visited[xs][ys] = 0
        while len(currentway) > 0:
            # x,y,从哪个方向来，扩展到了哪个方向
            xs, ys, df, dt = currentway[-1]
            # print(xs,ys,df, dt)

            if xs == xe and ys == ye:
                currentcnt = 0
                for j in range(1, len(currentway)):
                    if currentway[j][2] != currentway[j - 1][2]:
                        currentcnt += 1
                if currentcnt < bestcnt or (currentcnt == bestcnt and len(currentway) < len(bestway)):
                    bestcnt = currentcnt
                    # bestway = currentway.copy()
                    bestway = copy.copy(currentway)
                visited[xs][ys] = 1
                currentway.pop()
                continue

            flag = True
            for i in range(dt, 4):
                tempx = xs + direction[i][0]
                tempy = ys + direction[i][1]
                if 0 <= tempx < self.length and 0 <= tempy < self.width and visited[tempx][tempy] != 0:
                    currentway[-1][3] = i + 1
                    currentway.append([tempx, tempy, i, 0])
                    visited[tempx][tempy] = 0
                    flag = False
                    break
            if flag:  # 四个方向都不能走
                visited[xs][ys] = 1
                currentway.pop()

        return bestway

    def findway(self):
        bestway = self.dfs(self.now, self.target)
        result = []
        for i in range(len(bestway)):
            result.append(self.pos2info[self.Map[bestway[i][0]][bestway[i][1]]])
        return result


class uglyUI:
    buttons = []
    canvases = dict()

    def __init__(self, stupidcar):
        self.stupidcar = stupidcar

        # 界面
        root = tk.Tk()
        root.title("stupid car")
        frame1 = ttk.Frame(root, padding="3 3 12 12")
        frame1.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # 添加按钮和线
        temp = stupidcar.Map
        for i in range(2 * stupidcar.length - 1):
            if i % 2 == 0:
                for j in range(2 * stupidcar.width - 1):
                    if j % 2 == 0:
                        if temp[i // 2][j // 2] != 0:
                            b = tk.Button(frame1, text=str(int(temp[i // 2][j // 2])), width=2, bg='white')
                            b.bind("<Button-1>", func=self.press)
                            b.grid(row=i, column=j)
                            self.buttons.append(b)
                    else:
                        if temp[i // 2][(j - 1) // 2] != 0 and temp[i // 2][(j + 1) // 2] != 0:
                            cv = Canvas(frame1, width=30, height=30)
                            cv.create_line(0, 15, 30, 15, tags='line')
                            cv.grid(row=i, column=j)
                            self.canvases[str(temp[i // 2][(j - 1) // 2]) + 'to' + str(temp[i // 2][(j + 1) // 2])] = cv
                            self.canvases[str(temp[i // 2][(j + 1) // 2]) + 'to' + str(temp[i // 2][(j - 1) // 2])] = cv
            else:
                for j in range(2 * stupidcar.width - 1):
                    if j % 2 == 0 and temp[(i - 1) // 2][j // 2] != 0 and temp[(i + 1) // 2][j // 2] != 0:
                        cv = Canvas(frame1, width=30, height=30)
                        cv.create_line(15, 0, 15, 30, tags='line')
                        cv.grid(row=i, column=j)
                        self.canvases[str(temp[(i - 1) // 2][j // 2]) + 'to' + str(temp[(i + 1) // 2][j // 2])] = cv
                        self.canvases[str(temp[(i + 1) // 2][j // 2]) + 'to' + str(temp[(i - 1) // 2][j // 2])] = cv

        self.newTravel()
        #t = threading.Thread(target=VirtualCar, args=(self,), name="thread-refresh")
        t = threading.Thread(target=Demo.run, args=(self,), name="thread-car")
        t.setDaemon(True)
        t.start()

        root.mainloop()

    # 每一次新征程之前调用一次
    def newTravel(self):
        self.stupidcar.pres = []
        self.stupidcar.target = -1
        for b in self.buttons:
            b['bg'] = "white"
        self.buttons[stupidcar.now - 1]['bg'] = 'yellow'
        for cv in self.canvases.values():
            cv.delete("triangle")

    def addArrow(self, f, t):
        if f == t:
            return
        o = self.stupidcar.getOrientation2(f, t)
        cv = self.canvases[str(f) + 'to' + str(t)]
        if o == 0:
            cv.create_polygon(15, 30, 10, 25, 20, 25, tags='triangle')
        elif o == 1:
            cv.create_polygon(2, 15, 7, 10, 7, 20, tags='triangle')
        elif o == 2:
            cv.create_polygon(15, 2, 10, 7, 20, 7, tags='triangle')
        else:
            cv.create_polygon(25, 10, 25, 20, 30, 15, tags='triangle')

    def clear(self):
        for b in self.buttons:
            b['bg'] = 'white'
        for cv in self.canvases.values():
            cv.delete("triangle")

    def repaint(self):
        # pres = self.stupidcar.pres.copy()
        pres = copy.copy(self.stupidcar.pres)
        pres.append(self.stupidcar.now)
        #print(pres)
        route = self.stupidcar.findway()
        self.buttons[pres[0] - 1]['bg'] = 'pink'
        for i in range(1, len(pres)):
            self.buttons[pres[i] - 1]['bg'] = 'gray'
            self.addArrow(pres[i - 1], pres[i])
        for i in range(len(route)):
            num = route[i]
            if i == 0:
                self.buttons[num - 1]['bg'] = 'yellow'
                self.addArrow(num, route[i + 1])
            # print(num)
            elif i == len(route) - 1:
                self.buttons[num - 1]['bg'] = 'red'
            else:
                self.buttons[num - 1]['bg'] = 'orange'
                self.addArrow(num, route[i + 1])

    def press(self, event):
        self.clear()
        target = int(event.widget['text'])
        self.stupidcar.target = target
        self.repaint()

    def updatePosition(self, newposition):
        nextposition, nextaction = self.stupidcar.updatePosition(newposition)
        if self.stupidcar.target != -1 and self.stupidcar.now != self.stupidcar.target:
            self.clear()
            self.repaint()
        else:
            self.newTravel()
        return nextposition, nextaction+1

    def threadmove(self):
        fakemove = [2, 3, 4, 5, 6, 7, 16, 21, 26, 35, 36, 37, 38, 27, 22, 17, 10, 11]
        it = iter(fakemove)
        while True:
            time.sleep(3)
            # print("here")
            if random.randint(0, 1) == 0:
                #print("move")
                self.updatePosition(next(it))


# def VirtualCar(UI):
#     fakemove = [2, 3, 4, 15]
#     it = iter(fakemove)
#     while True:
#         time.sleep(3)
#         try:
#             print(UI.updatePosition(next(it)))
#         except:
#             break


grids = [
    (0,0,1),(0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,6),(0,6,7),(0,7,8),(0,8,9),(0,9,10),(0,10,11),(0,11,12),(0,12,13),
    (1,0,14),(1,3,15),(1,6,16),(1,9,17),(1,12,18),
    (2,0,19),(2,3,20),(2,6,21),(2,9,22),(2,12,23),
    (3,0,24),(3,3,25),(3,6,26),(3,9,27),(3,12,28),
    (4,0,29),(4,1,30),(4,2,31),(4,3,32),(4,4,33),(4,5,34),(4,6,35),(4,7,36),(4,8,37),(4,9,38),(4,10,39),(4,11,40),(4,12,41)
]
stupidcar = sillycar(5,13,grids,1,3)
uglyui = uglyUI(stupidcar)

