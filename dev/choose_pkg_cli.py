#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from .search import search

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_multiple

# ./__init__.py -i message,a.a.a prompt

def choose_pkg_cli(
    direpa_rel,
    filen_json_rel,
    filen_json_app, 
    pkg_filter
):
    filenpa_json_rel=os.path.join(direpa_rel, filen_json_rel)
    db=Json_config(filenpa_json_rel).data
    
    components=pkg_filter.split(",")
    alias=components[0]
    version=""
    bound=""
    if len(components) == 2:
        version=components[1]
    elif len(components) == 3:
        bound=components[2]

    tmp_filter="a:{}".format(alias)
    if version:
        tmp_filter+=",v:{}".format(version)
    else:
        tmp_filter+=",v:L.L.L"

    selected_pkgs=search(db["pkgs"], tmp_filter)
    chosen_pkg={}
    if len(selected_pkgs) == 1:
        chosen_pkg={
            "alias": alias,
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
                filenpa_description=os.path.join(direpa_rel, alias, pkg_version, alias, filen_json_app)
                description=""
                if os.path.exists(filenpa_description):
                    description=Json_config(filenpa_description).data["description"]

                items.append("{} {}\n\t{}".format(db["uuid4s"][uuid4], uuid4, description))

            chosen_uuid4=prompt_multiple(
                names=items,
                title="Select a package",
                values=uuid4s,
            )
                                
        versions=[pkg["version"] for pkg in selected_pkgs if pkg["uuid4"] == chosen_uuid4]
        chosen_version=""

        if len(versions) == 1:
            chosen_version=versions[0]
        else:
            items=[]
            for version in versions:
                items.append("{} {}".format(alias, version))

            chosen_version=prompt_multiple(
                names=items,
                title="Select a version for pkg '{}'".format(alias),
                values=versions,
            )

            chosen_pkg={
                "alias": alias,
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
