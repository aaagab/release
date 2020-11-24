#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import shutil

from .search import search
from . import regex_obj as ro

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_multiple

# ./__init__.py -i message,a.a.a prompt

def get_dy_pkg_filter(
    pkg_filter=None,
    get_search_format=False,
):
    dy_pkg=dict(
        bound=None,
        name=None,
        uuid4=None,
        version=None,
        version_regex=None,
    )

    if pkg_filter is not None:
        for elem in pkg_filter.split(","):
            reg_version=ro.Version_filter_regex(elem)
            if reg_version.match:
                dy_pkg["version"]=elem
                dy_pkg["version_regex"]=reg_version
            elif ro.Uuid4_regex(elem).match:
                dy_pkg["uuid4"]=elem
            elif elem in ["gpm", "sys"]:
                dy_pkg["bound"]=elem
            else:
                if ro.Package_name_regex(elem).match:
                    dy_pkg["name"]=elem
                else:
                    msg.error("In pkg filter value unknown '{}'".format(elem), exit=1)
    
    if get_search_format is True:
        search_formats=[]
        for key, value in dy_pkg.items():
            if value is not None and key != "version_regex":
                search_formats.append("{}:{}".format(key[0], value))
        return ",".join(search_formats)
    else:
        return dy_pkg


