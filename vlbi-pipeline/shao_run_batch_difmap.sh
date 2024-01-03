#!/usr/bin/env bash

for i in `ls $1`
do
    echo "processing $1/$i"
    python run_difmap.py $1/$i/
done