from card import Card
from stack import pile
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton,QLabel,QHBoxLayout
import random

def generate(w):
    
    """for i in range(4):
        pile.lst.append(Card(1,2,75+50*i,75,w))
        pile.inside+=1
    for i in range(5):
        pile.lst.append(Card(1,1,50+50*i,50,w))
        pile.inside+=1
    pile.detect()
    layout = QHBoxLayout()
    for x in range(pile.floor,0,-1):
        for card in pile.lst:
            if card.floor==x:
                card.display()"""
    cards=all_card()
    for floor in range(pile.floor,0,-1):
        this_floor=[(x,y) for x in range(225-floor*25,225-floor*25+50*floor+1,50) for y in range(165-25*floor,165-25*floor+50*floor+1,50)]
        random.shuffle(this_floor)
        for i in range(pile.cardnumber[floor-1]):
            pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],w))

    pile.detect()
    for card in pile.lst:
        card.display()
            
def all_card():
    n = pile.inside  # 请根据实际情况修改这个值

    lst = []
    for i in range(10):
    # 为每个数生成一个随机的出现次数（是3的倍数）
        count = max(1, random.randint((n // 3 // 10) - 1, (n // 3 // 10) + 1)) * 3
    # 将这个数添加到列表中
        lst += [i] * count

# 如果生成的列表的元素个数超过了 n，我们需要删除一些元素
    if len(lst) > n:
        lst = lst[:n]

    # 打乱列表的顺序
    random.shuffle(lst)
    return lst