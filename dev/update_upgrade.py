#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.3.0
# name: release
# license: MIT
import os, sys
from pprint import pprint
import shutil

from ..modules.json_config.json_config import Json_config
from ..modules.prompt.prompt import prompt_multiple
from ..modules.message import message as msg
from ..modules.prompt.prompt import prompt_boolean

from .search import search
from .helpers import is_pkg_git, get_direpa_root, get_pkg_id
from .refine import get_paths_to_copy, copy_to_destination
from .check_pkg_integrity import check_pkg_integrity
from .choose_pkg_cli import choose_pkg_cli
from . import regex_obj as ro

from ..gpkgs.sort_separated import sort_separated

# ./__init__.py -i message,a.a.a prompt

def update_upgrade(dy_app, action):
    if is_pkg_git():
        direpa_root=get_direpa_root()
        check_pkg_integrity(dy_app, direpa_root)
        pkg_names=dy_app["args"][action]

        filenpa_json=os.path.join(direpa_root, dy_app["filen_json_app"])
        conf_app=Json_config(filenpa_json)
        dep_pkgs={}
        dep_pkg_names=[]
        for dep in conf_app.data["deps"]:
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
            msg.warning("Waiting confirmation to update all dependencies for '{}'".format(direpa_root))
            if not prompt_boolean("Do you want to continue" , 'N'):
                sys.exit(1)
        else:
            pkg_names=sorted(pkg_names)

        for pkg_name in pkg_names:
            direpa_dep=os.path.join(direpa_root, dy_app["diren_pkgs"], pkg_name)
            if not pkg_name in dep_pkg_names:
                msg.warning("Package '{}' not found in '{}'".format(pkg_name, os.path.dirname(direpa_dep)))
                continue
            else:
                reg_version_dep=dep_pkgs[pkg_name]["regex"]
                version_filter=""
                if reg_version_dep.match:
                    if action == "update":
                        version_filter="{}.L.L".format(reg_version_dep.major)
                    elif action == "upgrade":
                        version_filter="L.L.L".format(reg_version_dep.major)
                else:
                    version_filter="A.A.A"

                chosen_pkg=choose_pkg_cli(dy_app, action, "{},{}".format(pkg_name, version_filter))
                if reg_version_dep.match:
                    reg_version_chosen_pkg=ro.Version_regex(chosen_pkg["version"])
                    compare_status=reg_version_chosen_pkg.compare(reg_version_dep)
                    if compare_status == "smaller":
                        msg.warning("For '{}' {} not needed".format(pkg_name, action),
                            "Version '{}' from '{}' is smaller than".format(chosen_pkg["version"], dy_app["direpa_release"]),
                            "Version '{}' from '{}'".format(dep_pkgs[pkg_name]["version"], direpa_root)
                            )
                        continue
                    elif compare_status == "equals":
                        msg.warning("For '{}' {} not needed".format(pkg_name, action),
                            "Version '{}' is already the latest {}".format(chosen_pkg["version"], action, dy_app["direpa_release"])
                            )
                        continue
                    elif compare_status == "bigger":
                        pass # package is going to be updated|upgraded with chosen
                        
                else:
                    pass # package is going to be updated|upgraded with chosen

                delete_index=dep_pkg_names.index(pkg_name)
                del conf_app.data["deps"][delete_index]

                if os.path.exists(direpa_dep):
                    shutil.rmtree(direpa_dep)

                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), dep_pkgs[pkg_name]["bound"])
                conf_app.data["deps"].append(dep_to_insert)
                conf_app.data["deps"]=sort_separated(conf_app.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
                conf_app.set_file_with_data()

                if dep_pkgs[pkg_name]["bound"] == "gpm":
                    direpa_src=os.path.join(dy_app["direpa_release"], chosen_pkg["name"], chosen_pkg["version"], chosen_pkg["name"])
                    paths=get_paths_to_copy(direpa_src)
                    copy_to_destination(paths, direpa_src, direpa_dep)

                msg.success("Package '{}' {}d from '{}' to '{}' in '{}'".format(chosen_pkg["name"], action, reg_version_dep.text, reg_version_chosen_pkg.text, os.path.dirname(direpa_dep)))
    else:
        msg.user_error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)
