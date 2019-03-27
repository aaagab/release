#!/usr/bin/env python3
# author: Gabriel Auger
# version: 0.1.0
# name: release
# license: MIT
import sys
import os
import subprocess
import modules.shell_helpers.shell_helpers as shell

def get_direpa_root():
    return subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()

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