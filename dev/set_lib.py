#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: release
# license: MIT
import sys
import os
import modules.message.message as msg
import shutil
import contextlib
from distutils.dir_util import copy_tree

from modules.prompt.prompt import prompt, prompt_boolean, prompt_multiple

# sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from dev.helpers import append_path_to_ignore_paths
# del sys.path[0]

def set_lib(self):
    if "export_lib" in self.conf_upack.data:
        if self.conf_upack.data["export_lib"] is True:
            self.export_lib=True

    if self.export_lib == True:
        main_modified=False
        if not "main" in self.conf_upack.data or not self.conf_upack.data["main"]:
            self.conf_upack.data["main"]=prompt("Enter main file for '{}'".format(self.conf_upack.data["name"]))
            main_modified=True

        filenpa_main=os.path.join(self.direpa_root, self.conf_upack.data["main"])
        while not os.path.exists(filenpa_main):
            self.conf_upack.data["main"]=prompt("Enter main file for '{}'".format(self.conf_upack.data["name"]))
            filenpa_main=os.path.join(
                self.direpa_root,
                self.conf_upack.data["main"]
            )
            main_modified=True

        if main_modified:
            self.conf_upack.set_file_with_data()

def set_lib_export(self):
    if self.export_lib:
        direpa_lib_app=os.path.join(self.direpa_lib, self.conf_upack.data["name"])
        if os.path.exists(direpa_lib_app):
            shutil.rmtree(direpa_lib_app)

        copy_tree(self.direpa_dst_release, direpa_lib_app)

        self.init_copy_modules(direpa_lib_app)

        
