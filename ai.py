from stack import pile,stack
from PyQt6.QtWidgets import QApplication, QWidget
import copy
import time

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

    def greedy(self):
        self.can_move=[card for card in pile.lst if card.up==[]]
        while self.can_move and self.on_going:
            self.can_see=[card for card in pile.lst if card.cansee]
            score=[(self.score2(1,card,copy.copy(self.can_move),copy.copy(self.can_see),copy.deepcopy(stack.dic),stack.capacity-stack.inside),card) for card in self.can_move]
            score.sort(reverse=True)
            print([(score,card.get_no()) for score,card in score])
            score[0][1].move()
            QApplication.processEvents()
            time.sleep(0.5)
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
            


ai=AI()