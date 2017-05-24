# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 10:56:25 2016

@author: wang
"""

import h5py
import matplotlib.pyplot as plt
import os, sys, time
#import pp
import random
import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.PDBParser import PDBParser
import pdb
import copy
import multiprocessing
from sklearn.externals import joblib

def print_PID(num):
    PID = os.getpid()
    print('Thread:', num, 'PID:', PID, ' is using.')

def Init(filename):
    ptask = open("task.input","r")
    para = {}
    jobs = []
    for line in ptask.readlines():
        if(line[0]=='/' or line[0]=='\n'):
            continue
        [a,b] = line.split("=")
        if a=='angle':
            jobs.append([float(x) for x in b.strip().split(',')])
        else:
            para[a]=b.strip()
    ptask.close()
#    filename = para['protein_file']
    protein_name = filename.strip().split('.')[0]
    file_type = filename.strip().split('.')[1]
    if file_type == 'cif':
        mt = MMCIF2Dict(filename)
        xlist = [float(x) for x in mt['_atom_site.Cartn_x']]
        ylist = [float(x) for x in mt['_atom_site.Cartn_y']]
        zlist = [float(x) for x in mt['_atom_site.Cartn_z']]
        allarr = np.vstack((xlist,ylist,zlist)).T
    elif file_type == 'pdb':
        parser = PDBParser()
        structure = parser.get_structure("test", filename)
        atoms = structure.get_atoms()
        alllist = []
        xlist = []
        ylist = []
        zlist = []
        for atom in atoms:
            xlist.append(atom.get_coord()[0])
            ylist.append(atom.get_coord()[1])
            zlist.append(atom.get_coord()[2])
            alllist.append(atom.get_coord())
        allarr = np.array(alllist)
    elif file_type == 'csv':
        scale = 30.0/8.0
        with open("tmp.csv") as f:
            alllist = []
            for ff in f.readlines():
                a,b,c = [float(n) for n in ff.strip().split(',')]
                alllist.append([a,b,c])
        allarr = np.array(alllist)
        allarr = allarr*scale
    if para['CENTER'] == 'ON':
        x_ave = allarr.mean(axis=0)[0]
        y_ave = allarr.mean(axis=0)[1]
        z_ave = allarr.mean(axis=0)[2]
        allarr[:,0] = allarr[:,0]-x_ave;
        allarr[:,1] = allarr[:,1]-y_ave;
        allarr[:,2] = allarr[:,2]-z_ave

    scr_size = int(para['scr_size'])
    pix_size = float(para['pix_size'])
    distance = float(para['distance'])
    lbd = float(para['lambda'])
    wavenum = 1.0/float(para['lambda'])
    ssc = scr_size/2.0-0.5

    parameters = {}
    parameters['scr_size'] = scr_size
    parameters['pix_size'] = pix_size
    parameters['distance'] = distance
    parameters['lambda'] = lbd

    s = np.zeros((scr_size,scr_size,3))
    for i in range(scr_size):
        for j in range(scr_size):
            x = (i-ssc)*pix_size
            y = (j-ssc)*pix_size
            z = distance
            sr = np.sqrt(x*x+y*y+z*z)
            s[i,j,:] = np.array([x*wavenum/sr,y*wavenum/sr,z*wavenum/sr-wavenum])

    return s,allarr,parameters,protein_name

def Gen_patt(s,tryarr,angles,scr_size):
    Rx = lambda t: np.array([[1,0,0],[0,np.cos(t),-np.sin(t)],[0,np.sin(t),np.cos(t)]])
    Ry = lambda t: np.array([[np.cos(t),0,np.sin(t)],[0,1,0],[-np.sin(t),0,np.cos(t)]])
    Rz = lambda t: np.array([[np.cos(t),-np.sin(t),0],[np.sin(t),np.cos(t),0],[0,0,1]])

    e1,e2,e3 = angles
    r1 = Rz(e1*np.pi/180)
    r2 = Rx(e2*np.pi/180)
    r3 = Rz(e3*np.pi/180)
    rall = np.dot(np.dot(r1,r2),r3)
    transarr = np.dot(rall,tryarr.T)*1.0e-10
#gen pattern in reciprocal space
    patt = np.zeros((scr_size,)*3)
    patt = map(lambda x: abs(sum(np.exp(2*np.pi*1j*np.dot(x,transarr)))),s)
    patt = np.array(patt)
    patt = patt.reshape((scr_size,)*3)
#gen pattern on screen:
#    patt = map(lambda x: abs(sum(np.exp(2*np.pi*1j*np.dot(x,transarr)))),s.reshape(scr_size*scr_size,3))
#    patt = np.array(patt).reshape((scr_size,)*2)
#    plt.imshow(patt)
    return patt

def Gen_rand_angle():
    e1 = np.random.rand() * 360.0
    e2 = np.arccos(np.random.rand()*2-1)/np.pi*180
    e3 = np.random.rand() * 360.0
    return e1,e2,e3


def Save_patt(patts,filename,parameters):
    h = h5py.File(filename,'w')
    h.create_dataset('patt',patts.shape,data=patts)
    h['scr_size'] = parameters['scr_size']
    h['pix_size'] = parameters['pix_size']
    h['distance'] = parameters['distance']
    h['lambda'] = parameters['lambda']
    h.close()

def run(filename):
    print 'init...\n'
    s,allarr,parameters,protein_name= Init(filename)
    #gen all grid in reciprocal space
    lbd = parameters['lambda']
    down = -2.5e9
    up = 2.5e9
    n_grid = 129
    len_grid = (up-down)/n_grid
    s=  []
    for i in range(n_grid+1):
        for j in range(n_grid+1):
            for k in range(n_grid+1):
                x = (i-n_grid/2)*len_grid
                y = (j-n_grid/2)*len_grid
                z = (k-n_grid/2)*len_grid
                s.append(np.array([x,y,z]))
    print 'generate grid\n'
    angles = [0,0,0]
    import time
    s1 = time.time()
    patt = Gen_patt(s,allarr,angles,n_grid+1)
    print 'time:', time.time()-s1
    patt = np.array(patt)
    Save_patt(patt,'re_space_%s.h5' % protein_name,parameters)

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

isParallel = True
numthreads = 20
if isParallel:
    pool, numthreads = paraSetup(numthreads)
    pool.map(print_PID, [i for i in range(numthreads)])
else:
    print_PID(1)
task = []
for filename in os.listdir('./'):
    if filename[0] == 'c' and filename[-4:] == '.pdb':
        task.append(filename)


if isParallel:
    pool.map(run, task)
    pool.close()
    pool.join()
else:
    for filename in task:
        run(filename)
