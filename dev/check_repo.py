#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs.json_config import Json_config

def check_repo(
    filen_repo_default,
    direpa_repo
    # dy_app, direpa_rel=None
    ):
    # if direpa_rel is None:
        # direpa_rel=dy_app["direpa_repo"]
    if not os.path.exists(direpa_repo):
        os.makedirs(direpa_repo, exist_ok=True)
    
    filenpa_json=os.path.join(direpa_repo, filen_repo_default)
    if not os.path.exists(filenpa_json):
        with open(filenpa_json, "w") as f:
            f.write("{}")

        data={"pkgs":{}, "uuid4s":{}}
        Json_config(filenpa_json).save(data)
    
