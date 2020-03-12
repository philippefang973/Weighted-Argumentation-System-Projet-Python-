import random as rand

def random_partition(l) :
    s = set(l)
    res = []
    while(len(s)>0) :
        tmp = set(rand.sample(s,rand.randint(1,len(s))))
        res.append(list(tmp))
        s = s-tmp
    return res

def generate_was(f) :
    #Data generation
    nAgent = rand.randint(5,15)
    top = range(rand.randint(nAgent,nAgent*2))
    agents = [rand.sample(top,rand.randint(1,5)) for i in range(nAgent)]
    arguments = [random_partition(l) for l in agents]
    ind = []
    nArgument = 0
    for i in arguments :
        tmp = []
        for j in i : 
            tmp.append(nArgument)
            nArgument+=1
        ind.append(tmp)
    attacks = []
    for i in range(nArgument) :
         for j in rand.sample(range(nArgument),rand.randint(0,nArgument)) :
             if i!=j : attacks.append((i,j))

    votes = []
    for i in range(nAgent) :
        for j in range(len(attacks)) :
            votes.append((i,j,1 if attacks[j][0] in ind[i] else rand.choice([1,-1])))
            
    #File writing
    with open(f,"w+") as fd :
        fd.write(str(nAgent)+";"+str(nArgument)+";"+str(len(attacks))+";"+str(len(votes))+";\n")
        for i in range(nAgent) :
            fd.write("agent"+str(i)+";")
            for j in agents[i] :
                fd.write("topic"+str(j)+";")
            fd.write("\n")
        x = 0
        for i in range(len(arguments)) :
            for j in arguments[i] :
                fd.write("argument"+str(x)+";")
                for k in j :
                    fd.write("topic"+str(k)+";")
                x+=1
                fd.write("\n")
        for i in range(len(attacks)) :
            fd.write("attack"+str(i)+";argument"+str(attacks[i][0])+";argument"+str(attacks[i][1])+";\n")
        for i in range(len(votes)) :
            fd.write("vote"+str(i)+";agent"+str(votes[i][0])+";attack"+str(votes[i][1])+";"+str(votes[i][2])+";\n")
           
generate_was("randomized.txt")
