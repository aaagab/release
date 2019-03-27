#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.0.0
# name: release
# license: MIT
import sys
import os
import json
import subprocess, shlex
from distutils.dir_util import copy_tree
from copy import deepcopy
import shutil
import re
import contextlib
from pprint import pprint

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from modules.json_config.json_config import Json_config
import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean, prompt
import modules.shell_helpers.shell_helpers as shell
del sys.path[0:2]

preset_ignore=dict(
    names=[
        ".git",
        "__pycache__",
        ".env",
        ".pytest_cache",
        ".vscode"
    ],
    paths=[
        ".gitignore",
    ],
    exts=[
        ".pyc",
        ".db"
    ]
)



def get_direpa_root():
    return subprocess.check_output(shlex.split("git rev-parse --show-toplevel")).decode('utf-8').rstrip()

def append_path_to_ignore_paths(preset, direpa_root):
    for i, path in enumerate(preset["paths"]):
        if not os.path.isabs(path):
            preset["paths"][i]=os.path.join(direpa_root, path)

class Bump_version(object):
    def __init__(self):
        self.check_args_num()
        self.release_version=sys.argv[1]
        self.direpa_root = get_direpa_root()
        self.preset_ignore=deepcopy(preset_ignore)
        self.preset_ignore["paths"].extend([
                "license.txt",
                "modules"
            ])
        self.preset_ignore["exts"].extend([
                ".json",
            ])
        append_path_to_ignore_paths(self.preset_ignore, self.direpa_root)
        
    def append_path_to_ignore_paths(self):
        for i, path in enumerate(self.preset_ignore["paths"]):
            if not os.path.isabs(path):
                self.preset_ignore["paths"][i]=os.path.join(self.direpa_root, path)

    def execute(self):
        self.update_config_version()
        self.update_files()
        # self.update_modules_json()
        self.update_upacks_json()
        msg.success("Bumped version v{}".format(self.release_version))
        return self

    def update_upacks_json(self):
        filenpa_upacks_json=os.path.join(
            self.direpa_root,
            "upacks.json"
        )

        if os.path.exists(filenpa_upacks_json):
            data=""

            with open(filenpa_upacks_json, 'r') as f:
                data=json.load(f)

            data["version"]=self.release_version

            with open(filenpa_upacks_json, 'w') as outfile:
                outfile.write(json.dumps(data,sort_keys=True, indent=4))

    def update_config_version(self):
        filenpa_config=os.path.join(
            self.direpa_root,
            "config",
            "config.json"
        )

        if os.path.exists(filenpa_config):
            data=""

            with open(filenpa_config, 'r') as f:
                data=json.load(f)

            data["version"]=self.release_version

            with open(filenpa_config, 'w') as outfile:
                outfile.write(json.dumps(data,sort_keys=True, indent=4))

    def update_modules_json(self):
        direpa_modules=os.path.join(self.direpa_root, "modules")
        modules={}
        if os.path.exists(direpa_modules):
            for elem in os.listdir(direpa_modules):
                path_elem=os.path.join(direpa_modules, elem)
                if elem not in ["__pycache__"]:
                    if os.path.isdir(path_elem):
                        filenpa_version=os.path.join(path_elem, "version.txt")
                        tmp_elem={}
                        if os.path.exists(filenpa_version):
                            with open(filenpa_version, "r") as f:
                                version=f.read().rstrip()
                            
                            tmp_elem=dict({
                                elem:{
                                    "version":version
                                }
                            })
                        else:
                            tmp_elem=dict({
                                elem:{
                                    "version":""
                                }
                            })
                        
                        modules.update(
                            tmp_elem
                        )

        filenpa_module=os.path.join(self.direpa_root, "modules.json")
        with open(filenpa_module, 'w') as outfile:
            outfile.write(json.dumps(modules,sort_keys=True, indent=4))

    def update_files(self, direpa=""):
        if not direpa:
            direpa=self.direpa_root

        for elem_name in os.listdir(direpa):
            elem_path=os.path.join(direpa, elem_name)
            if not elem_path in self.preset_ignore["paths"]:
                if not elem_name in self.preset_ignore["names"]:
                    if os.path.isdir(elem_path):
                        self.update_files(elem_path)
                    else:
                        if not os.path.splitext(elem_name)[1] in self.preset_ignore["exts"]:
                            self.update_file_version(elem_path)

    def update_file_version(self, file):
        version_found=False
        data=""
        try:
            with open(file, "r") as f:
                line_num=1
                for line in f.read().splitlines():
                    # version: 1.0.0-draft-1544111083
                    if line_num <= 15:

                        text=re.match(r"^# version:.*$", line)
                        if text:
                            version_found=True
                            data+="# version: {}\n".format(self.release_version)
                            continue

                    data+=line+"\n"
                    line_num+=1

            if version_found:
                with open(file, "w") as f:
                    f.writelines(data)
        except:
            msg.warning("file '{}' is not readable.".format(file))

    def check_args_num(self):
        if len(sys.argv) != 2:
            msg.user_error(
                "You need to provide the release_version.",
                "Examples:",
                "bump_version.py 1.0.0",
                "bump_version.py 1.0.0-beta-1541014157"
            )
            sys.exit(1)

def set_bump_version_file():
    # needs to add prompt here

    data=re.sub(r"\n\s+","\n","""
        #!/usr/bin/env python3
        from release.release import Bump_version
        Bump_version().execute()
    """)[1:-1]
    direpa=os.getcwd()
    filenpa_bump_version=os.path.join(direpa, "bump_version.py")
    if os.path.exists(filenpa_bump_version):
        with open(filenpa_bump_version, "w") as f:
            f.writelines(data+"\n")

def set_deploy_file():
    tab="    "
    # data=re.sub(r"\n("+tab+"){2}","\n","""
    #     #!/usr/bin/env python3
    #     from release.release import Deploy
    #     Deploy().ignore({"paths":["modules"]}).execute()
    #     # Deploy().main("display.py").ignore(dict(paths=["modules"]), "draft").bin("release").lib(["draft","early_release"]).execute()
    # """)[1:-1].rstrip()
    app_name=prompt("app name")
    data=re.sub(r"\n("+tab+"){2}","\n","""
        #!/usr/bin/env python3
        import sys
        from release import Deploy
        version=sys.argv[1]
        added_refine_rules=["/modules/"]
        added_refine_rules=[]
        Deploy("{}", version, added_refine_rules)
    """.format(app_name))[1:-1].rstrip()

    direpa=os.getcwd()
    filenpa_deploy=os.path.join(direpa, "deploy.py")
    if os.path.exists(filenpa_deploy):
        with open(filenpa_deploy, "w") as f:
            f.writelines(data+"\n")


def deploy(app_name, version, added_refine_rules=[]):
    from dev.refine import get_paths_to_copy, copy_to_destination
    
    direpa_root=get_direpa_root()
    paths=get_paths_to_copy(direpa_root, added_refine_rules)

    direpa_tmp=direpa_root
    direpa_release=""
    while True:
        direpa_parent=os.path.dirname(direpa_tmp)
        if os.path.basename(direpa_parent) == app_name:
            direpa_release=os.path.join(direpa_parent, "rel")
            os.makedirs(direpa_release, exist_ok=True)
            break
        elif direpa_parent == "/":
            msg.user_error("You don't have a folder in path '{}' that has name '{}'".format(direpa_root, app_name))
            sys.exit(1)
            break
        else:
            direpa_tmp=direpa_parent
        
    direpa_dst=os.path.join(direpa_release, version, app_name)
    
    if os.path.exists(direpa_dst):
        msg.warning("'{}' already exists.".format(direpa_dst))
        if prompt_boolean("Do you want to replace it"):
            shutil.rmtree(direpa_dst)
    
    os.makedirs(direpa_dst, exist_ok=True)
    copy_to_destination(paths, direpa_root, direpa_dst)

# class Deploy(object):
#     def __init__(self):
#         print("just an update")

#         sys.exit()
#         sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
#         from dev.set_conf_upack import set_conf_upack
#         from dev.set_direpa_dst_release import set_direpa_dst_release
#         from dev.set_bin import set_bin, set_bin_export
#         from dev.set_lib import set_lib, set_lib_export
#         from dev.helpers import append_path_to_ignore_paths

#         self.check_args_num()
#         self.release_version=sys.argv[1]
#         msg.title("Deploy '{}'".format(self.release_version))

#         self.direpa_bin="/data/bin"
#         self.direpa_lib="/data/lib"
#         self.direpa_rel="/data/rel"
#         # self.filer_exec=""
#         # self.filen_exec=""
#         self.direpa_root = get_direpa_root()

#         self.conf_upack=""
#         set_conf_upack(self)

#         self.direpa_dst_release=""
#         set_direpa_dst_release(self)

#         self.export_bin=False
#         set_bin(self)

#         self.export_lib=False
#         set_lib(self)

#         # sys.exit()
#         # get it from parameter or from json.
#         # lets go only json for now.
#         # set for bin bin
#         # set for lib lib
#         # set to ignore modules
#         # ignore_module
#         # self.bin_release_types=[]
#         # self.lib_release_types=[]
        
#         self.preset_ignore=deepcopy(preset_ignore)
#         # self.preset_ignore.update( release_type="" )
#         self.preset_ignore["paths"].extend([
#                 "hotfix-history.json",
#                 os.path.join("config", "private_config.json")
#             ])

#         append_path_to_ignore_paths(self.preset_ignore, self.direpa_root)

#         direpa_previous=os.getcwd()
#         previous_branch=subprocess.run(shlex.split("git rev-parse --abbrev-ref HEAD"), stdout=subprocess.PIPE).stdout.decode('utf-8')
#         os.chdir(self.direpa_root)
#         os.system("git checkout v"+self.release_version)
        
#         self.copy_to_dst_release()
#         self.set_dst_version_file()

#         set_bin_export(self)
#         set_lib_export(self)

#         # if self.release_type in ["early_release", "release"]:
#         os.system("git checkout "+previous_branch)
#         os.chdir(direpa_previous)
#         self.push_origin("mgt")
#         self.push_origin("doc")

#         msg.success("Deployed v{}".format(self.release_version))

#         # self.set_bin=False
#         # self.set_lib=False
        
#         # self.data={}
#         # self.init_data()


#     # def bin(self, release_types=[]):
#     #     if not self.filen_exec:
#     #         msg.user_error("main executable name needs to be set.")
#     #         sys.exit(1)
#     #     self.set_bin=True
#     #     self.bin_release_types=self.get_release_types(release_types)
#     #     append_path_to_ignore_paths(preset_ignore, self.direpa_root)
#     #     return self

#     # def lib(self, release_types=[]):
#     #     if not self.filen_exec:
#     #         msg.user_error("main executable name needs to be set.")
#     #         sys.exit(1)
#     #     self.set_lib=True
#     #     self.lib_release_types=self.get_release_types(release_types)
#     #     append_path_to_ignore_paths(preset_ignore, self.direpa_root)
#     #     return self

#     # def init_data(self):
#     #     self.data.update(ignore=[])
#     #     for release_type in self.release_types:
#     #         self.preset_ignore.update(
#     #             release_type=release_type
#     #         )
#     #         self.data["ignore"].append(deepcopy(self.preset_ignore))

#     # def main(self, file_root):
#     #     self.filen_exec=file_root
#     #     self.filer_exec=os.path.splitext(file_root)[0]
#     #     return self

#     def execute(self):
#         # if self.release_type in ["early_release", "release"]:
#         return self

#     def push_origin(self, diren):
#         direpa_previous=os.getcwd()
#         direpa=os.path.join(os.path.dirname(self.direpa_root), diren)
#         os.chdir(direpa)
#         print(os.getcwd())
#         files_to_commit=shell.cmd_get_value("git status --porcelain")
#         if files_to_commit:
#             print("__untracked files present__")
#             for f in files_to_commit.splitlines():
#                 print("  "+str(f))

#             # user_str=prompt("Type Commit Message")
#             shell.cmd_prompt("git add .")
#             shell.cmd_prompt("git commit -am \"update for v"+self.release_version+"\"")
#         os.system("git push --all origin")
#         os.chdir(direpa_previous)

#     def ignore(self, user_ignore, release_types=[]):
#         for release_type in self.get_release_types(release_types):
#             index=self.release_types.index(release_type)
#             ignore=self.data["ignore"][index]
#             if user_ignore.get("names"):
#                 if not type(user_ignore["names"]) is list:
#                     print("In deploy.py 'names' needs to be an array")
#                     sys.exit(1)
#                 for name in user_ignore["names"]:
#                     ignore["names"].append(name)
#             if user_ignore.get("exts"):
#                 if not type(user_ignore["exts"]) is list:
#                     print("In deploy.py 'exts' needs to be an array")
#                     sys.exit(1)
#                 for ext in user_ignore["exts"]:
#                     ignore["exts"].append(ext)
#             if user_ignore.get("paths"):
#                 if not type(user_ignore["paths"]) is list:
#                     print("In deploy.py 'paths' needs to be an array")
#                     sys.exit(1)
#                 for path in user_ignore["paths"]:
#                     if not os.path.isabs(path):
#                         ignore["paths"].append(
#                             os.path.join(
#                                 self.direpa_root,
#                                 path
#                             )
#                         )
#                     else:
#                         ignore["paths"].append(path)
#         return self

#     def copy_modules(self, direpa_modules_root, direpa_modules_dst):
#         direpa_relative=direpa_modules_root.replace(os.path.join(self.direpa_root,"modules")+os.sep, "")
#         if direpa_relative==direpa_modules_root:
#             direpa_relative=""

#         direpa_dst=os.path.normpath(os.path.join(
#             direpa_modules_dst,
#             direpa_relative
#         ))

#         for elem_name in os.listdir(direpa_modules_root):
#             elem_path=os.path.join(direpa_modules_root, elem_name)
#             if not elem_path in preset_ignore["paths"]:
#                 if not elem_name in preset_ignore["names"]:
#                     if os.path.isdir(elem_path):
#                         direpa_dst_elem=os.path.join(direpa_dst, elem_name)
#                         os.makedirs(direpa_dst_elem, exist_ok=True)
#                         self.copy_modules(elem_path, direpa_modules_dst)
#                     else:
#                         if not os.path.splitext(elem_name)[1] in preset_ignore["exts"]:
#                             pass
#                             shutil.copy2(elem_path, direpa_dst)

#     # def set_bin_export(self, release_types=[]):
#     #     if self.set_bin:
#     #         if self.release_type in self.bin_release_types:
#     #             direpa_bin_app=os.path.join(self.direpa_bin, self.filer_exec+"_data", self.release_version)
                            
#     #             copy_tree(self.direpa_dst_release, direpa_bin_app)
#     #             self.init_copy_modules(direpa_bin_app)

#     #             filenpa_exec=os.path.join(direpa_bin_app, self.filen_exec)
#     #             filenpa_symlink_dst=os.path.join(self.direpa_bin, self.filer_exec)

#     #             with contextlib.suppress(FileNotFoundError):
#     #                 os.remove(filenpa_symlink_dst)

#     #             os.symlink(
#     #                 filenpa_exec,
#     #                 filenpa_symlink_dst
#     #             )
#     def init_copy_modules(self, direpa_dst):
#         direpa_modules_dst=os.path.join(direpa_dst, "modules")
#         direpa_modules_root=os.path.join(self.direpa_root, "modules")
#         if not os.path.exists(direpa_modules_dst):
#             if os.path.exists(direpa_modules_root):
#                 os.makedirs(direpa_modules_dst, exist_ok=True)
#                 self.copy_modules(direpa_modules_root, direpa_modules_dst)

#     # def set_lib_export(self):
#     #     if self.set_lib:
#     #         if self.release_type in self.lib_release_types:
#     #             direpa_lib_app=os.path.join(self.direpa_lib, self.filer_exec)
#     #             if os.path.exists(direpa_lib_app):
#     #                 shutil.rmtree(direpa_lib_app)

#     #             copy_tree(self.direpa_dst_release, direpa_lib_app)

#     #             self.init_copy_modules(direpa_lib_app)

#     def copy_to_dst_release(self, direpa=""):
#         if not direpa:
#             direpa=self.direpa_root
#             direpa_dst=self.direpa_dst_release
#         else:
#             direpa_dst=os.path.join(
#                 self.direpa_dst_release,
#                 direpa.replace(self.direpa_root+os.sep, "")
#             )

#         # index=self.release_types.index(self.release_type)
#         # ignored=self.data["ignore"][index]
#         # ignored=self.preset_ignore
#         for elem_name in os.listdir(direpa):
#             elem_path=os.path.join(direpa, elem_name)
#             if not elem_path in self.preset_ignore["paths"]:
#                 if not elem_name in self.preset_ignore["names"]:
#                     if os.path.isdir(elem_path):
#                         direpa_dst_elem=os.path.join(direpa_dst, elem_name)
#                         os.makedirs(direpa_dst_elem)
#                         self.copy_to_dst_release(elem_path)
#                     else:
#                         if not os.path.splitext(elem_name)[1] in self.preset_ignore["exts"]:
#                             shutil.copy2(elem_path, direpa_dst)

#     def set_dst_version_file(self):
#         version_file=os.path.join(self.direpa_dst_release, "version.txt")
#         with open(version_file, 'w') as f:
#             f.write(self.release_version+"\n")

#     def check_args_num(self):
#         if len(sys.argv) < 2:
#             msg.user_error(
#                 "You need to provide at least a release version.",
#                 "deploy.py 1.0.0 release",
#                 "deploy.py v1.0.0 release",
#                 "deploy.py v1.0.0-r release"
#             )
#             sys.exit(1)


