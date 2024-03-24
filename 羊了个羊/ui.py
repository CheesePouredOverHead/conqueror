import sys
from PyQt6 import QtWidgets
from stack import stack,pile,Pile
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton,QLabel,QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QRect
from generate import generate
from PyQt6.QtWidgets import QMessageBox, QApplication,QDialogButtonBox
from PyQt6.QtCore import QCoreApplication,QTimer
from PyQt6.QtCore import Qt
import gc


class InputCapacity:
    def __init__(self,app):
        self.app=app
        self.w = QWidget()
        self.w.setWindowTitle('自定义设置')
        self.w.setFixedSize(500, 500)

        self.txt = QLabel('设置暂存区容量：', self.w)
        self.txt.move(50,40)
        self.txt.show()

        self.input = QtWidgets.QLineEdit(self.w)
        self.input.setGeometry(50,70,50,30)
        self.input.move(50,60)
        self.input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.input.show()
        self.input.editingFinished.connect(self.convey)

        self.txt2 = QLabel('设置层数：', self.w)
        self.txt2.move(50,120)
        self.txt2.show()

        self.input2 = QtWidgets.QLineEdit(self.w)
        self.input2.setGeometry(50,70,50,30)
        self.input2.move(50,140)
        self.input2.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.input2.show()
        self.input2.editingFinished.connect(self.convey2)

        self.label_3 = QLabel('从第1层开始每层牌数：', self.w)
        self.label_3.setGeometry(QRect(50, 180, 351, 16))
        self.label_3.show()

        self.label_4 = QLabel('注意：总数须为3的倍数，第i层数量不超过(i+1)^2，空格分隔',self.w)
        self.label_4.setGeometry(QRect(50, 200, 400, 16))
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        self.label_4.setFont(font)
        self.label_4.show()

        self.input3 = QtWidgets.QLineEdit(self.w)
        self.input3.setGeometry(50,70,150,30)
        self.input3.move(50,220)
        self.input3.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.input3.editingFinished.connect(self.convey3)
        self.input3.show()

        self.w.show()

    def convey(self):
        stack.capacity = int(self.input.text())

    def convey2(self):
        pile.floor = int(self.input2.text())

    def convey3(self):
        lst=list(map(int,self.input3.text().split()))
        if sum(lst)%3!=0 or len(lst)!=pile.floor or any(lst[i]>(i+2)**2 for i in range(pile.floor)):
            self.label_5 = QLabel('请重新输入', self.w)
            self.label_5.setGeometry(QRect(50, 250, 351, 16))
            self.label_5.show()
        else:
            pile.cardnumber=lst
            pile.inside=sum(lst)
            pile.setting=sum(lst)
            self.w.deleteLater()
            # self.app.deleteLater()
            QApplication.processEvents()


    def run(self):
        self.app.exec()

    def delete_all_widgets(self):
        for widget in self.w.findChildren(QWidget):
            widget.deleteLater()
        QApplication.processEvents()

class Play:
    def __init__(self,app):
        self.app=app

    def play(self):
        
        self.w = QWidget()
        self.w.setWindowTitle('羊了个羊')
        self.w.setFixedSize(500, 500)
        stackk=QLabel('',self.w)
        stackk.setFixedSize(50*stack.capacity,50)
        stackk.move(int((500-50*stack.capacity)/2),380)
        stackk.setStyleSheet("border: 2px solid black;")
        self.w.show()
        generate(self.w)

        
        self.app.exec()

    def win(self):
        print('win')
        self.label = QLabel('你赢了', self.w)
        self.label.setGeometry(QRect(190, 140, 120, 50))
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.show()

        """self.regame = QPushButton('再来一局',self.w)
        self.regame.setGeometry(QRect(210, 200, 80, 30))
        self.regame.clicked.connect(self.replay)
        self.regame.show()"""

        self.quit = QPushButton('退出程序',self.w)
        self.quit.setGeometry(QRect(210, 240, 80, 30))
        self.quit.show()
        self.quit.clicked.connect(QCoreApplication.quit)

    def lose(self):
        print('lose')
        self.label = QLabel('你输了', self.w)
        self.label.setGeometry(QRect(190, 140, 120, 50))
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: white;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.show()

        """self.regame = QPushButton('再来一局',self.w)
        self.regame.setGeometry(QRect(210, 200, 80, 30))
        self.regame.clicked.connect(self.replay)
        self.regame.show()"""

        self.quit = QPushButton('退出程序',self.w)
        self.quit.setGeometry(QRect(210, 240, 80, 30))
        self.quit.show()
        self.quit.clicked.connect(QCoreApplication.quit)

        