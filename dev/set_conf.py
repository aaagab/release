#!/usr/bin/env python3
# author: Gabriel Auger
# version: 7.2.0
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
def set_conf(default_filen, 
    authors=[],
    description=None,
    filen_main=None,
	filenpa_conf=None,
	# get_uuid4=False,
    licenses=[],
    pkg_name=None,
    pkg_version=None,
	uuid4=None,
):
	if filenpa_conf is None:
		filenpa_conf=os.path.join(os.getcwd(), default_filen)

	if os.path.exists(filenpa_conf):
		msg.warning("{} already exists.".format(filenpa_conf))
		sys.exit(1)

	if uuid4 is None:
		uuid4=str(uuid.uuid4())
	dct_gpm=dict(
		name=get_pkg_name(pkg_name),
		authors=get_authors(authors),
		licenses=get_licenses(licenses),
		description=get_description(description),
		filen_main=get_filen_main(filen_main),
		version=get_pkg_version(pkg_version),
		deps=[],
		installer="gpm",
		uuid4=uuid4
	)

	with open(filenpa_conf, "w") as f:
		f.write(json.dumps(dct_gpm,sort_keys=True, indent=4))

	# if get_uuid4 is True:
		# print(uuid4)

def get_pkg_name(pkg_name):
	if pkg_name is None:
		pkg_name=prompt("Package Name")
	
	while ro.Package_name_regex(pkg_name).match is False:
		pkg_name=prompt("Package Name")

	return pkg_name

def get_authors(authors):
	if not authors:
		authors=[]
		authors.append(prompt("Author"))
		while True:
			if prompt_boolean("Do you want to add another author"):
				authors.append(prompt("Author"))
			else:
				break

	return authors

def get_licenses(licenses):
	if not licenses:
		licenses=[]
		licenses.append(prompt("License"))

		while True:
			if prompt_boolean("Do you want to add another license"):
				licenses.append(prompt("License"))
			else:
				break

	return licenses

def get_description(description):
	if description is None:
		description=prompt("Package Description")

	return description

def get_filen_main(filen_main):
	if filen_main is None:
		filen_main=prompt("Package Main File", allow_empty=True)

	return filen_main

def get_pkg_version(pkg_version):
	prompt_text="Package Version ex:0.0.0"
	if pkg_version is None:
		pkg_version=prompt(prompt_text)
	
	while ro.Version_regex(pkg_version).match is False:
		pkg_version=prompt(prompt_text)

	return pkg_version
