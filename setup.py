#! /usr/bin/env python3
"""
Setup for shao_vlbi_pipeline
"""
import os
import sys
from setuptools import setup

__vlbi_pipeline_name__ = "shao_vlbi_pipeline"
__vlbi_pipeline_version__ = get_version()
__vlbi_pipeline_author__ = "Shaoguang Guo"
__vlbi_pipeline_author_email__ = "sgguo@shao.ac.cn"


def read(fname):
    """Read a file"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    """Get the version number of shao_plot_dstat"""
    import vlbi-pipeline as vlbipipeline
    return vlbipipe.__version__


reqs = ['scipy>=0.16',
        'healpy >=1.10',
        'six>=1.11']

if sys.version_info < (3, 0):
    reqs.append('matplotlib>=3.1.2,<3.2.2')
else:
    reqs.append('matplotlib>=3.2.2')

setup(
    name=__vlbi_pipeline_name__,
    version=__vlbi_pipeline_version__,
    author=__vlbi_pipeline_author__,
    author_email=__vlbi_pipeline_author_email__,
    description="A simplest pipeline for VLBI data using AIPS.",
    url="https://github.com/SHAO-SKA/vlbi-pipeline",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=['shao_vlbi_pipeline'],
    install_requires=reqs,
    data_files=[('data/DAY1.CH0.UV.FITS')],
    python_requires='>=2.7',
    scripts=['scripts/shao_vlbi_pipeline']
)
