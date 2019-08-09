#!/usr/bin/env python3
import os
from pprint import pprint
import shutil
import sys

from .helpers import is_pkg_git, get_direpa_root
from .check_pkg_integrity import check_pkg_integrity

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean

# ./__init__.py -i message,a.a.a prompt

def remove(dy_app, pkg_names):
    if is_pkg_git():
        direpa_root=get_direpa_root()
        check_pkg_integrity(dy_app, direpa_root)

        filenpa_json=os.path.join(direpa_root, dy_app["filen_json_app"])
        conf_app=Json_config(filenpa_json)
        dep_pkgs={}
        dep_pkg_names=[]
        for dep in conf_app.data["deps"]:
            uuid4, name, version, bound = dep.split("|")
            dep_pkg_names.append(name)
            dep_pkgs.update({
                name:{
                    "bound": bound,
                    "version": version,
                    "uuid4": uuid4
                }
            })

        if pkg_names:
            pkg_names=sorted(pkg_names)
        else:
            pkg_names=sorted([name for name in dep_pkgs])
            msg.warning("Waiting confirmation to remove all dependencies from '{}'".format(direpa_root))
            if not prompt_boolean("Do you want to continue" , 'N'):
                sys.exit(1)

        for pkg_name in pkg_names:
            if not pkg_name in dep_pkg_names:
                msg.warning("Package '{}' not found in '{}'".format(pkg_name, os.path.dirname(direpa_dep)))
                continue
            else:
                direpa_dep=os.path.join(direpa_root, dy_app["diren_pkgs"], pkg_name)
                delete_index=dep_pkg_names.index(pkg_name)
                del conf_app.data["deps"][delete_index]
                if os.path.exists(direpa_dep):
                    shutil.rmtree(direpa_dep)
                conf_app.save()
                msg.success("Package '{}' removed from '{}'".format(pkg_name, os.path.dirname(direpa_dep)))
    else:
        msg.error("'{}' is not a git repository".format(os.getcwd()))
        sys.exit(1)
