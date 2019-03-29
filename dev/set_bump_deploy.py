#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.2.0
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint

from dev.helpers import get_direpa_root, is_pkg_git
from dev.refine import get_paths_to_copy, copy_to_destination
import modules.message.message as msg
import modules.shell_helpers.shell_helpers as shell
from modules.json_config.json_config import Json_config
from modules.prompt.prompt import prompt_boolean, prompt

def set_bump_deploy(dy_rel):
    filens=["bump_version.py", "deploy.py", "scriptjob_save.json"]
    direpa_current=os.getcwd()
    direpa_src=os.path.join(direpa_current, "src")
    if not os.path.exists(direpa_src):
        msg.user_error("'{}' not found.".format(direpa_src),
            "This is not a gitframe project structure.")
        sys.exit(1)

    if not is_pkg_git(direpa_src):
        msg.user_error("'{}' is not a git folder.".format(direpa_src))
        sys.exit(1)

    os.chdir(direpa_src)
    username=shell.cmd_get_value("git config user.name")
    os.chdir(direpa_current)

    if not username:
        msg.user_error("username has not been set for git folder '{}'.".format(direpa_src))
        sys.exit(1)

    direpa_mgt=os.path.join(direpa_current, "mgt", username)
    if not os.path.exists(direpa_mgt):
        msg.user_error("'{}' not found".format(direpa_mgt),
            "This is not a gitframe project structure.")
        sys.exit(1)

    for filen in filens:
        filenpa_symlink=os.path.join(direpa_current, filen)
        filenpa_original=os.path.join(direpa_current, "mgt", username, filen)
        if os.path.islink(filenpa_symlink):
            if os.path.exists(filenpa_original):
                # repair link
                os.remove(filenpa_symlink)
                os.symlink(
                    filenpa_original,
                    filenpa_symlink
                )
                msg.success("link '{}' checked.".format(filen))

                if filen != "scriptjob_save.json":
                    msg.warning("'{}' already exists.".format(filen))
                    if prompt_boolean("Do you want to overwrite it with default values"):
                        if filen == "bump_version.py":
                            data=get_default_bump_version_file()
                        elif filen == "deploy.py":
                            data=get_default_deploy_file()

                        data=re.sub(r"\n\s+","\n", data)[1:-1]
                        with open(filenpa_original, "w") as f:
                            f.writelines(data+"\n")
            else:
                if filen == "bump_version.py":
                    data=get_default_bump_version_file()
                elif filen == "deploy.py":
                    data=get_default_deploy_file()

                data=re.sub(r"\n\s+","\n", data)[1:-1]
                with open(filenpa_original, "w") as f:
                    f.writelines(data+"\n")
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
        os.system("release --export-rel --rversion {}".format(version))
        # os.system("release --export-bin --rversion {}".format(version))
    """
