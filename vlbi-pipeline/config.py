#!/usr/bin/env python

AIPS_NUMBER = 12345   # Make sure you know what is meaning?
AIPS_VERSION = '31DEC20'
version_date = '2016/04/06'
antname = 'VLBA'  # Antenna order for FITLD
geo_path = '/home/share/VLBI/geod/'
# file_path = sys.argv[1]
# TODO can be modify
file_path = '../data/'

########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
INTER_FLAG = 0 # interactive (1) or non-interactive (0)
DEF_DISKS = 1 # default AIPS disk to use (can be change anytime)

#todo check how to rename
filename = 'test123.idifits'
max_files = 16
outname = range(max_files)
outname[0] = filename.split(',')[0]

# Download data from archive? not needed
DOWNLOAD_FLAG = 0
# data file with geo data? (<0 for no geoblock)
geo_data_nr = 0
# Run TECOR, EOPs, ATMOS, PANG, and position shift?
pr_prep_flag = 0
