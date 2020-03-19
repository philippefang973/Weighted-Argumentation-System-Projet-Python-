import networkx as nx
import matplotlib.pyplot as plt
import generate as gen
import random as rand

class Agent:
    def __init__(self, name, expertises):
        self.expertises = expertises
        self.name = name

    def getImpact(self, att):
        interProm = self.expertises.intersection(att.prom)
        interRel = self.expertises.intersection(att.rel)
        i = 2*len(interProm)+len(interRel)
        return i


class Argument:
    def __init__(self, topics, name):
        self.topics = topics
        self.name = name


class VectorEval:
    def __init__(self,a):
        self.attack = a
        self.weight = 0
        self.maxWeight = 0
        
    def updateWeights(self, a, sign):
        i = a.getImpact(self.attack)
        if i != 0 : 
            self.weight += i*sign
            self.maxWeight += len(self.attack.top)

class Attack:
    def __init__(self, a, b, name):
        self.name = name
        self.a = a
        self.b = b
        self.top = list(a.topics)+list(b.topics)
        self.prom = a.topics.intersection(b.topics)
        self.rel = (a.topics - b.topics).union(b.topics - a.topics)

    def affichetout(self):
        print("Prom are: ")
        print(self.prom)
        print("Rel are: ")
        print(self.rel)


class AS:
    def __init__(self, arguments, attacks):
        self.arguments = arguments
        self.attacks = attacks

    def Neighbours(self,a) :
        t = []
        for att in self.attacks :
            if att.a.name==a.name : t.append(att.b)
        return t

    def notAttacked(self) :
        t = []
        for a in self.arguments :
            b = False
            for att in self.attacks :
                if att.b.name==a.name :
                    b = True
                    break
            if not b : t.append(a)
        return t
                 
    def affichegraphe(self):
        G = nx.DiGraph()
        for arg in self.arguments:
            G.add_node(arg.name)
        for att in self.attacks:
            G.add_edge(att.a.name, att.b.name)
        pos = nx.spring_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels={}, font_color='red')
        nx.draw(G, pos, edge_color='black', length = 100, width=1,size=20, linewidths=1,
                node_size=300, node_color='pink', alpha=1,
                labels={node: node for node in G.nodes()}
                )
        plt.show()

    def labels(self):
        l = {x.name:"und" for x in self.arguments}
        noAtt = self.notAttacked()
        in_attacked = set()
        while len(noAtt)>0 :
            k = noAtt.pop()
            l[k.name] = "in"
            tmp = [k]
            visited = set()
            while len(tmp)>0 :
                x = tmp.pop()
                visited.add(x.name)
                for n in self.Neighbours(x) :
                    if l[x.name] == "in" :
                        l[n.name] = "out"
                        in_attacked.add(n.name)
                    elif l[x.name] == "out" and n.name not in in_attacked and l[n.name]!="in": l[n.name] = "in"
                    if n.name not in visited : tmp.append(n)
        return l
    
class WAS:
    def __init__(self,sys,v):
        self.sys = sys
        self.vectors = v

    def getAttack(self,att) :
        for v in self.vectors :
            if v.attack.name == att.name :
                return v
        return None
        
    def affichegraphe(self):
        G = nx.DiGraph()
        valueLabels = {}
        for arg in self.sys.arguments:
            G.add_node(arg.name)
        for att in self.sys.attacks:
            G.add_edge(att.a.name, att.b.name)
            tmp = self.getAttack(att)
            valueLabels.update({(att.a.name, att.b.name): '<' + str(tmp.weight) + "," + str(tmp.maxWeight) + '>'})
        pos = nx.spring_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=valueLabels, font_color='red')
        nx.draw(G, pos, edge_color='black', length = 100, width=1,size=20, linewidths=1,
                node_size=300, node_color='pink', alpha=1,
                labels={node: node for node in G.nodes()}
                )
        plt.show()

    def counterpartAS(self):
        args=self.sys.arguments
        att=[v.attack for v in self.vectors if v.weight>0]
        return AS(args,att)

    def labels(self) :
        c = self.counterpartAS()
        return c.labels()

    def attacks(self,lmbda,epsilon) :
        l = {}
        for v in self.vectors :
            w,mw,t = v.weight,v.maxWeight,len(v.attack.top)
            if (w==0 and mw==0) or (float(mw)/float(t)>lmbda and float(abs(w))/float(mw)>epsilon) :
                l["("+v.attack.a.name+","+v.attack.b.name+")"] = "bd"
            elif (w>0 and w-t>0) or (w<=0 and abs(w)-t>=0) :
                l["("+v.attack.a.name+","+v.attack.b.name+")"] = "str"
            else :
                l["("+v.attack.a.name+","+v.attack.b.name+")"] = "wk"
        return l


def votes(vector,agent,sign):
    vector.updateWeights(agent,sign)

def generate_was(n) :
     gen.generate_file("randomized.txt",n)
     with open("randomized.txt","r") as fd :
        l = fd.readlines()
        s = l[0].split(";")
        nAgent,nArgument,nAttack,nVotes = int(s[0]),int(s[1]),int(s[2]),int(s[3])
        agents,args,attacks,vectors=[],[],[],[]
        x,y = 1,1
        for i in range(nAgent):
            s = l[x+i].split(";")
            agents.append(Agent(s[0],set(s[1:-1])))
            y+=1
        x = y
        for i in range(nArgument):
            s = l[x+i].split(";")
            args.append(Argument(set(s[1:-1]),s[0]))
            y+=1
        x = y
        for i in range(nAttack):
            s = l[x+i].split(";")
            a = Attack(args[int(s[1])],args[int(s[2])],s[0])
            attacks.append(a)
            vectors.append(VectorEval(a))
            y+=1
        x = y
        for i in range(nVotes):
            s = l[x+i].split(";")
            votes(vectors[int(s[2])],agents[int(s[1])],int(s[3]))
        w = AS(set(args),set(attacks))
        sysw = WAS(w,vectors)
        return sysw


def main():
    PC1 = Agent("PC1",{"kr","cog"})
    PC2 = Agent("PC2",{"kr","comp"})
    PC3 = Agent("PC3",{"comp","ml"})
    a = Argument({"kr","cog"},"a")
    b = Argument({"comp"},"b")
    c = Argument({"comp","ml"},"c")
    d = Argument({"kr"},"d")
    ba = Attack(b,a,"ba")
    da = Attack(d,a,"da")
    cb = Attack(c,b,"cb")
    w = AS({a,b,c,d},{ba,da,cb})
    vba = VectorEval(ba)
    vda = VectorEval(da)
    vcb = VectorEval(cb)
    votes(vcb,PC1,-1)
    votes(vcb,PC2,1)
    votes(vcb,PC3,1)
    votes(vba,PC2,1)
    votes(vba,PC1,-1)
    votes(vba,PC3,-1)
    votes(vda,PC2,1)
    vectors = [vba,vda,vcb]
    sysw = WAS(w,vectors)
    print(sysw.labels())
    #l,e = rand.randint(0,3),rand.uniform(0,1)
    #print(l,e)
    print(sysw.attacks(4,0.5))
    sysw.affichegraphe()
    #sysw.counterpartAS().affichegraphe()
'''
    was = generate_was(5)
    c = was.counterpartAS()
    print(c.labels())
    c.affichegraphe()
'''
main()
