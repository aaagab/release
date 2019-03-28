#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.1.0
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
from pprint import pprint

from dev.helpers import get_direpa_root, to_be_coded
from dev.refine import get_paths_to_copy, copy_to_destination
import modules.message.message as msg
from modules.json_config.json_config import Json_config

def export(dy_rel, args):
    # print(action)
    pprint(args)


    direpa_root=get_direpa_root()

    dy_app=get_app_meta_data(direpa_root)
    added_refine_rules=[]
    direpa_dst=""
    if args["export_rel"] is True:
        if args["release_version"] is None:
            msg.user_error("You need to provide a release version with --rversion for export release")
            sys.exit(1)

        version=args["release_version"][0]
        
        if args["modules"] is False:
            added_refine_rules=["/modules/"]

        direpa_dst=os.path.join(direpa_root, dy_rel["diren_release"], version, dy_app["name"])
        to_be_coded()
    elif args["export_bin"] is True:
        if args["modules"] is True:
            msg.warning(
                "Modules not an option for export to bin",
                "--modules can be removed."
                )

        added_refine_rules=[]
        if args["release_version"] is None: # get current repository state
            if args["path"] is None:
                direpa_dst=os.path.join(
                    dy_rel["direpa_bin"], 
                    "{}_data".format(dy_app["name"]),
                    "beta", 
                    dy_app["name"])

                if os.path.exists(direpa_dst):
                    shutil.rmtree(direpa_dst)
                os.makedirs(direpa_dst, exist_ok=True)

            else:
                to_be_coded()
                if os.path.exists(args["path"]):
                    direpa_dst=os.path.join(args["path"])

        else: # checkout at chosen version
            version=args["release_version"][0]
            to_be_coded()
            # check first in rel,
            
            # if not checkout at version.



    paths=get_paths_to_copy(direpa_root, added_refine_rules)
    # pprint(paths)
    sys.exit()
    # to_be_coded()
    copy_to_destination(paths, direpa_root, direpa_dst)

    if args["export_bin"] is True:
        filenpa_exec=os.path.join(direpa_dst, dy_app["filen_main"])
        filenpa_symlink=os.path.join(dy_rel["direpa_bin"], dy_app["name"])

        with contextlib.suppress(FileNotFoundError):
            os.remove(filenpa_symlink)

        os.symlink( filenpa_exec, filenpa_symlink)

    # if args["export_rel"] is True:
    #     if os.path.exists(direpa_dst):
    #         msg.warning("'{}' already exists.".format(direpa_dst))
    #         if prompt_boolean("Do you want to replace it"):
    #             shutil.rmtree(direpa_dst)
    

# def get_direpa_release(direpa_root):
#     direpa_release=os.path.join(
#         os.path.dirname(direpa_root),
#         "rel"
#     )

# def get_direpa_bin():
#     return "data/bin"

# def delete_existing_path(direpa):


def get_app_meta_data(direpa_root):
    confs=["config/config.json", "modules.json", "gpm.json"]
    keys=["name", "filen_main", "version"]
    for filen_conf in confs:
        filenpa_conf=os.path.join(direpa_root, filen_conf)
        if os.path.exists(filenpa_conf):
            data=Json_config(filenpa_conf).data
            all_key_found=True
            for key in keys:
                if not key in data:
                    msg.warning("Missing '{}' in '{}'".format(key, filen_conf))
                    all_key_found=False
                    break

            if all_key_found:
                if "options" in data:
                    del data["options"]
                return data
        
    msg.user_error("keys ['{}'] in at least one conf file from ['{}'']".format(
        "', '".join(keys),
        "', '".join(confs)
    ))
    sys.exit(1)

  

# git_tag_data=shell.cmd_get_value("git tag").strip()
# existing_versions=[]
# if git_tag_data:
#     for tag in git_tag_data.splitlines():
#         reg_version=""
#         tag=tag.strip()
#         if tag[0] == "v":
#             reg_version=ro.Version_regex(tag[1:])
#             if reg_version.match:
#                 existing_versions.append(reg_version.text)

# if not dy_gpm["export_version"] in existing_versions:
#     msg.user_error("Version '{}' does not exist in '{}' at path '{}'".format(
#         dy_gpm["export_version"],
#         location_src.alias,
#         location_src.direpa_root
#     ))
#     sys.exit(1)
# else:
#     # checkout to export version
#     previous_branch=subprocess.run(shlex.split("git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
#     os.system("git checkout v"+dy_gpm["export_version"])

# paths=get_paths_to_copy(location_src.direpa_root, ["/{}/".format(dy_gpm["diren_pkgs"])])
# copy_to_destination(paths, location_src.direpa_root, location_dst.direpa_root)

# if location_dst.alias == "pkg_version":
# # checkout to latest source state
# os.system("git checkout "+previous_branch)

