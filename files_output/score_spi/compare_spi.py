# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:03:40 2016
This program convert lstc*.h5 to ave line. In parallel method.
@author: wang
"""

import h5py
import os
import numpy as np
import multiprocessing

def paraSetup(numthreads=None):
    """Setup parallel environment"""
    det_numthreads = multiprocessing.cpu_count()
    if numthreads == None:
        use_numthreads = det_numthreads
    else:
        use_numthreads = min(det_numthreads, numthreads)
    print('Detected {0} cores, using {1} threads'.format(det_numthreads, use_numthreads))
    pool = multiprocessing.Pool(processes=use_numthreads)
    return pool, use_numthreads


def print_PID(num):
    PID = os.getpid()
    print('Thread:', num, 'PID:', PID, ' is using.')

def one_proc(fname):
    if fname[-2:] != 'h5':
        return 0
    fpath = "../h5files/"
    fh = h5py.File(fpath+'lstc0.h5')
    std = fh['pattern'][()]
    fh.close()
    difflst = []
    f = h5py.File(fname)
    p = f['pattern'][()]
    f.close()
    for n in range(len(p)):
        diff = np.linalg.norm((p[n]-std[n]),ord=2)
        print diff
        print p[n].shape
        difflst.append(diff)
#    np.random.shuffle(difflst)
    if not os.path.exists('./outfiles'):
        os.mkdir('./outfiles')
    fout = open('./outfiles/'+fname[:-2].split('/')[-1]+'out','w')
    for diff in difflst:
        fout.write(str(diff)+'\n')
    fout.close()




def run_task():
    """run task"""
    # initial parallel eviroment
    isParallel = False
    numthreads = 9
    if isParallel:
        pool, numthreads = paraSetup(numthreads)
        pool.map(print_PID, [i for i in range(numthreads)])
    else:
        print_PID(1)

    # read file list
    fpath = '../h5files/'
    filelist = os.listdir(fpath)
    a = []
    for filename in filelist:
        if filename in a:
            filelist.remove(filename)
    print(filelist)
    task = [fpath + x  for  x in filelist]
    fname_std = "../h5files/lstc0.h5"
    s1_name = 'lstc0'
    h1 = h5py.File(fname_std,'r')
    s1 = h1['pattern'].value

    # computing
    if isParallel:
        pool.map(one_proc, task)
        pool.close()
        pool.join()
    else:
        for filename in task:
            one_proc(filename)
    # close file
    h1.close()


if __name__ == "__main__":
    run_task()

