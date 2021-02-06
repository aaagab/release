#!/usr/bin/env python3
from lxml import etree
from pprint import pprint
import os
import re
import sys

from . import regex_obj as ro
from .helpers import get_direpa_root
from .get_pkg_from_db import get_pkg_from_db



from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination

def increment_version_value(version_type, regex_version_value):
    if version_type == "major":
        major=int(regex_version_value.major)+1
        return "{}.0.0".format(major)
    elif version_type == "minor":
        minor=int(regex_version_value.minor)+1
        return "{}.{}.0".format(regex_version_value.major, minor)
    elif version_type == "patch":
        patch=int(regex_version_value.patch)+1
        return "{}.{}.{}".format(
            regex_version_value.major,
            regex_version_value.minor,
            patch
            )

def get_increment_type(regex_curr_tag):
    menu="""
        1 - Major
        2 - Minor
        3 - Patch

        Choose an increment type for tag '{tag}' or 'q' to quit: """.format(tag=regex_curr_tag.text)

    user_choice=None
    while user_choice is None:
        user_choice = input(menu)
        if user_choice == "1":
            return increment_version_value("major", regex_curr_tag)
        elif user_choice == "2":
            return increment_version_value("minor", regex_curr_tag)
        elif user_choice == "3":
            return increment_version_value("patch", regex_curr_tag)
        elif user_choice.lower() == "q":
            sys.exit(1)
        else:
            msg.warning("Wrong input")
            input("  Press Enter To Continue...")
            user_choice=None
            # clear terminal 
            # ft.clear_screen()

def get_filenpa_conf(direpa_pkg, filen_json_app, filenpa_conf=None):
    if filenpa_conf is None:
        filenpa_conf=os.path.join(direpa_pkg, filen_json_app)
        if not os.path.exists(filenpa_conf):
            filenpa_conf=os.path.join(direpa_pkg, "web.config")
    if not os.path.exists(filenpa_conf):
        return None
    else:
        return filenpa_conf

def get_version_from_conf(filenpa_conf):
    filer, ext =os.path.splitext(filenpa_conf)
    if os.path.basename(filenpa_conf).lower() == "web.config":
        xml_elem=etree.parse(filenpa_conf).getroot().find("./appSettings/add[@key='VERSION']")
        if xml_elem is None:
            msg.error("VERSION attribute not found in appsettings '{}'.".format(filenpa_conf), exit=1)
        version=xml_elem.attrib["value"]
    elif ext == ".json":
        data=Json_config(filenpa_conf).data
        if not "version" in data:
            msg.error("version attribute not found in '{}'".format(filenpa_conf), exit=1)
        version=data["version"]
    else:
        with open(filenpa_conf, "r") as f:
            version=f.read().strip()

    return version            

def bump_version(
    db_data,
    diren_pkgs,
    direpa_rel,
    filen_json_app,
    filenpa_conf,
    increment,
    increment_type,
    is_git,
    only_paths,
    pkg_alias,
    direpa_pkg,
    save_filenpa_conf,
    version,
):
    if direpa_pkg is None:
        if is_git is True:
            direpa_pkg=get_direpa_root()
        else:
            direpa_pkg=os.getcwd()

    filenpa_conf=get_filenpa_conf(direpa_pkg, filen_json_app, filenpa_conf)
    if increment is True:
        if version is not None:
            msg.error(
                "When using --increment version must be none",
                "Version must be given from --filenpa-conf or from pkg_alias searched in the db"
            )
            sys.exit(1)
        if filenpa_conf is None:
            if pkg_alias is None:
                msg.error("conf file for version not found '{}'".format(filenpa_conf))
                msg.error("Provide either a version with either --filenpa-conf or --pkg-alias")
                sys.exit(1)
            else:
                chosen_pkg=get_pkg_from_db(
                    db_data=db_data,
                    direpa_rel=direpa_rel,
                    filen_json_default=filen_json_app, 
                    not_found_error=True,
                    not_found_exit=True,
                    pkg_alias=pkg_alias,
                )
                version=chosen_pkg["version"]
        else:
            version=get_version_from_conf(filenpa_conf)
        version_regex=ro.Version_regex(version)
        if increment_type is None:
            version=(get_increment_type(version_regex))
        else:
            version=increment_version_value(increment_type, version_regex)

    if version is None:
        msg.error("No version to bump")
        sys.exit(1)

    paths=[]
    ignore=[]
    if len(only_paths) > 0:
        paths=only_paths
    else:
        # paths=get_paths_to_copy(direpa_pkg, added_rules=)
        ignore_files=[   
            "config.json",
            "gpm.json",
            "modules.json",
            "upacks.json",
            ".refine",
            ".gitignore",
        ]
        ignore_exts=[
            ".db",
            ".ico",
        ]
        conf_elems=[
            "config/config.json",
            "config.json",
            "gpm.json",
            "modules.json",
            "upacks.json"
        ]

        for elem in os.listdir(direpa_pkg):
            path_elem=os.path.join(direpa_pkg, elem)
            if os.path.isfile(path_elem) and elem not in ignore_files:
                filer, ext = os.path.splitext(elem)
                if ext not in ignore_exts:
                    paths.append(path_elem)

        if filenpa_conf is not None:
            if save_filenpa_conf is True:
                conf_elems.append(filenpa_conf)

        for elem in conf_elems:
            filenpa_conf_elem=None
            if os.path.isabs(elem):
                filenpa_conf_elem=elem
            else:
                filenpa_conf_elem=os.path.join(direpa_pkg, elem)
            if os.path.exists(filenpa_conf_elem):
                filer, ext =os.path.splitext(filenpa_conf_elem)

                if os.path.basename(filenpa_conf_elem).lower() == "web.config":
                    xml_tree=etree.parse(filenpa_conf_elem)
                    xml_tree.getroot().find("./appSettings/add[@key='VERSION']").attrib["value"]=version
                    xml_tree.write(filenpa_conf_elem)
                elif ext == ".json":
                    conf=Json_config(filenpa_conf_elem)
                    if "version" in conf.data:
                        conf.data["version"]=version
                        conf.save()
                else:
                    with open(filenpa_conf_elem, "w") as f:
                        f.write("{}\n".format(version))

    for path in paths:
        if os.path.isfile(path):
            header_version_found=False
            init_version_found=False
            data=""
            try:
                with open(path, "r") as f:
                    line_num=1
                    for line in f.read().splitlines():
                        
                        if header_version_found is False:
                            if line_num <= 15:
                                text=re.match(r"^#\s+version:.*$", line)
                                if text:
                                    header_version_found=True
                                    data+="# version: {}\n".format(version)
                                    continue

                        if init_version_found is False:
                            if os.path.basename(path) == "__init__.py":
                                text=re.match(r"^__version__\s*=.*$", line)
                                if text:
                                    init_version_found=True
                                    data+="__version__ = \"{}\"\n".format(version)
                                    continue

                        data+=line+"\n"
                        line_num+=1

                if header_version_found is True or init_version_found is True:
                    with open(path, "w") as f:
                        f.writelines(data)
            except:
                msg.warning("file '{}' is not readable.".format(path))
    
    msg.success("Bumped to version v{}".format(version))
    return version

