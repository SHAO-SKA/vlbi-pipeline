#!/usr/bin/env ParselTongue

import sys
from AIPS import AIPS, AIPSDisk
from AIPSTask import AIPSTask, AIPSList
from AIPSData import AIPSUVData, AIPSImage
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData
import AIPSTV
import AIPS, os, math, time
from pylab import *
from utils import *
from config import *
from check_utils import *
from get_utils import *
import logging

def loadindx(filepath, filename, outname, outclass, outdisk, nfiles, ncount, doconcat, antname, logfile):

    '''
    load_data

    Load the data into AIPS and index it

    Parameter
    ---------


    Returns
    -------
    bool

    if uvdata.exists():
        warnings.warn('zapping old uvdata data')
        uvdata.zap()
    '''

    if os.path.exists(filepath + '/' + filename):
        print ("File {} exists.".format(filepath+'/'+filename))
    else:
        print("File {} not exists. Check the path first!!".format(filepath+'/'+filename))

    fitld = AIPSTask('FITLD', version = AIPS_VERSION)
    #fitld.infile = filepath + '/' + filename
    fitld.datain = filepath + '/' + filename
    #fitld.outdata = uvdata
    fitld.outname = outname
    fitld.outclass = outclass
    fitld.outdisk = int(outdisk)
    fitld.outseq = 1
    fitld.ncount = ncount
    fitld.nfiles = nfiles
    fitld.doconcat = doconcat
    fitld.clint = 1./60
    if antname == 'VLBA':
        fitld.wtthresh = 0.7
        fitld.digicor = 1
    elif antname == 'EVN':
        fitld.digicor = -1

    data = AIPSUVData(fitld.outname, fitld.outclass,int(fitld.outdisk), int(fitld.outseq))

    print (fitld.outname, fitld.outclass,int(fitld.outdisk), int(fitld.outseq))

    if data.exists():
        print('Data already there')
        pass
    else:
        print('Data not there')
        fitld.input()
        fitld.go()


#print("LOADED DATA:====================")
#AIPSTask('pca', version='31DEC20')
#print("LOADED DATA:====================")
#loadindx(sys.argv[1], sys.argv[2],'test','tstc',1,1,1,1,'VLBA','loggg.txt')

    logging.info('#############################')
    logging.info('#############################')
    logging.info('################################################')
    logging.info('%s loaded!',str(data))
    logging.info('################################################')

    if data.exists():
        data.zap_table('AIPS CL',1)
        runindxr(data)
        logging.info('##########################################')
        logging.info('#################')
        logging.info('Data new indexed!')
        logging.info('#################')
    else:
        logging.info('No!')

##############################################################################
#
def runtasav(indata, i, logfile):
    tasav         = AIPSTask('TASAV')
    tasav.indata  = indata
    tasav.outna   = indata.name
    tasav.outcla  = 'TASAV'+str(i)
    tasav.outdisk = indata.disk
    tasav_data=AIPSUVData(indata.name,'TASAV'+str(i),int(indata.disk),1)
    if tasav_data.exists():
        logging.info('TASAV file [%s] exists, do not need save talbes', logfile)
    else:
        tasav()

def runindxr(indata):
    indxr = AIPSTask('indxr')
    indxr.indata = indata
    indxr.cparm[1:] = [0, 0, 1./60.]
    indxr()

def rundtsum(indata):
    dtsum=AIPSTask('DTSUM')
    dtsum.indata   = indata
    dtsum.docrt    = -1
    if os.path.exists(indata.name+'.DTSM'):
        os.popen('rm '+indata.name+'.DTSM')
    dtsum.outprint = 'PWD:'+indata.name.strip()+'.DTSM'
    dtsum()
    if (os.path.exists(dtsum.outprint)==False):
        os.popen(r'mv '+dtsum.outprint[4:]+' '+outname[0]+'/')

def runlistr(indata):
    listr=AIPSTask('LISTR')
    listr.indata   = indata
    listr.optype   = 'SCAN'
    listr.docrt    = -1
    if os.path.exists(indata.name+'.LST'):
        os.popen('rm '+indata.name+'.LST')
    listr.outprint = 'PWD:'+indata.name.strip()+'.Listr'
    listr()
    if (os.path.exists(listr.outprint)==False):
        os.popen(r'mv '+listr.outprint[4:]+' '+outname[0]+'/')

def runTECOR(indata,year,doy,num_days,gainuse,TECU_model):
    year=str(year)[2:4]
    if doy<10:
        doy='00'+str(doy)
    if doy<100:
        doy='0'+str(doy)
    else:
        doy=str(doy)
    name=TECU_model+doy+'0.'+year+'i'
    #    name2='codg'+doy+'0.'+year+'i'
    print(geo_path+name)
    tecor = AIPSTask('TECOR')
    if os.path.exists(geo_path+name):
        tecor.infile=geo_path+name
    #    elif os.path.exists(name2):
    #        tecor.infile='PWD:'+name2
    print(tecor.infile)
    tecor.indata=indata
    tecor.nfiles=num_days
    tecor.gainuse = gainuse
    tecor.aparm[1:] = [1,0]
    tecor()

def runeops(indata, geo_path):
    eops        = AIPSTask('CLCOR')
    eops.indata = indata
    eops.gainver = 2
    eops.gainuse = 3
    eops.opcode  = 'EOPS'
    eops.infile  = geo_path+'usno_finals.erp'
    eops()


def runuvflg(indata,flagfile,logfile):
    if flagfile!='' and os.path.exists(flagfile):
        uvflg        = AIPSTask('UVFLG')
        uvflg.indata = indata
        uvflg.intext = flagfile
        uvflg.opcode = 'FLAG'
        uvflg.go()
    else:
        logging.info('[%s] No UVFLG file applied', logfile)













