#!/usr/bin/env ParselTongue

import time
import sys
#import pathlib

import os
from AIPS import AIPS
import logging
import argparse
from config import AIPS_VERSION, AIPS_NUMBER, INTER_FLAG, DEF_DISKS #, split_outcl, antname
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


def run_main(logfile):


    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logfile+'-test',
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    if os.path.exists('logs'):
        logging.info("<< Start VLBI-pipeline >>")
        logging.info("Commanding : %s ", sys.argv)
    else:
        os.mkdir('logs')
        logging.info("<< Start VLBI-pipeline >>")

    #AIPS.log = logfile+'-test'

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

    logging.info('#############################################')
    logging.info('### Using definition file from %s ###', version_date)
    logging.info('### Using AIPS Version %s ###',  aipsver)
    logging.info('#############################################')

    debug = 1
    #n = DEF_DISKS

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
                logging.info('################################################' )
                logging.warning('split_outcl longer than 6 characters. Truncating ')
                logging.warning('it to:  %s ' ,split_outcl )
                logging.info('################################################' )
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
    if 'TECU_model' in locals() and globals():
        pass
    else:
        TECU_model = 'jplg'

    ##############################################################################
    # Start main script

    logging.info('######################' )
    logging.info('%s',get_time())
    logging.info('###################### ' )

    calsource = ''  # calibrator        '' => automatically
    target = ['']  # continuum sources '' => automatically
    mp_source = ['']  # fringe finder     '' => automatically
    mp_timera = [0, 0, 0, 0, 0, 0, 0, 0]  # constrain time range for fringe finder?
    bandcal = ['']  # Bandpass calibrator

    #################
    # Split Options #
    #################

    smooth = [0, 0, 0]  # Smooth during split for line data
    split_outcl = 'SPLIT'  # outclass in SPLIT '' => 'SPLIT'

    ##################################
    # Optional inputs for fringe fit #
    ##################################

    [fr_n, fr_c, fr_d, fr_s] = ['', '', 1, 1]
    # Input image to use in FRINGE:
    # ['NAME','CLASS',DISK,SEQUENCE]
    smodel = [1, 0]  # SMODEL in FRING
    solint = 0  # SOLINT in FRING
    nmaps = 1  # NMAPS in FRING

    
    logging.info("FILE NAME %s", filename[0])
    logging.info("OUT  NAME %s ", outname[0])
    #print("FILE NAME =========", filename[0])  # ,filename[1],filename[2])
    #print("OUT  NAME =========", outname[0])  # ,outname[1],outname[2])
    if not os.path.exists(outname[0]):
        os.mkdir(outname[0])
    #################
    # Control Flags #
    #################
    step1 = 1  # auto control of the flags in this block
    # set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
    step2 = 0  # Auto control of the second block
    step3 = 0
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

    if load_flag == 1:
        loadindx(file_path, filename[0], outname[0], outclass[0], outdisk[0], nfiles[0], ncount[0], doconcat[0], antname, logfile+'-test')
        #for i in range(n):
        #    loadindx(file_path, filename[i], outname[i], outclass[i], outdisk[i], nfiles[i], ncount[i], doconcat[i], antname, logfile)

    data = range(n)

    logging.info('################################## ')
    for i in range(n):
        data[i] = AIPSUVData(outname[i], outclass[i], int(outdisk[i]), int(1))
        if data[i].exists():
            data[i].clrstat()
        if dtsum_flag == 1:
            rundtsum(data[i])
        if listr_flag == 1:
            runlistr(data[i])
    logging.info('################################## ' )

    # Download TEC maps and EOPs

    if pr_prep_flag == 1 or geo_prep_flag == 1:
        (year, month, day) = get_observation_year_month_day(data[0])
        num_days = get_num_days(data[0])

        doy = get_day_of_year(year, month, day)

        get_TEC(year, doy, TECU_model, geo_path)
        get_eop(geo_path)

        if num_days == 2: get_TEC(year, doy + 1, TECU_model, geo_path)

    logging.info('################################## ')
    logging.info(get_time())
    logging.info('################################## ')


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


    pr_data = data[0]

    if tasav_flag == 1:
        if flagfile[0] != '':
            runuvflg(pr_data, flagfile[0], logfile)
        if antabfile[0] != '':
            runantab(pr_data, antabfile[0])
        runtasav(pr_data, 0, logfile)


        #todo : possom choose time range
        pass


if __name__ == '__main__':
    #current_time()
    logfilename = 'logs/vlbi-pipeline.' + current_time() + '.log'
    run_main(logfilename)
