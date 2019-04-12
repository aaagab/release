#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.1.1
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

            components=pkg_filter.split(",")
            name=components[0]
            version=""
            bound=""
            if len(components) == 2:
                version=components[1]
            elif len(components) == 3:
                bound=components[2]

            tmp_filter="n:{}".format(name)
            if version:
                tmp_filter+=",v:{}".format(version)
            else:
                tmp_filter+=",v:L.L.L"

            selected_pkgs=search(db["pkgs"], tmp_filter)
            chosen_pkg={}
            if not selected_pkgs:
                msg.warning("No package found with filter '{}' in  db.json from repository".format(pkg_filter))
                continue
            elif len(selected_pkgs) == 1:
                chosen_pkg={
                    "name": name,
                    "uuid4": selected_pkgs[0]["uuid4"],
                    "version": selected_pkgs[0]["version"]
                }
            else:
                uuid4s=[]
                for pkg in selected_pkgs:
                    if pkg["uuid4"] not in uuid4s:
                        uuid4s.append(pkg["uuid4"])

                chosen_uuid4=""
                if len(uuid4s) == 1:
                    chosen_uuid4=uuid4s[0]
                else:
                    items=[]
                    for uuid4 in uuid4s:
                        pkg_version=[pkg["version"] for pkg in selected_pkgs if pkg["uuid4"] == uuid4][-1]
                        filenpa_description=os.path.join(dy_app["direpa_release"], name, pkg_version, name, dy_app["filen_json_app"])
                        description=""
                        if os.path.exists(filenpa_description):
                            description=Json_config(filenpa_description).data["description"]

                        items.append("{} {}\n\t{}".format(db["uuid4s"][uuid4], uuid4, description))

                    chosen_uuid4=prompt_multiple(
                        dict(
                            items=items,
                            title="Select a package",
                            values=uuid4s
                        ))
                                       
                versions=[pkg["version"] for pkg in selected_pkgs if pkg["uuid4"] == chosen_uuid4]
                chosen_version=""

                if len(versions) == 1:
                    chosen_version=versions[0]
                else:
                    items=[]
                    for version in versions:
                        items.append("{} {}".format(name, version))

                    chosen_version=prompt_multiple(
                        dict(
                            items=items,
                            title="Select a version for pkg '{}'".format(name),
                            values=versions
                        ))

                    chosen_pkg={
                        "name": name,
                        "uuid4": chosen_uuid4,
                        "version": chosen_version
                    }
                    
            if bound:
                bounds=["gpm", "sys"]
                if bound not in bounds:
                    msg.user_error("For filter '{}' bound '{}' not in ['{}']".format(pkg_filter, bound, "', '".join(bounds)))
                    sys.exit(1)
            else:
                bound="gpm"

            chosen_pkg.update(dict(bound=bound))

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

                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), bound)
                conf_app.data["deps"].append(dep_to_insert)
                conf_app.data["deps"]=sort_separated(conf_app.data["deps"], sort_order=[1,0,2,3], keep_sort_order=False, separator="|")
                conf_app.set_file_with_data()

                if bound == "gpm":
                    paths=get_paths_to_copy(direpa_src)
                    copy_to_destination(paths, direpa_src, direpa_dst)

                msg.success("Package '{}' installed in '{}'".format(chosen_pkg["name"], os.path.dirname(direpa_dst)))
    else:
        msg.user_error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)
    
