class Agent:
    def __init__(self, name, expertises):
        self.expertises = expertises
        self.name = name

    def __str__(self) :
        return "Agent("+self.name+","+str(self.expertises)+")"
    
    def __repr__(self) :
        return str(self)

    def getImpact(self, att):
        interProm = self.expertises.intersection(att.prom)
        interRel = self.expertises.intersection(att.rel)
        i = 2*len(interProm)+len(interRel)
        return i
