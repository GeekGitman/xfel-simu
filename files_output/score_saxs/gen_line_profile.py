# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 13:38:27 2016

@author: wang
"""

import numpy as np
import h5py
import os
import time
import multiprocessing

def biInterplot(x,y,arr):
    size = arr.shape[0]
    x1 = np.floor(x)
    x2 = x1+1
    if x2 >= size:
        x2 = size-1
    y1 = np.floor(y)
    y2 = y1+1
    if y2 >= size:
        y2 = size-1
    return arr[x1,y1]*(x2-x)*(y2-y)+arr[x1,y2]*(x2-x)*(y-y1)+arr[x2,y1]*(x-x1)*(y2-y)+arr[x2,y2]*(x-x1)*(y-y1)

def one_proc(fname):
    h = h5py.File(fname,'r')

    #You need to set output path here:
    #outpath = './h5lines/'
    #outpath = './h5saxsgrid3/'
    outpath = './h5saxsrand/'


    if not os.path.exists(outpath):
        os.mkdir(outpath)
    if os.path.isfile(outpath+fname.split('/')[-1]):
        return
    out = h5py.File(outpath+fname.split('/')[-1],'w')
    num_pattern = len(h['pattern'])
    size = h['pattern'].shape[1]
    angle = h['angle'].value
    half_size = (size-1.0)/2.0

    r_sample = size/2
    t_sample = size/2

    allsaxs = []
    pattsaxs = []
    print fname
    for i in range(num_pattern):
        orisaxs = []
        hh = h['pattern'][i]
        for r in range(r_sample):
            point = 0
            for t in range(t_sample):
                x = (r*half_size/r_sample)*np.cos(t*2.0*np.pi/t_sample) + half_size
                y = (r*half_size/r_sample)*np.sin(t*2.0*np.pi/t_sample) + half_size
                point += hh[int(round(x)),int(round(y))]
                #Using bi-interplot will promote the precision, decreasing the speed
                #point += biInterplot(x,y,hh)
            point = point*1.0/t_sample
            orisaxs.append(point)
        pattsaxs.append(orisaxs)
    allsaxs.append(pattsaxs)
    allsaxs = np.array(allsaxs)
    out.create_dataset('data',data=allsaxs[0])
    out.create_dataset('angle',data=angle)
    out.close()
    h.close()


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
    print('Thread:', num, 'PID:', PID, 'is using')


def run(numthreads):
    if numthreads <= 1:
        isParallel = False
    else:
        isParallel = True
    if isParallel:
        pool, numthreads = paraSetup(numthreads)
        pool.map(print_PID, [ i for i in range(numthreads)])
    else:
        print_PID(1)

    #You need to set input path here:
    #fpath = '../h5files/'
    #fpath = '../h5grid3/'
    fpath = '../h5rand/'
    filelist = os.listdir(fpath)
    print filelist
    task = [fpath + x  for x in filelist]
    t1 = time.time()
    if isParallel:
        pool.map(one_proc,task)
        pool.close()
        pool.join()
    else:
        for filename in task:
            one_proc(filename)
    print time.time()-t1

import sys
if len(sys.argv) < 2:
    run(1)
else:
    run(sys.argv[1])
