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
            # score=[(self.score(card),card) for card in self.can_move]
            score=[(self.score2(1,card,copy.copy(self.can_move),copy.copy(self.can_see)),card) for card in self.can_move]
            score.sort(reverse=True)
            score[0][1].move()
            QApplication.processEvents()
            # time.sleep(1)
            self.can_move=[card for card in pile.lst if card.up==[]]
        

    def score(self,card):
        if stack.dic[int(card.get_no())]==2:
            return 5
        if len([others for others in self.can_move if others.get_no()==card.get_no()])==3:
            return 4
        if stack.dic[int(card.get_no())]==1:
            for another in self.can_see:
                if another.get_no()==card.get_no() and another.up==[]:
                    return 4
                if another.get_no()==card.get_no() and card in another.up:
                    return 3
        return 0
    
    def score2(self,step,card,canmove,cansee):
        if step==3:
            return self.score(card)
        elif canmove==[card]:
            return self.score(card)
        else:
            for cards in card.below:
                if cards.up==[card]:
                    canmove+=[cards]

                if not cards.cansee:
                    cansee+=[cards]
            canmove.remove(card)
            cansee.remove(card)
            return self.score(card)+max([self.score2(step+1,another,canmove,cansee) for another in canmove])
        
        


ai=AI()