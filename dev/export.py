#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.1.1
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from dev.helpers import get_direpa_root, to_be_coded, get_app_meta_data
from dev.refine import get_paths_to_copy, copy_to_destination
import dev.regex_obj as ro

import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean
from modules.json_config.json_config import Json_config
import modules.shell_helpers.shell_helpers as shell

def export(dy_rel, args):
    direpa_root=get_direpa_root()

    os.chdir(direpa_root)

    dy_app=get_app_meta_data(direpa_root)
    added_refine_rules=[]
    direpa_dst=""
    previous_branch=""
    direpa_bin=""

    if args["export_rel"] is True:
        if args["release_version"] is None:
            msg.user_error("You need to provide a release version with --rversion for export release")
            sys.exit(1)

        version=args["release_version"][0]
        if args["path"] is None:
            added_refine_rules=["/modules/", "/.pkgs/", "/upacks/"]
            if args["add_deps"] is True:
                msg.warning(
                    "--add-deps is not an option for export to release, when path is not provided.",
                    "dependencies are not included in this context."
                )

            direpa_dst=os.path.join(dy_rel["direpa_release"], dy_app["name"], version, dy_app["name"])
            prompt_for_replace(direpa_dst)
            
            previous_branch=checkout_version(version, direpa_root)
        else:
            if args["add_deps"] is False:
                added_refine_rules=["/modules/", "/.pkgs/", "/upacks/"]

            direpa_dst_root=args["path"][0]
            direpa_dst=os.path.join(direpa_dst_root, dy_app["name"])
            prompt_for_replace(direpa_dst)

            # check if release is already in rel
            direpa_rel_version=os.path.join(dy_rel["direpa_release"], dy_app["name"], version, dy_app["name"])
            if os.path.exists(direpa_rel_version): # if exists copy existing 
                direpa_root=direpa_rel_version
            else: # else checkout a new one
                previous_branch=checkout_version(version, direpa_root)

    elif args["export_bin"] is True:
        if args["add_deps"] is True:
            msg.warning(
                "--add-deps is not an option for export to bin",
                "dependencies are included by default in this context."
                )

        added_refine_rules=[]
        if args["path"] is None:
            direpa_bin=dy_rel["direpa_bin"]
        else:
            direpa_bin=args["path"][0]

        if args["release_version"] is None: # get current repository state
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_app["name"]),
                "beta", 
                dy_app["name"])
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)

        else: # checkout at chosen version
            version=args["release_version"][0]
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_app["name"]),
                version, 
                dy_app["name"])

            prompt_for_replace(direpa_dst)

            previous_branch=checkout_version(version, direpa_root)

    paths=get_paths_to_copy(direpa_root, added_refine_rules)
    copy_to_destination(paths, direpa_root, direpa_dst)

    if direpa_bin:
        if args["no_symlink"] is False:
            filenpa_exec=os.path.join(direpa_dst, dy_app["filen_main"])
            filenpa_symlink=os.path.join(direpa_bin, dy_app["name"])

            with contextlib.suppress(FileNotFoundError):
                os.remove(filenpa_symlink)

            os.symlink( filenpa_exec, filenpa_symlink)

    if previous_branch:
        shell.cmd_prompt("git checkout "+previous_branch)

def prompt_for_replace(direpa_dst):
    if os.path.exists(direpa_dst):
        msg.warning("'{}' already exists.".format(direpa_dst))
        if prompt_boolean("Do you want to replace it", "N"):
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

