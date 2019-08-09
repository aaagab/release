#!/usr/bin/env python3
import json
import os
from pprint import pprint
import re
import sys

from . import regex_obj as ro
from .export import export
from .filter_version import filter_version
from .helpers import get_pkg_id
from .get_pkg_from_db import get_pkg_from_db

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.sort_separated import sort_separated

# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def to_repo(dy_app, direpa_rel, pkg_filters):
    filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    db=Json_config(filenpa_json_repo).data
    for pkg_filter in pkg_filters:
        chosen_pkg=get_pkg_from_db(db, dy_app, pkg_filter)
        if chosen_pkg is None:
            continue
        else:
            export(dy_app, "to_repo", dy_pkg=chosen_pkg, direpa_repo_dst=direpa_rel)      
   
