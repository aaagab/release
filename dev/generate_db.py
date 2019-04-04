#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.4.0
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from dev.helpers import get_direpa_root, to_be_coded
from dev.refine import get_paths_to_copy, copy_to_destination
import dev.regex_obj as ro

import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean
from modules.json_config.json_config import Json_config
import modules.shell_helpers.shell_helpers as shell

# mockpackage 0.2.2
# mockpackage 0.2.3
# mockpackage beta

def generate_db(dy_rel):
    pkgs={}
    for pkg_name in sorted(os.listdir(dy_rel["direpa_release"])): 
        if pkg_name != "db.json":
            direpa_pkg=os.path.join(dy_rel["direpa_release"], pkg_name)
            for version in os.listdir(direpa_pkg):
                filenpa_gpm=os.path.join(direpa_pkg, version, pkg_name, "gpm.json")
                if os.path.exists(filenpa_gpm):
                    dy_pkg=Json_config(filenpa_gpm).data
                    pkg_id="{}|{}|{}".format(dy_pkg["uuid4"], dy_pkg["name"], dy_pkg["version"])
                    pkgs[pkg_id]=[]
                    for dep in dy_pkg["deps"]:
                        pkgs[pkg_id].append(dep)
                else:
                    msg.warning("'{}' does not exists".format(filenpa_gpm))

    filenpa_db=os.path.join(dy_rel["direpa_release"], "db.json")
    with open(filenpa_db, "w") as f:
        Json_config(filenpa_db).set_file_with_data(pkgs)
