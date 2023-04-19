#!/usr/bin/env python
# from get_utils import get_ant
# from select_utils import *
import os
import logging
import argparse
from config import AIPS_VERSION, AIPS_NUMBER, INTER_FLAG, DEF_DISKS
from utils import *
from make_utils import *
from run_tasks import *
from get_utils import *
from check_utils import *
from config import *
from AIPS import AIPS, AIPSDisk
from AIPSTask import AIPSTask, AIPSList
from AIPSData import AIPSUVData, AIPSImage
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData
import AIPSTV
import AIPS
##############################################################################
# Plot results from geofit
#


def possmplot(uvdata, sources='', timer=[0, 0, 0, 0, 0, 0, 0, 0], gainuse=0, flagver=0, stokes='HALF', nplot=1, bpv=0, ant_use=[0], cr=1):
    uvdata.zap_table('AIPS PL', -1)
    possm = AIPSTask('possm')
    possm.default()
    possm.indata = uvdata
    if (type(sources) == type('string')):
        possm.sources[1] = sources
    else:
        possm.sources[1:] = sources
    if (timer != None):
        if (timer[0] == None):
            possm.timerange = timer
        else:
            possm.timerang[1:] = timer
    possm.stokes = stokes
    possm.nplot = nplot
    # if cr == 0:
    # possm.nplot=0
    if (gainuse >= 0):
        possm.docalib = 1
        possm.gainuse = gainuse
    possm.flagv = flagver
    if cr == 1:  # cross-correlation
        possm.aparm[1:] = [0, 1, 0, 0, -180, 180, 0, 0, 1, 0]
    elif cr == 0:  # total power
        possm.aparm[1:] = [0, 0, 0, 0, 0, 0, 0, 1, 0]
    possm.bchan = 0
    possm.echan = 0
    possm.dotv = -1
    if (bpv > 0):
        possm.doband = 1
        possm.bpver = bpv
    if (ant_use != 0):
        possm.antennas[1:] = ant_use
    possm.baseline = [None, 0]
    textname = outname[0]+'-'+possm.sources[1]+'.rfichk'+str(nplot)
    possm.outtext = 'PWD:' + textname
    # possm.input()
    #print ant_use
    if (ant_use != [0]):
        ants = ant_use
    elif (ant_use == [0]):
        ants = get_ant(uvdata)
    if cr == 1:
        for i in ants:
            possm.antennas[1:] = [i, 0]
            possm.go()
    else:
        possm.go()
    lwpla = AIPSTask('lwpla')
    lwpla.indata = uvdata
    # lwpla.outfile = 'PWD:'+outname[0]+'-'+sources[0]+'-cl'+str(gainuse)+'-bp'+str(bpv)+'.possm'
    if sources == '':
        sources = ['']
    filename = outname[0]+'-'+possm.sources[1]+'-cl' + \
        str(gainuse)+'-bp'+str(bpv)+'-'+str(cr)+'.possm'+str(nplot)
    lwpla.outfile = 'PWD:'+filename
    lwpla.plver = 1
    lwpla.inver = 100
    if os.path.exists(filename):
        os.popen('rm '+filename)
        lwpla.go()
    if (os.path.exists(filename) == True):
        os.popen(r'mv '+filename+' '+outname[0]+'/')
    if (os.path.exists(textname) == True):
        os.popen(r'mv '+textname+' '+outname[0]+'/')

#################################################################################


def plt_sn_cl(indata, snchk, clchk, source_chk, cl_trange, bpv):
    if bpv == 0:
        doband = -1
    else:
        doband = 1
    # runsnplt(data_i,inver=snchk,inex='SN',sources=source_chk,optype='DELA',nplot=4,timer=[])
    # runsnplt(data_i,inver=snchk,inex='SN',sources=source_chk,optype='RATE',nplot=4,timer=[])
    possmplot(data_i, sources=source_chk, timer=chk_trange, gainuse=clchk,
              flagver=flagver, stokes='HALF', nplot=9, bpv=bpv, ant_use=[0], cr=1)


def runpossm(indata, calsource='', ant_use=[0], doband=-1, bpver=1, bchan=1, echan=0, gainuse=1, flagver=0, bpv=0,
             stokes='HALF', nplot=9):
    indata.zap_table('PL', -1)

    # calsource=check_calsource(indata, calsource)

    if bchan == echan and echan != 0:
        print 'Only one channel selected.'
    elif bchan > echan:
        print 'bchan > echan'
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
        lwpla.outfile = 'PWD:' + \
            outname[0] + '-' + [calsource] + '-cl' + \
            str(gainuse) + '-bp' + str(bpv) + '.possm'
        lwpla()

        indata.zap_table('PL', -1)
        os.popen('gv possm.ps')
        # os.popen('rm possm.ps')
##############################################################################
#


def run_snplt(indata, inter_flag):

    indata.zap_table('PL', -1)
    n_ant = len(get_ant(indata))
    snplt = AIPSTask('SNPLT')
    snplt.indata = indata
    snplt.stokes = 'RR'
    snplt.inver = 4
    snplt.inext = 'SN'
    snplt.optype = 'PHAS'
    snplt.nplots = n_ant
    snplt.bif = 1
    snplt.eif = 1
    snplt.dotv = -1
    snplt()

    name = indata.name+'_sn4.ps'

    if os.path.exists(name):
        os.popen('rm '+name)

    lwpla = AIPSTask('LWPLA')
    lwpla.indata = indata
    lwpla.inver = 0
    lwpla.outfile = 'PWD:'+name
    lwpla()

    if inter_flag == 1:
        tv = AIPSTV.AIPSTV()
    if tv.exists() == False:
        tv.start()
    if tv.exists():
        tv.clear()

    if AIPSTV.AIPSTV().exists():
        snplt.dotv = 1
        snplt()
    else:
        os.popen('gv '+name)

    indata.zap_table('PL', -1)


def runsnplt(indata, inver=1, inex='cl', sources='', optype='phas', nplot=4, timer=[]):
    indata.zap_table('PL', -1)
    snplt = AIPSTask('snplt')
    snplt.default()
    snplt.indata = indata
    snplt.dotv = -1
    snplt.nplot = nplot
    snplt.inex = inex
    snplt.inver = inver
    snplt.optype = optype
    snplt.do3col = 2
    if (type(sources) == type('string')):
        snplt.sources[1] = sources
    else:
        snplt.sources[1:] = sources
    if (timer != None):
        snplt.timerang[1:] = timer
    snplt.go()
    lwpla = AIPSTask('lwpla')
    lwpla.indata = indata
    if sources == '':
        lwpla.outfile = 'PWD:'+outname[0]+'-'+inex+str(inver)+'-'+optype+'.snplt'
        filename = outname[0]+'-'+inex+str(inver)+'-'+optype+'.snplt'
    else:
        lwpla.outfile = 'PWD:'+outname[0]+'-'+inex + \
        str(inver)+'-'+optype+'-'+sources[0]+'.snplt'
        filename = outname[0]+'-'+inex + \
        str(inver)+'-'+optype+'-'+sources[0]+'.snplt'
    lwpla.plver = 1
    lwpla.inver = 200
    if os.path.exists(filename):
        os.popen('rm '+filename)
    lwpla.go()
    if (os.path.exists(filename) == True):
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
    lwpla.outfile = 'PWD:' + outname[0] + '-' + \
        inext + str(inver) + '-' + optype + '.snplt'
    lwpla()
    f.writelines('<A HREF="plotfiles/' + name +
                 '"><img SRC="plotfiles/' + name2 + '" width=500></A>\n')
    os.popen(r'convert ' + name + ' ' + name2)
    os.popen(r'mv ' + name + ' plotfiles/')
    os.popen(r'mv ' + name2 + ' plotfiles/')

    f.writelines('<br><hr>\n')
    f.close()
    indata.zap_table('PL', -1)


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
        print 'Target frequency unknonw. Using 6.67 GHz.'
    f_tar = 6.67e9

    f = open('./geoblock/diff_files.inp', 'w')
    f.writelines(namma + '_low.dat		   ' +
                 '		  ! Low frequency data\n')
    f.writelines(namma + '_high.dat		   ' +
                 '		 ! High frequency data\n')
    f.writelines(str(f_low / 1e9) + '		  ' +
                 '			       ! Low frequency\n')
    f.writelines(str(f_high / 1e9) + '		  ' +
                 '			       ! High frequency\n')
    f.writelines(str(f_tar / 1e9) + '		  ' +
                 '			     ! Target frequency\n')
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


'''
def plot_baseline(indata, ant, inter_flag, ptype, doplot_flag, logfile):
    baselines = []
    str_baselines = []
    str_baselines2 = []
    data = []
    start = 100
    end = 0

    ant_str = get_ant(indata)

    if ant < 10:
    str_ant = '0' + str(ant)
    else:
    str_ant = str(ant)

    for ant2 in ant_str:
    if ant2 < 10:
        str_ant2 = '0' + str(ant2)
    else:
        str_ant2 = str(ant2)
    if ant2 > ant:
        bl = str_ant + str_ant2
        str_bl = str(ant) + '-' + str(ant2)
        str_bl2 = ant_str[ant] + '-' + ant_str[ant2]
    else:
        bl = str_ant2 + str_ant
        str_bl = str(ant2) + '-' + str(ant)
        str_bl2 = ant_str[ant2] + '-' + ant_str[ant]

    if ptype == 'A':
        file = './geoblock/tropos/fit_geodetic_bl' + bl + '.dat'
    elif ptype == 'I':
        file = './geoblock/ionos/fit_geodetic_bl' + bl + '.dat'
    if os.path.exists(file):
        f = open(file)
        content = f.read()
        if len(content) > 99:
        newdata = loadtxt(file, usecols=(0, 1, 2, 3, 4, 5, 6), comments='!')
        data.append(newdata)
        baselines.append(ant2)
        str_baselines.append(str_bl)
        str_baselines2.append(str_bl2)

    num_baselines = len(baselines)

    f1 = figure()

    if ptype == 'A':
    toptext = indata.header['observer'] + ' observed on ' + indata.header['date_obs'] + ' at ' + str(
        round(get_center_freq(indata) / 1e9, 2)) + ' GHz'
    elif ptype == 'I':
    toptext = indata.header['observer'] + ' observed on ' + indata.header['date_obs'] + ' for target frequency'
    figtext(0.25, 0.97, toptext)

    times2 = []
    block_times = []
    for tmp in data:
    for tmp2 in tmp:
        times2.append(tmp2[0])
    times2.sort()
    start = min(times2)
    end = max(times2)

    n = 1
    block_times.append([min(times2), 0])
    for i in range(1, len(times2)):
    if times2[i] - times2[i - 1] > 1:
        block_times[n - 1][1] = times2[i - 1]
        block_times.append([times2[i], 0])
        n += 1
    block_times[n - 1][1] = max(times2)
    n_blocks = len(block_times)

    size = 3
    print
    'Baseline      rms_delay  rms_rate      data/block'
    print
    '	       [nsec]     [mHz]'

    if len(baselines) > 20:
    print
    'More than 20 antennas, plotting only 15.'
    b = int(round(len(baselines) / 2.))
    num_baselines = b
    num_baselines2 = len(baselines) - b
    oneplot = False
    else:
    oneplot = True
    b = len(baselines)

    n = 0
    m = 0
    for i in baselines[0:b]:
    n += 1
    m += 1
    make_baseline_plot2(num_baselines, data, n, m, start, end, str_baselines, str_baselines2, n_blocks, block_times,
                f1)

    draw()
    if ptype == 'A':
    savefig('delay-rate.ps')
    elif ptype == 'I':
    savefig('delay-rate-ionos.ps')

    if oneplot == False:
    m = 0
    f2 = figure()
    toptext = indata.header['observer'] + ' observed on ' + indata.header['date_obs'] + ' at ' + str(
        round(get_center_freq(indata) / 1e9, 2)) + ' GHz'
    figtext(0.25, 0.97, toptext)
    for i in baselines[b:]:
        n += 1
        m += 1
        make_baseline_plot2(num_baselines2, data, n, m, start, end, str_baselines, str_baselines2, n_blocks,
                block_times, f2)

    draw()
    if ptype == 'A':
        savefig('delay-rate2.ps')
    elif ptype == 'I':
        savefig('delay-rate2-ionos.ps')

    mprint('', logfile)
    mprint('Note: A small number of high delays or rates is usually no problem.', logfile)
    mprint('', logfile)

    if inter_flag == 1:
    if int(matplotlib.__version__[0]) == 0:
        if int(matplotlib.__version__[2:4]) < 99:
        print
        'Close figure to continue.'
        show()
        close()
        else:
        f1.show()
        raw_input('Press enter to close figure and continue. ')
        close()
    else:
        print
        'Close figure to continue.'
        show()
        close()


#############################################################################
#
def plotatmos(inter_flag, logfile):
    file = 'ATMOS.FITS'
    data = loadtxt(file, skiprows=1)

    ant = []
    data2 = []
    avg = []
    rms = []

    for i in range(int(max(data[:, 0]))):
    ant.append([])
    data2.append([])
    avg.append(-1)
    rms.append(-1)
    for row in data:
    if (row[0] in ant) == False:
        ant[int(row[0]) - 1] = int(row[0])
    time = row[1] * 24. + (row[2] + row[3] / 60. + row[4] / 3600.)
    data2[int(row[0]) - 1].append([int(row[0]), time, row[5], row[6], row[7], row[8]])

    max_ant = len(data2)
    num_ant = 0
    for i in ant:
    if i != []:
        num_ant += 1

    fig = figure(0)
    n = 0
    start = 100
    end = 0

    for entry in data2:
    n = n + 1
    if entry != []:
        ant_data = array(entry)
        if start > min(ant_data[:, 1]):
        start = min(ant_data[:, 1])
        if end < max(ant_data[:, 1]):
        end = max(ant_data[:, 1])
        sum = 0
        for i in range(len(ant_data)):
        sum = sum + ant_data[i][2]
        avg[n - 1] = (sum / len(ant_data))
        rms[n - 1] = (ant_data[:, 2].std())

    n = 0
    plot = 0
    span = 2
    mprint('', logfile)
    mprint('Plotting ATMOS.FITS file.', logfile)
    mprint('Antenna       rms [cm]', logfile)
    for entry in data2:
    n += 1
    if entry != []:
        plot += 1
        ant_data = array(entry)
        ax = fig.add_subplot(num_ant, 1, plot)
        line = ' %4d  %12.3f ' % (int(ant_data[0][0]), round(rms[n - 1], 3))

        if (max(ant_data[:, 2]) < avg[n - 1] + span) and (min(ant_data[:, 2]) > avg[n - 1] - span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'gx')
        ax.set_ylim(avg[n - 1] - span, avg[n - 1] + span)
        line2 = ''
        elif (max(ant_data[:, 2]) < avg[n - 1] + 2 * span) and (min(ant_data[:, 2]) > avg[n - 1] - 2 * span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'bx')
        ax.set_ylim(avg[n - 1] - 2 * span, avg[n - 1] + 2 * span)
        line2 = '  (variations > ' + str(int(span)) + ' cm from mean)'
        elif (max(ant_data[:, 2]) < avg[n - 1] + 3 * span) and (min(ant_data[:, 2]) > avg[n - 1] - 3 * span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'rx')
        ax.set_ylim(avg[n - 1] - 3 * span, avg[n - 1] + 3 * span)
        line2 = '  (variations > ' + str(int(2 * span)) + ' cm from mean)'
        else:
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'ro')
        ax.set_ylim(avg[n - 1] - 4 * span, avg[n - 1] + 4 * span)
        line2 = '  (variations > ' + str(int(3 * span)) + ' cm from mean)'
        ax.set_xlim(start - 1., end + 1.)
        yticks([int(avg[n - 1]) - 2 * span, int(avg[n - 1]), int(avg[n - 1]) + 2 * span])

        mprint(line + line2, logfile)

        ax.text(0.03, 0.60, str(int(ant_data[0][0])), transform=ax.transAxes)

        if n == 1:
        title('ATMOS.FITS zenith delays [cm]')
        if n < max_ant:
        ax.xaxis.set_major_locator(NullLocator())
        if n == max_ant:
        xlabel('UT [hours]')

    mprint('', logfile)
    mprint('Green *: variations < ' + str(int(span)) + ' cm from mean', logfile)
    mprint('Blue  x: variations between ' + str(int(span)) + ' and ' + str(int(2 * span)) + ' cm from mean', logfile)
    mprint('Red   x: variations between ' + str(int(2 * span)) + ' and ' + str(int(3 * span)) + ' cm from mean',
       logfile)
    mprint('Red   o: variations > ' + str(int(3 * span)) + ' cm from mean', logfile)
    mprint('', logfile)

    draw()
    savefig('atmos.ps')

    if inter_flag == 1:
    if int(matplotlib.__version__[0]) == 0:
        if int(matplotlib.__version__[2:4]) < 99:
        print
        'Close figure to continue.'
        show()
        close()
        cont = raw_input('Continue with current ATMOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
            sys.exit()
        close()
        else:
        fig.show()
        cont = raw_input('Continue with current ATMOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
            sys.exit()
        close()
    else:
        print
        'Close figure to continue.'
        show()
        close()
        cont = raw_input('Continue with current ATMOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
        sys.exit()
        close()


#############################################################################
#
def plotionos(inter_flag, logfile):
    file = 'IONOS.FITS'
    data = loadtxt(file, skiprows=1)

    ant = []
    data2 = []
    avg = []
    rms = []

    for i in range(int(max(data[:, 0]))):
    ant.append([])
    data2.append([])
    avg.append(-1)
    rms.append(-1)
    for row in data:
    if (row[0] in ant) == False:
        ant[int(row[0]) - 1] = int(row[0])
    time = row[1] * 24. + (row[2] + row[3] / 60. + row[4] / 3600.)
    data2[int(row[0]) - 1].append([int(row[0]), time, row[5], row[6], row[7], row[8]])

    max_ant = len(data2)
    num_ant = 0
    for i in ant:
    if i != []:
        num_ant += 1

    fig = figure(0)
    n = 0
    start = 100
    end = 0

    for entry in data2:
    n = n + 1
    if entry != []:
        ant_data = array(entry)
        if start > min(ant_data[:, 1]):
        start = min(ant_data[:, 1])
        if end < max(ant_data[:, 1]):
        end = max(ant_data[:, 1])
        sum = 0
        for i in range(len(ant_data)):
        sum = sum + ant_data[i][2]
        avg[n - 1] = (sum / len(ant_data))
        rms[n - 1] = (ant_data[:, 2].std())

    n = 0
    plot = 0
    span = 2
    mprint('', logfile)
    mprint('Plotting IONOS.FITS file.', logfile)
    mprint('Antenna       rms [cm]', logfile)
    for entry in data2:
    n += 1
    if entry != []:
        plot += 1
        ant_data = array(entry)
        ax = fig.add_subplot(num_ant, 1, plot)
        line = ' %4d  %12.3f ' % (int(ant_data[0][0]), round(rms[n - 1], 3))

        if (max(ant_data[:, 2]) < avg[n - 1] + span) and (min(ant_data[:, 2]) > avg[n - 1] - span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'gx')
        ax.set_ylim(avg[n - 1] - span, avg[n - 1] + span)
        line2 = ''
        elif (max(ant_data[:, 2]) < avg[n - 1] + 2 * span) and (min(ant_data[:, 2]) > avg[n - 1] - 2 * span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'bx')
        ax.set_ylim(avg[n - 1] - 2 * span, avg[n - 1] + 2 * span)
        line2 = '  (variations > ' + str(int(span)) + ' cm from mean)'
        elif (max(ant_data[:, 2]) < avg[n - 1] + 3 * span) and (min(ant_data[:, 2]) > avg[n - 1] - 3 * span):
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'rx')
        ax.set_ylim(avg[n - 1] - 3 * span, avg[n - 1] + 3 * span)
        line2 = '  (variations > ' + str(int(2 * span)) + ' cm from mean)'
        else:
        ax.plot(ant_data[:, 1], ant_data[:, 2], 'ro')
        ax.set_ylim(avg[n - 1] - 4 * span, avg[n - 1] + 4 * span)
        line2 = '  (variations > ' + str(int(3 * span)) + ' cm from mean)'
        ax.set_xlim(start - 1., end + 1.)
        yticks([int(avg[n - 1]) - 2 * span, int(avg[n - 1]), int(avg[n - 1]) + 2 * span])

        mprint(line + line2, logfile)

        ax.text(0.03, 0.60, str(int(ant_data[0][0])), transform=ax.transAxes)

        if n == 1:
        title('IONOS.FITS zenith delays [cm]')
        if n < max_ant:
        ax.xaxis.set_major_locator(NullLocator())
        if n == max_ant:
        xlabel('UT [hours]')

    mprint('', logfile)
    mprint('Green *: variations < ' + str(int(span)) + ' cm from mean', logfile)
    mprint('Blue  x: variations between ' + str(int(span)) + ' and ' + str(int(2 * span)) + ' cm from mean', logfile)
    mprint('Red   x: variations between ' + str(int(2 * span)) + ' and ' + str(int(3 * span)) + ' cm from mean',
       logfile)
    mprint('Red   o: variations > ' + str(int(3 * span)) + ' cm from mean', logfile)
    mprint('', logfile)

    draw()
    savefig('ionos.ps')

    if inter_flag == 1:
    if int(matplotlib.__version__[0]) == 0:
        if int(matplotlib.__version__[2:4]) < 99:
        print
        'Close figure to continue.'
        show()
        close()
        cont = raw_input('Continue with current IONOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
            sys.exit()
        close()
        else:
        fig.show()
        cont = raw_input('Continue with current IONOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
            sys.exit()
        close()
    else:
        print
        'Close figure to continue.'
        show()
        close()
        cont = raw_input('Continue with current IONOS.FITS file? (y/n) ')
        if cont == 'n' or cont == 'N':
        sys.exit()
        close()
def plot_spot_map(inimg,indata):
    srcname = inimg.name
    obs=inimg.header['observer']
    xsize=abs(inimg.header['naxis'][0]*inimg.header['cdelt'][0])*3600
    ysize=inimg.header['naxis'][1]*inimg.header['cdelt'][1]*3600
    date_obs=inimg.header['date_obs']
    (linename,restfreq) = get_line_name(indata)
    filename = srcname+'.'+linename+'.spotmap.txt'
    f=open(filename)
    content=f.readlines()
    f.close()
    x=[]
    y=[]
    z=[]
    f=[]
    f_max=0
    n_poi=0
    for entry in content:
    if entry[0]=='!':
        pass
    else:
        n_poi+=1
        x_off = float(entry.split()[3])
        y_off = float(entry.split()[5])
        if abs(x_off)<0.48*xsize and abs(y_off)<0.48*ysize:
        x.append(x_off)
        y.append(y_off)
        z.append(float(entry.split()[1]))
        flux=float(entry.split()[2])
        f.append(flux**0.5)
        if float(entry.split()[2])>f_max:
            f_max=float(entry.split()[2])
    min_x=min(x)
    max_x=max(x)
    dx=max_x-min_x
    min_y=min(y)
    max_y=max(y)
    size=max(max_y-min_y,max_x-min_x,0.2)/2
    x_cent = (max_x+min_x)/2
    y_cent = (max_y+min_y)/2
    dy=max_y-min_y
    f2=array(f)
    scale = 300/max(f2)
    f1=figure()

    ra,dec= deg_to_radec([inimg.header['crval'][0],inimg.header['crval'][1]])
    title(srcname+' '+linename+' on '+date_obs+'\n (0,0)='+ra+','+
      dec+' (J2000)')
    ax=axes()
    s=ax.scatter(x,y,c=z,s=f2*scale,marker='o',edgecolors='')
    ax.scatter(x_cent+1.05*size,y_cent-1.15*size,c='0.8',s=max(f2)*scale)
    cb = plt.colorbar(s)
    cb.set_label('v$_{LSR}$ [km s$^{-1}$]')
    xlabel('East Offset [arcseconds]')
    ylabel('North Offset [arcseconds]')
    ax.set_xlim(x_cent+1.2*size,x_cent-1.2*size)
    ax.set_ylim(y_cent-1.3*size,y_cent+1.1*size)
    xy=(x_cent+0.93*size,y_cent-1.17*size)
    ax.annotate('= '+str(round(f_max,1))+
        ' Jy bm$^{-1}$', xy, xytext=None, xycoords='data',
        textcoords='data', arrowprops=None,
        bbox=dict(boxstyle="round", fc="0.8"),)
    draw()
    imname = srcname+'.'+linename+'.spotmap.ps'
    #    show()
    savefig(imname)
    os.popen('ps2pdf '+imname)
'''
