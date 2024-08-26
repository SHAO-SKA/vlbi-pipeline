#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys
import glob
import re

data_path = sys.argv[1]

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


# assume path is in the form of /path/to/files/J0646+4451/
# outname will be pm-J0646+4451.txt
outname = 'pm-'+sys.argv[1].split('/')[-2]+'.txt'
fp_out = open(outname, 'w')
fp_out.write('date,R1,theta,R1_err1\n')
for i in all_files:
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
    for ii in lines:
        if '!' in ii:
            pass
        else:
            dat.append(ii)
    if (len(dat)) > 1:
        R_c = float(dat[0].replace('v', '').split()[1])
        theta_c = float(dat[0].replace('v', '').split()[2])
        R_j = float(dat[1].replace('v', '').split()[1])
        theta_j = float(dat[1].replace('v', '').split()[2])

        # Convert to Cartesian coordinates
        x_j, y_j = polar_to_cartesian(R_j, theta_j)
        x_c, y_c = polar_to_cartesian(R_c, theta_c)

        # Calculate coordinates of J relative to C
        x_new = x_j - x_c
        y_new = y_j - y_c

        # Convert back to polar coordinates
        R_new, theta_new = cartesian_to_polar(x_new, y_new)

        # Adjust theta_new if necessary to conform to the North-to-East convention
        theta_new = (theta_new + 360) % 360

        print(f"New radial distance (J-C): {R_new}")
        print(f"New position angle of A: {theta_new} degrees")
        fp_out.write(date + ', ' + str(R_new) + ', ' +
                     str(theta_new) + ', 0.0000' + '\n')

fp_out.close()