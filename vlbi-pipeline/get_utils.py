#!/usr/bin/env python

import os
import time

def get_load_data(data):
    antennas = {}
    for row in data.table('AN', 0):
        antennas[row.nosta] = row.anname[0:2]
    return antennas

def get_ant(data):
    antennas = {}
    for row in data.table('AN', 0):
        antennas[row.nosta] = row.anname[0:2]
    return antennas
def get_timerange_tab(indata,table,i):
    sn_table = indata.table(table, 0)
    time1 = sn_table[i].time-0.5*sn_table[i].time_interval
    time2 = sn_table[i].time+0.5*sn_table[i].time_interval
    (day1,hour1,min1,sec1)=time_to_hhmmss(time1)
    (day2,hour2,min2,sec2)=time_to_hhmmss(time2)
    timerange = [day1, hour1, min1, sec1, day2, hour2, min2, sec2]
    return timerange


##############################################################################
# Get the day-of-year integer from the year/month/day
#
def get_day_of_year(year, month, day):
    day_of_year_list = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    doy = day_of_year_list[month - 1] + day
    if (month > 2):
        if ((year & 0x3) == 0):
            if ((year % 100 != 0) or (year % 400 == 0)):
                doy = doy + 1
    return doy


##############################################################################
# Get the day of year from the Year, month, day for the start of observations
#
def get_observation_year_month_day(aips_data):
    date_string = aips_data.header.date_obs
    date_list = date_string.split('-')
    year = int(date_list[0])
    month = int(date_list[1])
    day = int(date_list[2])
    return (year, month, day)


##############################################################################
# Get number of days
#
def get_num_days(indata):
    nx_table = indata.table('AIPS NX', 0)
    n = len(nx_table)
    num_days = int(nx_table[n - 1]['time'] + 1)
    return num_days


##############################################################################
# Get center UTC
#
def get_utc(indata):
    nx_table = indata.table('AIPS NX', 0)
    n = len(nx_table)
    ut1 = nx_table[0]['time']
    ut2 = nx_table[n - 1]['time']
    utc = (ut1 + ut2) / 2.
    return utc


##############################################################################
# Get center frequency in GHz
#
def get_center_freq(indata):
    fq = indata.table('AIPS FQ', 0)
    naxis = indata.header['naxis']
    if naxis[3] > 1:
        fq_span = fq[0]['if_freq'][indata.header.naxis[3] - 1] - fq[0]['if_freq'][0]
        frq = (indata.header.crval[2] + 0.5 * fq_span)
    else:
        frq = indata.header.crval[2]
    return frq


##############################################################################
# Download TEC maps
#
def get_TEC(year, doy, TECU_model, geo_path):
    year = str(year)[2:4]
    if doy < 10:
        doy = '00' + str(doy)
    elif doy < 100:
        doy = '0' + str(doy)
    else:
        doy = str(doy)

    name = TECU_model + doy + '0.' + year + 'i'
    #    name4='esag'+doy+'0.'+year+'i'
    #    if os.path.exists(name) or os.path.exists(name2):
    if os.path.exists(geo_path + name):
        print
        'TEC File already there.'
    else:
        path = 'https://cddis.nasa.gov/archive/gps/products/ionex/20' + year + '/' + doy + '/'
        os.popen(r'curl -c cookies.curl --netrc-file ~/.netrc -n -L -O ' + path + name + '.Z')
        os.popen(r'uncompress -f ' + name + '.Z')
        os.popen(r'mv ' + name + ' ' + geo_path)


#        if os.path.exists(name+'.Z'):
#            os.popen(r'rm '+name+'.Z')
#            os.popen(r'wget -t 30 -O '+name2+'.Z '+path+name2+'.Z')
#            os.popen(r'uncompress -f '+name2+'.Z')


##############################################################################
# Download EOP file
#
def get_eop(geo_path):
    if os.path.exists(geo_path + 'usno_finals.erp'):
        # +++ ZB
        # age = (time.time() - os.stat(eop_path+'usno_finals.erp')[8])/3600
        # if age<12: pass
        # else:
        #    os.popen(r'wget http://gemini.gsfc.nasa.gov/solve_save/usno_finals.erp')
        #    os.popen(r' rm -rf '+eop_path+'usno_finals.erp')
        #    os.popen(r'mv usno_finals.erp '+eop_path)
        print
        '---> Use downloaed erp file'
        # --- ZB
    else:
        os.popen(
            r'curl -c cookies.curl --netrc-file ~/.netrc -n -L -O "https://cddis.nasa.gov/archive/vlbi/gsfc/ancillary/solve_apriori/usno_finals.erp"')
        os.popen(r'mv usno_finals.erp ' + geo_path)

##############################################################################
# Get .key and .sum file from archive
def get_key_file(indata,code):
    mon_dir={1:'jan',2:'feb',3:'mar',4:'apr',5:'may',6:'jun',7:'jul',8:'aug'
        ,9:'sep',10:'oct',11:'nov',12:'dec'}
    path0=('http://www.vlba.nrao.edu/astro/VOBS/astronomy/')
    (year,month,day) = get_observation_year_month_day(indata)
    if code=='':
        code_str         = indata.header.observer.lower()
    else:
        code_str      = code
    path1=path0+mon_dir[month]+str(year)[2:4]+'/'+code_str+'/'+code_str+'.key'
    path2=path0+mon_dir[month]+str(year)[2:4]+'/'+code_str+'/'+code_str+'.sum'
    if os.path.exists(code_str+'.key'):
        pass
    else:
        os.popen(r'wget '+path1)
    if os.path.exists(code_str+'.sum'):
        pass
    else:
        os.popen(r'wget '+path2)


##############################################################################
#
def get_sources(indata):
    su_table = indata.table('AIPS SU', 0)
    max_source = 0

    for i in su_table:
        if i['id__no'] > max_source:
            max_source = i['id__no']

    sources = []
    for i in range(max_source):
        sources.append([])

    for i in su_table:
        sources[i['id__no'] - 1] = i['source']
    return sources


##############################################################################
# Find best scan for manual phasecal
#
def get_best_scan(indata, logfile, qualfile, do_write):
    sn_table = indata.table('AIPS SN', 0)
    naxis = indata.header['naxis']
    sources = get_sources(indata)

    t = [0]
    qf = [0]
    snr = []
    tr = []
    sid = []

    n = 0
    max_sol = 0

    sid.append(sn_table[0]['source_id'])
    tr.append(get_timerange_tab(indata, 'AIPS SN', 0))
    snr.append([])

    if naxis[3] > 1:
        for j in range(naxis[3]):
            if isinde(sn_table[0]['delay_1'][j]) == False:
                t[n] += 1
                qf[n] = qf[n] + 1. / sn_table[0]['weight_1'][j] ** 2
                snr[n].append(sn_table[0]['weight_1'][j])

        for i in range(1, len(sn_table)):
            if sn_table[i]['time'] == sn_table[i - 1]['time']:
                for j in range(naxis[3]):
                    if isinde(sn_table[i]['delay_1'][j]) == False:
                        t[n] += 1
                        qf[n] = qf[n] + 1. / sn_table[i]['weight_1'][j] ** 2
                        snr[n].append(sn_table[i]['weight_1'][j])
                if t[n] > max_sol:
                    max_sol = t[n]
                    id = n
            else:
                t.append(0)
                qf.append(0)
                snr.append([])
                n += 1
                sid.append(sn_table[i]['source_id'])
                tr.append(get_timerange_tab(indata, 'AIPS SN', i))
                for j in range(naxis[3]):
                    if isinde(sn_table[i]['delay_1'][j]) == False:
                        t[n] += 1
                        qf[n] = qf[n] + 1. / sn_table[i]['weight_1'][j] ** 2
                        snr[n].append(sn_table[i]['weight_1'][j])
                if t[n] > max_sol:
                    max_sol = t[n]
                    id = n

    elif naxis[3] == 1:
        if isinde(sn_table[0]['delay_1']) == False:
            t[n] += 1
            qf[n] = qf[n] + 1. / sn_table[0]['weight_1'] ** 2
            snr[n].append(sn_table[0]['weight_1'])

        for i in range(1, len(sn_table)):
            if sn_table[i]['time'] == sn_table[i - 1]['time']:
                if isinde(sn_table[i]['delay_1']) == False:
                    t[n] += 1
                    qf[n] = qf[n] + 1. / sn_table[i]['weight_1'] ** 2
                    snr[n].append(sn_table[i]['weight_1'])
                if t[n] > max_sol:
                    max_sol = t[n]
                    id = n
            else:
                t.append(0)
                qf.append(0)
                snr.append([])
                n += 1
                sid.append(sn_table[i]['source_id'])
                tr.append(get_timerange_tab(indata, 'AIPS SN', i))
                if isinde(sn_table[i]['delay_1']) == False:
                    t[n] += 1
                    qf[n] = qf[n] + 1. / sn_table[i]['weight_1'] ** 2
                    snr[n].append(sn_table[i]['weight_1'])
                if t[n] > max_sol:
                    max_sol = t[n]
                    id = n

    #    for i in range(len(t)):
    #        print sources[sid[i]-1],'Sol: ',t[i], 'QF: ',max(1/(qf[i]-0.00001),0), tr[i]
    #    print 'Max sol:',max_sol

    if do_write == 1:
        file = './' + outname[0] + '/' + qualfile
        f = open(file, 'w')
        for i in range(len(t)):
            f.writelines(' ' + sources[sid[i] - 1] + ' Sol: ' + str(t[i]) + ' QF: ' + str(
                round(max(1 / (qf[i] - 0.00001), 0), 3)) + ' ' + str(tr[i]) + '\n')
        f.close()

    scan = 0
    good_scans = []
    bad_scans = []
    bad_sources = []
    for i in range(len(t)):
        if t[i] == max_sol:
            good_scans.append(i)
        elif t[i] < max_sol * 0.4:
            bad_scans.append(i)

    scan = good_scans[0]
    source = sources[sid[0] - 1]
    timerange = tr[0]

    for i in good_scans:
        if qf[i] <= qf[scan]:
            scan = i
            source = sources[sid[i] - 1]
            timerange = tr[i]

    for i in range(len(bad_scans)):
        k = bad_scans[i]
        bad_sources.append(sources[sid[k] - 1])
    mprint('#################################', logfile)
    mprint('Bad sources: ' + str(bad_sources), logfile)
    mprint('#################################', logfile)

    mprint('#################################', logfile)
    mprint('Manual phase-cal on: ' + source, logfile)
    mprint('#################################', logfile)

    max_sol = naxis[3] * naxis[1] * len(indata.antennas)

    mprint('#################################', logfile)
    mprint('TIMERANGE: ' + str(timerange), logfile)
    mprint('Max number of solutions: ' + str(max_sol), logfile)
    mprint('#################################', logfile)

    return source, timerange

##############################################################################
# Write out qualities of geosources
#
def get_geosource_stats(indata):
    (year, month, day)=get_observation_year_month_day(indata)
    frq      = get_center_freq(indata)
    sn_table = indata.table('AIPS SN', 0)
    naxis    = indata.header['naxis']
    obs      = indata.header['observer']
    sources  = get_sources(indata)

    num_sour=len(indata.sources)
    snr=[]
    for i in range(0,len(sources)+1):
        snr.append([])

    for i in range(1,len(sn_table)):
        for j in range(naxis[3]):
            if isinde(sn_table[i]['weight_1'][j])==False and sn_table[i]['weight_1'][j] > 6:
                snr[sn_table[i]['source_id']].append(sn_table[i]['weight_1'][j])

    file = './geoblock/'+obs+'_geostat.dat'
    f = open(file,'w')
    f.writelines('!Source   #Det    Max      Min   Avgerage  Median on '+str(year)+'-'+str(month)+'-'+str(day)+' at '+str(round(frq,1))+' GHz \n')
    for i in range(1,len(sources)):
        if len(snr[i])>0 and sources[i]!=[]:
            outprint= sources[i]+'  %4d %6.1f   %6.1f   %6.1f   %6.1f\n' % (len(snr[i]), round(max(snr[i]),1), round(min(snr[i]),1), round(average(snr[i]),1), round(median(snr[i]),1))
            f.writelines(outprint)
        elif sources[i]!=[]:
            outprint= sources[i]+'  %4d %6.1f   %6.1f   %6.1f   %6.1f\n' % (0, 0, 0, 0, 0)
            f.writelines(outprint)
    f.close()

##############################################################################
#
def get_time():
    t=range(6)
    t[0]=time.localtime()[0]
    t[0]=str(t[0])
    for i in range(1,6):
        t[i]=time.localtime()[i]
        if t[i]<10:
            t[i]='0'+str(t[i])
        else:
            t[i]=str(t[i])
    a=t[3]+':'+t[4]+':'+t[5]+' on '+t[0]+'/'+t[1]+'/'+t[2]
    return a
##############################################################################
#


def findtarget(indata, target):
    targets=[]
    for entry in target:
        targets.append(entry)

    if targets == ['']:
        targets = []
        n = 0
        for source in indata.sources:
            if source[0]=='J':
                targets.append(source)
                n=n+1
    return targets


def get_split_sources(indata, target, cvelsource, calsource):

    split_sources=findtarget(indata, target)

    if calsource in cvelsource or calsource in target:
        pass
    else:
        split_sources.append(calsource)

    return split_sources
##############################################################################
#
def get_velocity(indata,cvelsource):
    cvelsource=findcvelsource(indata, cvelsource)
    light = 299792458
    nchan = indata.header['naxis'][2]
    res   = indata.header['cdelt'][2]
    su    = indata.table('AIPS SU',0)
    nif   = indata.header['naxis'][3]
    for entry in su:
        if entry['source'].strip() in cvelsource:
            vel=entry['lsrvel']
            restfreq=entry['restfreq']

    if nif>1:
        restfreq=restfreq[0]
    spacing=res/restfreq*light
    return vel, restfreq, nchan, res, spacing


##############################################################################
#
def get_real_sources(indata):
    nx=indata.table('AIPS NX',0)
    su=indata.table('AIPS SU',0)

    real_sources=[]
    for entry in nx:
        if (su[entry['source_id']-1]['source'].rstrip() in real_sources)==False:
            real_sources.append(su[entry['source_id']-1]['source'].rstrip())

    return real_sources

##############################################################################
#
def get_antname(an_table,n):
    name=''
    for entry in an_table:
        if n==entry['nosta']:
            name=entry['anname']
    return name



##############################################################################
#
def get_phasecal_sources(indata,mp_source,logfile):
    if mp_source == ['']:
        mp_source = []
        for source in indata.sources:
            if source[0]=='F':
                mp_source.append(source)

    newdata = AIPSUVData(indata.name, 'UVCOP', indata.disk, 1)
    if newdata.exists():
        newdata.zap()

    uvcop        = AIPSTask('UVCOP')
    uvcop.indata = indata
    uvcop.source[1:] = mp_source
    uvcop.go()

    return newdata
################################################################################
# Extract line name from a uvdata
#
def get_line_name(indata):
    freq = get_center_freq(indata)/1e9
    if freq>12 and freq<13:
        restfreq = [1.2178E+10,597000]
        linename='CH3OH_12GHz'
        print 'Assuming 12.2 GHz methanol maser.'
    elif freq>22 and freq<23:
        restfreq = [2.2235E+10,80000]
        linename='H2O'
        print 'Assuming 22.2 GHz water maser.'
    elif freq>6 and freq<7:
        restfreq = [6.668e+09, 519200]
        linename='CH3OH_6.7GHz'
        print 'Assuming 6.7 GHz methanol maser.'
    elif freq>43.1 and freq<43.2:
        restfreq = [43.122e+09,80000]
        linename='SiO_43.1GHz'
        print 'Assuming 43.122 GHz SiO maser.'
    else:
        print 'Unknown maser line.'
        exit()

    return (linename, restfreq)





##############################################################################
#
def get_image_peak(idir='./'):
    infile = idir+"imean.txt"
    if os.path.exists(infile):
        myfile = open(infile)

        for line in myfile.readlines():
            strtmp = 'Maximum'
            if cmp(strtmp,line[0:7]) == 0:
                peak = line[9:20]
        myfile.close()

        peak=float(peak)
        return peak
    else:
        print('###--- '+infile)
        print('###--- Input file dose not exsit')
def get_download_names(ou, op, of):
    user=ou
    passw=op
    if user=='nopass':
        file_names = []
        file_sizes = []
        for entry in date_pubfiles_nr[date_nr+1]:
            file_names.append(pubfiles[entry-1])
            file_sizes.append('')
    else:
        os.popen(r'wget --no-check-certificate --http-user '+user+
                 ' --http-passwd '+passw+' -t45 -O files.txt'+
                 ' https://archive.nrao.edu/secured/'+user+'/', 'w')

        f=open('files.txt')
        content=f.read()
        f.close()

        t=content.split('"')
        t=content.split('\n')
        file_names=[]
        file_sizes=[]
        for entry in t:
            if 'fits' in entry:
                t2=entry.split('"')
                file_names.append(t2[1])
                file_sizes.append(entry[-8:])
        os.popen(r'rm files.txt')

    if inter_flag==1 and of[0]==0:
        print_download_options(user,passw, file_names,file_sizes)
        cont=raw_input('Use these filenames? (y/n) ')
        if cont=='n' or cont=='N':
            order=[]
            for i in range(0,len(file_names)):
                entry = file_names[i]
                print entry,file_sizes[i]
                cont=raw_input('File number? ')
                if int(cont)>len(file_names)-1:
                    print 'Only Number 0 to '+str(len(file_names)-1)+' allowed.'
                    cont=raw_input('File number? ')
                order.append(cont)


            new_file_names=range(0,len(file_names))
            for i in range(0,len(file_names)):
                new_file_names[int(order[i])]=file_names[i]
            file_names = new_file_names
            print_download_options(user,passw,file_names,file_sizes)
            return file_names, len(file_names)

        else:
            return file_names, len(file_names)

    elif inter_flag==1 and of[0]!=0:
        print_download_options(user,passw, of, file_sizes)
        cont=raw_input('Use these filenames? (y/n) ')
        if cont=='n' or cont=='N':
            order=[]
            for entry in file_names:
                print entry
                cont=raw_input('File number? ')
                if int(cont)>len(file_names)-1:
                    print 'Only Number 0 to '+str(len(file_names)-1)+' allowed.'
                    cont=raw_input('File number? ')
                order.append(cont)

            new_file_names=range(0,len(file_names))
            for i in range(0,len(file_names)):
                new_file_names[int(order[i])]=file_names[i]
            file_names = new_file_names
            print_download_options(user,passw,file_names, file_sizes)
            return file_names, len(file_names)

        else:
            return of, len(of)

    else:
        if of[0]!=0:
            print_download_options(ou,op,of,file_sizes)
            return of, len(of)
        else:
            print_download_options(user,passw, file_names,file_sizes)
            return file_names, len(file_names)

