#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.3.0
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from ..dev.helpers import get_direpa_root, to_be_coded
from ..dev.refine import get_paths_to_copy, copy_to_destination

from ..modules.message import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell

# mockpackage 0.2.2
# mockpackage 0.2.3
# mockpackage beta

def generate_db(dy_app):
    db={}
    pkgs={}
    uuid4s={}
    for pkg_name in sorted(os.listdir(dy_app["direpa_release"])): 
        if pkg_name != dy_app["filen_json_repo"]:
            direpa_pkg=os.path.join(dy_app["direpa_release"], pkg_name)
            for version in os.listdir(direpa_pkg):
                filenpa_gpm=os.path.join(direpa_pkg, version, pkg_name, "gpm.json")
                if os.path.exists(filenpa_gpm):
                    dy_pkg=Json_config(filenpa_gpm).data
                    if dy_pkg["uuid4"] in uuid4s:
                        if dy_pkg["name"] != uuid4s[dy_pkg["uuid4"]]:
                            msg.app_error("Failed Insert '{}' with uuid4 '{}' ".format(
                                dy_pkg["name"], dy_pkg["uuid4"]),
                                "In db[uuid4s] same uuid4 has name '{}'".format(uuid4s[dy_pkg["uuid4"]]),
                                "You can't have same uuid for different names.")
                            sys.exit(1)
                    else:
                        uuid4s.update({dy_pkg["uuid4"]: dy_pkg["name"]})
                    pkg_id="{}|{}|{}".format(dy_pkg["uuid4"], dy_pkg["name"], dy_pkg["version"])
                    pkgs[pkg_id]=[]
                    for dep in dy_pkg["deps"]:
                        pkgs[pkg_id].append(dep)
                else:
                    msg.warning("'{}' does not exists".format(filenpa_gpm))

    filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    db.update({"pkgs": pkgs, "uuid4s": uuid4s})
    with open(filenpa_json_repo, "w") as f:
        Json_config(filenpa_json_repo).set_file_with_data(db)
