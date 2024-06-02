class Stack:
    """表示一个堆栈的类。

    Attributes:
        capacity (int): stack的容量。
        inside (int): stack中当前的元素数量。
        dic (dict): 存储stack中不同号码的牌的索引的字典。
        lst (list): 存储卡片对象的列表。
        on_lose (function): 当stack满时触发的回调函数。
    """

    def __init__(self, capacity):
        """初始化。

        Args:
            capacity (int): 堆栈的容量。
        """
        self.capacity = capacity
        self.inside = 0
        self.dic = {i: [] for i in range(10)}
        self.lst = []
        self.on_lose = None

    def get_location(self, index=None):
        """获取指定索引的卡片位置。

        Args:
            index (int, optional): 要获取位置的卡片索引。如果未提供索引，则默认为当前内部索引。

        Returns:
            tuple: 包含卡片位置的元组，格式为 (x, y)。
        """
        if index is None:
            index = self.inside
        return int((500 - 50 * self.capacity) / 2 + 50 * index), 380

    def add(self, card):
        """向stack中添加卡片。

        Args:
            card (Card): 要添加的卡片对象。
        """
        self.dic[card.no] += [self.inside]
        self.lst += [card]
        if len(self.dic[card.no]) == 3:
            self.eliminate(self.dic[card.no])
            self.inside -= 2
            self.dic[card.no] = []
        else:
            self.inside += 1
        self.judge()

    def judge(self):
        """判断stack是否已满，如果满则触发 on_lose 回调函数。"""
        if self.inside >= self.capacity:
            self.on_lose()

    def eliminate(self, to_delete):
        """从stack中删除指定的卡片。

        Args:
            to_delete (list): 要删除的卡片索引列表。
        """
        for index in to_delete:
            self.lst[index].btn.hide()

        self.lst = [self.lst[i] for i in range(len(self.lst)) if i not in to_delete]
        for no, indices in self.dic.items():
            self.dic[no] = [i for i in indices if i not in to_delete]
            self.dic[no] = [i - len([j for j in to_delete if j < i]) for i in self.dic[no]]
        for index_after in range(len(self.lst)):
            self.lst[index_after].move(index_after)
#暂存区默认设为7，后续再自定义
stack=Stack(7) 

class Pile:
    """表示一堆牌的类。

    Attributes:
        inside (int): 表示堆内的牌数。
        setting (int): 表示设置的值。
        lst (list): 表示堆内的牌列表。
        floor (int): 表示堆的楼层。
        on_win (function): 表示当堆内没有牌时触发的回调函数。
        cardnumber (list): 表示牌的编号列表。
    """

    def __init__(self):
        self.inside = 0
        self.setting = 0
        self.lst = []
        self.floor = 2
        self.on_win = None
        self.cardnumber = []

    def move(self, card):
        """移动一张牌。

        Args:
            card: 要移动的牌对象。
        """
        self.inside -= 1
        lst = [other if card != other else None for other in self.lst]
        self.lst = lst
        self.judge()

    def judge(self):
        """判断堆内是否没有牌，并触发相应的回调函数。"""
        if self.inside == 0:
            self.on_win()

    def detect(self):
        """检测牌与其他牌的位置关系。"""
        for card in self.lst:
            rect = card.btn.geometry()
            for other in self.lst:
                if other.floor < card.floor:
                    rect1 = other.btn.geometry()
                    if rect.intersects(rect1):
                        card.up.append(other)
                        other.below.append(card)
    
pile=Pile()