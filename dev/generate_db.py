#!/usr/bin/env python3
from pprint import pprint
import os
import sys

from ..gpkgs import message as msg
from ..gpkgs.json_config import Json_config

# mockpackage 0.2.2
# mockpackage 0.2.3
# mockpackage beta

def generate_db(
    direpa_rel,
    filen_json_rel,
):
    db={}
    pkgs={}
    uuid4s={}
    for pkg_alias in sorted(os.listdir(direpa_rel)): 
        if pkg_alias != filen_json_rel:
            direpa_pkg=os.path.join(direpa_rel, pkg_alias)
            if os.path.isdir(direpa_pkg):
                for version in os.listdir(direpa_pkg):
                    direpa_version=os.path.join(direpa_pkg, version)
                    if os.path.isdir(direpa_version):
                        filenpa_gpm=os.path.join(direpa_version, pkg_alias, "gpm.json")
                        if os.path.exists(filenpa_gpm):
                            dy_pkg=Json_config(filenpa_gpm).data
                            pkg_alias=None
                            if "alias" in dy_pkg:
                                pkg_alias=dy_pkg["alias"]
                            else:
                                pkg_alias=dy_pkg["name"]
                            if dy_pkg["uuid4"] in uuid4s:
                                if pkg_alias != uuid4s[dy_pkg["uuid4"]]:
                                    msg.error(["Failed Insert '{}' with uuid4 '{}' ".format(
                                        pkg_alias, dy_pkg["uuid4"]),
                                        "In db[uuid4s] same uuid4 has name '{}'".format(uuid4s[dy_pkg["uuid4"]]),
                                        "You can't have same uuid for different names."])
                                    sys.exit(1)
                            else:
                                uuid4s.update({dy_pkg["uuid4"]: pkg_alias})
                            pkg_id="{}|{}|{}".format(dy_pkg["uuid4"], pkg_alias, dy_pkg["version"])
                            pkgs[pkg_id]=[]
                            for dep in dy_pkg["deps"]:
                                pkgs[pkg_id].append(dep)
                        else:
                            msg.warning("'{}' does not exists".format(filenpa_gpm))

    filenpa_json_rel=os.path.join(direpa_rel, filen_json_rel)
    db.update({"pkgs": pkgs, "uuid4s": uuid4s})
    with open(filenpa_json_rel, "w") as f:
        Json_config(filenpa_json_rel).save(db)
        msg.success("db regenerated {}".format(filenpa_json_rel))
