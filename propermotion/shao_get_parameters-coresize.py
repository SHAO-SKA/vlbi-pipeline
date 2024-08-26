#!/usr/bin/env python
import numpy as np
import sys
import glob
import re

data_path =  sys.argv[1]

all_files = glob.glob(data_path + "*.mod")

print(all_files)

def polar_to_cartesian(R, theta_deg):
    theta_rad = np.radians(theta_deg)
    x = R * np.sin(theta_rad)
    y = R * np.cos(theta_rad)
    return x, y

def cartesian_to_polar(x, y):
    R_new = np.sqrt(x**2 + y**2)
    theta_new_rad = np.arctan2(y, x)
    theta_new_deg = np.degrees(theta_new_rad)
    return R_new, theta_new_deg
outname = 'coresize-'+sys.argv[1].split('/')[-2]+'.txt'
fp_out = open(outname, 'w')
outname_C = 'coresize-'+sys.argv[1].split('/')[-2]+'-C.txt'
fp_out_C = open(outname_C, 'w')
fp_out.write('date,major,minor,comp\n')
fp_out_C.write('date,major,minor,comp\n')
for i in all_files:
    coresize = ''
    a = open(i)
    i = i.split('/')[-1]
    # assume i is in the form of J0646+4451-20190101X-mod.mod
    # date will be 2019/01/01
    match = re.search(r'\d{8}', i)

    if match:
        date_str = match.group(0)
        formatted_date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
        print(formatted_date)
    else:
        print("No date found in the string.")

    date = formatted_date
    print(date)
    lines = a.readlines()
    dat = []
    is_core = 0
    for ii in lines:
        if '!' in ii:
            pass
        else:
            coresize = float(ii.replace('v', '').split()[3])
            ratio = float(ii.replace('v', '').split()[4])
            if is_core == 0:
                fp_out.write(date + ', ' + str(coresize) + ',' + str(coresize*ratio) +  ', C \n')
                fp_out_C.write(date + ', ' + str(coresize) + ',' + str(coresize*ratio) +  ', C \n')
            if is_core == 1:
                fp_out.write(date + ', ' + str(coresize) +  ',' + str(coresize*ratio) +', J \n') 
            is_core = 1

fp_out.close()
fp_out_C.close()
