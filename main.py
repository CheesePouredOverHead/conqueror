import sys
from ui import Setting,Play
from stack import stack,pile
from generate import *
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    setting=Setting(app)
    setting.run()
    
    begin=Play(app)
    pile.on_win=begin.win
    stack.on_lose=begin.lose
    begin.play()
    
    app.exit()
    
if __name__ == '__main__':
    main()