Calculate proper motion and plot the result
############################################

This is a step by step guide to calculate proper motion and plot the result.

get the parameters without errbar 
====================================

First , make sure you gather all the model fit parameters from the model fit result.
The parameters files are stored in the file with the name of `JXXXX-XXXX-mod.mod` in the model fit result directory. 

You can type the following command to get the parameters from the model fit result.
The output file will be stored in the command directory with the name of `pm-JXXXX.txt`.

.. code-block:: bash

    $ python shao_get_parameters-pm.py  /the/path/of/mod/directory/
    # for example
    $ python shao_get_parameters-pm.py lcz/mod/J0539/
    # it will generate pm-J0539.txt in the current directory


Get the coresize with or without the Jet
==========================================

Running the following command to get the coresize with or without the Jet.

.. code-block:: bash

    $ python shao_get_parameters-coresize.py  /the/path/of/mod/directory/
    # for example
    $ python shao_get_parameters-coresize.py lcz/mod/J0539/
    # it will generate coresize-J0539.txt and coresize-J0539-C.txt in the current directory


Get all the parameters with errorbar from model fits file 
==========================================================

Running the following command to get all the parameters with errorbar from model fits file.

.. code-block:: bash

    $ python get-parameters-propermotion.py  /the/path/of/modelfit/directory/
    # for example
    $ python get-parameters-propermotion.py  /lcz/modelfits/J0539-2839/
    # it will generate propermotion-J0539-X.txt in the current directory

Calculate the proper motion error 
===================================

Running the following command to calculate the proper motion error, 
using the parameters with errorbar from model fits file, the mod file.

.. code-block:: bash

    $ python shao_get_parameters-pm-witherror.py  JXXXX
    # for example
    $ python shao_get_parameters-pm-witherror.py  J0539
    # it will generate pm-J0539-X-errorbar.txt in the current directory



Plot the proper motion
=======================

Running the following command to plot the proper motion.
The output file will be stored in the command directory with the name of `pm-JXXXX-Y.png`,
where Y is the band(X by defalut) .

.. code-block:: bash

    $ python plot_propermotion.py pm-JXXXX-Y-errorbar.txt
    # for example
    $ python3 plot_propermotion.py pm-J0539-X-errorbar.txt 
