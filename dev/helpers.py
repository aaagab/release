#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.1.0
# name: release
# license: MIT
import os, shlex, sys
import subprocess
import modules.shell_helpers.shell_helpers as shell
import modules.message.message as msg

def get_direpa_root():
    if is_pkg_git():
        return subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()
    else:
        direpa_current=os.getcwd()
        direpa_src=os.path.join(direpa_current, "src")
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
