# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:03:40 2016
This program convert lstc*.h5 to ave line. In parallel method.
@author: wang
"""

import h5py
import numpy as np
import os


if __name__ == "__main__":
    inputname = "./h5files/lstc0.h5"
    outputname = "./h5noise/lstc0_1.h5"
    if not os.path.exists(outputname):
         os.mkdir(outputname)
    GAUSSIAN = True
    #signal noise ratio of gaussian noise
    SNR = 1
    f = h5py.File(inputname)
    std = f['pattern'][()]
    for n in range(len(std)):
        #Add Poisson noise
        std[n] = np.random.poisson(std[n])
        if GAUSSIAN:
            varI = np.std(std[n])**2
            sigma_noise = np.sqrt(varI/SNR)
            std[n] = std[n] + np.random.normal(0,sigma_noise,std[n].shape)
    h = h5py.File(outputname,'w')
    h.create_dataset('pattern',data=std)
    h.create_dataset('protein_name',data=f['protein_name'][()])
    h.create_dataset('angle',data=f['angle'][()])
    f.close()
    h.close()
