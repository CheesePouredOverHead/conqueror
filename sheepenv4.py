import gym
import numpy as np
from card import Card
from stack import Stack,Pile
from ui import Play
from PyQt6.QtWidgets import QApplication
import random
import copy
from typing import Dict, Optional, Tuple
import sys

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
    R = 50
    
    def __init__(self, floor: int, stack_capacity: int = 7, agent: bool = True) -> None:
        self.floor = floor
        self.stack_capacity = stack_capacity
        self.agent = agent
        self.pile=Pile()
        self.stack=Stack(self.stack_capacity)
        self.app = QApplication(sys.argv)
        self.play=Play(self.app)
        self.pile.setting=12*self.floor
        self.pile.cardnumber=[12 for x in range(self.floor)]
        self.pile.floor=floor
        self.item_per_icon=1 if self.pile.setting<=30 else round(self.pile.setting/10)
        self._make_game()

    def seed(self, seed: int) -> None:
        self._seed = seed
        np.random.seed(self._seed)

    def _make_game(self) -> None:
        # TODO wash scene
        cards=all_card(self.pile)
        for floor in range(self.pile.floor,0,-1):
            if floor%2==1:
                this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
            else:
                this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
            random.shuffle(this_floor)
            for i in range(self.pile.cardnumber[floor-1]):
                self.pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],self.play.w))

        self.pile.detect()
        self.reward_3tiles = self.R * 0.5 / (self.pile.setting // 3)

        self._update_visible_accessible()
        self._set_space()

    def _update_visible_accessible(self) -> None:
        for i in range(self.pile.setting):
            item1 = self.pile.lst[i]
            if item1 is None:
                continue
            item1.accessible = 1 if item1.up==[] else 0
            item1.visible = item1.can_see()
    
    def _execute_action(self, action: int) -> float:
        try:
        # print(action)
        # print(self.pile.lst)
        # print(self.pile.lst[action])
        # print(len(self.pile.lst),action)
            for belows in self.pile.lst[action].below:
                belows.up.remove(self.pile.lst[action])
            self.pile.inside -= 1
            self.stack.dic[self.pile.lst[action].no]+=[self.stack.inside]
            self.stack.lst+=[self.pile.lst[action]]
            if len(self.stack.dic[self.pile.lst[action].no])==3:
                self.stack.lst = [self.stack.lst[i] for i in range(len(self.stack.lst)) if i not in self.stack.dic[self.pile.lst[action].no]]
                self.stack.dic[self.pile.lst[action].no]=[]
                self.stack.inside-=2
                
                self.pile.lst[action] = None
                # reward=copy.deepcopy(self.reward_3tiles)
                return 30.
            # elif len(self.stack.dic[self.pile.lst[action].no])==2:
            #     self.stack.inside+=1
            #     self.pile.lst[action] = None
            #     return 10.
            else:
                self.stack.inside+=1
                self.pile.lst[action] = None
                return 0.
        except IndexError:
            print(len(self.pile.lst),action)
            return 0.
        
    def reset(self, level: Optional[int] = None) -> Dict:
        if level is not None:
            self.floor = level
            assert 1 <= self.level <= self.max_level
        self.pile.inside=self.pile.setting
        self.pile.setting=12*self.floor
        self.pile.lst=[]
        self.pile.cardnumber=[12 for x in range(self.floor)]
        self.stack=Stack(self.stack_capacity)
        self._make_game()
        self._set_space()
        return self._get_obs()
    
    def step(self, action: int) -> Tuple:
        rew = self._execute_action(action)
        self._update_visible_accessible()
        # print('stack',self.stack.inside)
        obs = self._get_obs()
        if self.pile.inside == 0:
            rew += self.R
            done = True
        elif self.stack.inside == self.stack.capacity:
            rew -= self.R
            done = True
        else:
            done = False
        info = {}
        # print(obs['action_mask'])
        return obs, rew, done, info
    
    def _get_obs(self) -> Dict:
        item_obs = np.zeros((180, 39))
        action_mask = np.zeros(180).astype(np.uint8)

        for i in range(self.pile.setting):
            item = self.pile.lst[i]
            if item is None:
                item_obs[i][11] = 1
            else:
                if item.can_see():
                    item_obs[i][item.no] = 1
                    item_obs[i][12+(item.x-75)//25]=1
                    item_obs[i][25+(item.y-15)//25]=1
                    item_obs[i][38]=1
                    if item.up==[]:
                        item_obs[i][10]=1
                        action_mask[i] = 1


        stack_obs = np.zeros(3 * 10)
        for i in self.stack.dic:
            stack_obs[i*3+len(self.stack.dic[i])]=1

        global_obs = np.zeros(self.global_size)
        # print('inside',self.stack.inside)
        # print(self.stack.lst)
        global_obs[round(self.pile.inside/self.pile.setting*10)] = 1
        global_obs[self.global_size - self.stack.capacity - 1 + self.stack.inside] = 1

        return {
            'item_obs': item_obs,
            'stack_obs': stack_obs,
            'global_obs': global_obs,
            'action_mask': action_mask,
        }
    
    def _set_space(self) -> None:
    
        self.global_size = 10 + 1 + 7 + 1
        self.observation_space = gym.spaces.Dict(
            {
                'item_obs': gym.spaces.Box(0, 1, dtype=np.float32, shape=(180, 39)),
                'stack_obs': gym.spaces.Box(0, 1, dtype=np.float32, shape=(30, )),
                'global_obs': gym.spaces.Box(0, 1, dtype=np.float32, shape=(self.global_size, )),
                'action_mask': gym.spaces.Box(0, 1, dtype=np.float32, shape=(180, ))  # TODO
            }
        )
        self.action_space = gym.spaces.Discrete(180)
        self.reward_space = gym.spaces.Box(-self.R * 1.5, self.R * 1.5, dtype=np.float32)

    def close(self) -> None:
        pass