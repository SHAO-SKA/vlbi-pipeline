#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

"""
Get the No of visibility from a UVF file

"""

from astropy.io import fits
import sys

# Replace 'your_file_path.uvf' with the path to your UVFITS file
file_path = sys.argv[1]

gcount  = 0
nchan = 0
nif = 0
npol = 0

# Open the file
with fits.open(file_path) as hdul:
    # Access the primary HDU (Header Data Unit)
    header = hdul[0].header
    print(header)
    # Extract values
    gcount = header.get('GCOUNT', 'Value not found')
    nchan = header.get('NCHAN', 'Value not found')
    nif = header.get('NIF', 'Value not found')
    npol = header.get('NPOL', 'Value not found')
    header = hdul[1].header
    # Extract values
    if gcount == 0:
        gcount = header.get('GCOUNT', 'Value not found')
    nchan = header.get('NCHAN', 'Value not found')
    nif = header.get('NIF', 'Value not found')
    npol = header.get('NPOL', 'Value not found')
    
    print(f"gcount: {gcount}, nchan: {nchan}, nif: {nif}, npol: {npol}")