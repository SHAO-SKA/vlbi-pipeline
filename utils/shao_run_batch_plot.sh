#!/usr/bin/env bash

for i in `ls J*/*cln.fits`; do
    echo $i
    if echo $i | grep -q "S"; then
        python3 plot_VLBI_images.py  $i 3.2 1.2 20 30
    elif echo $i | grep -q "X"; then
        python3 plot_VLBI_images.py  $i 3.2 1.2 10 10
    elif echo $i | grep -q "U"; then
        python3 plot_VLBI_images.py  $i 3.2 1.2 10 10
    else
        python3 plot_VLBI_images.py  $i 3.2 1.2 20 10
    fi
done