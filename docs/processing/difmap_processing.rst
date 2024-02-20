Processing using Difmap
################################

Checking data
===============

We can using shao_get_visibilities to check how many visibilities owned by the data,
then decide whether use it or not

.. code:: bash

    python3 shao_get_visibilities.py J0646-20001023S-cln.uvf


Single file 
================


.. code:: bash

    python run_difmap.py /the/directory/of/the/file.fits/

All processing data will be stored in the same directory.


Multiple files
================    


