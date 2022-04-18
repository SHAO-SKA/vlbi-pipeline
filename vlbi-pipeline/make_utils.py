#!/usr/bin/env python

##############################################################################
# Make control_file.inp
#
def make_control_file(indata, refant, max_ant):
    (year, month, day) = get_observation_year_month_day(indata)
    f = open('./geoblock/control_file.inp', 'w')
    f.writelines('    1.0000                          ' +
                 '             ! data format (0=old; 1=new)\n' +
                 '   30.0000                              ! number interations\n' +
                 '    0.5000                              ! loop gain\n' +
                 '    0.0000                              ! debug print out level\n')

    if month < 10:
        s_month = '0' + str(month)
    else:
        s_month = str(month)
    if day < 10:
        s_day = '0' + str(day)
    else:
        s_day = str(day)

    f.writelines(str(year) + ' ' + s_month + ' ' + s_day +
                 '                              ! yyyy mm dd\n')
    frq = get_center_freq(indata) / 1e9
    f.writelines(str(frq) + 'd9                              ! obs freq (Hz)\n')
    f.writelines('    3.0        0.003        1.0         ' +
                 '! delay err, rate err, re-weight flag\n')
    f.writelines('    0.0                 ' +
                 '               ! Reference UT (hhmmss) for clock\n')
    bt = check_geo(indata)
    for i in range(len(bt) - 1):
        f.writelines('    ' + str(bt[i]) + '       ' + str(bt[i + 1]) + '              ' +
                     '       ! UT time range for block ' + str(i + 1) + '\n')
    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            f.writelines('    0.00       0.00              ' +
                         '       ! UT time range for block ' + str(i + 1) + '\n')

    ant = get_ant(indata)
    nan = len(ant)

    co = 1

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' C(cm)\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 0 and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' Rcm/h\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 1 and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' Ac/h2\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')

    for i in range(len(bt) - 1):
        for j in range(max_ant):
            if j + 1 in ant:
                if j + 1 in ant:
                    f.writelines('    0.0        1.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
                else:
                    f.writelines('    0.0        0.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
            else:
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')

    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            for j in range(max_ant):
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
    f.close()


##############################################################################
# Make control_file.inp
#
def make_control_file_sx(indata, pr_data, refant, max_ant):
    (year, month, day) = get_observation_year_month_day(indata)
    f = open('./geoblock/control_file_tropos.inp', 'w')
    f.writelines('    1.0000                          ' +
                 '             ! data format (0=old; 1=new)\n' +
                 '   30.0000                              ! number interations\n' +
                 '    0.5000                              ! loop gain\n' +
                 '    0.0000                              ! debug print out level\n')

    if month < 10:
        s_month = '0' + str(month)
    else:
        s_month = str(month)
    if day < 10:
        s_day = '0' + str(day)
    else:
        s_day = str(day)

    f.writelines(str(year) + ' ' + s_month + ' ' + s_day +
                 '                              ! yyyy mm dd\n')
    frq = get_center_freq(indata) / 1e9
    f.writelines(str(frq) + 'd9                              ! obs freq (Hz)\n')
    f.writelines('    3.0        0.003        1.0         ' +
                 '! delay err, rate err, re-weight flag\n')
    f.writelines('    0.0                 ' +
                 '               ! Reference UT (hhmmss) for clock\n')
    bt = check_geo(indata)
    for i in range(len(bt) - 1):
        f.writelines('    ' + str(bt[i]) + '       ' + str(bt[i + 1]) + '              ' +
                     '       ! UT time range for block ' + str(i + 1) + '\n')
    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            f.writelines('    0.00       0.00              ' +
                         '       ! UT time range for block ' + str(i + 1) + '\n')

    ant = get_ant(indata)
    nan = len(ant)

    co = 1

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' C(cm)\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 0 and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' Rcm/h\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 1 and max_ant < 30):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' Ac/h2\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')

    for i in range(len(bt) - 1):
        for j in range(max_ant):
            if j + 1 in ant:
                if j + 1 in ant:
                    f.writelines('    0.0        1.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
                else:
                    f.writelines('    0.0        0.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
            else:
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')

    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            for j in range(max_ant):
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
    f.close()

    f = open('./geoblock/control_file_ionos.inp', 'w')
    f.writelines('    1.0000                          ' +
                 '             ! data format (0=old; 1=new)\n' +
                 '   50.0000                              ! number interations\n' +
                 '    0.5000                              ! loop gain\n' +
                 '    0.0000                              ! debug print out level\n')

    if month < 10:
        s_month = '0' + str(month)
    else:
        s_month = str(month)
    if day < 10:
        s_day = '0' + str(day)
    else:
        s_day = str(day)

    f.writelines(str(year) + ' ' + s_month + ' ' + s_day +
                 '                              ! yyyy mm dd\n')
    frq = get_center_freq(pr_data) / 1e9
    f.writelines(str(frq) + 'd9                              ! obs freq (Hz)\n')
    f.writelines('    2.0        0.999        1.0         ' +
                 '! delay err, rate err, re-weight flag\n')
    f.writelines('    0.0                 ' +
                 '               ! Reference UT (hhmmss) for clock\n')
    bt = check_geo(indata)
    for i in range(len(bt) - 1):
        f.writelines('    ' + str(bt[i]) + '       ' + str(bt[i + 1]) + '              ' +
                     '       ! UT time range for block ' + str(i + 1) + '\n')
    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            f.writelines('    0.00       0.00              ' +
                         '       ! UT time range for block ' + str(i + 1) + '\n')

    ant = get_ant(indata)
    nan = len(ant)

    co = 1

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant):
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' C(cm)\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 0):
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Rcm/h\n')

    for i in range(max_ant):
        if i + 1 in ant:
            if (i + 1 in ant and i + 1 != refant and co > 1):
                f.writelines('    0.0        1.0                      ! A' + str(i + 1) + ' Ac/h2\n')
            else:
                f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')
        else:
            f.writelines('    0.0        0.0                      ! A' + str(i + 1) + ' Ac/h2\n')

    for i in range(len(bt) - 1):
        for j in range(max_ant):
            if j + 1 in ant:
                if j + 1 in ant:
                    f.writelines('    0.0        1.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
                else:
                    f.writelines('    0.0        0.0                      ' +
                                 '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
            else:
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')

    if len(bt) < 6:
        for i in range(len(bt) - 1, 5):
            for j in range(max_ant):
                f.writelines('    0.0        0.0                      ' +
                             '! A' + str(j + 1) + ' B' + str(i + 1) + ' cm\n')
    f.close()


##############################################################################
# Make station_file.inp
#

def make_station_file(indata):
    ant = get_ant(indata)

    f = open('./geoblock/station_file.inp', 'w')
    for i in ant:
        if i == min(ant):
            f.writelines(str(ant[i]) + ' ' + str(i) + '   ! station_file.inp for '
                         + indata.header.observer + ' on ' + indata.header.date_obs + '\n')
        else:
            if 'Y' in ant[i]:
                pass
            else:
                f.writelines(str(ant[i]) + ' ' + str(i) + '\n')
    f.close()


##############################################################################
# Make calibrator_file.inp
#

def make_calibrator_file(indata):
    (year, month, day) = get_observation_year_month_day(indata)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    f = open('./geoblock/calibrator_file.inp', 'w')
    f.writelines(namma + '_RATE_MDEL.DAT                   ' +
                 '                   ! calibrator data file name\n')
    f.writelines(namma + '_SU_TABLE.PRTAB                  ' +
                 '                   ! SU table file name\n')
    f.close()


##############################################################################
# Make calibrator_file.inp
#

def make_calibrator_file_sx(indata):
    (year, month, day) = get_observation_year_month_day(indata)
    monthlist = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    if day < 10:
        strday = '0' + str(day)
    else:
        strday = str(day)

    namma = str(year) + monthlist[int(month) - 1] + strday

    f = open('./geoblock/calibrator_file_tropos.inp', 'w')
    f.writelines(namma + '-tropos.dat                     ' +
                 '                   ! calibrator data file name\n')
    f.writelines(namma + '_SU_TABLE.PRTAB                  ' +
                 '                   ! SU table file name\n')
    f.close()

    f = open('./geoblock/calibrator_file_ionos.inp', 'w')
    f.writelines(namma + '-ionos.dat                      ' +
                 '                   ! calibrator data file name\n')
    f.writelines(namma + '_SU_TABLE.PRTAB                  ' +
                 '                   ! SU table file name\n')
    f.close()


##############################################################################
# Plot results from geofit
#
def make_baseline_plot(num_baselines, data, n, m, start, end, str_baselines, str_baselines2, n_blocks, block_times, f1):
    size = 3
    ax = f1.add_subplot(num_baselines, 2, 2 * m - 1)
    high_delay = max(max(data[n - 1][:, 3]), 1)
    low_delay = min(min(data[n - 1][:, 3]), -1)
    if max(data[n - 1][:, 3]) < 0.2:
        high_delay = max(max(data[n - 1][:, 3]) * 1.2, 0.1)
        low_delay = min(min(data[n - 1][:, 3]) * 1.2, -0.1)
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 1], '.b', ms=size)  # Delay
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 2], '.g', ms=size)  # Model
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 3], '.r', ms=size)  # Resid
    trang = end - start
    over = trang / 10
    ax.plot([start - over, end + over], [0, 0], 'k:')
    ax.set_xlim(start - over, end + over)
    # +++ ZB
    if doplot_flag == 1:
        # ax.set_ylim(low_delay*1.1,high_delay*1.1)
        ax.set_ylim(-1, 1)
    else:
        # ax.set_ylim(-1,1)
        ax.set_ylim(-1, 1)
    # --- ZB
    if m == 1:
        title('Multiband delay [nsec]')
    if n < num_baselines:
        ax.xaxis.set_major_locator(NullLocator())
    if n == num_baselines:
        xlabel('UT [hours]')
    ax.text(0.2, 0.65, str_baselines2[n - 1], transform=ax.transAxes)

    ax = f1.add_subplot(num_baselines, 2, 2 * m)
    high_rate = max(max(data[n - 1][:, 6]), 10)
    low_rate = min(min(data[n - 1][:, 6]), -10)
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 4], '.b', ms=size)
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 5], '.g', ms=size)
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 6], '.r', ms=size)
    ax.plot([start - over, end + over], [0, 0], 'k:')
    ax.set_xlim(start - over, end + over)
    if doplot_flag == 1:
        ax.set_ylim(low_rate * 1.1, high_rate * 1.1)
    else:
        ax.set_ylim(-3, 3)
    if m == 1:
        title('Rate [mHz]')
    if n < num_baselines:
        ax.xaxis.set_major_locator(NullLocator())
    if n == num_baselines:
        xlabel('UT [hours]')
    ax.text(0.2, 0.65, str_baselines2[n - 1], transform=ax.transAxes)

    if max(data[n - 1][:, 3]) > 2 or min(data[n - 1][:, 3]) < -2:
        delays = data[n - 1][:, 3]
        rms = delays.std()
        bad_delays = []
        for entry in delays:
            if entry > 3 * rms or entry < -3 * rms or entry < -2 or entry > 2:
                bad_delays.append(entry)
        if float(len(bad_delays)) / float(len(delays)) > 0.3:
            warning1 = '\033[7;33;40m' + str(len(bad_delays)) + '/' + str(len(delays)) + ' high delays\033[0m'
        else:
            warning1 = '\033[0m' + str(len(bad_delays)) + '/' + str(len(delays)) + ' high delays\033[0m'
    else:
        warning1 = ''

    if max(data[n - 1][:, 6]) > 10 or min(data[n - 1][:, 6]) < -10:
        rates = data[n - 1][:, 6]
        rms = rates.std()
        bad_rates = []
        for entry in rates:
            if entry > 3 * rms or entry < -3 * rms or entry < -10 or entry > 10:
                bad_rates.append(entry)
        if float(len(bad_rates)) / float(len(rates)) > 0.3:
            warning2 = '\033[7;33;40m' + str(len(bad_rates)) + '/' + str(len(rates)) + ' high rates\033[0m'
        else:
            warning2 = str(len(bad_rates)) + '/' + str(len(rates)) + ' high rates'
    else:
        warning2 = ''

    times = data[n - 1][:, 0]
    j = 0

    blocks = []
    for i in range(n_blocks):
        blocks.append(0)
        for tmp in times:
            if block_times[i][1] >= tmp >= block_times[i][0]:
                blocks[i] += 1

    if 1 in blocks or 2 in blocks or 3 in blocks:
        warning0 = '\033[7;33;40m<3 scans\033[0m'
    else:
        warning0 = ''

    str_blocks = ' '
    for k in range(n_blocks):
        if int(blocks[k]) < 10:
            str_blocks = str_blocks + '   ' + str(int(blocks[k]))
        else:
            str_blocks = str_blocks + '  ' + str(int(blocks[k]))

    mprint('%5s(%5s)    %4.2f      %4.2f    %18s %8s %17s %10s' % (
        str_baselines2[n - 1], str_baselines[n - 1], round(data[n - 1][:, 2].std(), 3), round(data[n - 1][:, 6].std(), 2),
        str_blocks, warning0, warning1, warning2), logfile)
    draw()


##############################################################################
# Plot results from geofit
#
def make_baseline_plot2(num_baselines, data, n, m, start, end, str_baselines, str_baselines2, n_blocks, block_times,
                        f1):
    size = 3
    ax = f1.add_subplot(num_baselines, 1, m)
    high_delay = max(max(data[n - 1][:, 3]), 1)
    low_delay = min(min(data[n - 1][:, 3]), -1)
    if max(data[n - 1][:, 3]) < 0.2:
        high_delay = max(max(data[n - 1][:, 3]) * 1.2, 0.1)
        low_delay = min(min(data[n - 1][:, 3]) * 1.2, -0.1)
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 1], '.b', ms=size)  # Delay
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 2], '.g', ms=size)  # Model
    ax.plot(data[n - 1][:, 0], data[n - 1][:, 3], '.r', ms=size)  # Resid
    trang = end - start
    over = trang / 8
    ax.plot([start - over, end + over], [0, 0], 'k:')
    ax.set_xlim(start - over, end + over)
    if doplot_flag == 1:
        # +++ ZB
        # ax.set_ylim(-2.1,2.1)
        ax.set_ylim(-1.1, 1.1)
    #            ax.set_ylim(min([low_delay*1.1,-1.1]),max([high_delay*1.1,1.1]))
    # --- ZB
    else:
        ax.set_ylim(-1, 1)
    if m == 1:
        title('Multiband delay [nsec]')
    if m < num_baselines:
        ax.xaxis.set_major_locator(NullLocator())
    if m == num_baselines:
        xlabel('UT [hours]')
    ax.text(0.01, 0.60, str_baselines2[n - 1], transform=ax.transAxes)

    if max(data[n - 1][:, 3]) > 2 or min(data[n - 1][:, 3]) < -2:
        delays = data[n - 1][:, 3]
        rms = delays.std()
        bad_delays = []
        for entry in delays:
            if entry > 3 * rms or entry < -3 * rms or entry < -2 or entry > 2:
                bad_delays.append(entry)
        if float(len(bad_delays)) / float(len(delays)) > 0.3:
            warning1 = '\033[7;33;40m' + str(len(bad_delays)) + '/' + str(len(delays)) + ' high delays\033[0m'
        else:
            warning1 = '\033[0m' + str(len(bad_delays)) + '/' + str(len(delays)) + ' high delays\033[0m'
    else:
        warning1 = ''

    if max(data[n - 1][:, 6]) > 10 or min(data[n - 1][:, 6]) < -10:
        rates = data[n - 1][:, 6]
        rms = rates.std()
        bad_rates = []
        for entry in rates:
            if entry > 3 * rms or entry < -3 * rms or entry < -10 or entry > 10:
                bad_rates.append(entry)
        if float(len(bad_rates)) / float(len(rates)) > 0.3:
            warning2 = '\033[7;33;40m' + str(len(bad_rates)) + '/' + str(len(rates)) + ' high rates\033[0m'
        else:
            warning2 = str(len(bad_rates)) + '/' + str(len(rates)) + ' high rates'
    else:
        warning2 = ''

    times = data[n - 1][:, 0]
    j = 0

    blocks = []
    for i in range(n_blocks):
        blocks.append(0)
        for tmp in times:
            if block_times[i][1] >= tmp >= block_times[i][0]:
                blocks[i] += 1

    if 1 in blocks or 2 in blocks or 3 in blocks:
        warning0 = '\033[7;33;40m<3 scans\033[0m'
    else:
        warning0 = ''

    str_blocks = ' '
    for k in range(n_blocks):
        if int(blocks[k]) < 10:
            str_blocks = str_blocks + '   ' + str(int(blocks[k]))
        else:
            str_blocks = str_blocks + '  ' + str(int(blocks[k]))

    mprint('%5s(%5s)    %4.2f      %4.2f    %18s %8s %17s %10s' % (
        str_baselines2[n - 1], str_baselines[n - 1], round(data[n - 1][:, 2].std(), 3), round(data[n - 1][:, 6].std(), 2),
        str_blocks, warning0, warning1, warning2), logfile)
    draw()


##############################################################################
#
def make_name_atmos(indata):
    ant = get_ant(indata)
    file = 'ATMOS.FITS'
    data = loadtxt(file, skiprows=1)
    data2 = []
    n = int(max(data[:, 0]))
    for j in range(1, n + 1):
        for entry in data:
            if entry[0] == j:
                data2.append(entry)

    f = open('ATMOS_NAME.FITS', 'w')
    f.writelines('   ' + str(len(data2)) + '\n')
    for i in data2:
        line1 = '%2s  %2d %2d %2d %4.1f' % (ant[i[0]], int(i[1]), int(i[2]), int(i[3]), i[4])
        line2 = ' %8.3f   %8.3f    %8.5f    %8.5f' % (i[5], i[6], i[7], i[8])
        f.writelines(line1 + line2 + '\n')

    f.close()


##############################################################################
#
def make_name_ionos(indata):
    ant = get_ant(indata)
    file = 'IONOS.FITS'
    data = loadtxt(file, skiprows=1)
    data2 = []
    n = int(max(data[:, 0]))
    for j in range(1, n + 1):
        for entry in data:
            if entry[0] == j:
                data2.append(entry)

    f = open('IONOS_NAME.FITS', 'w')
    f.writelines('   ' + str(len(data2)) + '\n')
    for i in data2:
        line1 = '%2s  %2d %2d %2d %4.1f' % (ant[i[0]], int(i[1]), int(i[2]), int(i[3]), i[4])
        line2 = ' %8.3f   %8.3f    %8.5f    %8.5f' % (i[5], i[6], i[7], i[8])
        f.writelines(line1 + line2 + '\n')

    f.close()


def make_check_RDBE(data, logfile, inter_flag, dtype):
    wdata = WAIPSUVData(data.name, 'UVAVG', data.disk, data.seq)
    nif = data.header['naxis'][3]

    sources = get_sources(data)
    su_table = data.table('AIPS SU', 0)
    an_table = data.table('AIPS AN', 0)

    times = []
    for visibility in wdata:
        there = False
        if visibility.time in times:
            pass
        else:
            if len(times) > 0:
                for time in times:
                    if visibility.time - time < 6.94e-4:
                        there = True
            else:
                pass

            if there:
                pass
            else:
                times.append(visibility.time)

    blocks = []
    for entry in times:
        if len(blocks) == 0:
            blocks.append(entry)
        else:
            new_block = True
            for time in blocks:
                if abs(entry - time) < 4.17e-2:
                    new_block = False
            if new_block:
                blocks.append(entry)

    antennas = []
    for ant in an_table:
        antennas.append(ant['nosta'])

    if len(antennas) < max(antennas):
        for i in range(1, max(antennas)):
            if i in antennas:
                pass
            else:
                antennas.append(i)

    antennas = sort(antennas)

    block_nr = 0
    block_data = []
    bad = 0
    flagline = []
    bt = check_geo(data)

    for block in blocks:
        block_nr += 1

        if dtype == 'GEO':
            mprint('#####################################', logfile)
            mprint('###### Checking geoblock Nr.:' + str(block_nr) + ' ######', logfile)
            mprint('#####################################', logfile)
        elif dtype == 'CONT':
            mprint('######################################', logfile)
            mprint('###### Checking contblock Nr.:' + str(block_nr) + ' ######', logfile)
            mprint('######################################', logfile)
        antdata = []
        for ant in antennas:
            if_data = []
            for IF in range(nif):
                if_data.append([])
            antdata.append(if_data)

        avgantdata = []
        for ant in antennas:
            if_data = []
            for IF in range(nif):
                if_data.append([])
            avgantdata.append(if_data)

        n = 0
        for visibility in wdata:
            if abs(block - visibility.time) < 4.17e-2:
                n += 1
                for IF in range(nif):
                    vis = visibility.visibility[IF][0][0]
                    amp = (sqrt(vis[0] ** 2 + vis[1] ** 2))
                    antdata[visibility.baseline[0] - 1][IF].append(amp)
                    antdata[visibility.baseline[1] - 1][IF].append(amp)

        for ant in antennas:
            for IF in range(nif):
                if len(antdata[ant - 1][IF]) > 0:
                    avg = average(antdata[ant - 1][IF])
                else:
                    avg = 0.0
                avgantdata[ant - 1][IF] = avg

        plot = 1
        an_table = data.table('AIPS AN', 0)
        for entry in antennas:
            myantdata = array(avgantdata[entry - 1])
            ymax = (1.3 * max(myantdata) + 0.000001)
            avg = average(myantdata) * 1000
            rms = std(myantdata) * 1000
            #            print get_antname(an_table,entry),average(myantdata)/min(myantdata)
            if min(myantdata) > 0 and average(myantdata) / min(myantdata) > 2:
                if 'MK' in get_antname(an_table, entry) or 'SC' in get_antname(an_table, entry):
                    if average(myantdata) / min(myantdata) > 2.2:
                        bad_IF = []
                        for IF in range(nif):
                            if average(myantdata) / myantdata[IF] > 2.2:
                                bad_IF.append(IF + 1)
                        mprint(
                            'Probable RDBE Error: ' + get_antname(an_table, entry).strip() + ', bad IFs:' + str(bad_IF),
                            logfile)
                        bad += 1
                else:
                    bad_IF = []
                    for IF in range(nif):
                        if average(myantdata) / myantdata[IF] > 2:
                            bad_IF.append(IF + 1)
                    if len(bad_IF) == 1 and 7 in bad_IF:
                        mprint(
                            'Probable IF 7 Error: ' + get_antname(an_table, entry).strip() + ', bad IFs:' + str(bad_IF),
                            logfile)
                    else:
                        mprint(
                            'Probable RDBE Error: ' + get_antname(an_table, entry).strip() + ', bad IFs:' + str(bad_IF),
                            logfile)
                        flagline.append([get_antname(an_table, entry).strip(), bt[block_nr - 1], bt[block_nr]])
                    bad += 1
            fig = figure(block_nr, figsize=(8, 12))
            ax = fig.add_subplot(len(antennas), 1, plot)
            # +++ ZB
            # ax.set_xlim(-0.8,nif-0.5)
            # ax.set_ylim(0.0, ymax*1000)
            # ax.text(0.03, 0.60, get_antname(an_table,entry), transform=ax.transAxes)
            # --- ZB

            if round(ymax * 900, 1) < 0.01:
                yticks([0, 0.1])
            else:
                yticks([0, round(ymax * 900, 1)])

            # +++ ZB
            # ax.plot(myantdata[:]*1000, 'bx')
            # ax.plot([0,nif-1],[avg,avg],'k-')
            ax.plot(range(1, nif + 1), myantdata[:] * 1000, 'bx')
            ax.plot([1, nif + 1], [avg, avg], 'k-')
            # --- ZB

            # +++ ZB
            # ax.set_xlim(-0.8,nif-0.5)
            ax.set_xlim(0.5, nif + 0.5)
            ax.set_ylim(0.0, ymax * 1000)
            ax.text(0.03, 0.60, get_antname(an_table, entry), transform=ax.transAxes)
            # --- ZB

            if entry == min(antennas):
                title('Aplitude in arbitrary units across the IFs\n Block:' + str(block_nr))
            if entry < max(antennas):
                ax.xaxis.set_major_locator(NullLocator())
            if entry == max(antennas):
                # +++ ZB
                # xlabel('No. IF - 1')
                xlabel('No. IF')
                # --- ZB
            plot += 1

        #        print 'test'
        draw()
        if dtype == 'GEO':
            savefig('RDBE_check_geoblock' + str(block_nr) + '.ps')
        elif dtype == 'CONT':
            savefig('RDBE_check_contblock' + str(block_nr) + '.ps')

        if inter_flag == 1:
            if int(matplotlib.__version__[0]) == 0:
                if int(matplotlib.__version__[2:4]) < 99:
                    print
                    'Close figure to continue.'
                    show()
                    close()
                else:
                    fig.show()
                    raw_input('Press enter to close figure and continue. ')
                    close()
            else:
                print
                'Close figure to continue.'
                show()
                close()

    mprint('########################################', logfile)
    mprint('#### ' + str(bad) + ' probable RDBE errors detected ###', logfile)
    mprint('########################################', logfile)

    date = get_observation_year_month_day(data)
    doy = get_day_of_year(date[0], date[1], date[2])

    if bad > 0:
        flagfile = data.name + '.flagfile'
        f = open(flagfile, 'w')
        for entry in flagline:
            d1, h1, m1, s1 = time_to_hhmmss(entry[1])
            d2, h2, m2, s2 = time_to_hhmmss(entry[2])
            f.writelines(
                'ANT_NAME=\'' + entry[0] + '\' TIMERANG=' + str(d1 + doy) + ',' + str(h1) + ',' + str(m1) + ',' + str(
                    s1) + ',' + str(d2 + doy) + ',' + str(h2) + ',' + str(m2) + ',' + str(
                    s2) + ' REASON=\'RDBE problem\'/\n')
        f.close()

        if inter_flag == 1:
            cont = raw_input('Apply flags? (y/n) ')
            if cont == 'y' or cont == 'Y':
                runuvflg(data, flagfile, logfile)
        else:
            runuvflg(data, flagfile, logfile)

    return len(blocks)

#    if data.exists():
#        print 'Yes'
#    else:
#        print 'No'
