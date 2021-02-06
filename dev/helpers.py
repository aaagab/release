#!/usr/bin/env python3
import contextlib
import os
import shlex
import subprocess
import sys

from . import regex_obj as ro

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean

def get_direpa_root(direpa_pkg=None):
    direpa_current=None
    if direpa_pkg is None:
        direpa_pkg=os.getcwd()
    else:
        if direpa_pkg != os.getcwd():
            direpa_current=os.getcwd()
            os.chdir(direpa_pkg)

    if is_pkg_git(direpa_pkg) is False:
        msg.error("'{}' is not a git repository".format(direpa_pkg))
        sys.exit(1)

    direpa_root=subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()
    if direpa_current is not None:
        os.chdir(direpa_current)

    return direpa_root

def append_path_to_ignore_paths(preset, direpa_root):
    for i, path in enumerate(preset["paths"]):
        if not os.path.isabs(path):
            preset["paths"][i]=os.path.join(direpa_root, path)

def is_pkg_git(direpa_pkg):
    if not os.path.exists(direpa_pkg):
        return False

    direpa_current=None
    if direpa_pkg != os.getcwd():
        direpa_current=os.getcwd()
        os.chdir(direpa_pkg)
    
    is_git=shell.cmd_devnull("git rev-parse --git-dir") == 0

    if direpa_current is not None:
        os.chdir(direpa_current)

    return is_git

def to_be_coded(text=""):
    if not text:
        msg.error("To be coded")
    else:
        msg.error("To be coded: '{}'".format(text))
    sys.exit(1)

def create_symlink(system, filenpa_exec, filenpa_symlink ):
    if system == "Windows":
        if os.path.splitext(filenpa_symlink)[1] == "":
            filenpa_symlink=filenpa_symlink+".py"
        
    with contextlib.suppress(FileNotFoundError):
        os.remove(filenpa_symlink)

    curdir=os.getcwd()
    os.chdir(os.path.dirname(filenpa_symlink))
    filenrel_exec=os.path.relpath(filenpa_exec, os.path.dirname(filenpa_symlink))

    if system == "Linux":
        # >>> os.symlink("mgt/file.txt", "file.txt")
        os.symlink(filenrel_exec, os.path.basename(filenpa_symlink))
    elif system == "Windows":
        #  mklink launch.pyw mgt\launch.pyw
        cmd='mklink "{}" "{}"'.format(os.path.basename(filenpa_symlink), filenrel_exec)
        if os.system(cmd) != 0:
            print("Error When creating link '{}'".format(filenpa_symlink))
            sys.exit(1)
    
    os.chdir(curdir)
    msg.success("symlink '{}' set.".format(filenpa_symlink))

def get_pkg_id(dy_pkg, **added):
    if added:
        dy_pkg.update(added)

    alias=None
    if "alias" in dy_pkg:
        alias=dy_pkg["alias"]
    else:
        alias=dy_pkg["name"]

    return "{}|{}|{}".format(dy_pkg["uuid4"], alias, dy_pkg["version"])
