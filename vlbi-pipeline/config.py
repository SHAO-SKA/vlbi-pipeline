#!/usr/bin/env python
import sys
AIPS_NUMBER = 248
antname = 'VLBA'  # Antenna order for FITLD
geo_path = '../geod/'
# file_path = sys.argv[1]
# data information
#file_path = '../data/'
file_path = '/data/VLBI/VLBA/br240/br240a/'
#file_name = sys.argv[2]
file_name = 'br240a.idifits' #better use obs_code.idifits as name
num_files = 1 #number of files to load
#exp_path = ''
#source information#
do_quack = 1
solint = 4
calsource   = ['J1642+3948']            # calibrator        '' => automatically
target      = ['J1702+1301']         # target sourcer continuum source 
p_ref_cal   = ['J1707+1331']   



#################
# Control Flags #
#################
# set to 1 for automatic procedure, set 0 to enable task by ta sk mannual checking
step1 = 0  # auto control of the flags in this block
step2 = 0  # Auto control of the second block
step3 = 1


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
###                  Do not change or move this part                     ####
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

#note: this version no bandpass used for fringe fitting.
#### for mannual checking###########
'''
split_outcl = 'SPLIT'

max_files = 1024

outname = range(max_files)

outname[0] = filename.split(',')[0]

execfile(r''+main_file)
'''