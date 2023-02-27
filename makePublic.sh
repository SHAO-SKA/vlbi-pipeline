#!/usr/bin/env bash

cp -rv docs/conf.py ../vlbi-pipeline-public/docs/
cp -rv docs/index.rst ../vlbi-pipeline-public/docs/
cp -rv docs/Makefile ../vlbi-pipeline-public/docs/
cp -rv docs/data ../vlbi-pipeline-public/docs/
cp -rv docs/installation ../vlbi-pipeline-public/docs/
cp -rv docs/source ../vlbi-pipeline-public/docs/
cp -rv docs/usage ../vlbi-pipeline-public/docs/

cp -rv vlbi-pipeline/config.py ../vlbi-pipeline-public/vlbi-pipeline/
cp -rv vlbi-pipeline/main.py ../vlbi-pipeline-public/vlbi-pipeline/
cp -rv vlbi-pipeline/*_utils.py ../vlbi-pipeline-public/vlbi-pipeline/
cp -rv vlbi-pipeline/run_tasks.py ../vlbi-pipeline-public/vlbi-pipeline/
cp -rv vlbi-pipeline/utils.py ../vlbi-pipeline-public/vlbi-pipeline/

cp -rv setup.py ../vlbi-pipeline-public/
