from stack import pile,stack
from PyQt6.QtWidgets import QApplication, QWidget
import copy
import time
import torch
from gym.envs.registration import register
import numpy as np
from dqn import DQN

def copy_list(lst):
    new_lst = []
    for item in lst:
        if not isinstance(item, QWidget):
            new_lst.append(copy.deepcopy(item))
        else:
            new_lst.append(item)
    return new_lst

class AI:
    def __init__(self):
        self.work=False
        self.on_going=True
        self.model= DQN(32767,180)
        self.state_dict = torch.load("model_parameters.pth")
        self.model.load_state_dict(self.state_dict)
    
    def greedy(self):
        self.can_move=[card for card in pile.lst if card.up==[]]
        while self.can_move and self.on_going:
            self.can_see=[card for card in pile.lst if card.cansee]
            score=[(self.score2(1,card,copy.copy(self.can_move),copy.copy(self.can_see),copy.deepcopy(stack.dic),stack.capacity-stack.inside),card) for card in self.can_move]
            score.sort(reverse=True)
            # print([(score,card.get_no()) for score,card in score])
            score[0][1].move()
            QApplication.processEvents()
            # time.sleep(0.5)
            self.can_move=[card for card in pile.lst if card.up==[]]
        

    def score(self,card,canmove,cansee,dicc,rest):
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
        if step==1:
            return score
        elif step==2:
            return 0.7*score
        elif step==3:
            return 0.5*score

    def score2(self,step,card,canmove,cansee,dicc,rest):
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
        
    def get_obs(self):
        self.relation=np.zeros((180,180),dtype=np.int32)

        for i in range(len(pile.lst)):
            rect=pile.lst[i].btn.geometry()
            for j in range(len(pile.lst)):
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

        self.movable_cards = np.ones(180, dtype=np.int32)
        for i, card in enumerate(pile.lst):
            if not card.up:
                self.movable_cards[i] = 1
            else:
                self.movable_cards[i] = 0
        for i in range(pile.inside,180):
            self.movable_cards[i] = 0

        self.card_num=np.zeros(180,dtype=np.int32)
        for i in range(180):
            if i>=pile.inside:
                self.card_num[i]=-1
            else:
                self.card_num[i]=int(pile.lst[i].get_no())

        self.stack_positions = np.full(7, -1, dtype=np.int32)
        for i in range(stack.inside):
            self.stack_positions[i] = stack.lst[i].no
        for i in range(stack.inside, 7):
            self.stack_positions[i] = -1

        return  {
            "card_num": self.card_num,
            "movable_cards": self.movable_cards,
            "relation":self.relation,
            "stack_positions": self.stack_positions
        }
    
    def dqn_work(self):
        while self.on_going:
            observation = self.get_obs()  
            part1 = torch.tensor(observation["card_num"])  
            part2 = torch.tensor(observation["movable_cards"])  
            part3 = torch.tensor(observation["relation"])
            part4 = torch.tensor(observation["stack_positions"])
            part3 = part3.view(-1)
            # 将多个部分合并成一个张量
            observation_tensor = torch.cat([part1, part2,part3,part4], dim=-1)
            observation_tensor=observation_tensor.float()

            action_probs = self.model(observation_tensor)

            # 选择概率最高的动作
            legal_actions = [i for i in range(180) if observation['movable_cards'][i]==1]
            act_values_legal = action_probs.clone().detach()
            act_values_legal[[i for i in range(180) if i not in legal_actions]] = float('-inf')
            action = torch.argmax(act_values_legal).item()

            pile.lst[action].move()
            QApplication.processEvents()
        
            
            
ai=AI()

