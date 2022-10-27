# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 16:28:32 2017

"""

import pexpect
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

def get_clnpar():#-cln.par
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-cln.par')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_debug():
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-debug.uvf')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_uvmod(): #-cln.vuf
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-cln.uvf')]
	images = np.array(images)
	images = np.sort(images)
	return images

def get_modpar():#-mod.par
	images = [os.path.splitext(f)[0] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('-mod.par')]  # modr of mod
	images = np.array(images)
	images = np.sort(images)
	return images
def get_modrpar():#-modr.par
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
    print(p.findall(s))
    snr = float(p.findall(s)[0])
    difmap.sendline('print imstat(rms)')
    difmap.expect('0>')
    p2 = re.compile(r'([-+]?[0-9\.]+)')
    s2 = difmap.before.decode()
    rms = float(p2.findall(s2)[0])
    difmap.sendline('print peak(x,max)')
    difmap.expect('0>')
    s3 = difmap.before.decode()
    peakx = float(p.findall(s3)[0])
    difmap.sendline('print peak(y,max)')
    difmap.expect('0>')
    s4 = difmap.before.decode()
    peaky = float(p.findall(s4)[0])
    return snr,rms,peakx,peaky

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
            
            
def difmap_image(band):#imaging
    # TODO setting the script path :(
    # Must be absolutely data path
    src_path='/data/VLBI/code/vlbi-pipeline/utils/'
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 200000
    images = get_splt()
    for i in range(images.size):
        tname=images[i] + '.splt'
        code=tname[:-5]+'-cln'
        print('Running code ', code)
        if not os.path.exists('%s.fits'% code):
            difmap.sendline('obs %s' %tname)
            difmap.expect('0>')
            print('obs ' + tname)    
            if band == 'S' or 'L':
                print('running [S] ' + tname)    
                difmap.sendline('@%sdscrip-new-s %s' % (src_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            elif band == 'X' or 'C' or 'U':
                print('running [X] ' + tname)    
                difmap.sendline('@%sdscrip-new-x %s' % (src_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            elif band ==  'K' or 'Q' or 'W' :
                print('running [U] ' + tname)    
                difmap.sendline('@%sdscrip-new-u %s' % (src_path,code))
                difmap.expect('Writing difmap environment.*0>',timeout=400)
            print('done %s' % code)
        else:
            print('file already there, move on')
    difmap.sendline('quit')
    #print('0>',difmap.read().decode('ascii'))
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
        
        
def modfit1(step,freq,solint): #direct auto-model fitting with point models
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    if step == 1:#purely from split file
        images=get_splt()
        readn='.splt'
        saven='-automod'
    elif step == 2:#from mannual -cln file
        images=get_uvmod()
        readn='.uvf'
        saven='-clnautomod'
    elif step == 3:#from -automod file
        images=get_autodata()
        readn='.uvf'
        saven='-automod2'
    elif step == 4:#from automod2 and save as automod2-- cycle
        images=get_autodata2()
        readn='.uvf'
        saven='-automod2'
    for i in range(images.size):
      namer=images[i]+readn
      names=images[i]+saven
      print(namer,names)
      if not os.path.exists('%s.mod'% names) or step==4:
          difmap.sendline('obs %s' %namer)
          difmap.expect('0>')
          difmap.sendline('select i')
          difmap.expect('0>')
          if freq <=3 :
              difmap.sendline('mapsize 2048,0.4')
              difmap.expect('0>')
          elif freq >= 3.1 and freq <= 10:
              difmap.sendline('mapsize 2048,0.2')
              difmap.expect('0>')
          elif freq >=10.1:
              difmap.sendline('mapsize 2048,0.1')
              difmap.expect('0>')
          difmap.sendline('uvw 0,-1')
          difmap.expect('0>')
          modfcal(difmap,7,9)
          difmap.sendline('gscale')
          difmap.expect('0>') 
          while solint >= 2:
              difmap.sendline('modelfit 50')
              difmap.expect('0>',timeout=500)
              modfcal(difmap,5.5,5)
              apscal(difmap,solint)
              solint=solint/2
              print(solint)
          difmap.sendline('save %s' %names)
          difmap.expect('0>')
          print('done %s'%names)
      else:
          print('model already there, move on')
    difmap.sendline('quit')
    difmap.close()
    if os.path.isfile(logfile):
        os.remove(logfile)
        
def modfit2(freq): # mod files after mannual cleaning
    difmap = pexpect.spawn('difmap')
    difmap.waitnoecho
    difmap.expect('0>')
    p = re.compile(r'(difmap.log_?\d*)')
    logfile = p.findall(difmap.before.decode())[0]
    difmap.timeout = 8000000
    #images=get_uvmod()
    images=get_splt()
    for i in range(images.size):
      name2=images[i]+'.uvf'
      names=name2[:-4]+'-clnmod'
      print(name2)
      if not os.path.exists('%s.mod'% names):
          difmap.sendline('obs %s' %name2)
          difmap.expect('0>')
          difmap.sendline('select i')
          difmap.expect('0>')
          if freq <=3 :
              difmap.sendline('mapsize 2048,0.4')
              difmap.expect('0>')
          elif freq >= 3.1 and freq <= 10:
              difmap.sendline('mapsize 2048,0.2')
              difmap.expect('0>')
          elif freq >=10.1:
              difmap.sendline('mapsize 2048,0.1')
              difmap.expect('0>')
          difmap.sendline('uvw 0,-1')
          difmap.expect('0>')
          snr,rms,pkx,pky=getsnr(difmap)
          print(snr,rms,pkx,pky)
          nm=0
          while snr > 5.5:
              if nm > 12:
                  break
              else:
                  difmap.sendline('addcmp 0.1,true,%f,%f,true,0,false,1,false,0,true,0'%(pkx,pky))
                  difmap.expect('0>')
                  difmap.sendline('modelfit 50')
                  difmap.expect('0>',timeout=500)
                  snr,rms,pkx,pky=getsnr(difmap)
                  print(snr,rms,pkx,pky)
                  nm=nm+1
          difmap.sendline('save %s' %names)
          difmap.expect('0>')
          print('done %s'%names)
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

        

        
        
if __name__ == '__main__' :
    #path='/home/ykzhang/Scripts/BeSSel/BZ083B/'
    path='./ba114b/' # TODO SPLIT data location
    #J0203%2B1134, J0646%2B4451, J1354-0206, J1510%2B5702, J2129-1538, J2219-2719, J2321-0827
    os.chdir(path)
    difmap_image('C')
    #modfit1(3,1,300)  # adding models automatically
    #modfit2(1.4)
    # check()
    # debug()
    #check_mod('S',0)   #'' means original point fitting, for preview. 'r' means rmod results, for checking re
    # check_mod('X',0)
