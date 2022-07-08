# vlbi-pipeline

VLBI Data Processing Pipeline.

## Background

Simplest VLBI data processing pipeline.

## Install

This software depends upon the following software:

- AIPS
- ParselTongue
- Obit

See [Installation](docs/installation) for more details.

## Usage

Make sure to set the **AIPS_NUMBER** in config.py at first.




## Contributing




Feel free to PR or suggestions! [Open an issue](https://github.com/SHAO-SKA/vlbi-pipeline/issues/new) or submit PRs.


## ENV

#!/usr/bin/env bash
# User specific aliases and function
module use /home/software/modulefiles/
module load python/cpu-2.7.14
unset PYTHONPATH

#export PATH=$PATH:/usr/local/astrosoft/anaconda3/bin/
#conda initial
#conda activate virtual-py39



#export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/pgplot
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/astrosoft/funtools/lib
#export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/astrosoft/funtools/lib
#export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/astrosoft/CASA/casa-release-4.5.2-el6/lib/
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/astrosoft/CASA/casa-release-4.5.2-el6/lib/



/ibo9000/VLBI/astrosoft/parseltongue-3.0/bin/ParselTongue \
/home/ykzhang/zykdata/VLBA-pipeline/ba114a-pipeline.py 




## License

[GPL © SHAO](LICENSE)