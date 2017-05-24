#generate grid mesh, you need to paste the output of this file to the task.input
import numpy as np


def Gen_grid(angle):
    """
    3Eular angles:
    """
    task = open('taskgrid.txt','w')
    a,b,c = angle
    out = []
    a_range = np.linspace(a-180.0*ratio,a+180.0*ratio,num)
    b_range = np.linspace(b-180.0*ratio,b+180.0*ratio,num)
    c_range = np.linspace(c-180.0*ratio,c+180.0*ratio,num)
    for aa in a_range:
        for bb in b_range:
            for cc in c_range:
                task.write("angle={:f},{:f},{:f}\n".format(aa,bb,cc))
                out.append([aa,bb,cc])

def Rand_gen(angle,num):
    """
    3Eular angles:
    """
    task = open('taskrand.txt','w')
    a,b,c = angle
    out = []
    a1 = a-180.0*ratio
    a2 = a+180.0*ratio
    b1 = b-180.0*ratio
    b2 = b+180.0*ratio
    c1 = c-180.0*ratio
    c2 = c+180.0*ratio
    for n in range(num):
        aa = (a2-a1)*np.random.rand()+a1
        bb = (b2-b1)*np.random.rand()+b1
        cc = (c2-c1)*np.random.rand()+c1
        out.append([aa,bb,cc])
        task.write("angle={:f},{:f},{:f}\n".format(aa,bb,cc))

#gen_grid
#The bottom angle to the center angle
ratio = 22.5/180.0
#angle step.(grid mesh)
step = 3
#number of grids of one angle
num = 2*ratio*180.0/step + 1
#Call Gen_grid, with center on (0,0,0)
Gen_grid((0,0,0))

#Randomly generate 5000 angles with center on (0,0,0)
Rand_gen((0,0,0),5000)
