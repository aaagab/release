#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: release
# license: MIT
import sys
import os
import modules.message.message as msg
import shutil

from modules.prompt.prompt import prompt, prompt_boolean, prompt_multiple

def set_direpa_dst_release(self):
    # what is data["path"]: it is the path of the package in the repository, repository_path + package_name + package_index
    # direpa_par2_dst_release: repository_path + package_name
    # direpa_par1_dst_release: repository_path + package_name + package_index
    # direpa_dst_release: repository_path + package_name + package_index + package_version

    valid_path=False
    if "path" in self.conf_upack.data and self.conf_upack.data["path"]:
        if os.path.exists(self.conf_upack.data["path"]):
            valid_path=True
            # ready to set direpa_dst_release

    if not valid_path:
        # set direpa_par2_dst_release
        # set direpa_par1_dst_release
        # set data["path"]           

        # set direpa_par2_dst_release
        direpa_par2_dst_release=os.path.join(
            self.direpa_rel,
            self.conf_upack.data["name"]
        )

        if not os.path.exists(direpa_par2_dst_release):
            os.makedirs(direpa_par2_dst_release)

        # set direpa_par1_dst_release
        direpa_par1_dst_release=""
        direpas_packages=os.listdir(direpa_par2_dst_release)
        if not direpas_packages:
            direpa_par1_dst_release=os.path.join(direpa_par2_dst_release, "1")
            os.makedirs(direpa_par1_dst_release)
        else:
            if prompt_boolean("Is this package exists on repository '{}'".format(self.direpa_rel)):
                choices=dict(
                    title="Select a package index",
                    items=direpas_packages,
                    values=list(range(len(direpas_packages)))
                )
                package_index=prompt_multiple(choices)
                direpa_par1_dst_release=os.path.join(direpa_par2_dst_release, direpas_packages[package_index])
            else:
                direpa_par1_dst_release=os.path.join(
                    direpa_par2_dst_release, 
                    str(max([int(direpa) for direpa in direpas_packages])+1))
                os.makedirs(direpa_par1_dst_release)

        self.conf_upack.data["path"]=direpa_par1_dst_release
        self.conf_upack.set_file_with_data()

    self.direpa_dst_release=os.path.join(
        self.conf_upack.data["path"],
        self.release_version
    )

    if os.path.exists(self.direpa_dst_release):
        msg.warning("Path '{}' already exists on repository '{}'".format(
            self.direpa_dst_release,
            self.direpa_rel
        ))
        if prompt_boolean("Do you want to overwrite it"):
            shutil.rmtree(self.direpa_dst_release)
        else:
            msg.warning("deploy for version '{}' cancelled.".format(self.release_version))
            sys.exit(1)

    os.makedirs(self.direpa_dst_release)


    # if not direpas_packages:
            # if os.path.join(direpa_par2_dst_release, "1")
            # direpa_par1_dst_release=os.path.join(direpa_par2_dst_release, "1")
        # new or existing
        # I would say new, because existing should already have the right path
        # print("hello")

    # print(self.direpa_par1_dst_release)

    # self.direpa_dst_release=os.path.join(
    #     self.direpa_rel,
    #     self.release_version)

    # print(self.direpa_dst_release)
    # if not os.path.exists(self.direpa_dst_release):
    #     os.makedirs(self.direpa_dst_release, exist_ok=True)
    
