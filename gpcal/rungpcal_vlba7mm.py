

import gpcal as gp

import timeit


# AIPS user ID number for ParselTongue.
aips_userno = 122


# The working directory where the input UVFITS and image fits files are located.
direc = '/home/leo/gpcal/examples/vlba_7mm/'


# The data name. The input files should have the names like dataname.sourcename.uvf and dataname.sourcename.fits (e.g., bl229ae.u.edt.OJ287.uvf).
dataname = 'bm413i.q.edt.'

# The list of calibrators which will be used for an initial D-term estimation using the similarity assumption.
calsour = ['0235+164', '0420-014', '0716+714', 'OJ287', '1156+295', '1510-089', '1749+096']

# The list of the number of CLEAN sub-models for calsour.
cnum = [1, 3, 3, 2, 2, 2]

# The list of booleans specifying whether the sub-model division will be done automatically or manually.
autoccedt = [True] + [False] * (len(calsour) - 1)


# Perform instrumental polarization self-calibraiton.
selfpol = True

# Iterate 10 times of instrumental polarization self-calibraiton.
selfpoliter = 10

# Mapsize for CLEAN in Difmap.
ms = 2048

# Pixelsize for CLEAN in Difmap.
ps = 0.04

# Uvbin for CLEAN in Difmap.
uvbin = 0

# Uv power-law index for CLEAN in Difmap.
uvpower = -1

# Perform CLEAN until the peak intensity within the CLEAN windows reach the map rms-noise.
dynam = 1

# The list of calibrators which will be used for additional D-term estimation using instrumental polarization self-calibration. This list does not have to be the same as calsour.
polcalsour = ['0235+164', '3C111', '0420-014', '3C120', '0716+714', 'OJ287', '1156+295', '1510-089', '3C345', '1749+096', 'BLLAC']

# The list of sources to which the best-fit D-terms will be applied.
source = ['0235+164', '3C84', '3C111', '0420-014', '3C120', '0716+714', 'OJ287', '1156+295', '3C273', '1510-089', '3C345', 'MKN501', '1749+096', 'BLLAC']

# Perform additional self-calibration with CALIB in Difmap.
selfcal = True

# CALIB parameters.
soltype = 'L1R'
solmode = 'A&P'
solint = 10./60.
weightit = 1


# Draw vplots, fitting residual plots, and field-rotation angle plots.
vplot = True
resplot = True
parplot = True

# Draw D-term plots for each IF separately.
dplot_IFsep = True

# Output the figures in the format of png.
filetype = 'png'


# The real and imaginary parts of all D-terms are assumed to be within 50%.
Dbound = 0.5

# The source-polarization terms for the D-term estimation using the similarity assumption are assumed to be less than 500%. 
Pbound = 5.


# The D-term plots will be shown for ranges of (-15%, 15%) for both the real and imaginary parts.
drange = 15.



time1 = timeit.default_timer()

# Load the GPCAL class POLCAL using the above parameters.
obs = gp.polcal(aips_userno, direc, dataname, calsour, source, cnum, autoccedt, Dbound = Dbound, Pbound = Pbound, \
               solint = solint, solmode = solmode, soltype = soltype, weightit = weightit, dplot_IFsep = dplot_IFsep, \
               drange = drange, polcalsour = polcalsour, ms = ms, ps = ps, uvbin = uvbin, uvpower = uvpower, dynam = dynam, selfpoliter = selfpoliter, \
               selfcal=selfcal, vplot=vplot, resplot=resplot, parplot = parplot, selfpol=selfpol, filetype = filetype)

# Run GPCAL.
obs.dtermsolve()


time2 = timeit.default_timer()


# Print time elapsed for different processes.
print('Time elapsed for AIPS-related processes = {:d} seconds.\nTime elapsed for Difmap-related processes = {:d} seconds.\nTime elapsed for GPCAL-related processes = {:d} seconds.\nTotal time elapsed = {:d}'\
      .format(int(round(obs.aipstime)), int(round(obs.difmaptime)), int(round((time2 - time1) - obs.aipstime - obs.difmaptime - obs.gpcaltime)), int(round(time2 - time1))))

