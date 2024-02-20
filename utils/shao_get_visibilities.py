#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

"""
Get the No of visibility from a UVF file

"""

from astropy.io import fits
import sys

file_path = sys.argv[1]

gcount  = 0
nchan = 0
nif = 0
npol = 0
n_vis = 0

# Open the file
with fits.open(file_path) as hdu:
    # Access the primary HDU (Header Data Unit)
    for i in range(len(hdu)):
        n = hdu[i].data.shape[0]
        if n >= n_vis:
            n_vis = n 
        header = hdu[i].header
        if gcount == 0:
            gcount = header.get('GCOUNT', 0)
        if nchan == 0:
            nchan = header.get('NCHAN', 0)
        if nif == 0:
            nif = header.get('NO_IF', 0)
        if npol == 0 :
            npol = header.get('NPOL', 0)
    
    print(f"gcount: {gcount}, nchan: {nchan}, nif: {nif}, npol: {npol}")
    print(f" {file_path}  number of visibilities: {n_vis*nif}")