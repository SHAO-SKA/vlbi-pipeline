#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from astropy.io import fits
import datetime
import sys

base = sys.argv[1]

#band default is 'X' otherwise give by sys.argv[2]
band = 'X'
if len(sys.argv) > 2:
    band = sys.argv[2]

year = datetime.datetime.now().year
mon = datetime.datetime.now().month
day = datetime.datetime.now().day
hour = datetime.datetime.now().hour
minute = datetime.datetime.now().minute
sec = datetime.datetime.now().second

cur_time = '{}{}{}-{}{}{}'.format(year, mon, day, hour, minute, sec)


outname = 'propermotion-error-' +base.split('/')[-2][0:5] +'-' + band +'.txt'
os.system('mv ' + outname + ' ' + outname+'.'+cur_time)


dtype1 = [('name', 'U20'), ('date', 'U15'), ('maj', 'f4'), ('min', 'f4'), ('PA', 'f4'), ('freq', 'f4'), ('comp', 'U10'), ('flux', 'f4'),('x','f4'), ('y', 'f4'), ('a', 'f4'), ('peak', 'f4'), ('RMS', 'f4'), ('SNR', 'f4'), ('ratio', 'f4'), ('theta', 'f4'), ('error','f4')]
data = np.zeros(0, dtype=dtype1)
pd.set_option('expand_frame_repr', False)
dir1 = base

mod_paths = []
for root, dirs, files in os.walk(dir1):
    if files:
        for f in files:
            if f.endswith('-mod.fits'):
                file_path = os.path.join(root, f)
                mod_paths.append(file_path)
# print(mod_paths)


for file in sorted(mod_paths):
    print('File is : ', file)
    hdu = fits.open(file)
    h = hdu[0].header
    mods = hdu[1].data
    imgs = hdu[0].data[0, 0, :, :]
    print(type(imgs))
    print(len(imgs))

    dat = np.zeros(mods.size, dtype=dtype1)
    dat['name'] = h['object']
    dat['date'] = h['date-obs'][0:10]
    dat['freq'] = h['crval3']/1.0E9
    freq = h['crval3']/1.0E9
    dat['flux'] = mods['FLUX']*1000
    dat['x'] = mods['DELTAX'] * 3.6e6
    dat['y'] = mods['DELTAY'] * 3.6e6
    dat['a'] = mods['MAJOR AX']*3.6E6
    dat['peak'] = h['DATAMAX']*1000
    print ('DATAMAX, ', h['DATAMAX'])
    print ('DATAMAX, ', np.max(imgs))
    dat['RMS'] = np.std(imgs)*1000
    rms  = np.std(imgs)*1000
    print('rmsall ', rms)
    rms1  = np.std(imgs[0:100,0:100])*1000
    if rms1 < rms:
        rms = rms1
    print('rms1 ', rms1)
    rms2  = np.std(imgs[-100:,-100:])*1000
    print('rms2 ', rms2)
    if rms2 < rms:
        rms = rms2
    print('rms ', rms)
    #dat['SNR'] = h['DATAMAX']/dat['RMS']
    dat['SNR'] = h['DATAMAX']/rms
    k = 5
    w = (k, -k, -k, k)

    b = (w[0]-1.5*h['bmaj']*3.6E6, w[2]+1.5*h['bmaj'] *
         3.6E6, h['bmaj']*3.6E6, h['bmin']*3.6E6, h['bpa'])
    dat['maj'] = b[2]
    dat['min'] = b[3]
    dat['error'] = 0.5 * np.sqrt(dat['maj'] * dat['min'])/dat['SNR']
    error = np.sqrt(dat['maj'] * dat['min'])/dat['SNR']
    print('error ', error)
    dat['PA'] = 90-b[4]
    dat['ratio'] = np.divide(mods['MINOR AX']*3.6E6, mods['MAJOR AX']*3.6E6)
    dat['ratio'] = np.nan_to_num(dat['ratio'])
    dat['theta'] = mods['POSANGLE']
    r = dat['x']**2 + dat['y']**2
    r = np.sqrt(r)
    hdu.close()
    dat = dat[np.argsort(r)]
    dat['comp'] = ['J%d' % (dat.size-i) for i in range(dat.size)]
    dat[0]['comp'] = 'C'
    print('freq', freq)
    if band == 'X':
        if 7 < freq < 9:
            data = np.append(data, dat)
    if band == 'S':
        if 2 < freq < 4:
            data = np.append(data, dat)
# print(data)


with open(outname, 'w') as o:
    o.write("# name, date, maj, min, PA, freq, comp, flux, x, y, major,peak,RMS, SNR, ratio, theta, error\n")
    for i in data:
        o.write(str(i)+'\n')
