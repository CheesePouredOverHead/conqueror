import gymnasium as gym
from gymnasium import spaces
# from collections import deque
from stack import Stack,Pile
from ui import Play
from generate import generate
import random
import numpy as np
from PyQt6.QtWidgets import QApplication
import sys
from card import Card
from gym.spaces import Dict, MultiBinary

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
    def __init__(self):
        super(SheepEnv, self).__init__()
        self.stack=Stack(7)
        self.pile=Pile()
        self.pile.floor=random.randrange(2,3)
        self.app= QApplication(sys.argv)
        self.play=Play(self.app)
        self.done=False
        while True:
            self.pile.cardnumber=[]
            for i in range(self.pile.floor):
                self.pile.cardnumber.append(random.randrange(1,(i+2)**2))
            if sum(self.pile.cardnumber)%3==0:
                self.pile.setting=sum(self.pile.cardnumber)
                self.pile.inside=self.pile.setting
                break
        # generate(self.play.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            this_floor=[(x,y) for x in range(225-floor*25,225-floor*25+50*floor+1,50) for y in range(165-25*floor,165-25*floor+50*floor+1,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))


        for card in self.pile.lst:
            rect = card.btn.geometry()
            for other in self.pile.lst:
                if other.floor<card.floor:
                    rect1=other.btn.geometry()
                    if rect.intersects(rect1) :
                        card.up.append(other)
                        other.below.append(card)

        self.movable_cards = np.ones(self.pile.setting, dtype=bool)

        # 初始化 stack 中的位置信息，假设初始时所有位置都为空
        self.stack_positions = np.zeros(self.stack.capacity, dtype=bool)
        self.action_space = spaces.Discrete(self.pile.setting)
        self.observation_space = spaces.Dict({
            "movable_cards": spaces.MultiBinary(self.pile.setting),
            "stack_positions": spaces.MultiBinary(self.stack.capacity)
        })
        


    def step(self, action):
        if self.movable_cards[action]==False or self.pile.lst[action].up!=[]:
            self._update_movable_cards()
            self._update_stack_positions()
            observation = self._get_observation()
            return observation, -1, False, False,{}
        else:
            inside_record=self.stack.inside

            # self.pile.lst[action].move()
            self.pile.lst[action].x,self.pile.lst[action].y=self.stack.get_location()
            self.pile.lst[action].btn.move(self.pile.lst[action].x,self.pile.lst[action].y)
            # self.stack.add(self.pile.lst[action])
            self.stack.dic[self.pile.lst[action].no]+=[self.stack.inside]
            self.stack.lst+=[self.pile.lst[action]]
            if len(self.stack.dic[self.pile.lst[action].no])==3:
                self.stack.eliminate(self.stack.dic[self.pile.lst[action].no])
                self.stack.inside-=2
                self.stack.dic[self.pile.lst[action].no]=[]
            else:
                self.stack.inside+=1

            # self.pile.move(self.pile.lst[action])
            self.pile.inside-=1
            self.pile.lst[action].district='stack'
            for belows in self.pile.lst[action].below:
                belows.up.remove(self.pile.lst[action])
            self.pile.lst.remove(self.pile.lst[action])
            # self.pile.judge()

            

            if self.pile.inside==0:
                # self.done=True
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                return observation,10,True,False,{}
            if self.stack.inside==self.stack.capacity:
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                return observation,-10,True,False,{}
            inside_now=self.stack.inside
            self._update_movable_cards()
            self._update_stack_positions()
            observation = self._get_observation()
            return observation,inside_record-inside_now+1,False,False,{}

        

    def reset(self,seed=None):
        self.stack.inside=0
        self.pile.inside=self.pile.setting
        self.stack.dic={i:[] for i in range(10)}
        self.pile.lst=[]
        self.pile.lst=[]
        self.done=False

        while True:
            self.pile.cardnumber=[]
            for i in range(self.pile.floor):
                self.pile.cardnumber.append(random.randrange(1,(i+2)**2))
            if sum(self.pile.cardnumber)==self.pile.setting:
                break
        # generate(self.play.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            this_floor=[(x,y) for x in range(225-floor*25,225-floor*25+50*floor+1,50) for y in range(165-25*floor,165-25*floor+50*floor+1,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))


        for card in self.pile.lst:
            rect = card.btn.geometry()
            for other in self.pile.lst:
                if other.floor<card.floor:
                    rect1=other.btn.geometry()
                    if rect.intersects(rect1) :
                        card.up.append(other)
                        other.below.append(card)

        self.movable_cards = np.ones(self.pile.setting, dtype=bool)

        # 初始化 stack 中的位置信息，假设初始时所有位置都为空
        self.stack_positions = np.zeros(self.stack.capacity, dtype=bool)
        self.action_space = spaces.Discrete(self.pile.setting)
        self.observation_space = spaces.Dict({
            "movable_cards": spaces.MultiBinary(self.pile.setting),
            "stack_positions": spaces.MultiBinary(self.stack.capacity)
        })
        return self._get_observation(),{}

    def _get_observation(self):
        # 返回当前游戏界面的状态，包括可移动牌和栈中位置的信息
        return  {
            "movable_cards": self.movable_cards,
            "stack_positions": self.stack_positions
        }
    
    def _update_movable_cards(self):
        # 更新可移动牌的信息，当 pile 中某张牌的上方没有其他牌时，将对应的 movable_cards 设置为 True
        for i, card in enumerate(self.pile.lst):
            if not card.up:
                self.movable_cards[i] = True
            else:
                self.movable_cards[i] = False
        for i in range(self.pile.inside,self.pile.setting):
            self.movable_cards[i] = False

    def _update_stack_positions(self):
        for i in range(self.stack.inside):
            self.stack_positions[i] = True
        for i in range(self.stack.inside, self.stack.capacity):
            self.stack_positions[i] = False

    def render(self):
        for card in self.pile.lst:
                card.display()