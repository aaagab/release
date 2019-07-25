#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.2.0
# name: gpm
# license: MIT

import os
from pprint import pprint
import re
import glob
import shutil

from ..dev import glob as my_glob
from ..dev.helpers import is_pkg_git

def copy_to_destination(paths, direpa_src, direpa_dst):
	os.makedirs(direpa_dst, exist_ok=True)
	for path in paths:
		path_rel=os.path.relpath(path, direpa_src)
		path_dst=os.path.join(direpa_dst, path_rel)

		if os.path.isdir(path):
			os.makedirs(path_dst, exist_ok=True)
		else:
			shutil.copy2(path, path_dst)

def get_all_paths(direpa_src, direpas_all, filenpas_all, direpa=""):
	if not direpa:
		direpa=direpa_src

	for elem_name in os.listdir(direpa):
		elem_path=os.path.join(direpa, elem_name)
		if os.path.isdir(elem_path):
			direpas_all.add(elem_path)
			get_all_paths(direpa_src, direpas_all, filenpas_all, elem_path)
		else:
			filenpas_all.add(elem_path)

def set_rules(rules, filenpa_rules):
	if os.path.exists(filenpa_rules):
		with open(filenpa_rules, "r") as f:
			for line in f.read().splitlines():
				sline=line.strip()
				# A blank line matches no files, so it can serve as a separator for readability.
				if sline != "":
					if not re.match(r"#", sline):
						rules.append(sline)

def get_paths_to_copy(direpa_src, added_rules=[]):
	rules=[]
	excluded_paths=set()

	if is_pkg_git(direpa_src):
		filenpa_private=os.path.join(direpa_src, ".git","info", "refine")
		set_rules(rules, filenpa_private)

	filenpa_refine=os.path.join(direpa_src, ".refine")
	set_rules(rules, filenpa_refine)

	if added_rules:
		rules.extend(added_rules)
	# if location_alias_src == "pkg_version":
		# rules.append("/.gpm/")

	filenpas_all=set()
	direpas_all=set()
	get_all_paths(direpa_src, direpas_all, filenpas_all)

	excluded_dirs=set()
	for rule in rules:
		rule=rule.strip()
		if rule: # ignore empty lines
			if rule[0] != "#": # ignore comment
				negative=re.match(r"^\!(.*)", rule)
				if negative:
					rule=negative.group(1)

				absolute=re.match(r"^/(.*)$", rule)
				if absolute:
					rule=absolute.group(1)

				directory=re.match(r"^(.*)/$", rule) # means match only directory, so no file or symbolic link
				if directory:
					rule=directory.group(1)

				if rule in ["*", "/*", "**", "/**/*", "**/*"]:
					rule="**"
				else:
					if not absolute:
						rule = "**/{}".format(rule)

				rule=rule.replace("**/**/", "**/")
				double_asterix_ended=re.match(r"^(.*)\*\*$", rule)
				if double_asterix_ended:
					rule="{}/*".format(rule)

				if rule == "**/*": # top_level
					if negative:
						excluded_dirs=set()
						excluded_paths=set()
					else:
						process_excluded_dir(direpa_src, excluded_dirs)
						for p in filenpas_all:
							excluded_paths.add(p)
				else:
					if negative:
						# get all matches with regular glob
						for path in glob.glob("{}/{}".format(direpa_src, rule), recursive=True):
							# according to path
							# check if for one excluded_dirs, one is path direct parent or path is equals.
							if path in excluded_dirs:
								direpa_path_relation=path
							else:
								direpa_path_relation=get_direct_parent(path, excluded_dirs)
							if direpa_path_relation:
								# remove direpa_path_relation from excluded_dirs
								excluded_dirs.remove(direpa_path_relation)
								# pprint(excluded_dirs)
								# add all other children folders from parent folders in excluded dirs
								if direpa_path_relation != path: # direct_parent
									# print("ousous")
									for elem in os.listdir(direpa_path_relation):
										direpa=os.path.join(direpa_path_relation, elem)
										if os.path.isdir(direpa):
											if direpa != path:
												process_excluded_dir(direpa, excluded_dirs)
								else: # path == direpa_path_relation
									pass # do nothing path has already been removed from excluded dirs

								# remove all paths in excluded_paths that contain paths
								paths_remove=[]
								for expath in excluded_paths:
									if os.path.isdir(path):
										if "{}/".format(path) in expath:
											paths_remove.append(expath)
									else:
										if path == expath:
											paths_remove.append(expath)

								for rpath in paths_remove:
									excluded_paths.remove(rpath)
					else:
						for path in my_glob.glob(excluded_dirs, "{}/{}".format(direpa_src, rule), recursive=True):
							if directory:
								if os.path.isdir(path):
									process_excluded_dir(path, excluded_dirs)
									for p in filenpas_all:
										if "{}/".format(path) in p:
											excluded_paths.add(p)
							else:
								if not os.path.isdir(path):
									excluded_paths.add(path)
								else:
									process_excluded_dir(path, excluded_dirs)
									for p in filenpas_all:
										if "{}/".format(path) in p:
											excluded_paths.add(p)

	# pprint(excluded_paths)
	# pprint(excluded_dirs)
	# add direpas not removed
	remove_dirs=set()
	for exdir in excluded_dirs:
		for direpa in direpas_all:
			if exdir in direpa:
				remove_dirs.add(direpa)

	kept_paths=filenpas_all - excluded_paths
	remaing_folders=direpas_all - remove_dirs
	kept_paths.update(remaing_folders)
	# pprint(kept_paths)

	return sorted(kept_paths)

# direct_parent means a level up from path 
def get_direct_parent(path, excluded_dirs):
	num_elems_path=len(path.split("/"))

	for exdir in excluded_dirs:
		num_elems_exdir=len(exdir.split("/"))
		
		if num_elems_path > num_elems_exdir:
			if num_elems_path - num_elems_exdir == 1:
				return exdir # direct_parent
	return ""

# this function always keep only the highest directory and get rid of its children, if all its children are excluded
def process_excluded_dir(direpa, excluded_dirs):
	num_elems_direpa=len(direpa.split("/"))
	add_direpa=True
	for exdir in excluded_dirs:
		num_elems_exdir=len(exdir.split("/"))
		
		if num_elems_direpa < num_elems_exdir:
			if direpa in exdir: # if direpa is parent of exdir
				remove_children(excluded_dirs, direpa)
				break
		elif num_elems_direpa == num_elems_exdir:
			if direpa == exdir: 
				add_direpa=False
				break
		elif num_elems_direpa > num_elems_exdir:
			if exdir in direpa: # exdir is parent of direpa, direpa is not need in set.
				add_direpa=False
				break

	if add_direpa:
		excluded_dirs.add(direpa)

def remove_children(excluded_dirs, pattern):
	delete_elems=[]
	for exdir in excluded_dirs:
		if pattern in exdir:
			delete_elems.append(exdir)

	for elem in delete_elems:
		excluded_dirs.remove(elem)
				
def compare_set(set1, set2):
	print(len(set1), len(set2))
	pprint(set1 ^ set2)
