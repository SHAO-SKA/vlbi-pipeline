#!/usr/bin/env bash

for i in `ls J*/*cln.fits`; do
    echo $i
    if echo $i | grep -q "S"; then
        python3 shao_plot_VLBI_images.py  $i 3.2 1.2 20 30
        python3 shao_plot_VLBI_images.py  $i --redshift 3.2 --rms 1.2 --pixels 20 --parsecs 30 --sigma 3
    elif echo $i | grep -q "X"; then
        python3 shao_plot_VLBI_images.py  $i --redshift 3.2 --rms 1.2 --pixels 20 --parsecs 10 --sigma 3
    elif echo $i | grep -q "U"; then
        python3 shao_plot_VLBI_images.py  $i --redshift 3.2 --rms 1.2 --pixels 20 --parsecs 10 --sigma 3
    else
        python3 shao_plot_VLBI_images.py  $i --redshift 3.2 --rms 1.2 --pixels 20 --parsecs 10 --sigma 3
    fi
done