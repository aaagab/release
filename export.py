#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0
# name: release
# license: MIT
import sys
import os
import shutil
from distutils.dir_util import copy_tree

direpa_source_app=os.path.dirname(os.path.realpath(__file__))

direpa_lib="/data/lib"
direpa_source_dst=os.path.join(direpa_lib, "release")
if os.path.exists(direpa_source_dst):
    shutil.rmtree(direpa_source_dst)

os.makedirs(direpa_source_dst)

copy_tree(direpa_source_app, direpa_source_dst)
shutil.rmtree(os.path.join(direpa_source_dst,".git"))
shutil.rmtree(os.path.join(direpa_source_dst,"__pycache__"))
os.remove(os.path.join(direpa_source_dst,".gitignore"))
