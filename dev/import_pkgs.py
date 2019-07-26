#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.7
# name: release
# license: MIT
import os, sys
from pprint import pprint
import shutil

from ..modules.json_config.json_config import Json_config
from ..modules.prompt.prompt import prompt_multiple
from ..modules.message import message as msg
from ..modules.prompt.prompt import prompt_boolean

from .get_pkg_from_db import get_pkg_from_db
from .search import search
from .helpers import is_pkg_git, get_direpa_root, get_pkg_id
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from .check_pkg_integrity import check_pkg_integrity
from ..gpkgs.sort_separated import sort_separated

# ./__init__.py -i message,a.a.a prompt

def import_pkgs(dy_app):
    if is_pkg_git():
        filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
        db=Json_config(filenpa_json_repo).data

        direpa_root=get_direpa_root()
        # direpa_pkgs=os.path.join(direpa_root, dy_app["diren_pkgs"])
        # os.makedirs(direpa_pkgs, exist_ok=True)
        pkg_filters=dy_app["args"]["import_pkgs"]
        for pkg_filter in pkg_filters:
            chosen_pkg=get_pkg_from_db(db, dy_app, pkg_filter)
            if chosen_pkg is None:
                continue         
            direpa_src=os.path.join(dy_app["direpa_release"], chosen_pkg["name"], chosen_pkg["version"], chosen_pkg["name"])
            direpa_dst=os.path.join(direpa_root, dy_app["diren_pkgs"], chosen_pkg["name"])
            filenpa_dst_root=os.path.join(direpa_root, dy_app["filen_json_app"])

            # check pkgs integrity
            check_pkg_integrity(dy_app, direpa_root)

            check_pkg_integrity(dy_app, direpa_src)

            if os.path.exists(direpa_dst):
                check_pkg_integrity(dy_app, direpa_dst)

            conf_app=Json_config(filenpa_dst_root)

            to_install=True
            delete_index=""

            for d, dep in enumerate(conf_app.data["deps"]):
                ex_uuid4, ex_name, ex_version, ex_bound = dep.split("|")

                if chosen_pkg["name"] == ex_name:
                    msg.warning("'{}' already exists in destination '{}'.".format(chosen_pkg["name"], dy_app["filen_json_app"]),
                        "-  existing 'v{}' with bound '{}' and uuid4 '{}'".format(ex_version, ex_bound, ex_uuid4),
                        "- to import 'v{}' with bound '{}' and uuid4 '{}'".format(chosen_pkg["version"], chosen_pkg["bound"], chosen_pkg["uuid4"]))

                    if prompt_boolean("Do you want to replace it", "Y"):
                        delete_index=d
                        break
                    else:
                        to_install=False
                        break

            if to_install is False:
                continue
            else:
                if delete_index != "":
                    del conf_app.data["deps"][delete_index]
                    shutil.rmtree(direpa_dst)

                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), chosen_pkg["bound"])
                conf_app.data["deps"].append(dep_to_insert)
                conf_app.data["deps"]=sort_separated(conf_app.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
                conf_app.set_file_with_data()

                if chosen_pkg["bound"] == "gpm":
                    paths=get_paths_to_copy(direpa_src)
                    copy_to_destination(paths, direpa_src, direpa_dst)

                msg.success("Package '{}' installed in '{}'".format(chosen_pkg["name"], os.path.dirname(direpa_dst)))
    else:
        msg.user_error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)
    
