#!/usr/bin/env python3
import os
from pprint import pprint
import shutil
import sys

from .helpers import is_pkg_git, get_direpa_root
from .check_pkg_integrity import check_pkg_integrity

from .remove import remove 
from .import_pkgs import import_pkgs 
from .update_upgrade import update_upgrade 

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean

def setup_vars(
    dy_app,
    arg_str, 
    direpa_deps,
    direpa_pkg,
    filenpa_conf,
    is_git,
    no_conf_src,
    no_conf_dst,
    no_root_dir,
    pkg_filters,
    pkg_names,
):
    if direpa_pkg is None:
        if is_git is True:
            if not is_pkg_git():
                msg.error("'{}' is not a git repository".format(os.getcwd()))
                sys.exit(1)
            direpa_pkg=get_direpa_root()
        else:
            direpa_pkg=os.getcwd()

    if direpa_deps is None:
        direpa_deps=os.path.join(direpa_pkg, dy_app["diren_pkgs"])

    conf_pkg=None
    if no_conf_src is False:
        if filenpa_conf is None:
            filenpa_conf=os.path.join(direpa_pkg, dy_app["filen_json_app"])
        conf_pkg=Json_config(filenpa_conf)
   
        check_pkg_integrity(
            filen_json_default=dy_app["filen_json_app"],
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            restore=dy_app["args"]["restore"].here,
        )

    options=dict(
        conf_pkg=conf_pkg,
        direpa_pkg=direpa_pkg,
        direpa_deps=direpa_deps,
        no_conf_src=no_conf_src,
        pkg_filters=pkg_filters,
    )
    if arg_str == "remove":
        remove(
            **options,
        )
    elif arg_str in ["import_pkgs", "restore"]:
        options["conf_db"]=Json_config(os.path.join(dy_app["direpa_repo"], dy_app["filen_json_repo"]))
        options["filen_json_default"]=dy_app["filen_json_app"]
        options["direpa_repo"]=dy_app["direpa_repo"]
        options["no_conf_dst"]=no_conf_dst
        options["no_root_dir"]=no_root_dir
        if arg_str == "restore":
            for dep in conf_pkg.data["deps"]:
                uuid4, name, version, bound = dep.split("|")
                options["pkg_filters"].append("{},{}".format(name,version))

        import_pkgs(**options)
    elif arg_str in ["upgrade", "update"]:
        update_upgrade(
            arg_str=arg_str,
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_repo=dy_app["direpa_repo"],
            filen_json_app=dy_app["filen_json_app"],
            filen_json_repo=dy_app["filen_json_repo"],
            pkg_names=pkg_names,
        )
