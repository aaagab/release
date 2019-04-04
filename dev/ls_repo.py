#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.3.0
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from dev.helpers import get_direpa_root, to_be_coded
from dev.refine import get_paths_to_copy, copy_to_destination
import dev.regex_obj as ro

import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean
from modules.json_config.json_config import Json_config
import modules.shell_helpers.shell_helpers as shell

# mockpackage 0.2.2
# mockpackage 0.2.3
# mockpackage beta

def ls_repo(dy_rel):
    pkg_names=dy_rel["args"]["ls_repo"]
    filenpa_db=os.path.join(dy_rel["direpa_release"], "db.json")
    pkg_ids=[]
    name_uuids={}
    for pkg_id in Json_config(filenpa_db).data:
        uuid4, pkg_name, version = pkg_id.split('|')
        name_uuids[pkg_name]=uuid4
        if pkg_names is True:
            pkg_ids.append("{}|{}".format(pkg_name, version))
        else:
            if pkg_name in pkg_names:
                pkg_ids.append("{}|{}".format(pkg_name, version))

    for pkg_id in sorted(pkg_ids):
        pkg_name, version = pkg_id.split('|')
        print("{}|{}|{}".format(name_uuids[pkg_name], pkg_name, version))