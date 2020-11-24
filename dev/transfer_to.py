#!/usr/bin/env python3
import contextlib
from pprint import pprint
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

from . import regex_obj as ro
from .bump_version import bump_version
from .check_rel import check_rel
from .helpers import get_direpa_root, to_be_coded, get_app_meta_data, create_symlink
from .get_filenpa_conf_from_rel import get_filenpa_conf_from_rel


from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt_boolean, prompt

from .helpers_transfer import checkout_version, prompt_for_replace, checkout

def transfer_to_bin(
    added_refine_rules,
    direpa_from,
    direpa_to,
    filen_main,
    filenpa_conf,
    is_beta,
    is_git,
    no_conf,
    no_symlink,
    pkg_name,
    pkg_version,
    system,
):
    conf_data=None
    if no_conf is True:
        if pkg_name is None:
            pkg_name=prompt("package name")
        if pkg_version is None:
            pkg_version=prompt("package version", default="beta")
    else:
        conf_data=Json_config(filenpa_conf).data  
        pkg_name=conf_data["name"]
        if pkg_version is None and is_beta is False:
            pkg_version=conf_data["version"]

    diren_bin=None
    if is_beta is True:
        diren_bin="beta"
    else:
        diren_bin=pkg_version

    direpa_bin=direpa_to
    direpa_to=os.path.join(
        direpa_to, 
        "{}_data".format(pkg_name),
        diren_bin,
        pkg_name
    )

    if filen_main is None:
        if no_conf is True:
            filen_main=prompt("main file name", default="main.py")
        else:
            filen_main=conf_data["filen_main"]
        
    previous_branch=None
    if is_git is True and pkg_version is not None:
        previous_branch=checkout_version(pkg_version, direpa_from)

    paths=get_paths_to_copy(direpa_from, added_rules=added_refine_rules)
    
    if diren_bin == "beta":
        if os.path.exists(direpa_to):
            shutil.rmtree(direpa_to)
        os.makedirs(direpa_to, exist_ok=True)
    else:
        prompt_for_replace(direpa_to, previous_branch, direpa_from)

    msg.info("Copying from '{}' to '{}'".format(direpa_from, direpa_to))
    copy_to_destination(paths, direpa_from, direpa_to)
    
    if no_symlink is False:
        filenpa_exec=os.path.join(direpa_to, filen_main)
        filenpa_symlink=os.path.join(direpa_bin, pkg_name)
        create_symlink(system, filenpa_exec, filenpa_symlink )

    if previous_branch is not None:
        checkout(previous_branch, direpa_from)

def transfer_to_rel(
    add_deps,
    added_refine_rules,
    direpa_from,
    direpa_to,
    filen_json_rel,
    filenpa_conf,
    is_git,
    pkg_name,
    pkg_version,
):

    conf_data=Json_config(filenpa_conf).data
    pkg_name=conf_data["name"]
    if pkg_version is None:
        pkg_version=conf_data["version"]

    direpa_rel=direpa_to
    direpa_to=os.path.join(direpa_to, pkg_name, pkg_version, pkg_name)

    previous_branch=None
    if is_git is True:
        previous_branch=checkout_version(pkg_version, direpa_from)
        if not os.path.exists(filenpa_conf):
            if previous_branch is not None:
                checkout(previous_branch, direpa_from)
            msg.error("'{}' not found".format(filenpa_conf), exit=1)
        conf_data=Json_config(filenpa_conf).data

    conf_db=Json_config(os.path.join(direpa_rel, filen_json_rel))
    
    dy_pkg_src=conf_data
    if dy_pkg_src["uuid4"] in conf_db.data["uuid4s"]:
        if dy_pkg_src["name"] != conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]:
            if previous_branch:
                shell.cmd_prompt("git checkout "+previous_branch)
            msg.error("Failed Insert '{}' with uuid4 '{}' ".format(
                dy_pkg_src["name"], dy_pkg_src["uuid4"]),
                "In db[uuid4s] same uuid4 has name '{}'".format(conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]),
                "You can't have same uuid for different names.")
            sys.exit(1)

    conf_db.data["uuid4s"].update({dy_pkg_src["uuid4"]: dy_pkg_src["name"]})
    conf_db.data["pkgs"].update({
        "{}|{}|{}".format(dy_pkg_src["uuid4"], dy_pkg_src["name"], dy_pkg_src["version"]
            ): dy_pkg_src["deps"]
    })

    if add_deps is False:
        added_refine_rules=refine_rules
    paths=get_paths_to_copy(direpa_from, added_rules=added_refine_rules)

    prompt_for_replace(direpa_to, previous_branch, direpa_from)
    msg.info("Copying from '{}' to '{}'".format(direpa_from, direpa_to))
    copy_to_destination(paths, direpa_from, direpa_to)
    conf_db.save()

    if previous_branch is not None:
        checkout(previous_branch, direpa_from)
