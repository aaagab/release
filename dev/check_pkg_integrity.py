#!/usr/bin/env python3
import os
import sys

from .helpers import get_pkg_id

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean
from ..gpkgs import shell_helpers as shell

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
        uuid4, alias, version, bound = dep.split("|")
        if not alias in pkg_deps:
            pkg_deps.update({
                alias:{
                    "version": version,
                    "uuid4": uuid4,
                    "bound": bound
                }
            })
        else:
            msg.error("'{}' tmp_id exists at least two times in deps from '{}'".format(alias, conf_pkg.filenpa), "Correct issue manually")
            sys.exit(1)

    if os.path.exists(direpa_deps):
        diren_deps=os.path.basename(direpa_deps)
        deps_direns=os.listdir(direpa_deps)
        if restore is True:
            if len(deps_direns) > 0:
                if prompt_boolean("Do you want to remove and recreate deps directory '{}'".format(direpa_deps)):
                    shell.rmtree(direpa_deps)
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
                    dep_alias=None
                    if "alias" in conf_dep.data:
                        dep_alias=conf_dep.data["alias"]
                    else:
                        dep_alias=conf_dep.data["name"]

                    if not dep_alias in pkg_deps:
                        msg.error([
                            "At location '{}' for package '{}'".format(direpa_deps, dep_alias), 
                            "Package id '{}'".format(get_pkg_id(conf_dep.data)),
                            "found in '{}' but not found in '{}'".format(diren_deps, conf_pkg.filenpa),
                        ])
                        sys.exit(1)

                    for field in ["uuid4", "version"]:
                        value=conf_dep.data[field]
                        if value != pkg_deps[dep_alias][field]:
                            msg.error([
                                "At location '{}' for package '{}'".format(direpa_deps, dep_alias), 
                                "Non matching values for field '{}'".format(field),
                                "Value = '{}' in '{}'".format(value, os.path.join(conf_dep.filenpa)),
                                "Value = '{}' in '{}' deps".format(pkg_deps[dep_alias][field], conf_pkg.filenpa)
                            ])
                            sys.exit(1)

                    if pkg_deps[dep_alias]["bound"] == "sys":
                        msg.error([
                            "At location '{}' for package '{}'".format(direpa_deps, dep_alias),
                            "Package is present in '{}'".format(diren_deps),
                            "However it has a 'sys' bound in '{}'".format(conf_pkg.filenpa),
                            "Package should be removed from '{}' or bound should be 'gpm' in '{}'".format(diren_deps, conf_pkg.filenpa)
                        ])
                        sys.exit(1)
                    
                    dir_pkgs.update({
                        dep_alias: {
                            "version": conf_dep.data["version"],
                            "uuid4": conf_dep.data["uuid4"],
                            "bound": "gpm"
                        }
                    })

                else:
                    msg.error(["'{}' not allowed.".format(direpa_dep),
                        "Only folders are allowed in '{}' folder".format(diren_deps)])
                    sys.exit(1)
        
            # check that all pkg_deps with bound gpm have a match in dir_pkgs
            dir_aliases=set([ alias for alias in dir_pkgs])
            db_aliases=set([ alias for alias in pkg_deps])
            remaining_aliases=db_aliases - dir_aliases

            for alias in remaining_aliases:
                if pkg_deps[alias]["bound"] == "gpm":
                    pkg_id=get_pkg_id(pkg_deps[alias], alias=alias)
                    msg.error([
                        "At location '{}' for package '{}'".format(direpa_deps, alias),
                        "Package id = '{}'".format(pkg_id),
                        "Package is present in '{}' with bound 'gpm'".format(filen_json_default),
                        "However package is not present in '{}'".format(diren_deps)
                    ])
                    sys.exit(1)

def check_minimum_data(conf: Json_config):
    for field in ["alias", "name", "version", "uuid4", "deps"]:
        if not field in conf.data:
            if field == "alias":
                if "name" not in conf.data:
                    msg.warning("Name not found either")
                else:
                    continue
            msg.error("Field '{}' not found in '{}'".format(field, conf.filenpa))
            sys.exit(1)

        if field != "deps":
            if field in conf.data and not conf.data[field]:
                msg.error("Field '{}' is empty in '{}'".format(field, conf.filenpa))
                sys.exit(1)

