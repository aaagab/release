#!/usr/bin/env python3
import json
import platform
from pprint import pprint
import os
import re
import sys

from ..dev.helpers import is_pkg_git, create_symlink, get_direpa_root

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.prompt import prompt_boolean, prompt
from ..gpkgs.json_config import Json_config

def set_launcher(
    pkg_alias=None,
    direpa_project=None,
    overwrite=False,
    system=None,
):
    filen="scriptjob_save.json"
    if system is None:
        system=platform.system()
    if system == "Windows":
        filen="launch.pyw"

    direpa_current=os.getcwd()
    direpa_project=None
    direpa_src=None

    if direpa_project is None:
        if is_pkg_git(direpa_current):
            direpa_root=get_direpa_root(direpa_current)
            if os.path.basename(direpa_root) == "src":
                direpa_project=os.path.dirname(direpa_root)
                direpa_src=direpa_root
        else:
            if os.path.basename(direpa_current) == "src":
                direpa_project=os.path.dirname(direpa_current)
                direpa_src=direpa_current
            elif "src" in os.listdir(direpa_current):
                direpa_project=direpa_current
                direpa_src=os.path.join(direpa_project, "src")
    else:
        if "src" in os.listdir(direpa_project):
            direpa_src=os.path.join(direpa_project, "src")

    if not os.path.exists(direpa_project):
        msg.error("Project path not found '{}'".format(direpa_project), exit=1)

    if pkg_alias is None:
        if direpa_src is None:
            pkg_alias=prompt("package alias")
        else:
            filenpa_gpm=os.path.join(direpa_src, "gpm.json")
            if os.path.exists(filenpa_gpm):
                json_data=Json_config(filenpa_gpm).data
                pkg_alias=json_data["name"]
                if "alias" in json_data:
                    pkg_alias=json_data["alias"]
            else:
                pkg_alias=prompt("package alias")

    filenpa_launcher=os.path.join(direpa_project, filen)

    if overwrite is False:
        if os.path.exists(filenpa_launcher):
            msg.warning("'{}' already exists.".format(filenpa_launcher))
            if not prompt_boolean("Do you want to overwrite it with default values"):
                sys.exit(1)

    if filen == "scriptjob_save.json":
        data=get_default_scriptjob_save_json_file(direpa_project, pkg_alias)
    elif filen == "launch.pyw":
        data=get_default_launch_pyw(pkg_alias)      

    with open(filenpa_launcher, "w") as f:
        if filen == "scriptjob_save.json":
            data=re.sub(r"\n\s+","\n", data)[1:-1]
            f.write(json.dumps(json.loads(data),sort_keys=True, indent=4))
        else:
            indent=None
            for line in data.splitlines()[1:-1]:
                if line.strip():
                    reg=re.match(r"^( +)(.+)", line)
                    tmp_indent=reg.group(1)
                    cmd=reg.group(2)
                    if indent is None:
                        indent=tmp_indent
                    f.write(line[len(indent):]+"\n")
                else:
                    f.write(line+"\n")
    msg.success("'{}' created.".format(filenpa_launcher))
        

def get_default_launch_pyw(pkg_alias):
    return """
        #/usr/bin/env python3
        import platform
        import os
        import shlex
        import subprocess
        import sys

        filenpa_start_script=os.path.realpath(__file__)
        direpa_project=os.path.dirname(filenpa_start_script)
        direpa_project_src=os.path.join(direpa_project,"src")

        # using 32 bit python on 64 bit system that needs to be done otherwise 
        # when launching a command from the terminal you have on some programs error is not 
        # recognized as an internal or external command, operable program or batch file.
        system32 = os.path.join(os.environ['SystemRoot'], 'SysNative' if platform.architecture()[0] == '32bit' else 'System32')

        os.system('start {{}} /K "title {pkg_alias} & cd /d {{}}"'.format(
            os.path.join(system32, "cmd.exe"),
            direpa_project_src))
        subprocess.call('code "{{}}"'.format(direpa_project), shell=True)
    """.format(pkg_alias=pkg_alias)

def get_default_scriptjob_save_json_file(direpa_app, pkg_alias):
    return """
        {{
            "diren": "src",
            "groups": [
                {{
                    "name": "{pkg_alias}",
                    "windows": [
                        {{
                            "actions": [
                                {{
                                    "name": "execute_terminal",
                                    "parameters": [
                                        "win_id:co_0",
                                        "win_id:ko_1"
                                    ]
                                }}
                            ],
                            "id": "co_0"
                        }},
                        {{
                            "actions": [
                                {{
                                    "name": "active_group_previous_window",
                                    "parameters": [
                                        "previous_window_hex_id"
                                    ]
                                }}
                            ],
                            "id": "ko_1"
                        }}
                    ]
                }}
            ],
            "windows": [
                {{
                    "_class": "code",
                    "cmd_parameters": "--new-window {direpa_app}",
                    "exe": "code",
                    "filenpa_exe": "/usr/share/code/code",
                    "groups": [
                        "{pkg_alias}"
                    ],
                    "id": "co_0",
                    "monitor": 1,
                    "name": "{pkg_alias}",
                    "paths": [
                        "{direpa_app}"
                    ],
                    "tile": "maximize"
                }},
                {{
                    "_class": "konsole",
                    "cmd_parameters": "-p tabtitle={pkg_alias}",
                    "exe": "konsole",
                    "filenpa_exe": "/usr/bin/konsole",
                    "groups": [
                        "{pkg_alias}"
                    ],
                    "id": "ko_1",
                    "monitor": 0,
                    "name": "{pkg_alias} \u2014 Konsole",
                    "paths": [],
                    "rcfile_cmds": [
                        "cd {direpa_app}/src"
                    ],
                    "tile": "right"
                }}
            ]
        }}
    """.format(pkg_alias=pkg_alias, direpa_app=direpa_app)
