class Stack:
    def __init__(self,capacity):
        self.capacity=capacity
        self.inside=0
        self.dic={i:[] for i in range(10)}
        self.lst=[]
        self.on_lose = None

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

        
    def judge(self):
        if self.inside>=self.capacity:
            self.on_lose()
            


    def eliminate(self,to_delete):
        for index in to_delete:
            self.lst[index].btn.deleteLater()
        self.lst = [self.lst[i] for i in range(len(self.lst)) if i not in to_delete]
        for no, indices in self.dic.items():
            self.dic[no] = [i for i in indices if i not in to_delete]
            self.dic[no] = [i - len([j for j in to_delete if j < i]) for i in self.dic[no]]
        for index_after in range(len(self.lst)):
            self.lst[index_after].move(index_after)

#暂存区默认设为7，后续再自定义
stack=Stack(7)

class Pile:
    def __init__(self):
        self.inside=0
        self.setting=0
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
            self.on_win()
    
    def detect(self):
        for card in pile.lst:
            rect = card.btn.geometry()
            for other in self.lst:
                if other.floor<card.floor:
                    rect1=other.btn.geometry()
                    if rect.intersects(rect1) :
                        card.up.append(other)
                        other.below.append(card)
    
pile=Pile()