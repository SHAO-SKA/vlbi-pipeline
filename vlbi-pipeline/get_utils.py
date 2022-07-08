#!/usr/bin/env python

import os
import time

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
        #todo make sure .netrc exists
        os.popen(r'curl -c cookies.curl --netrc-file ~/.netrc -n -L -O ' + path + name + '.Z')
        #todo make sure the file download
        os.popen(r'uncompress -f ' + name + '.Z')
        os.popen(r'mv ' + name + ' ' + geo_path)


'''
CDDIS Archive Access: .netrc instructions
In order for cURL to use those credentials you will need to create a .netrc file.

To create a .netrc file, you will need to create a text file with the name .netrc; this file needs to have read permissions set to only yourself, so that no one can read your file and get your username and password. The format of the file is:

machine urs.earthdata.nasa.gov login <username> password <password>

where <username> and <password> are the values you set when you created your Earthdata login account.
'''


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
        #todo make sure .netrc exists
        os.popen(
            r'curl -c cookies.curl --netrc-file ~/.netrc -n -L -O "https://cddis.nasa.gov/archive/vlbi/gsfc/ancillary/solve_apriori/usno_finals.erp"')
        os.popen(r'mv usno_finals.erp ' + geo_path)



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

def get_observation_year_month_day(aips_data):
    '''
    Get the day ot year/month/day for the start of observation
    '''
    date_string = aips_data.header.date_obs
    date_list = date_string.split('-')
    year = int(date_list[0])
    month = int(date_list[1])
    day = int(date_list[2])
    return (year, month, day)

def get_num_days(indata):
    '''
    Get number of days
    '''
    nx_table = indata.table('AIPS NX', 0)
    n = len(nx_table)
    num_days = int(nx_table[n - 1]['time'] + 1)
    return num_days

def get_day_of_year(year, month, day):
    '''
    Get the doy from year/month/day
    '''
    day_of_year_list = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    doy = day_of_year_list[month - 1] + day
    if (month > 2):
        if ((year & 0x3) == 0):
            if ((year % 100 != 0) or (year % 400 == 0)):
                doy = doy + 1
    return doy
