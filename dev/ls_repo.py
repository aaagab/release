#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .search import search

from ..gpkgs.json_config import Json_config

def ls_repo(dy_app, pkg_filters=[], add_deps=False):
    filenpa_json_repo=os.path.join(dy_app["direpa_repo"], dy_app["filen_json_repo"])
    pkg_name_and_versions=[]
    name_uuids={}
    db=Json_config(filenpa_json_repo).data

    selected_pkgs=[]
    if not pkg_filters:
        selected_pkgs=search(db["pkgs"], identify=True)
    else:
        for ftr in pkg_filters:
            selected_pkgs=search(db["pkgs"], pkg_filter=ftr, identify=True)

    for pkg in selected_pkgs:
        print(pkg["id"])
        if add_deps is True:
            deps=db["pkgs"][pkg["id"]]
            for dep in deps:
                print("\t", dep)
