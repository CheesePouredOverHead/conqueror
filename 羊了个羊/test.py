import sys
from ui import InputCapacity,Play
from stack import stack,pile
from generate import *
from PyQt6.QtWidgets import QApplication
from ai import ai
from PyQt6.QtCore import QCoreApplication
class test:
    def __init__(self):
        self.count=0
    def test(self,num,app):
        for i in range(num):
            stack.capacity=7
            stack.inside=0
            stack.dic={i:[] for i in range(10)} 
            stack.lst=[]
            pile.lst=[]
            pile.floor=4
            pile.cardnumber=[4,9,16,25]
            pile.setting=54
            pile.inside=54

        
            ai.work=True
            begin=Play(app)
            self.w=begin.w
            pile.on_win=self.win
            stack.on_lose=self.lose
            begin.play()
            

            QCoreApplication.processEvents()
            QCoreApplication.sendPostedEvents(None, 0)

            # Destroy the Play instance
            begin = None
            ai.on_going = True
            print(i,'end')

        print(self.count/num)
        QCoreApplication.quit()
        sys.exit(0)
        

    def win(self):
        self.count+=1
        ai.on_going=False
        print('win')
        self.w.deleteLater()

    def lose(self):
        ai.on_going=False
        print('lose')
        self.w.deleteLater()

#test 需要把ui.play中的延时改为瞬时，ai.greedy中的延时也要改为瞬时
if __name__ == '__main__':
    app = QApplication(sys.argv)
    test1=test()
    test1.test(10,app)
    app.exec()
    