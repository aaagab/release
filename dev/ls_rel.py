#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .search import search
from .get_dy_pkg_filter import get_dy_pkg_filter

from ..gpkgs.json_config import Json_config

def ls_rel(
    direpa_rel,
    filen_json_rel,
    pkg_filters=[], 
    add_deps=False
):
    filenpa_json_rel=os.path.join(direpa_rel, filen_json_rel)
    db=Json_config(filenpa_json_rel).data

    selected_pkgs=[]
    if not pkg_filters:
        selected_pkgs=search(db["pkgs"], identify=True)
    else:

        for ftr in pkg_filters:
            ftr=get_dy_pkg_filter(pkg_filter=ftr, get_search_format=True)
            selected_pkgs=search(db["pkgs"], pkg_filter=ftr, identify=True)

    for pkg in selected_pkgs:
        print(pkg["id"])
        if add_deps is True:
            deps=db["pkgs"][pkg["id"]]
            for dep in deps:
                print("\t", dep)
