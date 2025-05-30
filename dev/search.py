#!/usr/bin/env python3
import json
import os
import re
import sys

from . import regex_obj as ro
from .filter_version import filter_version
from .helpers import get_pkg_id

from ..gpkgs import message as msg
from ..gpkgs.sort_separated import sort_separated

def search(pkgs, pkg_filter="",identify=False):
    # pkgs=[
    #     '259d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|3.2.0',
    #     '259d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|3.2.3',
    #     '259d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|0.2.1',
    #     '259d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|1.1.0',
    #     '259d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|0.2.2',
    #     '999d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|5.2.3',
    #     '999d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|5.2.1',
    #     '999d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|4.1.0',
    #     '999d7ae3-d03e-4e5a-96d4-32259ff55a07|mockpackage|0.2.2'
    # ]

    # pkg_filter=[
    #     # "u:259d7ae3-d03e-4e5a-96d4-32259ff55a07,v:0.A.L",
    #     # "a:mockpackage,v:0.A.L"
    #     # "a:mockpackage,v:0.A.L",
    #     # "a:mockpackage,v:0.2.3",
    #     # "a:mockpackage,v:L.L.A",
    #     # "a:mockpackage,v:L.L.L",
    #     "a:mockpackage",
    #     # "v:3.A.X",
    #     # "v:3.A.X,a:mike"
    #     # "3.L.A",
    # ]

    # ftr=pkg_filter[0]

    selected_pkgs=[]
    if not pkg_filter:
        for pkg in pkgs:
            uuid4, alias, version, *bound = pkg.split('|')
            tmp_pkg={ "uuid4": uuid4, "alias": alias, "version": version, "bound": bound}
            tmp_pkg.update({ "id": get_pkg_id(tmp_pkg) })
            selected_pkgs.append(tmp_pkg)
    else:
        ftr=pkg_filter

        ftr_split=ftr.split(",")
        dy_filter={}
        if len(ftr_split) == 1:
            ftr_component=ftr_split[0]
            dy_filter=get_dy_filter_part(ftr_component, identify)
            if not "alias" in dy_filter and not "uuid4" in dy_filter:
                msg.error([
                    "Search Filter incomplete for '{}'".format(ftr_component),
                    "Please provide at least a alias or a uuid4.",
                ])
                sys.exit(1)
        elif len(ftr_split) < 5:
            for ftr_component in ftr_split:
                filter_part=get_dy_filter_part(ftr_component, identify)
                if next(iter(filter_part)) in dy_filter:
                    msg.error("for '{}' key '{}' already in '{}'".format(json.dumps(filter_part), next(iter(filter_part)), json.dumps(dy_filter) ))
                    sys.exit(1)
                else:
                    dy_filter.update(filter_part)
        else:
            msg.error("search filter '{}' has too many elements.".format(ftr))
            sys.exit(1)

        pre_selected_pkgs=[]
        # print(pkg_filter)
        # pprint(dy_filter)
        for pkg in pkgs:
            uuid4, alias, version, *bound = pkg.split('|')
            if bound != []:
                bound=bound[0]
            else:
                bound=""

            match=True
            
            if "uuid4" in dy_filter:
                if dy_filter["uuid4"] != uuid4:
                    match=False

            if match is True:
                if "alias" in dy_filter:
                    if dy_filter["alias"] != alias:
                        match=False
            
            if match is True:
                if "bound" in dy_filter:
                    if dy_filter["bound"] != bound:
                        match=False

            if match is True:
                tmp_pkg={ "uuid4": uuid4, "alias": alias, "version": version, "bound": bound}
                tmp_pkg.update({ "id": get_pkg_id(tmp_pkg) })

                if "version_ftr" in dy_filter:
                    pre_selected_pkgs.append(tmp_pkg)
                else:
                    selected_pkgs.append(tmp_pkg)

        if pre_selected_pkgs:
            uuids=set([pkg["uuid4"] for pkg in pre_selected_pkgs])

            for uuid4 in uuids:
                pre_pkgs=[pkg for pkg in pre_selected_pkgs]
                versions=[pkg["version"] for pkg in pre_pkgs if pkg["uuid4"] == uuid4]
                selected_versions=filter_version(versions, dy_filter["version_ftr"])
                selected_pkgs.extend([pkg for pkg in pre_selected_pkgs if pkg["version"] in selected_versions])

    if selected_pkgs:
        # sort by alias, uuid, and version (reg and non reg)
        package_ids=[pkg["id"] for pkg in selected_pkgs]
        # pprint(package_ids)
        presort_ids=sort_separated(package_ids, separator="|", sort_order=[1,0,2], keep_sort_order=False)
        # print()
        # pprint(presort_ids)
        presort_packages=[]
        uuid4s=[]
        for presort_id in presort_ids:
            pkg=[pkg for pkg in selected_pkgs if pkg["id"] == presort_id][0]
            if pkg["uuid4"] not in uuid4s:
                uuid4s.append(pkg["uuid4"])
            presort_packages.append(pkg)

        # print()
        sorted_pkgs=[]
        for uuid4 in uuid4s:
            # print(uuid4)
            reg_version_pkgs=[]
            non_reg_version_pkgs=[]
            uuid4_pkgs=[pkg for pkg in presort_packages if pkg["uuid4"] == uuid4]
            for pkg in uuid4_pkgs:
                if ro.Version_regex(pkg["version"]).match:
                    reg_version_pkgs.append(pkg)
                else:
                    non_reg_version_pkgs.append(pkg)

            if reg_version_pkgs:
                sorted_indexes=sort_separated([pkg["version"] for pkg in reg_version_pkgs], get_index=True)
                for index in sorted_indexes:
                    sorted_pkgs.append(reg_version_pkgs[index])

            if non_reg_version_pkgs:
                sorted_indexes=[index for index in sorted(range(len(non_reg_version_pkgs)), key=lambda k: non_reg_version_pkgs[k])]
                for index in sorted_indexes:
                    sorted_pkgs.append(non_reg_version_pkgs[index])

    # print()
    # for pkg in sorted_pkgs:
        # print(pkg["id"])

        return sorted_pkgs
    else:
        return []

def get_dy_filter_part(ftr_component, identify):
    identifiers=["b", "a", "u", "v"]
    reg_identifier=re.match(r"^(["+"{}".format("|".join(identifiers))+r"]):(.*)$", ftr_component)
    if reg_identifier:
        id_letter=reg_identifier.group(1)
        search_elem=reg_identifier.group(2)

        if id_letter == "b":
            bounds=["gpm", "sys"]
            if not search_elem in bounds:
                msg.error("In '{}' dependency bound must be in '['{}']'".format(ftr_component, "', '".join(bounds)))
                sys.exit(1)
            else:
                return dict(bound=search_elem)
        elif id_letter == "a":
            reg_alias=ro.Package_alias_regex(search_elem)
            if not reg_alias.match:
                sys.exit(1)
            else:
                return dict(alias=search_elem)
        elif id_letter == "u":
            reg_uuid4=ro.Uuid4_regex(search_elem)
            if reg_uuid4.match:
                return dict(uuid4=search_elem)
            else:
                msg.error("In '{}'".format(ftr_component))
                reg_uuid4.print_error()
                sys.exit(1)
        elif id_letter == "v":
            return dict(version_ftr=search_elem)
    else:
        # if identify is False:
        msg.error(
            [
                "'{}' has not identifier".format(ftr_component),
                "identifiers are '{}'".format(identifiers),
                "Use them like that 'a:alias,v:2.3.4,u:2b20ffd7-d9bf-4a23-b8cf-354b6063a26b,b:gpm'",
            ],
        exit=1)
        # else:
            
            
            
        #     print("I am here")
        #     sys.exit()
