import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import itertools
from copy import deepcopy
from argument import *
from attack import *

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

