# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 13:17:42 2016
Paralize calculate distance of random orientation

customizable parameters:
    num = 1500
    numx = 100
    ncpus = 19@tianhe 23@sun 2@test
    (length of filelist)

@author: wang
"""

import os
import time
import h5py
import numpy as np
import multiprocessing
from functools import partial

def paraSetup(numthreads=None):
    """Setup parallel environment"""
    det_numthreads = multiprocessing.cpu_count()
    if numthreads == None:
        use_numthreads = det_numthreads
    else:
        use_numthreads = max(det_numthreads, numthreads)
    print('Detected {0} cores, using {1} threads'.format(det_numthreads, use_numthreads))
    pool = multiprocessing.Pool(processes=use_numthreads)
    return pool, use_numthreads


def print_PID(num):
    PID = os.getpid()
    print('Thread:', num, 'PID:', PID, ' is using.')


def compare(fname, s1,a1, s1_name):
    """compare 2 files"""
    # initial Environment
    print('PID:',os.getpid(),' is calculating file', fname)
    ffname = 'log_'+fname.split('/')[-1][4:-3] + '.txt'
    min_diff = []
    min_j = []

    # read h5 file
    print(fname)
    hx = h5py.File(fname, 'r')
    sx = hx['corr'].value
    ax = hx['angle'].value
    numx = len(sx)
    num = len(s1)

    if not os.path.exists('./corrlog_mis/'):
        os.mkdir('./corrlog_mis')
    f = open('./corrlog_mis/'+ffname,'w')
    # Calclate distance of two image
    tic = time.time()
    for i in range(num):
        diff = []
        for j in range(numx):
            ss1 = s1[i]
            sx2 = sx[j]
            diff.append(np.linalg.norm(np.abs(ss1-sx2)))
        min_diff.append(min(diff))
        min_j = diff.index(min(diff))
        f.write(str(min(diff))+','+str(a1[i])+','+str(ax[min_j])+'\n')
    mean_diff = np.mean(min_diff)
    toc = time.time() - tic
    print(mean_diff)
    f.close()



    # open a file to write
    DIR = 'corrlog_mis/'
    output_name = 'ave_' + fname.split('/')[-1][:-3] + '.txt'
    f = open(DIR+output_name,'w+')
    # write result
    print('write file:', output_name)
    f.write(str(mean_diff)+'\n')
    f.write('time usage:'+str(toc)+' s')

    # close files
    f.close()
    hx.close()


def run_task():
    """run task"""
    # initial parallel eviroment
    isParallel = True
    numthreads = 6
    if isParallel:
        pool, numthreads = paraSetup(numthreads)
        pool.map(print_PID, [i for i in range(numthreads)])
    else:
        print_PID(1)

    # read file list
    fpath = './h5corrgrid3/'
    filelist = os.listdir(fpath)
#    filelist = ['lstc0.h5']
    print(filelist)
    task = [fpath + x  for  x in filelist]
    fname_std = "./h5corrrand/corr0.h5"
    s1_name = 'g3_0'
    h1 = h5py.File(fname_std,'r')
    s1 = h1['corr'].value
    a1 = h1['angle'].value
    # computing
    if isParallel:
        par_compare = partial(compare, s1=s1,a1=a1, s1_name=s1_name)
        pool.map(par_compare, task)
        pool.close()
        pool.join()
    else:
        for filename in task:
            compare(filename, s1,a1, s1_name)
    # close file
    h1.close()


if __name__ == "__main__":
    run_task()
