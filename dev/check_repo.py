#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.2.1
# name: release
# license: MIT
import os, sys
from pprint import pprint

from ..modules.json_config.json_config import Json_config

def check_repo(dy_app, direpa_rel=None):
    if direpa_rel is None:
        direpa_rel=dy_app["direpa_release"]
    if not os.path.exists(direpa_rel):
        os.makedirs(direpa_rel, exist_ok=True)
    
    filenpa_json=os.path.join(direpa_rel, dy_app["filen_json_repo"])
    if not os.path.exists(filenpa_json):
        with open(filenpa_json, "w") as f:
            f.write("{}")

        data={"pkgs":{}, "uuid4s":{}}
        Json_config(filenpa_json).set_file_with_data(data)
    
