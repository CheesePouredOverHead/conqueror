import sys
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont,QPolygonF
from PyQt6.QtCore import QPointF,Qt
from stack import stack,pile

class Card:
    def __init__(self,no,floor,x,y,window):
        self.no=no
        self.x=x
        self.y=y
        self.floor=floor
        self.window=window
        self.district='pile'
        self.btn=QPushButton(str(self.no),self.window)
        self.btn.setGeometry(self.x, self.y, 50, 50)
        self.up=[]
        self.below=[]

    def __lt__(self, other):
        return self.no < other.no

    def get_no(self):
        self.can_see()
        if not self.cansee:
            return '-1'
        else:
            return str(self.no)

    def display(self):
        self.can_see()
        self.btn.setText(self.get_no())
        font = QFont("Arial", 15)  # 创建字体对象，设置字体为Arial，大小为12
        self.btn.setFont(font)
        self.btn.setGeometry(self.x, self.y, 50, 50)
        self.btn.setStyleSheet('background-color:'+self.color(self.no))
        self.btn.show()
        self.btn.clicked.connect(self.being_clicked)

    def can_see(self):
        rect = self.btn.geometry()
        polygon=QPolygonF([QPointF(rect.topLeft()),QPointF(rect.topRight()),QPointF(rect.bottomRight()),QPointF(rect.bottomLeft())])
        points = [QPointF(0, 0)]
        superpolygon = QPolygonF(points)
        for other in self.up:
            rect1=other.btn.geometry()
            polygon1=QPolygonF([QPointF(rect1.topLeft()),QPointF(rect1.topRight()),QPointF(rect1.bottomRight()),QPointF(rect1.bottomLeft())])
            superpolygon=superpolygon.united(polygon1)

        if all(superpolygon.containsPoint(point, Qt.FillRule.OddEvenFill) for point in polygon):
            self.cansee=False
            return 0
        else:
            self.cansee=True
            return 1



    def color(self,no):
        dic={0:'white',1:'red',2:'blue',3:'orange',4:'yellow',\
             5:'seagreen',6:'blueviolet',7:'tomato',8:'cyan',9:'pink'}
        if self.cansee:
            return dic[no]
        else:
            return 'black'
        
    
    def being_clicked(self):
        if self.district=='pile' and self.up==[]:
            self.move()
    
    def move(self,index=None):
        self.x,self.y=stack.get_location(index)
        self.btn.move(self.x,self.y)
        
        if self.district=='pile':
            
            stack.add(self)
            pile.move(self)
            self.district='stack'
            for belows in self.below:
                belows.up.remove(self)
            for card in pile.lst:
                if card!=None:
                    card.display()


