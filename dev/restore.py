#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.1.0
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint
import shutil
import json

from .import_pkgs import import_pkgs

from ..gpkgs import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell
from . import regex_obj as ro
from .filter_version import filter_version
from .helpers import get_pkg_id, get_direpa_root
from ..gpkgs.sort_separated import sort_separated
from .get_pkg_from_db import get_pkg_from_db
from .search import search


from .export import export


# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def restore(dy_app, args):
    filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    db=Json_config(filenpa_json_repo).data

    filenpa_json_app=os.path.join(get_direpa_root(), dy_app["filen_json_app"])
    dy_app_cwd=Json_config(filenpa_json_app).data
    dep_pkgs={}
    # get_already_installed packages:
    # direpa_gpkgs=os.path.join(get_direpa_root(), dy_app["diren_pkgs"])
    # existing_pkgs={}
    # if os.path.exists(direpa_gpkgs):
    #     for elem in os.listdir(direpa_gpkgs):
    #         direpa_pkg=os.path.join(direpa_gpkgs, elem)
    #         filenpa_json_tmp=os.path.join(direpa_pkg, dy_app["filen_json_app"])
    #         if os.path.exists(filenpa_json_tmp):
    #             dy_app_tmp=Json_config(filenpa_json_tmp).data
    #             existing_pkgs.update({
    #                 dy_app_tmp["uuid4"]: {
    #                     "name": dy_app_tmp["name"],
    #                     "version": dy_app_tmp["version"],
    #                     "direpa": direpa_pkg,
    #                 }
    #             })

    for dep in dy_app_cwd["deps"]:
        uuid4, name, version, bound = dep.split("|")
        import_pkgs(dy_app, ["{},{}".format(name,version)], action="restore")
