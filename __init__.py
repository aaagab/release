#!/usr/bin/env python3
# author: Gabriel Auger
# version: 2.1.0
# name: release
# license: MIT

import sys, os
from pprint import pprint

import modules.message.message as msg
import modules.options.options as ops
from modules.message.format_text import Format_text as ft
from modules.json_config.json_config import Json_config


if __name__ == "__main__":
    conf=Json_config()
    filenpa_script=os.path.realpath(__file__)
    direpa_script=os.path.dirname(filenpa_script)

    args, this_help=ops.get_args(sys.argv, conf.data)

    if args.help:
        print(this_help)
        sys.exit(0)

    if args.bump_version:
        from dev.bump_version import bump_version
        bump_version(args.bump_version[0])
        sys.exit(0)

    # if args.import_rel:
        # sys.exit(0)

    # if args.switch_bin
 
    if args.export_bin:
        from dev.export import export
        export(conf.data, vars(args))
        sys.exit(0)

    if args.export_rel:
        from dev.export import export
        export(conf.data, vars(args))
        sys.exit(0)

    if args.version is True:
        lspace="  "
        print(lspace+ft.bold("Name: ")+conf.data["name"])
        print(lspace+ft.bold("Author: ")+conf.data["authors"][0])
        print(lspace+ft.bold("License: ")+conf.data["licenses"][0])
        print(lspace+ft.bold("Version: ")+conf.data["version"])
        sys.exit(0)

