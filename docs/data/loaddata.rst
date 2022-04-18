Load data
###################


Setup the enviroment
=========================

.. code-block:: bash

    $ source /home/app/astrosoft_leo/start_aips.rc
    $ source /home/app/astrosoft_leo/start_parseltongue.rc

.. code-block:: bash

    # load the data
    $ ParselTongue main.py ../data/ ba114a.idifits


running on computer node
================================


.. code-block:: bash

    $ srun -N 1 -n 1 -p hw  -w hw-x86-cpu10  ParselTongue run_tasks.py ../data/ ba114a.idifits