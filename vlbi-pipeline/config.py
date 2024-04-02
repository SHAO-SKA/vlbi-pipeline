#!/usr/bin/env python
import sys
import numpy as np
import ba158c1_inputs as inputs 
#set input parameters in separate py files which can be one data per input and can also be tracked for history.

AIPS_NUMBER = inputs.AIPS_NUMBER
antname = inputs.antname  # Antenna order for FITLD
geo_path = '../geod/'
#file_path = sys.argv[1]
# data information
#file_path = '../data/'
file_path = inputs.file_path
#file_name = sys.argv[2]
file_name = inputs.file_name #better use obs_code.idifits as name
num_files = 1 #number of files to load
#exp_path = ''
#source information#
do_quack = 1
ap_dofit = 1
#ap_dofit = [-1,1,1,1,1,1,1,1,1,1] #modify this if some antenna is not suitable for opacity in apcal
solint = 4
calsource   = inputs.calsource	# calibrator for fringe fitting and bandpass(if used). '' => automatically
target	    = inputs.target	# target sourcer continuum source 
p_ref_cal   = inputs.p_ref_cal
#please put the corresponding files in the outname[0]/
logfilename = file_name.split('.')[0]

#####################################################
auto_fringe = 0 #for automatic step connecting step1 and step2, if =0, the following parameters must be set, please refer to the results from step1. If =1, the following parameters are ignored. It is high recommanded to set 0, especially for EVN

reference_antenna = inputs.reference_antenna
search_antennas = inputs.search_antennas
scan_for_fringe = inputs.scan_for_fringe

auto_mapping = 0  #automatic step connecting step2 and step3, if =0, the following parameters must be set, just file name end with .fits
man_fr_file = inputs.man_fr_file
#####################mannual flagging################################
do_flag = 0
fgbchan=[0]
fgechan=[0]
fgbif=[0]
fgeif=[0]
fgantennas=[[1]]
#print len(fgbchan),len(fgechan),len(fgbif),len(fgantennas)
#fgbchan,fgechan,fgbif,fgeif=[[0,0],[0,0],[5,7],[5,7]]
#fgantennas=[[0],[7]]

[fgtimer,outfg]=[[0],2]

#############for_EVN_data_only########################################
pipepath='/data/VLBI/EVN/eg119/pipeline-eg119a/'
#format'/data/path/'

if antname != 'VLBA':
	fgfile = pipepath+'eg119a.uvflg'
	antfile = pipepath+'eg119a.antab'
else:
	fgfile = ''
	antfile = ''
###############Mannual calibration of antenna gain##############################################################
matxi=[[1.0,1.0,1.0,0.9,1.0,1.0,1.0,1.0,1.0],
       [1.1,1.0,0.8,0.8,1.0,1.0,0.8,0.8,1.2],
       [1.0,1.0,1.0,0.9,1.0,1.0,1.0,1.0,1.0],       
       [1.1,1.0,2.0,0.8,1.0,1.0,1.2,1.0,1.0]]
#[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

#matxl=[[1.3,1.0,1.1,0.9,1.1,1.0,1.0,1.0,0.9,1.1],
#[1.0,0.9,1.1,1.0,1.0,1.0,1.0,1.0,1.0,0.9],
#[1.0,0.9,0.9,0.9,1.0,1.0,0.9,1.0,1.0,1.1],
#[0.9,0.9,1.0,1.0,1.2,1.0,1.2,1.1,1.0,1.2]]

#matxr=[[1.0,1.0,1.0,0.9,0.8,1.0,1.1,1.0,1.0,1.0],
#[1.1,1.0,1.2,1.0,0.9,1.1,1.0,1.1,0.9,1.0],
#[1.0,0.9,0.9,0.9,1.0,1.0,1.0,1.0,1.0,1.1],
#[1.0,1.0,1.0,0.9,0.8,1.0,1.2,0.8,0.9,1.2]]

pol='I'  #if use I correction, set POL='I' and ues matxi; if use both x and l, set pol='LR' and used maxtl and matxr.
# snchk=3
# cluse=7
ant_gan_cal = inputs.ant_gan_cal   #set this and go back to step2s
#############################################################################
#################
# Control Flags #
#################
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step1 = inputs.step1  # auto control of the flags in this block
step2 = inputs.step2  # Auto control of the second block
step3 = inputs.step3
stepn = inputs.stepn
#############################################################################
#if you need further functions after step3, please check these
#uv-shift before spliting, belong to stepn
rash=inputs.rash   #in arcsec, no need to times cos(dec)
decsh=inputs.decsh  #in arcsec
do_uvshift_flag = inputs.do_uvshift_flag ###note!! this is out of any steps

########DO NOT EDIT UNLESS YOU KNOW THE MEANING #######################################################################################

AIPS_VERSION = '31DEC19'
version_date = '2016/04/06'
INTER_FLAG = 0 # interactive (1) or non-interactive (0)
main_file = 'main.py'
DEF_DISKS = 1			
# FITLD parameters, for multiple input files change ncount
# file_path = sys.argv[1]
#fr_path = exp_path

TECU_model = 'jplg'
#############################################################################
###				  Do not change or move this part					 ####
defdisk=1
n = 1
[filename, outname, outclass] = [range(n), range(n), range(n)]
[nfiles, ncount, doconcat] = [range(n), range(n), range(n)]
[outdisk, flagfile, antabfile] = [range(n), range(n), range(n)]
for i in range(n):
	[flagfile[i], antabfile[i], outdisk[i]] = ['', '', defdisk]
	[nfiles[i], ncount[i], doconcat[i]] = [0, 1, 1]
#############################################################################
###############
# Input Files #
###############
# This only for single file
# print("FILE PATH =========",file_path)
filename[0] = file_name
outname[0] = file_name.split('.')[0]
outclass[0] = 'UVDATA'
nfiles[0] = 1  # FITLD parameter NFILES
ncount[0] = num_files  # FITLD parameter NCOUNT
doconcat[0] = 1  # FITLD parameter DOCONCAT
flagfile[0] = fgfile
antabfile[0] = antfile
code = ''

#note: this version no bandpass used for fringe fitting.
#### for mannual checking###########
'''
split_outcl = 'SPLIT'

max_files = 1024

outname = range(max_files)

outname[0] = filename.split(',')[0]

execfile(r''+main_file)
'''
