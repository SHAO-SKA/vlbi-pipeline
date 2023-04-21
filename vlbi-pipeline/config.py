#!/usr/bin/env python
import sys

AIPS_NUMBER = 606
antname = 'EVN'  # Antenna order for FITLD
geo_path = '../geod/'
#file_path = sys.argv[1]
# data information
#file_path = '../data/'
file_path = '/data/VLBI/EVN/RA006/'
#file_name = sys.argv[2]
file_name = 'ra006_1_1.IDI1' #better use obs_code.idifits as name
num_files = 9 #number of files to load
#exp_path = ''
#source information#
do_quack = 1
solint = 4
calsource   = ['J1504+1029']			# calibrator		'' => automatically
target	    = ['J1430+2303']	# target sourcer continuum source 
p_ref_cal   = ['P1427+2348']
#please put the corresponding files in the outname[0]/
logfilename = 'logs/vlbi-pipe'
#####################################################
auto_fringe = 0 #for automatic step connecting step1 and step2, if =0, the following parameters must be set, please refer to the results from step1. If =1, the following parameters are ignored. It is high recommanded to set 0, especially for EVN

reference_antenna = 2
search_antennas = [5,7,0]
scan_for_fringe = [0,0,6,0,0,0,8,0]
#####################################################
pipepath='/home/ykzhang/EVN/RA006/'

if antname != 'VLBA':
	fgfile = pipepath+'ra006.uvflg'
	antfile = pipepath+'ra006.antab'
else:
	fgfile = ''
	antfile = ''

#################
# Control Flags #
#################
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step1 = 1  # auto control of the flags in this block
step2 = 0  # Auto control of the second block
step3 = 0


########DO NOT EDIT UNLESS YOU KNOW THE MEANING ##########
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


#note: this version no bandpass used for fringe fitting.
#### for mannual checking###########
'''
split_outcl = 'SPLIT'

max_files = 1024

outname = range(max_files)

outname[0] = filename.split(',')[0]

execfile(r''+main_file)
'''
