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


See [Usage](docs/usage/usage.rst) for more details.


## Contributing




Feel free to PR or suggestions! [Open an issue](https://github.com/SHAO-SKA/vlbi-pipeline/issues/new) or submit PRs.


## ENV

```bash
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

```

## Citation

## Selected publications that use vlbi-pipeline


Let us know if you use vlbi-pipeline in your publication or work and we'll list it here!
(sorted by date)


- Zhang Y, An T, Frey S, et al. J2102+6015: a young radio source at z = 4.575 [J/OL]. , 2021,
507(3): 3736-3744. DOI: 10.1093/mnras/stab2289.
- Cheng X, An T, Sohn B W, et al. Parsec-scale properties of eight Fanaroff-Riley type 0 radio
galaxies [J/OL]. , 2021, 506(2): 1609-1622. DOI: 10.1093/mnras/stab1388.
- An T, Mohan P, Zhang Y, et al. Evolving parsec-scale radio structure in the most distant
blazar known [J]. Nature Communications, 2020, 11(1): 1-8.
- Mohan P, An T, Yang J. The nearby luminous transient at2018cow: A magnetar formed in
a subrelativistically expanding nonjetted explosion [J]. The Astrophysical Journal Letters,
2020, 888(2): L24.
- Cheng X P, An T, Frey S, et al. Compact Bright Radio-loud AGNs. III. A Large VLBA Survey
at 43 GHz [J/OL]. , 2020, 247(2): 57. DOI: 10.3847/1538-4365/ab791f.
- An T, Salafia O S, Zhang Y, et al. East asia vlbi network observations of the tev gamma-ray
burst 190114c [J]. Science Bulletin, 2020, 65(4): 267-271.
- Zhang Y K, An T, Frey S. Fast jet proper motion discovered in a blazar at z=4.72 [J]. Science
Bulletin, 2020, 65(7): 525-530.
- Zhang Y K, An T, Wang A L, et al. VLBI observations of VIK J2318−3113, a quasar at z = 6.44
[J]. Astronomy Astrophysics, 2022, 662: L2

## License

[GPL © SHAO](LICENSE)