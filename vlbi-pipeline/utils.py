#!/usr/bin/env python

from pylab import *
from check_utils import *


def mprint(intext, logfile):
    print(intext)
    f = open(logfile, 'a')
    f.writelines(intext + '\n')
    f.close()


#############################################

def time_to_hhmmss(time):
    day = int(time)
    if time > 1:
        time = time - int(time)
    hour = int(time * 24)
    min = int(60 * (time * 24 - hour))
    sec = int(60 * (60 * (time * 24 - hour) - min))
    return day, hour, min, sec


def isinde(number):
    INDE = 3140.892822265625
    return abs(number - INDE) < 1e-12


def deg_to_radec(pos):
    if pos[0] < 0:
        pos[0] = 360 + pos[0]
    ra_deg = pos[0] / 15.
    dec_deg = pos[1]
    hour = int(ra_deg)
    min = int(60 * (ra_deg - hour))
    sec = (60 * (60 * (ra_deg - hour) - min))
    if abs(60 - round(sec, 5)) < 1e-5:
        sec = 0
        min += 1
    if min == 60:
        min = 0
        hour += 1
    if hour < 0: hour = hour + 24
    if hour >= 24: hour = hour - 24
    hp = ''
    mp = ''
    sp = ''
    if hour < 10: hp = '0'
    if min < 10: mp = '0'
    if sec < 10: sp = '0'
    ra = hp + str(hour) + ':' + mp + str(min) + ':' + sp + str(round(sec, 5))
    deg = abs(int(dec_deg))
    amin = int(60 * (abs(dec_deg) - deg))
    asec = (60 * (60 * (abs(dec_deg) - deg) - amin))
    if 60 - abs(round(asec, 4)) < 1e-4:
        asec = 0
        amin += 1
    if amin == 60:
        amin = 0
        deg += 1
    if dec_deg < 0:
        sign = '-'
    else:
        sign = '+'
    dp = ''
    amp = ''
    asp = ''
    if deg < 10: dp = '0'
    if amin < 10: amp = '0'
    if asec < 10: asp = '0'
    dec = sign + dp + str(abs(deg)) + ':' + amp + str(abs(amin)) + ':' + asp + str(round(abs(asec), 4))
    return ra, dec


def fringecal(indata, fr_image, nmaps, gainuse, refant, refant_candi, calsource,solint,smodel, doband, bpver, dpfour, logfile):
    fringe             = AIPSTask('FRING')
    if fr_image.exists():
        fringe.in2data = fr_image
        logging.info('#############################')
        mprint('Using input model '+fringe.in2name+'.'+fringe.in2class+'.'+str(int(fringe.in2seq))+' on diks '+str(int(fringe.in2disk)), logfile)
        logging.info('#############################')
    elif smodel!=[1,0]:
        fringe.smodel[1:] = smodel
        logging.info('#############################')
        mprint('Using SMODEL='+str(smodel)+' for fringe.',logfile)
        logging.info('#############################')
    else:
        logging.info('#############################')
        mprint('Using point source as imput model for fringe.',logfile)
        logging.info('#############################')

    if doband==1:
        logging.info('#############################')
        mprint('Applying bandpass table '+str(bpver), logfile)
        logging.info('#############################')
    else:
        logging.info('#############################')
        mprint('Applying no bandpass table ', logfile)
        logging.info('#############################')

    fringe.indata      = indata
    fringe.refant      = refant
    fringe.docal       = 1
    fringe.calsour[1:] = [calsource]
    fringe.solint      = solint
    fringe.aparm[1:]   = [2, 0, 1, 0, 1]
    fringe.dparm[1:]   = [1, 20, 50, 0]
    fringe.dparm[4]    = dpfour
    fringe.dparm[8]    = 0
    fringe.nmaps       = nmaps
    fringe.snver       = 0
    fringe.gainuse     = gainuse
    fringe.doband      = int(doband)
    fringe.bpver       = int(bpver)
    fringe.search[1:]  = refant_candi
    fringe()

def fringecal_ini(indata, refant, refant_candi, calsource, gainuse, flagver, solint, doband, bpver):
    fringe             = AIPSTask('FRING')
    fringe.indata      = indata
    fringe.refant      = refant
    fringe.docal       = 1
    print type(calsource)
    if(type(calsource) == type('string')):
    	fringe.calsour[1] = calsource
    else:
	fringe.calsour[1:] = calsource
    fringe.search[1:]  = refant_candi
    fringe.solint      = solint
    fringe.aparm[1:]   = [3, 0, 0, 0, 1, 0, 0, 0, 1]
    fringe.dparm[1:]   = [0, 100, 100, 0]
    #fringe.dparm[4]   = dpfour
    fringe.dparm[8]    = 0
    fringe.gainuse     = gainuse
    fringe.flagv       = flagver
    fringe.snver       = 0
    fringe.doband      = int(doband)
    fringe.bpver       = int(bpver)
    fringe.input()
    fringe()


##############################################################################
# Get download options from mail

def read_mail(mail_path, ou, op, of, inter_flag):
    f=open(mail_path)
    content=f.readlines()
    f.close()

    users=[]
    passs=[]
    dates=[]
    pubfiles=[]
    date_pubfiles_nr={}
    pubfile_nr=[]
    k = 0
    kk = 0
    j = 0

    for n in range(len(content)):
        if 'From: VLA/VLBA' in content[n]:
            j=j+1
            date=content[n-1].rstrip()
            dates.append(date)
        pfa = 'Public File available :'
        if pfa in content[n] and (pfa in content[n-1])==False:
            while pfa in content[n+kk]:
                kk=kk+1
                k=k+1
                pubfile_nr.append(k)           
            date_pubfiles_nr[j]=pubfile_nr 
        pubfile_nr=[] 
        kk=0


    for entry in content:
        if 'Proprietary File Dir :' in entry:
            prop_dir = entry.split(' ')[4].rstrip()
        elif 'Your access username, password :' in entry:
            user  = entry.split(' ')[5]
            passw = entry.split(' ')[7].rstrip()
            users.append(user)
            passs.append(passw)
        elif 'Public File available :' in entry:
            user = 'nopass'
            passw = ''
            users.append(user)
            passs.append(passw)
            pubfiles.append(entry.split('/')[4].rstrip())


    if len(dates)>1:
        print 'Found VLA/VLBA archive emails from:'
        for i in range(len(dates)):
            print str(i+1)+': '+dates[i] 

        if inter_flag==1: 
            date_nr=input('Which one? (1-'+str(len(dates))+') ')-1
            if (date_nr in range(len(dates)))==False:
                print 'No such date.'
                sys.exit()
        else: 
            date_nr=len(dates)-1

        print 'Using: '+date
        print ''
        user=users[date_nr]
        passw=passs[date_nr]
        print user, passw


    if user=='nopass': 
        file_names = []  
        for entry in date_pubfiles_nr[date_nr+1]:
            file_names.append(pubfiles[entry-1])
    else:
        os.popen(r'wget --no-check-certificate --http-user '+user+
                 ' --http-passwd '+passw+' -t45 -O files.txt'+
                 ' https://archive.nrao.edu/secured/'+user+'/', 'w')
        print ' https://archive.nrao.edu/secured/'+user+'/'

        f=open('files.txt')
        content=f.read() 
        f.close()  

        t=content.split('"')
        file_names=[]
        for entry in t:
            if 'fits' in entry:
                file_names.append(entry)

        os.popen(r'rm files.txt')

    print_download_options(user,passw, file_names)
       
    if inter_flag==1: 
        cont=raw_input('Use these filenames? (y/n) ')
        if cont=='n' or cont=='N':
            print 'Using other filenames:'
            print_download_options(ou,op,of)
            return ou, op, '', of, len(of)

        else:
            return user, passw, prop_dir, file_names, len(file_names)
    else:
        return user, passw, prop_dir, file_names, len(file_names)


def print_download_options(user,passw,file_names,file_sizes):
    print '    file        = range(n)'
    print '    arch_user   = \''+user+'\''
    print '    arch_pass   = \''+passw+'\''  
    print ''
    
    n=0
    for i in range(0,len(file_names)):
        print '    file['+str(n)+'] = \''+file_names[i]+'\' ('+file_sizes[i]+')'
        n=n+1
    print ''

def data_info(indata, i, geo, cont, line, logfile):
    if indata.exists():
        frq=get_center_freq(indata)/1e9
        if frq>1.3 and frq< 1.8:  band='L'
        elif frq>2.1 and frq<2.4: band='S'
        elif frq>4.5 and frq<8: 
            if check_sx(indata, logfile): band='S/X'
            else: band='C'
        elif frq>8.0 and frq<10.0:  band='X'
        elif frq>11.5 and frq<16.0: band='U'
        elif frq>21.5 and frq<24.5: band='K'
        elif frq>40.5 and frq<45.5: band='Q'
        else:
            band='unknown'
        if i==geo: add = ' (geoblock data)'
        elif i==cont and i!=line: add = ' (continuum data)'
        elif i==line and i!=cont: add = ' (line data)'
        elif i==line and i==cont: add = ' (line or continuum data)'
        else: add = ' (data not used)'
        naxis    = indata.header['naxis']  
        mprint('File '+str(i)+': '+indata.name+' '+band+' band, '+str(naxis[1])
              +' Stokes, '+str(naxis[2])+' channels '+str(naxis[3])
              +' IFs'+add, logfile)
        return band, naxis[1], naxis[2], naxis[3]

def restore_su(indata, logfile):
    tasav_data=AIPSUVData(indata.name,'TASAV'+str(i),int(indata.disk),1)
    if tasav_data.exists():
        logging.info('##########################################')
        mprint('TASAV file exists, restoring old SU table.', logfile)
        logging.info('##########################################')
        while indata.table_highver('AIPS SU')>0:
            indata.zap_table('AIPS SU', 1)
        runtacop(tasav_data, indata, 'SU', 1, 1, 0)
    else:
        logging.info('##########################################')
        mprint('No TASAV file. Restoring SU table not possible.',logfile)
        logging.info('##########################################')

##############################################################################
#  
def restore_fg(indata, logfile):
    tasav_data=AIPSUVData(indata.name,'TASAV'+str(i),int(indata.disk),1)
    if tasav_data.exists():
        logging.info('##########################################')
        mprint('TASAV file exists, restoring old FG table.', logfile)
        logging.info('##########################################')
        while indata.table_highver('AIPS FG')>0:
            indata.zap_table('AIPS FG', 0)
        runtacop(tasav_data, indata, 'FG', 1, 1, 0)
    else:
        logging.info('##########################################')
        mprint('No TASAV file. Restoring SU table not possible.',logfile)
        logging.info('##########################################')
