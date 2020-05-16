import random as rand
import itertools as it

def generate_file(f,nAg,nEx,nTop,nArg,nAtt) :
    #Data generation
    l,e = rand.randint(0,nAg),rand.uniform(0,1)

    top = [i for i in range(nTop)]
    arguments = [rand.sample(top,rand.randint(1,nTop)) for i in range(nArg)] 
    agents = [rand.sample(top,rand.randint(1,nTop)) for i in range(nAg)]
    experts = [rand.sample(top,rand.randint(1,nTop)) for i in range(nEx)]

    couple = list(it.product([i for i in range(nArg)],repeat=2))
    cc = [i for i in couple if i[0]!=i[1]]
    attacks = rand.sample(cc,nAtt)

    votes = []
    for i in range(nAg) :
        for j in range(nAtt) :
            k = rand.choice([1,-1,0])
            if k!=0 :
                votes.append((i,j,k))
            
    #File writing
    with open(f,"w+") as fd :
        fd.write(str(l)+";"+str(e)+";\n")
        fd.write(str(nEx)+";"+str(nAg)+";"+str(nArg)+";"+str(nAtt)+";"+str(len(votes))+";\n")
        for i in range(nEx) :
            fd.write("expert"+str(i)+";")
            for j in experts[i] :
                fd.write("topic"+str(j)+";")
            fd.write("\n")
        for i in range(nAg) :
            fd.write("agent"+str(i)+";")
            for j in agents[i] :
                fd.write("topic"+str(j)+";")
            fd.write("\n")
        for i in range(nArg) :
            fd.write("argument"+str(i)+";")
            for j in arguments[i] :
                fd.write("topic"+str(j)+";")
            fd.write("\n")
        for i in range(len(attacks)) :
            fd.write("attack"+str(i)+";argument"+str(attacks[i][0])+";argument"+str(attacks[i][1])+";\n")
        for i in range(len(votes)) :
            fd.write("vote"+str(i)+";agent"+str(votes[i][0])+";attack"+str(votes[i][1])+";"+str(votes[i][2])+";\n")
