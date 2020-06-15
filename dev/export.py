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


def export(
    dy_app,
    action, # export_bin, export_rel, to_repo
    add_deps=False,
    dy_pkg=None,
    filenpa_conf=None,
    is_git=True, 
    # path_dst=None,
    # path_src=None,
    pkg_name=None,
    pkg_version=None,
    direpa_repo_dst=None,
    
    from_repo=None,
    direpa_bin=None,
    direpa_repo=None,
    direpa_pkg=None,
    filen_main=None,
):
    # --path-bin
    # --path-repo
    # path_dst must be local, path_src must be local too,
    # path_pkg if not in path.
    # --path-pkg
    # --filenpa-conf
    # not_git
    # path_dst
    # actually the to-repo is an export rel to another repo, so to repo must be --path-repo --to-repo

    direpa_src=None
    direpa_dst=None

    previous_branch=None
    added_refine_rules=[]

    conf_db=None

    if action == "export_bin":
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
        # else:
        #     direpa_src=from_repo
        
        if from_repo is None:
            if filenpa_conf is None:
                filenpa_conf=os.path.join(direpa_src, dy_app["filen_json_app"])
            conf_data=Json_config(filenpa_conf).data
            pkg_name=conf_data["name"]
            filen_main=conf_data["filen_main"]
        else:
            if pkg_version is None:
                chosen_pkg=get_pkg_from_db(
                    db_data=Json_config(os.path.join(direpa_repo, dy_app["filen_json_repo"])),
                    direpa_repo=direpa_repo,
                    filen_json_default=dy_app["filen_json_app"], 
                    pkg_filter=pkg_name,
                )
                pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(direpa_repo, pkg_name, pkg_version, pkg_name)
            filen_main=Json_config(os.path.join(direpa_src, dy_app["filen_json_app"])).data["filen_main"]

        diren_bin=None
        if pkg_version is None: # get current repository state
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
            previous_branch=checkout_version(pkg_version, direpa_root)

    elif action == "export_rel":
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
                        chosen_pkg=get_pkg_from_db(
                            db_data=Json_config(os.path.join(direpa_repo, dy_app["filen_json_repo"])),
                            direpa_repo=direpa_repo,
                            filen_json_default=dy_app["filen_json_app"], 
                            pkg_filter=pkg_name,
                        )
                        if chosen_pkg is None:
                            msg.error("No package found with name '{}' at '{}'".format(pkg_name, direpa_repo))
                            sys.exit(1) 
                        else:
                            pkg_version=chosen_pkg["version"]
                            filenpa_conf=os.path.join(direpa_repo, pkg_name, pkg_version, pkg_name, dy_app["filen_json_app"])

            conf_data=Json_config(filenpa_conf).data
            pkg_name=conf_data["name"]
            filen_main=conf_data["filen_main"]
            if pkg_version is None:
                pkg_version=conf_data["version"]
        else:
            is_git=False
            if direpa_repo == from_repo:
                msg.error("direpa_repo and from_repo are the same '{}'".format(direpa_src))
                sys.exit(1)

            if pkg_version is None:
                chosen_pkg=get_pkg_from_db(
                    db_data=Json_config(os.path.join(from_repo, dy_app["filen_json_repo"])),
                    direpa_repo=from_repo,
                    filen_json_default=dy_app["filen_json_app"], 
                    pkg_filter=pkg_name,
                )
                pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(from_repo, pkg_name, pkg_version, pkg_name)
            filen_main=Json_config(os.path.join(direpa_src, dy_app["filen_json_app"])).data["filen_main"]


        # dy_pkg=get_app_meta_data(dy_app["filen_json_app"], filenpa_conf)


        direpa_dst=os.path.join(direpa_repo, pkg_name, pkg_version, pkg_name)

        if is_git is True:
            previous_branch=checkout_version(pkg_version, direpa_root)

        if add_deps is False:
            added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]

        # if path_dst is None:
        #     if pkg_version is None:
        #         msg.error("You need to provide a release version with --pkg-version for export release")
        #         sys.exit(1)

            # direpa_dst=os.path.join(dy_app["direpa_repo"], dy_pkg["name"], pkg_version, dy_pkg["name"])
        # prompt_for_replace(direpa_dst)


        #     insert_db=True
        # else:
        #     direpa_dst_root=path_dst
        #     direpa_dst=os.path.join(direpa_dst_root, dy_pkg["name"])
        #     prompt_for_replace(direpa_dst)

        #     if pkg_version is not None:
        #         direpa_rel_version=os.path.join(dy_app["direpa_repo"], dy_pkg["name"], pkg_version, dy_pkg["name"])
        #         if os.path.exists(direpa_rel_version): # if exists copy existing 
        #             direpa_root=direpa_rel_version
        #         else: # else checkout a new one
        #             if is_git is True:
        #                 previous_branch=checkout_version(pkg_version, direpa_root)

        
    if action == "export_rel":
        if action == "to_repo":
            conf_db=Json_config(os.path.join(direpa_repo_dst, dy_app["filen_json_repo"]))
        else:
            conf_db=Json_config(os.path.join(dy_app["direpa_repo"], dy_app["filen_json_repo"]))
        
        # filenpa_conf=os.path.join(direpa_root, "gpm.json")
        if not os.path.exists(filenpa_conf):
            if previous_branch:
                shell.cmd_prompt("git checkout "+previous_branch)
            msg.error("'{}' not found".format(filenpa_conf))
            sys.exit(1)
        else:
            dy_pkg_src=Json_config(filenpa_conf).data
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


    paths=get_paths_to_copy(direpa_src, added_rules=added_refine_rules)
    if action == "export_bin":
        if diren_bin == "beta":
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            prompt_for_replace(direpa_dst)
    elif action == "export_rel":
        prompt_for_replace(direpa_dst)

    copy_to_destination(paths, direpa_src, direpa_dst)

    if action == "export_rel":
        conf_db.save()

    if action == "export_bin":
        filenpa_exec=os.path.join(direpa_dst, filen_main)
        filenpa_symlink=os.path.join(direpa_bin, pkg_name)
        create_symlink(dy_app["platform"], filenpa_exec, filenpa_symlink )

    if previous_branch:
        shell.cmd_prompt("git checkout "+previous_branch)

    

    sys.exit()
    # direpa_root=""
    # if from_repo is True:
    #     direpa_root=os.path.join(dy_app["direpa_repo"], pkg_name, pkg_version, pkg_name)
    #     if not os.path.exists(direpa_root):
    #         msg.error("Not found '{}'".format(direpa_root), exit=1)
    # elif path_src is not None:
    #     direpa_root=get_direpa_root(path_src)
    # else:
    #     if is_git is False:
    #         direpa_root=os.getcwd()
    #     elif action == "to_repo":
    #         direpa_root=os.path.join(dy_app["direpa_repo"], dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
    #     else:
    #         direpa_root=get_direpa_root()

    # if filenpa_conf is None:
    #     filenpa_conf=os.path.join(direpa_root, dy_app["filen_json_app"])
        

    # if from_repo is False and action != "to_repo" :
        # os.chdir(direpa_root) # do I really need that
    # dy_pkg=None
    # added_refine_rules=[]
    # direpa_dst=""
    # previous_branch=""
    # direpa_bin=""
    # insert_db=False

    # if action == "export_rel":
    #     dy_pkg=get_app_meta_data(dy_app["filen_json_app"], filenpa_conf)
        
    #     if add_deps is False:
    #         added_refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]

    #     if path_dst is None:
    #         if pkg_version is None:
    #             msg.error("You need to provide a release version with --pkg-version for export release")
    #             sys.exit(1)

    #         direpa_dst=os.path.join(dy_app["direpa_repo"], dy_pkg["name"], pkg_version, dy_pkg["name"])
    #         prompt_for_replace(direpa_dst)

    #         if is_git is True:
    #             previous_branch=checkout_version(pkg_version, direpa_root)
    #         insert_db=True
    #     else:
    #         direpa_dst_root=path_dst
    #         direpa_dst=os.path.join(direpa_dst_root, dy_pkg["name"])
    #         prompt_for_replace(direpa_dst)

    #         if pkg_version is not None:
    #             direpa_rel_version=os.path.join(dy_app["direpa_repo"], dy_pkg["name"], pkg_version, dy_pkg["name"])
    #             if os.path.exists(direpa_rel_version): # if exists copy existing 
    #                 direpa_root=direpa_rel_version
    #             else: # else checkout a new one
    #                 if is_git is True:
    #                     previous_branch=checkout_version(pkg_version, direpa_root)

   
    # elif action == "to_repo":
    #     direpa_dst=os.path.join(direpa_repo_dst, dy_pkg["name"], dy_pkg["version"], dy_pkg["name"])
    #     prompt_for_replace(direpa_dst)
    #     # check_repo(dy_app, direpa_repo_dst)
    #     check_repo(
    #         filen_repo_default=dy_app["filen_json_repo"],
    #         direpa_repo=direpa_repo_dst,
    #     )
    #     insert_db=True

   

    # paths=get_paths_to_copy(direpa_root, added_rules=added_refine_rules)
    # copy_to_destination(paths, direpa_root, direpa_dst)

    # if insert_db:
    #     conf_db.save()

  
    # if previous_branch:
    #     shell.cmd_prompt("git checkout "+previous_branch)

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

