#!/usr/bin/env python
import numpy as np
import sys
import glob

id = sys.argv[1]
#band default is 'X' otherwise give by sys.argv[2]
band = 'X'
if len(sys.argv) > 2:
    band = sys.argv[2]

pm_file = 'pm-{}.txt'.format(id)
core_file = 'coresize-{}-C.txt'.format(id)
pm_file_difmap = 'propermotion-error-{}-X.txt'.format(id)
pm_file_new = 'pm-{}-{}-errorbar.txt'.format(id, band)

title_line = 'date,R1,theta,R1_err\n'

pm_ratio = 0.1 # 10% of beamsize

def find_Jet_beam(corefile, date):
    fp = open(corefile,'r')
    fp.readline()
    lines = fp.readlines()
    date_new = date.replace('/', '-')
    #date_new = date
    for i in lines:
        if date_new in i:
            major = i.split(',')[2]
            minor = i.split(',')[3]
            #if 'C' in minor :
            #    minor = major
            print(major, minor)
            #return np.sqrt(float(major) * float(minor))
            return float(minor)
    return 0.0


fp = open(pm_file,'r')
fp_out = open(pm_file_new,'w')
fp_out.write(title_line)
fp.readline()
lines = fp.readlines()
for i in lines:
    date = i.split(',')[0]
    r = i.split(',')[1]
    theta = i.split(',')[2]
    error = find_Jet_beam(pm_file_difmap, date) * pm_ratio
    fp_out.write(date + ',' + r + ',' + theta + ',' + str(error)  + '\n')    
fp_out.close()
fp.close()