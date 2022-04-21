#!/usr/bin/env python

AIPS_NUMBER = 12345   # Make sure you know what is meaning?
AIPS_VERSION = '31DEC20'
version_date = '2016/04/06'
antname = 'VLBA'  # Antenna order for FITLD
geo_path = '/home/share/VLBI/geod/'

################# todo
target_source = ''
phase_ref_source = ''

########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
INTER_FLAG = 0 # interactive (1) or non-interactive (0)
DEF_DISKS = 1 # default AIPS disk to use (can be change anytime)

# Download data from archive? not needed
DOWNLOAD_FLAG = 0
# data file with geo data? (<0 for no geoblock)
geo_data_nr = 0
# Run TECOR, EOPs, ATMOS, PANG, and position shift?
pr_prep_flag = 0
def_file = '/home/ykzhang/Scripts/BeSSel/def_bessel_vlbi-lba.py'

fr_path = '/home/ykzhang/VLBA/ba114/ba114b/BA114b/'

file_path = '../data/'
# file_path = sys.argv[1]
fit_path = '/home/ykzhang/VLBA/ba115/'  # not used
TECU_model = 'jplg'

filename = 'test123.idifits'

split_outcl = 'SPLIT'

max_files = 1024

outname = range(max_files)

outname[0] = filename.split(',')[0]
