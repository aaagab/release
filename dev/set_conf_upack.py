#!/usr/bin/env python3
# author: Gabriel Auger
# version: 0.1.0
# name: release
# license: MIT
import sys
import os
import modules.message.message as msg
from modules.json_config.json_config import Json_config
from modules.prompt.prompt import prompt

def set_conf_upack(self):
    if not os.path.exists(self.direpa_rel):
        os.makedirs(self.direpa_rel)

    direpa_mgt=os.path.join(
        os.path.dirname(self.direpa_root),
        "mgt"
        )

    diren_package=os.path.basename(os.path.dirname(self.direpa_root))

    if not os.path.exists(direpa_mgt):
        msg.user_error(
            "Path '{} not found.".format(direpa_mgt),
            "This directory needs to be present to continue."
            )
        sys.exit(1)

    filenpa_upack=os.path.join(direpa_mgt, "upack.json")
    if not os.path.exists(filenpa_upack):
        with open(filenpa_upack, 'w') as f:
            f.write('{}')

    self.conf_upack=Json_config(filenpa_upack)
    if not "name" in self.conf_upack.data or not self.conf_upack.data["name"]:
        name=prompt("Enter Package Name for dir '{}'".format(diren_package))
        self.conf_upack.data["name"]=name.replace(" ","_")

    if not "description" in self.conf_upack.data or not self.conf_upack.data["description"]:
        self.conf_upack.data["description"]=prompt("Enter Package Description for dir '{}'".format(diren_package))

        
    self.conf_upack.set_file_with_data()
    