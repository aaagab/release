#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: release
# license: MIT
import sys
import os
import shutil
from distutils.dir_util import copy_tree

app_name="release"
direpa_lib="/data/lib"

version=""
if len(sys.argv) > 1:
    version=sys.argv[1]

direpa_source_app=""
if version != "":
    direpa_source_app=os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "rel",
        version,
        app_name
    )

    if not os.path.exists(direpa_source_app):
        print("'{}' not found, export cancelled.".format(direpa_source_app))
        sys.exit(1)

else:
    direpa_source_app=os.path.dirname(os.path.realpath(__file__))

direpa_source_dst=os.path.join(direpa_lib, app_name)
if os.path.exists(direpa_source_dst):
    shutil.rmtree(direpa_source_dst)

os.makedirs(direpa_source_dst)
copy_tree(direpa_source_app, direpa_source_dst)
if not version:
    shutil.rmtree(os.path.join(direpa_source_dst,".git"))
    shutil.rmtree(os.path.join(direpa_source_dst,"__pycache__"))
    os.remove(os.path.join(direpa_source_dst,".gitignore"))
