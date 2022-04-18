#!/usr/bin/env ParselTongue

import time
import sys
#import pathlib

from AIPS import AIPS
import os
from config import *
import argparse
from config import AIPS_VERSION, AIPS_NUMBER, DEF_DISKS, split_outcl, antname
from utils import *
from make_utils import *
from run_tasks import *
from get_utils import *
from check_utils import *

# Init setting
aipsver = AIPS_VERSION
AIPS.userno =  AIPS_NUMBER
inter_flag = INTER_FLAG
antname = antname

# Setting the parameters
parser = argparse.ArgumentParser(description="VLBI pipeline")
parser.add_argument('aips-number', metavar='aips number', type=int, nargs='+', help='the AIPS number <keep only>')
parser.add_argument('fits_file', metavar='fits file', type=str, nargs='+', help='files file name')
#parser.add_argument('-p', '--file-path', type=pathlib.Path, default='/data/VLBI/VLBA/', help='the data path of fits file')
#parser.add_argument('-i', '--image-path', type=pathlib.Path, default='/data/VLBI/VLBA/images/', help='the data path of image file')
parser.add_argument('-o', '--output-filename', default='demo', help='the output file name')



def current_time():
    cur_time = time.strftime('%Y%m%d.%H%M%S')
    print (time.strftime('%Y%m%d.%H%M%S'))
    return cur_time

def mprint(intext, logfile):
    print(intext)
    f = open(logfile, 'a')
    f.writelines(intext + '\n')
    f.close()


calsource   = ''                     # calibrator        '' => automatically
target      = ['']                   # continuum sources '' => automatically
mp_source   = ['']                   # fringe finder     '' => automatically
mp_timera   = [0,0,0,0,0,0,0,0]      # constrain time range for fringe finder?
bandcal     = ['']                   # Bandpass calibrator

delzn_flag  =  0              # Use DELZN (1) or fit_geblocks (0)?
dual_geo    =  0              # Using dual frequency geodetic blocks?

geo_data_nr =  0              # data file with geo data? (<0 for no geoblock)
cont        =  2              # data file with continuum data?
line        =  1              # data file with line data?
                              # if you have only one dataset, use cont = line

cvelsource  = ['']            # line sources '' => calsource
vel         = [21]           # Velocity for cvel
# v1_old
#channel     = 1108             # channel used for fringe fit
#pos_shift   = {'G032.79+0.19'   : [-0.146,0.539],

channel     = 1054             # channel used for fringe fit
pos_shift   = {'G032.79+0.19'   : [-0.124,0.003],
               'J1853-0010' : [-0, +0.012],
               'J1857-0048' : [+0.005,+0.013],
               'J1848+0138': [+0.003, -0.001]}

                               # Which source should be shifted ''=calsource
                               # e.g. {'G211':[0.2,0.3], 'J0007':[0.1,0.3]}
                               # {'' : [0,0]} => no shift
#################
# Split Options #
#################

smooth       = [0,0,0]          # Smooth during split for line data
split_outcl  = 'SPLIT'          # outclass in SPLIT '' => 'SPLIT'

##################################
# Optional inputs for fringe fit #
##################################

[fr_n, fr_c, fr_d, fr_s] = ['','',1,1]
                                             # Input image to use in FRINGE:
                                             # ['NAME','CLASS',DISK,SEQUENCE]
smodel = [1,0]                 # SMODEL in FRING
solint = 0                     # SOLINT in FRING
nmaps  = 1                     # NMAPS in FRING

##############################################
# Optional imput for phased VLA observations #
##############################################

flux = {'' : [0,0,0,0]}         # Flux of cal source (for VLA)

######################
# Imaging Parameters #
######################

cellsize     = 0.0005          # CELLSIZE for IMAGR
imsize       = 2048            # IMSIZE for IMAGR
#bchan        = 901             # Start channel for data cube
#echan        = 1300            # End channel for data cube
#TODO
bchan        = 1054             # Start channel for data cube
echan        = 1054            # End channel for data cube
niter        = 250             # niter in imagr
uvwtfn       = 'N'             # UVWTFN in IMAGR
robust       =  0              # ROBUST in IMAGR
beam         = [0,0,0]         # Restoring beam: bmaj, bmin, PA
antennas     = [2,4,5,7,8,9]   # Also used for RPOSSM

######################
#   SAD Parameters   #
######################

min_snr      = 10                            # Fit only Peaks with SNR>min_snr
dyna         = 0.1                           # Don't fit peaks less than
                                             # dyna*peak in channel
####################
# Self Calibration #
####################

phase_loop = [30./60,20./60.]                # Solints for Phase selfcal
amp_loop   = [1200.,360, 60.,30.]
dofit      = [[0], [0], [0],[0]]



print("FILE NAME =========", filename[0])  # ,filename[1],filename[2])
print("OUT  NAME =========", outname[0])  # ,outname[1],outname[2])
print(sys.argv)
if (os.path.exists(outname[0]) == False):
    os.mkdir(outname[0])
logfile = outname[0] + '.log'
#################
# Control Flags #
#################
step1 = 1  # auto control of the flags in this block
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step2 = 1  # Auto control of the seond block
step3 = 1
##################################
# Data preparation and first prep#
##################################

load_flag = 0  # Load data from disk?
listr_flag = 0  # Print out LISTR?
dtsum_flag = 0  # Run dtsum to check antena participation?
tasav_flag = 0  # Run tasav on original tables?
geo_prep_flag = 0  # Run TECOR and EOP corrections? and uvflg for evn data
# get_key_flag    = 0        # Download key-file from archive
# RDBE_check      = 0        # Check Geoblock data for RDBE errors?
if step1 == 1:
    load_flag = 1
    listr_flag = 1
    tasav_flag = 1
    geo_prep_flag = 1
    dtsum_flag = 1
#########################################################################
# information to fill after first prep #
#########################################################################
## single step before step 2: find the calibrator scan as possm scan   ##
## and run possm, snplt(ty) to find refantenna and fill the rest info  ##
#########################################################################
possm_scan = [0, 16, 54, 0, 0, 16, 56, 0]
inspect_flag = 0  # Run possm and snplt to check and run antab for EVN data
quack_flag = 0  # Run quack if special considerations (e.g. EVN p-ref)

refant = 9  # refant=0 to select refant automatically
refant_candi = [1, 2, 7, 0]  # candidate refant for search in fringe
calsource = ['4C39.25']  # calibrator        '' => automatically
mp_source = ['4C39.25']  # fringe finder     '' => automatically
mp_timera = possm_scan  # constrain time range for fringe finder?
bandcal = ['4C39.25']  # Bandpass calibrator
flagver = 1  # Flag table version to be used
tyver = 1  # Tsys table version to be used
chk_trange = [0, 16, 50, 0, 1, 4, 40, 0]  # set the whole time range
dofit = 1
# dofit=  [-1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,-1]  #usually for EVN with tsys antenas

# tar_names=['PG0921+525','PG1004+130','PG1116+215','PG1211+143','PG1351+640',
tar_names = ['PG1448+273', 'PG1612+261']
# pref_names=['J0932+5306','J1002+1232','J1119+2226','J1213+1307','J1353+6324',
pref_names = ['J1453+2648', 'J1609+2641']

if step2 == 1:
    for i in range(len(tar_names)):
        target = [tar_names[i]]  # target sourcer
        p_ref_cal = [pref_names[i]]  # phase ref calbrator sources '' => automatically
        targets = [target[0], p_ref_cal[0]]
        if i == 0:
            apcal_flag = 1  # Do amplitude calibration?
            pang_flag = 1  # Run PANG?
            pr_fringe_flag = 1  # Do manual phase cal?
        else:
            apcal_flag = 0  # Do amplitude calibration?
            pang_flag = 0  # Run PANG?
            pr_fringe_flag = 0  # Do manual phase cal?
        do_fringe_flag = 1  # Do first run of fringe cal on all sources?
        plot_first_run = 1  # DO possm and snplt to check first run result?
        do_band_flag = 1
        split_1_flag = 1  # Split calibrated data in first run?
        #execfile(r'' + def_file)

#########################################################################
# second-run--data_calibration #
#########################################################################

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

do_gaincor_flag = 0  # set this and go back to step2s

###########################################################################
##################################
# Optional inputs for fringe fit #
##################################

# fr_files=['J0932-v1-mod2.fits','J1002-v1-mod2.fits','J1119-v1-mod2.fits','J1213-v1-mod2.fits','J1353-v1-mod2.fits','J1453-v1-mod2.fits','J1609-v1-mod2.fits']
# fr_nms=['J0932-fr','J1002-fr','J1119-fr','J1213-fr','J1353-fr','J1453-fr','J1609-fr']
fr_files = ['J1453-v1-mod2.fits', 'J1609-v1-mod2.fits']
fr_nms = ['J1453-fr', 'J1609-fr']
smodel = [0, 0]  # SMODEL in FRING
solint = 2  # SOLINT in FRING
nmaps = 1  # NMAPS  in FRING
# doband  = -1

if step3 == 1:
    for i in range(len(fr_files)):
        target = [tar_names[i]]  # target sourcer
        p_ref_cal = [pref_names[i]]  # phase ref calbrator sources '' => automatically
        targets = [target[0], p_ref_cal[0]]
        fr_file = fr_files[i]
        [fr_nm, fr_cls, fr_dsk, fr_sq] = [fr_nms[i], 'CLN', 1, 1]
        # Input image to use in FRINGE:
        # ['NAME','CLASS',DISK,SEQUENCE]
        ld_fr_fringe_flag = 1
        do_fr_fringe_flag = 1
        do_calib_1_flag = 1
        check_delay_rate = 1
        split_2_flag = 1
        #execfile(r'' + def_file)
# step3


# Which source should be shifted ''=calsource
# e.g. {'G211':[0.2,0.3], 'J0007':[0.1,0.3]}
# {'' : [0,0]} => no shift
#################
# Split Options #
#################


##############################################
# Optional imput for phased VLA observations #
##############################################

######################
# Imaging Parameters #
######################

# cellsize     = 0.0005          # CELLSIZE for IMAGR
# imsize       = 2048            # IMSIZE for IMAGR
# bchan        = 901             # Start channel for data cube
# echan        = 1300            # End channel for data cube
# TODO
# bchan        = 1054             # Start channel for data cube
# echan        = 1054            # End channel for data cube
# niter        = 250             # niter in imagr
# uvwtfn       = 'N'             # UVWTFN in IMAGR
# robust       =  0              # ROBUST in IMAGR
# beam         = [0,0,0]         # Restoring beam: bmaj, bmin, PA
# antennas     = [2,4,5,7,8,9]   # Also used for RPOSSM

######################
#   SAD Parameters   #
######################

# min_snr      = 10                            # Fit only Peaks with SNR>min_snr
# dyna         = 0.1                           # Don't fit peaks less than
# dyna*peak in channel
####################
# Self Calibration #
####################

# phase_loop = [30./60,20./60.]                # Solints for Phase selfcal
# amp_loop   = [1200.,360, 60.,30.]
# dofit      = [[0], [0], [0],[0]]

def run_main(logfile):
    n = DEF_DISKS
    defdisk = 1  # Default AIPS disk to use (can be changed later)

    #############################################################################
    ###                  Do not change or move this part                     ####
    [filename, outname, outclass] = [range(n), range(n), range(n)]
    [nfiles, ncount, doconcat] = [range(n), range(n), range(n)]
    [outdisk, flagfile, antabfile] = [range(n), range(n), range(n)]
    for i in range(n):
        [flagfile[i], antabfile[i], outdisk[i]] = ['', '', defdisk]
        [nfiles[i], ncount[i], doconcat[i]] = [0, 1, -1]
    #############################################################################
    ###############
    # Input Files #
    ###############
    # This only for single file
    # print("FILE PATH =========",file_path)
    filename[0] = 'ba114a.idifits'
    outname[0] = 'BA114a'
    outclass[0] = 'UVDATA'
    nfiles[0] = 1  # FITLD parameter NFILES
    ncount[0] = 1  # FITLD parameter NCOUNT
    doconcat[0] = 1  # FITLD parameter DOCONCAT
    # Optional parameters for each file
    # outdisk[0]   = 3                  # AIPS disk for this file (if != defdisk)
    # usually for EVN stations
    # flagfile[0]  = 'es094.uvflg'   # flag file for UVFLG
    # antabfile[0] = 'es094.antab'  # antab file for ANTAB

    antname = 'VLBA'  # Antenna order for FITLD
    refant = 4  # refant=0 to select refant automatically
    AIPS.log = open(logfile, 'a')

    mprint('#############################################', logfile)
    mprint('### Using definition file from ' + version_date + ' ###', logfile)
    mprint('### Using AIPS Version ' + aipsver + (19 - len(aipsver)) * ' ' + '###', logfile)
    mprint('#############################################', logfile)

    debug = 1
    n = DEF_DISKS

    try:
        debug = debug
    except:
        debug = 0

    try:
        if inter_flag == 0:
            print
            'Running in non-interactive mode.'
        else:
            print
            'Running in interactive mode.'
    except:
        inter_flag = 1
        print
        'Running in interactive mode.'

    try:
        if split_outcl == '':
            split_outcl = 'SPLIT'
        else:
            if len(split_outcl) > 6:
                split_outcl = split_outcl[0:6]
                mprint('################################################', logfile)
                mprint('split_outcl longer than 6 characters. Truncating', logfile)
                mprint('it to: ' + split_outcl, logfile)
                mprint('################################################', logfile)
    except:
        split_outcl = 'SPLIT'

    ##############################################################################
    #####                 Set default parameters, if not set                 #####
    ##############################################################################
    if 'ld_fr_fringe_flag' in locals() and globals():
        pass
    else:
        ld_fr_fringe_flag = 0
    if 'do_fr_fringe_flag' in locals() and globals():
        pass
    else:
        do_fr_fringe_flag = 0
    if 'do_calib_1_flag' in locals() and globals():
        pass
    else:
        do_calib_1_flag = 0
    if 'check_delay_rate' in locals() and globals():
        pass
    else:
        check_delay_rate = 0
    if 'split_2_flag' in locals() and globals():
        pass
    else:
        split_2_flag = 0

    if 'apcal_flag' in locals() and globals():
        pass
    else:
        apcal_flag = 0
    if 'pang_flag' in locals() and globals():
        pass
    else:
        pang_flag = 0
    if 'do_fringe_flag' in locals() and globals():
        pass
    else:
        do_fringe_flag = 0
    if 'plot_first_run' in locals() and globals():
        pass
    else:
        plot_first_run = 0
    if 'split_1_flag' in locals() and globals():
        pass
    else:
        split_1_flag = 0

    if 'pr_fringe_flag' in locals() and globals():
        pass
    else:
        pr_fringe_flag = 0
    if 'delzn_flag' in locals() and globals():
        pass
    else:
        delzn_flag = 0
    if 'restore_fg_flag' in locals() and globals():
        pass
    else:
        restore_fg_flag = 0
    if 'restore_su_flag' in locals() and globals():
        pass
    else:
        restore_su_flag = 0
    if 'do_gaincor_flag' in locals() and globals():
        pass
    else:
        do_gaincor_flag = 0
    if 'split_flag' in locals() and globals():
        pass
    else:
        split_flag = 0
    if 'ma_imagr_flag' in locals() and globals():
        pass
    else:
        ma_imagr_flag = 0
    if 'co_imagr_flag' in locals() and globals():
        pass
    else:
        co_imagr_flag = 0
    if 'cube_imagr_flag' in locals() and globals():
        pass
    else:
        cube_imagr_flag = 0
    if 'fr_nm' in locals() and globals():
        pass
    else:
        fr_nm = ''
    if 'fr_cls' in locals() and globals():
        pass
    else:
        fr_cls = ''
    if 'fr_dsk' in locals() and globals():
        pass
    else:
        fr_dsk = defdisk
    if 'fr_sq' in locals() and globals():
        pass
    else:
        fr_sq = 1
    if 'nmaps' in locals() and globals():
        pass
    else:
        nmaps = 1
    if 'flux' in locals() and globals():
        pass
    else:
        flux = {'': [0, 0, 0, 0]}
    if 'niter' in locals() and globals():
        pass
    else:
        niter = 100
    if 'grid_flag' in locals() and globals():
        pass
    else:
        grid_flag = 0
    if 'gridsource' in locals() and globals():
        pass
    else:
        gridsource = ''
    if 'n_grid' in locals() and globals():
        pass
    else:
        n_grid = 0
    if 'm_grid' in locals() and globals():
        pass
    else:
        m_grid = 0
    if 'grid_offset' in locals() and globals():
        pass
    else:
        grid_offset = 0
    if 'dual_geo' in locals() and globals():
        pass
    else:
        dual_geo = 0
    if 'arch_user' in locals() and globals():
        pass
    else:
        arch_user = ''
    if 'arch_pass' in locals() and globals():
        pass
    else:
        arch_pass = ''
    if 'file' in locals() and globals():
        pass
    else:
        file = []
    if 'kntr_flag' in locals() and globals():
        pass
    else:
        kntr_flag = 0
    if 'fittp_flag' in locals() and globals():
        pass
    else:
        fittp_flag = 0
    if 'get_key_flag' in locals() and globals():
        pass
    else:
        get_key_flag = 0
    if 'code' in locals() and globals():
        pass
    else:
        code = ''
    if 'max_ant' in locals() and globals():
        pass
    else:
        max_ant = 12
    if 'phase_cal_flag' in locals() and globals():
        pass
    else:
        phase_cal_flag = 0
    if 'amp_cal_flag' in locals() and globals():
        pass
    else:
        amp_cal_flag = 0
    if 'imna' in locals() and globals():
        pass
    else:
        imna = ''
    if 'phase_target_flag' in locals() and globals():
        pass
    else:
        phase_target_flag = ''
    if 'amp_target_flag' in locals() and globals():
        pass
    else:
        amp_target_flag = ''
    if 'antennas' in locals() and globals():
        pass
    else:
        antennas = [0]
    if 'refeed_flag' in locals() and globals():
        pass
    else:
        refeed_flag = 0
    if 'plot_tables' in locals() and globals():
        pass
    else:
        plot_tables = -1
    if 'dofit' in locals() and globals():
        pass
    else:
        dofit = [0]
    if 'apply_selfcal' in locals() and globals():
        pass
    else:
        apply_selfcal = 0
    if 'tysmo_flag' in locals() and globals():
        pass
    else:
        tysmo_flag = 0
    if 'solint' in locals() and globals():
        pass
    else:
        solint = 0
    if 'smodel' in locals() and globals():
        pass
    else:
        smodel = [1, 0]
    if 'uvwtfn' in locals() and globals():
        pass
    else:
        uvwtfn = ''
    if 'robust' in locals() and globals():
        pass
    else:
        robust = 0
    if 'bandcal' in locals() and globals():
        pass
    else:
        bandcal = ['']
    if 'do_band_flag' in locals() and globals():
        pass
    else:
        do_band_flag = 0
    if 'dpfour' in locals() and globals():
        pass
    else:
        dpfour = 0
    if 'min_elv' in locals() and globals():
        pass
    else:
        min_elv = 0
    if 'rpossm_flag' in locals() and globals():
        pass
    else:
        rpossm_flag = 0
    if 'ma_sad_flag' in locals() and globals():
        pass
    else:
        ma_sad_flag = 0
    if 'plot_map' in locals() and globals():
        pass
    else:
        plot_map = 0
    if 'min_snr' in locals() and globals():
        pass
    else:
        min_snr = 7
    if 'smooth' in locals() and globals():
        pass
    else:
        smooth = [0]
    if 'beam' in locals() and globals():
        pass
    else:
        beam = [0, 0, 0]
    if 'RDBE_check_flag' in locals() and globals():
        pass
    else:
        RDBE_check_flag = 0
    if 'TECU_model' in locals() and globals():
        pass
    else:
        TECU_model = 'jplg'

    ##############################################################################
    # Start main script

    mprint('######################', logfile)
    mprint(get_time(), logfile)
    mprint('######################', logfile)

    refant_flag = 0
    refant = 9  # refant=0 to select refant automatically
    if refant == 0:
        refant_flag = 1

    download_flag = DOWNLOAD_FLAG
    if download_flag == 1:
        try:
            if os.path.exists(mail_path):
                (arch_user, arch_pass, prop_dir, file, m) = read_mail(mail_path, arch_user, arch_pass, file, inter_flag)
        except:
            if arch_user != 'nopass':
                (file, m) = get_download_names(arch_user, arch_pass, file)

                mprint('########################################', logfile)
                mprint('Found ' + str(m) + ' files to download from archive.', logfile)
                if m < n:
                    mprint('Not what expected! Using only ' + str(m)
                           + ' files.', logfile)
                    n = m
                elif m > n:
                    mprint('Not what expected! Making ' + str(m - n)
                           + ' dummy files', logfile)
                    for i in range(m - n):
                        filename.append('Dummy' + str(i))
                        outname.append('Dummy' + str(i))
                        outclass.append('UVDATA')
                        nfiles.append(0)
                        ncount.append(1)
                        doconcat.append(-1)
                        flagfile.append('')
                        antabfile.append('')
                        outdisk.append(defdisk)
                    n = m
                mprint('########################################', logfile)
            elif arch_user == 'nopass' and file[0] == 0:
                mprint('###########################################', logfile)
                mprint('Need to specify filenames for public data.', logfile)
                mprint('###########################################', logfile)
                sys.exit()

        for i in range(n):
            mprint('##################################', logfile)
            mprint('Download file ' + str(i) + ' from archive.', logfile)
            download(arch_user, arch_pass, file[i], file_path, filename[i])
            mprint(get_time(), logfile)
            mprint('##################################', logfile)

    if load_flag == 1:
        for i in range(n):
            loadindx(file_path, filename[i], outname[i], outclass[i], outdisk[i],
                     nfiles[i], ncount[i], doconcat[i], antname, logfile)

    data = range(n)

    mprint('##################################', logfile)
    for i in range(n):
        data[i] = AIPSUVData(outname[i], outclass[i], int(outdisk[i]), int(1))
        if data[i].exists():
            data[i].clrstat()
        if dtsum_flag == 1:
            rundtsum(data[i])
            if listr_flag == 1:
                runlistr(data[i])
            if get_key_flag == 1:
                get_key_file(data[i], code)
    mprint('##################################', logfile)

    ###########################
    # Data Preparation

    if geo_data_nr < 0:
        do_geo_block = 0
    else:
        do_geo_block = 1

    pr_data_nr = []

    if cont != -1:
        pr_data_nr.append(cont)
        if line != cont:
            pr_data_nr.append(line)

    check_data(data, n, geo_data_nr, cont, line, logfile)

    # Download TEC maps and EOPs

    if pr_prep_flag == 1 or geo_prep_flag == 1:
        if do_geo_block == 1:
            (year, month, day) = get_observation_year_month_day(data[geo_data_nr])
            num_days = get_num_days(data[geo_data_nr])
        else:
            (year, month, day) = get_observation_year_month_day(data[pr_data_nr[0]])
            num_days = get_num_days(data[pr_data_nr[0]])

        doy = get_day_of_year(year, month, day)

        get_TEC(year, doy, TECU_model, geo_path)
        get_eop(geo_path)

        if num_days == 2: get_TEC(year, doy + 1, TECU_model, geo_path)

    mprint('######################', logfile)
    mprint(get_time(), logfile)
    mprint('######################', logfile)

    ###########################b########################################
    # Geodetic block analysis

    if RDBE_check_flag == 1:
        blocks = check_RDBE(data[geo_data_nr], logfile, inter_flag, 'GEO')

    if geo_prep_flag > 0:
        geo_data = data[geo_data_nr]
        # runuvflg(geo_data,flagfile[geo_data_nr],logfile)
        check_sncl(geo_data, 0, 1, logfile)
        if geo_data.header['telescop'] == 'EVN':
            if geo_prep_flag == 1:
                runTECOR(geo_data, year, doy, num_days, 3, TECU_model)
            else:
                runtacop(geo_data, geo_data, 'CL', 1, 3, 0)
        else:
            if geo_prep_flag == 1:
                runTECOR(geo_data, year, doy, num_days, 2, TECU_model)
            else:
                runtacop(geo_data, geo_data, 'CL', 1, 2, 0)
            runeops(geo_data, geo_path)

        geo_data = data[geo_data_nr]
        sx_geo = False
        if check_sx(geo_data, logfile):
            mprint('####################################', logfile)
            mprint('Geoblock observation in SX mode', logfile)
            mprint('####################################', logfile)
            (geo_data_l, geo_data_h) = split_sx(geo_data, 1)
            if dual_geo > 0:
                sx_geo = True
                cw_geo = False
            geo_data = geo_data_h
        elif check_clh(geo_data, logfile):
            mprint('#########################################', logfile)
            mprint('Geoblock observation in wide C-band mode', logfile)
            mprint('########################################', logfile)
            (geo_data_l, geo_data_h) = split_clh(geo_data, 1)
            if dual_geo > 0:
                sx_geo = True
                cw_geo = True
            geo_data = geo_data_h

    if do_geo_block == 1:
        geo_data = data[geo_data_nr]
        sx_geo = False
        if check_sx(geo_data, logfile):
            mprint('####################################', logfile)
            mprint('Geoblock observation in SX mode', logfile)
            mprint('####################################', logfile)
            (geo_data_l, geo_data_h) = split_sx(geo_data, 0)
            if dual_geo > 0:
                sx_geo = True
                cw_geo = False
            if geo_data_h.exists(): geo_data = geo_data_h
        elif check_clh(geo_data, logfile):
            mprint('#########################################', logfile)
            mprint('Geoblock observation in wide C-band mode', logfile)
            mprint('########################################', logfile)
            (geo_data_l, geo_data_h) = split_clh(geo_data, 0)
            if dual_geo > 0:
                sx_geo = True
                cw_geo = True
            if geo_data_h.exists(): geo_data = geo_data_h

        if delzn_flag == 0:
            if (os.path.exists('geoblock') == False):
                os.mkdir('geoblock')
    ###################################################################
    # Data inspect

    if inspect_flag == 1:
        # if antname == 'EVN':
        # runantab(data[0],antabfile[0])
        possmplot(data[0], sources='', timer=possm_scan, gainuse=3, flagver=0, stokes='HALF', nplot=9, bpv=0,
                  ant_use=[0])
        runsnplt(data[0], inver=1, inex='TY', sources='', optype='TSYS', nplot=4, timer=[])
        print
        data[0].sources

    mprint('############################', logfile)
    mprint('Data inspection before apcal', logfile)
    mprint('############################', logfile)
    ###################################################################
    # Phase referencing analysis

    print(data[cont])

    line_data = data[line]
    cont_data = data[cont]

    if RDBE_check_flag == 2:
        newdata = get_phasecal_sources(cont_data, mp_source, logfile)
        blocks = check_RDBE(newdata, logfile, inter_flag, 'CONT')

    if line_data.sources == cont_data.sources:
        pass
    else:
        mprint('########################################################', logfile)
        mprint('### Sources in line and continuum files not idential ###', logfile)
        mprint('########################################################', logfile)
        sys.exit()

    if do_geo_block == 1 and pr_prep_flag == 1 and delzn_flag == 0:
        for i in pr_data_nr:
            if (get_ant(geo_data) == get_ant(data[i])):
                mprint('Antennas identical in geoblock data and file ' + str(i), logfile)
            else:
                mprint('## ATTENTION ## ATTENTION ## ATTENTION ##', logfile)
                mprint('Antennas different for geoblock data and file ' + str(i), logfile)
                mprint('## ATTENTION ## ATTENTION ## ATTENTION ##', logfile)
        mprint('####################################', logfile)
        # +++ ZB
        # checkatmos(inter_flag, logfile)
        # --- ZB
        mprint('####################################', logfile)

    n = 0
    pr_data = 0
    for i in pr_data_nr:
        n = n + 1
        pr_data = data[i]
        mprint('#######################################', logfile)
        mprint('Processing phase-ref file: ' + outname[i], logfile)
        mprint('#######################################', logfile)

        if tasav_flag == 1:
            if flagfile[i] != '':
                runuvflg(pr_data, flagfile[i], logfile)
        if antabfile[i] != '':
            runantab(pr_data, antabfile[i])
        runtasav(pr_data, i, logfile)

        if restore_su_flag == 1:
            restore_su(pr_data, logfile)

        if restore_fg_flag == 1:
            restore_fg(pr_data, logfile)

        if pr_prep_flag > 0:
            runuvflg(pr_data, flagfile[i], logfile)
            check_sncl(pr_data, 0, 1, logfile)
            if pr_data.header['telescop'] == 'EVN':
                if pr_prep_flag == 1:
                    runTECOR(pr_data, year, doy, num_days, 3, TECU_model)
                else:
                    runtacop(pr_data, pr_data, 'CL', 1, 3, 0)
            else:
                if pr_prep_flag == 1:
                    runTECOR(pr_data, year, doy, num_days, 2, TECU_model)
                else:
                    runtacop(pr_data, pr_data, 'CL', 1, 2, 0)
                runeops(pr_data, geo_path)

            if refant_flag == 1:
                refant = select_refant(pr_data)
            if do_geo_block == 1:
                if delzn_flag == 1:
                    atmos_file = 'DELZN.FITS'
                else:
                    geo_data = data[geo_data_nr]
                    # +++ ZB
                    # make_name_atmos(geo_data)
                    # --- ZB
                    atmos_file = 'ATMOS_NAME.FITS'
                runatmos(pr_data, atmos_file)
                if sx_geo == True and dual_geo == 1:
                    ionos_file = 'IONOS_NAME.FITS'
                    make_name_ionos(geo_data)
                    runionos(pr_data, ionos_file)
                runpang(pr_data)
                for source in pos_shift:
                    [ra, dec] = [pos_shift[source][0], pos_shift[source][1]]
                    if ra != 0 or dec != 0:
                        if source == '':
                            source = findcal(pr_data, '')
                        mprint('###############################' +
                               '###########################', logfile)
                        mprint('Shift ' + source + ' by ' + str(ra) +
                               ' arcsec in RA and ' + str(dec) +
                               ' arcsec in DEC', logfile)
                        mprint('###############################' +
                               '###########################', logfile)
                        shift_pos(pr_data, source, ra, dec, 4, 4)
            else:
                mprint('####################################', logfile)
                mprint('Using no ATMOS.FITS file', logfile)
                mprint('####################################', logfile)
                runpang2(pr_data)
                for source in pos_shift:
                    [ra, dec] = [pos_shift[source][0], pos_shift[source][1]]
                    if ra != 0 or dec != 0:
                        if source == '':
                            source = findcal(pr_data, '')
                        mprint('####################################' +
                               '################################', logfile)
                        mprint('Shift ' + source + ' by ' + str(ra) +
                               ' arcsec in RA and ' + str(dec) +
                               ' arcsec in DEC', logfile)
                        mprint('####################################' +
                               '################################', logfile)
                        shift_pos(pr_data, source, ra, dec, 4, 4)

        if quack_flag == 1:  # for EVN
            runtacop(pr_data, pr_data, 'FG', 1, 2, 1)
            begquack(pr_data, [0], 30. / 60., 2)
            endquack(pr_data, [0], 5. / 60., 2)

        if apcal_flag == 1:
            vla_pres = False
            check_sncl(pr_data, 0, 3, logfile)
            if flux.items()[0][0] != '':
                ants = get_ant(pr_data)
                for ant in ants:
                    if ants[ant] == 'Y':
                        vla = ant
                        vla_pres = True
                        runquack(pr_data, [ant], 10. / 60.)
                sources = get_sources(pr_data)
                for entry in sources:
                    run_setjy(pr_data, entry, [1, 0, 0, 0])
            for entry in flux:
                if entry != '':
                    run_setjy(pr_data, entry, flux[entry])
            if refant_flag == 1:
                refant = select_refant(pr_data)
            # if antabfile[i]!='':
            #   runantab(pr_data,antabfile[i])
            if tysmo_flag == 1:
                runtysmo(pr_data, 90, 10)
        print
        pr_data.header['telescop']
        if pr_data.header['telescop'] == 'EVN':
            runapcal(pr_data, tyver, 1, 1, dofit, 'GRID')
            runclcal(pr_data, 1, 3, 4, '', 1, refant)
        runtacop(pr_data, pr_data, 'SN', 1, 2, 1)
        runtacop(pr_data, pr_data, 'CL', 4, 5, 1)
    if antname == 'VLBA':
        runaccor(pr_data)
        runclcal(pr_data, 1, 3, 4, 'self', 1, refant)
        runapcal(pr_data, tyver, 1, 2, 1, 'GRID')
        runclcal(pr_data, 2, 4, 5, '', 1, refant)
    else:  # for LBA
        runaccor(pr_data)
        runclcal(pr_data, 1, 3, 4, 'self', 1, refant)
        runapcal(pr_data, tyver, 1, 2, -1, 'GRID')
        runclcal(pr_data, 2, 4, 5, '', 1, refant)
        #            if vla_pres:
        #                runclcal2(pr_data, 2, 5, 6, '', 1, refant, [-vla],
        #                          [''])
        #                runclcal2(pr_data, 2, 5, 6, '', 1, refant, [vla],
        #                          [flux.items()[0][0]])
        #            else:
        #                runclcal(pr_data, 2, 5, 6, '',  1, refant)

    mprint('######################', logfile)
    mprint(get_time(), logfile)
    mprint('######################', logfile)


    if pang_flag == 1:
        check_sncl(pr_data, 2, 5, logfile)
        runpang2(pr_data)
        mprint('######################', logfile)
        mprint('finish pang', logfile)
        mprint('######################', logfile)

    if pr_fringe_flag == 1:
        mprint('######################', logfile)
        mprint('Begin mannual phase-cal', logfile)
        mprint('######################', logfile)
        check_sncl(pr_data, 2, 6, logfile)
        # if refant_flag==1:
        #    refant=select_refant2(pr_data, logfile)
        so, ti = man_pcal(pr_data, refant, mp_source, mp_timera, debug, logfile, dpfour)
        print(so, ti)
    if n == 1:
        so_ti = [so, ti]
    if n == 2:
        if so_ti[0] == so and so_ti[1] == ti:
            mprint('#############################################', logfile)
            mprint('### Both manual phasecal scans identical. ###', logfile)
            mprint('#############################################', logfile)
        else:
            mprint('#############################################', logfile)
            mprint('### Manual phasecal scans different.      ###', logfile)
            mprint('### Select one manually.                  ###', logfile)
            mprint('#############################################', logfile)
            sys.exit()
        # runclcal(pr_data, 3, 6, 7, '', 0, refant,[0], [''])
    runclcal2(pr_data, 3, 6, 7, '2pt', 0, refant, [0], mp_source, '')
    if do_fringe_flag == 1:
        mprint('######################', logfile)
        mprint('Begin first fringe', logfile)
        mprint('######################', logfile)
        check_sncl(pr_data, 3, 7, logfile)
        fringecal_ini(pr_data, refant, refant_candi, calsource[0], 7, 1, solint, -1, 0)
        fringecal_ini(pr_data, refant, refant_candi, p_ref_cal[0], 7, 1, solint, -1, 0)
        # fringecal_ini(pr_data,refant, refant_candi, p_ref_cal,7,1,solint,-1,0)
        runclcal2(pr_data, 4, 7, 8, 'ambg', -1, refant, [0], calsource, calsource)
        runclcal2(pr_data, 5, 7, 9, 'ambg', 1, refant, [0], p_ref_cal[0], targets)
    if do_fringe_flag == 2:
        mprint('######################', logfile)
        mprint('Begin first fringe', logfile)
        mprint('######################', logfile)
        check_sncl(pr_data, 3, 7, logfile)
        fringecal_ini(pr_data, refant, refant_candi, calsource[0], 7, 1, solint, -1, 0)
        fringecal_ini(pr_data, refant, refant_candi, targets, 7, 1, solint, -1, 0)
        runclcal2(pr_data, 4, 7, 8, 'ambg', -1, refant, [0], calsource, calsource)
        runclcal2(pr_data, 5, 7, 9, 'ambg', -1, refant, [0], targets, targets)
        # fringecal_ini(indata, refant, refant_candi, calsource, gainuse, flagver, solint, doband, bpver)
    if plot_first_run == 1:
        # check_sncl(pr_data,5,7,logfile)
        runsnplt(pr_data, inver=9, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='DELA', nplot=4, timer=[])
        runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='RATE', nplot=4, timer=[])
        possmplot(pr_data, sources=p_ref_cal[0], timer=chk_trange, gainuse=9, flagver=flagver, stokes='HALF', nplot=9, bpv=0,
                  ant_use=[0])
    mprint('######################', logfile)
    mprint(get_time(), logfile)
    mprint('######################', logfile)
    if do_band_flag == 1:
        check_sncl(pr_data, 5, 9, logfile)
    if pr_data.table_highver('AIPS BP') >= 1:
        pr_data.zap_table('AIPS BP', -1)
        do_band(pr_data, bandcal, 8, 1, logfile)
    else:
        do_band(pr_data, bandcal, 8, 1, logfile)
        possmplot(pr_data, sources=p_ref_cal[0], timer=chk_trange, gainuse=9, flagver=0, stokes='HALF', nplot=9, bpv=1,
                  ant_use=[0])
        possmplot(pr_data, sources=bandcal[0], timer=possm_scan, gainuse=8, flagver=0, stokes='HALF', nplot=9, bpv=1,
                  ant_use=[0])

    line_data = data[line]
    cont_data = data[cont]
    line_data2 = AIPSUVData(line_data.name, line_data.klass, line_data.disk, 2)
    cont_data2 = AIPSUVData(cont_data.name, cont_data.klass, cont_data.disk, 2)

    if bandcal == ['']:
        doband = -1
        bpver = -1
    else:
        doband = 1
        bpver = 1

    if split_1_flag == 1:
        check_sncl(cont_data, 5, 9, logfile)
        run_split2(cont_data, calsource[0], 8, split_outcl, doband, bpver, flagver)
        run_split2(cont_data, p_ref_cal[0], 9, split_outcl, doband, bpver, flagver)
        run_split2(cont_data, target[0], 9, split_outcl, doband, bpver, flagver)
        if len(p_ref_cal) >= 2:
            run_split2(cont_data, p_ref_cal[1], 9, split_outcl, doband, bpver, flagver)
        # run_fittp_data(source, split_outcl, defdisk, logfile)

    if do_gaincor_flag == 1:  # for EVN ususally
        # runtacop(cont_data,cont_data, 'CL', 9, 10, 1)
        gcal_app(cont_data, matxl, matxr, 5)
        # run_split2(cont_data, p_ref_cal[0], 9, split_outcl, doband, bpver, flagver)
    ##up: zyk++

###################################################################

    ##zyk+++
    if ld_fr_fringe_flag == 1:
        fr_image = AIPSImage(fr_nm, fr_cls, fr_dsk, fr_sq)
        if fr_image.exists():
            pass
        else:
            loadfr(fr_path, fr_file, fr_nm, fr_cls, fr_dsk, antname, logfile)

    if do_fr_fringe_flag == 1:
        check_sncl(cont_data, 3, 7, logfile)
        fringecal(cont_data, fr_image, nmaps, 7, refant, refant_candi, p_ref_cal[0], solint, smodel, doband, bpver, dpfour, logfile)
        runclcal2(cont_data, 4, 7, 8, 'AMBG', -1, refant, [0], p_ref_cal[0], targets)

    if do_calib_1_flag == 1:
        check_sncl(cont_data, 4, 8, logfile)
        calib_1(cont_data, fr_image, 8, refant, 5, doband, bpver, p_ref_cal[0], flagver, solint)
        runclcal2(cont_data, 5, 8, 9, '2PT', -1, refant, [0], p_ref_cal[0], targets)

    if check_delay_rate == 1:
        # chk_sn_cl(cont_data,6,10,p_ref_cal[0],chk_trange,1)
        chk_sn_cl(cont_data, 5, 9, p_ref_cal[0], chk_trange, 1)
        runsnplt(pr_data, inver=8, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=9, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='DELA', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='RATE', nplot=4, timer=[])
        runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='DELA',nplot=4,timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='RATE',nplot=4,timer=[])

    if split_2_flag >= 1:
        # check_sncl(cont_data, 6, 10,logfile)
        check_sncl(cont_data, 5, 9, logfile)
        # run_split2(cont_data, p_ref_cal[0], 10, 'SCL10', doband, bpver, flagver)
        run_split2(cont_data, target[0], 8, 'SCL10', doband, bpver, flagver)
        # run_split2(cont_data, p_ref_cal[0], 11, 'SCL11', doband, bpver, flagver)
        run_split2(cont_data, target[0], 9, 'SCL11', doband, bpver, flagver)
        if split_2_flag >= 2:
            run_split2(cont_data, p_ref_cal[0], 8, 'SCL10', doband, bpver, flagver)
        run_split2(cont_data, p_ref_cal[0], 9, 'SCL11', doband, bpver, flagver)

    if split_flag == 1:

        split_sources = get_split_sources(cont_data, target, cvelsource, calsource)

        if cont_data2.exists():
            check_sncl(cont_data2, 5, 8, logfile)
            run_split(cont_data2, split_sources, split_outcl, doband, bpver)
        else:
            check_sncl(cont_data, 4, 8, logfile)
            run_split(cont_data, split_sources, split_outcl, doband, bpver)

        cvelsource = findcvelsource(line_data, cvelsource)

        if line_data2.exists():
            check_sncl(line_data2, 4, 8, logfile)
            run_masplit(line_data2, cvelsource, split_outcl, doband, bpver, smooth, channel)
        else:
            check_sncl(line_data, 4, 8, logfile)
            run_masplit(line_data, cvelsource, split_outcl, doband, bpver, smooth, channel)


###########################################################################

    if phase_cal_flag == 1:
        source = calsource
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        cal_ants = antennas
        im_ants = []
        for entry in dofit[0]:
            im_ants.append(-entry)

        for i in range(len(phase_loop)):
            cal_data = phase_selfcal(indata, source, phase_loop[i], line_data.disk,
                                     niter, cellsize, imsize, logfile, imna,
                                     cal_ants, im_ants, refant, fr_image, beam)
            indata = cal_data
        mprint('########################################################', logfile)

    if amp_cal_flag == 1:
        source = calsource
        if len(dofit) != len(amp_loop):
            dofit = range(amp_loop)
            mprint('dofit and amp_loop not equal length, solving for all antennas', logfile)
            for i in range(len(dofit)):
                dofit[i] = 0

        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        indata = check_cal(indata, source, outdisk, logfile, imna)
        for i in range(len(amp_loop)):
            cal_data = amp_selfcal(indata, source, amp_loop[i], line_data.disk,
                                   niter, cellsize, imsize, logfile, imna, antennas,
                                   refant, dofit[i], beam)
            indata = cal_data
        mprint('########################################################', logfile)

    if refeed_flag == 1:

        source = calsource
        if imna == '':
            outname = source
        else:
            outname = source[:11 - len(imna)] + '-' + imna
        nimage = 1
        while AIPSImage(outname, 'ICL001', line_data.disk, nimage + 1).exists():
            nimage += 1

        model = AIPSImage(outname, 'ICL001', line_data.disk, nimage)

        if cont_data2.exists():
            mprint('Using shifted data (CVEL).', logfile)
            cont_used = cont_data2
        else:
            mprint('Using unshifted data (CVEL).', logfile)
            cont_used = cont_data

        check_sncl(cont_used, 3, 7, logfile)
        fringecal(cont_used, model, nmaps, refant, calsource, solint, smodel, doband, bpver, dpfour, logfile)
        if snflg_flag == 1:
            runsnflg(cont_used, 4, calsource)
        if min_elv > 0:
            run_elvflag(cont_used, min_elv, logfile)
        runclcal(cont_used, 4, 7, 8, '', 1, refant)
        run_snplt(cont_used, inter_flag)

        mprint('######################', logfile)
        mprint(get_time(), logfile)
        mprint('######################', logfile)

        split_sources = get_split_sources(cont_data, target, cvelsource, calsource)

        if cont_data2.exists():
            check_sncl(cont_data2, 4, 8, logfile)
            run_split(cont_data2, split_sources, split_outcl, doband, bpver)
        else:
            check_sncl(cont_data, 4, 8, logfile)
            run_split(cont_data, split_sources, split_outcl, doband, bpver)

        cvelsource = findcvelsource(line_data, cvelsource)

        if line_data2.exists():
            check_sncl(line_data2, 4, 8, logfile)
            run_masplit(line_data2, cvelsource, split_outcl, doband, bpver, smooth, channel)
        else:
            check_sncl(line_data, 4, 8, logfile)
            run_masplit(line_data, cvelsource, split_outcl, smooth, channel)

        split_sources = get_split_sources(cont_data, target, cvelsource, calsource)

        for source in split_sources:
            split_data = AIPSUVData(source, split_outcl, cont_data.disk, 1)
            if split_data.exists():
                runimagr(split_data, source, niter, cellsize, imsize, -1, imna,
                         antennas, uvwtfn, robust, beam)

    if phase_target_flag != '':
        source = phase_target_flag
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        for entry in phase_loop:
            cal_data = phase_selfcal(indata, source, entry, line_data.disk, niter,
                                     cellsize, imsize, logfile, imna, antennas,
                                     refant, beam)
            indata = cal_data

    if amp_target_flag != '':
        source = phase_target_flag
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        for entry in amp_loop:
            cal_data = amp_selfcal(indata, source, entry, line_data.disk, niter,
                                   cellsize, imsize, logfile, imna, antennas,
                                   beam, refant)
            indata = cal_data

    if apply_selfcal == 1:
        do_apply_selfcal(calsource, calsource, split_outcl, defdisk, refant)
        for entry in target:
            do_apply_selfcal(entry, calsource, split_outcl, defdisk, refant)

    if plot_tables != -1:

        if plot_tables == line:
            if line_data2.exists():
                mprint('Using shifted data (CVEL).', logfile)
                line_used = line_data2
            else:
                mprint('Using unshifted data (CVEL).', logfile)
                line_used = line_data
            plot_data = line_used
        else:
            plot_data = data[plot_tables]

        setup_plotfiles(plot_data)
        run_snplt_2(plot_data, inver=1, inext='sn', optype='AMP', nplot=8, sources='', timer=[])
        # run_snplt_2(plot_data, 1,  'AMP', 'SN1')
        # run_snplt_2(plot_data, 2,  'AMP', 'SN2')
        # run_snplt_2(plot_data, 3, 'DELA', 'SN3')
        # run_snplt_2(plot_data, 4, 'PHAS', 'SN4')
        if (os.path.exists('delay-rate.ps')):
            os.popen(r'convert delay-rate.ps delay-rate.png')
            os.popen(r'mv delay-rate.png plotfiles/')
        if (os.path.exists('delay-rate-ionos.ps')):
            os.popen(r'convert delay-rate-ionos.ps delay-rate-ionos.png')
            os.popen(r'mv delay-rate-ionos.png plotfiles/')
            #    rdbe_plot(data[geo_data_nr],logfile,'GEO')

    if rpossm_flag == 1:
        cvelsource = findcvelsource(line_data, cvelsource)
        for source in cvelsource:
            split_data = AIPSUVData(source, split_outcl, line_data.disk, 1)
            if split_data.exists():
                tv = AIPSTV.AIPSTV()
                if inter_flag == 1:
                    if tv.exists() == False: tv.start()
                runrpossm(split_data, cvelsource, tv, inter_flag, antennas)

    if ma_sad_flag == 1:
        cvelsource = findcvelsource(line_data, cvelsource)
        for source in cvelsource:
            ma_cube = AIPSImage(source, 'ICL001', line_data.disk, 1)
            run_ma_sad(ma_cube, line_data, min_snr, dyna)
            #        orfit_to_plot_sorted(ma_cube, line_data)
            orfit_to_plot_sorted(ma_cube, line_data, bchan, vel)

    if plot_map == 1:
        cvelsource = findcvelsource(line_data, cvelsource)
        for source in cvelsource:
            ma_cube = AIPSImage(source, 'ICL001', line_data.disk, 1)
            plot_spot_map(ma_cube, line_data)

    tv = AIPSTV.AIPSTV()
    if tv.exists():
        raw_input('Press Enter to close window. ')
        tv.kill()


if __name__ == '__main__':
    #current_time()
    logfilename = 'logs/vlbi-pipeline.' + current_time() + '.log'
    if os.path.exists('logs'):
        logfile = open(logfilename, 'a')
        logfile.write("Start VLBI-pipeline >>\n")
        logfile.close()
    else:
        os.mkdir('logs')
        logfile = open(logfilename, 'a')
        logfile.write("Start VLBI-pipeline >>\n")
        logfile.close()
    run_main(logfilename)