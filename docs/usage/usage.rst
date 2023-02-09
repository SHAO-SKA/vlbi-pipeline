Usage
###################


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

.. code-block:: bash

    # load the data and test on login node
    $ ParselTongue main.py ../data/ ba114a.idifits

running on single computer or login node
=============================================


.. code-block:: bash

    $ cd /ibo9000/VLBI/shao/vlbi-pipeline/
    # source the same environment
    $ ParselTongue main.py ../data/ ba114a.idifits --step2

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
    $ python3 rund_difmap.py CODE #code is where SPLIT data location 