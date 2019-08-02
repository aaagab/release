#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.1.1
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint

from ..dev.helpers import get_direpa_root, is_pkg_git
from ..gpkgs.refine import get_paths_to_copy, copy_to_destination
from ..gpkgs import message as msg
from ..modules.json_config.json_config import Json_config

def bump_version(version):
    direpa_root=get_direpa_root()
    
    paths=get_paths_to_copy(direpa_root, added_rules=[
        "config.json",
        "gpm.json",
        "modules.json",
        "upacks.json",
        ".refine",
        "modules/",
        ".pkgs/",
        "gpkgs/",
        "*.db"
    ])

    for elem in ["config/config.json", "config.json", "gpm.json", "modules.json", "upacks.json"]:   
        filenpa_conf=os.path.join(direpa_root, elem)
        if os.path.exists(filenpa_conf):
            conf=Json_config(filenpa_conf)
            if "version" in conf.data:
                conf.data["version"]=version
                conf.set_file_with_data()

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
                                text=re.match(r"^# version:.*$", line)
                                if text:
                                    header_version_found=True
                                    data+="# version: {}\n".format(version)
                                    continue

                        if init_version_found is False:
                            if os.path.basename(path) == "__init__.py":
                                text=re.match(r"^__version__ =.*$", line)
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
    
    msg.success("Bumped version v{}".format(version))
