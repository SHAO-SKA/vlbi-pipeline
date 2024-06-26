# VLBI-pipeline

## Usage of run_difmap

The following command will processing all vis fits file in the directory,
and also, there are two modes to choose, `clean` and `modfit`.
`clean` is the default mode, and `modfit` is the mode to do model fitting.

```bash
$ python run_difmap.py /the/directory/of/the/file.fits/
# do clean
$ python run_difmap.py /the/directory/of/the/file.fits/ clean
# do modfit
$ python run_difmap.py /the/directory/of/the/file.fits/ modfit
```