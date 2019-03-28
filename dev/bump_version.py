#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.0
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint

from dev.helpers import get_direpa_root, is_pkg_git
from dev.refine import get_paths_to_copy, copy_to_destination
import modules.message.message as msg
from modules.json_config.json_config import Json_config

def bump_version(version):
    direpa_root=get_direpa_root()
    
    paths=get_paths_to_copy(direpa_root, [
        ".refine",
        "/modules/",
    ])
    for path in paths:
        if os.path.isfile(path):
            if os.path.basename(path) in ["config.json", "gpm.json", "modules.json"]:
                conf=Json_config(path)
                if "version" in conf.data:
                    conf.data["version"]=version
                    conf.set_file_with_data()
            else:
                version_found=False
                data=""
                try:
                    with open(path, "r") as f:
                        line_num=1
                        for line in f.read().splitlines():
                            if line_num <= 15:
                                text=re.match(r"^# version:.*$", line)
                                if text:
                                    version_found=True
                                    data+="# version: {}\n".format(version)
                                    continue

                            data+=line+"\n"
                            line_num+=1

                    if version_found:
                        with open(path, "w") as f:
                            f.writelines(data)
                except:
                    msg.warning("file '{}' is not readable.".format(path))
    
    msg.success("Bumped version v{}".format(version))
