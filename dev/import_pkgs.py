#!/usr/bin/env python3
import os
from pprint import pprint
import re
import tempfile

from .get_pkg_from_db import get_pkg_from_db
from .helpers import get_pkg_id
from .get_dy_pkg_filter import get_dy_pkg_filter

from ..gpkgs import message as msg
from ..gpkgs.prompt import prompt_boolean, prompt
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.sort_separated import sort_separated
from ..gpkgs import shell_helpers as shell

# ./__init__.py -i message,a.a.a prompt

def import_pkgs(
    conf_pkg,
    conf_db,
    direpa_deps,
    direpa_rel,
    direpa_pkg,
    filen_json_default,
    filter_rules,
    keys,
    is_template,
    no_conf_src,
    no_conf_dst,
    no_root_dir,
    pkg_filters,
):
    for pfilter in pkg_filters:
        dy_pkg_filter=get_dy_pkg_filter(pfilter)
        chosen_pkg=get_pkg_from_db(
            db_data=conf_db.data, 
            direpa_rel=direpa_rel,
            filen_json_default=filen_json_default, 
            not_found_error=True,
            not_found_exit=False,
            pkg_bound=dy_pkg_filter["bound"],
            pkg_alias=dy_pkg_filter["alias"],
            pkg_version=dy_pkg_filter["version"],
            pkg_uuid4=dy_pkg_filter["uuid4"],

        )

        if chosen_pkg is None:
            continue         
        direpa_src=os.path.join(direpa_rel, chosen_pkg["alias"], chosen_pkg["version"], chosen_pkg["alias"])
        if no_root_dir is True:
            direpa_dst=os.path.join(direpa_deps)
        else:
            direpa_dst=os.path.join(direpa_deps, chosen_pkg["alias"])
        to_install=True

        delete_index=""
        if no_conf_src is False:
            for d, dep in enumerate(conf_pkg.data["deps"]):
                ex_uuid4, ex_alias, ex_version, ex_bound = dep.split("|")
                if chosen_pkg["alias"] == ex_alias:
                    msg.warning([
                        "'{}' already exists in destination '{}'.".format(chosen_pkg["alias"], filen_json_default),
                        "-  existing 'v{}' with bound '{}' and uuid4 '{}'".format(ex_version, ex_bound, ex_uuid4),
                        "- to import 'v{}' with bound '{}' and uuid4 '{}'".format(chosen_pkg["version"], chosen_pkg["bound"], chosen_pkg["uuid4"]),
                    ])
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
                    shell.rmtree(direpa_dst)

            if no_conf_src is False:
                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), chosen_pkg["bound"])
                conf_pkg.data["deps"].append(dep_to_insert)
                conf_pkg.data["deps"]=sort_separated(conf_pkg.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
                conf_pkg.save()

            if chosen_pkg["bound"] == "gpm":
                if no_conf_dst:
                    filter_rules.extend(["/gpm.json", "/.refine"])

                paths=get_paths_to_copy(direpa_src, added_rules=filter_rules)

                if is_template:
                    direpa_tmp = tempfile.mkdtemp()
                    copy_to_destination(paths, direpa_src, direpa_tmp)
                    tmp_paths=get_paths_to_copy(direpa_tmp)

                    for t, tmp_path in enumerate(tmp_paths):
                        new_path=re.sub(r"{{([a-zA-Z0-9-_ ]+?)}}", lambda m: replace_key(m, keys), tmp_path)
                        tmp_path_changed=None
                        if new_path != tmp_path:
                            os.rename(tmp_path, new_path)
                            tmp_path_changed=tmp_path
                            tmp_path=new_path
                            tmp_paths[t]=new_path

                        if os.path.isdir(tmp_path):
                            if tmp_path_changed is not None:
                                if t+1 < len(tmp_paths):
                                    for u, update_path in enumerate(tmp_paths[t+1:]):
                                        if update_path[:len(tmp_path_changed)] == tmp_path_changed:
                                            tmp_paths[u+t+1]=new_path+update_path[len(tmp_path_changed):]
                        elif os.path.isfile(tmp_path):
                            data=None
                            with open(tmp_path, "r") as f:
                                data=f.read()
                                data=re.sub(r"{{([a-zA-Z0-9-_ ]+?)}}", lambda m: replace_key(m, keys), data)
                            with open(tmp_path, "w") as f:
                                f.write(data)

                    copy_to_destination(tmp_paths, direpa_tmp, direpa_dst)
                    shell.rmtree(direpa_tmp)
                else:
                    copy_to_destination(paths, direpa_src, direpa_dst)

            msg.success("Package '{}' '{}' installed in '{}'".format(chosen_pkg["alias"], chosen_pkg["version"], os.path.dirname(direpa_dst)))
    
    
def replace_key(reg, keys):
    key=next(iter(reg.groups()))
    if key in keys:
        return keys[key]
    else:
        return prompt(key)
