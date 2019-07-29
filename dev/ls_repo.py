#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.5.0
# name: release
# license: MIT
import os, sys
from pprint import pprint

from ..modules.json_config.json_config import Json_config
from .search import search

def ls_repo(dy_app):
    pkg_filters=dy_app["args"]["ls_repo"]
    filenpa_json_repo=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
    pkg_name_and_versions=[]
    name_uuids={}
    db=Json_config(filenpa_json_repo).data

    selected_pkgs=[]
    if pkg_filters is True:
        selected_pkgs=search(db["pkgs"], [])
    else:
        for ftr in pkg_filters:
            selected_pkgs=search(db["pkgs"], ftr)

    for pkg in selected_pkgs:
        print(pkg["id"])
        if dy_app["args"]["add_deps"] is True:
            deps=db["pkgs"][pkg["id"]]
            for dep in deps:
                print("\t", dep)
