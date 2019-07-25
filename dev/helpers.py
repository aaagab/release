#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.3
# name: release
# license: MIT
import os, shlex, sys
import contextlib
import subprocess
from ..modules.shell_helpers import shell_helpers as shell
# from modules.message import message as msg
from ..modules.message import message as msg
# from import 
from ..modules.json_config.json_config import Json_config


def get_direpa_root(path=""):
    if is_pkg_git(path):
        direpa_current=""
        if path:
            direpa_current=os.getcwd()
            os.chdir(path)

        direpa_root=subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()
        if path:
            os.chdir(direpa_current)

        return direpa_root
    else:
        direpa_current==os.getcwd()

        if not path:
            path=direpa_current

        direpa_src=os.path.join(path, "src")
        if os.path.exists(direpa_src):
            if is_pkg_git(direpa_src):
                os.chdir(direpa_src)
                direpa_root=subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()
                os.chdir(direpa_current)
                return direpa_root
            else:
                msg.user_error("In '{}' src exists however".format(os.getcwd()))

        msg.app_error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)

def append_path_to_ignore_paths(preset, direpa_root):
    for i, path in enumerate(preset["paths"]):
        if not os.path.isabs(path):
            preset["paths"][i]=os.path.join(direpa_root, path)

def is_pkg_git(path=""):
    start_path=""
    git_directory_found=False

    if path:
        if os.path.exists(path):
            start_path=os.getcwd()
            os.chdir(path)
        else:
            return False

    if shell.cmd_devnull("git rev-parse --git-dir") == 0:
        git_directory_found=True

    if path:
        os.chdir(start_path)

    if not git_directory_found:
        return False
    else:
        return True

def to_be_coded(text=""):
    if not text:
        msg.app_error("To be coded")
    else:
        msg.app_error("To be coded: '{}'".format(text))
    sys.exit(1)

def create_symlink(platform, filenpa_exec, filenpa_symlink ):
    if platform == "Windows":
        if os.path.splitext(filenpa_symlink)[1] == "":
            filenpa_symlink=filenpa_symlink+".py"
        
    with contextlib.suppress(FileNotFoundError):
        os.remove(filenpa_symlink)
    
    if platform == "Linux":
        os.symlink( filenpa_exec, filenpa_symlink)
    elif platform == "Windows":
        cmd='mklink "{}" "{}"'.format(filenpa_symlink, filenpa_exec)
        if os.system(cmd) != 0:
            print("Error When creating link '{}'".format(filenpa_symlink))
            sys.exit(1)
    
    msg.success("symlink '{}' set.".format(filenpa_symlink))


def get_app_meta_data(direpa_root):
    keys=["name", "filen_main", "version"]
    filenpa_conf=os.path.join(direpa_root, "gpm.json")
    if os.path.exists(filenpa_conf):
        data=Json_config(filenpa_conf).data
        all_key_found=True
        for key in keys:
            if not key in data:
                msg.warning("Missing '{}' in '{}'".format(key, filenpa_conf))
                all_key_found=False

        if all_key_found:
            if "options" in data:
                del data["options"]
            return data
        else:
            sys.exit(1)

    else:
        msg.user_error(
            "'{}' not found".format(filenpa_conf),
            "Run 'gpm --init --no-db'")
        sys.exit(1)   

def get_pkg_id(dy_pkg, **added):
    if added:
        dy_pkg.update(added)

    return "{}|{}|{}".format(dy_pkg["uuid4"], dy_pkg["name"], dy_pkg["version"])
