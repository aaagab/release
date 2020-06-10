#!/usr/bin/env python3
import json
import os
from pprint import pprint
import re
import shutil
import sys

from .generate_db import generate_db

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.sort_separated import sort_separated


# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def repo_strip(dy_app, pkg_names):

    # pprint(dy_app)
    # print(pkg_names)
    if pkg_names:
        pkg_names=pkg_names
    else:
        pkg_names=os.listdir(dy_app["direpa_release"])

    packagesRemoved=False
    for pkg_name in sorted(pkg_names):
        direpa_pkg=os.path.join(dy_app["direpa_release"], pkg_name)
        if os.path.exists(direpa_pkg) and os.path.isdir(direpa_pkg):
            versions=os.listdir(direpa_pkg)
            if len(versions) > 1:
                versions=sort_separated(versions)
                versions.pop()
                for version in versions:
                    packagesRemoved=True
                    direpa_version=os.path.join(direpa_pkg, version)
                    shutil.rmtree(direpa_version)
                    msg.success("package removed {} {}".format(pkg_name, version))

    if packagesRemoved is True:
        generate_db(dy_app)



        # if os.path.exists()
    # pkg_
    # filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    # db=Json_config(filenpa_json_repo).data
    # for pkg_filter in pkg_filters:
    #     chosen_pkg=get_pkg_from_db(db, dy_app, pkg_filter)
    #     if chosen_pkg is None:
    #         continue
    #     else:
    #         export(dy_app, "to_repo", dy_pkg=chosen_pkg, direpa_repo_dst=direpa_rel)      
   
