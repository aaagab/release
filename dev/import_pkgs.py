#!/usr/bin/env python3
import os
from pprint import pprint
import re
import shutil
import sys
import tempfile

from .check_pkg_integrity import check_pkg_integrity
from .get_pkg_from_db import get_pkg_from_db
from .helpers import is_pkg_git, get_direpa_root, get_pkg_id

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean, prompt
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.sort_separated import sort_separated

# ./__init__.py -i message,a.a.a prompt

def import_pkgs(
    conf_pkg,
    conf_db,
    direpa_deps,
    direpa_repo,
    direpa_pkg,
    filen_json_default,
    keys,
    is_template,
    no_conf_src,
    no_conf_dst,
    no_root_dir,
    pkg_filters,
):
    for pkg_filter in pkg_filters:
        chosen_pkg=get_pkg_from_db(
            db_data=conf_db.data, 
            direpa_repo=direpa_repo,
            filen_json_default=filen_json_default, 
            pkg_filter=pkg_filter,
        )
        if chosen_pkg is None:
            continue         
        direpa_src=os.path.join(direpa_repo, chosen_pkg["name"], chosen_pkg["version"], chosen_pkg["name"])
        if no_root_dir is True:
            direpa_dst=os.path.join(direpa_deps)
        else:
            direpa_dst=os.path.join(direpa_deps, chosen_pkg["name"])
        to_install=True

        delete_index=""
        if no_conf_src is False:
            for d, dep in enumerate(conf_pkg.data["deps"]):
                ex_uuid4, ex_name, ex_version, ex_bound = dep.split("|")
                if chosen_pkg["name"] == ex_name:
                    msg.warning(
                        "'{}' already exists in destination '{}'.".format(chosen_pkg["name"], filen_json_default),
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
                del conf_pkg.data["deps"][delete_index]
                if os.path.exists(direpa_dst):
                    shutil.rmtree(direpa_dst)

            if no_conf_src is False:
                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), chosen_pkg["bound"])
                conf_pkg.data["deps"].append(dep_to_insert)
                conf_pkg.data["deps"]=sort_separated(conf_pkg.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
                conf_pkg.save()

            if chosen_pkg["bound"] == "gpm":
                added_rules=[]
                if no_conf_dst:
                    added_rules=["/gpm.json", "/.refine"]
                paths=get_paths_to_copy(direpa_src, added_rules=added_rules)

                if is_template:
                    direpa_tmp = tempfile.mkdtemp()
                    copy_to_destination(paths, direpa_src, direpa_tmp)
                    tmp_paths=get_paths_to_copy(direpa_tmp)
                    for tmp_path in tmp_paths:
                        if os.path.isfile(tmp_path):
                            data=None
                            with open(tmp_path, "r") as f:
                                data=f.read()
                                data=re.sub(r"{{([a-zA-Z0-9-_ ]+?)}}", lambda m: replace_key(m, keys), data)
                            print()
                            print(tmp_path)
                            print("##########")
                            pprint(data)
                                
                    copy_to_destination(tmp_paths, direpa_tmp, direpa_dst)
                    shutil.rmtree(direpa_tmp)
                else:
                    copy_to_destination(paths, direpa_src, direpa_dst)

            msg.success("Package '{}' installed in '{}'".format(chosen_pkg["name"], os.path.dirname(direpa_dst)))
    
    
def replace_key(reg, keys):
    key=next(iter(reg.groups()))
    if key in keys:
        return keys[key]
    else:
        return prompt(key)
