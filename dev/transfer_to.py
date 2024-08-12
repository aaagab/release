#!/usr/bin/env python3
import os
import sys

from .helpers import create_symlink

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt

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
    pkg_alias,
    pkg_version,
    pkg_uuid4,
    system,
):
    conf_data=None
    if no_conf is True:
        if pkg_alias is None:
            pkg_alias=prompt("package alias")
        if pkg_version is None:
            pkg_version=prompt("package version", default="beta")
    else:
        conf_data=Json_config(filenpa_conf).data
        pkg_alias=None
        if "alias" in conf_data:
            pkg_alias=conf_data["alias"]
        else:
            pkg_alias=conf_data["name"]
        if pkg_version is None and is_beta is False:
            pkg_version=conf_data["version"]
        if pkg_uuid4 is None:
            pkg_uuid4=conf_data["uuid4"]

    diren_bin=None
    if is_beta is True:
        diren_bin="beta"
    else:
        diren_bin=pkg_version

    direpa_bin=direpa_to

    path_elems=[
        direpa_to, 
        "{}_data".format(pkg_alias),
    ]

    if pkg_uuid4 is not None:
        path_elems.append(pkg_uuid4.lower().replace("-", ""))

    path_elems.extend([
        diren_bin,
        pkg_alias
    ])

    direpa_to=os.path.join(*path_elems)

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
            shell.rmtree(direpa_to)
        os.makedirs(direpa_to, exist_ok=True)
    else:
        prompt_for_replace(direpa_to, previous_branch, direpa_from)

    msg.info("Copying from '{}' to '{}'".format(direpa_from, direpa_to))
    copy_to_destination(paths, direpa_from, direpa_to)
    
    if no_symlink is False:
        filenpa_exec=os.path.join(direpa_to, filen_main)
        filenpa_symlink=os.path.join(direpa_bin, pkg_alias)
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
    pkg_alias,
    pkg_version,
):

    conf_data=Json_config(filenpa_conf).data
    pkg_alias=None
    if "alias" in conf_data:
        pkg_alias=conf_data["alias"]
    else:
        pkg_alias=conf_data["name"]
    if pkg_version is None:
        pkg_version=conf_data["version"]

    direpa_rel=direpa_to
    direpa_to=os.path.join(direpa_to, pkg_alias, pkg_version, pkg_alias)

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
    pkg_alias=None
    if "alias" in dy_pkg_src:
        pkg_alias=dy_pkg_src["alias"]
    else:
        pkg_alias=dy_pkg_src["name"]

    if dy_pkg_src["uuid4"] in conf_db.data["uuid4s"]:
        if pkg_alias != conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]:
            if previous_branch:
                shell.cmd_prompt("git checkout "+previous_branch)
            msg.error([
                "Failed Insert '{}' with uuid4 '{}' ".format(
                pkg_alias, dy_pkg_src["uuid4"]),
                "In db[uuid4s] same uuid4 has alias '{}'".format(conf_db.data["uuid4s"][dy_pkg_src["uuid4"]]),
                "You can't have same uuid for different aliases."
            ])
            sys.exit(1)

    conf_db.data["uuid4s"].update({dy_pkg_src["uuid4"]: pkg_alias})
    conf_db.data["pkgs"].update({
        "{}|{}|{}".format(dy_pkg_src["uuid4"], pkg_alias, dy_pkg_src["version"]
            ): dy_pkg_src["deps"]
    })

    # if add_deps is False:
        # added_refine_rules=refine_rules
    paths=get_paths_to_copy(direpa_from, added_rules=added_refine_rules)

    prompt_for_replace(direpa_to, previous_branch, direpa_from)
    msg.info("Copying from '{}' to '{}'".format(direpa_from, direpa_to))
    copy_to_destination(paths, direpa_from, direpa_to)
    conf_db.save()

    if previous_branch is not None:
        checkout(previous_branch, direpa_from)
