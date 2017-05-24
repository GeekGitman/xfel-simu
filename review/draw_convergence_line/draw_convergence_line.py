import h5py
import os
import numpy as np
import pickle as pkl

f = open("NumberVsRMSD.dat",'r')
d = dict()
for line in f.readlines():
    ind,rmsd = line.strip().split(',')
    ind = int(ind)
    d[ind] = rmsd
f.close()

fpath = "./alllstc/"
flist = os.listdir(fpath)

fh = h5py.File(fpath+'lstc1.h5')
std = fh['pattern'][()]
fh.close()

patt = []
difflst = []
alldiff = []
lrmsd = []
for item in flist:
    aname = fpath+item
    print item
    num = int(item[4:-3])
    if num == 1:
        continue
    lrmsd.append(d[num-1])
    p = h5py.File(aname)['pattern'][()]
    difflst = []
    for n in range(2004):
        diff = np.linalg.norm(p[n]-std[n],ord=2)
        difflst.append(diff)
    np.random.shuffle(difflst)
    alldiff.append(difflst)

allave = []
print 'calc ave'
for prot in range(len(alldiff)):
    avelst = []
    for n in range(2000):
        ave2 = np.mean(alldiff[prot][:n])
        avelst.append(ave2)
    allave.append(avelst)

pkl.dump((lrmsd,allave),open('allave.pkl','w'))

