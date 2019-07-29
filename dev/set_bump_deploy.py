#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.5.0
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint
import json

from ..dev.helpers import get_direpa_root, is_pkg_git, create_symlink
from ..gpkgs import message as msg
from ..modules.shell_helpers import shell_helpers as shell
from ..modules.json_config.json_config import Json_config
from ..modules.prompt.prompt import prompt_boolean, prompt

def set_bump_deploy(dy_app):
    filens=["bump_version.py", "deploy.py", "scriptjob_save.json"]
    if dy_app["platform"] == "Windows":
        filens=["bump_version.py", "deploy.py", "launch.pyw"]

    direpa_current=os.getcwd()
    direpa_src=os.path.join(direpa_current, "src")
    if not os.path.exists(direpa_src):
        msg.error("'{}' not found.".format(direpa_src),
            "This is not a gitframe project structure.")
        sys.exit(1)

    if not is_pkg_git(direpa_src):
        msg.error("'{}' is not a git folder.".format(direpa_src))
        sys.exit(1)

    os.chdir(direpa_src)
    username=shell.cmd_get_value("git config --local user.name")
    os.chdir(direpa_current)
    direpa_mgt=os.path.join(direpa_current, "mgt")
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

    for filen in filens:
        filenpa_symlink=os.path.join(direpa_current, filen)
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
                    continue
                    
            if filen == "bump_version.py":
                data=get_default_bump_version_file()
            elif filen == "deploy.py":
                data=get_default_deploy_file()
            elif filen == "scriptjob_save.json":
                data=get_default_scriptjob_save_json_file(direpa_current)
            elif filen == "launch.pyw":
                data=get_default_launch_pyw()            

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

def get_default_bump_version_file():
    return """
        #!/usr/bin/env python3
        import os, sys
        version=sys.argv[1]
        os.system("release --bump-version {}".format(version))
    """

def get_default_deploy_file():
    return """
        #!/usr/bin/env python3
        import os, sys
        version=sys.argv[1]
        os.system("release --export-rel --rversion {} --add-deps".format(version))
        # os.system("release --export-bin --rversion {}".format(version))
    """

def get_default_launch_pyw():
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
        app_name=os.path.basename(direpa_project)

        os.system('start cmd.exe /K "prompt $G$S & title {} & cd {}"'.format(app_name, direpa_project_src))
        subprocess.call('code "{}"'.format(direpa_project), shell=True)
        # subprocess.call('firefox https://lclwapps.edu/t/timeclock/1/', shell=True)
    """

def get_default_scriptjob_save_json_file(direpa_app):
    diren_app=os.path.basename(direpa_app)
    return """
        {{
            "diren": "src",
            "groups": [
                {{
                    "name": "{diren_app}",
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
                        "{diren_app}"
                    ],
                    "id": "co_0",
                    "monitor": 1,
                    "name": "{diren_app} - update_groups.py",
                    "paths": [
                        "{direpa_app}"
                    ],
                    "tile": "maximize"
                }},
                {{
                    "_class": "konsole",
                    "cmd_parameters": "-p tabtitle={diren_app}",
                    "exe": "konsole",
                    "filenpa_exe": "/usr/bin/konsole",
                    "groups": [
                        "{diren_app}"
                    ],
                    "id": "ko_1",
                    "monitor": 0,
                    "name": "{diren_app} \u2014 Konsole",
                    "paths": [],
                    "rcfile_cmds": [
                        "cd {direpa_app}/src"
                    ],
                    "tile": "right"
                }}
            ]
        }}
    """.format(diren_app=diren_app, direpa_app=direpa_app)
