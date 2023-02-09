#!/usr/bin/env ParselTongue

import sys
from AIPS import AIPS, AIPSDisk
from AIPSTask import AIPSTask, AIPSList
from AIPSData import AIPSUVData, AIPSImage
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData
import AIPSTV
import AIPS
import os
import math
import time
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
        print("File {} exists.".format(filepath+'/'+filename))
    else:
        print("File {} not exists. Check the path first!!".format(
            filepath+'/'+filename))

    fitld = AIPSTask('FITLD', version=AIPS_VERSION)
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

    data = AIPSUVData(fitld.outname, fitld.outclass,
                      int(fitld.outdisk), int(fitld.outseq))

    print(fitld.outname, fitld.outclass, int(fitld.outdisk), int(fitld.outseq))

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
    logging.info('%s loaded!', str(data))
    logging.info('################################################')

    if data.exists():
        data.zap_table('AIPS CL', 1)
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
    tasav = AIPSTask('TASAV')
    tasav.indata = indata
    tasav.outna = indata.name
    tasav.outcla = 'TASAV'+str(i)
    tasav.outdisk = indata.disk
    tasav_data = AIPSUVData(indata.name, 'TASAV'+str(i), int(indata.disk), 1)
    if tasav_data.exists():
        logging.info(
            'TASAV file [%s] exists, do not need save talbes', logfile)
    else:
        tasav()


def runindxr(indata):
    indxr = AIPSTask('indxr')
    indxr.indata = indata
    indxr.cparm[1:] = [0, 0, 1./60.]
    indxr()


def rundtsum(indata):
    dtsum = AIPSTask('DTSUM')
    dtsum.indata = indata
    dtsum.docrt = -1
    if os.path.exists(indata.name+'.DTSM'):
        os.popen('rm '+indata.name+'.DTSM')
    dtsum.outprint = 'PWD:'+indata.name.strip()+'.DTSM'
    dtsum()
    if (os.path.exists(dtsum.outprint) == False):
        os.popen(r'mv '+dtsum.outprint[4:]+' '+outname[0]+'/')


def runlistr(indata):
    listr = AIPSTask('LISTR')
    listr.indata = indata
    listr.optype = 'SCAN'
    listr.docrt = -1
    if os.path.exists(indata.name+'.LST'):
        os.popen('rm '+indata.name+'.LST')
    listr.outprint = 'PWD:'+indata.name.strip()+'.Listr'
    listr()
    if (os.path.exists(listr.outprint) == False):
        os.popen(r'mv '+listr.outprint[4:]+' '+outname[0]+'/')


def runTECOR(indata, year, doy, num_days, gainuse, TECU_model):
    year = str(year)[2:4]
    if doy < 10:
        doy = '00'+str(doy)
    if doy < 100:
        doy = '0'+str(doy)
    else:
        doy = str(doy)
    name = TECU_model+doy+'0.'+year+'i'
    #    name2='codg'+doy+'0.'+year+'i'
    print(geo_path+name)
    tecor = AIPSTask('TECOR')
    if os.path.exists(geo_path+name):
        tecor.infile = geo_path+name
    #    elif os.path.exists(name2):
    #        tecor.infile='PWD:'+name2
    print(tecor.infile)
    tecor.indata = indata
    tecor.nfiles = num_days
    tecor.gainuse = gainuse
    tecor.aparm[1:] = [1, 0]
    tecor()


def runeops(indata, geo_path):
    eops = AIPSTask('CLCOR')
    eops.indata = indata
    eops.gainver = 2
    eops.gainuse = 3
    eops.opcode = 'EOPS'
    eops.infile = geo_path+'usno_finals.erp'
    eops()


def runuvflg(indata, flagfile, logfile):
    if flagfile != '' and os.path.exists(flagfile):
        uvflg = AIPSTask('UVFLG')
        uvflg.indata = indata
        uvflg.intext = flagfile
        uvflg.opcode = 'FLAG'
        uvflg.go()
    else:
        logging.info('[%s] No UVFLG file applied', logfile)

def runsnplt(indata,inver=1,inex='cl',sources='',optype='phas',nplot=4,timer=[]):
    indata.zap_table('PL', -1)
    snplt=AIPSTask('snplt')
    snplt.default()
    snplt.indata=indata
    snplt.dotv=-1
    snplt.nplot=nplot
    snplt.inex=inex
    snplt.inver=inver
    snplt.optype=optype
    snplt.do3col=2
    if(type(sources) == type('string')):
        snplt.sources[1] = sources
    else:
        snplt.sources[1:] = sources
    if(timer != None):
        snplt.timerang[1:] = timer
    snplt.go()
    lwpla = AIPSTask('lwpla')
    lwpla.indata = indata
    if sources == '':
        lwpla.outfile = 'PWD:'+outname[0]+'-'+inex+str(inver)+'-'+optype+'.snplt'
    else:
        lwpla.outfile = 'PWD:'+outname[0]+'-'+inex+str(inver)+'-'+optype+'-'+sources[0]+'.snplt'
    filename=  outname[0]+'-'+inex+str(inver)+'-'+optype+'.snplt'
    lwpla.plver = 1
    lwpla.inver = 200
    if os.path.exists(filename):
        os.popen('rm '+filename)
    lwpla.go()
    if (os.path.exists(filename)==True):
        os.popen(r'mv '+filename+' '+outname[0]+'/')

def runtysmo(indata, tywin, maxdev):
    while indata.table_highver('AIPS TY') > 1:
        indata.zap_table('TY', 0)
    tysmo = AIPSTask('TYSMO')
    tysmo.indata = indata
    tysmo.dobtween = 0
    tysmo.cparm[1:] = [tywin, 0, 0, 0, 0, maxdev, 0]
    tysmo.inext = 'TY'
    tysmo.inver = 1
    tysmo.outver = 2
    tysmo()

def runapcal(indata, tyver, gcver, snver, dofit, opcode):
    indata.zap_table('AIPS PL', -1)
    apcal = AIPSTask('APCAL')
    apcal.indata = indata
    apcal.tyver = tyver
    apcal.gcver = gcver
    apcal.snver = snver
    apcal.opcode = opcode
    ant = get_ant(indata)
    apcal.dotv = -1
    if antname == 'VLBA':
        apcal.inver = 1  # use WX table 1
        for i in ant:
            apcal.dofit[i] = dofit
    elif antname == 'LBA':
        for i in ant:
            apcal.dofit[i] = dofit
    else:
        apcal.inver = 0
        apcal.dofit[1:] = dofit
    apcal.input()
    apcal()
    if dofit > 0:
        lwpla = AIPSTask('lwpla')
        lwpla.indata = indata
        lwpla.outfile = 'PWD:' + outname[0] + '-sn' + str(snver) + '.apcal'
        filename = outname[0] + '-sn' + str(snver) + '.apcal'
        lwpla.plver = 1
        lwpla.inver = 100
        if os.path.exists(filename):
            os.popen('rm ' + filename)
        lwpla.go()
        indata.zap_table('PL', -1)
        if os.path.exists(filename):
            os.popen('mv ' + filename + ' ./' + outname[0] + '/')

##############################################################################
# Run CLCAL
#
def runclcal(indata, snver, gainver, gainuse, interpol, dobtween, refant):
    clcal = AIPSTask('CLCAL')
    clcal.indata = indata
    clcal.refant = refant
    clcal.snver = snver
    clcal.inver = 0
    clcal.gainver = gainver
    clcal.gainuse = gainuse
    clcal.interpol = interpol
    clcal.dobtween = dobtween
    clcal()

def runtacop(indata, outdata, inext, inver, outver, ncount):
    tacop         = AIPSTask('TACOP')
    tacop.indata  = indata
    tacop.outdata = outdata
    tacop.inext   = inext
    tacop.inver   = inver
    tacop.outver  = outver
    tacop.ncount  = ncount
    tacop()

def runaccor(indata):
    accor = AIPSTask('ACCOR')
    accor.indata = indata
    accor.timer[1:] = [0]
    accor.solint = 0
    accor()

def runantab(indata, antabfile):
    antab = AIPSTask('ANTAB')
    antab.indata = indata
    antab.calin = antabfile
    antab.tyver = 1
    antab.gcver = 1
    antab.offset = 3600
    antab.go()

def runclcal2(indata, snver, gainver, gainuse, interpol, dobtween, refant, antenna, cals, sources):
    clcal = AIPSTask('CLCAL')
    clcal.indata = indata
    clcal.refant = refant
    clcal.antennas[1:] = antenna
    clcal.source[1:] = sources
    if (type(cals) == type('string')):
        clcal.calsour[1] = cals
    else:
        clcal.calsour[1:] = cals
    clcal.snver = snver
    clcal.inver = 0
    clcal.gainver = gainver
    clcal.gainuse = gainuse
    clcal.interpol = interpol
    clcal.dobtween = dobtween  # if >= 1, smooth within with one source;if <=0 smooth separately
    clcal.input()
    clcal()

def runtacop(indata, outdata, inext, inver, outver, ncount):
    tacop         = AIPSTask('TACOP')
    tacop.indata  = indata
    tacop.outdata = outdata
    tacop.inext   = inext
    tacop.inver   = inver
    tacop.outver  = outver
    tacop.ncount  = ncount
    tacop()

def runpang2(indata):
    pang = AIPSTask('CLCOR')
    pang.indata = indata
    pang.gainver = 5
    pang.gainuse = 6
    pang.opcode = 'PANG'
    pang.clcorprm[1:] = [1, 0]
    antennas = []
    for row in indata.table('AN', 0):
        if row['mntsta'] == 0:
            antennas.append(row['nosta'])
    pang.antennas[1:] = antennas
    pang()

def runantab(indata, antabfile):
    antab = AIPSTask('ANTAB')
    antab.indata = indata
    antab.calin = antabfile
    antab.tyver = 1
    antab.gcver = 1
    antab.offset = 3600
    antab.go()

def man_pcal(indata, refant, mp_source, mp_timera, debug, logfile, dpfour):

    if mp_source == ['']:
        mp_source = []
        for source in indata.sources:
            if source[0]=='F':
                mp_source.append(source)

    fringe            = AIPSTask('FRING')
    fringe.indata     = indata
    fringe.refant     = refant
    fringe.docal      = 1
    fringe.solint     = 10
    fringe.bchan      = 0
    fringe.echan      = 0
    fringe.aparm[1:]  = [3,0]
    fringe.dparm[8]   = 1
    fringe.dparm[2]   = 0
    fringe.dparm[3]   = 0
    #+++ZB (same as 060907)
    fringe.dparm[2]   = 250
    #fringe.dparm[2]   = 50
    #---ZB
    fringe.dparm[3]   = 100
    fringe.dparm[4]   = dpfour
    fringe.snver      = 0
    fringe.calso[1:]  = mp_source
    fringe.inputs()
    if mp_timera==0:
        fringe.timer[1:]=[0]
        fringe()
    else:
        #TODO manual modify
        fringe.timer[1:] = mp_timera
        fringe()
    
    qualfile = indata.name+'.'+indata.klass+'-qual.dat'
    (source,timerange)=get_best_scan(indata,logfile, qualfile, 1)

    # Delete SN table from test fringe.
    #check_sncl(indata, 2, 6, logfile)
    #fringe.calsour[1]  = source
    #fringe.timerang[1:] = timerange
    #fringe()    

    sn=indata.table('AIPS SN', 0)
    logging.info('###########################################')
    logging.info('Found solutions for ', str(len(sn)), ' of ',  str(len(indata.antennas)), ' antennas.')
    logging.info('###########################################',logfile)  
    return source, timerange

def do_band(indata, bandcal,gainuse,flagver,logfile):
    if bandcal==['']:
        sys.exit()

    if indata.table_highver('AIPS BP')>0:
        while indata.table_highver('AIPS BP')>0:
            indata.zap_table('AIPS BP', 0)
    
    bpass              = AIPSTask('BPASS')
    bpass.indata       = indata
    bpass.calsour[1:]  = bandcal
    bpass.docal        = 1
    bpass.gainuse      = gainuse
    bpass.flagver      = flagver
    bpass.solint       = -1
    bpass.bpassprm[4]  = 1 # only store phase
    bpass.bpassprm[5]  = 0
    bpass.bpassprm[10] = 3
    bpass.outver       = 1
    bpass.go()

def run_split2(indata, source, gainuse, outclass, doband, bpver, flagver,split_seq):

    channels = indata.header['naxis'][2]
    if channels==16:
        bad=1                     # remove 1 channel from each side
    elif channels==32:
        bad=2                     # remove 2 channels from each side
    elif channels==64:
        bad=4                     # remove 2 channels from each side
    elif channels==128:
        bad=6                     # remove 6 channels from each side
    elif channels==256:
        bad=8                     # remove 8 channels from each side
    elif channels==512:
        bad=10                    # remove 10 channels from each side
    elif channels==1024:
        bad=12                    # remove 12 channels from each side
    else:
        bad=0

    [bchan,echan]=[1+bad,channels-bad]   

    print 'Averaging channels '+str(bchan)+' - '+str(echan)+'.'

    split_data=AIPSUVData(source,outclass,indata.disk,split_seq)

    if split_data.exists():
	print 'Clear old split data'
        split_data.clrstat()
        split_data.zap()
    if isinstance(source, str):
        source=[source]
            
    split            = AIPSTask('SPLIT')
    split.indata     = indata
    split.bchan      = bchan
    split.echan      = echan
    #split.freqid     = 1	
    split.docalib    = 1
    #split.qual	     = -1
    split.gainuse    = gainuse
    split.flagver    = flagver
    split.source[1:] = source
    split.outclass   = outclass
    split.outseq     = split_seq
    split.aparm[1:]  = [2,2,0]
    #split.aparm[6]   = 1
    split.outdisk    = indata.disk
    split.doband     = doband
    split.bpver      = bpver
    #split.smooth[1:] = smooth
    #split.input()
    split()
	

    fittp         = AIPSTask('FITTP')
    fittp.indata  = split_data
    fitname=fittp.inname+'_'+fittp.inclass+'_'+str(int(fittp.inseq))+'.splt'
    fittp.dataout = 'PWD:'+fitname

    if split_data.exists():
        fittp.go()
    else:
        print("NOW")

    if os.path.exists(outname[0]+'/'+fitname):
        os.popen(r'rm '+outname[0]+'/'+fitname)
    if os.path.exists(fitname):
        os.popen(r'mv '+fitname+' '+outname[0]+'/')

def run_split(indata, source, outclass, doband, bpver):

    channels = indata.header['naxis'][2]
    if channels==16:
        bad=1                     # remove 1 channel from each side
    elif channels==32:
        bad=2                     # remove 2 channels from each side
    elif channels==64:
        bad=4                     # remove 2 channels from each side
    elif channels==128:
        bad=6                     # remove 6 channels from each side
    elif channels==256:
        bad=8                     # remove 8 channels from each side
    elif channels==512:
        bad=10                    # remove 10 channels from each side
    elif channels==1024:
        bad=12                    # remove 12 channels from each side
    else:
        bad=0

    [bchan,echan]=[1+bad,channels-bad]   

    print 'Averaging channels '+str(bchan)+' - '+str(echan)+'.'

    target           = findtarget(indata, source)
    if isinstance(target, str):
        target=[target]

    if target!=[]:
        for source in target:
            split_data=AIPSUVData(source,outclass,indata.disk,1)
            if split_data.exists():
                split_data.clrstat()
                split_data.zap()

        split            = AIPSTask('SPLIT')
        split.indata     = indata
        split.bchan      = bchan
        split.echan      = echan
        split.docalib    = 1
        split.flagver    = 0
        split.source[1:] = target
        split.outclass   = outclass
        split.aparm[1:]  = [3,0]
        split.aparm[6]   = 1
        split.outdisk    = indata.disk
        split.doband     = doband
        split.bpver      = bpver
        split.smooth[1:] = smooth
	#split.input()
        split()
def run_split3(indata, target, outclass, doband, bpver, gainuse, avg, fittp):
    if fittp >= 0:
        split            = AIPSTask('SPLIT')
        split.indata     = indata
	if gainuse <= 0:
        	split.docalib    = -1
	else:	
		split.docalib    = 1
		split.gainuse    = gainuse
        split.flagver    = 0
    	if isinstance(target, str):
            source=[target]
        split.source[1:] = [target]
        split.outclass   = outclass
	#split.outname	 = parm not there
	if avg == 0:
            split.aparm[1:]  = [0]
	elif avg == 1:
	    split.aparm[1:]  = [2,2,0]
        #split.aparm[6]   = 1
        split.outdisk    = indata.disk
        split.doband     = doband
        split.bpver      = bpver
        split.smooth[1:] = smooth
	split.input()
        split()
    splt_data=AIPSUVData(target,outclass,indata.disk,split_seq)
    #    if uvfix_data.exists():
#	print 'Clear old uvfix data'
#        splt_data.clrstat()
#        splt_data.zap()
    if fittp == 1:
    	fittp         = AIPSTask('FITTP')
    	fittp.indata  = splt_data
    	fitname=fittp.inname+'_'+fittp.inclass+'_'+str(int(fittp.inseq))+'.splt'
    	fittp.dataout = 'PWD:'+fitname
	
    if splt_data.exists():
        logging.info('Writing out calibrated and splitted uv-data for ', source[0])
        fittp.go()
    else:
        logging.info('No calibrated and splitted uv-data for ', source[0])
    
    if os.path.exists(outname[0]+'/'+fitname):
	    os.popen(r'rm '+outname[0]+'/'+fitname)
    if os.path.exists(fitname):
	    os.popen(r'mv '+fitname+' '+outname[0]+'/')

