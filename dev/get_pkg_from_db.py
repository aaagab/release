#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import shutil

from .search import search

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_multiple

# ./__init__.py -i message,a.a.a prompt

def get_pkg_from_db(
    db_data=None, 
    direpa_rel=None,
    filen_json_default=None, 
    not_found_error=False,
    not_found_exit=False,
    pkg_bound=None,
    pkg_alias=None,
    pkg_version=None,
    pkg_uuid4=None,
):
    tmp_filters=[]
    if pkg_bound is not None:
        tmp_filters.append("b:{}".format(pkg_bound))
    if pkg_alias is not None:
        tmp_filters.append("a:{}".format(pkg_alias))
    if pkg_uuid4 is not None:
        tmp_filters.append("u:{}".format(pkg_uuid4))
    if pkg_version is None:
        tmp_filters.append("v:L.L.L")
    else:
        tmp_filters.append("v:{}".format(pkg_version))

    tmp_filter=",".join(tmp_filters)

    selected_pkgs=search(db_data["pkgs"], tmp_filter)
    chosen_pkg={}
    if not selected_pkgs:
        if not_found_error is True:
            msg.error("In '{}' db.json with filter '{}' pkg not found.".format(direpa_rel, tmp_filter))
        if not_found_exit is True:
            sys.exit(1)
        return None
    elif len(selected_pkgs) == 1:
        chosen_pkg={
            "alias": selected_pkgs[0]["alias"],
            "uuid4": selected_pkgs[0]["uuid4"],
            "version": selected_pkgs[0]["version"]
        }
    else:
        alias=selected_pkgs[0]["alias"]
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
                filenpa_description=os.path.join(direpa_rel, alias, pkg_version, alias, filen_json_default)
                description=""
                if os.path.exists(filenpa_description):
                    description=Json_config(filenpa_description).data["description"]

                items.append("{} {}\n\t{}".format(db_data["uuid4s"][uuid4], uuid4, description))

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
                items.append("{} {}".format(alias, version))

            chosen_version=prompt_multiple(
                dict(
                    items=items,
                    title="Select a version for pkg '{}'".format(alias),
                    values=versions
                ))

            chosen_pkg={
                "alias": alias,
                "uuid4": chosen_uuid4,
                "version": chosen_version
            }
            
    if pkg_bound:
        bounds=["gpm", "sys"]
        if pkg_bound not in bounds:
            msg.error("For filter '{}' bound '{}' not in ['{}']".format(pkg_filter, pkg_bound, "', '".join(bounds)))
            sys.exit(1)
    else:
        pkg_bound="gpm"

    chosen_pkg.update(dict(bound=pkg_bound))
    return chosen_pkg
