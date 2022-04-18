#!/usr/bin/env python

AIPS_VERSION = '31DEC20'
version_date = '2016/04/06'

# Download data from archive? not needed
download_flag = 0
# data file with geo data? (<0 for no geoblock)
geo_data_nr = 0
# data file with continuum data?
cont = 0
# data file with line data?
line = 0
# Run TECOR, EOPs, ATMOS, PANG, and position shift?
pr_prep_flag = 0
def_file = '/home/ykzhang/Scripts/BeSSel/def_bessel_vlbi-lba.py'

fr_path = '/home/ykzhang/VLBA/ba114/ba114b/BA114b/'

file_path = '/data/VLBI/VLBA/ba114/'
# file_path = sys.argv[1]
geo_path = '/home/ykzhang/Scripts/geod/'
fit_path = '/home/ykzhang/VLBA/ba115/'  # not used
TECU_model = 'jplg'

filename = 'test123.idifits'


max_files = 1024

outname = range(max_files)

outname[0] = filename.split(',')[0]

antname = 'VLBA'  # Antenna order for FITLD