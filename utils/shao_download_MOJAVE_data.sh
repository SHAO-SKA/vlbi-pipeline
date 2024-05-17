#!/bin/bash

# print a tips for the use to input one parameter at least
if [ "$#" -eq 0 ];then
	echo "Please input a source name at lease"
	echo "Usage: shao_download_MOJAVE_data.sh 1156+295"
	echo "Or, download_type is gz by default"
	echo "Usage: shao_download_MOJAVE_data.sh 1156+295 download_type"
fi

if [ "$#" -eq 1 ];then
	echo "Downloading $1 data ..."
	mkdir $1
	cd $1
	wget https://www.cv.nrao.edu/MOJAVE/sourcepages/$1.shtml -O - | grep -oP '(?<=href=")[^"]+(?=")' | grep -i "\.gz" | xargs wget
	cd ..
fi
# if the parameter is two, then specify the second parameter
if [ "$#" -eq 2 ];then
	echo "Downloading $1 data ..."
	mkdir $1
	cd $1
	wget https://www.cv.nrao.edu/MOJAVE/sourcepages/$1.shtml -O - | grep -oP '(?<=href=")[^"]+(?=")' | grep -i "\.$2" | xargs wget
	cd ..
fi
