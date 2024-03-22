import sys
from card import Card
from ui import InputCapacity,Play
from stack import stack,pile
from generate import *
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton

def main():
    app = QApplication(sys.argv)

    input_capacity=InputCapacity()
    input_capacity.run()
    
    """w = QWidget()
    w.setWindowTitle('羊了个羊')
    w.setFixedSize(500, 500)
    stackk=QLabel('',w)
    stackk.setFixedSize(50*stack.capacity,50)
    stackk.move(int((500-50*stack.capacity)/2),380)
    stackk.setStyleSheet("border: 2px solid black;")
    w.show()"""
    # play()
    begin=Play()
    begin.play()
    
    
    generate(begin.w)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()