#!/usr/bin/env python3
import os
import logging
from pprint import pprint
import shutil
import sys

from .search import search
from .helpers import get_pkg_id

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean

# deps packages all still needs to have a least a gpm.json at their root
def check_pkg_integrity(
    filen_json_default, 
    conf_pkg,
    direpa_deps,
    restore,
):

    check_minimum_data(conf_pkg)

    # check for duplicate in data_root["deps"]
    pkg_deps={}
    for dep in conf_pkg.data["deps"]:
        uuid4, name, version, bound = dep.split("|")
        # tmp_id="{}|{}".format(uuid4, name)
        if not name in pkg_deps:
            pkg_deps.update({
                name:{
                    "version": version,
                    "uuid4": uuid4,
                    "bound": bound
                }
            })
        else:
            msg.error("'{}' tmp_id exists at least two times in deps from '{}'".format(conf_pkg.filenpa), "Correct issue manually")
            sys.exit(1)

    if os.path.exists(direpa_deps):
        diren_deps=os.path.basename(direpa_deps)
        deps_direns=os.listdir(direpa_deps)
        if restore is True:
            if len(deps_direns) > 0:
                if prompt_boolean("Do you want to remove and recreate deps directory '{}'".format(direpa_deps)):
                    shutil.rmtree(direpa_deps)
                    os.makedirs(direpa_deps, exist_ok=True)
                else:
                    msg.warning("Restore operation cancelled")
                    sys.exit(1)
        else:
            dir_pkgs={}
            for diren_dep in deps_direns:
                direpa_dep=os.path.join(direpa_deps, diren_dep)
                if os.path.isdir(direpa_dep):
                    conf_dep=Json_config(os.path.join(direpa_dep, filen_json_default))
                    filen_conf_dep=os.path.basename(conf_dep.filenpa)
                    check_minimum_data(conf_dep)
                    dep_name=conf_dep.data["name"]

                    if not dep_name in pkg_deps:
                        msg.error(
                            "At location '{}' for package '{}'".format(direpa_deps, dep_name), 
                            "Package id '{}'".format(get_pkg_id(conf_dep.data)),
                            "found in '{}' but not found in '{}'".format(diren_deps, conf_pkg.filenpa)
                        )
                        sys.exit(1)

                    for field in ["uuid4", "version"]:
                        value=conf_dep.data[field]
                        if value != pkg_deps[dep_name][field]:
                            msg.error(
                                "At location '{}' for package '{}'".format(direpa_deps, dep_name), 
                                "Non matching values for field '{}'".format(field),
                                "Value = '{}' in '{}'".format(value, os.path.join(conf_dep.filenpa)),
                                "Value = '{}' in '{}' deps".format(pkg_deps[dep_name][field], conf_pkg.filenpa))
                            sys.exit(1)

                    if pkg_deps[dep_name]["bound"] == "sys":
                        msg.error(
                            "At location '{}' for package '{}'".format(direpa_deps, dep_name),
                            "Package is present in '{}'".format(diren_deps),
                            "However it has a 'sys' bound in '{}'".format(conf_pkg.filenpa),
                            "Package should be removed from '{}' or bound should be 'gpm' in '{}'".format(diren_deps, conf_pkg.filenpa)
                        )
                        sys.exit(1)
                    
                    dir_pkgs.update({
                        dep_name: {
                            "version": conf_dep.data["version"],
                            "uuid4": conf_dep.data["uuid4"],
                            "bound": "gpm"
                        }
                    })

                else:
                    msg.error("'{}' not allowed.".format(direpa_dep),
                        "Only folders are allowed in '{}' folder".format(diren_deps))
                    sys.exit(1)
        
            # check that all pkg_deps with bound gpm have a match in dir_pkgs
            dir_names=set([ name for name in dir_pkgs])
            db_names=set([ name for name in pkg_deps])
            remaining_names=db_names - dir_names

            for name in remaining_names:
                if pkg_deps[name]["bound"] == "gpm":
                    pkg_id=get_pkg_id(pkg_deps[name], name=name)
                    msg.error(
                        "At location '{}' for package '{}'".format(direpa_deps, name),
                        "Package id = '{}'".format(pkg_id),
                        "Package is present in '{}' with bound 'gpm'".format(filen_json_default),
                        "However package is not present in '{}'".format(diren_deps)
                    )
                    sys.exit(1)

def check_minimum_data(conf):
    for field in ["name", "version", "uuid4", "deps"]:
        if not field in conf.data:
            msg.error("Field '{}' not found in '{}'".format(field, filenpa_json))
            sys.exit(1)

        if field != "deps":
            if not conf.data[field]:
                msg.error("Field '{}' is empty in '{}'".format(field, filenpa_json))
                sys.exit(1)

