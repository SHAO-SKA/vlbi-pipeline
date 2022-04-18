Load data
###################


Setup the enviroment
=========================

.. code-block:: bash

    $ source /home/app/astrosoft_leo/start_aips.rc
    $ source /home/app/astrosoft_leo/start_parseltongue.rc

.. code-block:: bash

    # load the data and test on login node
    $ ParselTongue main.py ../data/ ba114a.idifits


running on computer node
================================


.. code-block:: bash

    $ cd /ibo9000/VLBI/shao/vlbi-pipeline/
    $ srun -N 1 -n 1 -p hw  -w hw-x86-cpu14  source /home/app/astrosoft_leo/start_parseltongue.rc;source /home/app/astrosoft_leo/start_parseltongue.rc;  ParselTongue main.py ../data/ ba114a.idifits