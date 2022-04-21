#!/usr/bin/env ParselTongue
#####!/usr/bin/python3

#sys.path.append('/usr/share/parseltongue/python/')
#sys.path.append('/usr/lib/obit/python3')
#export PYTHONPATH=$PYTHONPATH:/usr/share/parseltongue/python:/usr/lib/obit/python3

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

#def load_index_data(filepath, filename, outname, outclass, outdisk, nfiles, ncount, doconcat, antname, logfile):
def loadindx(filepath, filename, outname, outclass, outdisk, nfiles, ncount, doconcat, antname, logfile):

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

    mprint('################################################',logfile)
    mprint(str(data)+' loaded!',logfile)
    mprint('################################################',logfile)
    logging.info('################################################')
    logging.info('%s loaded!',str(data))
    logging.info('################################################')

    if data.exists():
        data.zap_table('AIPS CL',1)
        runindxr(data)
        mprint('#################',logfile)
        mprint('Data new indexed!',logfile)
        mprint('#################',logfile)
        logging.info('#################')
        logging.info('Data new indexed!')
        logging.info('#################')
    else:
        mprint('No!',logfile)
        logging.info('No!')
##############################################################################
#
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




##############################################################################
#
def runeops(indata, geo_path):
    eops        = AIPSTask('CLCOR')
    eops.indata = indata
    eops.gainver = 2
    eops.gainuse = 3
    eops.opcode  = 'EOPS'
    eops.infile  = geo_path+'usno_finals.erp'
    eops()

##############################################################################
#
def runuvflg(indata,flagfile,logfile):
    if flagfile!='' and os.path.exists(flagfile):
        uvflg        = AIPSTask('UVFLG')
        uvflg.indata = indata
        uvflg.intext = flagfile
        uvflg.opcode = 'FLAG'
        uvflg.go()
    else:
        mprint('No UVFLG file applied.',logfile)


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
    snflg             = AIPSTask('snflg')
    snflg.indata      = indata
    snflg.flagver     = 0
    snflg.inext       = 'SN'
    snflg.inver       = inver
    snflg.optype      = 'JUMP'
    snflg.dparm[1:]   = [57., 10., 0.]
    snflg()

##############################################################################
#
def run_elvflag(indata,elv_min,logfile):
    uvflg        = AIPSTask('UVFLG')
    uvflg.indata = indata
    uvflg.opcode = 'FLAG'
    uvflg.aparm[1:] = [0,elv_min]
    mprint('#####################################',logfile)
    mprint('Flagging data for Elevations < '+str(elv_min),logfile)
    mprint('#####################################',logfile)
    uvflg.go()
##############################################################################

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
#
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


##############################################################################
# Print out SN table
#
def runprtsn(indata):
    prtab = AIPSTask('PRTAB')
    prtab.indata = indata
    prtab.inext = 'SN'
    prtab.invers = 0
    prtab.docrt = -1
    prtab.ndig = 1
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
    prtab.doflag = 0
    (year, month, day) = get_observation_year_month_day(indata)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_RATE_MDEL.DAT'
    prtab()


##############################################################################
# Print out SN table
#
def runprtsn_sx(indata_s, indata_x, indata):
    prtab = AIPSTask('PRTAB')
    prtab.indata = indata_s
    prtab.inext = 'SN'
    prtab.invers = 0
    prtab.docrt = -1
    prtab.ndig = 2
    prtab.box[1][1] = 1
    prtab.box[1][2] = 3
    prtab.box[1][3] = 4
    prtab.box[1][4] = 9
    if check_sn_ver(indata_s) > 15:
        prtab.box[2][1] = 15
        prtab.box[2][2] = 17
    else:
        prtab.box[2][1] = 13
        prtab.box[2][2] = 15
    prtab.dohms = -1
    prtab.doflag = 0
    (year, month, day) = get_observation_year_month_day(indata_s)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_low.dat'
    prtab()

    prtab.indata = indata_x
    prtab.outprint = 'PWD:' + namma + '_high.dat'
    prtab()

    f_low = get_center_freq(indata_s)
    f_high = get_center_freq(indata_x)
    if indata.exists():
        f_tar = get_center_freq(indata)
    else:
        print
        'Target frequency unknonw. Using 6.67 GHz.'
        f_tar = 6.67e9

    f = open('./geoblock/diff_files.inp', 'w')
    f.writelines(namma + '_low.dat                   ' +
                 '                  ! Low frequency data\n')
    f.writelines(namma + '_high.dat                   ' +
                 '                 ! High frequency data\n')
    f.writelines(str(f_low / 1e9) + '                  ' +
                 '                               ! Low frequency\n')
    f.writelines(str(f_high / 1e9) + '                  ' +
                 '                               ! High frequency\n')
    f.writelines(str(f_tar / 1e9) + '                  ' +
                 '                             ! Target frequency\n')
    f.close()


##############################################################################
# Print out SU table
#
def runprtsu(indata):
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
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_SU_TABLE.PRTAB'
    prtab()


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
    clcal.dobtween = dobtween  # if >= 1, smooth within with one source;if <=0 smooth separately
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
##############################################################################
#
def runsnsmo(indata, inver, outver, refant):
    snsmo           = AIPSTask('SNSMO')
    snsmo.indata    = indata
    snsmo.refant    = refant
    snsmo.inver     = inver
    snsmo.outver    = outver
    snsmo.bparm[1:] = [0, 0, 1, 1, 1]
    snsmo.smotype   = 'VLBI'
    snsmo()
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
        mprint('TASAV file exists, do not need save tables', logfile)
    else:
        tasav()

##############################################################################
#

##############################################################################
#
def runtacop(indata, outdata, inext, inver, outver, ncount):
    tacop         = AIPSTask('TACOP')
    tacop.indata  = indata
    tacop.outdata = outdata
    tacop.inext   = inext
    tacop.inver   = inver
    tacop.outver  = outver
    tacop.ncount  = ncount
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
    print
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
    antab.offset = 3600
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
            os.popen('mv ' + filename + ' /' + outname[0] + '/')


##############################################################################
#
def runimagr(indata, source, niter, cz, iz, docal, imna, antennas, uvwtfn, robust, beam, logfile):
    if imna == '':
        outname = source
    else:
        outname = source[:11 - len(imna)] + '-' + imna
    mprint('#########################################################', logfile)
    mprint('Imaging ' + source + ' with imsize=' + str(iz) + ', cellsize=' + str(cz) +
           ' and ' + str(niter) + ' iterations. Using antennas=' + str(antennas) +
           '.', logfile)
    mprint('#########################################################', logfile)
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
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_' + prtab.inname + '_CH' + str(channel) + '.RATE'
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
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    prtab.outprint = 'PWD:' + namma + '_' + prtab.inname + '_CH' + str(channel) + '.SU'
    prtab()


##############################################################################
#
def runcvel(indata, cvelsource, vel, inter_flag, doband, bpver):
    print
    'Running CVEL.'
    if inter_flag == 1:
        cvelsource = check_calsource(indata, cvelsource)

    naxis = indata.header['naxis']
    crpix = indata.header['crpix']

    if isinstance(vel, float) or isinstance(vel, int):
        vel = [vel]

    if naxis[3] != len(vel):
        print
        'You have ' + str(naxis[3]) + ' IFs, and ' + str(len(vel)) + ' velocities.'
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


##############################################################################
#
def runpossm(indata, calsource='', ant_use=[0], doband=-1, bpver=1, bchan=1, echan=0, gainuse=1, flagver=0,bpv=0,
             stokes='HALF', nplot=9):
    indata.zap_table('PL', -1)

    # calsource=check_calsource(indata, calsource)

    if bchan == echan and echan != 0:
        print
        'Only one channel selected.'

    elif bchan > echan:
        print
        'bchan > echan'

    else:
        possm = AIPSTask('POSSM')
        possm.eif = 0
        possm.bif = 0
        possm.indata = indata
        if (type(calsource) == type('string')):
            possm.source[1] = calsource
        else:
            possm.source[1:] = calsource
        # possm.source[1:]  = [calsource]
        possm.antenna[1:] = ant_use
        possm.stokes = stokes
        possm.docal = 1
        possm.gainuse = gainuse
        possm.nplots = nplot
        possm.bchan = bchan
        possm.echan = echan
        possm.doband = doband
        possm.bpver = bpver
        possm.flagver = flagver

        if AIPSTV.AIPSTV().exists():
            possm.dotv = 1
            gv_flag = 0
        else:
            possm.dotv = -1
            gv_flag = 1
        possm()

        if gv_flag == 1:
            if os.path.exists('possm.ps'):
                os.popen('rm possm.ps')
            lwpla = AIPSTask('LWPLA')
            lwpla.indata = indata
            lwpla.inver = 0
            lwpla.outfile = 'PWD:' + outname[0] + '-' + [calsource] + '-cl' + str(gainuse) + '-bp' + str(bpv) + '.possm'
            lwpla()

            indata.zap_table('PL', -1)
            os.popen('gv possm.ps')
            # os.popen('rm possm.ps')
##############################################################################
#
def run_snplt(indata, inter_flag):

    indata.zap_table('PL', -1)
    n_ant         = len(get_ant(indata))
    snplt         = AIPSTask('SNPLT')
    snplt.indata  = indata
    snplt.stokes  = 'RR'
    snplt.inver   = 4
    snplt.inext   = 'SN'
    snplt.optype  = 'PHAS'
    snplt.nplots  = n_ant
    snplt.bif     = 1
    snplt.eif     = 1
    snplt.dotv    = -1
    snplt()

    name=indata.name+'_sn4.ps'

    if os.path.exists(name):
        os.popen('rm '+name)

    lwpla         = AIPSTask('LWPLA')
    lwpla.indata  = indata
    lwpla.inver   = 0
    lwpla.outfile = 'PWD:'+name
    lwpla()

    if inter_flag==1:
        tv=AIPSTV.AIPSTV()
        if tv.exists()==False:
            tv.start()
        if tv.exists():
            tv.clear()

        if AIPSTV.AIPSTV().exists():
            snplt.dotv        = 1
            snplt()
        else:
            os.popen('gv '+name)

    indata.zap_table('PL', -1)

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


##############################################################################
#
def run_snplt_2(indata, inver=1, inext='sn', optype='phas', nplot=1, sources='', timer=[]):
    indata.zap_table('PL', -1)
    nif = indata.header['naxis'][3]
    n_ant = len(get_ant(indata))
    snplt = AIPSTask('SNPLT')
    snplt.indata = indata
    snplt.stokes = ''
    snplt.inver = inver
    snplt.inext = inext
    snplt.optype = optype
    snplt.nplots = nplot
    snplt.bif = 1
    snplt.eif = 0
    snplt.dotv = -1
    if (type(sources) == type('string')):
        snplt.sources[1] = sources
    else:
        snplt.sources[1:] = sources
    if (timer != None):
        snplt.timerang[1:] = timer
    snplt()

    if (os.path.exists('plotfiles') == False):
        os.mkdir('plotfiles')

        # f = open('./index.html','a')
        # f.writelines('<A NAME="'+snplt_name+'">\n')
        # f.writelines(snplt_name+' <A HREF = "#TOP">TOP</A><br>\n')
        # for n in range(1,indata.table_highver('AIPS PL')+1):
        #   name=indata.name.strip()+'_'+snplt_name+'_'+str(n)+'.ps'
        #   name2=indata.name.strip()+'_'+snplt_name+'_'+str(n)+'.png'
        name = indata.name + '_sn4.ps'
        name2 = indata.name + '_sn4.png'

        if os.path.exists(name):
            os.popen('rm ' + name)

        lwpla = AIPSTask('LWPLA')
        lwpla.indata = indata
        lwpla.plver = n
        lwpla.inver = n
        lwpla.dparm[5] = 1
        lwpla.outfile = 'PWD:' + outname[0] + '-' + inext + str(inver) + '-' + optype + '.snplt'
        lwpla()
        f.writelines('<A HREF="plotfiles/' + name + '"><img SRC="plotfiles/' + name2 + '" width=500></A>\n')
        os.popen(r'convert ' + name + ' ' + name2)
        os.popen(r'mv ' + name + ' plotfiles/')
        os.popen(r'mv ' + name2 + ' plotfiles/')

    f.writelines('<br><hr>\n')
    f.close()
    indata.zap_table('PL', -1)


##############################################################################
#
def run_split2(indata, source, gainuse, outclass, doband, bpver, flagver, logfile):
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

    print ('Averaging channels ' + str(bchan) + ' - ' + str(echan) + '.')

    split_data = AIPSUVData(source, outclass, indata.disk, 1)

    if split_data.exists():
        split_data.clrstat()
        split_data.zap()
    if isinstance(source, str):
        source = [source]

    split = AIPSTask('SPLIT')
    split.indata = indata
    split.bchan = bchan
    split.echan = echan
    split.docalib = 1
    split.gainuse = gainuse
    split.flagver = flagver
    split.source[1:] = source
    split.outclass = outclass
    split.aparm[1:] = [2, 2, 0]
    split.aparm[6] = 1
    split.outdisk = indata.disk
    split.doband = doband
    split.bpver = bpver
    # split.smooth[1:] = smooth
    # split.input()
    split()

    fittp = AIPSTask('FITTP')
    fittp.indata = split_data
    fitname = fittp.inname + '_' + fittp.inclass + '_' + str(int(fittp.inseq)) + '.splt'
    fittp.dataout = 'PWD:' + fitname

    if split_data.exists():
        mprint('Writing out calibrated and splitted uv-data for ' + source[0], logfile)
        fittp.go()
    else:
        mprint('No calibrated and splitted uv-data for ' + source[0], logfile)

    if os.path.exists(outname[0] + '/' + fitname):
        os.popen(r'rm ' + outname[0] + '/' + fitname)
    if os.path.exists(fitname):
        os.popen(r'mv ' + fitname + ' ' + outname[0] + '/')


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

    print ('Averaging channels ' + str(bchan) + ' - ' + str(echan) + '.')

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


def run_fittp_data(source, outcl, disk, logfile):
    fittp = AIPSTask('FITTP')
    data = AIPSUVData(source, outcl, disk, 1)
    fittp.indata = data
    if os.path.exists(fittp.inname + '.' + fittp.inclass + '.fits'):
        os.popen(r'rm ' + fittp.inname + '.' + fittp.inclass + '.fits')
    fittp.dataout = 'PWD:' + fittp.inname + '.' + fittp.inclass + '.fits'

    if data.exists():
        mprint('Writing out calibrated and splitted uv-data for ' + source, logfile)
        fittp.go()
    else:
        mprint('No calibrated and splitted uv-data for ' + source, logfile)


def shift_pos(indata, source, ra, dec, inver, outver):
    if source == '':
        source=findcal(indata, '')
    clcor             = AIPSTask('CLCOR')
    clcor.indata      = indata
    clcor.source[1]   = source
    clcor.opcode      = 'ANTC'
    clcor.clcorprm[5] = ra
    clcor.clcorprm[6] = dec
    clcor.gainver     = inver
    clcor.gainuse     = outver
    if ra!=0 or dec!=0:
        clcor()

def run_grid(indata, source, cellsize, imsize, n, m, grid_offset, uvwtfn, robust, beam):
    grid = []
    if n % 2 != 0:
        for i in range(n):
            if m % 2 != 0:
                for j in range(m):
                    grid.append([i - n / 2, j - m / 2])

    for shift in grid:
        shift_pos(indata, source, shift[0] * grid_offset, shift[1] * grid_offset, 8, 9)

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
        rungridimagr(split_data, source, 10, cellsize, imsize, -1, uvwtfn, robust, beam)
        split_data.zap()

        restore_su(indata, logfile)
        check_sncl(indata, 4, 8, logfile)


def findcal(indata, calsource):
    if calsource == '':
        n = 0
        for source in indata.sources:
            if source[0]=='G':
                calsource=source
                n=n+1
        if n>1:
            print ('More than one Maser source! Using '+calsource )

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
                spectfile = 'PWD:' + cvelsource[0] + '.' + linename + '.spectrum.txt'
                filename = cvelsource[0] + '.' + linename + '.POSSM.ps'
            else:
                spectfile = ''
                filename = cvelsource[0] + '.' + linename + '.POSSM_CH' + str(bchan) + '-' + str(echan) + '.ps'

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
def run_ma_sad(inimg,indata,cut,dyna):
    if inimg.exists():
        inimg.clrstat()
        num_ch = inimg.header.naxis[3-1]
        srcname = inimg.name
        obs=inimg.header['observer'];
        date_obs=inimg.header['date_obs']
        (linename,restfreq) = get_line_name(indata)
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

        sad_file = srcname+'_'+linename+'_'+obs+'_'+ \
                   date_obs+'_CH'+bch_str+'-'+ech_str+'_sad.txt'
        if os.path.exists(sad_file):
            os.popen('rm '+sad_file)
        if os.path.exists('sad.txt'):
            os.popen('rm sad.txt')

        sad           =  AIPSTask('SAD')
        sad.indata    = inimg
        sad.doresid   = -1
        sad.ngauss    = 3
        #--- for weak source, we may need to increase gain
        sad.gain      = 0.3
        sad.sort      = 'S'
        sad.docrt     = -4
        sad.fitout    = 'PWD:'+'sad.txt'
        mpeak=[]
        mrms=[]
        for i in range(1,num_ch+1):
            (peak, rms) = runimean(inimg,[0,0,i],[0,0,i])
            mpeak.append(peak)
            mrms.append(rms)

            c1 = peak*0.5
            c3 = max(rms*cut,peak*dyna)
            c2 = (c1 + c3)*0.5

            d1 = c3
            d2 = c3
            d3 = 0
            #--- pixel (depended on the compactness)
            #--- cellsize = 0.1 mas, then 40 means 4 mas
            d4 = 40
            d5 = 40
            cparm=[c1,c2,c3]
            cparm.sort()
            cparm.reverse()
            sad.cparm[1:] = cparm
            sad.icut      = c3
            sad.dparm[1:] = [d1,d2,d3,d4,d5]
            sad.blc[3]    = i
            sad.trc[3]    = i
            if peak>rms*cut:
                sad()

        cmd='cp sad.txt '+sad_file
        os.popen(cmd)
        mprint ('Channel:   Peak     rms      SNR',logfile)
        mprint ('            (Jy)   (Jy)',logfile)
        mprint ('---------------------------------',logfile)
        for i in range(len(mpeak)):
            mprint(('%3d     %7.4f %7.4f %8.4f' % (i+bchan-1,
                                                   mpeak[i], mrms[i], mpeak[i]/mrms[i])),logfile)
    else:
        print 'Image does not exist, please check it.'
        exit()
