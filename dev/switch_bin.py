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


from ..gpkgs.prompt import prompt_multiple
from ..gpkgs.json_config import Json_config
from ..gpkgs import message as msg

def switch_bin(direpa_bin, pkg_alias, pkg_uuid4, pkg_version, system):
    direpa_package=os.path.join(direpa_bin, pkg_alias+"_data")
    if not os.path.exists(direpa_package):
        msg.error("Not found '{}'".format(direpa_package), exit=1)

    if pkg_uuid4 is None:
        uuid4s=sorted(os.listdir(direpa_package))
        if len(uuid4s) == 1:
            pkg_uuid4=uuid4s[0]
        elif len(uuid4s) > 1:
            pkg_uuid4=prompt_multiple(uuid4s, title="Choose uuid4 for '{}'.".format(pkg_alias))

    direpa_uuid4=os.path.join(direpa_package, pkg_uuid4)

    filenpa_pkg_json=""
    if pkg_version == "latest":
        versions=[]
        for version in os.listdir(direpa_uuid4):
            if ro.Version_regex(version).match:
                versions.append(version)

        if not versions:
            msg.error("No versions are available for '{}' in '{}'".format(pkg_alias, direpa_uuid4), exit=1)
        pkg_version=filter_version(versions, "l.l.l")[0]
    
    filenpa_pkg_json=os.path.join(direpa_uuid4, pkg_version, pkg_alias, "gpm.json")

    if os.path.exists(filenpa_pkg_json):
        dy_pkg=Json_config(filenpa_pkg_json).data
        if "alias" in pkg_alias:
            pkg_alias=dy_pkg["alias"]
        else:
            pkg_alias=dy_pkg["name"]

        filenpa_exec=os.path.join(os.path.dirname(filenpa_pkg_json), dy_pkg["filen_main"])
        filenpa_symlink=os.path.join(direpa_bin, pkg_alias)

        create_symlink(system, filenpa_exec, filenpa_symlink )
        msg.success("Bin '{}' switched to '{}'".format(pkg_alias, pkg_version))
    else:
        msg.error("Not found '{}'".format(filenpa_pkg_json))
        sys.exit(1)
