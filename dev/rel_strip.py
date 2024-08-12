#!/usr/bin/env python3
import json
import os
from pprint import pprint
import re

from .generate_db import generate_db

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.sort_separated import sort_separated
from ..gpkgs import shell_helpers as shell

def rel_strip(direpa_rel, filen_json_rel, pkg_aliases=[]):
    if len(pkg_aliases) == 0:
        pkg_aliases=os.listdir(direpa_rel)
    else:
        pkg_aliases=pkg_aliases

    packagesRemoved=False
    for pkg_alias in sorted(pkg_aliases):
        pprint(pkg_aliases)
        direpa_pkg=os.path.join(direpa_rel, pkg_alias)
        if os.path.exists(direpa_pkg) and os.path.isdir(direpa_pkg):
            versions=os.listdir(direpa_pkg)
            pprint(versions)
            if len(versions) > 1:
                versions=sort_separated(versions)
                versions.pop()
                for version in versions:
                    packagesRemoved=True
                    direpa_version=os.path.join(direpa_pkg, version)
                    shell.rmtree(direpa_version)
                    msg.success("package removed {} {}".format(pkg_alias, version))

    if packagesRemoved is True:
        generate_db(
            direpa_rel,
            filen_json_rel,
        )
