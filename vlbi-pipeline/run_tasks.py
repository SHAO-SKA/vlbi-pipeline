#!/usr/bin/env ParselTongue
#####!/usr/bin/python3

# sys.path.append('/usr/share/parseltongue/python/')
# sys.path.append('/usr/lib/obit/python3')
# export PYTHONPATH=$PYTHONPATH:/usr/share/parseltongue/python:/usr/lib/obit/python3

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
from logging_config import logger

# def load_index_data(filepath, filename, outname, outclass, outdisk, nfiles, ncount, doconcat, antname):


def loadindx(filepath, filename, outname, outclass, outdisk, nfiles, ncount, doconcat, antname):
    '''load_data

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

    if os.path.exists(filepath + filename):
        logger.info("File {} exists.".format(filepath+filename))
    else:
        logger.info("File {} not exists. Check the path first!!".format(filepath+filename))

    fitld = AIPSTask('FITLD', version=AIPS_VERSION)
    # fitld.infile = filepath + '/' + filename
    fitld.datain = filepath + filename
    # fitld.outdata = uvdata
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
    logger.info('Processing following data file in AIPS')
    logger.info(data)

    if data.exists():
        logger.info('Data already there, re-index')
        data.zap_table('AIPS CL', 1)
        data.zap_table('AIPS NX', 1)
        runindxr(data)
        logger.info('#################')
        logger.info('Data new indexed!')
        logger.info('#################')
    else:
        logger.info('Data not in AIPS, read in')
        fitld.input()
        fitld.go()
        data.zap_table('AIPS CL', 1)
        data.zap_table('AIPS NX', 1)
        runindxr(data)
        logger.info('#################')
        logger.info('Data new indexed!')
        logger.info('#################')

    logger.info('#############################')
    logger.info('#############################')
    logger.info('################################################')
    logger.info('%s loaded!', str(data))
    logger.info('################################################')

# print("LOADED DATA:====================")
# AIPSTask('pca', version='31DEC20')
# print("LOADED DATA:====================")
# loadindx(sys.argv[1], sys.argv[2],'test','tstc',1,1,1,1,'VLBA','loggg.txt')

# _____________________________________________________________


def loadfr(filepath, filename, outname, outclass, outdisk, antname):
    if os.path.exists(filepath+filename):
        logger.info('File exists!')
    else:
        logger.info('File '+filepath+filename+' dose not exists')
        raise RuntimeError('File does not exists!')

    fitld = AIPSTask('FITLD')
    fitld.datain = filepath+filename
    fitld.outname = outname
    fitld.outclass = outclass
    fitld.outseq = 1
    fitld.outdisk = int(outdisk)
    # if aipsver!='31DEC09':
    #   fitld.antname[1:] = [antname]

    data = AIPSUVData(fitld.outname, fitld.outclass,
                      int(fitld.outdisk), int(fitld.outseq))
    if data.exists():
        logger.info('##############################')
        logger.info('Data already there => passed!')
        logger.info('##############################')
        pass
        # data.clrstat()
        # data.zap()
        # logger.info('##############################')
        # logger.info('Data already there => deleted!')
        # logger.info('##############################')
    else:
        logger.info('#########################')
        logger.info('Data not there => read in')
        logger.info('#########################')
    fitld.go()

    # fitld.go()

    logger.info('################################################')
    logger.info(str(data)+' loaded!')
    logger.info('################################################')


##############################################################################
#
def runTECOR(indata, year, doy, num_days, gainuse, TECU_model):
    logger.info('Doing TECOR to generate CL table'+str(gainuse))
    year = str(year)[2:4]
    if doy < 10:
        doy = '00'+str(doy)
    if doy < 100:
        doy = '0'+str(doy)
    else:
        doy = str(doy)
    name = TECU_model+doy+'0.'+year+'i'
#    name2='codg'+doy+'0.'+year+'i'
    tecor = AIPSTask('TECOR')
    if os.path.exists(geo_path+name):
        tecor.infile = geo_path+name
#    elif os.path.exists(name2):
#        tecor.infile='PWD:'+name2
    tecor.indata = indata
    tecor.nfiles = num_days
    tecor.gainuse = gainuse
    tecor.aparm[1:] = [1, 0]
    tecor()


##############################################################################
#
def runeops(indata, geo_path):
    logger.info('Doing EOPS to generate CL table 3')
    eops = AIPSTask('CLCOR')
    eops.indata = indata
    eops.gainver = 2
    eops.gainuse = 3
    eops.opcode = 'EOPS'
    eops.infile = geo_path+'usno_finals.erp'
    eops()

##############################################################################
#


def runuvflg(indata, flagfile):
    if flagfile != '' and os.path.exists(flagfile):
        uvflg = AIPSTask('UVFLG')
        uvflg.indata = indata
        uvflg.intext = flagfile
        uvflg.opcode = 'FLAG'
        uvflg.go()
    else:
        logger.info('No UVFLG file applied.')


##############################################################################
#
def runindxr(indata):
    indxr = AIPSTask('indxr')
    indxr.indata = indata
    indxr.cparm[1:] = [0, 0, 1./60.]
    indxr()

##############################################################################
#


def runsnflg(indata, inver, calsource):

    flag_sources = [calsource]
    snflg = AIPSTask('snflg')
    snflg.indata = indata
    snflg.flagver = 0
    snflg.inext = 'SN'
    snflg.inver = inver
    snflg.optype = 'JUMP'
    snflg.dparm[1:] = [57., 10., 0.]
    snflg()

##############################################################################
#


def run_elvflag(indata, elv_min, outfg):
    uvflg = AIPSTask('UVFLG')
    uvflg.indata = indata
    uvflg.opcode = 'FLAG'
    uvflg.aparm[1:] = [0, elv_min]
    uvflg.outfgver = outfg
    logger.info('#####################################')
    logger.info('Flagging data for Elevations < '+str(elv_min))
    logger.info('#####################################')
    uvflg.go()
##############################################################################


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
#


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


##############################################################################
# Run DELZN
#
def run_delzn(indata):
    indata.zap_table('PL', -1)
    if os.path.exists('DELZN.FITS'):
        os.popen('rm DELZN.FITS')

    ant = get_ant(indata)

    delzn = AIPSTask('DELZN')
    delzn.indata = indata
    delzn.aparm[1:] = [0, 2, 2, 0, 0, 0, 0, 0, 1, 0]
    delzn.nplots = len(ant) - 1
    delzn.outfile = 'PWD:DELZN.FITS'
    delzn.dotv = -1
    delzn()

    if os.path.exists('delzn.ps'):
        os.popen('rm delzn.ps')
    lwpla = AIPSTask('LWPLA')
    lwpla.indata = indata
    lwpla.inver = 0
    lwpla.outfile = 'PWD:delzn.ps'
    lwpla()

    indata.zap_table('PL', -1)


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
    # if >= 1, smooth within with one source;if <=0 smooth separately
    clcal.dobtween = dobtween
    clcal.input()
    clcal()


##############################################################################
# Run QUACK
#
def runquack(indata, antennas, time):
    quack = AIPSTask('QUACK')
    quack.indata = indata
    quack.antennas[1:] = antennas
    quack.opcode = 'ENDB'
    quack.aparm[1:] = [0, time, 0]
    quack()


def endquack(indata, antennas, time, outfgver):
    quack = AIPSTask('QUACK')
    quack.indata = indata
    quack.antennas[1:] = antennas
    quack.opcode = 'ENDB'
    quack.aparm[1:] = [0, time, 0]
    quack.flagver = outfgver
    quack()


def begquack(indata, antennas, time, outfgver):
    quack = AIPSTask('QUACK')
    quack.indata = indata
    quack.antennas[1:] = antennas
    quack.opcode = 'BEG'
    quack.aparm[1:] = [0, time, 0]
    quack.flagver = outfgver
    quack()
###############################################################


def run_aclip(indata, infg, outfg, gainuse, ant, ifnum, pol, vmax, near):
    aclip = AIPSTask('ACLIP')
    aclip.indata = indata
    aclip.flagver = infg
    aclip.outfgver = outfg
    aclip.antenna[1:] = [ant, 0]
    aclip.bif = ifnum
    aclip.eif = ifnum
    aclip.stokes = pol
    aclip.docalib = 1
    aclip.gainuse = gainuse
    aclip.aparm[1] = vmax  # maximum allowed
    aclip.aparm[3] = 0.01  # minimum allowed (0 is -1e6)
    aclip.aparm[7] = near  # if =1 flag surrounding channels
    aclip.go()

##############################################################################
#

def run_uvflg(indata, timeran, bif, eif, bchan, echan, antennas, outfg):
    uvflg = AIPSTask('UVFLG')
    uvflg.indata = indata
    uvflg.opcode = 'FLAG'
    uvflg.timer[1:] = timeran
    uvflg.bif = bif
    uvflg.eif = eif
    uvflg.bchan = bchan
    uvflg.echan = echan
    uvflg.antenna[1:] = antennas
    uvflg.outfgver = outfg
    # uvflg.input()
    uvflg.go()
##############################################################################
#
def runsnsmo(indata, inver, outver, refant):
    snsmo = AIPSTask('SNSMO')
    snsmo.indata = indata
    snsmo.refant = refant
    snsmo.inver = inver
    snsmo.outver = outver
    snsmo.bparm[1:] = [0, 0, 1, 1, 1]
    snsmo.smotype = 'VLBI'
    snsmo()
##############################################################################
#


def runtasav(indata, i):
    tasav = AIPSTask('TASAV')
    tasav.indata = indata
    tasav.outna = indata.name
    tasav.outcla = 'TASAV'+str(i)
    tasav.outdisk = indata.disk
    tasav_data = AIPSUVData(indata.name, 'TASAV'+str(i), int(indata.disk), 1)
    if tasav_data.exists():
        logger.info('TASAV file exists, do not need save tables')
    else:
        tasav()

##############################################################################
#


def man_pcal(indata, refant, mp_source, mp_timera, gainuse, dpfour):

    if mp_source == ['']:
        mp_source = []
        for source in indata.sources:
            if source[0] == 'F':
                mp_source.append(source)

    fringe = AIPSTask('FRING')
    fringe.indata = indata
    fringe.refant = refant
    fringe.docal = 1
    fringe.solint = 10
    fringe.bchan = 0
    fringe.echan = 0
    fringe.gainuse = gainuse
    fringe.aparm[1:] = [3, 0]
    fringe.dparm[8] = 1
    fringe.dparm[2] = 0
    fringe.dparm[3] = 0
    # +++ZB (same as 060907)
    fringe.dparm[2] = 500
    # fringe.dparm[2]   = 50
    fringe.dparm[3] = 500
    fringe.dparm[4] = dpfour
    fringe.snver = 0
    fringe.calso[1:] = mp_source
#    fringe.inputs()
    if mp_timera == 0:
        fringe.timer[1:] = [0]
        fringe()
    else:
        fringe.timer[1:] = mp_timera
        fringe.input()
        fringe()
##############################################################################
#


def run_bpass_cal(indata, bandcal, gainuse, flagver):
    if bandcal == ['']:
        logger.info('No Bandpass calibrator selected.')
        sys.exit()

    if indata.table_highver('AIPS BP') > 0:
        logger.info('Deleting old BP tables.')
        while indata.table_highver('AIPS BP') > 0:
            indata.zap_table('AIPS BP', 0)

    bpass = AIPSTask('BPASS')
    bpass.indata = indata
    bpass.calsour[1:] = bandcal
    bpass.docal = 1
    bpass.gainuse = gainuse
    bpass.flagver = flagver
    bpass.solint = -1
    bpass.bpassprm[4] = 1  # only store phase
    bpass.bpassprm[5] = 0
    bpass.bpassprm[10] = 3
    bpass.outver = 1
    bpass.go()

##############################################################################
#


def runtacop(indata, outdata, inext, inver, outver, ncount):
    tacop = AIPSTask('TACOP')
    tacop.indata = indata
    tacop.outdata = outdata
    tacop.inext = inext
    tacop.inver = inver
    tacop.outver = outver
    tacop.ncount = ncount
    tacop()


##############################################################################
#
def runatmos(indata, atmos_file):
    atmos = AIPSTask('CLCOR')
    atmos.indata = indata
    atmos.gainver = 3
    atmos.gainuse = 4
    atmos.clcorprm[1:] = [1, 0]
    atmos.opcode = 'ATMO'
    atmos.infile = 'PWD:' + atmos_file
    atmos()


def runionos(indata, ionos_file):
    atmos = AIPSTask('CLCOR')
    atmos.indata = indata
    atmos.gainver = 4
    atmos.gainuse = 4
    atmos.clcorprm[1:] = [1, 0]
    atmos.opcode = 'IONO'
    atmos.infile = 'PWD:' + ionos_file
    atmos()


##############################################################################
#
def runpang(indata):
    pang = AIPSTask('CLCOR')
    pang.indata = indata
    pang.gainver = 4
    pang.gainuse = 4
    pang.opcode = 'PANG'
    pang.clcorprm[1:] = [1, 0]
    antennas = []
    for row in indata.table('AN', 0):
        if row['mntsta'] == 0:
            antennas.append(row['nosta'])
    pang.antennas[1:] = antennas
    pang()


##############################################################################
#
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


##############################################################################
#
def runaccor(indata):
    accor = AIPSTask('ACCOR')
    accor.indata = indata
    accor.timer[1:] = [0]
    accor.solint = 0
    accor()


##############################################################################
#
def run_setjy(indata, source, flux):
    setjy = AIPSTask('SETJY')
    setjy.indata = indata
    setjy.source[1:] = [source]
    setjy.zerosp[1:] = flux
    setjy.optype = ''
    setjy.bif = 0
    setjy.eif = 0
    setjy.optype = 'VCAL'
    setjy.optype
    setjy()


##############################################################################
#
def runantab(indata, antabfile):
    antab = AIPSTask('ANTAB')
    antab.indata = indata
    antab.calin = antabfile
    antab.tyver = 1
    antab.gcver = 1
    antab.offset = 60
    antab.go()


##############################################################################
#
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


##############################################################################
#
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
    if indata.table_highver('AIPS WX')>=1:
        apcal.inver = 1  # use WX table 1
    if isinstance(dofit, int):
        for i in ant: apcal.dofit[i] = dofit
        if antname == 'EVN':
            for i in range(30): apcal.dofit[i+1] = -1
    else:
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
            os.popen('mv ' + filename + ' ' + outname[0] + '/')


#################################################################################
def run_fringecal_2(indata, fr_image, nmaps, gainuse, refant, refant_candi, calsource, solint, smodel, doband, bpver, no_rate, dwin, rwin):
    fringe = AIPSTask('FRING')
    if fr_image.exists():
        fringe.in2data = fr_image
        logger.info('################################################')
        logger.info('Using input model '+fringe.in2name+'.'+fringe.in2class+'.' +
               str(int(fringe.in2seq))+' on diks '+str(int(fringe.in2disk)))
        logger.info('################################################')
    elif smodel != [1, 0]:
        fringe.smodel[1:] = smodel
        logger.info('################################################')
        logger.info('Using SMODEL='+str(smodel)+' for fringe.')
        logger.info('################################################')
    else:
        logger.info('################################################')
        logger.info('Using point source as imput model for fringe.')
        logger.info('################################################')

    if doband == 1:
        logger.info('################################################')
        logger.info('Applying bandpass table '+str(bpver))
        logger.info('################################################')
    else:
        logger.info('################################################')
        logger.info('Applying no bandpass table ')
        logger.info('################################################')

    fringe.indata = indata
    fringe.refant = refant
    fringe.docal = 1
    fringe.calsour[1:] = [calsource]
    fringe.solint = solint
    fringe.aparm[1:] = [2, 0, 1, 0, 1, 0, 0, 0, 1]  # change if needed
    fringe.dparm[1:] = [0, dwin, rwin, 0]
    # fringe.dparm[4]    = dpfour
    fringe.dparm[8] = 0  # zeroing rate, delay, phase?
    fringe.dparm[9] = no_rate  # supressing rate(1) or not(0)?
    fringe.nmaps = nmaps
    fringe.snver = 0
    fringe.gainuse = gainuse
    fringe.doband = int(doband)
    fringe.bpver = int(bpver)
    fringe.search[1:] = refant_candi
    fringe()


def run_fringecal_1(indata, refant, refant_candi, calsource, gainuse, flagver, solint, doband, bpver, dwin, rwin):
    fringe = AIPSTask('FRING')
    fringe.indata = indata
    fringe.refant = refant
    fringe.docal = 1
    if (type(calsource) == type('string')):
        fringe.calsour[1] = calsource
    else:
        fringe.calsour[1:] = calsource
    fringe.search[1:] = refant_candi
    fringe.solint = solint
    fringe.aparm[1:] = [3, 0, 0, 0, 1, 0, 0, 0, 1]
    fringe.dparm[1:] = [0, dwin, rwin, 0]
    # fringe.dparm[4]   = dpfour
    fringe.dparm[8] = 0
    fringe.gainuse = gainuse
    fringe.flagv = flagver
    fringe.snver = 0
    fringe.doband = int(doband)
    fringe.bpver = int(bpver)
    fringe.input()
    fringe()


##############################################################################
#
def runimagr(indata, source, niter, cz, iz, docal, imna, antennas, uvwtfn, robust, beam):
    if imna == '':
        outname = source
    else:
        outname = source[:11 - len(imna)] + '-' + imna
    logger.info('#########################################################')
    logger.info('Imaging ' + source + ' with imsize=' + str(iz) + ', cellsize=' + str(cz) +
           ' and ' + str(niter) + ' iterations. Using antennas=' + str(antennas) +
           '.')
    logger.info('#########################################################')
    imagr = AIPSTask('IMAGR')
    imagr.indata = indata
    imagr.docal = docal
    imagr.sourc[1:] = [source]
    imagr.uvwtfn = uvwtfn
    imagr.robust = robust
    imagr.bif = 0
    imagr.eif = 0
    imagr.nchav = 16
    imagr.bchan = 0
    imagr.echan = 0
    imagr.cellsize[1:] = [cz, cz]
    imagr.imsize[1:] = [iz, iz]
    imagr.outna = outname
    imagr.niter = niter
    imagr.outdisk = indata.disk
    imagr.dotv = -1
    imagr.antennas[1:] = antennas
    imagr.bmaj = beam[0]
    imagr.bmin = beam[1]
    imagr.bpa = beam[2]
    imagr()


##############################################################################
#
def rungridimagr(indata, source, niter, cz, iz, docal, uvwtfn, robust, beam):
    imagr = AIPSTask('IMAGR')
    imagr.indata = indata
    imagr.docal = docal
    imagr.sourc[1:] = [source]
    imagr.uvwtfn = uvwtfn
    imagr.robust = robust
    imagr.bif = 0
    imagr.eif = 0
    imagr.nchav = 16
    imagr.uvtaper[1:] = [100000, 100000]
    imagr.uvwtfn = 'N'
    imagr.bchan = 0
    imagr.echan = 0
    imagr.cellsize[1:] = [cz, cz]
    imagr.imsize[1:] = [iz, iz]
    imagr.outna = source
    imagr.niter = niter
    imagr.outdisk = indata.disk
    imagr.dotv = -1
    imagr.bmaj = beam[0]
    imagr.bmin = beam[1]
    imagr.bpa = beam[2]
    imagr()


##############################################################################
#
def runmaimagr(indata, source, niter, cz, iz, channel, docal, imna, uvwtfn, robust, beam):
    if imna == '':
        outname = source
    else:
        outname = source[:11 - len(imna)] + '-' + imna

    imagr = AIPSTask('IMAGR')

    if indata.header['naxis'][3] > 1:
        imagr.bif = input('Enter IF: ')
        imagr.eif = imagr.bif
    else:
        imagr.eif = 1
        imagr.bif = 1

    imagr.indata = indata
    imagr.docal = docal
    imagr.sourc[1:] = [source]
    imagr.uvwtfn = uvwtfn
    imagr.robust = robust
    imagr.nchav = 1
    imagr.bchan = channel
    imagr.echan = channel
    imagr.cellsize[1:] = [cz, cz]
    imagr.imsize[1:] = [iz, iz]
    imagr.outna = outname
    imagr.niter = niter
    imagr.outdisk = indata.disk
    imagr.dotv = -1
    imagr.bmaj = beam[0]
    imagr.bmin = beam[1]
    imagr.bpa = beam[2]
    imagr()


##############################################################################
#
def runcube(indata, source, niter, cz, iz, bch, ech, docal, ant, uvwtfn, robust, beam):
    imagr = AIPSTask('IMAGR')

    if indata.header['naxis'][3] > 1:
        imagr.bif = input('Enter IF: ')
        imagr.eif = imagr.bif
    else:
        imagr.eif = 1
        imagr.bif = 1

    imagr.indata = indata
    imagr.docal = docal
    imagr.sourc[1:] = [source]
    imagr.antennas[1:] = ant
    imagr.nchav = 1
    imagr.bchan = bch
    imagr.echan = ech
    imagr.uvwtfn = uvwtfn
    imagr.robust = robust
    imagr.cellsize[1:] = [cz, cz]
    imagr.imsize[1:] = [iz, iz]
    imagr.outna = source
    imagr.niter = niter
    imagr.outdisk = indata.disk
    imagr.dotv = -1
    imagr.bmaj = beam[0]
    imagr.bmin = beam[1]
    imagr.bpa = beam[2]
    imagr()


##############################################################################
#
def runprtmasn(indata, channel):
    prtab = AIPSTask('PRTAB')
    prtab.indata = indata
    prtab.inext = 'SN'
    prtab.invers = 0
    prtab.docrt = -1
    prtab.box[1][1] = 1
    prtab.box[1][2] = 3
    prtab.box[1][3] = 4
    prtab.box[1][4] = 9
    if check_sn_ver(indata) > 15:
        prtab.box[2][1] = 15
        prtab.box[2][2] = 17
    else:
        prtab.box[2][1] = 13
        prtab.box[2][2] = 15
    prtab.dohms = -1
    (year, month, day) = get_observation_year_month_day(indata)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY',
                 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_' + \
        prtab.inname + '_CH' + str(channel) + '.RATE'
    prtab()


##############################################################################
#
def runprtmasu(indata, channel):
    prtab = AIPSTask('PRTAB')
    prtab.indata = indata
    prtab.inext = 'SU'
    prtab.invers = 0
    prtab.docrt = -1
    prtab.box[1][1] = 1
    prtab.box[1][2] = 2
    prtab.box[1][3] = 11
    prtab.box[1][4] = 12
    prtab.box[2][1] = 13
    prtab.box[2][2] = 14
    prtab.box[2][3] = 15
    prtab.dohms = -1
    prtab.ndig = 4
    (year, month, day) = get_observation_year_month_day(indata)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY',
                 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_' + \
        prtab.inname + '_CH' + str(channel) + '.SU'
    prtab()


##############################################################################
#
def runcvel(indata, cvelsource, vel, inter_flag, doband, bpver):
    logger.info('Running CVEL.')
    if inter_flag == 1:
        cvelsource = check_calsource(indata, cvelsource)

    naxis = indata.header['naxis']
    crpix = indata.header['crpix']

    if isinstance(vel, float) or isinstance(vel, int):
        vel = [vel]

    if naxis[3] != len(vel):
        logger.info('You have ' + str(naxis[3]) + ' IFs, and ' + \
            str(len(vel)) + ' velocities.')
        sys.exit()
    (linename, restfreq) = get_line_name(indata)

    #    freq = get_center_freq(indata)/1e9
    #    if freq>12 and freq<13:
    #        restfreq = [1.2178E+10,597000]
    #        print 'Assuming 12.2 GHz methanol maser.'
    #    elif freq>22 and freq<23:
    #        restfreq = [2.2235E+10,80000]
    #        print 'Assuming 22.2 GHz water maser.'
    #    elif freq>6 and freq<7:
    #        restfreq = [6.668e+09, 519200]
    #        print 'Assuming 6.7 GHz methanol maser.'
    #    elif freq>43.1 and freq<43.2:
    #        restfreq = [43.122e+09,80000]
    #       print 'Assuming 43.122 GHz SiO maser.'
    #    else:
    #        print 'Unknown maser line.'

    setjy = AIPSTask('SETJY')
    setjy.indata = indata
    setjy.source[1:] = cvelsource
    setjy.restfreq[1:] = restfreq
    setjy.optype = ''
    setjy.veltyp = 'LSR'
    setjy.veldef = 'RADIO'
    channum = indata.header['naxis'][2]
    setjy.aparm[1:] = [channum / 2. + crpix[2], 0]
    #    if int(aipsver[6])>1:
    #        setjy.optype='VCAL'

    for i in range(naxis[3]):
        setjy.sysvel = vel[i]
        setjy.bif = i + 1
        setjy.eif = i + 1
        setjy()

    cvel = AIPSTask('CVEL')
    cvel.indata = indata
    cvel.source[1:] = cvelsource
    cvel.outna = cvel.inna
    cvel.outcl = cvel.incl
    cvel.gainuse = 7
    cvel.freqid = 1
    cvel.outseq = cvel.inseq + 1
    cvel.outdisk = cvel.indisk
    cvel.doband = doband
    cvel.bpver = bpver
    #    cvel.aparm[1] = vel[i]
    #    cvel.aparm[2] = channum
    #    cvel.aparm[3] = 0
    #    cvel.aparm[4] = 1
    #    cvel.aparm[5] = restfreq[0]
    #    cvel.aparm[6] = restfreq[1]

    cveldata = AIPSUVData(cvel.inna, cvel.incl, int(cvel.indisk), 2)
    if cveldata.exists():
        cveldata.clrstat()
        cveldata.zap()
    cvel()

    indxr = AIPSTask('indxr')
    indxr.indata = cveldata
    indxr()

#########################################################################################


def run_calib_1(indata, fr_image, smode, gainuse, refant, snout, doband, bpver, calsour, flagver, solint):
    calib = AIPSTask('CALIB')
    calib.indata = indata
    calib.docalib = 1
    calib.doband = int(doband)
    calib.bpver = int(bpver)
    calib.gainuse = gainuse
    calib.cmethod = 'DFT'
    calib.in2data = fr_image
    calib.nmaps = 1
    if (type(calsour) == type('string')):
        calib.calsour[1] = calsour
    else:
        calib.calsour[1:] = calsour
        calib.flagver = flagver
        calib.refant = refant
        calib.solmode = smode
        calib.snver = snout
        calib.solint = solint*2
    if smode == 'P':
        nant = 3
    elif smode == 'A&P':
        nant = 4
    calib.aparm[1:] = nant, 0, 1, 0, 1, 0
    calib.normaliz = 1
    calib.cparm[1:] = 15, 1, 0
    calib.input()
    calib.go()

##############################################################################
#


def run_split2(indata, source, gainuse, outclass, doband, bpver, flagver, split_seq):

    channels = indata.header['naxis'][2]
    if channels == 16:
        bad = 1                     # remove 1 channel from each side
    elif channels == 32:
        bad = 2                     # remove 2 channels from each side
    elif channels == 64:
        bad = 4                     # remove 2 channels from each side
    elif channels == 128:
        bad = 6                     # remove 6 channels from each side
    elif channels == 256:
        bad = 8                     # remove 8 channels from each side
    elif channels == 512:
        bad = 10                    # remove 10 channels from each side
    elif channels == 1024:
        bad = 12                    # remove 12 channels from each side
    else:
        bad = 0

    [bchan, echan] = [1+bad, channels-bad]

    logger.info ('Averaging channels '+str(bchan)+' - '+str(echan)+'.')

    split_data = AIPSUVData(source, outclass, indata.disk, split_seq)

    if split_data.exists():
        logger.info ('Zapping old split data')
        split_data.clrstat()
        split_data.zap()
    if isinstance(source, str):
        source = [source]

    split = AIPSTask('SPLIT')
    split.indata = indata
    split.bchan = 0  # bchan
    split.echan = 0  # echan
    # split.freqid     = 1
    split.docalib = 1
    # split.qual	     = -1
    split.gainuse = gainuse
    split.flagver = flagver
    split.source[1:] = source
    split.outclass = outclass
    split.outseq = split_seq
    split.aparm[1:] = [2, 2, 0]
    # split.aparm[6]   = 1
    split.outdisk = indata.disk
    split.doband = doband
    split.bpver = bpver
    # split.smooth[1:] = smooth
    # split.input()
    split.ichansel[1] = [None, 1+bad, channels-bad, 1, 0]
    split()

    fittp = AIPSTask('FITTP')
    fittp.indata = split_data
    fitname = fittp.inname+'_CL'+str(gainuse)+'_'+fittp.inclass+'_'+str(int(fittp.inseq))+'.splt'
    fittp.dataout = 'PWD:'+fitname

    if split_data.exists():
        logger.info('Writing out calibrated and splitted uv-data for '+source[0])
        fittp.go()
    else:
        logger.info('No calibrated and splitted uv-data for '+source[0])

    if os.path.exists(outname[0]+'/'+fitname):
        os.popen(r'rm '+outname[0]+'/'+fitname)
    if os.path.exists(fitname):
        os.popen(r'mv '+fitname+' '+outname[0]+'/')


def run_split(indata, source, outclass, doband, bpver):
    channels = indata.header['naxis'][2]
    if channels == 16:
        bad = 1  # remove 1 channel from each side
    elif channels == 32:
        bad = 2  # remove 2 channels from each side
    elif channels == 64:
        bad = 4  # remove 2 channels from each side
    elif channels == 128:
        bad = 6  # remove 6 channels from each side
    elif channels == 256:
        bad = 8  # remove 8 channels from each side
    elif channels == 512:
        bad = 10  # remove 10 channels from each side
    elif channels == 1024:
        bad = 12  # remove 12 channels from each side
    else:
        bad = 0

    [bchan, echan] = [1 + bad, channels - bad]

    logger.info('Averaging channels ' + str(bchan) + ' - ' + str(echan) + '.')

    target = findtarget(indata, source)
    if isinstance(target, str):
        target = [target]

    if target != []:
        for source in target:
            split_data = AIPSUVData(source, outclass, indata.disk, 1)
            if split_data.exists():
                split_data.clrstat()
                split_data.zap()

        split = AIPSTask('SPLIT')
        split.indata = indata
        split.bchan = bchan
        split.echan = echan
        split.docalib = 1
        split.flagver = 0
        split.source[1:] = target
        split.outclass = outclass
        split.aparm[1:] = [3, 0]
        split.aparm[6] = 1
        split.outdisk = indata.disk
        split.doband = doband
        split.bpver = bpver
        split.smooth[1:] = smooth
        # split.input()
        split()


def run_fittp_data(source, outcl, disk):
    fittp = AIPSTask('FITTP')
    data = AIPSUVData(source, outcl, disk, 1)
    fittp.indata = data
    if os.path.exists(fittp.inname + '.' + fittp.inclass + '.fits'):
        os.popen(r'rm ' + fittp.inname + '.' + fittp.inclass + '.fits')
    fittp.dataout = 'PWD:' + fittp.inname + '.' + fittp.inclass + '.fits'

    if data.exists():
        logger.info('Writing out calibrated and splitted uv-data for ' + source)
        fittp.go()
    else:
        logger.info('No calibrated and splitted uv-data for ' + source)


def shift_pos(indata, source, ra, dec, inver, outver):
    if source == '':
        source = findcal(indata, '')
    clcor = AIPSTask('CLCOR')
    clcor.indata = indata
    clcor.source[1] = source
    clcor.opcode = 'ANTC'
    clcor.clcorprm[5] = ra
    clcor.clcorprm[6] = dec
    clcor.gainver = inver
    clcor.gainuse = outver
    if ra != 0 or dec != 0:
        clcor()


def run_grid(indata, source, cellsize, imsize, n, m, grid_offset, uvwtfn, robust, beam):
    grid = []
    if n % 2 != 0:
        for i in range(n):
            if m % 2 != 0:
                for j in range(m):
                    grid.append([i - n / 2, j - m / 2])

    for shift in grid:
        shift_pos(indata, source, shift[0] *
                  grid_offset, shift[1] * grid_offset, 8, 9)

        channels = indata.header['naxis'][2]
        if channels == 16:
            bad = 1  # remove 1 channel from each side
        elif channels == 32:
            bad = 2  # remove 2 channels from each side
        elif channels == 64:
            bad = 4  # remove 2 channels from each side
        elif channels == 128:
            bad = 6  # remove 6 channels from each side
        elif channels == 256:
            bad = 8  # remove 8 channels from each side
        elif channels == 512:
            bad = 10  # remove 10 channels from each side
        elif channels == 1024:
            bad = 12  # remove 12 channels from each side
        else:
            bad = 0

        [bchan, echan] = [1 + bad, channels - bad]

        split_data = AIPSUVData(source, 'GRIDS', indata.disk, 1)
        if split_data.exists():
            split_data.clrstat()
            split_data.zap()

        split = AIPSTask('SPLIT')
        split.indata = indata
        split.bchan = bchan
        split.echan = echan
        split.docalib = 1
        split.flagver = 0
        split.source[1:] = [source]
        split.outclass = 'GRIDS'
        split.aparm[1:] = [3, 0]
        split.aparm[6] = 1
        split.outdisk = indata.disk
        split()

        print
        'Imaging ' + str(shift[0]) + ' ' + str(shift[1])
        rungridimagr(split_data, source, 10, cellsize,
                     imsize, -1, uvwtfn, robust, beam)
        split_data.zap()

        restore_su(indata)
        check_sncl(indata, 4, 8)


def findcal(indata, calsource):
    if calsource == '':
        n = 0
        for source in indata.sources:
            if source[0] == 'G':
                calsource = source
                n = n+1
        if n > 1:
            logger.info('More than one Maser source! Using '+calsource)

    return calsource


def run_masplit(indata, source, outclass, doband, bpver, smooth, channel):
    source = findcal(indata, source)
    if isinstance(source, str):
        source = [source]

    if source != []:
        for target in source:
            split_data = AIPSUVData(target, outclass, indata.disk, 1)
            if split_data.exists():
                split_data.clrstat()
                split_data.zap()

        split = AIPSTask('SPLIT')
        split.indata = indata
        split.bchan = 0
        split.echan = 0
        split.flagver = 0
        split.docalib = 1
        split.source[1:] = source
        split.outclass = outclass
        split.aparm[1:] = [0, 0]
        split.aparm[6] = 1
        split.outdisk = indata.disk
        split.doband = doband
        split.bpver = bpver
        split.smooth[1:] = smooth
        split()


##############################################################################
# run possm to make an ampscalar spectrum using only the inner-5 antennae
#
def runrpossm(indata, cvelsource, tv, interflag, antennas):
    indata.zap_table('PL', -1)

    if indata.table_highver('AIPS SN') == 0:
        docal = 0
    else:
        docal = 1

    if interflag == 1:
        #        nchvel = input('Enter 1 for vel or 2 for ch: ')
        #        chvel_str=['vel','ch']
        #        chvel=chvel_str[nchvel-1]
        chvel = 'vel'

        if indata.header['naxis'][3] > 1:
            bif = input('Enter IF: ')
            eif = bif
        else:
            eif = 1
            bif = 1

        possm = AIPSTask('POSSM')
        possm.indata = indata
        # possm.source[1:]  = cvelsource[0]
        possm.source[1:] = cvelsource
        # possm.antenna[1:] = [2,4,5,8,9]
        possm.antenna[1:] = antennas
        possm.stokes = 'I'
        possm.docal = docal
        possm.gainuse = 0
        possm.nplots = 0
        possm.bchan = 1
        possm.echan = 0
        possm.bif = bif
        possm.eif = eif
        possm.aparm[8] = 0
        possm.aparm[1] = -1
        possm.codetype = 'AMP'
        if AIPSTV.AIPSTV().exists():
            possm.dotv = 1
            gv_flag = 0
        else:
            possm.dotv = -1
            gv_flag = 1
        possm()

        bchan = input('Enter bchan: ')
        echan = input('Enter echan: ')

    else:
        chvel = 'vel'
        bchan = 0
        echan = 0
        bif = 1
        eif = 1

    if bchan == echan and echan != 0:
        print
        'Only one channel selected.'

    elif bchan > echan:
        print
        'bchan > echan'

    else:
        possm = AIPSTask('POSSM')
        possm.indata = indata
        # possm.source[1:]  = cvelsource[0]
        possm.source[1:] = cvelsource
        # possm.antenna[1:] = [2,4,5,8,9]
        possm.antenna[1:] = [3, 4, 7, 8]
        possm.stokes = 'I'
        possm.docal = docal
        possm.gainuse = 0
        possm.nplots = 0
        possm.bchan = bchan
        possm.echan = echan
        possm.bif = bif
        possm.eif = eif
        possm.aparm[8] = 0
        possm.aparm[1] = -1
        possm.codetype = 'AMP'

        (linename, restfreq) = get_line_name(indata)

        # --- x-axis labeled with channel number
        if chvel == 'ch':
            if bchan == 0 and echan == 0:
                spectfile = 'PWD:' + \
                    cvelsource[0] + '.' + linename + '.spectrum.txt'
                filename = cvelsource[0] + '.' + linename + '.POSSM.ps'
            else:
                spectfile = ''
                filename = cvelsource[0] + '.' + linename + \
                    '.POSSM_CH' + str(bchan) + '-' + str(echan) + '.ps'

            if gv_flag == 0:
                possm.dotv = -1
                possm.outtext = spectfile
                possm()

            if os.path.exists(filename):
                os.popen('rm ' + filename)
            lwpla = AIPSTask('LWPLA')
            lwpla.indata = indata
            lwpla.inver = 0
            lwpla.outfile = 'PWD:' + filename
            lwpla()

        # --- x-axis labeled with velocity
        if chvel == 'vel':
            possm.aparm[7] = 2
            possm.aparm[10] = 1
            possm.dotv = -1
            possm()

            filename = cvelsource[0] + '.' + linename + '.POSSM.ps'

            if os.path.exists(filename):
                os.popen('rm ' + filename)
            lwpla = AIPSTask('LWPLA')
            lwpla.indata = indata
            lwpla.inver = 0
            lwpla.outfile = 'PWD:' + filename
            lwpla()
        os.popen(r'ps2pdf ' + filename)

        indata.zap_table('PL', -1)
        # os.popen('gv '+filename)


###############################################################################
# Get peak and rms from an image
#
def runimean(imgdata, blc=[0, 0, 0], trc=[0, 0, 0]):
    '''Must set imgdata'''
    if os.path.exists('imean.txt'):
        os.popen('rm imean.txt')
    imean = AIPSTask('imean')
    imean.indata = imgdata
    imean.blc[1:] = blc
    imean.trc[1:] = trc
    if int(aipsver[6]) > 1:
        imean.doprint = 1
    imean.outtext = 'PWD:imean.txt'
    imean()
    # datamax = imgdata.header.datamax
    datamax = get_image_peak()
    return (datamax, imean.pixstd)
################################################################################
# run SAD for maser source
#


def run_ma_sad(inimg, indata, cut, dyna):
    if inimg.exists():
        inimg.clrstat()
        num_ch = inimg.header.naxis[3-1]
        srcname = inimg.name
        obs = inimg.header['observer']
        date_obs = inimg.header['date_obs']
        (linename, restfreq) = get_line_name(indata)
        for line in inimg.history:
            if line[0:11] == 'IMAGR BCHAN':
                bchan = int(line[15:22])
            if line[0:11] == 'IMAGR ECHAN':
                echan = int(line[15:22])
                break

        bch_str = str(bchan+1000)
        bch_str = bch_str[1:4]
        ech_str = str(echan+1000)
        ech_str = ech_str[1:4]

        sad_file = srcname+'_'+linename+'_'+obs+'_' + \
            date_obs+'_CH'+bch_str+'-'+ech_str+'_sad.txt'
        if os.path.exists(sad_file):
            os.popen('rm '+sad_file)
        if os.path.exists('sad.txt'):
            os.popen('rm sad.txt')

        sad = AIPSTask('SAD')
        sad.indata = inimg
        sad.doresid = -1
        sad.ngauss = 3
        # --- for weak source, we may need to increase gain
        sad.gain = 0.3
        sad.sort = 'S'
        sad.docrt = -4
        sad.fitout = 'PWD:'+'sad.txt'
        mpeak = []
        mrms = []
        for i in range(1, num_ch+1):
            (peak, rms) = runimean(inimg, [0, 0, i], [0, 0, i])
            mpeak.append(peak)
            mrms.append(rms)

            c1 = peak*0.5
            c3 = max(rms*cut, peak*dyna)
            c2 = (c1 + c3)*0.5

            d1 = c3
            d2 = c3
            d3 = 0
            # --- pixel (depended on the compactness)
            # --- cellsize = 0.1 mas, then 40 means 4 mas
            d4 = 40
            d5 = 40
            cparm = [c1, c2, c3]
            cparm.sort()
            cparm.reverse()
            sad.cparm[1:] = cparm
            sad.icut = c3
            sad.dparm[1:] = [d1, d2, d3, d4, d5]
            sad.blc[3] = i
            sad.trc[3] = i
            if peak > rms*cut:
                sad()

        cmd = 'cp sad.txt '+sad_file
        os.popen(cmd)
        logger.info('Channel:   Peak     rms      SNR')
        logger.info('            (Jy)   (Jy)')
        logger.info('---------------------------------')
        for i in range(len(mpeak)):
            logger.info(('%3d     %7.4f %7.4f %8.4f' % (i+bchan-1,
                                                   mpeak[i], mrms[i], mpeak[i]/mrms[i])))
    else:
        logger.info ('Image does not exist, please check it.')
        exit()
