#!/usr/bin/env python

AIPS_NUMBER = 160
antname = 'VLBA'  # Antenna order for FITLD
geo_path = '../geod/'
#file_path = sys.argv[1]
# data information
#file_path = '../data/'
file_path = '/data/VLBI/VLBA/ba158/'
#file_name = sys.argv[2]
file_name = 'ba158l2.idifits' #better use obs_code.idifits as name
num_files = 1 #number of files to load
#exp_path = ''
#source information#
do_quack = 1
ap_dofit = 1
#ap_dofit = [-1,1,1,1,1,1,1,1,1,1] #modify this if some antenna is not suitable for opacity in apcal
solint = 4
calsource   = ['4C39.25','test']	# calibrator for fringe fitting and bandpass(if used). '' => automatically
target	    = ['J1133+47','J1204+55','J1256+27','J1318+32']	# target sourcer continuum source 
p_ref_cal   = ['P1138+4745','P1208+5441','P1300+2830','P1317+3425']
#please put the corresponding files in the outname[0]/
logfilename = file_name.split('.')[0]

#####################################################
auto_fringe = 0 #for automatic step connecting step1 and step2, if =0, the following parameters must be set, please refer to the results from step1. If =1, the following parameters are ignored. It is high recommanded to set 0, especially for EVN

reference_antenna = 4
search_antennas = [8,2,0]
scan_for_fringe = [0,8,15,0,0,8,17,0]

auto_mapping = 0  #automatic step connecting step2 and step3, if =0, the following parameters must be set, just file name end with .fits
man_fr_file = ['P1138-v1-mod1.fits','P1208-v1-mod1.fits','P1300-v1-mod1.fits','P1317-v1-mod1.fits']
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
ant_gan_cal = 1   #set this and go back to step2s
#############################################################################
step1 = 1  # auto control of the flags in this block
step2 = 0  # Auto control of the second block
step3 = 0
stepn = 0
#############################################################################
#in stepn
rash=-0.1095   #in arcsec, no need to times cos(dec)
decsh=-0.1075  #in arcsec
do_uvshift_flag = 1 ###note!! this is out of any steps
