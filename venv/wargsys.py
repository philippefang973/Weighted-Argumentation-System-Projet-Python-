import networkx as nx
import matplotlib.pyplot as plt
import random as rand
import itertools
from copy import deepcopy
from argsys import *

class WAS:
    def __init__(self, sys, v, l, e):
        self.sys = sys
        self.vectors = v
        self.lmbda = l
        self.epsilon = e

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

    def attacks(self):
        l = {"bd":[],"str":[],"wk":[]}
        for v in self.vectors:
            w, mw, t = v.weight, v.maxWeight, len(v.attack.top)
            if (w == 0 and mw == 0) or (float(mw)/float(t) > self.lmbda and float(abs(w))/float(mw) > self.epsilon):
                l["bd"].append(v.attack)
            elif (w > 0 and w-t > 0) or (w <= 0 and abs(w)-t >= 0):
                l["str"].append(v.attack)
            else:
                l["wk"].append(v.attack)
        return l

    def alternative_was(self):
        unstable = self.attacks()["wk"]
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

    def persistence(self):
        alts = self.alternative_was()
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
            vector = possible_was.getVector(key)
            vector.updateWeights(agent, sign)
        return possible_was

    def get_all_possible_was_by_expert(self,expert):
        all_possible_was = set()
        # get all weak and strong attacks that will be reviewed by the expert
        attacks = self.attacks()
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
            all_possible_was.add(poss_was)
        res = list(all_possible_was)
        return res

    def single_attacks_stability(self,possible_was):
        attacks = self.attacks()
        new_attacks = possible_was.attacks()
        reinforced = [i for i in attacks["wk"] if i.name in list(map(lambda a:a.name,new_attacks["str"]))]
        weakened = [i for i in attacks["str"] if i.name in list(map(lambda a:a.name,new_attacks["wk"]))]
        return {"reinforced":reinforced,"weakened":weakened}


    def max_stability_possible_was(self,expert) :
        p = self.get_all_possible_was_by_expert(expert)
        max_stable = max(p,key=lambda was: len(self.single_attacks_stability(was)["reinforced"]))
        max_unstable = max(p,key=lambda was: len(self.single_attacks_stability(was)["weakened"]))
        return max_stable,max_unstable
        
    def single_labels_persistence(self,possible_was) :
        pers = self.persistence()
        new_pers = possible_was.persistence()
        turned_pers = [i for i in pers["not_pers"] if i in new_pers["pers"]]
        turned_not_pers = [i for i in pers["pers"] if i in new_pers["not_pers"]]
        return {"turned_pers":turned_pers,"turned_not_pers":turned_not_pers}

    def max_persistence_possible_was(self,expert) :
        p = self.get_all_possible_was_by_expert(expert)
        max_turned_pers = max(p,key=lambda was: len(self.single_labels_persistence(was)["turned_pers"]))
        max_turned_not_pers = max(p,key=lambda was: len(self.single_labels_persistence(was)["turned_not_pers"]))
        return max_turned_pers,max_turned_not_pers

    def reinforce_dominate(self, i, j):
        max_stable_i, max_unstable_i = self.max_stability_possible_was(i)
        max_stable_j, max_unstable_j = self.max_stability_possible_was(j)

        Rstable_i = set(self.single_attacks_stability(max_stable_i)["reinforced"])
        Rstable_j = set(self.single_attacks_stability(max_stable_j)["reinforced"])
        Runstable_i = set(self.single_attacks_stability(max_unstable_i)["weakened"])
        Runstable_j = set(self.single_attacks_stability(max_unstable_j)["weakened"])
        
        res = {"more_reinforce":set(),"less_weaken":set()}
        dom = 0
        res["more_reinforce"] = Rstable_i-Rstable_j
        res["less_weaken"] = Runstable_j-Runstable_i
        if len(res["more_reinforce"])>0 : dom+=1
        if len(res["less_weaken"])>0 : dom+=1
        return res,dom

    def persist_dominate(self, i, j):
        max_turned_pers_i, max_turned_not_pers_i = self.max_persistence_possible_was(i)
        max_turned_pers_j, max_turned_not_pers_j = self.max_persistence_possible_was(j)

        Rpers_i = set(self.single_labels_persistence(max_turned_pers_i)["turned_pers"])
        Rpers_j = set(self.single_labels_persistence(max_turned_pers_j)["turned_pers"])
        Runpers_i = set(self.single_labels_persistence(max_turned_not_pers_i)["turned_not_pers"])
        Runpers_j = set(self.single_labels_persistence(max_turned_not_pers_j)["turned_not_pers"])

        res = {"more_turn_pers":set(),"less_turn_non_pers":set()}
        dom = 0
        res["more_turn_pers"] = Rpers_i-Rpers_j
        res["less_turn_non_pers"] =  Runpers_j-Runpers_i
        if len(res["more_turn_pers"])>0 : dom+=1
        if len(res["less_turn_non_pers"])>0 : dom+=1
        return res,dom

    def pick_expert(self,experts) :
        a = None
        score = 0
        for x in list(experts) :
            s = 0
            for y in list(experts) :               
                if x!=y:
                    r,domR = self.reinforce_dominate(experts[x],experts[y])
                    p,domP = self.persist_dominate(experts[x],experts[y])
                    s+=domR+domP
            print("score de "+x+": "+str(s))
            if s>score :
                score = s
                a = experts[x]
        return a
        
