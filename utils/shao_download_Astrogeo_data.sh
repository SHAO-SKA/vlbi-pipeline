#!/bin/bash

# Bash program to download UVDATA files from astrogeo website:
#Input source list file: 'source_list.txt'

for i in `cat source_list.txt`
do
    basedir=`pwd`
    sleep 5 # sleep for a while to avoid overloading the server
    echo Downloading ${i:0:10} data ...
    mkdir $i
    cd $i
    wget -nd -l0 -r -e robots=off -q -np -A "*_vis.fits" http://astrogeo.org/images/${i:0:10}/  --no-check-certificate
    cd $basedir
done
