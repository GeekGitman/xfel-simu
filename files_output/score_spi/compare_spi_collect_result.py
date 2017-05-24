#-*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:03:40 2016
This program convert lstc*.h5 to ave line. In parallel method.
@author: wang
"""

import h5py
import os
import numpy as np
import copy
import pdb

def one_proc(fname):
    fpath = "./outfiles/"
    f = open(fpath + fname,'r')
    if fname[-4:]!='.out':
        return 0
    num = 0.0
    ave = 0.0
    count  = 0
    nums = []
    print fname
    for diff in f.readlines():
        if '.' in diff:
            num = float(diff.strip())
            nums.append(num)
            count = count +1
    f.close()
    std = np.std(nums)
    print std
    ave = np.average(nums)
    nums = np.sort(nums)
    c = len(nums)
    return ave

files_all = os.listdir('./outfiles/')
for fname in files_all:
    if fname[-3:] != 'out':
        files_all.remove(fname)
        continue
files_t = copy.deepcopy(files_all)

f = open("spi.csv",'w')
for fname in files_t:
    ave = one_proc(fname)
    f.write(fname[4:-4]+','+str(ave)+'\n')
