from agent import *
from argument import *
from vectoreval import *
from attack import *
from argsys import *
from wargsys import *
import generate as gen
import sys

def was_from_file(f):
     with open(f, "r") as fd:
        l = fd.readlines()
        s = l[0].split(";")
        delta,epsilon = int(s[0]), float(s[1])
        s = l[1].split(";")
        nExpert, nAgent, nArgument, nAttack, nVotes = int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4])
        experts, agents, args, attacks, vectors = {}, {}, {}, {}, {}
        x, y = 2, 2
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
            vectors[s[2]].updateWeights( agents[s[1]], int(s[3]))
        w = AS(set(args.values()), set(attacks.values()))
        sysw = WAS(w, list(vectors.values()), delta, epsilon)
        return experts,agents,sysw


def main():
    args = sys.argv[1:]
    if (len(args)!=1 and len(args)!=6) :
        print("To execute, please use syntax:")
        print("IF fileName exists:")
        print("     python3 main.py fileName")
        print("OR generate with:")
        print("     python3 main.py fileName nAgents nExperts nTopics nArguments nAttacks")
        return
    if (len(args)==6) :
        print("generating WAS file...")
        gen.generate_file(args[0],int(args[1]),int(args[2]),int(args[3]),int(args[4]),int(args[5]))
    exp, ag, sysw = was_from_file(args[0])
    print("Delta: "+str(sysw.delta)+" | Epsilon: "+str(sysw.epsilon))
    print("\nAgents:")
    print(ag)
    print("\nExperts:")
    print(exp)
    print("\nArguments:")
    print(sysw.sys.arguments)
    print("\nAttacks:")
    print(sysw.sys.attacks)
    print("\nArg labels:")
    print(sysw.labels())
    print("\nAttack types:")
    print(sysw.attacks())
    print("\nExpert choisi:")
    print("Calcul en cours...")
    print(sysw.pick_expert(exp))
    sysw.show_graph()




if __name__ == "__main__":
    main()
