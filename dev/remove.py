#!/usr/bin/env python3
import os
from pprint import pprint
import shutil
import sys

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config
from ..gpkgs.prompt import prompt_boolean

# ./__init__.py -i message,a.a.a prompt

def remove(
    conf_pkg,
    direpa_deps,
    direpa_pkg,
    no_conf_src,
    pkg_filters,
):
    pkg_aliases=[]

    if no_conf_src is True:
        msg.info("Removing a package that has been installed without a conf still needs to be coded")
        msg.info("Conf from the package needs to be retrieved from a release repository, and then version must be chosen")
        msg.info("Then all the files from the packages are listed, and they are searched on the destination and removed if any")
        sys.exit(1)

    dep_pkg_aliases=[]
    dep_pkgs={}
    for dep in conf_pkg.data["deps"]:
        uuid4, alias, version, bound = dep.split("|")
        dep_pkg_aliases.append(alias)
        dep_pkgs.update({
            alias:{
                "bound": bound,
                "version": version,
                "uuid4": uuid4
            }
        })

    if pkg_filters:
        pkg_aliases=sorted(pkg_filters)
    else:
        pkg_aliases=sorted([alias for alias in dep_pkgs])
        msg.warning("Remove all dependencies from '{}'".format(direpa_pkg))
        if not prompt_boolean("Do you want to continue" , 'N'):
            sys.exit(1)

    for pkg_alias in pkg_aliases:
        print(pkg_alias)
        direpa_dep=os.path.join(direpa_deps, pkg_alias)
        if not pkg_alias in dep_pkg_aliases:
            msg.warning("Package '{}' not found in '{}'".format(pkg_alias, os.path.dirname(direpa_dep)))
            continue
        else:
            direpa_dep=os.path.join(direpa_deps, pkg_alias)
            delete_index=dep_pkg_aliases.index(pkg_alias)
            del conf_pkg.data["deps"][delete_index]
            if os.path.exists(direpa_dep):
                shutil.rmtree(direpa_dep)
            conf_pkg.save()
            msg.success("Package '{}' removed from '{}'".format(pkg_alias, os.path.dirname(direpa_dep)))
       
