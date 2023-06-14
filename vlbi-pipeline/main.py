#!/usr/bin/env ParselTongue

import time
import sys
#import pathlib
# import logging
from AIPS import AIPS
import os
from config import *
import argparse
from utils import *
from make_utils import *
from run_tasks import *
from get_utils import *
from check_utils import *
from plot_utils import *
from logging_config import logger

# Init setting
aipsver = AIPS_VERSION
AIPS.userno =  AIPS_NUMBER
inter_flag = INTER_FLAG
antname = antname

# Setting the parameters
parser = argparse.ArgumentParser(description="VLBI pipeline")
#parser.add_argument('aips-number', metavar='aips number', type=int, nargs='+', help='the AIPS number <keep only>')
#parser.add_argument('fits_file', metavar='fits file', type=str, nargs='+', help='files file name')
#parser.add_argument('-p', '--file-path', type=pathlib.Path, default='/data/VLBI/VLBA/', help='the data path of fits file')
#parser.add_argument('-i', '--image-path', type=pathlib.Path, default='/data/VLBI/VLBA/images/', help='the data path of image file')
#parser.add_argument('-o', '--output-filename', default='demo', help='the output file name')



# Optional parameters for each file
# outdisk[0]   = 3				  # AIPS disk for this file (if != defdisk)
# usually for EVN stations
# flagfile[0]  = 'es094.uvflg'   # flag file for UVFLG
# antabfile[0] = 'es094.antab'  # antab file for ANTAB

#antname = 'VLBA'  # Antenna order for FITLD
#refant = 4  # refant=0 to select refant automatically
#AIPS.log = open(logfile, 'a')

finder_man_flag = auto_fringe  #activate automatice selecting fringe scan and refant

#################
# Control Flags #
#################
step1 = step1  # auto control of the flags in this block
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step2 = step2  # Auto control of the seond block
step3 = step3

##################################
# Data preparation and first prep#
##################################
RFI_clip_flag = 0		  # Automatic flagging of RFI by cliping auto-correlation with 2.5
		# Download key-file from archive
# RDBE_check	  = 0		# Check Geoblock data for RDBE errors?
quack_flag = 0  # Run quack if special considerations (e.g. EVN p-ref)
get_key_flag	= 0
load_flag = 0  # Load data from disk?
listr_flag = 0  # Print out LISTR?
dtsum_flag = 0  # Run dtsum to check antena participation?
tasav_flag = 0  # Run tasav on original tables?
geo_prep_flag = 0  # Run TECOR and EOP corrections? and uvflg for evn data
inspect_flag = 0

if step1 == 1:
    load_flag = 1
    listr_flag = 1
    dtsum_flag = 1
    if antname=='VLBA':
        get_key_flag	= 1
    geo_prep_flag = 1
    RFI_clip_flag = 1 # Automatic flagging of RFI by cliping auto-correlation with 2.5
    quack_flag = do_quack  # Run quack if special considerations (e.g. EVN p-ref)	
    tasav_flag = 1	
    inspect_flag = 1
#########################################################################
# information to fill after first prep #
#########################################################################
## single step before step 2: find the calibrator scan as possm scan   ##
## and run possm, snplt(ty) to find refantenna and fill the rest info  ##
#########################################################################
if os.path.exists(outname[0]+'/'):
    pass
else:
    os.system('mkdir '+ outname[0])
calsource = calsource  # calibrator		'' => automatically
mp_source = calsource  # fringe finder	 '' => automatically
  # constrain time range for fringe finder?
bandcal = calsource  # Bandpass calibrator
targets= target + p_ref_cal
flagver = 2  # Flag table version to be used
tyver = 1  # Tsys table version to be used
chk_trange = [0]  # set the whole time range
dofit = 1
outfg=2
dpfour = 1
split_seq = 1
# dofit=  [-1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,-1]  #usually for EVN with tsys antenas

apcal_flag	  = 0		# Do amplitude calibration?
pang_flag	   = 0		# Run PANG?
pr_fringe_flag  = 0		# Do manual phase cal?
do_fringe_flag  = 0		# Do first run of fringe cal on all sources?
plot_first_run  = 0		# DO possm and snplt to check first run result?
do_band_flag	= 0
split_1_flag	= 0		# Split calibrated data in first run?

if step2 == 1:
    apcal_flag	  = 1		# Do amplitude calibration?
    pang_flag	   = 1		# Run PANG?
    pr_fringe_flag  = 1		# Do manual phase cal?
    do_fringe_flag  = 1		# Do first run of fringe cal on all sources?
    plot_first_run  = 1		# DO possm and snplt to check first run result?
    do_band_flag	= 1
    split_1_flag	= 1   

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
'''
fr_files = ['J1453-v1-mod2.fits', 'J1609-v1-mod2.fits']
fr_nms = ['J1453-fr', 'J1609-fr']
solint = 2  # SOLINT in FRING
nmaps = 1  # NMAPS  in FRING
# doband  = -1
'''
[fr_nm, fr_cls, fr_dsk, fr_sq] = [p_ref_cal[0][:5], 'CLN', 1, 1]
[dwin,rwin]=[100,100]
no_rate = 0 #if =1,supress rate solutions in fringe, if =0 not do this.
smodel = [0, 0]  # SMODEL in FRING step3
#----------------------------------------------------------------
ld_fr_fringe_flag = 0
do_fr_fringe_flag = 0
do_calib_1_flag = 0
check_delay_rate = 0
split_2_flag = 0
if step3 == 1:
        ld_fr_fringe_flag = 1
        do_fr_fringe_flag = 1
        do_calib_1_flag = 1
        check_delay_rate = 1
        split_2_flag = 1

'''
    for i in range(len(fr_files)):
        target = [tar_names[i]]  # target sourcer
        p_ref_cal = [pref_names[i]]  # phase ref calbrator sources '' => automatically
        targets = [target[0], p_ref_cal[0]]
        fr_file = fr_files[i]
        [fr_nm, fr_cls, fr_dsk, fr_sq] = [fr_nms[i], 'CLN', 1, 1]
        # Input image to use in FRINGE:
        # ['NAME','CLASS',DISK,SEQUENCE]

        #execfile(r'' + def_file)
# step3
'''


def run_main():
    logger.info('#############################################')
    logger.info('### Using definition file from ' + version_date + ' ###')
    logger.info('### Using AIPS Version ' + aipsver + (19 - len(aipsver)) * ' ' + '###')
    logger.info('#############################################')
    #n = DEF_DISKS
    debug = 1
    global n
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
                logger.info('################################################')
                logger.info('split_outcl longer than 6 characters. Truncating')
                logger.info('it to: ' + split_outcl)
                logger.info('################################################')
    except:
        split_outcl = 'SPLIT'

    ##############################################################################
    #####				 Set default parameters, if not set				 #####
    ##############################################################################
    ##############################################################################
    # Start main script
    if load_flag == 1:
        for i in range(n):
            loadindx(file_path, filename[i], outname[i], outclass[i], outdisk[i],
                     nfiles[i], ncount[i], doconcat[i], antname)

    data = range(n)

    logger.info('##################################')
    for i in range(n):
        data[i] = AIPSUVData(outname[i], outclass[i], int(outdisk[i]), int(1))
        if data[i].exists():
            data[i].clrstat()
        if dtsum_flag == 1:
            rundtsum(data[i])
        if listr_flag == 1:
            runlistr(data[i])
        if get_key_flag == 1:#for vlba only
            if antname=='VLBA':
                get_key_file(data[i], code)
            else:
                pass
    logger.info('##################################')

    ###########################

    ###########################b########################################
    # Geodetic block analysis
    # Data Preparation
    # Download TEC maps and EOPs

    if geo_prep_flag > 0:
        geo_data = data[0]
        #download TEC and eop files
        (year, month, day) = get_observation_year_month_day(geo_data)
        num_days = get_num_days(geo_data)
        doy = get_day_of_year(year, month, day)
        get_TEC(year, doy, TECU_model, geo_path)
        get_eop(geo_path)
        if num_days == 2: 
            get_TEC(year, doy + 1, TECU_model, geo_path)
            logger.info('######################')
            logger.info(get_time())
            logger.info('######################')
        # runuvflg(geo_data,flagfile[geo_data_nr])
        check_sncl(geo_data, 0, 1)
        if geo_data.header['telescop'] == 'EVN':#no eops for EVN
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

        geo_data = data[0]
        sx_geo = False
###################################################################
#save tables, do flaggings
    pr_data = data[0]
    if tasav_flag == 1:
        logger.info('Begin tasave')
        if flagfile[i] != '':
            runuvflg(pr_data, flagfile[i])
        if antabfile[i] != '':
            if pr_data.table_highver('AIPS TY') > 0:
                pr_data.zap_table('AIPS TY',1)
                pr_data.zap_table('AIPS GC',1)
                logger.info('Deleting old TY and GC tables')
            logger.info('Creating TY and GC tables from' + antabfile[i])
            runantab(pr_data, antabfile[i])
        runtasav(pr_data, i)
        logger.info('Finish tasave')
    if quack_flag == 1:  # for EVN
        if data[0].table_highver('AIPS FG')>=2:
            data[0].zap_table('AIPS FG',outfg) 
        else:
            runtacop(data[0],data[0], 'FG', 1, 2, 1)
        if antname == 'EVN' or antname == 'LBA':
            begquack(data[0],[0], 30./60.,2)
            endquack(data[0],[0], 5./60.,2)
        elif antname == 'VLBA':
            begquack(data[0],[0], 4./60.,2)
            endquack(data[0],[0], 2./60.,2)
        run_elvflag(data[0],15,2)
    if RFI_clip_flag >= 1:
        if data[0].table_highver('AIPS FG')>=2:
    #data[0].zap_table('AIPS FG',outfg)
            infg=2
        else:
            infg=1
        run_aclip(data[0],infg,flagver,3,0,0,'',2.5,0)
        
###################################################################
#automatic search refant and fringe scan
    if finder_man_flag == 1:
        print 'Automaticlly search for refant and fringe scan'
        parms_filename = 'parms-'+ outname[0] +'.txt'
        p_path = './'+outname[0]
        if os.path.exists(p_path+'/'+parms_filename):
            pass
        else:
            timerange,N_obs=get_fringe_time_range(data[0],calsource[0])
            N_ant,refants=get_refantList(data[0])
            refant	  = refants[0]
            refant_candi= refants[1:]+[0]
            parms_filename = 'parms-'+ outname[0] +'.txt'
            if os.path.exists(parms_filename):
                os.remove(parms_filename)
            sys.stdout = open(parms_filename,'w')
            print (N_ant,N_obs)
            print (timerange)
            print (refant)
            print (refant_candi)
            sys.stdout = sys.__stdout__
            print 'mv tmp_test*.txt ' + outname[0]
            os.system('mv tmp_test*.txt ' + outname[0])
            os.system('mv ' + parms_filename + ' ' + outname[0])
        lines=open(outname[0] + '/' + parms_filename,'r').read()
        lines=lines.splitlines()
        refant	  = int(lines[2])		  # refant=0 to select refant automatically
        refant_candi=[]
        possm_scan =[]
        b = lines[3]	 # candidate refant for search in fringe
        c = lines[1]
        for i in b.split(','):
            refant_candi.append(int(i.strip().strip('[]')))
        for i in c.split(','):
            possm_scan.append(int(i.strip().strip('[]')))
            mp_timera = possm_scan  # constrain time range for fringe finder?
        print 'end finding scans'
    elif finder_man_flag != 1:
        refant = reference_antenna
        refant_candi = search_antennas
        possm_scan = scan_for_fringe
        mp_timera = possm_scan
    if inspect_flag == 1:
        logger.info('############################')
        logger.info('Data inspection')
        logger.info('############################')
        #possmplot(data[0],sources='',timer=possm_scan,gainuse=3,flagver=0,stokes='HALF',nplot=2,bpv=0,ant_use=[0],cr=0)
        possmplot(data[0],sources='',timer=possm_scan,gainuse=3,flagver=0,stokes='HALF',nplot=9,bpv=0,ant_use=[0],cr=1)
        possmplot(data[0],sources='',timer=possm_scan,gainuse=3,flagver=0,stokes='HALF',nplot=0,bpv=0,ant_use=[0],cr=0) #this will average all antennas
        possmplot(data[0],sources='',timer=possm_scan,gainuse=3,flagver=0,stokes='HALF',nplot=1,bpv=0,ant_use=[0],cr=0)
        runsnplt(data[0],inver=1,inex='TY',sources='',optype='TSYS',nplot=4,timer=[]) 

###################################################################
    # Phase referencing analysis
    n = 1
    for i in range(n):
        #n = n + 1
        pr_data = data[i]
        logger.info('#######################################')
        logger.info('Processing phase-ref file: ' + outname[i])
        logger.info('#######################################')
        
        if apcal_flag == 1:
            print pr_data.header['telescop']
            check_sncl(data[i],0,3)
            if antname == 'EVN':
                runapcal(pr_data, tyver, 1, 1, dofit, 'GRID')
                runclcal(pr_data, 1, 3, 4, '', 1, refant)
                runtacop(pr_data, pr_data, 'SN', 1, 2, 1)
                runtacop(pr_data, pr_data, 'CL', 4, 5, 1)
            elif antname == 'VLBA':
                runaccor(pr_data)
                runclcal(pr_data, 1, 3, 4, 'self', 1, refant)
                runapcal(pr_data, tyver, 1, 2, dofit, 'GRID')
                runclcal(pr_data, 2, 4, 5, '', 1, refant)
            elif antname == 'LBA':  # for LBA
                runaccor(pr_data)
                runclcal(pr_data, 1, 3, 4, 'self', 1, refant)
                runapcal(pr_data, tyver, 1, 2, dofit, 'GRID')
                runclcal(pr_data, 2, 4, 5, '', 1, refant)
            logger.info('######################')
            logger.info(get_time())
            logger.info('######################')
        if pang_flag == 1:
            check_sncl(pr_data, 2, 5)
            runpang2(pr_data)
            logger.info('######################')
            logger.info('finish pang')
            logger.info('######################')
        if pr_fringe_flag == 1:
            logger.info('######################')
            logger.info('Begin mannual phase-cal')
            logger.info('######################')
            check_sncl(data[i],2,6)
        #if refant_flag==1: 
        #	refant=select_refant2(data[i])
            man_pcal(data[i], refant, mp_source, mp_timera,6, dpfour)
            runclcal2(data[i],3,6,7,'2pt',0,refant,[0],mp_source,'')
        if do_fringe_flag == 1:
            logger.info('######################')
            logger.info('Begin first fringe')
            logger.info('######################')
            check_sncl(pr_data, 3, 7)
            run_fringecal_1(pr_data, refant, refant_candi, calsource[0], 7, 1, solint, -1, 0,200,200)
            run_fringecal_1(pr_data, refant, refant_candi, p_ref_cal[0], 7, 1, solint, -1, 0,200,200)
            runclcal2(pr_data, 4, 7, 8, 'ambg', -1, refant, [0], calsource, calsource)
            runclcal2(pr_data, 5, 7, 9, 'ambg', 1, refant, [0], p_ref_cal[0], targets)
        if do_band_flag == 1:
            check_sncl(pr_data, 5, 9)
            if pr_data.table_highver('AIPS BP') >= 1:
                pr_data.zap_table('AIPS BP', -1)
                run_bpass_cal(pr_data, bandcal, 8, 1)
            else:
                run_bpass_cal(pr_data, bandcal, 8, 1)
            possmplot(pr_data, sources=p_ref_cal[0], timer=chk_trange, gainuse=9, flagver=0, stokes='HALF', nplot=9, bpv=1,ant_use=[0])
            possmplot(pr_data, sources=bandcal[0], timer=possm_scan, gainuse=8, flagver=0, stokes='HALF', nplot=9, bpv=1,ant_use=[0])

        if bandcal == ['']:
            doband = -1
            bpver = -1
        else:
            doband = 1
            bpver = 1

        if split_1_flag == 1:
            check_sncl(data[i], 5, 9)
            run_split2(data[i], calsource[0], 8, split_outcl, doband, bpver, flagver,split_seq)
            run_split2(data[i], p_ref_cal[0], 9, split_outcl, doband, bpver, flagver,split_seq)
            run_split2(data[i], target[0], 9, split_outcl, doband, bpver, flagver,split_seq)
            if len(p_ref_cal) >= 2:
                    run_split2(data[i], p_ref_cal[1], 9, split_outcl, doband, bpver, flagver,split_seq)
        # run_fittp_data(source, split_outcl, defdisk)

        if do_gaincor_flag == 1:  # for EVN ususally
            # runtacop(data[i],data[i], 'CL', 9, 10, 1)
            gcal_app(data[i], matxl, matxr, 5)
            # run_split2(data[i], p_ref_cal[0], 9, split_outcl, doband, bpver, flagver)
    ##up: zyk++

###################################################################
    print step3
    ##step3 from here
    if step3==1:
        pr_data = data[0]
        fr_path=outname[0]+'/'
        os.system('python3 run_difmap.py '+fr_path) 
        fr_file=str(p_ref_cal[0])+'_SPLIT_'+str(int(split_seq))+'-cln.fits'
        fr_image = AIPSImage(fr_nm, fr_cls, fr_dsk, fr_sq)
        print fr_image
        if ld_fr_fringe_flag == 1:
            if fr_image.exists():
                    pass
            else:
                    loadfr(fr_path, fr_file, fr_nm, fr_cls, fr_dsk, antname)
        if do_fr_fringe_flag == 1:
            check_sncl(data[i], 3, 7)
            run_fringecal_1(pr_data, refant, refant_candi, p_ref_cal[0], 7, 0, solint, -1, 0,dwin,rwin)
            runclcal2(pr_data,4,7,8,'AMBG',1,refant,[0],p_ref_cal[0],targets)
            run_fringecal_2(pr_data, fr_image, 1, 8, refant, refant_candi, p_ref_cal[0],solint,smodel, -1, 0, no_rate,dwin,rwin)
            runclcal2(pr_data,5,8,9,'2PT',1,refant,[0],p_ref_cal[0],targets)
        if do_calib_1_flag == 1:
            check_sncl(pr_data, 5, 9)
            run_calib_1(pr_data,fr_image,'A&P',9,refant,6,-1,bpver,p_ref_cal[0],0,solint)
            runclcal2(pr_data, 6, 9, 10, '2PT', 1, refant, [0], p_ref_cal[0], targets)
        if check_delay_rate == 1:
            #plt_sn_cl(pr_data,6, 10, p_ref_cal[0], chk_trange, 1)
            runsnplt(pr_data, inver=8, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
            runsnplt(pr_data, inver=9, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
            runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
            runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='DELA', nplot=4, timer=[])
            runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='RATE', nplot=4, timer=[])
            runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
            runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='DELA', nplot=4, timer=[])
            runsnplt(pr_data, inver=6, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='DELA',nplot=4,timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='RATE',nplot=4,timer=[])
        if split_2_flag >= 1:
            check_sncl(pr_data, 5, 10)
            doband =-1
            run_split2(pr_data, target[0], 9, 'SCL9', doband, bpver, flagver,split_seq)
            run_split2(pr_data, target[0], 10, 'SCL10', doband, bpver, flagver,split_seq)
            run_split2(pr_data, p_ref_cal[0], 8, 'SCL8', doband, bpver, flagver,split_seq)
            run_split2(pr_data, p_ref_cal[0], 9, 'SCL9', doband, bpver, flagver,split_seq)
            run_split2(pr_data, p_ref_cal[0], 10, 'SCL10', doband, bpver, flagver,split_seq) 
#Step3
'''
    #TODO add run_difmap.py
    
    # TODO
    fr_path='/data/VLBI/code/vlbi-pipeline/vlbi-pipeline/BB203A/'
    # TODO Phase cal
    #fr_file=p_ref_cal'J1339+6328_SPLIT_1-cln.fits'
    fr_file='J1339+6328_SPLIT_1-cln.fits'
    #TODO fr_nm limit to 6 chars
    if ld_fr_fringe_flag == 1:
        fr_image = AIPSImage(fr_nm, fr_cls, fr_dsk, fr_sq)
        if fr_image.exists():
            pass
        else:
            loadfr(fr_path, fr_file, fr_nm, fr_cls, fr_dsk, antname)

    if do_fr_fringe_flag == 1:
        check_sncl(data[i], 3, 7)
        fringecal(data[i], fr_image, nmaps, 7, refant, refant_candi, p_ref_cal[0], solint, smodel, doband, bpver, dpfour)
        runclcal2(data[i], 4, 7, 8, 'AMBG', -1, refant, [0], p_ref_cal[0], targets)

    if do_calib_1_flag == 1:
        check_sncl(data[i], 4, 8)
        calib_1(data[i], fr_image, 8, refant, 5, doband, bpver, p_ref_cal[0], flagver, solint)
        runclcal2(data[i], 5, 8, 9, '2PT', -1, refant, [0], p_ref_cal[0], targets)

    if check_delay_rate == 1:
        # chk_sn_cl(data[i],6,10,p_ref_cal[0],chk_trange,1)
        plt_sn_cl(indata,,clchk,source_chk,cl_trange,bpv)
        runsnplt(pr_data, inver=8, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=9, inex='CL', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='DELA', nplot=4, timer=[])
        runsnplt(pr_data, inver=4, inex='SN', sources=targets, optype='RATE', nplot=4, timer=[])
        runsnplt(pr_data, inver=5, inex='SN', sources=targets, optype='PHAS', nplot=4, timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='DELA',nplot=4,timer=[])
        # runsnplt(pr_data,inver=7,inex='SN',sources='',optype='RATE',nplot=4,timer=[])

    if split_2_flag >= 1:
        # check_sncl(data[i], 6, 10)
        check_sncl(data[i], 5, 9)
        # run_split2(data[i], p_ref_cal[0], 10, 'SCL10', doband, bpver, flagver)
        run_split2(data[i], target[0], 8, 'SCL10', doband, bpver, flagver,split_seq)
        # run_split2(data[i], p_ref_cal[0], 11, 'SCL11', doband, bpver, flagver)
        run_split2(data[i], target[0], 9, 'SCL11', doband, bpver, flagver,split_seq)
        if split_2_flag >= 2:
            run_split2(data[i], p_ref_cal[0], 8, 'SCL10', doband, bpver, flagver,split_seq)
        run_split2(data[i], p_ref_cal[0], 9, 'SCL11', doband, bpver, flagver,split_seq)
'''
###########################################################################
'''
    if phase_cal_flag == 1:
        source = calsource
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        cal_ants = antennas
        im_ants = []
        for entry in dofit[0]:
            im_ants.append(-entry)

        for i in range(len(phase_loop)):
            cal_data = phase_selfcal(indata, source, phase_loop[i], line_data.disk,
                                     niter, cellsize, imsize, imna,
                                     cal_ants, im_ants, refant, fr_image, beam)
            indata = cal_data
        logger.info('########################################################')

    if amp_cal_flag == 1:
        source = calsource
        if len(dofit) != len(amp_loop):
            dofit = range(amp_loop)
            logger.info('dofit and amp_loop not equal length, solving for all antennas')
            for i in range(len(dofit)):
                dofit[i] = 0

        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        indata = check_cal(indata, source, outdisk, imna)
        for i in range(len(amp_loop)):
            cal_data = amp_selfcal(indata, source, amp_loop[i], line_data.disk,
                                   niter, cellsize, imsize, imna, antennas,
                                   refant, dofit[i], beam)
            indata = cal_data
        logger.info('########################################################')

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

        if data[i].exists():
            logger.info('Using shifted data (CVEL).')
            cont_used = data[i]
        else:
            logger.info('Using unshifted data (CVEL).')
            cont_used = data[i]

        check_sncl(cont_used, 3, 7)
        fringecal(cont_used, model, nmaps, refant, calsource, solint, smodel, doband, bpver, dpfour)
        if snflg_flag == 1:
            runsnflg(cont_used, 4, calsource)
        if min_elv > 0:
            run_elvflag(cont_used, min_elv)
        runclcal(cont_used, 4, 7, 8, '', 1, refant)
        run_snplt(cont_used, inter_flag)

        logger.info('######################')
        logger.info(get_time())
        logger.info('######################')

        split_sources = get_split_sources(data[i], target, cvelsource, calsource)

        if data[i].exists():
            check_sncl(data[i], 4, 8)
            run_split(data[i], split_sources, split_outcl, doband, bpver)
        else:
            check_sncl(data[i], 4, 8)
            run_split(data[i], split_sources, split_outcl, doband, bpver)

        cvelsource = findcvelsource(line_data, cvelsource)

        if line_data2.exists():
            check_sncl(line_data2, 4, 8)
            run_masplit(line_data2, cvelsource, split_outcl, doband, bpver, smooth, channel)
        else:
            check_sncl(line_data, 4, 8)
            run_masplit(line_data, cvelsource, split_outcl, smooth, channel)

        split_sources = get_split_sources(data[i], target, cvelsource, calsource)

        for source in split_sources:
            split_data = AIPSUVData(source, split_outcl, data[i].disk, 1)
            if split_data.exists():
                runimagr(split_data, source, niter, cellsize, imsize, -1, imna,
                         antennas, uvwtfn, robust, beam)

    if phase_target_flag != '':
        source = phase_target_flag
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        for entry in phase_loop:
            cal_data = phase_selfcal(indata, source, entry, line_data.disk, niter,
                                     cellsize, imsize, imna, antennas,
                                     refant, beam)
            indata = cal_data

    if amp_target_flag != '':
        source = phase_target_flag
        indata = AIPSUVData(source, split_outcl, line_data.disk, 1)
        for entry in amp_loop:
            cal_data = amp_selfcal(indata, source, entry, line_data.disk, niter,
                                   cellsize, imsize, imna, antennas,
                                   beam, refant)
            indata = cal_data

    if apply_selfcal == 1:
        do_apply_selfcal(calsource, calsource, split_outcl, defdisk, refant)
        for entry in target:
            do_apply_selfcal(entry, calsource, split_outcl, defdisk, refant)

    if plot_tables != -1:

        if plot_tables == line:
            if line_data2.exists():
                logger.info('Using shifted data (CVEL).')
                line_used = line_data2
            else:
                logger.info('Using unshifted data (CVEL).')
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
            #	rdbe_plot(data[geo_data_nr],'GEO')

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
            #		orfit_to_plot_sorted(ma_cube, line_data)
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
'''

if __name__ == '__main__':
    run_main()
