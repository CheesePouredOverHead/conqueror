from card import Card
from stack import pile
import random

def generate(w):
    """
    生成所有card对象。

    参数：
    w (int)：所在的qwidgit

    返回：
    无

    """
    cards=all_card(pile)
    for floor in range(pile.floor,0,-1):
        if floor%2==1:
            this_floor=[(x,y) for x in range(100,351,50) for y in range(40,291,50)]
        else:
            this_floor=[(x,y) for x in range(75,376,50) for y in range(15,316,50)]
        random.shuffle(this_floor)
        for i in range(pile.cardnumber[floor-1]):
            pile.lst.append(Card(cards.pop(),floor,this_floor[i][0],this_floor[i][1],w))

    pile.detect()
    for card in pile.lst:
        card.display()
            
def all_card(pile):
    """
    生成所有card的号码。

    参数：
    pile (Pile)：一个Pile对象。
    
    返回：
    lst: 包含所有card号码的列表。

    """
    n = pile.setting 

    lst = []
    for i in range(10):
    # 为每个数生成一个随机的出现次数（是3的倍数）
        count = max(1, random.randint((n // 3 // 10) - 1, (n // 3 // 10) + 1)) * 3
    # 将这个数添加到列表中
        lst += [i] * count

    # 如果生成的列表的元素个数超过了 n，我们需要删除一些元素
    while len(lst)!=n:
        if len(lst) > n:
            lst = lst[:n]
        else:
            lst=lst+lst[:n-len(lst)]
    # print(lst)
    # 打乱列表的顺序
    random.shuffle(lst)
    return lst