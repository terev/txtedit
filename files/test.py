result = 3
s = 2
c = 9
es=[True] * 300000000
es[0] = False
es[1] = False, False
num = 2
while num < 300000000:
    if es[num]:
        r=2
        index=0
        while r * num < 300000000:
            es[r * num] = False
            r+=1
    num += 1

print "done"
while(float(result) / (2*s+1) > .1):
    s += 2
    for i in range(3):
        c += s
        try:
            if es[c]:result+=1
        except:
            print c

    c += s
print s