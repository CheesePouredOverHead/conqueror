from stack import pile,stack
from PyQt6.QtWidgets import QApplication
import time

class AI:
    def __init__(self):
        self.work=False
        self.on_going=True

    def greedy(self):
        self.can_move=[card for card in pile.lst if card.up==[]]
        while self.can_move and self.on_going:
            self.can_see=[card for card in pile.lst if card.cansee]
            score=[(self.score(card),card) for card in self.can_move]
            score.sort(reverse=True)
            score[0][1].move()
            QApplication.processEvents()
            time.sleep(1)
            self.can_move=[card for card in pile.lst if card.up==[]]
        

    def score(self,card):
        if stack.dic[int(card.get_no())]==2:
            return 5
        elif stack.dic[int(card.get_no())]==1:
            for another in self.can_see:
                if another.get_no()==card.get_no() and card in another.up:
                    return 4
        return 0
        
        


ai=AI()