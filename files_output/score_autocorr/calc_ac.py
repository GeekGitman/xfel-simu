"""
Lanqing Huang made great contribution to this program.
"""

import math
import os
import h5py
import numpy as np
import multiprocessing
import sys
import argparse


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


def gen_ac(fname):
    # initial Environment
    print('PID:',os.getpid(),' is calculating file', fname)

    #You need to modify the output path here!
    #outpath = './h5corr/'
    #outpath = './h5corrgrid3/'
    outpath = './h5corrrand/'

    if not os.path.exists(outpath):
        os.mkdir(outpath)
    filename = fname
    if filename[-3:]=='.h5':
        print filename
        h = h5py.File(filename,'r')
        out = h5py.File(outpath + 'corr'+filename.split('lstc')[-1],'w')
        outl = []
        data = h['pattern'].value
        for i in range(len(data)):
            c2_img = get_corr_img(data[i], pcimg_interpolation='nearest')
            outl.append(c2_img)
        outl = np.array(outl)
        out.create_dataset("corr",data=outl)
        out.create_dataset("angle",data=h['angle'].value)
        out.close()
        h.close()



def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)

    return (phi, rho)

def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)

    return (x, y)


def imgpolarcoord(img):
    """
    converts a given image from cartesian coordinates to polar coordinates.

    Image center:
    The center of rotation of a 2D image of dimensions xdim x ydim is defined by
    ((int)xdim/2, (int)(ydim/2)) (with the first pixel in the upper left being (0,0).
    Note that for both xdim=ydim=65 and for xdim=ydim=64, the center will be at (32,32).
    This is the same convention as used in SPIDER and XMIPP. Origin offsets reported
    for individual images translate the image to its center and are to be applied
    BEFORE rotations.
    """
    row, col = img.shape
    cx = int(col/2)
    cy = int(row/2)
    radius = float(min([row-cy, col-cx, cx, cy]))
    angle = 360.0

    """Interpolation: Nearest"""
    pcimg = np.zeros((int(radius), int(angle)))
    radius_range = np.arange(0, radius, 1)
    angle_range = np.arange(0, 2*math.pi, 2*math.pi/angle)
    i = 0
    for r in radius_range:
        j = 0
        for a in angle_range:
            pcimg[i,j] = img[int(cy+round(r*np.sin(a))), int(cx+round(r*np.cos(a)))]
            j = j + 1
        i = i + 1

    return pcimg


def get_corr_img(img, pcimg_interpolation='nearest'):
    """
    get a angular correlation img
    """

    if pcimg_interpolation is 'nearest':
        pcimg = imgpolarcoord(img)
    elif pcimg_interpolation is 'linear':
        pcimg = imgpolarcoord(img)

    pcimg_fourier = np.fft.fftshift(np.fft.fft(pcimg, axis=1))
    C2_img = np.fft.ifft(np.fft.ifftshift(pcimg_fourier*np.conjugate(pcimg_fourier)), axis=1)
    C2_img = C2_img.real
    return C2_img




def run_task(num_processor):
    """run task"""
    # initial parallel eviroment
    if num_processor == 1:
        isParallel = False
        numthreads = 1
    else:
        isParallel = True
        numthreads = num_processor

    if isParallel:
        pool, numthreads = paraSetup(numthreads)
        numthreads = 3  ###
        pool.map(print_PID, [i for i in range(numthreads)])
    else:
        print_PID(1)

    #You need to modify the input path here!
    #read file list
    #fpath = '../h5files/'
    #fpath = '../h5grid3/'
    fpath = '../h5rand/'
    filelist = os.listdir(fpath)
    print(filelist)
    task = [fpath + x  for  x in filelist]

    # computing
    if isParallel:
        pool.map(gen_ac, task)
        pool.close()
        pool.join()
    else:
        for filename in task:
            gen_ac(filename)
    # close file


if __name__ == "__main__":
    if len(sys.argv) == 1:
        num_processor = 1
        run_task(num_processor)
    else:
        try:
            num_processor = sys.argv[1]
            run_task(num_processor)
        except ValueError:
            print('invalid number of processor!')

