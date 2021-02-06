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
from .helpers import get_direpa_root, to_be_coded, create_symlink
from .get_filenpa_conf_from_rel import get_filenpa_conf_from_rel
from .transfer_to import transfer_to_bin, transfer_to_rel


from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs.prompt import prompt_boolean, prompt

def not_supported(direction, location):
    msg.error("Transfer not supported {}_{}".format(direction, location), exit=1)

def not_supported_with_value(direction, location, value):
    msg.error("Transfer not supported {}_{} with a custom value '{}'.".format(direction, location, value), exit=1)

def exit_on_same_location(direpa_from, direpa_to):
    if direpa_from == direpa_to:
        msg.error("Transfer not supported if 'from' and 'to' are on the same location '{}'".format(direpa_from), exit=1)

def transfer(
    add_deps=False,
    conf_from_rel=None,
    diren_pkgs=None,
    dy_default_direpas=None,
    dy_locations=None,
    dy_pkg_filter=None,
    filen_json_app=None,
    filen_json_rel=None,
    filen_main=None,
    filenpa_conf=None,
    is_beta=False,
    is_git=True,
    no_conf=False,
    no_symlink=False,
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

    refine_rules=["/modules/", "/.pkgs/", "/upacks/", "/gpkgs/"]
    added_refine_rules=[]

    if from_ == "pkg":
        if direpa_from is None:
            if is_git is True:
                direpa_from=get_direpa_root()
            else:
                direpa_from=dy_default_direpas[from_]
        else:
            if is_git is True:
                direpa_from=get_direpa_root(direpa_from)

        if no_conf is False:
            if conf_from_rel is not None:
                if conf_from_rel is True:
                    conf_from_rel=dy_default_direpas["rel"]
                filenpa_conf=get_filenpa_conf_from_rel(dy_pkg_filter["alias"], dy_pkg_filter["version"], conf_from_rel, filen_json_rel, filen_json_app)
            elif filenpa_conf is None:
                filenpa_conf=os.path.join(direpa_from, filen_json_app)
        
            if not os.path.exists(filenpa_conf):
                msg.error("filenpa_conf not found '{}'".format(filenpa_conf), exit=1)
        
        if direpa_to is None:
            direpa_to=dy_default_direpas[to_]
        exit_on_same_location(direpa_from, direpa_to)
        
        if to_ == "bin":
            transfer_to_bin(
                added_refine_rules,
                direpa_from,
                direpa_to,
                filen_main,
                filenpa_conf,
                is_beta,
                is_git,
                no_conf,
                no_symlink,
                dy_pkg_filter["alias"],
                dy_pkg_filter["version"],
                system,
            )
        elif to_ == "rel":
            if no_conf is True:
                msg.error("--no-conf can't be used with --to-rel", exit=1)
            transfer_to_rel(
                add_deps,
                added_refine_rules,
                direpa_from,
                direpa_to,
                filen_json_rel,
                filenpa_conf,
                is_git,
                dy_pkg_filter["alias"],
                dy_pkg_filter["version"],
            )
        else:
            not_supported("to", to_)
    elif from_ == "rel":
        if direpa_from is None:
            direpa_from=dy_default_direpas[from_]
        if direpa_to is None:
            direpa_to=dy_default_direpas[to_]
        exit_on_same_location(direpa_from, direpa_to)

        if dy_pkg_filter["alias"] is None:
            msg.error("package alias needs to be provided", exit=1)

        direpa_rel=direpa_from

        chosen_pkg=get_pkg_from_db(
            db_data=Json_config(os.path.join(direpa_rel, filen_json_rel)).data,
            direpa_rel=direpa_rel,
            filen_json_default=filen_json_app,
            not_found_error=True,
            not_found_exit=True,
            pkg_alias=dy_pkg_filter["alias"],
            pkg_version=dy_pkg_filter["version"],
        )

        pkg_version=chosen_pkg["version"]
        direpa_from=os.path.join(direpa_rel, dy_pkg_filter["alias"], pkg_version, dy_pkg_filter["alias"])
        filenpa_conf=os.path.join(direpa_from, filen_json_app)
        
        is_git=False
        if to_ == "bin":
            transfer_to_bin(
                added_refine_rules,
                direpa_from,
                direpa_to,
                filen_main,
                filenpa_conf,
                is_beta,
                is_git,
                no_conf,
                no_symlink,
                dy_pkg_filter["alias"],
                pkg_version,
                system,
            )
        elif to_ == "rel":
            transfer_to_rel(
                add_deps,
                added_refine_rules,
                direpa_from,
                direpa_to,
                filen_json_rel,
                filenpa_conf,
                is_git,
                dy_pkg_filter["alias"],
                pkg_version,
            )
        else:
            not_supported("to", to_)
    else:
        not_supported("from", from_)
    