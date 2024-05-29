#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from math import sqrt, pi
import numpy as np
import matplotlib
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1.anchored_artists import (AnchoredSizeBar)
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy import wcs
from matplotlib.colors import SymLogNorm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Ellipse
from matplotlib.ticker import FormatStrFormatter

fp = FontProperties()
fp.set_size('x-large')

nature_colors = ['#DC000099', '#4DBBD599', '#00A08799', '#F39B7F99', '#8491B499', '#DC0000FF', '#3C5488FF']

# The function to calculating distance
def mas_pc(z):
    H0 = 71
    WM = 0.27
    WV = 0.73
    # initialize constants

    WR = 0.  # Omega(radiation)
    WK = 0.  # Omega curvaturve = 1-Omega(total)
    c = 299792.458  # velocity of light in km/sec
    Tyr = 977.8  # coefficent for converting 1/H into Gyr
    DTT = 0.5  # time from z to now in units of 1/H0
    DTT_Gyr = 0.0  # value of DTT in Gyr
    age = 0.5  # age of Universe in units of 1/H0
    age_Gyr = 0.0  # value of age in Gyr
    zage = 0.1  # age of Universe at redshift z in units of 1/H0
    zage_Gyr = 0.0  # value of zage in Gyr
    DCMR = 0.0  # comoving radial distance in units of c/H0
    DCMR_Mpc = 0.0
    DCMR_Gyr = 0.0
    DA = 0.0  # angular size distance
    DA_Mpc = 0.0
    DA_Gyr = 0.0
    kpc_DA = 0.0
    DL = 0.0  # luminosity distance
    DL_Mpc = 0.0
    DL_Gyr = 0.0  # DL in units of billions of light years
    V_Gpc = 0.0
    a = 1.0  # 1/(1+z), the scale factor of the Universe
    az = 0.5  # 1/(1+z(object))

    h = H0 / 100.
    # includes 3 massless neutrino species, T0 = 2.72528
    WR = 4.165E-5 / (h * h)
    WK = 1 - WM - WR - WV
    az = 1.0 / (1 + 1.0 * z)
    age = 0.
    n = 1000  # number of points in integrals
    for i in range(n):
        a = az * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        age = age + 1. / adot

    zage = az * age / n
    zage_Gyr = (Tyr / H0) * zage
    DTT = 0.0
    DCMR = 0.0

    # do integral over a=1/(1+z) from az to 1 in n steps, midpoint rule
    for i in range(n):
        a = az + (1 - az) * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        DTT = DTT + 1. / adot
        DCMR = DCMR + 1. / (a * adot)

    DTT = (1. - az) * DTT / n
    DCMR = (1. - az) * DCMR / n
    age = DTT + zage
    age_Gyr = age * (Tyr / H0)
    DTT_Gyr = (Tyr / H0) * DTT
    DCMR_Gyr = (Tyr / H0) * DCMR
    DCMR_Mpc = (c / H0) * DCMR

    ratio = 1.00
    x = sqrt(abs(WK)) * DCMR
    if x > 0.1:
        if WK > 0:
            ratio = 0.5 * (exp(x) - exp(-x)) / x
        else:
            ratio = sin(x) / x
    else:
        y = x * x
        if WK < 0:
            y = -y
        ratio = 1. + y / 6. + y * y / 120.
    DCMT = ratio * DCMR
    DA = az * DCMT
    DA_Mpc = (c / H0) * DA
    kpc_DA = DA_Mpc / 206.264806
    DA_Gyr = (Tyr / H0) * DA
    DL = DA / (az * az)
    DL_Mpc = (c / H0) * DL
    DL_Gyr = (Tyr / H0) * DL
    Mpc_cm = 3.08568 * 10 ** 24
    DL_cm = DL_Mpc * Mpc_cm

    ratio = 1.00
    x = sqrt(abs(WK)) * DCMR
    if x > 0.1:
        if WK > 0:
            ratio = (0.125 * (exp(2. * x) - exp(-2. * x)) -
                     x / 2.) / (x * x * x / 3.)
        else:
            ratio = (x / 2. - sin(2. * x) / 4.) / (x * x * x / 3.)
    else:
        y = x * x
        if WK < 0:
            y = -y
        ratio = 1. + y / 5. + (2. / 105.) * y * y
    VCM = ratio * DCMR * DCMR * DCMR / 3.
    V_Gpc = 4. * pi * ((0.001 * c / H0) ** 3) * VCM

    # DL_cm='%e'% DL_cm
    return kpc_DA


def pix2word(h, xy):
    """
    Make a function opposite to 'world2pix'
    for converting relative WCS coordinates into pixel coordinates:

    :param h:
    :param xy:
    :return:
    """
    x, y = xy
    x = h['cdelt1'] * 3.6E6 * (x - h['crpix1'])
    y = h['cdelt2'] * 3.6E6 * (y - h['crpix2'])
    return x, y


def W2w(h, w=()):
    """
    Make a function to find the lower and upper limits of X-axis and Y-axis
    in WCS 'mas' units for plotting (left, right, bottom, top):

    :param h:
    :param w:
    :return:
    """
    if len(w) == 4:
        x0, x1, y0, y1 = w
    else:
        x0, y0 = 0, 0
        x1, y1 = h['naxis1'], h['naxis2']
    x0, y0 = pix2word(h, (x0, y0))
    x1, y1 = pix2word(h, (x1, y1))
    w = x0, x1, y0, y1
    return w


# Open the fits image file and get the image data and header:
# filename='201402c-cln.fits'
if len(sys.argv) != 6:
    print("==================================================================================")
    print(' Usage: python3 plot_VLBI_images.py filename z rms k pc')
    print('        python3 plot_VLBI_images.py J0008+1415/201402c-cln.fits 3.2 1.5 20 10')
    print("==================================================================================")
    exit()

filename = sys.argv[1]
print('Processing ' + filename)
z = float(sys.argv[2])
rms = float(sys.argv[3])
k = int(sys.argv[4])
pc_input = int(sys.argv[5])

hdu = fits.open(filename)
h = hdu[0].header
freq = h['CRVAL3'] / 1000000000  # GHz

#ff = ('output/%s-%s-%dGHz.pdf' %
ff = ('output/%s-%s-%dGHz.png' %
      (filename.replace('/', '-'), h['OBJECT'], freq))
if not os.path.exists(ff):
    img = hdu[0].data[0, 0, :, :]
    img = img * 1000

    # Define the plot environment:
    fig, ax = plt.subplots(figsize=(7, 5))

    # Set figure size:
    # fig.set_size_inches(6,7)

    # Take the lower and upper limits of X- and Y-axes from image in WCS 'mas' units:
    w = W2w(h)

    # Plot the image in colormap:
    rms = rms * np.median(abs(img - np.median(img)))  # in units of Jy/beam
    print(rms)
    # The symmetrical logarithmic scale is logarithmic in both the positive and negative directions from the origin.
    # Since the values close to zero tend toward infinity, there is a need to have a range around zero that is
    # linear. The parameter 'linthresh' allows the user to specify the size of this range (-linthresh, linthresh).
    #pcm = ax.imshow(img, norm=SymLogNorm(linthresh=10 * rms), extent=w, origin='lower', cmap='inferno', interpolation='none')
    pcm = ax.imshow(img, norm=SymLogNorm(linthresh= 10* rms,vmin=-10,vmax=1200), extent=w, origin='lower', cmap='inferno', interpolation='none')
    #pcm = ax.imshow(img, norm=SymLogNorm(linthresh=10 * rms), extent=w, origin='lower', cmap='inferno', interpolation='none')
    #pcm = ax.imshow(img, extent=w, origin='lower', cmap='inferno', interpolation='none',vmin=1,vmax=128)

    # Plot the image in contours:
    #levs_positive = 3 * rms * np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    levs_positive = 3 * rms * np.array([1, 2, 4, 8, 16, 32, 64, 128, 256,400])
    levs_negative = 3 * rms * np.array([-1])
    ax.contour(img, levs_positive, extent=w,
               linestyles='solid', linewidths=0.8, colors='black')
    ax.contour(img, levs_negative, extent=w,
               linestyles='dashed', linewidths=0.5, colors='r')
    ax.set_xlabel('Relative Right Ascension (mas)', fontsize=20)
    ax.set_ylabel('Relative Declination (mas)', fontsize=20, labelpad=0.01)
    ax.set_aspect('equal')

    # Set the color bar:
    #cbar = fig.colorbar(pcm, aspect=25,vmin=1,vmax=1024)
    cbar = fig.colorbar(pcm, aspect=25)
    # cbar = fig.colorbar(pcm,fraction=0.046, pad=0.03,aspect=25)
    cbar.ax.minorticks_off()  # IMPORTANT
    cbar.ax.tick_params('both', direction='in', right=True,
                        top=True, which='both', labelsize=18)
    #cbar.set_ticks([1, 2, 4, 8, 16, 32, 64, 128])
    #cbar.set_ticklabels([1, 2, 4, 8, 16, 32, 64, 128])
    cbar.set_ticks([-5, 0, 5, 50, 250])
    cbar.set_ticklabels([-5, 0, 5, 50, 250])
    cbar.ax.set_position([0.88, 0.08, 0.2, 0.9])
    cbar.set_label('mJy/beam', fontsize=20)
    # ax.annotate('Jy/beam',xy=(0.96,0.6),rotation=90,xycoords='figure fraction')

    # Set axes position on the figure frame: left,bottom,right,top
    ax.set_position([-0.09, 0.08, 0.95, 0.9])
    ax.tick_params('both', direction='in', right=True, top=True, which='both')
    ax.minorticks_on()

    # set the length of minor and major ticks
    plt.tick_params(which='major', length=6, color='k')
    plt.tick_params(which='minor', length=3, color='k')

    # Specify tick label (value) font size
    ax.tick_params(axis='both', which='major', labelsize=20)

    # set the format of the major tick label
    # It should be similar to C-programming format syntex.
    # Use 'd' for decimal, 'f' for float, and 's' for string valued ticks.
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%d'))

    # Set the values ranges for x and y axes:
    k = k
    w = (k, -k, -k, k)
    ax.set_xlim(w[0], w[1])
    ax.set_ylim(w[2], w[3])

    # Draw beam:
    b = (w[0] - 1.5 * h['bmaj'] * 3.6E6, w[2] + 1.5 * h['bmaj']
         * 3.6E6, h['bmaj'] * 3.6E6, h['bmin'] * 3.6E6, h['bpa'])
    e = Ellipse(xy=(k - b[3], -k + b[2] / 1.5), width=b[2],
                height=b[3], angle=90 - b[4], ec='k', facecolor='grey')
    ax.add_artist(e)
    bmaj = h['bmaj'] * 3.6E6
    bmin = h['bmin'] * 3.6E6
    bpa = h['bpa']
    para_file = 'output/' + filename.replace('/','-') + '.txt'
    fp_para = open(para_file, 'w')
    fp_para.write('bmaj, bmin, bpa\n')
    fp_para.write(str(bmaj) + ',' + str(bmin) + ',' + str(bpa) + '\n')

    # Write texts on the plot:
    #ax.annotate(h['OBJECT'], xy=(0.15, 0.91), xycoords='figure fraction', color='w', fontsize=15)
    #ax.annotate('%.1f GHz' % freq, xy=(0.38, 0.91),
    #ax.annotate('%.1f GHz' % freq, xy=(0.15, 0.98), xycoords='figure fraction', color='w', fontsize=15)
    #ax.annotate(h['OBJECT'], xy=(0.15, 0.91), xycoords='figure fraction', color='w', fontsize=15)
    #ax.annotate('date: %s' % h['date-obs'], xy=(0.15, 0.93), xycoords='figure fraction', color='w', fontsize=15)
    ax.annotate('%s %.2f GHz' % (h['date-obs'], freq), xy=(0.15, 0.96), xycoords='figure fraction', color='w', fontsize=18,
bbox=dict(boxstyle="round,pad=0.5", #  the box style and the padding inside the box
                       fc=nature_colors[0], #  the fill color of the box
                       ec="black", #  the edge color of the box
                       alpha=0.8)) #  the transparency of the box
    #ax.annotate('%.1f GHz' % freq, xy=(0.48, 0.92), xycoords='figure fraction', color='w', fontsize=15)
    #ax.annotate('peak=%d mJy/beam' % round(np.max(img)), xy=(0.15, 0.88), xycoords='figure fraction', color='w', fontsize=18)
    #ax.annotate('rms=%.2f mJy/beam' % round(rms, 2), xy=(0.15, 0.83), xycoords='figure fraction', color='w', fontsize=18)

    def get_z(filename):
        bb = {}
        a = open('redshift.txt')
        aa = a.readlines()
        for i in aa[1:]:
            # print(i)
            name = i.split(',')[0]
            z = i.split(',')[1].rstrip('\n').lstrip()
            bb[name] = z
        return bb

    # all_z = get_z('redshift.txt')

    # z = all_z[filename.split('/')[0]]
    z = float(z)
    # z=3.20

#    ax.annotate('z=%.2f' % z, xy=(0.53, 0.91), xycoords='figure fraction', color='w', fontsize=15)

    #pc = 50 / mas_pc(z)
    #scalebar = AnchoredSizeBar(ax.transData, pc, '50 pc', 'lower center', pad=1, color='w', frameon=False, size_vertical=0.3, sep=5, prop=fp)
    #pc = 5 / mas_pc(z)
    #scalebar = AnchoredSizeBar(ax.transData, pc, '5 pc', 'lower center', pad=1, color='w', frameon=False, size_vertical=0.3, sep=5, prop=fp)
    pc = pc_input / mas_pc(z)
    scalebar = AnchoredSizeBar(ax.transData, pc, '%d pc'%pc_input, 'lower center', pad=1, color='w', frameon=False, size_vertical=0.03, sep=5, prop=fp)
    ax.add_artist(scalebar)

    plt.tick_params(labelsize=20)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    #[label.set_fontname('Times New Roman') for label in labels]

    # Show the bad pixels or NaN valued pixels as white spot:
    current_cmap = matplotlib.cm.get_cmap()
    current_cmap.set_bad(color='white')
    #fig.savefig('output/%s-%s-%dGHz.pdf' % (filename.replace('/',
    #fig.savefig('output/%s-%s-%dGHz.png' % (filename.replace('/', '-'), h['OBJECT'], freq), bbox_inches='tight', dpi=600)
    fig.savefig('output/%s.png' % (filename.replace('/', '-')), bbox_inches='tight', dpi=600)
else:
    print('File exists')

# To close plot window:
plt.close()
# To display the image on plot window:
# plt.show()