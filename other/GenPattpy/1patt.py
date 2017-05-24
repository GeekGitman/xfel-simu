# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 08:56:24 2016

@author: wang
"""

import numpy as np
import matplotlib.pyplot as plt
import random
import os,re
import h5py

lbd = 8.0e-10
distance = 0.581
scr_size = 300
pix_size = 0.0003

hlf_scr = scr_size*pix_size/2.0
theta = np.arctan(hlf_scr/distance)/2.0
q = 4*np.pi*np.sin(theta)/lbd
d = 2*np.pi/q

print d


def readfile(filename):
    f = open(filename,"r")
    allarr = []
    realarr = []
    imagarr = []
    print filename
    for line in f.readlines():
        comp = line.strip().split(',')[:-1]
        linereal = [float(y[0]) for y in [x.split('+') for x in comp]]
        lineimag = [float(y[1]) for y in [x.split('+') for x in comp]]
        realarr.append(linereal)
        imagarr.append(lineimag)
    realarr = np.array(realarr)
    imagarr = np.array(imagarr)
    allarr = realarr + imagarr*1j
    f.close()
    return allarr

def getdim(filename):
    f = open(filename,"r")
    dim1 = 0
    dim2 = 0
    for line in f.readlines():
        dim1 = dim1 + 1
        comp = line.strip().split(',')[:-1]
        dim2 = len(comp)
    print dim1,dim2
    return (dim1,dim2)

def Make_screen(scr_size,dr):
    scr = np.zeros((scr_size,scr_size),dtype=complex)
    z = 1.0 #distance=1.0m
    k = np.pi*2.0/lbd
    for i in range(scr_size):
        for j in range(scr_size):
            x = (i-(scr_size-1)/2.0)*pix_size
            y = (j-(scr_size-1)/2.0)*pix_size
            r = np.sqrt(x**2+y**2+z**2)
            s = k*np.array((x,y,z))/r
    #        print np.dot(s,dr)
#            print 'dr' , dr
 #           print 's', s
            scr[i][j] = np.exp(1.0j*np.dot(s,dr))
            #scr[i][j] = np.exp(1.0j*(i+j)/scr_size*6*2*np.pi)
     #       print 'v', 1.0*(i+j)/scr_size*12*np.pi
    return scr

def read2(dim,filename1,filename2,shift):
    scr = Make_screen(dim,shift)
    arr1 = readfile(filename1)
    arr2 = readfile(filename2)
    arrR = arr1+arr2*scr
    return arrR

def RandVecGen(rmin,rmax):
    e1 = 0
    e2 = 0
    e3 = 0
    while e1**2+e2**2+e3**2>rmax**2 or e1**2+e2**2+e3**2<rmin**2:
        e1 = (np.random.rand()*2-1)*rmax
        e2 = (np.random.rand()*2-1)*rmax
        e3 = (np.random.rand()*2-1)*rmax
#    rr = e1**2+e2**2+e3**2
#    r = np.random.rand()*r
    f = open('log.txt','a+')
    f.write( "%6.2f,%6.2f,%6.2f,%6.2f\n" % (1e9*e1,1e9*e2,1e9*e3,1e9*np.sqrt(e1**2+e2**2+e3**2)) )
    f.close()
    return np.array((e1,e2,e3))


#def show():
#    allarr1 = readfile("tmp1.dat")
#    plt.subplot(5,5,1)
#    plt.imshow(np.log(abs(allarr1)))
#    for i in range(20):
#        r = 1.0e-6*3
#        shift = RandVecGen(r)
#        allarr2 = read2("tmp1.dat","tmp2.dat",shift)
#        plt.subplot(5,5,i+6)
#        plt.imshow(np.log(abs(allarr2)))
filepath = './tmp/'
filename_list = os.listdir(filepath)
random.shuffle(filename_list)
rere = re.compile(r'tmp:\d+:(\w|-|\.)*:(\w|-|\.)*,(\w|-|\.)*,(\w|-|\.)*.dat')

num_files = len(filename_list)/3
arrlst = []
anglst = []
num_files = 100
filename = filename_list[0]
dim1,dim2 = getdim(filepath+filename)
for filename in filename_list[:num_files]:
    arrlst.append(abs(readfile(filepath+filename)))
    anglst.append([float(n) for n in filename[:-4].split(':')[-1].split(',')])
#arrall = np.array(arrlst)
h = h5py.File('v1.h5','w')
h.create_dataset('pattern',(num_files,dim1,dim2),data=arrlst)
h.create_dataset('angle',(num_files,3),data=anglst)
h['lambda'] = lbd
h['scr_size'] = scr_size
h['pix_size'] = pix_size
h.close()
arrlst = []
anglst1 = []
anglst2 = []
shiftlst = []
indLst = range(num_files,3*num_files,2)
rmin = 300e-9
rmax = 1e-6
for i,ind in enumerate(indLst):
    shift = RandVecGen(rmin,rmax)
    shiftlst.append(shift)
    arrlst.append(abs(read2(dim1,filepath+filename_list[ind],filepath+filename_list[ind+1],shift)))
    anglst1.append([float(n) for n in filename_list[ind][:-4].split(':')[-1].split(',')])
    anglst2.append([float(n) for n in filename_list[ind+1][:-4].split(':')[-1].split(',')])
arrall = np.array(arrlst)
shiftlst = np.array(shiftlst)
h = h5py.File('v21um.h5','w')
h.create_dataset('pattern',arrall.shape,data=arrall)
h.create_dataset('shift',shiftlst.shape,data=shiftlst)
h.create_dataset('angle1',(num_files,3),data=anglst1)
h.create_dataset('angle2',(num_files,3),data=anglst2)
h['lambda'] = lbd
h['scr_size'] = scr_size
h['distance'] = distance
h['pix_size'] = pix_size
h.close()

