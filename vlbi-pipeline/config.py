#!/usr/bin/env python

AIPS_NUMBER = 1351   # Make sure you know what is meaning?
antname = 'VLBA'  # Antenna order for FITLD
geo_path = './geod/'
#################
# Control Flags #
#################

#TODO
# For PG1351+640
#calsource   = ['J1706+1208']            # calibrator        '' => automatically
calsource   = ['J1642+3948']            # calibrator        '' => automatically
#target      = ['PG1351+640']         # target sourcer continuum source 
target      = ['J1702+1301']         # target sourcer continuum source 
p_ref_cal   = ['J1707+1331']               
#mp_source = ['']  # fringe finder     '' => automatically

########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
AIPS_VERSION = '31DEC19'
version_date = '2016/04/06'
INTER_FLAG = 0  # interactive (1) or non-interactive (0)
DEF_DISKS = 1  # default AIPS disk to use (can be change anytime)
NCOUNT = 1  # How many files should be readin

# Download data from archive? not needed
DOWNLOAD_FLAG = 0
# data file with geo data? (<0 for no geoblock)
geo_data_nr = 0
# Run TECOR, EOPs, ATMOS, PANG, and position shift?
pr_prep_flag = 0
#inspect_flag = 3                  #,0,1,2,3 Run possm and snplt to check and run antab for EVN data : 0 mute, 1/2 plot, 3 auto
#TODOTODO make sure this flag was between step1 and step2,
# set to 0 , then run step1, then set to 3, generate parm files, then run step2
inspect_flag = 3                  #,0,1,2,3 Run possm and snplt to check and run antab for EVN data : 0 mute, 1/2 plot, 3 auto
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

###########################################################################
########DO NOT EDIT UNLESS YOU KNOW THE MEANING############################
###########################################################################
# for networks that are not well constained with tgain(e.g. EVN)
matxl = [[0.89, 0.92, 0.79, 1.03, 0.9, 0.89, 0.79, 0.94, ],
            [1, 1, 1, 1, 0.43, 0.37, 0.31, 0.34, ],
            [1.1, 1.08, 1.23, 1.1, 1.11, 1.12, 1.12, 1.11, ],
            [1, 0.93, 0.97, 0.99, 1, 0.99, 0.98, 0.97, ],
            [1.01, 1.02, 1.02, 1, 1.02, 1.02, 1, 1.02, ],
            [1, 1, 1, 0.99, 0.96, 0.96, 0.95, 0.95, ],
            [0.95, 1.01, 0.96, 0.97, 0.99, 1.05, 1.07, 1.07, ],
            [0.92, 0.91, 0.93, 0.91, 0.95, 0.99, 1, 1.41, ],
            [1.09, 1.02, 1.1, 1.18, 1.23, 1.15, 1.15, 1.3, ],
            [0.82, 0.8, 0.84, 0.87, 0.85, 0.88, 0.91, 0.92, ],
            [0.7, 0.73, 0.71, 0.73, 0.75, 0.77, 0.78, 0.78, ],
            [0.96, 0.99, 1, 1.05, 1.07, 1.1, 1.14, 1.14, ],
            [1.07, 1.05, 1.02, 1.03, 1.05, 1.05, 1.1, 1.08, ],
            [1.14, 1.16, 1.19, 1.13, 1.12, 1.14, 1.18, 1.26, ]]
matxr = [[1.05, 1.17, 1.18, 1.02, 0.97, 1.27, 0.92, 1.28, ],
            [1, 1, 1, 1, 0.68, 0.51, 0.35, 0.35, ],
            [1.39, 1.39, 1.71, 1.43, 1.43, 1.5, 1.43, 1.41, ],
            [1.26, 1.12, 1.06, 1.24, 1.23, 1.1, 1.2, 1.19, ],
            [1.23, 1.25, 1.24, 1.23, 1.25, 1.24, 1.25, 1.23, ],
            [1.27, 1.27, 1.28, 1.24, 1.24, 1.24, 1.22, 1.23, ],
            [1.25, 1.45, 1.17, 1.25, 1.27, 1.4, 1.34, 1.38, ],
            [1.13, 1.14, 1.13, 1.12, 1.17, 1.23, 1.28, 1.58, ],
            [1.35, 1.26, 1.29, 1.38, 1.47, 1.42, 1.34, 1.53, ],
            [1.01, 1.01, 0.97, 1, 1.11, 1.17, 1.17, 1.18, ],
            [0.96, 0.99, 0.97, 0.99, 0.96, 0.99, 1.01, 1.03, ],
            [0.58, 0.54, 0.54, 0.58, 0.59, 0.63, 0.69, 0.69, ],
            [1.43, 1.39, 1.37, 1.37, 1.37, 1.36, 1.41, 1.4, ],
            [1.48, 1.47, 1.49, 1.46, 1.45, 1.45, 1.49, 1.58, ]]