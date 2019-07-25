#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.3
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint

from ..dev.helpers import get_direpa_root, is_pkg_git
from ..dev.refine import get_paths_to_copy, copy_to_destination
from ..modules.message import message as msg
from ..modules.json_config.json_config import Json_config

def bump_version(version):
    direpa_root=get_direpa_root()
    
    paths=get_paths_to_copy(direpa_root, [
        ".refine",
        "modules/",
        ".pkgs/",
        "gpkgs/",
        "*.db"
    ])
    for path in paths:
        if os.path.isfile(path):
            if os.path.basename(path) in ["config.json", "gpm.json", "modules.json", "upacks.json"]:
                conf=Json_config(path)
                if "version" in conf.data:
                    conf.data["version"]=version
                    conf.set_file_with_data()
            else:
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
