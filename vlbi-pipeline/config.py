#!/usr/bin/env python


AIPS_NUMBER = 12345   # Make sure you know what is meaning?
antname = 'VLBA'  # Antenna order for FITLD
geo_path = '/home/share/VLBI/geod/'
# file_path = sys.argv[1]
# TODO can be modify
file_path = '../data/'

#################
# Control Flags #
#################
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step1 = 0  # auto control of the flags in this block
step2 = 1  # Auto control of the second block
step3 = 0


# For BZ064A.idifits
calsource   = ['J2148+0657']            # calibrator        '' => automatically
target      = ['J1939-1002']         # target sourcer continuum source 
p_ref_cal   = ['J1939-1002']               
#mp_source = ['']  # fringe finder     '' => automatically

########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
AIPS_VERSION = '31DEC20'
version_date = '2016/04/06'
INTER_FLAG = 0  # interactive (1) or non-interactive (0)
DEF_DISKS = 1  # default AIPS disk to use (can be change anytime)

# todo check how to rename
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
inspect_flag    = 3                  # Run possm and snplt to check and run antab for EVN data : 0 mute, 1/2 plot, 3 auto
RFIck_tran = [0,23,0,0,0,24,0,0]
"""
################# todo
target_source = ''
phase_ref_source = ''


def_file = '/home/ykzhang/Scripts/BeSSel/def_bessel_vlbi-lba.py'

fr_path = '/home/ykzhang/VLBA/ba114/ba114b/BA114b/'

fit_path = '/home/ykzhang/VLBA/ba115/'  # not used
TECU_model = 'jplg'


split_outcl = 'SPLIT'


"""
