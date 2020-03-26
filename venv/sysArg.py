import networkx as nx
import matplotlib.pyplot as plt
import generate as gen
import random as rand
import itertools
from copy import deepcopy

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


class Argument:
    def __init__(self, topics, name):
        self.topics = topics
        self.name = name
        
    def __str__(self):
        return "Argument("+self.name+","+str(self.topics)+")"

    def __repr__(self) :
        return str(self)
    
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

    def affichetout(self):
        print("Prom are: ")
        print(self.prom)
        print("Rel are: ")
        print(self.rel)


class AS:
    def __init__(self, arguments, attacks):
        self.arguments = arguments
        self.attacks = attacks

    def __str__(self) :
        return "AS("+str(self.arguments)+","+str(self.attacks)+")"

    def __repr__(self) :
        return str(self)
        
    def Neighbours(self, a):
        t = []
        for att in self.attacks:
            if att.a.name == a.name:
                t.append(att.b)
        return t

    def notAttacked(self):
        t = []
        for a in self.arguments :
            b = False
            for att in self.attacks:
                if att.b.name == a.name:
                    b = True
                    break
            if not b:
                t.append(a)
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
        while len(noAtt) > 0:
            k = noAtt.pop()
            l[k.name] = "in"
            tmp = [k]
            visited = set()
            while len(tmp) > 0:
                x = tmp.pop()
                visited.add(x.name)
                for n in self.Neighbours(x):
                    if l[x.name] == "in":
                        l[n.name] = "out"
                        in_attacked.add(n.name)
                    elif l[x.name] == "out" and n.name not in in_attacked and l[n.name] != "in":
                        l[n.name] = "in"
                    if n.name not in visited:
                        tmp.append(n)
        return l


class WAS:
    def __init__(self, sys, v):
        self.sys = sys
        self.vectors = v

    def __str__(self) :
        return "WAS("+str(self.sys)+","+str(self.vectors)+")"
        
    def __repr__(self) :
        return str(self)
    
    def getVector(self, att):
        for v in self.vectors:
            if v.attack.name == att.name:
                return v
        return None
        
    def affichegraphe(self):
        G = nx.DiGraph()
        valueLabels = {}
        for arg in self.sys.arguments:
            G.add_node(arg.name)
        for att in self.sys.attacks:
            G.add_edge(att.a.name, att.b.name)
            tmp = self.getVector(att)
            valueLabels.update({(att.a.name, att.b.name): '<' + str(tmp.weight) + "," + str(tmp.maxWeight) + '>'})
        pos = nx.spring_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=valueLabels, font_color='red')
        nx.draw(G, pos, edge_color='black', length = 100, width=1,size=20, linewidths=1,
                node_size=300, node_color='pink', alpha=1,
                labels={node: node for node in G.nodes()}
                )
        plt.show()

    def counterpartAS(self):
        args = self.sys.arguments
        att = [v.attack for v in self.vectors if v.weight > 0]
        return AS(args, att)

    def labels(self):
        c = self.counterpartAS()
        return c.labels()

    def attacks(self, lmbda, epsilon):
        l = {"bd":[],"str":[],"wk":[]}
        for v in self.vectors:
            w, mw, t = v.weight, v.maxWeight, len(v.attack.top)
            if (w == 0 and mw == 0) or (float(mw)/float(t) > lmbda and float(abs(w))/float(mw) > epsilon):
                l["bd"].append(v.attack)
            elif (w > 0 and w-t > 0) or (w <= 0 and abs(w)-t >= 0):
                l["str"].append(v.attack)
            else:
                l["wk"].append(v.attack)
        return l

    def alternative_was(self,lmbda, epsilon):
        unstable = self.attacks(lmbda,epsilon)["wk"]
        n = len(unstable)
        subs = []
        while n > 0:
            subs += list(list(map(set, itertools.combinations(unstable, n))))
            n -= 1
        alts = [self]
        for sub in subs:
            new_was = deepcopy(self)
            for s in sub:
                v = new_was.getVector(s)
                if v.weight != 0 and s in unstable:
                    v.weight = - v.weight
                elif v.weight == 0:
                    v.weight = 1
            alts += [new_was]
        return alts

    def persistence(self, lmbda, epsilon):
        alts = self.alternative_was(lmbda,epsilon)
        l = {"pers":[], "not_pers":[]}
        labels = self.labels()
        ltmp = [a.labels() for a in alts]
        for arg in labels:    
            b = True
            for k in ltmp:
                if k[arg] != labels[arg]:
                    l["not_pers"].append(arg)
                    b = False
                    break
            if b:
                l["pers"].append(arg)
        return l

    def expert_vote(self, votes_expert, agent):
        # generate a possible was from one set of votes by an expert
        possible_was = deepcopy(self)
        for key,value in votes_expert.items():
            sign = value
            vector = self.getVector(key)
            votes(vector, agent, sign)
        return possible_was

    def get_all_possible_was_by_expert(self, lmbda, epsilon, expert):
        all_possible_was = []
        # get all weak and strong attacks that will be reviewed by the expert
        attacks = self.attacks(lmbda, epsilon)
        review_attacks = attacks["wk"] + attacks["str"]
        # get all possible combinations of votes, sous forme de liste de dictionnaires. Exemple:
        # [{'ab': 1, 'bc': 1, 'ac': 1}, {'ab': 1, 'bc': 1, 'ac': -1}, .... ]
        possible_votes = []
        values = ([[-1, 1]] * len(review_attacks))
        for row in itertools.product(*values):
            possible_votes.append(dict(zip(review_attacks, row)))
        # Iterate all possible votes list, generate a new WAS for each set of votes,
        # and add it to the list of possible WAS
        for vote in possible_votes:
            poss_was = self.expert_vote(vote, expert)
            all_possible_was.append(poss_was)
        return all_possible_was

    def single_attacks_stability(self, lmbda, epsilon, possible_was):
        attacks = self.attacks(lmbda, epsilon)
        new_attacks = possible_was.attacks(lmbda, epsilon)
        reinforced = [i for i in attacks["wk"] if i.name in list(map(lambda a:a.name,new_attacks["str"]))]
        weakened = [i for i in attacks["str"] if i.name in list(map(lambda a:a.name,new_attacks["wk"]))]
        return {"reinforced":reinforced,"weakened":weakened}

    def max_stability_possible_was(self,lmbda,epsilon,expert) :
        p = self.get_all_possible_was_by_expert(lmbda,epsilon,expert)
        max_stable = max(p,key=lambda was: len(self.single_attacks_stability(lmbda,epsilon,was)["reinforced"]))
        max_unstable = max(p,key=lambda was: len(self.single_attacks_stability(lmbda,epsilon,was)["weakened"]))
        return max_stable,max_unstable
        
    def single_labels_persistence(self,lmbda,epsilon,possible_was) :
        pers = self.persistence(lmbda,epsilon)
        new_pers = possible_was.persistence(lmbda,epsilon)
        turned_pers = [i for i in pers["not_pers"] if i in new_pers["pers"]]
        turned_not_pers = [i for i in pers["pers"] if i in new_pers["not_pers"]]
        return {"turned_pers":turned_pers,"turned_not_pers":turned_not_pers}

    def max_persistence_possible_was(self,lmbda,epsilon,expert) :
        p = self.get_all_possible_was_by_expert(lmbda,epsilon,expert)
        max_turned_pers = max(p,key=lambda was: len(self.single_labels_persistence(lmbda,epsilon,was)["turned_pers"]))
        max_turned_not_pers = max(p,key=lambda was: len(self.single_labels_persistence(lmbda,epsilon,was)["turned_not_pers"]))
        return max_turned_pers,max_turned_not_pers
        

def votes(vector, agent, sign):
    vector.updateWeights(agent, sign)


def was_from_file(f):
     with open(f, "r") as fd:
        l = fd.readlines()
        s = l[0].split(";")
        nExpert, nAgent, nArgument, nAttack, nVotes = int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4])
        experts, agents, args, attacks, vectors = {}, {}, {}, {}, {}
        x, y = 1, 1
        for i in range(nExpert):
            s = l[x+i].split(";")
            experts[s[0]] = Agent(s[0], set(s[1:-1]))
            y += 1
        x = y
        for i in range(nAgent):
            s = l[x+i].split(";")
            agents[s[0]] = Agent(s[0], set(s[1:-1]))
            y += 1
        x = y
        for i in range(nArgument):
            s = l[x+i].split(";")
            args[s[0]] = Argument(set(s[1:-1]), s[0])
            y += 1
        x = y
        for i in range(nAttack):
            s = l[x+i].split(";")
            a = Attack(args[s[1]], args[s[2]], s[0])
            attacks[s[0]] = a 
            vectors[s[0]] = VectorEval(a)
            y += 1
        x = y
        for i in range(nVotes):
            s = l[x+i].split(";")
            votes(vectors[s[2]], agents[s[1]], int(s[3]))
        w = AS(set(args.values()), set(attacks.values()))
        sysw = WAS(w, list(vectors.values()))
        return experts,agents,sysw


def main():
    exp, ag, sysw = was_from_file("example.txt")
    print("Experts:")
    print(exp)
    print("\nAgents:")
    print(ag)
    print("\nLabels:")
    print(sysw.labels())
    #l,e = rand.randint(0,3),rand.uniform(0,1)
    #print(l,e)
    print("\nAttack Types:")
    print(sysw.attacks(4, 0.5))
    #print(sysw.alternative_was(4,0.5))
    print("\nPersistent Arguments:")
    print(sysw.persistence(4,0.5))
    sysw.affichegraphe()
    possibles = sysw.get_all_possible_was_by_expert(4, 0.5, exp['Exp1'])
    print(len(possibles))
    #print(sysw.single_attacks_stability(4,0.5,possibles[1]))
    #print(sysw.single_labels_persistence(4,0.5,possibles[1]))
    print(sysw.max_stability_possible_was(4,0.5,exp['Exp1']))
    print(sysw.max_persistence_possible_was(4,0.5,exp['Exp1']))
    '''
    gen.generate_file("randomized.txt",5,3)
    exp, ag, was = was_from_file("example.txt")
    c = was.counterpartAS()
    
    print(c.labels())
    c.affichegraphe()
    '''
main()
