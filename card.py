import sys
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont,QPolygonF
from PyQt6.QtCore import QPointF,Qt
from stack import stack,pile

class Card:
    def __init__(self, no, floor, x, y, window):
        """
        初始化卡片对象。

        Args:
            no (int): 卡片编号。
            floor (int): 卡片所在层。
            x (int): 卡片的横坐标。
            y (int): 卡片的纵坐标。
            window (QWidget): 卡片所在的窗口。

        Attributes:
            no (int): 卡片编号。
            x (int): 卡片的横坐标。
            y (int): 卡片的纵坐标。
            floor (int): 卡片所在楼层。
            window (QWidget): 卡片所在的窗口。
            district (str): 卡片所在的区域。
            btn (QPushButton): 卡片的按钮。
            up (list): 卡片上方的卡片列表。
            below (list): 卡片下方的卡片列表。
        """
        self.no = no
        self.x = x
        self.y = y
        self.floor = floor
        self.window = window
        self.district = 'pile'
        self.btn = QPushButton(str(self.no), self.window)
        self.btn.setGeometry(self.x, self.y, 50, 50)
        self.up = []
        self.below = []

    def __lt__(self, other):
        """
        比较两个卡片的大小。

        Args:
            other (Card): 另一个卡片对象。

        Returns:
            bool: 如果当前卡片的编号小于另一个卡片的编号，则返回True，否则返回False。
        """
        return self.no < other.no

    def get_no(self):
        """
        获取卡片的编号。

        Returns:
            str: 卡片的编号，如果卡片不可见，则返回'-1'。
        """
        self.can_see()
        if not self.cansee:
            return '-1'
        else:
            return str(self.no)

    def display(self):
        """
        显示卡片。

        Updates:
            - 设置卡片按钮的文本为卡片的编号。
            - 设置卡片按钮的字体和样式。
            - 显示卡片按钮。
            - 连接卡片按钮的点击事件到being_clicked方法。
        """
        self.can_see()
        self.btn.setText(self.get_no())
        font = QFont("Arial", 15)
        self.btn.setFont(font)
        self.btn.setGeometry(self.x, self.y, 50, 50)
        self.btn.setStyleSheet('background-color:' + self.color(self.no))
        self.btn.show()
        self.btn.clicked.connect(self.being_clicked)

    def can_see(self):
        """
        判断卡片是否可见。

        Returns:
            int: 如果卡片可见，则返回1，否则返回0。
        """
        rect = self.btn.geometry()
        polygon = QPolygonF([QPointF(rect.topLeft()), QPointF(rect.topRight()), QPointF(rect.bottomRight()), QPointF(rect.bottomLeft())])
        points = [QPointF(0, 0)]
        superpolygon = QPolygonF(points)
        for other in self.up:
            rect1 = other.btn.geometry()
            polygon1 = QPolygonF([QPointF(rect1.topLeft()), QPointF(rect1.topRight()), QPointF(rect1.bottomRight()), QPointF(rect1.bottomLeft())])
            superpolygon = superpolygon.united(polygon1)

        if all(superpolygon.containsPoint(point, Qt.FillRule.OddEvenFill) for point in polygon):
            self.cansee = False
            return 0
        else:
            self.cansee = True
            return 1

    def color(self, no):
        """
        根据卡片的编号返回对应的颜色。

        Args:
            no (int): 卡片编号。

        Returns:
            str: 卡片的颜色，如果卡片不可见，则返回'black'。
        """
        dic = {0: 'white', 1: 'red', 2: 'blue', 3: 'orange', 4: 'yellow', 5: 'seagreen', 6: 'blueviolet', 7: 'tomato', 8: 'cyan', 9: 'pink'}
        if self.cansee:
            return dic[no]
        else:
            return 'black'

    def being_clicked(self):
        """
        处理卡片按钮的点击事件。

        Updates:
            - 如果卡片所在区域为'pile'且上方没有其他卡片，则调用move方法。
        """
        if self.district == 'pile' and self.up == []:
            self.move()

    def move(self, index=None):
        """
        移动卡片到指定位置。

        Args:
            index (int, optional): 移动到的位置索引。默认为None。

        Updates:
            - 更新卡片的横纵坐标。
            - 移动卡片按钮到新的位置。
            - 如果卡片所在区域为'pile'，则将卡片添加到堆栈中，并更新堆栈和堆叠区域的显示。
            - 更新卡片所在区域为'stack'。
            - 移除卡片下方卡片列表中的当前卡片。
            - 显示堆栈中的所有卡片。
        """
        self.x, self.y = stack.get_location(index)
        self.btn.move(self.x, self.y)

        if self.district == 'pile':
            stack.add(self)
            pile.move(self)
            self.district = 'stack'
            for belows in self.below:
                belows.up.remove(self)
            for card in pile.lst:
                if card != None:
                    card.display()


