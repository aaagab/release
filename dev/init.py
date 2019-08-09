#!/usr/bin/env python3
# author: Gabriel Auger
# version: 6.0.1
# name: release
# license: MIT
import json
import os
from pprint import pprint
import re
import shutil
import sys
import uuid

from . import regex_obj as ro

from ..gpkgs import message as msg
from ..gpkgs.prompt import prompt_boolean, prompt

# ./main.py --to-repo "/mnt/utrgv/rel/" --pkgs message
def init(dy_app, direpa_root=None):
	msg.info("gpm init")

	if direpa_root is None:
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
