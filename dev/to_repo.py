#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.3
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint
import json

from ..modules.message import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell
from . import regex_obj as ro
from .filter_version import filter_version
from .helpers import get_pkg_id
from ..gpkgs.sort_separated import sort_separated
from .get_pkg_from_db import get_pkg_from_db
from .export import export


# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def to_repo(dy_app, args):
    filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    db=Json_config(filenpa_json_repo).data
    pkg_filters=dy_app["args"]["packages"]
    direpa_rel=dy_app["args"]["to_repo"][0]
    for pkg_filter in pkg_filters:
        chosen_pkg=get_pkg_from_db(db, dy_app, pkg_filter)
        if chosen_pkg is None:
            continue
        else:
            export(dy_app, args, chosen_pkg, direpa_rel)      
   
