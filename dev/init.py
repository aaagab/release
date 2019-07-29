#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.6.0
# name: release
# license: MIT
import uuid
import os, sys
import re
from pprint import pprint
import shutil
import json

from .import_pkgs import import_pkgs

from ..gpkgs import message as msg
from ..modules.prompt.prompt import prompt_boolean, prompt
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell
from . import regex_obj as ro
from .filter_version import filter_version
from .helpers import get_pkg_id, get_direpa_root
from ..gpkgs.sort_separated import sort_separated
from .get_pkg_from_db import get_pkg_from_db
from .search import search

from .export import export


# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def init(dy_app, args, direpa_root=""):
	direpa_root=""
	if isinstance(args["init"], list):
		direpa_root=args["init"][0]
	msg.info("gpm init")

	if not direpa_root:
		direpa_root=os.getcwd()

	filenpa_gpm_json=os.path.join(direpa_root, dy_app["filen_json_app"])
	if os.path.exists(filenpa_gpm_json):
		msg.warning("{} already exists.".format(filenpa_gpm_json))
		sys.exit(1)

	# create gpm.json
	reg_name=ro.Package_name_regex(prompt("Package Name"))
	if not reg_name.match:
		sys.exit(1)

	dct_gpm=dict(
		name=reg_name.text,
		authors=get_authors(),
		licenses=get_licenses(),
		description=prompt("Package Description"),
		# cmds=get_cmds(),
		filen_main=prompt("Enter name Main File"),
		deps=[],
		installer="gpm",
		uuid4=str(uuid.uuid4()),
		gpm_version=dy_app["version"],
		# repository=prompt("Enter a repository path"),
		version=prompt("Enter version")
	)

	with open(filenpa_gpm_json, "w") as f:
		f.write(json.dumps(dct_gpm,sort_keys=True, indent=4))


def get_authors():
    authors=[]
    authors.append(prompt("Author"))

    while True:
        if prompt_boolean("Do you want to add another author"):
            authors.append(prompt("Author"))
        else:
            break
    
    return authors

def get_licenses():
    licenses=[]
    licenses.append(prompt("License"))

    while True:
        if prompt_boolean("Do you want to add another license"):
            licenses.append(prompt("License"))
        else:
            break

    return licenses
