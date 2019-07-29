#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.6.0
# name: release
# license: MIT
import os, sys
import logging
from pprint import pprint
import shutil

from ..modules.json_config.json_config import Json_config
from ..modules.prompt.prompt import prompt_multiple
from ..gpkgs import message as msg
from ..modules.prompt.prompt import prompt_boolean

from .search import search
from .helpers import is_pkg_git, get_direpa_root, get_pkg_id

# ./__init__.py -i message,a.a.a prompt

def check_pkg_integrity(dy_app, direpa_pkg, action=None):
    print
    filenpa_json_root=os.path.join(direpa_pkg, dy_app["filen_json_app"])
    data_root=get_json_data(filenpa_json_root)

    # check for duplicate in data_root["deps"]
    db_pkgs={}
    for dep in data_root["deps"]:
        uuid4_db, name_db, version_db, bound_db = dep.split("|")
        # tmp_id="{}|{}".format(uuid4_db, name_db)
        if not name_db in db_pkgs:
            db_pkgs.update({
                name_db:{
                    "version": version_db,
                    "uuid4": uuid4_db,
                    "bound": bound_db
                }
            })
        else:
            msg.error("'{}' tmp_id exists at least two times in deps from '{}'".format(filenpa_json_root), "Correct issue manually")
            sys.exit(1)

    # check that for each folder in gpkgs, an entry matches in its root gpm.json
    direpa_deps=os.path.join(direpa_pkg, dy_app["diren_pkgs"])

    dir_pkgs={}
    if os.path.exists(direpa_deps):
        for diren_dep in os.listdir(direpa_deps):
            direpa_dep=os.path.join(direpa_deps, diren_dep)
            if os.path.isdir(direpa_dep):
                filenpa_json_dep=os.path.join(direpa_dep, dy_app["filen_json_app"])
                data_dep=get_json_data(filenpa_json_dep)

                if not data_dep["name"] in db_pkgs:
                    msg.error(
                        "At location '{}' for package '{}'".format(direpa_pkg, data_dep["name"]), 
                        "Package id '{}'".format(get_pkg_id(data_dep)),
                        "found in '{}' but not found in '{}'".format(dy_app["diren_pkgs"], dy_app["filen_json_app"])
                    )
                    sys.exit(1)

                for field in ["uuid4", "version"]:
                    if data_dep[field] != db_pkgs[data_dep["name"]][field]:
                        msg.error(
                            "At location '{}' for package '{}'".format(direpa_pkg, data_dep["name"]), 
                            "Non matching values for field '{}'".format(field),
                            "Value = '{}' in '{}'".format(data_dep[field], os.path.join(
                                dy_app["diren_pkgs"],
                                data_dep["name"],
                                dy_app["filen_json_app"]
                                )),
                            "Value = '{}' in '{}' deps".format(db_pkgs[data_dep["name"]][field], dy_app["filen_json_app"]))
                        sys.exit(1)

                if db_pkgs[data_dep["name"]]["bound"] == "sys":
                    msg.error(
                        "At location '{}' for package '{}'".format(direpa_pkg, data_dep["name"]),
                        "Package is present in '{}'".format(dy_app["diren_pkgs"]),
                        "However it has a 'sys' bound in '{}'".format(dy_app["filen_json_app"]),
                        "Package should be removed from '{}' or bound should be 'gpm' in '{}'".format(dy_app["diren_pkgs"], dy_app["filen_json_app"])
                    )
                    sys.exit(1)
                
                dir_pkgs.update({
                    data_dep["name"]: {
                        "version": data_dep["version"],
                        "uuid4": data_dep["uuid4"],
                        "bound": "gpm"
                    }
                })

            else:
                msg.error("'{}' not allowed.".format(direpa_dep),
                    "Only folders are allowed in '{}' folder".format(dy_app["diren_pkgs"]))
                sys.exit(1)
    
    # check that all db_pkgs with bound gpm have a match in dir_pkgs
    dir_names=set([ name for name in dir_pkgs])
    db_names=set([ name for name in db_pkgs])
    remaining_names=db_names - dir_names



    for name in remaining_names:
        if db_pkgs[name]["bound"] == "gpm":
            pkg_id=get_pkg_id(db_pkgs[name], name=name)
            if action != "restore":
                msg.error(
                    "At location '{}' for package '{}'".format(direpa_pkg, name),
                    "Package id = '{}'".format(pkg_id),
                    "Package is present in '{}' with bound 'gpm'".format(dy_app["filen_json_app"]),
                    "However package is not present in '{}'".format(dy_app["diren_pkgs"])
                )
                sys.exit(1)


def get_json_data(filenpa_json):
    logger = logging.Logger('catch_all')

    if not os.path.exists(filenpa_json):
        msg.error("'{}' not found.".format(filenpa_json))
        sys.exit(1)

    try:
        # print(filenpa_json)
        data=Json_config(filenpa_json).data
    except BaseException as e:
        msg.error("There is a syntax error in '{}'".format(filenpa_json))
        logger.error(e, exc_info=True)
        sys.exit(1)

    for field in ["name", "version", "uuid4", "deps"]:
        if not field in data:
            msg.error("Field '{}' not found in '{}'".format(field, filenpa_json))
            sys.exit(1)

        if field != "deps":
            if not field:
                msg.error("Field '{}' is empty in '{}'".format(field, filenpa_json))
                sys.exit(1)

    return data
