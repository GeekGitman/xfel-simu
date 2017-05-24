import os
import time

nlst1 = range(1,2)
for i in nlst1:
        newdir = './p'+str(i)+'/'
        pdbname = 'c'+str(i)+'.pdb'
        os.mkdir(newdir)
        os.chdir(newdir)
        os.system('cp -r ../root/* .')
        os.system('cp ' + '../files_pdb/'+ pdbname + ' .')
        os.system('sed -i \'2c protein_file='+pdbname+'\' task.input')
        os.system('qsub ./qsublow.pbs')
        os.chdir('../')

#nlst1 = range(1001,2000,2)
#for i in nlst1:
#        newdir = './p'+str(i)+'/'
#        pdbname = 'c'+str(i)+'.pdb'
#        os.mkdir(newdir)
#        os.chdir(newdir)
#        os.system('cp -r ../root/* .')
#        os.system('cp ' + '../files_pdb/'+ pdbname + ' .')
#        os.system('sed -i \'5c protein_file='+pdbname+'\' task.input')
#        os.system('qsub ./qsubbatch.pbs')
#        os.chdir('../')
#
#while(1):
#    time.sleep(20)
#    if os.system('qstat -u whx | wc -l') == '0':
#        break
#
#print "gen done"
#os.system('mv p*/lstc*.h5 ./files_output/')
#os.system('mv p* ./store/')
#os.chdir('./files_output/')
#os.system('python ave_serial.py')
#os.system('pypython calc_ave.py')
#
