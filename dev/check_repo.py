#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.1.2
# name: release
# license: MIT
import os, sys
from pprint import pprint

from ..modules.json_config.json_config import Json_config

def check_repo(dy_app):
    if not os.path.exists(dy_app["direpa_release"]):
        os.makedirs(dy_app["direpa_release"], exist_ok=True)
        filenpa_json=os.path.join(dy_app["direpa_release"], dy_app["filen_json_repo"])
        with open(filenpa_json, "w") as f:
            f.write("{}")

        data={"pkgs":{}, "uuid4s":{}}
        Json_config(filenpa_json).set_file_with_data(data)
    
