#!/usr/bin/env python


AIPS_NUMBER = 1351   # Make sure you know what is meaning?
antname = 'VLBA'  # Antenna order for FITLD
geo_path = './geod/'
# file_path = sys.argv[1]
# TODO can be modify
#file_path = '../data/'
file_path = '/data/VLBI/VLBA/PG1351+640/BB203/BB203-UVFITS/'

#################
# Control Flags #
#################
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step1 = 0  # auto control of the flags in this block
step2 = 0  # Auto control of the second block
step3 = 1

#TODO
# For PG1351+640
calsource   = ['J1642+3948']            # calibrator        '' => automatically
#target      = ['PG1351+640']         # target sourcer continuum source 
target      = ['J1353+6345']         # target sourcer continuum source 
p_ref_cal   = ['J1339+6328']               
#mp_source = ['']  # fringe finder     '' => automatically

########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
AIPS_VERSION = '31DEC19'
version_date = '2016/04/06'
INTER_FLAG = 0  # interactive (1) or non-interactive (0)
DEF_DISKS = 1  # default AIPS disk to use (can be change anytime)
NCOUNT = 1  # How many files should be readin

# todo check how to rename
#filename = 'test123.idifits'
import sys
filename = sys.argv[2]
max_files = 16
outname = range(max_files)
outname[0] = filename.split('.')[0]


# Download data from archive? not needed
DOWNLOAD_FLAG = 0
# data file with geo data? (<0 for no geoblock)
geo_data_nr = 0
# Run TECOR, EOPs, ATMOS, PANG, and position shift?
pr_prep_flag = 0
inspect_flag = 0                  #,0,1,2,3 Run possm and snplt to check and run antab for EVN data : 0 mute, 1/2 plot, 3 auto
RFIck_tran = [0,0,0,0,0,0,0,0]
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
