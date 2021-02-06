#!/usr/bin/env python3
import os
import sys

from .get_pkg_from_db import get_pkg_from_db
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt

def get_filenpa_conf_from_rel(pkg_alias, pkg_version, direpa_rel, filen_json_rel, filen_json_app):
    if pkg_alias is None:
        pkg_alias=prompt("Package alias")

    db_data=Json_config(os.path.join(direpa_rel, filen_json_rel)).data
    chosen_pkg=get_pkg_from_db(
        db_data=db_data,
        direpa_rel=direpa_rel,
        filen_json_default=filen_json_app, 
        not_found_error=True,
        not_found_exit=True,
        pkg_alias=pkg_alias,
        pkg_version=pkg_version,
    )

    return os.path.join(direpa_rel, pkg_alias, chosen_pkg["version"], pkg_alias, filen_json_app)
 