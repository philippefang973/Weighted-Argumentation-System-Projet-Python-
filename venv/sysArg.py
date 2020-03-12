import networkx as nx
import matplotlib.pyplot as plt


class Agent:
    def __init__(self, name, expertises):
        self.expertises = expertises
        self.name = name
        self.impact = {}

    def setImpact(self, a):
        interProm = self.expertises.intersection(a.prom)
        interRel = self.expertises.intersection(a.rel)
        i = 2*len(interProm)+len(interRel)
        self.impact.update({a.name: i})


class Argument:
    def __init__(self, topics, name):
        self.topics = topics
        self.name = name


class VectorEval:
    def __init__(self):
        self.weight = 0
        self.maxWeight = 0

    def updateWeights(self, a, v, at):
        self.weight += a.impact[at.name]*v
        notdummy = 0
        for value in at.votingAgents.values():
            if value > 0:
                notdummy += 1
        self.maxWeight = len(at.top)*notdummy


class Attack:
    def __init__(self, a, b, name):
        self.name = name
        self.a = a
        self.b = b
        self.votes = {}
        self.vectorEval = VectorEval()
        self.votingAgents = {}
        self.top = list(a.topics)+list(b.topics)
        self.prom = a.topics.intersection(b.topics)
        self.rel = (a.topics - b.topics).union(b.topics - a.topics)

    def affichetout(self):
        print("Prom are: ")
        print(self.prom)
        print("Rel are: ")
        print(self.rel)
        print("Agents impacts on this attack are:")
        print(self.votingAgents)
        print("Vector is: ")
        print("<"+str(self.vectorEval.weight)+","+str(self.vectorEval.maxWeight)+">")

    def addVote(self, a, v):
        self.votes.update({a:v})
        self.votingAgents.update({a.name:a.impact[self.name]})
        self.vectorEval.updateWeights(a, v, self)


class AS:
    def __init__(self, arguments, attacks):
        self.arguments = arguments
        self.attacks = attacks


class WAS:
    def __init__(self, sys):
        self.sys = sys
        self.labelOut = set()
        self.labelIn = set()
        for att in sys.attacks:
            if att.vectorEval.weight > 0:
                self.labelIn.add(att.a.name)
                self.labelOut.add(att.b.name)
        print("In labelled are:")
        print(self.labelIn)
        print("Out labelled are:")
        print(self.labelOut)

    def affichegraphe(self):
        G = nx.DiGraph()
        valueLabels = {}
        for arg in self.sys.arguments:
            G.add_node(arg.name)
        for att in self.sys.attacks:
            G.add_edge(att.a.name, att.b.name)
            valueLabels.update({(att.a.name, att.b.name): '<' + str(att.vectorEval.weight) + "," + str(att.vectorEval.maxWeight) + '>'})
        pos = nx.spring_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=valueLabels, font_color='red')
        nx.draw(G, pos, edge_color='black', length = 100, width=1,size=20, linewidths=1,
                node_size=300, node_color='pink', alpha=1,
                labels={node: node for node in G.nodes()}
                )

        plt.show()


def votes(agent, attack, vote):
    agent.setImpact(attack)
    attack.addVote(agent, vote)


def main():
    aman = Agent("aman", {"biology", "nutrition"})
    philippe = Agent("philippe", {"health", "psychology"})
    a = Argument({"nutrition", "health", "biology", "fitness"}, "a")
    c = Argument({"health",  "fitness"}, "c")
    b = Argument({"nutrition", "psychology"}, "b")
    d = Argument({"health", "fitness", "beauty"}, "d")
    e = Argument({"biology", "psychology", 'health'}, "e")
    ab = Attack(a, b, "ab")
    ac = Attack(a, c, "ac")
    de = Attack(d, e, "de")
    votes(aman, ab, 1)
    votes(philippe, ab, -1)
    votes(aman, ac, 1)
    votes(philippe, ac, -1)
    votes(aman, de, -1)
    votes(philippe, de, 1)
    w = AS({a, b, c, d, e}, {ab, ac, de})
    sysw = WAS(w)
    ab.affichetout()
    sysw.affichegraphe()

main()