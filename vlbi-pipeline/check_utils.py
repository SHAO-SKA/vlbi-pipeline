#!/usr/bin/env python

from AIPSTask import AIPSTask
from plot_utils import *
#from run_tasks import runsnplt 
import logging

def runsnplt(indata,inver=1,inex='cl',sources='',optype='phas',nplot=4,outname='', timer=[]):
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
        lwpla.outfile = 'PWD:'+outname+'-'+inex+str(inver)+'-'+optype+'.snplt'
    else:
        lwpla.outfile = 'PWD:'+outname+'-'+inex+str(inver)+'-'+optype+'-'+sources[0]+'.snplt'
    filename=  outname+'-'+inex+str(inver)+'-'+optype+'.snplt'
    lwpla.plver = 1
    lwpla.inver = 200
    if os.path.exists(filename):
        os.popen('rm '+filename)
    lwpla.go()
    if (os.path.exists(filename)==True):
        os.popen(r'mv '+filename+' '+outname+'/')
def chk_sn_cl(indata,snchk,clchk,source_chk,cl_trange,bpv,flagver, outname):
    runsnplt(indata,inver=snchk,inex='SN',sources=source_chk,optype='DELA',nplot=4,outname = outname, timer=[])
    runsnplt(indata,inver=snchk,inex='SN',sources=source_chk,optype='RATE',nplot=4, outname = outname,timer=[])
    possmplot(indata,sources=source_chk,timer=cl_trange,gainuse=clchk,flagver=flagver,stokes='HALF',nplot=9,bpv=0,ant_use=[0],  outname = outname) 

def check_sx(indata, logfile):
    if indata.header.naxis[3] > 1:
        fq = indata.table('AIPS FQ', 0)
        fq_span = fq[0]['if_freq'][indata.header.naxis[3]-1] - \
            fq[0]['if_freq'][0]
        frq = (indata.header.crval[2]+0.5*fq_span)/1e9
        if 3 > indata.header.crval[2]/1e9 > 2 and fq_span > 1e9:
            return True
        return False
    else:
        return False


def check_clh(indata, logfile):
    if indata.header.naxis[3] > 1:
        fq = indata.table('AIPS FQ', 0)
        fq_span = fq[0]['if_freq'][indata.header.naxis[3]-1] - \
            fq[0]['if_freq'][0]
        frq = (indata.header.crval[2]+0.5*fq_span)/1e9
        if 8 > indata.header.crval[2]/1e9 > 4 and fq_span > 6e8:
            return True
        return False
    else:
        return False


def check_geo(indata):
    nx_table = indata.table('AIPS NX', 0)
    n_block = 1
    n = len(nx_table)
    b = []
    b.append(round(nx_table[0]['time']-0.01, 2))
    for i in range(1, n):
        if (nx_table[i]['time']-nx_table[i-1]['time']) > 0.02:
            n_block = n_block+1
            b.append(round(nx_table[i]['time']-0.01, 2))
    b.append(round(nx_table[n-1]['time']+0.01, 2))
    return b


##############################################################################
# Check table versions
#
def check_sncl(indata, sn, cl, logfile):
    if (indata.table_highver('AIPS CL') == cl and
            indata.table_highver('AIPS SN') == sn):
        logging.info('SN and CL tables ok. ')

    if indata.table_highver('AIPS CL') < cl:
        raise RuntimeError('Not enough CL tables')

    if indata.table_highver('AIPS CL') > cl:
        logging.warning('Deleting old CL tables. ')
        while indata.table_highver('AIPS CL') > cl:
            indata.zap_table('AIPS CL', 0)

    if indata.table_highver('AIPS SN') < sn:
        raise RuntimeError('Not enough SN tables')

    if indata.table_highver('AIPS SN') > sn:
        logging.warning('Deleting old SN tables. ')
        while indata.table_highver('AIPS SN') > sn:
            indata.zap_table('AIPS SN', 0)
##############################################################################
#


def check_sn_ver(indata):
    sn = indata.table('AIPS SN', 0)
    return len(sn[0])

##############################################################################
#


def check_calsource(indata, calsource):

    if isinstance(calsource, str):
        sour = raw_input('Using source '+calsource+'? (y/n) ')
    else:
        cals_str = ''
        for i in calsource:
            cals_str = cals_str+i+' '
        sour = raw_input('Using source '+cals_str+'? (y/n) ')

    if sour == 'n' or sour == 'N':
        print 'Searching for sources with data.'
        real_sources = get_real_sources(indata)
        print 'Available sources: '
        for i in range(len(real_sources)):
            print str(i+1)+': '+real_sources[i]

        calsource = raw_input('Which source? ')
        if (calsource in real_sources) == False:
            try:
                k = int(calsource)
                calsource = real_sources[k-1]
            except:
                print 'No such source.'
                sys.exit()
        else:
            print 'No such source.'
            sys.exit()

    return calsource


def check_RDBE(indata, logfile, inter_flag, dtype):

    logging.info('################################################ ',)
    logging.info('### Checking geoblock data for RDBE errors ##### ',)
    logging.info('################################################')
    avspc = AIPSTask('AVSPC')
    nchan = indata.header['naxis'][2]

    data1 = AIPSUVData(indata.name, 'AVSPC', indata.disk, 1)

    if data1.exists():
        data1.zap()

    avspc.indata = indata
    avspc.outdisk = indata.disk
    avspc.outclass = 'AVSPC'
    avspc.channel = nchan
    avspc.go()

    data2 = AIPSUVData(indata.name, 'UVAVG', indata.disk, 1)
    if data2.exists():
        data2.zap()

    uvavg = AIPSTask('UVAVG')
    uvavg.indata = AIPSUVData(indata.name, 'AVSPC', indata.disk, 1)
    uvavg.yinc = 300
    uvavg.outclass = 'UVAVG'
    uvavg.outdisk = indata.disk
    uvavg.go()

    block_nr = make_check_RDBE(indata, logfile, inter_flag, dtype)

    data1.zap()
    data2.zap()
    return block_nr
##############################################################################
# check_cal


def check_cal(indata, source, outdisk, logfile, imna):
    if imna == '':
        outname = source
    else:
        outname = source[:11-len(imna)]+'-'+imna

    ncal = 1
    while AIPSUVData(outname, 'CALIB', line_data.disk, ncal+1).exists():
        ncal += 1
    cal_data = AIPSUVData(outname, 'CALIB', line_data.disk, ncal)
    if cal_data.exists():
        return cal_data
    else:
        return indata


def check_data(data, n, geo, cont, line, logfile):
    count = 0
    for i in range(len(data)):
        if data[i].exists():
            count = count+1
            data_info(data[i], i, geo, cont, line, logfile)
    if count == n:
        logging.info('Found %s data files on disk', str(count))
    else:
        logging.info(
            'Expected %s files, but found %s data files on disk ', str(n), str(count))


##############################################################################
#
def checkatmos(inter_flag, logfile):
    file = 'ATMOS.FITS'
    data = loadtxt(file, skiprows=1)

    m = 0
    for i in data:
        if i[5] != 0:
            m = m + 1

    antennas = []
    for i in range(len(data)):
        tmp = []
        zero = []
        nonzero = []
        if data[i][5] == 0:
            antennas.append(data[i][0])
            time_i = data[i][1] + (data[i][2] + data[i]
                                   [3] / 60. + data[i][4] / 3600.) / 24.
            n = 0
            for j in range(len(data)):
                if data[j][0] == data[i][0]:
                    time = data[j][1] + (data[j][2] + data[j]
                                         [3] / 60. + data[j][4] / 3600.) / 24.
                    tmp.append([data[j][0], time, data[j][5]])
                    if data[j][5] == 0 or data[j][5] == 999:
                        zero.append(n)
                    else:
                        nonzero.append(n)
                    n = n + 1

            if tmp != [] and nonzero != []:
                for k in zero:
                    if k == 0 and time_i == tmp[k][1]:
                        data[i][5] = tmp[nonzero[0]][2]
                    elif k == n - 1 and time_i == tmp[k][1]:
                        data[i][5] = tmp[nonzero[len(nonzero) - 1]][2]
                    elif time_i == tmp[k][1]:
                        data[i][5] = 999

    n = 0
    for i in data:
        if i[5] != 999 and i[5] != 0:
            n = n + 1

    if m < len(data):
        logging.info('Original ATMOS.FITS file has zero zenith delays.')
        logging.info('Making new ATMOS file.')
        f = open('NEWATMOS.FITS', 'w')
        f.writelines('   ' + str(n) + '\n')
        for i in data:
            if i[5] != 999 and i[5] != 0:
                line1 = ' %2d  %2d %2d %2d %4.1f' % (
                    int(i[0]), int(i[1]), int(i[2]), int(i[3]), i[4])
                line2 = ' %8.3f   %8.3f    %8.5f    %8.5f' % (
                    i[5], i[6], i[7], i[8])
                f.writelines(line1 + line2 + '\n')
        f.close()

        os.popen('mv ATMOS.FITS ATMOS.FITS.orig')
        os.popen('mv NEWATMOS.FITS ATMOS.FITS')
    else:
        logging.info('ATMOS.FITS file ok.')

    plotatmos(inter_flag, logfile)
