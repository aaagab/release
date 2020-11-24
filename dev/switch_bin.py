#!/usr/bin/env python3
import contextlib
import os
from pprint import pprint
import re
import shlex
import shutil
import subprocess
import sys

from . import regex_obj as ro
from .filter_version import filter_version
from .helpers import to_be_coded, create_symlink



from ..gpkgs.json_config import Json_config
from ..gpkgs import message as msg

def switch_bin(direpa_bin, pkg_name, pkg_version, system):
    direpa_package=os.path.join(direpa_bin, pkg_name+"_data")
    if not os.path.exists(direpa_package):
        msg.error("Not found '{}'".format(direpa_package), exit=1)

    filenpa_pkg_json=""
    if pkg_version == "latest":
        versions=[]
        for version in os.listdir(direpa_package):
            if ro.Version_regex(version).match:
                versions.append(version)

        if not versions:
            msg.error("No versions are available for '{}' in '{}'".format(pkg_name, direpa_package), exit=1)
        pkg_version=filter_version(versions, "l.l.l")[0]

        # filenpa_pkg_json=os.path.join(direpa_package, pkg_version, pkg_name, "gpm.json")
    # elif pkg_version == "beta":
        # filenpa_pkg_json=os.path.join(direpa_package, "beta", "gpm.json")
    # else:
    
    filenpa_pkg_json=os.path.join(direpa_package, pkg_version, pkg_name, "gpm.json")

    if os.path.exists(filenpa_pkg_json):
        dy_pkg=Json_config(filenpa_pkg_json).data

        filenpa_exec=os.path.join(os.path.dirname(filenpa_pkg_json), dy_pkg["filen_main"])
        filenpa_symlink=os.path.join(direpa_bin, dy_pkg["name"])

        create_symlink(system, filenpa_exec, filenpa_symlink )
        msg.success("Bin '{}' switched to '{}'".format(pkg_name, pkg_version))
    else:
        msg.error("Not found '{}'".format(filenpa_pkg_json))
        sys.exit(1)
