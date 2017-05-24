import os
import time

nlst1 = range(1,9)
for i in nlst1:
    os.system('sed -i  \'11c python ./gen_line_profile.py ' + str(i)  +'\' qsub.pbs')
    os.system('qsub ./qsub.pbs')


