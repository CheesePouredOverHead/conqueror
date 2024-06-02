import gym as gym
from gym import spaces
# from collections import deque
from stack import Stack,Pile
from ui import Play
# from generate import generate
import random
import numpy as np
from PyQt6.QtWidgets import QApplication
import sys
from card import Card

def all_card(pile):
    n = pile.setting 

    lst = []
    for i in range(10):
    # 为每个数生成一个随机的出现次数（是3的倍数）
        count = max(1, random.randint((n // 3 // 10) - 1, (n // 3 // 10) + 1)) * 3
    # 将这个数添加到列表中
        lst += [i] * count

    # 如果生成的列表的元素个数超过了 n，我们需要删除一些元素
    while len(lst)!=n:
        if len(lst) > n:
            lst = lst[:n]
        else:
            lst=lst+lst[:n-len(lst)]
    # print(lst)
    # 打乱列表的顺序
    random.shuffle(lst)
    return lst

class SheepEnv(gym.Env):
    """
    SheepEnv 是一个继承自 gym.Env 的环境类，用于实现羊消除游戏的环境。

    Args:
        floor (int): 羊堆的层数。

    Attributes:
        stack (Stack): 栈对象，用于存放已消除的羊。
        pile (Pile): 堆对象，用于存放未消除的羊。
        app (QApplication): Qt 应用程序对象。
        play (Play): 游戏界面对象。
        done (bool): 表示游戏是否结束的标志。
        relation (np.ndarray): 羊之间的关系矩阵。
        movable_cards (np.ndarray): 可移动的羊的标志数组。
        card_num (np.ndarray): 羊的编号数组。
        stack_positions (np.ndarray): 栈中羊的位置信息数组。
        action_space (gym.spaces.Discrete): 行动空间。
        observation_space (gym.spaces.Dict): 观察空间。

    """
    def __init__(self,floor):
            """
            初始化SheepEnv类的实例。

            参数：
            - floor：整数，表示层数。

            属性：
            - stack：Stack类的实例，表示堆栈。
            - pile：Pile类的实例，表示牌堆。
            - app：QApplication类的实例，表示应用程序。
            - play：Play类的实例，表示游戏界面。
            - done：布尔值，表示游戏是否结束。
            - relation：二维数组，表示牌之间的关系。
            - movable_cards：一维数组，表示可移动的牌。
            - card_num：二维数组，表示每张牌的编号。
            - stack_positions：一维数组，表示堆栈中的位置信息。
            - action_space：Discrete类的实例，表示动作空间。
            - observation_space：Dict类的实例，表示观察空间。
            """
            super(SheepEnv, self).__init__()
            self.stack=Stack(7)
            self.pile=Pile()
            self.app= QApplication(sys.argv)
            self.play=Play(self.app)
            self.done=False
            
            # 设置牌堆的属性
            self.pile.setting=18*floor
            self.pile.floor=floor
            self.pile.cardnumber=[18 for x in range(self.pile.floor)]
            
            # 创建牌堆中的牌
            cards=all_card(self.pile)
            for floor in range(self.pile.floor,0,-1):
                if floor%2==1:
                    this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
                else:
                    this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
                random.shuffle(this_floor)
                for i in range(self.pile.cardnumber[floor-1]):
                    self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))

            self.relation=np.zeros((180,180),dtype=np.float64)

            # 计算牌之间的关系
            for i in range(len(self.pile.lst)):
                rect=self.pile.lst[i].btn.geometry()
                for j in range(len(self.pile.lst)):
                    if self.pile.lst[j].floor<self.pile.lst[i].floor:
                        rect1=self.pile.lst[j].btn.geometry()
                        if rect.intersects(rect1):
                            self.relation[i][j]=-1
                            self.relation[j][i]=1
                            self.pile.lst[i].up.append(self.pile.lst[j])
                            self.pile.lst[j].below.append(self.pile.lst[i])
                            continue
                    self.relation[i][j]=0
                    self.relation[j][i]=0

            self.movable_cards = np.ones(180, dtype=np.float64)
            for i, card in enumerate(self.pile.lst):
                if not card.up:
                    self.movable_cards[i] = 1
                else:
                    self.movable_cards[i] = 0
            for i in range(self.pile.inside,180):
                self.movable_cards[i] = 0

            self.card_num=np.zeros((180,11),dtype=np.float64)
            for i in range(180):
                if i>=self.pile.inside:
                    self.card_num[i][10]=1
                else:
                    self.card_num[i][int(self.pile.lst[i].get_no())]=1

            self.stack_positions = np.full(30, 0, dtype=np.float64)
            self.action_space = spaces.Discrete(180)
            self.observation_space = spaces.Dict({
                "card_num": spaces.Box(low=0,high=1,shape=(180,11), dtype=np.float64),
                "movable_cards": spaces.Box(low=0,high=1,shape=(180,), dtype=np.float64),
                "relation":spaces.Box(low=-1,high=1,shape=(180,180), dtype=np.float64),
                "stack_positions": spaces.Box(low=0, high=1, shape=(30,), dtype=np.float64)
            })
        


    def step(self, action):
            """
            执行一步动作并返回观察、奖励、完成标志和其他信息。

            参数：
            - action：要执行的动作

            返回值：
            - observation：当前的观察状态
            - reward：执行动作后的奖励
            - done：是否完成游戏
            - info：其他信息

            """
            self._update_movable_cards()
            # print(action,self.movable_cards)
            if self.movable_cards[action]==0 or self.pile.lst[action].up!=[]:
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                return observation, -1000, False,{}
            else:
                reward=0
                canmove=[card for card in self.pile.lst if card!=None and card.up==[]]
                cansee=[card for card in self.pile.lst if card!=None and card.can_see()]
                if self.stack.inside<6:# 空位不止一个
                    if len(self.stack.dic[int(self.pile.lst[action].get_no())])==2:# 这个牌刚好能消
                        reward+=30
                # 能点的同号牌不少于3张
                    elif len([others for others in canmove if others.get_no()==self.pile.lst[action].get_no()])>=3:
                        reward+=18
                # 暂存区有一张同号
                    elif len(self.stack.dic[int(self.pile.lst[action].get_no())])==1:
                        # 接下来两步可以消掉
                        if len([same for same in cansee if same.get_no()==self.pile.lst[action].get_no() and (same in canmove or same.up==[self.pile.lst[action]])])>=2:
                            reward+=12
                        # return 1
                else:
                # 除非马上消否则都是死
                    if len(self.stack.dic[int(self.pile.lst[action].get_no())])==2:
                        reward+=30

                
                self.stack.dic[self.pile.lst[action].no]+=[self.stack.inside]
                self.stack.lst+=[self.pile.lst[action]]
                if len(self.stack.dic[self.pile.lst[action].no])==3:
                    self.stack.lst = [self.stack.lst[i] for i in range(len(self.stack.lst)) if i not in self.stack.dic[self.pile.lst[action].no]]
                    self.stack.dic[self.pile.lst[action].no]=[]
                    self.stack.inside-=2
                    
                else:
                    self.stack.inside+=1

                # self.pile.move(self.pile.lst[action])
                self.pile.inside-=1
                self.pile.lst[action].district='stack'
                for belows in self.pile.lst[action].below:
                    belows.up.remove(self.pile.lst[action])
                self.pile.lst[action]=None
                self.relation[action,:]=0
                self.relation[:,action]=0
                # self.pile.judge()

                if self.pile.inside==0:
                    # self.done=True
                    self._update_movable_cards()
                    self._update_stack_positions()
                    observation = self._get_observation()
                    self.done=True
                    return observation,reward+50,True,{}
                if self.stack.inside==self.stack.capacity:
                    self._update_movable_cards()
                    self._update_stack_positions()
                    observation = self._get_observation()
                    self.done=True
                    return observation,reward-50,True,{}
                
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                
                return observation,reward,False,{}

        

    def reset(self, seed=None):
            """
            重置游戏环境的状态。

            参数：
            - seed：随机数种子（可选）

            返回：
            - observation：环境的初始观察值
            """
            self.stack.inside = 0
            self.pile.inside = self.pile.setting
            self.stack.dic = {i: [] for i in range(10)}
            self.stack.lst = []
            self.pile.lst = []
            self.done = False
            self.play.w.close()
            self.play = None
            self.play = Play(self.app)
            self.done = False
            
            cards = all_card(self.pile)
            for floor in range(self.pile.floor, 0, -1):
                if floor % 2 == 1:
                    this_floor = [(x, y) for x in range(100, 351, 50) for y in range(40, 291, 50)]
                else:
                    this_floor = [(x, y) for x in range(75, 376, 50) for y in range(15, 316, 50)]
                random.shuffle(this_floor)
                for i in range(self.pile.cardnumber[floor-1]):
                    self.pile.lst.append(Card(cards.pop(), floor, this_floor[i][0], this_floor[i][1], self.play.w))

            self.relation = np.zeros((180, 180), dtype=np.float64)

            for i in range(len(self.pile.lst)):
                rect = self.pile.lst[i].btn.geometry()
                for j in range(len(self.pile.lst)):
                    if self.pile.lst[j].floor < self.pile.lst[i].floor:
                        rect1 = self.pile.lst[j].btn.geometry()
                        if rect.intersects(rect1):
                            self.relation[i][j] = -1
                            self.relation[j][i] = 1
                            self.pile.lst[i].up.append(self.pile.lst[j])
                            self.pile.lst[j].below.append(self.pile.lst[i])
                            continue
                    self.relation[i][j] = 0
                    self.relation[j][i] = 0

            self.movable_cards = np.ones(180, dtype=np.float64)
            for i, card in enumerate(self.pile.lst):
                if not card.up:
                    self.movable_cards[i] = 1
                else:
                    self.movable_cards[i] = 0
            for i in range(self.pile.inside, 180):
                self.movable_cards[i] = 0

            self.card_num = np.zeros((180, 11), dtype=np.float64)
            for i in range(180):
                if i >= self.pile.inside:
                    self.card_num[i][10] = 1
                else:
                    self.card_num[i][int(self.pile.lst[i].get_no())] = 1

            self.stack_positions = np.full(30, 0, dtype=np.float64)
            self.action_space = spaces.Discrete(180)
            self.observation_space = spaces.Dict({
                "card_num": spaces.Box(low=0, high=1, shape=(180, 11), dtype=np.float64),
                "movable_cards": spaces.Box(low=0, high=1, shape=(180,), dtype=np.float64),
                "relation": spaces.Box(low=-1, high=1, shape=(180, 180), dtype=np.float64),
                "stack_positions": spaces.Box(low=0, high=1, shape=(30,), dtype=np.float64)
            })
            return self._get_observation()

    def _get_observation(self):
        """
        返回当前游戏界面的状态，包括可移动牌和栈中位置的信息
        """
        return  {
            "card_num": self.card_num,
            "movable_cards": self.movable_cards,
            "relation":self.relation,
            "stack_positions": self.stack_positions
        }
    
    def _update_movable_cards(self):
        """
        更新可移动牌的信息，当 pile 中某张牌的上方没有其他牌时，将对应的 movable_cards 设置为 True
        """
        self.movable_cards = np.zeros(180, dtype=np.float64)
        for i in range(self.pile.setting):
            if self.pile.lst[i]!=None:
                if self.pile.lst[i].up==[]:
                    self.movable_cards[i] = 1
                    self.card_num[i][int(self.pile.lst[i].get_no())]=1
                else:
                    self.movable_cards[i] = 0
                    self.card_num[i][int(self.pile.lst[i].get_no())]=1
            else:
                self.movable_cards[i] = 0
                self.card_num[10]=1
        for i in range(self.pile.setting,180):
            self.movable_cards[i] = 0
            self.card_num[10]=1

    def _update_stack_positions(self):
        """
        更新暂存区信息
        """
        self.stack_positions = np.full(30, 0, dtype=np.float64)
        for key in self.stack.dic:
            self.stack_positions[key*3+len(self.stack.dic[key])]=1

