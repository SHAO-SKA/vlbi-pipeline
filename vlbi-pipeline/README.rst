VLBI-pipeline Usage
#######################


Setup the enviroment
=========================

on CRATIV
---------------

.. code-block:: bash

    $ source ~/AIPS31DECC20/LOGIN.SH
    $ source /usr/local/astrosoft/start_parseltong.rc


on CSRC-P
---------------------------

.. code-block:: bash

    $ source /home/app/astrosoft_leo/start_aips.rc
    $ source /home/app/astrosoft_leo/start_parseltongue.rc
    $ export PYTHONPATH=$PYTHONPATH:/home/app/astrosoft_leo/parseltongue-3.0/share/parseltongue/python/:/home/app/astrosoft_leo/Obit-22JUN10m/python/

.. code-block:: bash

    # load the data and test on login node
    $ ParselTongue main.py ../data/ ba114a.idifits

running on single computer or login node
=============================================


.. code-block:: bash

    $ cd /the/path/of/vlbi-pipeline/
    # source the same environment
    $ ParselTongue main.py --filepath /data/VLBI/VLBA/br240/br240a/ --fitsfile  br240a.idifits --step1
    $ ParselTongue main.py --filepath /data/VLBI/VLBA/br240/br240a/ --fitsfile  br240a.idifits --step2
    $ ParselTongue main.py --filepath /data/VLBI/VLBA/br240/br240a/ --fitsfile  br240a.idifits --step3


.. note::information

    $ ParselTongue main.py --filepath /data/VLBI/VLBA/br240/br240a/ --fitsfile  br240a.idifits --step3 > br240a-log.txt
    will save all the output in terminal

running on computer node
================================


.. code-block:: bash

    $ cd /ibo9000/VLBI/shao/vlbi-pipeline/
    # source the same environment and test on the compute node
    $ srun -N 1 -n 1 -p hw  -w hw-x86-cpu14  source /home/app/astrosoft_leo/start_parseltongue.rc;source /home/app/astrosoft_leo/start_parseltongue.rc;  ParselTongue main.py ../data/ ba114a.idifits


running difmap
================================


.. code-block:: bash

    # source the same environment and test on the compute node
    $ python3 run_difmap.py CODE #code is where SPLIT data location 

Usage of run_difmap on instance
==================================

The following command will processing all vis fits file in the directory,
and also, there are two modes to choose, `clean` and `modfit`.
`clean` is the default mode, and `modfit` is the mode to do model fitting.


.. code:: bash

    $ python run_difmap.py /the/directory/of/the/file.fits/
    # do clean
    $ python run_difmap.py /the/directory/of/the/file.fits/ clean
    # do modfit
    $ python run_difmap.py /the/directory/of/the/file.fits/ modfit