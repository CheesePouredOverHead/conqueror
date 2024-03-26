from stack import pile,stack
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
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
            # score=[(self.score(card,copy.copy(self.can_move),copy.copy(self.can_see),copy.deepcopy(stack.dic)),card) for card in self.can_move]
            score=[(self.score2(1,card,copy.copy(self.can_move),copy.copy(self.can_see),copy.deepcopy(stack.dic)),card) for card in self.can_move]
            score.sort(reverse=True)
            print([(score,card.get_no()) for score,card in score])
            score[0][1].move()
            QApplication.processEvents()
            time.sleep(1)
            self.can_move=[card for card in pile.lst if card.up==[]]
        

    def score(self,card,canmove,cansee,dicc):
        if len(dicc[int(card.get_no())])%3==2:
            return 10
        if len([others for others in canmove if others.get_no()==card.get_no()])%3==0:
            return 6
        if len(dicc[int(card.get_no())])%3==1:
            for another in cansee:
                if another.get_no()==card.get_no() and another in canmove:
                    return 4
                if another.get_no()==card.get_no() and card in another.up:
                    return 3
        return 0
    
    def score2(self,step,card,canmove,cansee,dicc):
        canmove = canmove.copy()
        cansee = cansee.copy()
        if step==3:
            return 0.5*self.score(card,canmove,cansee,dicc)
        elif canmove==[card]:
            return self.score(card,canmove,cansee,dicc)
        else:
            for cards in card.below:
                if cards.up==[card]:
                    canmove+=[cards]

                if not cards.cansee:
                    cansee+=[cards]
            x=self.score(card,canmove,cansee,dicc)
            canmove.remove(card)
            cansee.remove(card)
            dicc[int(card.get_no())].append(stack.inside+step)
            if step==1:
                return x+max([self.score2(step+1,another,canmove,cansee,copy.deepcopy(dicc)) for another in canmove])
            else:
                return 0.7*x+max([self.score2(step+1,another,canmove,cansee,copy.deepcopy(dicc)) for another in canmove])


ai=AI()