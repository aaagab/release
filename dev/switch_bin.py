#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.2.0
# name: release
# license: MIT
import os, sys
import re
import shutil
import contextlib
import subprocess
import shlex
from pprint import pprint

from dev.helpers import get_direpa_root, to_be_coded
from dev.refine import get_paths_to_copy, copy_to_destination
import dev.regex_obj as ro

import modules.message.message as msg
from modules.prompt.prompt import prompt_boolean
from modules.json_config.json_config import Json_config
import modules.shell_helpers.shell_helpers as shell

def switch_bin(dy_rel, args):
    print("Ready to switch")
    sys.exit()
    
