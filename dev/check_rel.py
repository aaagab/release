#!/usr/bin/env python3
import os
import sys

from ..gpkgs.json_config import Json_config

def check_rel(
    filen_rel_default,
    direpa_rel
    ):
    if not os.path.exists(direpa_rel):
        os.makedirs(direpa_rel, exist_ok=True)
    
    filenpa_json=os.path.join(direpa_rel, filen_rel_default)
    if not os.path.exists(filenpa_json):
        with open(filenpa_json, "w") as f:
            f.write("{}")

        data={"pkgs":{}, "uuid4s":{}}
        Json_config(filenpa_json).save(data)
    
