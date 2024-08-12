#!/usr/bin/env python3
import os
from pprint import pprint
import shutil
import sys

from . import regex_obj as ro
from .choose_pkg_cli import choose_pkg_cli
from .helpers import get_pkg_id

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.sort_separated import sort_separated
from ..gpkgs import shell_helpers as shell

def update_upgrade(
    arg_str,
    conf_pkg,
    direpa_deps,
    direpa_pkg,
    direpa_rel,
    filen_json_app,
    filen_json_rel,
    pkg_aliases,
):
    dep_pkgs={}
    dep_pkg_aliases=[]
    for dep in conf_pkg.data["deps"]:
        uuid4, alias, version, bound = dep.split("|")
        dep_pkg_aliases.append(alias)
        dep_pkgs.update({
            alias:{
                "bound": bound,
                "version": version,
                "uuid4": uuid4,
                "regex": ro.Version_regex(version)
            }
        })

    if pkg_aliases is True:
        pkg_aliases=sorted([alias for alias in dep_pkgs])
        msg.warning("Waiting confirmation to update all dependencies for '{}'".format(direpa_pkg))
        if not prompt_boolean("Do you want to continue" , 'N'):
            sys.exit(1)
    else:
        pkg_aliases=sorted(pkg_aliases)

    if len(pkg_aliases) == 0:
        pkg_aliases=sorted(dep_pkgs)
    for pkg_alias in pkg_aliases:
        direpa_dep=os.path.join(direpa_deps, pkg_alias)
        if not pkg_alias in dep_pkg_aliases:
            msg.warning("Package '{}' not found in '{}'".format(pkg_alias, os.path.dirname(direpa_dep)))
            continue
        else:
            reg_version_dep=dep_pkgs[pkg_alias]["regex"]
            version_filter=""
            if reg_version_dep.match:
                if arg_str == "update":
                    version_filter="{}.L.L".format(reg_version_dep.major)
                elif arg_str == "upgrade":
                    version_filter="L.L.L"
            else:
                version_filter="A.A.A"

            chosen_pkg=choose_pkg_cli(
                direpa_rel,
                filen_json_rel,
                filen_json_app, 
                "{},{}".format(pkg_alias, version_filter),
            )

            if reg_version_dep.match:
                reg_version_chosen_pkg=ro.Version_regex(chosen_pkg["version"])
                compare_status=reg_version_chosen_pkg.compare(reg_version_dep)
                if compare_status == "smaller":
                    msg.warning([
                        "For '{}' {} not needed".format(pkg_alias, arg_str),
                        "Version '{}' from '{}' is smaller than".format(chosen_pkg["version"], direpa_rel),
                        "Version '{}' from '{}'".format(dep_pkgs[pkg_alias]["version"], direpa_pkg),
                    ])
                    continue
                elif compare_status == "equals":
                    msg.warning([
                        "For '{}' {} not needed".format(pkg_alias, arg_str),
                        "Version '{}' is already the latest {}".format(chosen_pkg["version"], arg_str),
                    ])
                    continue
                elif compare_status == "bigger":
                    pass # package is going to be updated|upgraded with chosen
                    
            else:
                pass # package is going to be updated|upgraded with chosen
            
            delete_index=dep_pkg_aliases.index(pkg_alias)
            del conf_pkg.data["deps"][delete_index]

            if os.path.exists(direpa_dep):
                shell.rmtree(direpa_dep)

            dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), dep_pkgs[pkg_alias]["bound"])
            conf_pkg.data["deps"].append(dep_to_insert)
            conf_pkg.data["deps"]=sort_separated(conf_pkg.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
            conf_pkg.save()

            if dep_pkgs[pkg_alias]["bound"] == "gpm":
                direpa_src=os.path.join(direpa_rel, chosen_pkg["alias"], chosen_pkg["version"], chosen_pkg["alias"])
                paths=get_paths_to_copy(direpa_src)
                copy_to_destination(paths, direpa_src, direpa_dep)

            msg.success("Package '{}' {}d from '{}' to '{}' in '{}'".format(chosen_pkg["alias"], arg_str, reg_version_dep.text, reg_version_chosen_pkg.text, os.path.dirname(direpa_dep)))
