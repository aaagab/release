#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.7
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from .check_repo import check_repo

from ..dev.helpers import get_direpa_root, to_be_coded, get_app_meta_data, create_symlink
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..dev import regex_obj as ro

from ..modules.message import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell

def export(dy_app, args, dy_pkg=None, direpa_rel=None):
    direpa_root=""

    if args["path_src"]:
        direpa_root=get_direpa_root(args["path_src"][0])
    else:
        direpa_root=get_direpa_root()

    os.chdir(direpa_root)
    # dy_pkg=None
    added_refine_rules=[]
    direpa_dst=""
    previous_branch=""
    direpa_bin=""
    insert_db=False

    if args["export_rel"] is True:
        dy_pkg=get_app_meta_data(direpa_root)
        if args["release_version"]:
            version=args["release_version"][0]

        if args["add_deps"] is False:
            added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]

        if args["path"] is None:
            if args["release_version"] is None:
                msg.user_error("You need to provide a release version with --rversion for export release")
                sys.exit(1)

            direpa_dst=os.path.join(dy_app["direpa_release"], dy_pkg["name"], version, dy_pkg["name"])
            prompt_for_replace(direpa_dst)

        
            previous_branch=checkout_version(version, direpa_root)
            insert_db=True
        else:
            direpa_dst_root=args["path"][0]
            direpa_dst=os.path.join(direpa_dst_root, dy_pkg["name"])
            prompt_for_replace(direpa_dst)

            if args["release_version"]:
                direpa_rel_version=os.path.join(dy_app["direpa_release"], dy_pkg["name"], version, dy_pkg["name"])
                if os.path.exists(direpa_rel_version): # if exists copy existing 
                    direpa_root=direpa_rel_version
                else: # else checkout a new one
                    previous_branch=checkout_version(version, direpa_root)

    elif args["export_bin"] is True:
        dy_pkg=get_app_meta_data(direpa_root)

        if args["add_deps"] is True:
            msg.warning(
                "--add-deps is not an option for export to bin",
                "dependencies are included by default in this context."
                )

        added_refine_rules=[]
        if args["path"] is None:
            direpa_bin=dy_app["direpa_bin"]
        else:
            direpa_bin=args["path"][0]

        if args["release_version"] is None: # get current repository state
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_pkg["name"]),
                "beta", 
                dy_pkg["name"])
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)

        else: # checkout at chosen version
            version=args["release_version"][0]
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_pkg["name"]),
                version, 
                dy_pkg["name"])

            prompt_for_replace(direpa_dst)

            previous_branch=checkout_version(version, direpa_root)
    elif direpa_rel is not None:
        direpa_root=os.path.join(dy_app["direpa_release"], dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
        direpa_dst=os.path.join(direpa_rel, dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
        prompt_for_replace(direpa_dst)
        insert_db=True

    if insert_db:
        conf_db=None
        if direpa_rel is not None:
            check_repo(dy_app, direpa_rel)
            conf_db=Json_config(os.path.join(direpa_rel, dy_app["filen_json_repo"]))
        else:
            conf_db=Json_config(os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"]))
        
        filenpa_gpm_json=os.path.join(direpa_root, "gpm.json")
        if not os.path.exists(filenpa_gpm_json):
            if previous_branch:
                shell.cmd_prompt("git checkout "+previous_branch)
            msg.user_error("'{}' not found".format(filenpa_gpm_json))
            sys.exit(1)
        else:
            dy_pkg_src=Json_config(filenpa_gpm_json).data
            if dy_pkg_src["uuid4"] in conf_db.data["uuid4s"]:
                if dy_pkg_src["name"] != conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]:
                    if previous_branch:
                        shell.cmd_prompt("git checkout "+previous_branch)
                    msg.user_error("Failed Insert '{}' with uuid4 '{}' ".format(
                        dy_pkg_src["name"], dy_pkg_src["uuid4"]),
                        "In db[uuid4s] same uuid4 has name '{}'".format(conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]),
                        "You can't have same uuid for different names.")
                    sys.exit(1)
            else:
                conf_db.data["uuid4s"].update({dy_pkg_src["uuid4"]: dy_pkg_src["name"]})
            
            conf_db.data["pkgs"].update({
                "{}|{}|{}".format(dy_pkg_src["uuid4"], dy_pkg_src["name"], dy_pkg_src["version"]
                    ): dy_pkg_src["deps"]
            })

    paths=get_paths_to_copy(direpa_root, added_rules=added_refine_rules)
    copy_to_destination(paths, direpa_root, direpa_dst)

    if insert_db:
        conf_db.set_file_with_data()

    if direpa_bin:
        if args["no_symlink"] is False:
            filenpa_exec=os.path.join(direpa_dst, dy_pkg["filen_main"])
            filenpa_symlink=os.path.join(direpa_bin, dy_pkg["name"])

            create_symlink(dy_app["platform"], filenpa_exec, filenpa_symlink )


    if previous_branch:
        shell.cmd_prompt("git checkout "+previous_branch)

def prompt_for_replace(direpa_dst):
    if os.path.exists(direpa_dst):
        msg.warning("'{}' already exists.".format(direpa_dst))
        if prompt_boolean("Do you want to replace it", "Y"):
            shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            msg.warning("Operation Cancelled.")
            sys.exit(1)

def checkout_version(version, direpa_root):
    git_tag_data=shell.cmd_get_value("git tag").strip()
    existing_versions=[]
    if git_tag_data:
        for tag in git_tag_data.splitlines():
            reg_version=""
            tag=tag.strip()
            if tag[0] == "v":
                reg_version=ro.Version_regex(tag[1:])
                if reg_version.match:
                    existing_versions.append(reg_version.text)

    if not version in existing_versions:
        msg.user_error("Version '{}' does not exist at path '{}'".format(
            version,
            direpa_root
        ))
        sys.exit(1)
    else:
        # checkout to export version
        previous_branch=subprocess.run(shlex.split("git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
        shell.cmd_prompt("git checkout v"+version)
        # os.system(cmd)
        # msg.success(cmd)

    # paths=get_paths_to_copy(location_src.direpa_root, ["/{}/".format(dy_gpm["diren_pkgs"])])
    # copy_to_destination(paths, location_src.direpa_root, location_dst.direpa_root)

    # if location_dst.alias == "pkg_version":
    # checkout to latest source state
        # os.system("git checkout "+previous_branch)
    return previous_branch

