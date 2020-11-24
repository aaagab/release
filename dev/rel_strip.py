#!/usr/bin/env python3
import json
import os
from pprint import pprint
import re
import shutil
import sys

from .generate_db import generate_db

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.sort_separated import sort_separated

def rel_strip(direpa_rel, filen_json_rel, pkg_names):
    if pkg_names:
        pkg_names=pkg_names
    else:
        pkg_names=os.listdir(direpa_rel)

    packagesRemoved=False
    for pkg_name in sorted(pkg_names):
        direpa_pkg=os.path.join(direpa_rel, pkg_name)
        if os.path.exists(direpa_pkg) and os.path.isdir(direpa_pkg):
            versions=os.listdir(direpa_pkg)
            if len(versions) > 1:
                versions=sort_separated(versions)
                versions.pop()
                for version in versions:
                    packagesRemoved=True
                    direpa_version=os.path.join(direpa_pkg, version)
                    shutil.rmtree(direpa_version)
                    msg.success("package removed {} {}".format(pkg_name, version))

    if packagesRemoved is True:
        generate_db(
            direpa_rel,
            filen_json_rel,
        )
