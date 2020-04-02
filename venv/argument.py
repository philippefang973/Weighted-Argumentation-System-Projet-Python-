class Argument:
    def __init__(self, topics, name):
        self.topics = topics
        self.name = name
        
    def __str__(self):
        return "Argument("+self.name+","+str(self.topics)+")"

    def __repr__(self) :
        return str(self)
