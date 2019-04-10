#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.4.0
# name: release
# license: MIT
import os, sys
from pprint import pprint
import shutil

from modules.json_config.json_config import Json_config
from modules.prompt.prompt import prompt_multiple
import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean

from .search import search
from .helpers import is_pkg_git, get_direpa_root, get_pkg_id
from .refine import get_paths_to_copy, copy_to_destination


# ./__init__.py -i message,a.a.a prompt

def check_pkg_integrity(dy_app, direpa_pkg):
    filenpa_json_root=os.path.join(direpa_pkg, dy_app["filen_json_app"])
    data_root=get_json_data(filenpa_json_root)

    # check for duplicate in data_root["deps"]
    existing_db_pkgs={}
    for dep in data_root["deps"]:
        uuid4_db, name_db, version_db, bound_db = dep.split("|")
        # tmp_id="{}|{}".format(uuid4_db, name_db)
        if not name_db in existing_db_pkgs:
            if bound_db == "gpm":
                existing_db_pkgs.update({
                    name_db:{
                        "version": version_db,
                        "uuid4": uuid4_db,
                        "bound": bound_db
                    }
                })
        else:
            msg.user_error("'{}' tmp_id exists at least two times in deps from '{}'".format(filenpa_json_root), "Correct issue manually")
            sys.exit(1)

    # check that package entry has at least one entry in gpkgs???
    direpa_deps=os.path.join(direpa_pkg, dy_app["diren_pkgs"])


    existing_dir_pkgs={}
    for diren_dep in os.listdir(direpa_deps):
        direpa_dep=os.path.join(direpa_deps, diren_dep)
        if os.path.isdir(direpa_dep):
            filenpa_json_dep=os.path.join(direpa_dep, dy_app["filen_json_app"])
            data_dep=get_json_data(filenpa_json_dep)

            if not data_dep["name"] in existing_db_pkgs:
                msg.user_error(
                    "At location '{}' for package '{}'".format(direpa_pkg, data_dep["name"]), 
                    "Package id '{}'".format(get_pkg_id(data_dep)),
                    "found in '{}' but not found in '{}'".format(dy_app["diren_pkgs"], dy_app["filen_json_app"])
                )
                sys.exit(1)


            for field in ["uuid4", "version"]:
                if data_dep[field] != existing_db_pkgs[data_dep["name"]][field]:
                    pprint(data_dep)
                    print()
                    pprint(existing_db_pkgs[data_dep["name"]])

                    msg.user_error(
                        "At location '{}' for package '{}'".format(direpa_pkg, data_dep["name"]), 
                        "Non matching values for field '{}'".format(field),
                        "Value = '{}' in '{}'".format(data_dep[field], os.path.join(
                            dy_app["diren_pkgs"],
                            data_dep["name"],
                            dy_app["filen_json_app"]
                            )),
                        "Value = '{}' in '{}' deps".format(existing_db_pkgs[data_dep["name"]][field], dy_app["filen_json_app"]))
                    sys.exit(1)
            
            # print(direpa_dep)
        else:
            msg.user_error("'{}' not allowed.".format(direpa_dep),
                "Only files are allowed in '{}' folder".format(dy_app["diren_pkgs"]))
            sys.exit(1)

    # check that all existing_db_pkgs have a match in existing_dir_pkgs

def get_json_data(filenpa_json):
    if not os.path.exists(filenpa_json):
        msg.user_error("'{}' not found.".format(filenpa_json))
        sys.exit(1)

    data=Json_config(filenpa_json).data

    for field in ["name", "version", "uuid4", "deps"]:
        if not field in data:
            msg.user_error("Field '{}' not found in '{}'".format(field, filenpa_json))
            sys.exit(1)

        if field != "deps":
            if not field:
                msg.user_error("Field '{}' is empty in '{}'".format(field, filenpa_json))
                sys.exit(1)

    return data



    
    # for pkg in existing_db_pkgs:


    # for elem in os.listdir(direpa_deps):

        # print(elem)

    # check that all packages have an entry in db too???

    # then I could also do a check on the match db, folder for version and uuid4
    print()