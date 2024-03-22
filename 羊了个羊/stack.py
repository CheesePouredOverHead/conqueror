# from judge import *
from PyQt6.QtGui import QFont,QColor,QPolygonF
from PyQt6.QtCore import QRect,QPoint,QPointF,Qt

class Stack:
    def __init__(self,capacity):
        self.capacity=capacity
        self.inside=0
        self.dic={i:[] for i in range(10)}
        self.lst=[]

    def get_location(self,index=None):
        if index==None:
            index=self.inside
        return int((500-50*self.capacity)/2+50*index),380
    
    def add(self,card):
        self.dic[card.no]+=[self.inside]
        self.lst+=[card]
        if len(self.dic[card.no])==3:
            self.eliminate(self.dic[card.no])
            self.inside-=2
            self.dic[card.no]=[]
        else:
            self.inside+=1
        self.judge()

        # print(self.inside,[x.no for x in self.lst],self.dic)
        # result=self.judge()
        # if result=='process':
        #     pass
        
    def judge(self):
        if self.inside>=self.capacity:
            lose()
            # return 'lose'
        # else:
            # return 'process'


    def eliminate(self,to_delete):
        """for index in to_delete:
            self.lst[index].btn.deleteLater()
            print(f'eliminate {self.lst[index].no} at {index}')
        self.lst = [self.lst[i] for i in range(len(self.lst)) if i not in to_delete]
        for index_after in range(len(self.lst)):
            self.lst[index_after].move(index_after)"""
        for index in to_delete:
            self.lst[index].btn.deleteLater()
            print(f'eliminate {self.lst[index].no} at {index}')
        self.lst = [self.lst[i] for i in range(len(self.lst)) if i not in to_delete]
        # for no, indices in self.dic.items():
        #     self.dic[no] = [i for i in indices if i not in to_delete]
        for no, indices in self.dic.items():
            self.dic[no] = [i for i in indices if i not in to_delete]
            self.dic[no] = [i - len([j for j in to_delete if j < i]) for i in self.dic[no]]
        for index_after in range(len(self.lst)):
            self.lst[index_after].move(index_after)

#暂存区暂时设为7，后续再自定义
stack=Stack(7)

class Pile:
    def __init__(self):
        self.inside=0
        self.lst=[]
        self.floor=2
        self.cardnumber=[]
        self.on_win = None

    def move(self,card):
        self.inside-=1
        self.lst.remove(card)
        self.judge()
        
    def judge(self):
        if self.inside==0:
            # win()   
            # return 'win'
            print('win')
            if self.on_win is not None:
                print('in')
                self.on_win()
    
    def detect(self):
        """for i in range(len(pile.lst)):
            for j in range(len(pile.lst)):
                if i!=j:
                    if pile.lst[i].x-26<=pile.lst[j].x<=pile.lst[i].x+26 and pile.lst[i].y-26<=pile.lst[j].x<=pile.lst[i].y+26:
                        if pile.lst[j].floor<pile.lst[i].floor:
                            pile.lst[i].up.append(pile.lst[j])
                            pile.lst[j].below.append(pile.lst[i])
                        # elif pile.lst[j].floor>pile.lst[i].floor:
                        #     pile.lst[j].up.append(pile.lst[i])
                        #     pile.lst[i].below.append(pile.lst[j])

                        print(i,'below',pile.lst[i].below,'up',pile.lst[i].up)
                        print(j,'below',pile.lst[j].below,'up',pile.lst[j].up)"""
        
        for card in pile.lst:
            rect = card.btn.geometry()
            for other in self.lst:
                if other!=card:
                    rect1=other.btn.geometry()
                    if rect.intersects(rect1) and other.floor<self.floor:
                        card.up.append(other)
                        other.below.append(card)
    



    

pile=Pile()