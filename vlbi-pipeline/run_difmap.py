# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 16:28:32 2017

"""

import pexpect
import sys
import os
import re
import time
import numpy as np
from shutil import copyfile
from astropy.io.fits import getheader
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, datestr2num
from matplotlib.backends.backend_pdf import PdfPages

current_path=''

def word2pix(h,xy):
	x,y = xy
	x = h['crpix1'] + x/(h['cdelt1']*3.6E6)
	y = h['crpix2'] + y/(h['cdelt2']*3.6E6)
	return x,y
def pix2word(h,xy):
	x,y = xy
	x = h['cdelt1']*3.6E6*(x-h['crpix1'])
	y = h['cdelt2']*3.6E6*(y-h['crpix2'])
	return x,y
def W2w(h,w=()):
	if len(w)==4:
		x0, x1, y0, y1 = w
	else:
		x0, y0 = 0, 0
		x1, y1 = h['naxis1'], h['naxis2']
	x0, y0 = pix2word(h,(x0,y0))
	x1, y1 = pix2word(h,(x1,y1))
	w = x0, x1, y0, y1
	return w
def w2W(h,w=()):
	if len(w)==4:
		x0, x1, y0, y1 = w
		x0, y0 = word2pix(h,(x0,y0))
		x1, y1 = word2pix(h,(x1,y1))
	else:
		x0, y0 = 0, 0
		x1, y1 = h['naxis1'], h['naxis2']
	w = x0, x1, y0, y1
	return w

def get_uvdata():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('vis.fits')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_clnpar():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-cln.par')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_debug():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-debug.uvf')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_uvmod():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-cln.uvf')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_modpar():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-mod.par')]  # modr of mod
	images = np.array(images)
	images = np.sort(images)
	return images
def get_modrpar():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-modr.par')]  # modr of mod
	images = np.array(images)
	images = np.sort(images)
	return images
def get_splt():#1.splt
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('1.splt')]  # for splt file
	images = np.array(images)
	images = np.sort(images)
	return images
def get_autodata():#automod.par
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('automod.par')]  # for splt file
	images = np.array(images)
	images = np.sort(images)
	return images
def get_autodata2():#-automod2.par
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-automod2.par')]  # for splt file
	images = np.array(images)
	images = np.sort(images)
	return images

def getsnr(difmap):
    difmap.sendline('invert')
    difmap.expect('0>')
    difmap.sendline('print peak(flux,max)/imstat(rms)')
    difmap.expect('0>')
    p = re.compile(r'([-+]?[0-9\.]+)')
    s = difmap.before.decode()
    snr = float(p.findall(s)[0])
    difmap.sendline('print imstat(rms)')
    difmap.expect('0>')
    p2 = re.compile(r'([-+]?[0-9\.]+)')
    s2 = difmap.before.decode()
    rms = float(p2.findall(s2)[0])
    difmap.sendline('print peak(x)')
    difmap.expect('0>')
    s3 = difmap.before.decode()
    peakx = float(p.findall(s3)[0])
    difmap.sendline('print peak(y)')
    difmap.expect('0>')
    s4 = difmap.before.decode()
    peaky = float(p.findall(s4)[0])
    difmap.sendline('device /null')
    difmap.expect('0>')
    difmap.sendline('maplot cln')
    difmap.expect('0>')
    difmap.sendline('print peak(flux,max)')
    difmap.expect('0>')
    p = re.compile(r'([-+]?[0-9\.]+)')
    s = difmap.before.decode()
    peak = float(p.findall(s)[0])
    return snr,rms,peakx,peaky, peak

def apscal(difmap,solint):
    difmap.sendline('selfcal true,true,%s' % solint)
    difmap.expect('0>')
    return
def modfcal(difmap,snrcut,numcut):
    nm=0
    snr,rms,pkx,pky=getsnr(difmap)
    print(snr,rms,pkx,pky)
    while snr > snrcut:
        if nm > numcut:
            break
        else:
            difmap.sendline('addcmp 0.1,true,%f,%f,true,0,false,1,false,0,true,0'%(pkx,pky))
            difmap.expect('0>')
            difmap.sendline('modelfit 50')
            difmap.expect('0>',timeout=500)
            difmap.sendline('selfcal')
            difmap.expect('0>',timeout=500)
            snr,rms,pkx,pky=getsnr(difmap)
            print(snr,rms,pkx,pky)
            nm=nm+1
    return

def difmap_image():#imaging
    script_path=current_path + '/'
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 200000
    images = get_uvdata()
    names = ''
    for i in range(images.size):
        tname=images[i] + '.fits'
        names=images[i] 
        code=tname[0:5] + '-'+ tname[13:17] + tname[18:20]+ tname[21:23] + tname[11] +'-cln'
        # tname = 'J0048+0640_S_2004_04_30_yyk_vis.fits'
        sourcename = tname.split('_')[0]
        band = tname.split('_')[1]
        date = tname.split('_')[2] + tname.split('_')[3] + tname.split('_')[4]
        people = tname.split('_')[5]
        code = sourcename + '_' + band + '_' + date + '_' + people
        if not os.path.exists('%s.fits'% code):
            difmap.sendline('obs %s' %tname)
            difmap.expect('0>')
            print('obs ' + tname)
            band = tname[11]
            if band == 'S':
                difmap.sendline('@%sdscrip-new-s %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            elif band  == 'X' or band == 'C' or  band == 'U':
                difmap.sendline('@%sdscrip-new-x %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            elif band ==  'K' or band == 'Q' or band == 'W' :
                difmap.sendline('@%sdscrip-new-u %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            print('done %s' % code)
        else:
            difmap.sendline('@%s.par' %code)
            difmap.expect('0>')
            difmap.sendline('device /null')
            difmap.expect('0>')
            difmap.sendline('mapplot cln')
            difmap.expect('0>')
            difmap.sendline('restore sqrt(bmaj*bmin)*3600*1000*180/3.1416')
            difmap.expect('0>')
            difmap.sendline('xyrange 40,-40,40,-40')
            difmap.expect('0>')
            #name_restore=tname[:-5]+'-circle_beam.fits'
            #name_restore=tname[0:5] + '-'+ tname[13:17] + tname[18:20]+ tname[21:23] + tname[11] +'-circle_beam.fits'
            name_restore=code
            difmap.sendline('wmap %s' %name_restore)
            difmap.expect('0>')
            print('wmap %s' %name_restore)
            print('file already there, move on')
    #print('0>',difmap.read().decode('ascii'))
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
        
        
def modfit1():
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    images=get_uvmod()
    for i in range(images.size):
      name2=images[i]+'.uvf'
      names=name2[0:15]+'-mod'
      print(name2)
      #if not os.path.exists('%s.mod'% names):
      if True:
          difmap.sendline('obs %s' %name2)
          difmap.expect('0>')
          difmap.sendline('select i')
          difmap.expect('0>')
          band = name2[14]
          if band == 'S':
              difmap.sendline('mapsize 2048,0.4')
              difmap.expect('0>')
          elif band == 'C':
              difmap.sendline('mapsize 1024,0.4')
              difmap.expect('0>')
          elif band == 'X':
              difmap.sendline('mapsize 1024,0.2')
              difmap.expect('0>')
          elif band == 'U':    
              difmap.sendline('mapsize 1024,0.1')
              difmap.expect('0>')
          difmap.sendline('uvw 0,-1')
          difmap.expect('0>')
          # difmap.sendline('rmod 0203mod.mod')
          # difmap.expect('0>')
          # difmap.sendline('modelfit 50')
          # difmap.expect('0>',timeout=200)
          name_flux =name2 + '-flux.txt'
          print(name_flux)
          fp = open(name_flux, 'a')
          snr,rms,pkx,pky, peak=getsnr(difmap)
          print(snr,rms,pkx,pky, peak)
          fp.write("snr : " + str(snr))
          fp.write('\n')
          fp.write("rms : " + str(rms))
          fp.write('\n')
          fp.write("pkx : " + str(pkx))
          fp.write('\n')
          fp.write("pky : " + str(pky))
          fp.write('\n')
          fp.write("peak: " + str(peak))
          fp.write('\n')
          nm=0
          while snr > 10:
              if nm > 9:
                  break
              else:
                  if nm == 0 : # make sure ecllipse guassian fit at first time
                        difmap.sendline('addcmp 0.1,true,%f,%f,true,0.1,true,1,true,0,true,1'%(pkx,pky))
                  else:
                        difmap.sendline('addcmp 0.1,true,%f,%f,true,0.1,true,1,false,0,true,1'%(pkx,pky))
                  #difmap.sendline('addcmp 0.1,true,%f,%f,true,0,false,1,false,0,true,0'%(pkx,pky))
                  difmap.expect('0>')
                  difmap.sendline('modelfit 50')
                  difmap.expect('0>',timeout=500)
                  snr,rms,pkx,pky, peak=getsnr(difmap)
                  print(snr,rms,pkx,pky,peak)
                  fp.write("snr : " + str(snr))
                  fp.write('\n')
                  fp.write("rms : " + str(rms))
                  fp.write('\n')
                  fp.write("pkx : " + str(pkx))
                  fp.write('\n')
                  fp.write("pky : " + str(pky))
                  fp.write('\n')
                  fp.write("peak: " + str(peak))
                  fp.write('\n')
                  nm=nm+1
          fp.close()
          difmap.sendline('save %s' %names)
          difmap.expect('0>')
          print('done %s'%names)
      else:
          print('model already there, move on')
    difmap.sendline('quit')
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
        
def modfit_rmod(mod,band):
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    images=get_uvmod()
    for i in range(images.size):
      name2=images[i]+'.par'
      names=name2[0:15]+'-mod'
      namenew=names+'r'
      # print(namenew,name2,names)
      if not os.path.exists('%s.mod'% namenew):
        if name2[14] ==band:
          difmap.sendline('@ %s' %name2)
          difmap.expect('0>')
          # difmap.sendline('clrmod true')
          # difmap.expect('0>')
          difmap.sendline('delwin')
          difmap.expect('0>')
          difmap.sendline('rmod %s' %mod)
          difmap.expect('0>')
          difmap.sendline('modelfit 100')
          difmap.expect('0>',timeout=300)
          snr,rms,pkx,pky=getsnr(difmap)
          print(snr,rms,pkx,pky)
          nm=0
          while snr > 5:
              if nm > 3:
                  break
              else:
                  difmap.sendline('modelfit 50')
                  difmap.expect('0>',timeout=500)
                  snr,rms,pkx,pky=getsnr(difmap)
                  print(snr,rms,pkx,pky)
                  nm=nm+1
          difmap.sendline('save %s' %namenew)
          difmap.expect('0>')
          print('done %s'%namenew)
      else:
          print('model already there, move on')
    difmap.sendline('quit')
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
        
        
def check():
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    images=get_clnpar()
    difmap.sendline('device radp.ps/vps')
    difmap.expect('0>')
    for i in range(images.size):
      name2=images[i]+'.par'
      # print(name2)
      difmap.sendline('@ %s' %name2)
      difmap.expect('0>')
      difmap.sendline('radpl')
      difmap.expect('0>')
      print('radp %s'%name2) 
    difmap.sendline('device resi.ps/vcps')
    difmap.expect('0>')
    for i in range(images.size):
      name2=images[i]+'.par'
      # print(name2)
      difmap.sendline('@ %s' %name2)
      difmap.expect('0>')
      difmap.sendline('mapcol col')
      difmap.expect('0>')
      difmap.sendline('mapl map,true')
      difmap.expect('0>')
      print('resi %s'%name2)
    difmap.sendline('quit')
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)  

        
def debug():
    script_path='./'
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    images=get_debug()
    for i in range(images.size):
        tname=images[i] + '.uvf'
        code=tname[0:15]+'-cln'
        difmap.sendline('obs %s' %tname)
        difmap.expect('0>')
        # difmap.sendline('uvaver 40')
        # difmap.expect('0>')
        print('obs ' + tname)
        band = tname[14]
        if band == 'S':
                difmap.sendline('@%sdscrip-new-s %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
        elif band == 'X' or band == 'C' or band == 'U':
                difmap.sendline('@%sdscrip-new-x %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
        elif band == 'K' or band == 'Q' or band == 'W' :
                difmap.sendline('@%sdscrip-new-u %s' % (script_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
        print('debug %s' % code)
    difmap.sendline('quit')
    #print('0>',difmap.read().decode('ascii'))
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
    
def check_mod(band,r):
    if r == 0 :
        images=get_modpar() #choose to use mod or modr, edit the original selection
    elif r == 1:
        images=get_modpar()
    elif r == 2:
        images=get_modrpar()
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    if r == 0:
        difmap.sendline('device mod-%s%s.ps/vps' %(band,r))
        difmap.expect('0>')
    elif r ==1:
        difmap.sendline('device mod-%s%s.ps/vcps' %(band,r))
        difmap.expect('0>')
    for i in range(images.size):
        name2=images[i]+'.par' 
        print(name2)
        #if name2[14] == band or True:
        if True:
            difmap.sendline('@ %s' %name2)
            difmap.expect('0>')
            if band == 'S' or band == 'C':
                difmap.sendline('xyrange 50,-50,50,-50')
                difmap.expect('0>')
            if band == 'X':
                difmap.sendline('xyrange 20,-20,20,-20')
                difmap.expect('0>')
            if band == 'U':
                difmap.sendline('xyrange 10,-10,10,-10')
                difmap.expect('0>')
            difmap.sendline('invert')
            difmap.expect('0>')
            difmap.sendline('low')
            difmap.expect('0>')                
            if band == 'S':
                difmap.sendline('mapsize 2048,0.5')
                difmap.expect('0>')
            elif band == 'C':
                difmap.sendline('mapsize 2048,0.4')
                difmap.expect('0>')
            elif band == 'X':
                difmap.sendline('mapsize 2048,0.2')
                difmap.expect('0>')
            elif band == 'U':    
                difmap.sendline('mapsize 2048,0.1')
                difmap.expect('0>')
            if r == 0:
                difmap.sendline('mapcol none,true')  #chcolor
                difmap.expect('0>')
            elif r ==1:
                difmap.sendline('mapcol col')  #chcolor
                difmap.expect('0>')
            # difmap.sendline('mapl map,true')
            difmap.sendline('mapl cln,true')
            difmap.expect('0>')
            print('checkmod %s'%name2)
    difmap.sendline('quit')
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)  
        
def go_dir(path):
  for root, dirs, files in os.walk(path):
      print('dirs', dirs)
      return dirs

def get_countour(path):
  for name in go_dir(path):
    print (name)
    os.chdir(name)
    check_mod('S',1)   #'' means original point fitting, for preview. 'r' means rmod results, for checking re
    check_mod('X',1)
    check_mod('C',1)
    check_mod('U',1)
    os.chdir('..')
    
        
if __name__ == '__main__' :
    path=sys.argv[1]+'/' # TODO SPLIT data location
    current_path=os.getcwd()
    os.chdir(path)
    mode = 'clean'
    if len(sys.argv) == 3:
        mode = sys.argv[2]
    if mode == 'clean':
        difmap_image()
    if mode == 'modfit':
        modfit1()  # adding models automatically
    #modfit1(3,1,300)  # adding models automatically
    #modfit2(1.4)
    # check()
    # debug()
    #check_mod('S',0)   #'' means original point fitting, for preview. 'r' means rmod results, for checking re
    # check_mod('X',0)
    # get_countour(path)
