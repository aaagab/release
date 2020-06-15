#!/usr/bin/env python3
from pprint import pprint
import os
import shutil
import sys

from .search import search

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_multiple

# ./__init__.py -i message,a.a.a prompt

def choose_pkg_cli(dy_app, action, pkg_filter):
    filenpa_json_repo=os.path.join(dy_app["direpa_repo"], dy_app["filen_json_repo"])
    db=Json_config(filenpa_json_repo).data
    
    components=pkg_filter.split(",")
    name=components[0]
    version=""
    bound=""
    if len(components) == 2:
        version=components[1]
    elif len(components) == 3:
        bound=components[2]

    tmp_filter="n:{}".format(name)
    if version:
        tmp_filter+=",v:{}".format(version)
    else:
        tmp_filter+=",v:L.L.L"

    selected_pkgs=search(db["pkgs"], tmp_filter)
    chosen_pkg={}
    if len(selected_pkgs) == 1:
        chosen_pkg={
            "name": name,
            "uuid4": selected_pkgs[0]["uuid4"],
            "version": selected_pkgs[0]["version"]
        }
    else:
        uuid4s=[]
        for pkg in selected_pkgs:
            if pkg["uuid4"] not in uuid4s:
                uuid4s.append(pkg["uuid4"])

        chosen_uuid4=""
        if len(uuid4s) == 1:
            chosen_uuid4=uuid4s[0]
        else:
            items=[]
            for uuid4 in uuid4s:
                pkg_version=[pkg["version"] for pkg in selected_pkgs if pkg["uuid4"] == uuid4][-1]
                filenpa_description=os.path.join(dy_app["direpa_repo"], name, pkg_version, name, dy_app["filen_json_app"])
                description=""
                if os.path.exists(filenpa_description):
                    description=Json_config(filenpa_description).data["description"]

                items.append("{} {}\n\t{}".format(db["uuid4s"][uuid4], uuid4, description))

            chosen_uuid4=prompt_multiple(
                dict(
                    items=items,
                    title="Select a package",
                    values=uuid4s
                ))
                                
        versions=[pkg["version"] for pkg in selected_pkgs if pkg["uuid4"] == chosen_uuid4]
        chosen_version=""

        if len(versions) == 1:
            chosen_version=versions[0]
        else:
            items=[]
            for version in versions:
                items.append("{} {}".format(name, version))

            chosen_version=prompt_multiple(
                dict(
                    items=items,
                    title="Select a version for pkg '{}'".format(name),
                    values=versions
                ))

            chosen_pkg={
                "name": name,
                "uuid4": chosen_uuid4,
                "version": chosen_version
            }
            
    if bound:
        bounds=["gpm", "sys"]
        if bound not in bounds:
            msg.error("For filter '{}' bound '{}' not in ['{}']".format(pkg_filter, bound, "', '".join(bounds)))
            sys.exit(1)
    else:
        bound="gpm"

    chosen_pkg.update(dict(bound=bound))

    return chosen_pkg
