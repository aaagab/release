#!/usr/bin/env python3
# author: Gabriel Auger
# version: 9.0.0
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

def set_conf(
	default_filen, 
    authors=[],
    description=None,
    filen_main=None,
	filenpa_conf=None,
    licenses=[],
	pkg_alias=None,
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
		alias=get_pkg_alias(pkg_alias),
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

def get_pkg_alias(pkg_alias):
	if pkg_alias is None:
		pkg_alias=prompt("Package Alias")
	
	while ro.Package_alias_regex(pkg_alias).match is False:
		pkg_alias=prompt("Package Alias")

	return pkg_alias

def get_authors(authors):
	if not authors:
		authors=[]
		author=prompt("Author", default="")
		if author.strip() != "":
			authors.append(author)
			while True:
				if prompt_boolean("Do you want to add another author"):
					authors.append(prompt("Author"))
				else:
					break
	return authors

def get_licenses(licenses):
	if not licenses:
		licenses=[]
		_license=prompt("License", default="")
		if _license.strip() != "":
			licenses.append(_license)
			while True:
				if prompt_boolean("Do you want to add another license"):
					licenses.append(prompt("License"))
				else:
					break
	else:
		if licenses[0] == "":
			return []

	return licenses

def get_description(description):
	if description is None:
		description=prompt("Package Description")

	return description

def get_filen_main(filen_main):
	if filen_main is None:
		filen_main=prompt("Package Main File", default="")

	return filen_main

def get_pkg_version(pkg_version):
	prompt_text="Package Version"
	if pkg_version is None:
		pkg_version=prompt(prompt_text, default="1.0.0")
	
	while ro.Version_regex(pkg_version).match is False:
		pkg_version=prompt(prompt_text)

	return pkg_version
