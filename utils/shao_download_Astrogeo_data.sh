#!/bin/bash

# Bash program to download UVDATA files from astrogeo website:
#Input source list file: 'source_list.txt'

if [ "$#" -eq 0 ];then
	echo "Trying to find source_list.txt"
	if [ -f "./source_list.txt" ];then
		for i in `cat ./source_list.txt`
		do
		    basedir=`pwd`
		    sleep 5 # sleep for a while to avoid overloading the server
		    echo Downloading ${i:0:10} data ...
		    mkdir $i
		    cd $i
		    wget -nd -l0 -r -e robots=off -q -np -A "*_vis.fits" http://astrogeo.org/images/${i:0:10}/  --no-check-certificate
		    cd $basedir
		done
	else
		echo "!!!source list do not exist"
		echo "Try adding a source name directly, Like"
		echo "shao_download_Astrogeo_data.sh J1357-1744"
	fi
fi

if [ "$#" -eq 1 ];then
		    basedir=`pwd`
		    sleep 5 # sleep for a while to avoid overloading the server
		    echo Downloading $1 data ...
		    mkdir $1
		    cd $1
		    wget -nd -l0 -r -e robots=off -q -np -A "*_vis.fits" http://astrogeo.org/images/$1  --no-check-certificate
		    cd $basedir
fi
