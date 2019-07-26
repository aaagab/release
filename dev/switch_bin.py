#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.9
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from ..dev.helpers import get_direpa_root, to_be_coded, create_symlink

from ..gpkgs import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell

def switch_bin(dy_app, args):
    pkg_name=args["switch_bin"][0]
    pkg_version=args["switch_bin"][1]
    
    direpa_bin=dy_app["direpa_bin"]
    filenpa_pkg_json=os.path.join(direpa_bin, pkg_name+"_data", pkg_version, pkg_name, "gpm.json")
    if os.path.exists(filenpa_pkg_json):
        dy_pkg=Json_config(filenpa_pkg_json).data

        filenpa_exec=os.path.join(os.path.dirname(filenpa_pkg_json), dy_pkg["filen_main"])
        filenpa_symlink=os.path.join(direpa_bin, dy_pkg["name"])

        create_symlink(dy_app["platform"], filenpa_exec, filenpa_symlink )
        msg.success("Bin '{}' switched to '{}'".format(pkg_name, pkg_version))
    else:
        msg.error("Not found '{}'".format(filenpa_pkg_json))
        sys.exit(1)
