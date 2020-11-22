#!/usr/bin/env python3
import os
from pprint import pprint
import shutil
import sys

from . import regex_obj as ro
from .choose_pkg_cli import choose_pkg_cli
from .helpers import get_pkg_id
from .search import search

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.sort_separated import sort_separated

def update_upgrade(
    arg_str,
    conf_pkg,
    direpa_deps,
    direpa_pkg,
    direpa_rel,
    filen_json_app,
    filen_json_rel,
    pkg_names,
):
    dep_pkgs={}
    dep_pkg_names=[]
    for dep in conf_pkg.data["deps"]:
        uuid4, name, version, bound = dep.split("|")
        dep_pkg_names.append(name)
        dep_pkgs.update({
            name:{
                "bound": bound,
                "version": version,
                "uuid4": uuid4,
                "regex": ro.Version_regex(version)
            }
        })

    if pkg_names is True:
        pkg_names=sorted([name for name in dep_pkgs])
        msg.warning("Waiting confirmation to update all dependencies for '{}'".format(direpa_pkg))
        if not prompt_boolean("Do you want to continue" , 'N'):
            sys.exit(1)
    else:
        pkg_names=sorted(pkg_names)

    if len(pkg_names) == 0:
        pkg_names=sorted(dep_pkgs)
    for pkg_name in pkg_names:
        direpa_dep=os.path.join(direpa_deps, pkg_name)
        if not pkg_name in dep_pkg_names:
            msg.warning("Package '{}' not found in '{}'".format(pkg_name, os.path.dirname(direpa_dep)))
            continue
        else:
            reg_version_dep=dep_pkgs[pkg_name]["regex"]
            version_filter=""
            if reg_version_dep.match:
                if arg_str == "update":
                    version_filter="{}.L.L".format(reg_version_dep.major)
                elif arg_str == "upgrade":
                    version_filter="L.L.L".format(reg_version_dep.major)
            else:
                version_filter="A.A.A"

            chosen_pkg=choose_pkg_cli(
                direpa_rel,
                filen_json_rel,
                filen_json_app, 
                "{},{}".format(pkg_name, version_filter),
            )
            if reg_version_dep.match:
                reg_version_chosen_pkg=ro.Version_regex(chosen_pkg["version"])
                compare_status=reg_version_chosen_pkg.compare(reg_version_dep)
                if compare_status == "smaller":
                    msg.warning("For '{}' {} not needed".format(pkg_name, arg_str),
                        "Version '{}' from '{}' is smaller than".format(chosen_pkg["version"], direpa_rel),
                        "Version '{}' from '{}'".format(dep_pkgs[pkg_name]["version"], direpa_pkg)
                        )
                    continue
                elif compare_status == "equals":
                    msg.warning("For '{}' {} not needed".format(pkg_name, arg_str),
                        "Version '{}' is already the latest {}".format(chosen_pkg["version"], arg_str, direpa_rel)
                        )
                    continue
                elif compare_status == "bigger":
                    pass # package is going to be updated|upgraded with chosen
                    
            else:
                pass # package is going to be updated|upgraded with chosen

            delete_index=dep_pkg_names.index(pkg_name)
            del conf_pkg.data["deps"][delete_index]

            if os.path.exists(direpa_dep):
                shutil.rmtree(direpa_dep)

            dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), dep_pkgs[pkg_name]["bound"])
            conf_pkg.data["deps"].append(dep_to_insert)
            conf_pkg.data["deps"]=sort_separated(conf_pkg.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
            conf_pkg.save()

            if dep_pkgs[pkg_name]["bound"] == "gpm":
                direpa_src=os.path.join(direpa_rel, chosen_pkg["name"], chosen_pkg["version"], chosen_pkg["name"])
                paths=get_paths_to_copy(direpa_src)
                copy_to_destination(paths, direpa_src, direpa_dep)

            msg.success("Package '{}' {}d from '{}' to '{}' in '{}'".format(chosen_pkg["name"], arg_str, reg_version_dep.text, reg_version_chosen_pkg.text, os.path.dirname(direpa_dep)))
