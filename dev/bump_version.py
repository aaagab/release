#!/usr/bin/env python3
from lxml import etree
from pprint import pprint
import os
import re
import sys
import time

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
    filenpas_update,
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
    timestamp=time.time()
    if len(only_paths) > 0:
        paths=only_paths
    else:
        # paths=get_paths_to_copy(direpa_pkg, added_rules=)
        ignore_files=[   
            "config.json",
            ".keep",
            "gpm.json",
            "modules.json",
            "upacks.json",
            ".refine",
            ".gitignore",
        ]
        ignore_exts=[
            ".db",
            ".ico",
            ".md",
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
                        conf.data["timestamp"]=timestamp
                        conf.save()
                else:
                    with open(filenpa_conf_elem, "w") as f:
                        f.write("{}\n".format(version))

    for elem_path in paths:
        update_file_version(elem_path, version)


    for elem_path in filenpas_update:
        update_file_version(elem_path, version, pkg_alias=pkg_alias, insert_version=True)
    
    msg.success("Bumped to version v{}".format(version))
    return version

def update_file_version(elem_path, version, pkg_alias=None, insert_version=False):
    if os.path.isfile(elem_path):
        header_version_found=False
        init_version_found=False
        filer, ext=os.path.splitext(elem_path)
        data=""
        updated=False
        
        if ext in [".js", ".py"]:
            is_init_file=(os.path.basename(elem_path) == "__init__.py")
            f=None
            try:
                f=open(elem_path, "r")
            except:
                msg.warning("file '{}' is not readable.".format(elem_path))

            try:
                if f is not None:
                    line_num=1
                    for line in f.read().splitlines():
                        reg_matched=False
                        has_quote=False
                        if line_num <= 15:
                            regex_strs=[]
                            if ext == ".py":
                                regex_strs.append(r"^\s*(?P<comment>#)\s+(?P<version_label_1>version)\s*(?P<version_label_2>:).*$")
                                if is_init_file is True:
                                    regex_strs.append(r"^\s*(?P<version_label_1>__version__)\s*(?P<version_label_2>=).*$")
                                    has_quote=True

                            elif ext == ".js":
                                regex_strs.append(r"^\s*(?P<comment>//)\s+(?P<version_label_1>version)\s*(?P<version_label_2>:).*$")

                            for regex_str in regex_strs:
                                reg=re.match(regex_str, line)
                                if reg:
                                    reg_matched=True
                                    updated=True
                                    dy=reg.groupdict()
                                    text=""
                                    if "comment" in dy:
                                        text+="{} ".format(dy["comment"])

                                    text+="{}{} ".format(
                                        dy["version_label_1"],
                                        dy["version_label_2"],
                                    )

                                    if has_quote is True:
                                        text+="\""
                                    text+=version
                                    if has_quote is True:
                                        text+="\""
                                    text+="\n"

                                    data+=text
                                    break
                            
                        else:
                            if updated is False and insert_version is False:
                                break

                        if reg_matched is False:
                            data+=line+"\n"

                        line_num+=1

                if updated is True:
                    with open(elem_path, "w") as f:
                        f.writelines(data)
                elif insert_version is True:
                    if ext == ".js":
                        tmp_data=""
                        if pkg_alias is not None:
                            tmp_data+="// module: {}\n".format(pkg_alias)
                        tmp_data+="// version: {}\n\n".format(version)
                        data="{}{}".format(tmp_data, data)
                        with open(elem_path, "w") as f:
                            f.writelines(data)        
            finally:
                f.close()
        elif ext == ".gradle":
            process_file=False
            try:
                process_file=os.path.basename(os.path.dirname(elem_path)) == "app"
            except:
                pass
            if process_file is True:
                lines=[]
                modified=False
                with open(elem_path, "r") as f:
                    reg_text=r"^(?P<before>\s*versionName\s+[\"\'])(?P<version>.+)(?P<after>[\"\']\s*)$"
                    for line in f.read().splitlines():
                        if modified is False:
                            reg=re.match(reg_text, line)
                            if reg is None:
                                lines.append(line)
                            else:
                                modified=True
                                before=reg.groupdict()["before"]
                                after=reg.groupdict()["after"]
                                newline=f"{before}{version}{after}"
                                lines.append(newline)
                        else:
                            lines.append(line)

                if modified is True:
                    with open(elem_path, "w") as f:
                        f.write("\n".join(lines)+"\n")
