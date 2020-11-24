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
from .get_pkg_from_db import get_pkg_from_db
from .helpers import get_direpa_root, to_be_coded, get_app_meta_data, create_symlink

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt_boolean


# dy_locations={"from": {"type": None, "direpa": None}, "to":{"type": None, "direpa": None}}
# dy_default_direpas=dict(
#     bin=os.path.join(os.path.expanduser("~"), "fty", "bin"),
#     pkg=os.getcwd(),
#     rel=os.path.join(os.path.expanduser("~"), "fty", "rel"),
#     src=os.path.join(os.path.expanduser("~"), "fty", "src"),
#     wrk=os.path.join(os.path.expanduser("~"), "fty", "wrk"),
# )

def not_supported(direction, location):
    msg.error("Transfer not supported {}_{}".format(direction, location), exit=1)

def not_supported_with_value(direction, location, value):
    msg.error("Transfer not supported {}_{} with a custom value '{}'.".format(direction, location, value), exit=1)

def exit_on_same_location(direpa_from, direpa_to):
    if direpa_from == direpa_to:
        msg.error("Transfer not supported if from and to is the same location '{}'".format(direpa_from), exit=1)

def transfer(
    add_deps=False,
    diren_pkgs=None,
    dy_default_direpas=None,
    dy_locations=None,
    filen_json_app=None,
    filen_json_rel=None,
    filenpa_conf=None,
    is_beta=False,
    is_git=True,
    no_symlink=False,
    pkg_name=None,
    pkg_version=None,
    only_paths=[],
    system=None,
):
    
    
    from_=dy_locations["from"]["type"]
    to_=dy_locations["to"]["type"]
    direpa_from=dy_locations["from"]["direpa"]
    direpa_to=dy_locations["to"]["direpa"]
    # ["bin", "pkg", "rel", "src", "wrk"]
    # not_supported={"from": ["bin", "src", "wrk"], "to":["pkg", "src", "wrk"]}
    # not_supported_with_value={"from": ["pkg"], "to":[]}

    if from_ == "pkg":
        if to_ == "bin":
            if direpa_from is None:
                direpa_from=dy_default_direpas[from_]
            if direpa_to is None:
                direpa_to=dy_default_direpas[to_]
            exit_on_same_location(direpa_from, direpa_to)
            print(direpa_from)
            print(direpa_to)
        elif to_ == "rel":
            if direpa_from is None:
                direpa_from=dy_default_direpas[from_]
            if direpa_to is None:
                direpa_to=dy_default_direpas[to_]
            exit_on_same_location(direpa_from, direpa_to)
            print(direpa_from)
            print(direpa_to)
        else:
            not_supported("to", to_)
    elif from_ == "rel":
        if to_ == "bin":
            if direpa_from is None:
                pass
            if direpa_to is None:
                pass
        elif to_ == "rel":
            if direpa_from is None:
                direpa_from=dy_default_direpas[from_]
            if direpa_to is None:
                direpa_to=dy_default_direpas[to_]
            exit_on_same_location(direpa_from, direpa_to)
            print(direpa_from)
            print(direpa_to)
        else:
            not_supported("to", to_)
    else:
        not_supported("from", from_)

    sys.exit()    


    # removed 
    # transfer_as=None,
    # direpa_bin_dst=None,
    # direpa_rel_src=None,
    # direpa_rel_dst=None,
    # direpa_pkg=None,
    # from_pkg=False,
    

    # direpa_rel_src=dy_default_direpas["rel"]
    # if args.from_rel.here is True:
    #     if args.from_rel.value is not None:
    #         direpa_rel_src=args.from_rel.value


    # if transfer_as == "as_bin":
    #     direpa_bin_dst=dy_direpas["bin"]
    #     if args.to_bin.here is True:
    #         if args.to_bin.value is None:
    #             direpa_bin_dst=dy_direpas["bin"]
    #         else:
    #             direpa_bin_dst=args.to_bin.value

    #     options.update(
    #         direpa_bin_dst=direpa_bin_dst,
    #         is_beta=args.beta.here,
    #         no_symlink=args.no_symlink.here,
    #     )
        
    # elif transfer_as == "as_rel":
    #     direpa_rel_dst=dy_direpas["rel"]
    #     if args.to_rel.here is True:
    #         if args.to_rel.value is not None:
    #             direpa_rel_dst=args.to_rel.value
    #             check_rel(direpa_rel_dst)
        
    #     options.update( 
    #         add_deps=not args.no_deps.here,
    #         direpa_rel_dst=direpa_rel_dst,
    #     )

    sys.exit()    
    
    

    
    
    
    added_refine_rules=[]
    conf_data=None
    conf_db=None
    direpa_dst=None
    direpa_src=None
    pkg_without_conf=False
    paths=None
    previous_branch=None









    if from_pkg is True:
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

    if transfer_as == "as_bin":
        add_deps=True


        if from_pkg is True:
            if filenpa_conf is None:
                filenpa_conf=os.path.join(direpa_src, filen_json_app)
            conf_data=Json_config(filenpa_conf).data
            pkg_name=conf_data["name"]
            if is_beta is False and pkg_version is None:
                pkg_version=conf_data["version"]
        else:
            if pkg_version is None:
                chosen_pkg=get_pkg_from_db(
                    db_data=Json_config(os.path.join(direpa_rel_src, filen_json_rel)).data,
                    direpa_rel=direpa_rel_src,
                    filen_json_default=filen_json_app,
                    not_found_error=True,
                    not_found_exit=True,
                    pkg_filter=pkg_name,
                )
                pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(direpa_rel_src, pkg_name, pkg_version, pkg_name)
            conf_data=Json_config(os.path.join(direpa_src, filen_json_app)).data
        
        filen_main=conf_data["filen_main"]

        diren_bin=None
        if pkg_version is None: # get current repository state
            add_deps=True
            diren_bin="beta"
        else:
            diren_bin=pkg_version

        direpa_dst=os.path.join(
            direpa_bin_dst, 
            "{}_data".format(pkg_name),
            diren_bin,
            pkg_name
        )

        if filen_main is None:
            msg.error("filen_main not set, it should be set with --filen-main arg")
            sys.exit(1)
            
        if is_git is True and pkg_version is not None and from_pkg is True:
            previous_branch=checkout_version(pkg_version, direpa_src)

    elif transfer_as == "as_rel":
        if from_pkg is True:
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
                filenpa_conf=os.path.join(direpa_src, filen_json_app)
                if not os.path.exists(filenpa_conf): # search it in repo
                    if pkg_name is None:
                        msg.error("At least a package name needs to be provided with --pkg-name")
                        sys.exit(1)
                    else:
                        db_data=Json_config(os.path.join(direpa_rel_dst, filen_json_rel)).data
                        chosen_pkg=get_pkg_from_db(
                            db_data=db_data,
                            direpa_rel=direpa_rel_dst,
                            filen_json_default=filen_json_app, 
                            not_found_error=True,
                            not_found_exit=True,
                            pkg_filter=pkg_name,
                        )

                        filenpa_conf=os.path.join(direpa_rel_dst, pkg_name, chosen_pkg["version"], pkg_name, filen_json_app)

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
                            diren_pkgs=diren_pkgs,
                            direpa_rel=direpa_rel_dst,
                            filen_json_app=filen_json_app, 
                            filenpa_conf=filenpa_conf,
                            increment=True,
                            is_git=False,
                            only_paths=paths,
                            pkg_name=pkg_name,
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
            if direpa_rel_src == direpa_rel_dst:
                msg.error("direpa_rel_src and direpa_rel_dst are the same '{}'".format(direpa_rel_src),
                "set --to-rel with a different path")
                sys.exit(1)

            pkg_filter=None
            if pkg_version is None:
                pkg_filter=pkg_name
            else:
                pkg_filter="{},{}".format(pkg_name, pkg_version)

            chosen_pkg=get_pkg_from_db(
                db_data=Json_config(os.path.join(direpa_rel_src, filen_json_rel)).data,
                direpa_rel=direpa_rel_src,
                filen_json_default=filen_json_app, 
                not_found_error=True,
                not_found_exit=True,
                pkg_filter=pkg_filter,
            )

            pkg_version=chosen_pkg["version"]
            direpa_src=os.path.join(direpa_rel_src, pkg_name, pkg_version, pkg_name)
            filenpa_conf=os.path.join(direpa_src, filen_json_app)
            filen_main=Json_config(os.path.join(direpa_src, filen_json_app)).data["filen_main"]

        direpa_dst=os.path.join(direpa_rel_dst, pkg_name, pkg_version, pkg_name)

        if is_git is True:
            previous_branch=checkout_version(pkg_version, direpa_src)

        if conf_data is None:
            conf_data=Json_config(filenpa_conf).data

    if transfer_as == "as_rel":
        conf_db=Json_config(os.path.join(direpa_rel_dst, filen_json_rel))
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
    
    if transfer_as == "as_bin":
        if diren_bin == "beta":
            if os.path.exists(direpa_dst):
                shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            prompt_for_replace(direpa_dst, previous_branch, direpa_src)
    elif transfer_as == "as_rel":
        prompt_for_replace(direpa_dst, previous_branch, direpa_src)

    msg.info("Copying from '{}' to '{}'".format(direpa_src, direpa_dst))
    copy_to_destination(paths, direpa_src, direpa_dst)
    if pkg_without_conf is True:
        data=Json_config(filenpa_conf).data
        data["version"]=pkg_version
        with open(os.path.join(direpa_dst, filen_json_app), "w") as f:
            f.write(json.dumps( data,sort_keys=True, indent=4))

    if transfer_as == "as_rel":
        conf_db.save()

    if transfer_as == "as_bin":
        if no_symlink is False:
            filenpa_exec=os.path.join(direpa_dst, filen_main)
            filenpa_symlink=os.path.join(direpa_bin_dst, pkg_name)
            create_symlink(system, filenpa_exec, filenpa_symlink )

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
            direpa_git,
        ))
        sys.exit(1)
    else:
        # checkout to export version
        previous_branch=subprocess.run(shlex.split("git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
        shell.cmd_prompt("git checkout v"+version)

    if dir_changed is True:
        os.chdir(direpa_current)
    return previous_branch
    
def prompt_for_replace(direpa_dst, previous_branch=None, direpa_src=None):
    if os.path.exists(direpa_dst):
        msg.warning("'{}' already exists.".format(direpa_dst))
        if prompt_boolean("Do you want to replace it", "Y"):
            shutil.rmtree(direpa_dst)
            os.makedirs(direpa_dst, exist_ok=True)
        else:
            if previous_branch:
                checkout(previous_branch, direpa_src)
            msg.warning("Operation Cancelled.")
            sys.exit(1)


