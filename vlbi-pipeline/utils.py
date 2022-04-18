#!/usr/bin/env python

def mprint(intext, logfile):
    print(intext)
    f = open(logfile, 'a')
    f.writelines(intext + '\n')
    f.close()


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
