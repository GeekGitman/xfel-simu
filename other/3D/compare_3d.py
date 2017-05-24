import os
import numpy as np
import h5py

def compare(std,name):
    a = h5py.File(name)
    arr = a['patt'][()]
    diff = np.linalg.norm(std-arr)
    print name[19:-3] +',' + str(diff)

std = h5py.File('./output/re_space_c0.h5')
std = std['patt'][()]
fnames = ['./output/' + i for i in os.listdir('./output/')]
for name in fnames:
    compare(std,name)

