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
from .check_pkg_integrity import check_pkg_integrity


# ./__init__.py -i message,a.a.a prompt

def import_pkgs(dy_app):
    if is_pkg_git():
        filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
        db=Json_config(filenpa_json_repo).data

        direpa_root=get_direpa_root()
        direpa_pkgs=os.path.join(direpa_root, dy_app["diren_pkgs"])
        os.makedirs(direpa_pkgs, exist_ok=True)
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
                tmp_filter+=",v:{}".format(version[0])
            else:
                tmp_filter+=",v:L.L.L"

            selected_pkgs=search(db["pkgs"], tmp_filter)
            chosen_pkg={}
            if len(selected_pkgs) == 1:
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
                    
            direpa_src=os.path.join(dy_app["direpa_release"], chosen_pkg["name"], chosen_pkg["version"], chosen_pkg["name"])
            direpa_dst=os.path.join(direpa_root, dy_app["diren_pkgs"], chosen_pkg["name"])
            filenpa_dst_root=os.path.join(direpa_root, dy_app["filen_json_app"])

            # check pkgs integrity
            check_pkg_integrity(dy_app, direpa_root)

            check_pkg_integrity(dy_app, direpa_src)

            if os.path.exists(direpa_dst):
                check_pkg_integrity(dy_app, direpa_dst)


 

            # first check if existing related package in db and in gpkgs
            # check db

            save_conf=False
            delete_existing=False 
            conf_app=Json_config(filenpa_dst_root)

            existing_pkg=""
            delete_index=""
            for d, dep in enumerate(conf_app.data["deps"]):
                if "{}|{}".format(chosen_pkg["uuid4"], chosen_pkg["name"]) in dep:
                    ex_uuid4, ex_name, ex_version, ex_bound = dep.split("|")
                    
                    msg.warning("'{}' already exists in destination '{}'.".format(chosen_pkg["name"], dy_app["filen_json_app"]),
                        "- existing 'v{}' with bound '{}'".format(ex_version, ex_bound),
                        "-   import 'v{}' with bound '{}'".format(chosen_pkg["version"], chosen_pkg["bound"]))

                    if prompt_boolean("Do you want to replace it", "Y"):
                        delete_index=d
                        break
            
            if delete_index != "":
                del conf_app.data["deps"][delete_index]
                save_conf=True
                delete_existing=True

            if os.path.exists(direpa_dst):
                if delete_existing is True:
                    shutil.rmtree(direpa_dst)

            sys.exit()
            # check folder



            if bound:
                bounds=["gpm", "sys"]
                if bound not in bounds:
                    msg.user_error("For filter '{}' bound '{}' not in ['{}']".format(pkg_filter, bound, "', '".join(bounds)))
                    sys.exit(1)
            else:
                bound="gpm"

            insert_db=""
            copy_folder=""

            if bound == "sys":
                insert_db=True
                copy_folder=False
                # remove if existing similar.

            elif bound == "gpm":
                copy_folder=True
                if os.path.exists(direpa_dst):
                    pass
                    # copy_folder=False
                    
                    #     os.makedirs(direpa_dst, exist_ok=True)
                    #     copy_folder=True
                    # else:
                    #     msg.warning("'{} v{}' not imported.".format(chosen_pkg["name"], chosen_pkg["version"]))

            if insert_db is True:
                conf_app=Json_config(filenpa_dst_root)
                dep_to_insert="{}|{}".format(get_pkg_id(chosen_pkg), bound)
                print(dep_to_insert)
                # conf_app.data["deps"].append()

                # check if existing related entry
                # for dep in conf_app.data["deps"]:
                    # if 


            if copy_folder is True:
                paths=get_paths_to_copy(direpa_src)
                copy_to_destination(paths, direpa_src, direpa_dst)

            

                # pprint(conf_app.data)
                # print(get_pkg_id(chosen_pkg))



    else:
        msg.user_error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)
    




    # pkg_filters=dy_app["args"]["ls_repo"]
    # filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    # pkg_name_and_versions=[]
    # name_uuids={}
    # db=Json_config(filenpa_json_repo).data

    # selected_pkgs=[]
    # if pkg_filters is True:
    #     selected_pkgs=search(db["pkgs"], [])
    # else:
    #     for ftr in pkg_filters:
    #         selected_pkgs=search(db["pkgs"], ftr)

    # for pkg in selected_pkgs:
    #     print(pkg["id"])
    #     if dy_app["args"]["add_deps"] is True:
    #         deps=db["pkgs"][pkg["id"]]
    #         for dep in deps:
    #             print("\t", dep)
