from attack import *
class VectorEval:
    def __init__(self, a):
        self.attack = a
        self.weight = 0
        self.maxWeight = 0

    def __str__(self) :
        return "VectoEval("+str(self.attack)+","+str(self.weight)+","+str(self.maxWeight)+")"
    
    def __repr__(self) :
        return str(self)

    def updateWeights(self, a, sign):
        i = a.getImpact(self.attack)
        if i != 0:
            self.weight += i*sign
            self.maxWeight += len(self.attack.top)
