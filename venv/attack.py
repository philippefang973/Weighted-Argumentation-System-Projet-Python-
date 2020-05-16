class Attack:
    def __init__(self, a, b, name):
        self.name = name
        self.a = a
        self.b = b
        self.top = list(a.topics)+list(b.topics)
        self.prom = a.topics.intersection(b.topics)
        self.rel = (a.topics - b.topics).union(b.topics - a.topics)

    def __str__(self) :
        return "Attack("+str(self.a)+","+str(self.b)+")"

    def __repr__(self) :
        return str(self)

    def print(self):
        print("Prom are: ")
        print(self.prom)
        print("Rel are: ")
        print(self.rel)
