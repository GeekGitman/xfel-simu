#!/home/whx/software/anaconda2/bin/ipython
'''
This program analysis the impact of RMSD and grid on the possibility of finding the nearest one
Hongxiao Wang
12/18/2016
'''
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import pdb
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve , auc
from sklearn import svm
import re

def Read_folder(folder_name,rmsdList):
    ind = [0,]
    ind.extend(range(1,2000,2))
    arr = []
    for i in ind:
        fname = folder_name + '/log_g3_0_' + str(i) + '.txt'
        if os.path.exists(fname):
            prob = Read_file(fname,1,int(folder_name[-1]))
            rmsd = float(rmsdList[i][1])
            if prob != - 1:
                arr.append([rmsd,prob])
    arr = np.array(arr)
    return arr


def Read_file(file_name):
    dists = []
    rere = re.compile('\s+')
    with open(file_name) as f:
        n_hit = 0
        n_all = 0
        d = dict()
        for l in f.readlines():
            a,b = l.strip().split(',')
            a = float(a)
            b = float(b)
            d[a] = b
    return d


def mySVM(scores,class1,class2,kernel,C,parameter):
    start1, end1 = class1
    start2, end2 = class2
    X = np.zeros((end1-start1 + end2-start2 +2,scores.shape[1]))
    y = np.zeros(end1-start1 + end2-start2 +2)
    X[start1:end1+1] = scores[start1:end1+1]
    y[start1:end1+1] = [1,]*1000
    X[end1+1:] = scores[start2:end2+1]
    y[end1+1:] = [0,]*1000
    Xtrain = np.vstack((X[0:600,:],X[1000:1600,:]))
    Xtest = np.vstack((X[600:1000,:],X[1600:2000,:]))
    ytrain = np.hstack((y[0:600],y[1000:1600]))
    ytest = np.hstack((y[600:1000],y[1600:2000]))
    #Xtrain = X
    #Xtest = X
    #ytrain = y
    #ytest = y
    clf = svm.SVC(kernel=kernel,C=C,probability=True).fit(Xtrain,ytrain)
    #clf = svm.SVC(kernel='linear',probability=True).fit(Xtrain,ytrain)
    clf = svm.SVC(kernel='sigmoid',probability=True).fit(Xtrain,ytrain)
    prob = clf.predict_proba(Xtest)
    #np.set_printoptions(threshold = 1e6)
    y_prob = clf.predict(Xtest)
    print sum(abs(ytest-y_prob))
    print y_prob
    #ROC
    fpr, tpr, thresholds = roc_curve(ytest,prob[:,0],pos_label=0)
    roc_auc = auc(fpr,tpr)
    #plt.figure()
    #plt.plot(fpr,tpr)
    return fpr,tpr,roc_auc

def Regression(scores,class1,class2,):
    start1, end1 = class1
    start2, end2 = class2
    clf = LogisticRegression(C=0.1,penalty='l1',tol=0.01)
    X = np.zeros((end1-start1 + end2-start2 +2,scores.shape[1]))
    y = np.zeros(end1-start1 + end2-start2 +2)
    X[start1:end1+1] = scores[start1:end1+1]
    y[start1:end1+1] = [0,]*1000
    X[end1+1:] = scores[start2:end2+1]
    y[end1+1:] = [1,]*1000
    Xtrain = np.vstack((X[0:600,:],X[1000:1600,:]))
    Xtest = np.vstack((X[600:1000,:],X[1600:2000,:]))
    ytrain = np.hstack((y[0:600],y[1000:1600]))
    ytest = np.hstack((y[600:1000],y[1600:2000]))
    clf.fit(Xtrain,ytrain)
    prob = clf.predict_proba(Xtest)
    print prob

    #ROC
    fpr, tpr, thresholds = roc_curve(ytest,prob[:,0],pos_label=0)
    roc_auc = auc(fpr,tpr)
    #plt.figure()
    #plt.plot(fpr,tpr)
    return fpr,tpr,roc_auc

def mykNN(scores,class1,class2,):
    start1, end1 = class1
    start2, end2 = class2
    neigh = KNeighborsClassifier(n_neighbors=5)
    X = np.zeros((end1-start1 + end2-start2 +2,scores.shape[1]))
    y = np.zeros(end1-start1 + end2-start2 +2)
    X[start1:end1+1] = scores[start1:end1+1]
    y[start1:end1+1] = [0,]*1000
    X[end1+1:] = scores[start2:end2+1]
    y[end1+1:] = [1,]*1000
    Xtrain = np.vstack((X[0:600,:],X[1000:1600,:]))
    Xtest = np.vstack((X[600:1000,:],X[1600:2000,:]))
    ytrain = np.hstack((y[0:600],y[1000:1600]))
    ytest = np.hstack((y[600:1000],y[1600:2000]))
    neigh.fit(Xtrain,ytrain)
    prob = neigh.predict_proba(Xtest)
    print prob

    #ROC
    fpr, tpr, thresholds = roc_curve(ytest,prob[:,0],pos_label=0)
    roc_auc = auc(fpr,tpr)
    #plt.figure()
    #plt.plot(fpr,tpr)
    return fpr,tpr,roc_auc


def Roc(prob):
    pass

def Run():
    fnamesfile = open('zdockjointfilenames_table.csv')
    outputnamefile = open('jointroc_curve.csv','w')
    #score  = Read_file('./lineprofile/log_g3_0_line.txt',1,1)
    if len(sys.argv) == 1:
        fname = './corrlog/s10000log_g3_0_0.txt'
    else:
        fname = sys.argv[1]
    labels = ['10000','20000','30000','40000']
    n_row = -1
    lines = []
    for fnames in fnamesfile.readlines():
        if fnames[0] == '#':
            continue
        n_row = n_row + 1
        fnamess = fnames.strip().split(',')
        n_fname = len(fnamess)
        data = {}
        allscores = np.zeros((6000,len(fnamess)))
        print n_row
        plt.subplot(2,2,n_row+1)
        for nlabel,fname in enumerate(fnamess):
            d = Read_file(fname)

        for key in data:
            if len(data[key]) < n_fname
                data

        #plt.scatter(allscores[:1000,1],allscores[:1000,2],color='b')
        #plt.scatter(allscores[1000:1999,1],allscores[1000:1999,2],color='r')
        #plt.xlabel('Autocorr',fontsize=20)
        #plt.ylabel('Line profile',fontsize=20)
        #plt.gca().tick_params(labelsize=15)


        starta = 0 #start num of training set
        enda = 600
        starte = 600 #start num of test set
        ende = 1000
        X = allscores[starta:enda]
        y =
        X = np.zeros((end1-start1 + end2-start2 +2,scores.shape[1]))
        y = np.zeros(end1-start1 + end2-start2 +2)
        X[start1:end1+1] = scores[start1:end1+1]
        y[start1:end1+1] = [0,]*1000
        X[end1+1:] = scores[start2:end2+1]
        y[end1+1:] = [1,]*1000
        Xtrain = np.vstack((X[0:600,:],X[1000:1600,:]))
        Xtest = np.vstack((X[600:1000,:],X[1600:2000,:]))
        ytrain = np.hstack((y[0:600],y[1000:1600]))
        ytest = np.hstack((y[600:1000],y[1600:2000]))

    #ROC
    fpr, tpr, thresholds = roc_curve(ytest,prob[:,0],pos_label=0)
    roc_auc = auc(fpr,tpr)
    #plt.figure()
    #plt.plot(fpr,tpr)
    return fpr,tpr,roc_auc

        classifier = 'knn'
        if classifier == 'reg':
            #use regression method
            reg = Regression(allscores[:,1:],(0,999),(1000,1999))  #psudo code
            fpr,tpr,roc_auc = reg
        if classifier == 'svm':
            #use svm method
            sv = mySVM(allscores[:,1:],(0,999),(2000,2999),'rbf',C=1,parameter=0.2)
            fpr,tpr,roc_auc = sv
        if classifier == 'knn':
            kn = mykNN(allscores[:,:],(0,999),(2000,2999))
            fpr,tpr,roc_auc = kn
        print roc_auc




        outputnamefile.write('%4.2f,'%roc_auc)
        #line, = plt.plot(fpr,tpr,label=labels[n_row])
        #lines.append(line)
        outputnamefile.write('\n')
    #plt.legend(handles=lines,loc=4)
    #plt.xlabel('False Positive Rate',fontsize=20)
    #plt.ylabel('True Positive Rate',fontsize=20)
    #plt.gca().tick_params(labelsize=15)
    plt.show()
    outputnamefile.close()

Run()
