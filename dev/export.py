#!/usr/bin/env python3
import contextlib
from pprint import pprint
import os
import re
import shlex
import shutil
import subprocess
import sys

from .check_repo import check_repo

from ..dev import regex_obj as ro
from ..dev.helpers import get_direpa_root, to_be_coded, get_app_meta_data, create_symlink

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt_boolean


    # from rel means from existing repository, it is supposed to be send to bin. so I don't have to export the code again.
    # it is not export bin then it is direpa_dst == bin
    # it is not export rel then it is direpa_dst == rel
    # you have different type of package, bin_package, git_package, rel_package. So according to one format to the other you have to do the conversion.
    # I already defined that in details in gpm......... 
    # to remove args
    # export should be direpa_src and direpa_dst and from there according to the destination and the source I know what to do.
    # the ideal would be from and to
    # for now I am not able to detect if release of other so it should be specify.
    # dy_pkg from path from-type repo to path to-type pkg,bin


# bin
# repo
# pkg


#  that is for later
# def export(
#     dy_app,
#     direpa_src,
#     direpa_dst,
#     src_type,
#     dst_type,
#     pkg_filters= [],
# ):

    # What about packages what form? provided or not?

    # pkgs, if no filters, grab



    # if src_type == "repo":
    #     if not pkg_filters:
    #         pass # grab all gpm packages
    #     else:
    #         for each pkgs get an a path and then for each path send to destination.
    #         I have to create locations
    #         create a location and then have all the data. needed.
    #     direpa_dst ==

    
    # elif src_type == "pkg":


    # if dst_type == "repo":

    # elif dst_type == "bin":
    
    # elif dst_type == "pkg":


# from_rel or --from-rel is when you want to send to bin from main repository
# path is when you export to release export_rel or export_bin to any destination. this one is not really clear

def export(dy_app,
    action, # export_bin, export_rel, to_repo
    add_deps=False,
    dy_pkg=None, 
    from_rel=False,
    no_symlink=False,
    path_dst=None,
    path_src=None,
    pkg_name=None,
    pkg_version=None,
    direpa_repo_dst=None,
):
    direpa_root=""
    if from_rel is True:
        direpa_root=os.path.join(dy_app["direpa_release"], pkg_name, pkg_version, pkg_name)
        if not os.path.exists(direpa_root):
            msg.error("Not found '{}'".format(direpa_root), exit=1)
    elif path_src is not None:
        direpa_root=get_direpa_root(path_src)
    else:
        if action != "to_repo":
            direpa_root=get_direpa_root()

    if from_rel is False and action != "to_repo" :
        os.chdir(direpa_root) # do I really need that
    # dy_pkg=None
    added_refine_rules=[]
    direpa_dst=""
    previous_branch=""
    direpa_bin=""
    insert_db=False


    if action == "export_rel":
        dy_pkg=get_app_meta_data(direpa_root)
        
        if add_deps is False:
            added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]

        if path_dst is None:
            if pkg_version is None:
                msg.error("You need to provide a release version with --pkg-version for export release")
                sys.exit(1)

            direpa_dst=os.path.join(dy_app["direpa_release"], dy_pkg["name"], pkg_version, dy_pkg["name"])
            prompt_for_replace(direpa_dst)

        
            previous_branch=checkout_version(pkg_version, direpa_root)
            insert_db=True
        else:
            direpa_dst_root=path_dst
            direpa_dst=os.path.join(direpa_dst_root, dy_pkg["name"])
            prompt_for_replace(direpa_dst)

            if pkg_version is not None:
                direpa_rel_version=os.path.join(dy_app["direpa_release"], dy_pkg["name"], pkg_version, dy_pkg["name"])
                if os.path.exists(direpa_rel_version): # if exists copy existing 
                    direpa_root=direpa_rel_version
                else: # else checkout a new one
                    previous_branch=checkout_version(pkg_version, direpa_root)

    elif action == "export_bin":
        dy_pkg=get_app_meta_data(direpa_root)

        if add_deps is True:
            msg.warning(
                "--add-deps is not an option for export to bin",
                "dependencies are included by default in this context."
                )

        added_refine_rules=[]
        if path_dst is None:
            direpa_bin=dy_app["direpa_bin"]
        else:
            direpa_bin=path_dst

        if pkg_version is None: # get current repository state
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_pkg["name"]),
                "beta", 
                dy_pkg["name"])
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else: # checkout at chosen version
            direpa_dst=os.path.join(
                direpa_bin, 
                "{}_data".format(dy_pkg["name"]),
                pkg_version, 
                dy_pkg["name"])

            prompt_for_replace(direpa_dst)
            if from_rel is False:
                previous_branch=checkout_version(pkg_version, direpa_root)
    elif action == "to_repo":
        direpa_root=os.path.join(dy_app["direpa_release"], dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
        direpa_dst=os.path.join(direpa_repo_dst, dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
        prompt_for_replace(direpa_dst)
        check_repo(dy_app, direpa_repo_dst)
        insert_db=True

    if insert_db:
        conf_db=None
        if action == "to_repo":
            conf_db=Json_config(os.path.join(direpa_repo_dst, dy_app["filen_json_repo"]))
        else:
            conf_db=Json_config(os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"]))
        
        filenpa_gpm_json=os.path.join(direpa_root, "gpm.json")
        if not os.path.exists(filenpa_gpm_json):
            if previous_branch:
                shell.cmd_prompt("git checkout "+previous_branch)
            msg.error("'{}' not found".format(filenpa_gpm_json))
            sys.exit(1)
        else:
            dy_pkg_src=Json_config(filenpa_gpm_json).data
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

    paths=get_paths_to_copy(direpa_root, added_rules=added_refine_rules)
    copy_to_destination(paths, direpa_root, direpa_dst)

    if insert_db:
        conf_db.save()

    if direpa_bin:
        if no_symlink is False:
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
        msg.error("Version '{}' does not exist at path '{}'".format(
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

