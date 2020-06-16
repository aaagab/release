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
from .check_repo import check_repo
from .get_pkg_from_db import get_pkg_from_db
from .helpers import get_direpa_root, to_be_coded, get_app_meta_data, create_symlink

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt_boolean

def export(
    dy_app,
    arg_str, # export_bin, export_rel, to_repo
    add_deps=False,
    filenpa_conf=None,
    is_git=True,
    pkg_name=None,
    pkg_version=None,
    from_repo=None,
    direpa_bin=None,
    direpa_repo=None,
    direpa_pkg=None,
    only_paths=[],
):

    added_refine_rules=[]
    conf_data=None
    conf_db=None
    direpa_dst=None
    direpa_src=None
    pkg_without_conf=False
    paths=None
    previous_branch=None

    if arg_str == "export_bin":
        add_deps=True
        if from_repo is None:
            if direpa_pkg is None:
                if is_git is True:
                    direpa_src=get_direpa_root()
                else:
                    direpa_src=os.getcwd()
            else:
                if is_git is True:
                    direpa_src=get_direpa_root(direpa_pkg)
                else:
                    direpa_src=direpa_pkg
        
        if from_repo is None:
            if filenpa_conf is None:
                filenpa_conf=os.path.join(direpa_src, dy_app["filen_json_app"])
            conf_data=Json_config(filenpa_conf).data
            pkg_name=conf_data["name"]
            filen_main=conf_data["filen_main"]
        else:
            if pkg_version is None:
                chosen_pkg=get_pkg_from_db(
                    db_data=Json_config(os.path.join(direpa_repo, dy_app["filen_json_repo"])).data,
                    direpa_repo=direpa_repo,
                    filen_json_default=dy_app["filen_json_app"], 
                    pkg_filter=pkg_name,
                )
                pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(direpa_repo, pkg_name, pkg_version, pkg_name)
            conf_data=Json_config(os.path.join(direpa_src, dy_app["filen_json_app"])).data
            filen_main=conf_data["filen_main"]

        diren_bin=None
        if pkg_version is None: # get current repository state
            add_deps=True
            diren_bin="beta"
        else:
            diren_bin=pkg_version

        direpa_dst=os.path.join(
            direpa_bin, 
            "{}_data".format(pkg_name),
            diren_bin,
            pkg_name
        )

        if filen_main is None:
            msg.error("filen_main not set, it should be set with --filen-main arg")
            sys.exit(1)
            
        if is_git is True and pkg_version is not None and from_repo is None:
            previous_branch=checkout_version(pkg_version, direpa_src)

    elif arg_str == "export_rel":
        if from_repo is None:
            if direpa_pkg is None:
                if is_git is True:
                    direpa_src=get_direpa_root()
                else:
                    direpa_src=os.getcwd()
            else:
                if is_git is True:
                    direpa_src=get_direpa_root(direpa_pkg)
                else:
                    direpa_src=direpa_pkg

            if filenpa_conf is None:
                filenpa_conf=os.path.join(direpa_src, dy_app["filen_json_app"])
                if not os.path.exists(filenpa_conf): # search it in repo
                    if pkg_name is None:
                        msg.error("At least a package name needs to be provided with --pkg-name")
                        sys.exit(1)
                    else:
                        db_data=Json_config(os.path.join(direpa_repo, dy_app["filen_json_repo"])).data
                        chosen_pkg=get_pkg_from_db(
                            db_data=db_data,
                            direpa_repo=direpa_repo,
                            filen_json_default=dy_app["filen_json_app"], 
                            pkg_filter=pkg_name,
                        )
                        if chosen_pkg is None:
                            msg.error("No package found with name '{}' at '{}'".format(pkg_name, direpa_repo))
                            sys.exit(1) 
                        else:
                            filenpa_conf=os.path.join(direpa_repo, pkg_name, chosen_pkg["version"], pkg_name, dy_app["filen_json_app"])

                            # from here version has to be incremented
                            # that is a special case where application does not have a config file
                            # files can also be selected
                            paths=get_paths_to_copy(direpa_src, added_rules=added_refine_rules)
                            if only_paths:
                                if add_deps is False:
                                    added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]
                                paths=get_paths_from_only_path(only_paths, paths, direpa_src)

                            pkg_version=bump_version(
                                db_data=db_data,
                                direpa_repo=direpa_repo,
                                dy_app=dy_app,
                                filen_json_default=dy_app["filen_json_repo"], 
                                filenpa_conf=filenpa_conf,
                                increment=True,
                                is_git=False,
                                only_paths=paths,
                                pkg_name=pkg_name,
                                direpa_deps=None,
                                direpa_pkg=direpa_src,
                                save_filenpa_conf=False,
                                version=None,
                            )
                
                            pkg_without_conf=True

            conf_data=Json_config(filenpa_conf).data
            if pkg_without_conf is True:
                if pkg_version != conf_data["version"]:
                    conf_data["version"]=pkg_version
            pkg_name=conf_data["name"]
            filen_main=conf_data["filen_main"]
            if pkg_version is None:
                pkg_version=conf_data["version"]
        else:
            is_git=False
            if direpa_repo == from_repo:
                msg.error("direpa_repo and from_repo are the same '{}'".format(direpa_repo),
                "set --path-repo with a different path")
                sys.exit(1)

            if pkg_version is None:
                chosen_pkg=get_pkg_from_db(
                    db_data=Json_config(os.path.join(from_repo, dy_app["filen_json_repo"])).data,
                    direpa_repo=from_repo,
                    filen_json_default=dy_app["filen_json_app"], 
                    pkg_filter=pkg_name,
                )
                pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(from_repo, pkg_name, pkg_version, pkg_name)
            filenpa_conf=os.path.join(direpa_src, dy_app["filen_json_app"])

            filen_main=Json_config(os.path.join(direpa_src, dy_app["filen_json_app"])).data["filen_main"]

        direpa_dst=os.path.join(direpa_repo, pkg_name, pkg_version, pkg_name)

        if is_git is True:
            previous_branch=checkout_version(pkg_version, direpa_src)

        if conf_data is None:
            conf_data=Json_config(filenpa_conf).data

    if arg_str == "export_rel":
        conf_db=Json_config(os.path.join(direpa_repo, dy_app["filen_json_repo"]))
        if filenpa_conf is None:
            msg.error("filenpa_conf is None")
            sys.exit(1)
        if not os.path.exists(filenpa_conf):
            if previous_branch:
                checkout(previous_branch, direpa_src)
            msg.error("'{}' not found".format(filenpa_conf))
            sys.exit(1)
        else:
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
            else:
                conf_db.data["uuid4s"].update({dy_pkg_src["uuid4"]: dy_pkg_src["name"]})
            
            conf_db.data["pkgs"].update({
                "{}|{}|{}".format(dy_pkg_src["uuid4"], dy_pkg_src["name"], dy_pkg_src["version"]
                    ): dy_pkg_src["deps"]
            })

    if paths is None:
        if add_deps is False:
            added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]
        paths=get_paths_to_copy(direpa_src, added_rules=added_refine_rules)
    
    if arg_str == "export_bin":
        if diren_bin == "beta":
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            prompt_for_replace(direpa_dst)
    elif arg_str == "export_rel":
        prompt_for_replace(direpa_dst)

    msg.info("Copying from '{}' to '{}'".format(direpa_src, direpa_dst))
    copy_to_destination(paths, direpa_src, direpa_dst)
    if pkg_without_conf is True:
        data=Json_config(filenpa_conf).data
        data["version"]=pkg_version
        with open(os.path.join(direpa_dst, dy_app["filen_json_app"]), "w") as f:
            f.write(json.dumps( data,sort_keys=True, indent=4))

    if arg_str == "export_rel":
        conf_db.save()

    if arg_str == "export_bin":
        filenpa_exec=os.path.join(direpa_dst, filen_main)
        filenpa_symlink=os.path.join(direpa_bin, pkg_name)
        create_symlink(dy_app["platform"], filenpa_exec, filenpa_symlink )

    if previous_branch:
        checkout(previous_branch, direpa_src)

def get_paths_from_only_path(only_paths, paths, direpa_src):
    index_path=0
    tmp_only_paths=[]
    for elem in sorted(only_paths):
        path_elem=os.path.normpath(os.path.join(direpa_src, elem))
        found=False
        for path_all in paths[index_path:]:
            if path_elem in path_all:
                found=True
                tmp_only_paths.append(path_all)
                index_path+=1
            else:
                if found is True:
                    break
                else:
                    index_path+=1
    return tmp_only_paths


def checkout(branch, direpa_git):
    direpa_current=os.getcwd()
    dir_changed=False
    if direpa_current != direpa_git:
        os.chdir(direpa_git)
        dir_changed=True

    shell.cmd_prompt("git checkout "+branch)

    if dir_changed is True:
        os.chdir(direpa_current)

def checkout_version(version, direpa_git):
    direpa_current=os.getcwd()
    dir_changed=False
    if direpa_current != direpa_git:
        os.chdir(direpa_git)
        dir_changed=True

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
        msg.error("Version '{}' does not exist at path '{}'".format(
            version,
            direpa
        ))
        sys.exit(1)
    else:
        # checkout to export version
        previous_branch=subprocess.run(shlex.split("git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
        shell.cmd_prompt("git checkout v"+version)

    if dir_changed is True:
        os.chdir(direpa_current)
    return previous_branch
    
def prompt_for_replace(direpa_dst):
    if os.path.exists(direpa_dst):
        msg.warning("'{}' already exists.".format(direpa_dst))
        if prompt_boolean("Do you want to replace it", "Y"):
            shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            msg.warning("Operation Cancelled.")
            sys.exit(1)


