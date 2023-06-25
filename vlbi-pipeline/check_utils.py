#!/usr/bin/env python

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
from get_utils import *
from logging_config import logger


    
def check_sx(indata):
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


def check_clh(indata):
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
def check_sncl(indata, sn, cl):
    if (indata.table_highver('AIPS CL') == cl and
            indata.table_highver('AIPS SN') == sn):
        logger.info('SN and CL tables ok. ')
        logger.info('Current top CL table:' + str(indata.table_highver('AIPS CL')))
        logger.info('Current top SN table:' + str(indata.table_highver('AIPS SN')))

    if indata.table_highver('AIPS CL') < cl:
        raise RuntimeError('Not enough CL tables')

    if indata.table_highver('AIPS CL') > cl:
        logger.warning('Deleting old CL tables. ')
        while indata.table_highver('AIPS CL') > cl:
            indata.zap_table('AIPS CL', 0)

    if indata.table_highver('AIPS SN') < sn:
        raise RuntimeError('Not enough SN tables')

    if indata.table_highver('AIPS SN') > sn:
        logger.warning('Deleting old SN tables. ')
        while indata.table_highver('AIPS SN') > sn:
            indata.zap_table('AIPS SN', 0)
##############################################################################
#


def check_sn_ver(indata):
    sn = indata.table('AIPS SN', 0)
    return len(sn[0])

##############################################################################
#

'''
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


def check_RDBE(indata, inter_flag, dtype):

    logger.info('################################################ ',)
    logger.info('### Checking geoblock data for RDBE errors ##### ',)
    logger.info('################################################')
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

    block_nr = make_check_RDBE(indata, inter_flag, dtype)

    data1.zap()
    data2.zap()
    return block_nr
##############################################################################
# check_cal

'''
def check_cal(indata, source, outdisk, imna):
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


def check_data(data, n, geo, cont, line):
    count = 0
    for i in range(len(data)):
        if data[i].exists():
            count = count+1
            data_info(data[i], i, geo, cont, line)
    if count == n:
        logger.info('Found %s data files on disk', str(count))
    else:
        logger.info(
            'Expected %s files, but found %s data files on disk ', str(n), str(count))


##############################################################################
#
def checkatmos(inter_flag):
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
        logger.info('Original ATMOS.FITS file has zero zenith delays.')
        logger.info('Making new ATMOS file.')
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
        logger.info('ATMOS.FITS file ok.')

    plotatmos(inter_flag)
