import gymnasium as gym
from gymnasium import spaces
# from collections import deque
from stack import Stack,Pile
# from generate import generate
import random
import numpy as np
from PyQt6.QtWidgets import QApplication
import sys
from card import Card
from PyQt6.QtWidgets import QWidget

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
        super().__init__()
        self.stack=Stack(7)
        self.pile=Pile()
        self.pile.floor=random.randrange(2,7)
        # self.pile.floor=2
        self.app= QApplication(sys.argv)
        self.w=QWidget()

        self.done=False
        while True:
            self.pile.cardnumber=[]
            for i in range(self.pile.floor):
                self.pile.cardnumber.append(random.randrange(1,37))
            if sum(self.pile.cardnumber)%3==0 and sum(self.pile.cardnumber)<=180:
                self.pile.setting=sum(self.pile.cardnumber)
                self.pile.inside=self.pile.setting
                # print(self.pile.floor,self.pile.setting)
                break
        """self.pile.setting=12
        self.pile.inside=self.pile.setting
        self.pile.cardnumber=[6,6]"""
        # generate(self.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            if floor%2==1:
                this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
            else:
                this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.w))

        self.pile.detect()

        self.inpile = np.full((180,5), 0, dtype=np.int32)
        for i, card in enumerate(self.pile.lst):
            self.inpile[i][0] = int(card.get_no())
            self.inpile[i][1] = card.floor
            self.inpile[i][2] = card.x
            self.inpile[i][3] = card.y
            if not card.up:
                self.inpile[i][4] = 1
            else:
                self.inpile[i][4] = 0
        for i in range(self.pile.inside,180):
            self.inpile[i,0:4]=-1

        self.instack = np.full(7, -1, dtype=np.int32)

        self.action_space = spaces.Discrete(180)
        self.observation_space = spaces.Dict({
            "pile": spaces.Box(low=-1,high=375,shape=(180,5), dtype=np.int32),
            "stack": spaces.Box(low=-1, high=9, shape=(7,), dtype=np.int32)
        })
        # self.observation_space=self._get_observation()
        


    def step(self, action):
        self.update()
        if self.inpile[action][4]==0 or self.pile.lst[action].up!=[]:
            self.update()
            obs=self._get_observation()
            return obs, -1000, False, False,{}
        else:
            inside_record=self.stack.inside

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
                self.update()
                observation = self._get_observation()
                self.done=True
                # print('win')
                return observation,500,True,False,{}
            if self.stack.inside==self.stack.capacity:
                self.update()
                observation = self._get_observation()
                self.done=True
                # print('lose')
                return observation,-500,True,False,{}
            inside_now=self.stack.inside
            self.update()
            observation = self._get_observation()
            
            if inside_now<inside_record:
                reward=300+(self.pile.setting-self.pile.inside)/self.pile.setting*500
            else:
                reward=(self.pile.setting-self.pile.inside)/self.pile.setting*500
            return observation,reward,False,False,{}

        

    def reset(self,seed=None,options=None):
        self.stack.inside=0
        # self.pile.inside=self.pile.setting
        self.stack.dic={i:[] for i in range(10)}
        self.stack.lst=[]
        self.pile.lst=[]
        self.pile.floor=random.randrange(2,7)
        # self.pile.floor=2
        self.done=False

        self.done=False
        while True:
            self.pile.cardnumber=[]
            for i in range(self.pile.floor):
                self.pile.cardnumber.append(random.randrange(1,(i+2)**2))
            if sum(self.pile.cardnumber)%3==0 and sum(self.pile.cardnumber)<=180:
                self.pile.setting=sum(self.pile.cardnumber)
                self.pile.inside=self.pile.setting
                break
        """self.pile.setting=12
        self.pile.inside=self.pile.setting
        self.pile.cardnumber=[6,6]"""
        # generate(self.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            if floor%2==1:
                this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
            else:
                this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.w))

        self.pile.detect()

        self.inpile = np.full((180,5), 0, dtype=np.int32)
        for i, card in enumerate(self.pile.lst):
            self.inpile[i][0] = int(card.get_no())
            self.inpile[i][1] = card.floor
            self.inpile[i][2] = card.x
            self.inpile[i][3] = card.y
            if not card.up:
                self.inpile[i][4] = 1
            else:
                self.inpile[i][4] = 0
        for i in range(self.pile.inside,180):
            self.inpile[i,0:4]=-1
            self.inpile[i,4]=0
        
        # 初始化 stack 中的位置信息，假设初始时所有位置都为空
        self.instack = np.full(7, -1, dtype=np.int32)   
        # self._update_stack_positions()
        self.action_space = spaces.Discrete(180)
        self.observation_space = spaces.Dict({
            "pile": spaces.Box(low=-1,high=375,shape=(180,5), dtype=np.int32),
            "stack": spaces.Box(low=-1, high=9, shape=(7,), dtype=np.int32)
        })
        return self._get_observation(),{}
    
    def seed(self, seed=None):
        self.np_random= np.random.SeedSequence(seed)
        return [seed]
    
    def update(self):
        # 更新可移动牌的信息，当 pile 中某张牌的上方没有其他牌时，将对应的 movable_cards 设置为 True
        for i, card in enumerate(self.pile.lst):
            self.inpile[i][0] = int(card.get_no())
            self.inpile[i][1] = card.floor
            self.inpile[i][2] = card.x
            self.inpile[i][3] = card.y
            if not card.up:
                self.inpile[i][4] = 1
            else:
                self.inpile[i][4] = 0
        for i in range(self.pile.inside,180):
            self.inpile[i,0:4]=-1
            self.inpile[i,4]=0

        for i in range(self.stack.inside):
            self.instack[i] = self.stack.lst[i].no
        for i in range(self.stack.inside, 7):
            self.instack[i] = -1

    def _get_observation(self):
        return {
            "pile": self.inpile,
            "stack": self.instack
        }
