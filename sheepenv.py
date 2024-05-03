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
    def __init__(self):
        super(SheepEnv, self).__init__()
        self.stack=Stack(7)
        self.pile=Pile()
        self.pile.floor=random.randrange(2,7)
        self.app= QApplication(sys.argv)
        self.play=Play(self.app)

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
        # generate(self.play.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            if floor%2==1:
                this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
            else:
                this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))

        # for card in self.pile.lst:
        #         card.display()

        self.relation=np.zeros((180,180),dtype=np.int32)

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
                    

        self.movable_cards = np.ones(180, dtype=np.int32)
        for i, card in enumerate(self.pile.lst):
            if not card.up:
                self.movable_cards[i] = 1
            else:
                self.movable_cards[i] = 0
        for i in range(self.pile.inside,180):
            self.movable_cards[i] = 0

        self.card_num=np.zeros(180,dtype=np.int32)
        for i in range(180):
            if i>=self.pile.inside:
                self.card_num[i]=-1
            else:
                self.card_num[i]=int(self.pile.lst[i].get_no())

        # 初始化 stack 中的位置信息，假设初始时所有位置都为空
        self.stack_positions = np.full(7, -1, dtype=np.int32)
        # self._update_stack_positions()
        self.action_space = spaces.Discrete(180)
        self.observation_space = spaces.Dict({
            "card_num": spaces.Box(low=-1,high=9,shape=(180,), dtype=np.int32),
            "movable_cards": spaces.Box(low=0,high=1,shape=(180,), dtype=np.int32),
            "relation":spaces.Box(low=-1,high=1,shape=(180,180), dtype=np.int32),
            "stack_positions": spaces.Box(low=-1, high=9, shape=(7,), dtype=np.int32)
        })
        # self.observation_space=self._get_observation()
        


    def step(self, action):
        self._update_movable_cards()
        # print(action,self.movable_cards)
        if self.movable_cards[action]==0 or self.pile.lst[action].up!=[]:
            self._update_movable_cards()
            self._update_stack_positions()
            observation = self._get_observation()
            return observation, -100, False, False,{}
        else:
            inside_record=self.stack.inside

            # self.pile.lst[action].move()
            # self.pile.lst[action].x,self.pile.lst[action].y=self.stack.get_location()
            # self.pile.lst[action].btn.move(self.pile.lst[action].x,self.pile.lst[action].y)
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
            self.relation[action,:]=0
            self.relation[:,action]=0
            # self.pile.judge()

            

            if self.pile.inside==0:
                # self.done=True
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                self.done=True
                return observation,50,True,False,{}
            if self.stack.inside==self.stack.capacity:
                self._update_movable_cards()
                self._update_stack_positions()
                observation = self._get_observation()
                self.done=True
                return observation,-50,True,False,{}
            inside_now=self.stack.inside
            self._update_movable_cards()
            self._update_stack_positions()
            observation = self._get_observation()
            
            if inside_now<inside_record:
                reward=30
            else:
                reward=(self.pile.setting-self.pile.inside)/self.pile.setting*10
            return observation,reward,False,False,{}

        

    def reset(self,seed=None):
        self.stack.inside=0
        # self.pile.inside=self.pile.setting
        self.stack.dic={i:[] for i in range(10)}
        self.stack.lst=[]
        self.pile.lst=[]
        self.pile.floor=random.randrange(2,7)
        self.done=False
        self.play.w.close()
        self.play=None
        self.play=Play(self.app)

        self.done=False
        while True:
            self.pile.cardnumber=[]
            for i in range(self.pile.floor):
                self.pile.cardnumber.append(random.randrange(1,(i+2)**2))
            if sum(self.pile.cardnumber)%3==0 and sum(self.pile.cardnumber)<=180:
                self.pile.setting=sum(self.pile.cardnumber)
                self.pile.inside=self.pile.setting
                break
        # generate(self.play.w,self.pile)

        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            if floor%2==1:
                this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
            else:
                this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))

        self.relation=np.zeros((180,180),dtype=np.int32)

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

        self.movable_cards = np.ones(180, dtype=np.int32)
        for i, card in enumerate(self.pile.lst):
            if not card.up:
                self.movable_cards[i] = 1
            else:
                self.movable_cards[i] = 0
        for i in range(self.pile.inside,180):
            self.movable_cards[i] = 0

        self.card_num=np.zeros(180,dtype=np.int32)
        for i in range(180):
            if i>=self.pile.inside:
                self.card_num[i]=-1
            else:
                self.card_num[i]=int(self.pile.lst[i].get_no())

        # 初始化 stack 中的位置信息，假设初始时所有位置都为空
        self.stack_positions = np.full(7, -1, dtype=np.int32)   
        # self._update_stack_positions()
        self.action_space = spaces.Discrete(180)
        self.observation_space = spaces.Dict({
            "card_num": spaces.Box(low=-1,high=9,shape=(180,), dtype=np.int32),
            "movable_cards": spaces.Box(low=0,high=1,shape=(180,), dtype=np.int32),
            "relation":spaces.Box(low=-1,high=1,shape=(180,180), dtype=np.int32),
            "stack_positions": spaces.Box(low=-1, high=9, shape=(7,), dtype=np.int32)
        })
        return self._get_observation()

    def _get_observation(self):
        # 返回当前游戏界面的状态，包括可移动牌和栈中位置的信息
        return  {
            "card_num": self.card_num,
            "movable_cards": self.movable_cards,
            "relation":self.relation,
            "stack_positions": self.stack_positions
        }
    
    def _update_movable_cards(self):
        # 更新可移动牌的信息，当 pile 中某张牌的上方没有其他牌时，将对应的 movable_cards 设置为 True
        for i, card in enumerate(self.pile.lst):
            if not card.up:
                self.movable_cards[i] = 1
            else:
                self.movable_cards[i] = 0
            self.card_num[i]=int(self.pile.lst[i].get_no())
        for i in range(self.pile.inside,180):
            self.movable_cards[i] = 0
            self.card_num[i]=-1

    def _update_stack_positions(self):
        for i in range(self.stack.inside):
            self.stack_positions[i] = self.stack.lst[i].no
        for i in range(self.stack.inside, 7):
            self.stack_positions[i] = -1

