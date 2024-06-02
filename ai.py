from stack import pile,stack
from PyQt6.QtWidgets import QApplication
import copy
import torch
import numpy as np
from model2 import SheepModel as SheepModel2
from dqn4 import Agent as Agent2
import time

class AI:
    """
    AI类用于实现游戏的人工智能功能。

    Attributes:
        work (bool): 表示AI是否在工作中。
        on_going (bool): 表示游戏是否正在进行中。
        model1 (Agent2): DQN模型。
        model2 (SheepModel2): PPO模型。
    """
    def __init__(self):
        """
        初始化AI对象的属性，加载模型。

        Args:
            None

        Returns:
            None
        """
        self.work=False
        self.on_going=True
        self.model1= Agent2(34590,180)
        self.model1.model.load_state_dict(torch.load('model_with_env6.pth'))
        self.model2= SheepModel2()
        ckpt = torch.load('sheep_ppo_env6_240601_111849\ckpt\ckpt_best.pth.tar', map_location='cpu')['model']
        self.model2.load_state_dict(ckpt,strict=False)

    
    def greedy(self):
        """
        使用贪心算法进行游戏。

        Args:
            None

        Returns:
            None
        """
        self.can_move=[card for card in pile.lst if card!=None and card.up==[]]
        while self.can_move and self.on_going:
            begin=time.time()
            self.can_see=[card for card in pile.lst if card!=None and card.can_see()]
            score=[(self.score2(1,card,copy.copy(self.can_move),copy.copy(self.can_see),copy.deepcopy(stack.dic),stack.capacity-stack.inside),card) for card in self.can_move]
            score.sort(reverse=True)
            # print([(score,card.get_no()) for score,card in score])
            end=time.time()
            if end-begin<0.5:
                time.sleep(0.5-end+begin)
            score[0][1].move()
            QApplication.processEvents()
            # time.sleep(0.5)
            self.can_move=[card for card in pile.lst if card!=None and card.up==[]]
        

    def score(self,card,canmove,cansee,dicc,rest):
        """
        计算牌的得分。

        Args:
            card (Card): 需要计算得分的牌。
            canmove (list): 可以移动的牌的列表。
            cansee (list): 可见的牌的列表。
            dicc (dict): 牌堆的字典。
            rest (int): 剩余空位的数量。

        Returns:
            int: 牌的得分。
        """
        if rest>1:# 空位不止一个
            if len(dicc[int(card.get_no())])==2:# 这个牌刚好能消
                return 10
            # 能点的同号牌不少于3张
            if len([others for others in canmove if others.get_no()==card.get_no()])>=3:
                return 6
            # 暂存区有一张同号
            if len(dicc[int(card.get_no())])==1:
                # 接下来两步可以消掉
                if len([same for same in cansee if same.get_no()==card.get_no() and (same in canmove or same.up==[card])])>=2:
                    return 4
                # return 1
        else:
            # 除非马上消否则都是死
            if len(dicc[int(card.get_no())])==2:
                return 10
        return 0
    
    def weight(self,step,score):
        """
        根据步骤和得分返回相应权重。

        Args:
            step (int): 当前步骤。
            score (int): 当前得分。

        Returns:
            float: 权重值。
        """
        if step==1:
            return score
        elif step==2:
            return 0.7*score
        elif step==3:
            return 0.5*score

    def score2(self,step,card,canmove,cansee,dicc,rest):
        """
        递归计算牌的得分。

        Args:
            step (int): 当前步骤。
            card (Card): 需要计算得分的牌。
            canmove (list): 可以移动的牌的列表。
            cansee (list): 可见的牌的列表。
            dicc (dict): 牌堆的字典。
            rest (int): 剩余空位的数量。

        Returns:
            int: 牌的得分。
        """
        if rest==0:
            return 0
        elif step==3:
            return self.weight(step,self.score(card,canmove,cansee,dicc,rest))
        elif canmove==[card]:
            return self.weight(step,self.score(card,canmove,cansee,dicc,rest))
        else:
            x=self.score(card,canmove,cansee,dicc,rest)
            for cards in card.below:
                if cards.up==[card]:
                    canmove+=[cards]

                if not cards.cansee:
                    cansee+=[cards]
            
            canmove.remove(card)
            cansee.remove(card)
            dicc[int(card.get_no())].append(stack.inside+step)
            if len(dicc[int(card.get_no())])==3:
                dicc[int(card.get_no())]=[]
                rest+=2
            else:
                rest-=1
            return self.weight(step,x)+max([self.score2(step+1,another,copy.copy(canmove),copy.copy(cansee),copy.deepcopy(dicc),copy.copy(rest)) for another in canmove])

    def ppo_work(self):
        """
        使用PPO模型进行游戏。

        Args:
            None

        Returns:
            None
        """
        while self.on_going:
            observation = self.get_obs5()  
            # print(observation)
            action = self.model2.compute_action(observation)

            pile.lst[action].move()
            QApplication.processEvents()
            time.sleep(0.5)

    def get_obs5(self):
        """
        获取游戏状态的观察值。

        Args:
            None

        Returns:
            dict: 包含游戏状态的观察值。
        """
        self.relation=np.zeros((180,180),dtype=np.float64)

        for i in range(len(pile.lst)):
            if pile.lst[i]!=None:
                rect=pile.lst[i].btn.geometry()
                for j in range(len(pile.lst)):
                    if pile.lst[j]==None:
                        continue
                    if pile.lst[j].floor<pile.lst[i].floor:
                        rect1=pile.lst[j].btn.geometry()
                        if rect.intersects(rect1):
                            self.relation[i][j]=-1
                            self.relation[j][i]=1
                            pile.lst[i].up.append(pile.lst[j])
                            pile.lst[j].below.append(pile.lst[i])
                            continue
                    self.relation[i][j]=0
                    self.relation[j][i]=0
            else:
                self.relation[i,:]=0
                self.relation[:,i]=0

        self.card_num=np.zeros((180,11),dtype=np.float64)
        self.movable_cards = np.zeros(180, dtype=np.float64)
        for i in range(pile.setting):
            if pile.lst[i]!=None:
                if pile.lst[i].up==[]:
                    self.movable_cards[i] = 1
                    self.card_num[i][int(pile.lst[i].get_no())]=1
                else:
                    self.movable_cards[i] = 0
                    self.card_num[i][int(pile.lst[i].get_no())]=1
            else:
                self.movable_cards[i] = 0
                self.card_num[10]=1
        for i in range(pile.setting,180):
            self.movable_cards[i] = 0
            self.card_num[10]=1

        self.stack_positions = np.full(30, 0, dtype=np.float64)
        for key in stack.dic:
            self.stack_positions[key*3+len(stack.dic[key])]=1

        return  {
            "card_num": self.card_num,
            "movable_cards": self.movable_cards,
            "relation":self.relation,
            "stack_positions": self.stack_positions
        }

    def dqn_work5(self):
        """
        使用DQN模型进行游戏。

        Args:
            None

        Returns:
            None
        """
        while self.on_going:
            observation = self.get_obs5()  
            action=self.model1.choose_action(observation)

            pile.lst[action].move()
            QApplication.processEvents()
            time.sleep(0.5)
    
            
ai=AI()

