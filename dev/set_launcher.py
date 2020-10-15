#!/usr/bin/env python3
import json
from pprint import pprint
import os
import re
import sys

from ..dev.helpers import get_direpa_root, is_pkg_git, create_symlink

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell
from ..gpkgs.prompt import prompt_boolean
from ..gpkgs.json_config import Json_config

def set_launcher(
    dy_app,
    app_name=None,
):
    filen="scriptjob_save.json"
    if dy_app["platform"] == "Windows":
        filen="launch.pyw"

    direpa_current=os.getcwd()
    direpa_project=None
    direpa_src=None
    if os.path.basename(direpa_current) == "src":
        direpa_project=os.path.dirname(direpa_current)
    else:
        direpa_project=direpa_current

    direpa_src=os.path.join(direpa_project, "src")

    if not os.path.exists(direpa_src):
        msg.error("'{}' not found.".format(direpa_src),
            "This is not a gitframe project structure.")
        sys.exit(1)

    if not is_pkg_git(direpa_src):
        msg.error("'{}' is not a git folder.".format(direpa_src))
        sys.exit(1)

    os.chdir(direpa_src)
    username=shell.cmd_get_value("git config --local user.name")
    os.chdir(direpa_project)
    direpa_mgt=os.path.join(direpa_project, "mgt")
    if not os.path.exists(direpa_mgt):
        msg.error("'{}' not found".format(direpa_mgt),
            "This is not a gitframe project structure.")
        sys.exit(1)

    if not username:
        msg.error("username has not been set for git folder '{}'.".format(direpa_src))
        sys.exit(1)

    direpa_mgt_username=os.path.join(direpa_mgt, username)
    if os.path.exists(direpa_mgt_username):
        direpa_mgt=direpa_mgt_username

    filenpa_symlink=os.path.join(direpa_project, filen)
    filenpa_original=os.path.join(direpa_mgt, filen)

    if not os.path.exists(filenpa_original):
        with open(filenpa_original, "w") as f:
            msg.success("'{}' created.".format(filenpa_original))

    newly_created=False
    if not os.path.exists(filenpa_symlink):
        create_symlink(dy_app["platform"], filenpa_original, filenpa_symlink )
        newly_created=True
    
    if os.path.islink(filenpa_symlink):
        if newly_created is False:
            os.remove(filenpa_symlink)
            create_symlink(dy_app["platform"], filenpa_original, filenpa_symlink )

            msg.warning("'{}' already exists.".format(filen))
            if not prompt_boolean("Do you want to overwrite it with default values"):
                sys.exit(1)
                
        if filen == "scriptjob_save.json":
            if app_name is None:
                filenpa_gpm=os.path.join(direpa_src, "gpm.json")
                if os.path.exists(filenpa_gpm):
                    app_name=Json_config(filenpa_gpm).data["name"]
                else:
                    app_name=prompt("app_name")
            data=get_default_scriptjob_save_json_file(direpa_project, app_name)
        elif filen == "launch.pyw":
            data=get_default_launch_pyw(app_name)            

        with open(filenpa_original, "w") as f:
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
    else:
        print("'{}' not a link.".format(filenpa_symlink))

def get_default_launch_pyw(app_name):
    return """
        #/usr/bin/env python3
        import os
        import shlex
        import subprocess
        import sys

        filenpa_start_script=os.path.realpath(__file__)
        direpa_project=os.path.dirname(os.path.dirname(filenpa_start_script))
        if os.path.basename(direpa_project) == "mgt":
            direpa_project=os.path.dirname(direpa_project)
        direpa_project_src=os.path.join(direpa_project,"src")

        os.system('start cmd.exe /K "title {app_name} & cd /d {{}}"'.format(direpa_project_src))
        subprocess.call('code "{{}}"'.format(direpa_project), shell=True)
        # subprocess.call('firefox https://lclwapps.edu/t/timeclock/1/', shell=True)
    """.format(app_name=app_name)

def get_default_scriptjob_save_json_file(direpa_app, app_name):
    return """
        {{
            "diren": "src",
            "groups": [
                {{
                    "name": "{app_name}",
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
                        "{app_name}"
                    ],
                    "id": "co_0",
                    "monitor": 1,
                    "name": "{app_name}",
                    "paths": [
                        "{direpa_app}"
                    ],
                    "tile": "maximize"
                }},
                {{
                    "_class": "konsole",
                    "cmd_parameters": "-p tabtitle={app_name}",
                    "exe": "konsole",
                    "filenpa_exe": "/usr/bin/konsole",
                    "groups": [
                        "{app_name}"
                    ],
                    "id": "ko_1",
                    "monitor": 0,
                    "name": "{app_name} \u2014 Konsole",
                    "paths": [],
                    "rcfile_cmds": [
                        "cd {direpa_app}/src"
                    ],
                    "tile": "right"
                }}
            ]
        }}
    """.format(app_name=app_name, direpa_app=direpa_app)
