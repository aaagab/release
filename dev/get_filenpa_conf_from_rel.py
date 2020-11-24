#!/usr/bin/env python3
import os
import sys

from .get_pkg_from_db import get_pkg_from_db
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt

def get_filenpa_conf_from_rel(pkg_name, pkg_version, direpa_rel, filen_json_rel, filen_json_app):
    if pkg_name is None:
        pkg_name=prompt("Package name")

    db_data=Json_config(os.path.join(direpa_rel, filen_json_rel)).data
    chosen_pkg=get_pkg_from_db(
        db_data=db_data,
        direpa_rel=direpa_rel,
        filen_json_default=filen_json_app, 
        not_found_error=True,
        not_found_exit=True,
        pkg_name=pkg_name,
        pkg_version=pkg_version,
    )

    return os.path.join(direpa_rel, pkg_name, chosen_pkg["version"], pkg_name, filen_json_app)
 