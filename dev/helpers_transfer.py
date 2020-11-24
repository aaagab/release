#!/usr/bin/env python3
from pprint import pprint
import os
import re
import shlex
import shutil
import subprocess
import sys

from . import regex_obj as ro

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean, prompt

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

def checkout(branch, direpa_git):
    direpa_current=os.getcwd()
    dir_changed=False
    if direpa_current != direpa_git:
        os.chdir(direpa_git)
        dir_changed=True

    shell.cmd_prompt("git checkout "+branch)

    if dir_changed is True:
        os.chdir(direpa_current)