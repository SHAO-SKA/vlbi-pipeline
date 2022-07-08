#!/usr/bin/env python

def select_refant(indata):
    '''
    Select one of the inner VLBA antennas
    '''
    ant=get_ant(indata)
    if 'LA' in indata.antennas:
        refant='LA'
    elif 'PT' in indata.antennas:
        refant='PT'
    elif 'KP' in indata.antennas:
        refant='KP'
    elif 'FD' in indata.antennas:
        refant='FD'
    elif 'EF' in indata.antennas:
        refant='EF'
    elif 'EB' in indata.antennas:
        refant='EB'
    for i in ant:
        if ant[i]==refant:
            j=i
    return j

def select_refant2(indata, logfile):
    '''
    Select best antenna  based on testfringe
    '''
    ant=get_ant(indata)
    sn=indata.table('AIPS SN', 2)
    sol=range(max(ant))
    for i in range(len(sol)):
        sol[i]=0
    for i in range(0,len(sn)):
        an=sn[i]['antenna_no']
        if (ant[an]=='LA' or ant[an]=='PT' or
                ant[an]=='KP' or ant[an]=='FD' or
                ant[an]=='EF' or ant[an]=='EB'):
            sol[an-1]+=1
    for i in ant:
        if sol[i-1]==max(sol):
            refant=i
    logging.info('##########################################')
    logging.info('Reference antenna : ', ant[refant])
    logging.info('##########################################')
    return refant

