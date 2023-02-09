#!/usr/bin/env python
#from get_utils import get_ant
from select_utils import *
import os
from AIPS import AIPS
import logging
import argparse
# , split_outcl, antname
from config import AIPS_VERSION, AIPS_NUMBER, INTER_FLAG, DEF_DISKS
from utils import *
from make_utils import *
from run_tasks import *
from get_utils import *
from check_utils import *


def possmplot(uvdata, sources='', timer=[0, 0, 0, 0, 0, 0, 0, 0], gainuse=0, flagver=0, stokes='HALF', nplot=1, bpv=0, ant_use=[0], cr=1):
    uvdata.zap_table('AIPS PL', -1)
    possm = AIPSTask('possm')
    possm.default()
    possm.indata = uvdata
    if(type(sources) == type('string')):
        possm.sources[1] = sources
    else:
        possm.sources[1:] = sources

    if(timer != None):
        if(timer[0] == None): 
            possm.timerange = timer
        else: 
            possm.timerang[1:] = timer

    possm.stokes=stokes
    possm.nplot=nplot
    if(gainuse >= 0):
        possm.docalib = 1
        possm.gainuse = gainuse
    possm.flagv=flagver
    if cr == 1:#cross-correlation
        possm.aparm[1:] = [0,1,0,0,-180,180,0,0,1,0] 
    elif cr == 0:#total power
        possm.aparm[1:] = [0,0,0,0,0,0,0,1,0]
    possm.bchan = 0
    possm.echan = 0
    possm.dotv=-1
    if(bpv > 0):
        possm.doband = 1
        possm.bpver = bpv
    if(ant_use!=0):
        possm.antennas[1:]=ant_use
    possm.baseline=[None,0]
    # possm.input()
    possm.go()
	
    lwpla = AIPSTask('lwpla')
    lwpla.indata = uvdata
    # lwpla.outfile = 'PWD:'+outname[0]+'-'+sources[0]+'-cl'+str(gainuse)+'-bp'+str(bpv)+'.possm'
    if sources == '':
        sources=['']
    filename=outname[0]+'-'+possm.sources[1]+'-cl'+str(gainuse)+'-bp'+str(bpv)+'-'+str(cr)+'.possm'
    lwpla.outfile='PWD:'+filename    	
    lwpla.plver = 1
    lwpla.inver = 100
    if os.path.exists(filename):
        os.popen('rm '+filename)
    lwpla.go()
    if (os.path.exists(filename)==True):
        os.popen(r'mv '+filename+' '+outname[0]+'/')

