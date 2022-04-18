#!/usr/bin/env python
from get_utils import get_ant
from .select_utils import *

##############################################################################
# Plot results from geofit
#
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
    '               [nsec]     [mHz]'

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
