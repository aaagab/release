#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.4.0
# name: release
# license: MIT

import sys, os
from pprint import pprint

import modules.message.message as msg
import modules.options.options as ops
from modules.json_config.json_config import Json_config

if __name__ == "__main__":
    conf_options=Json_config()
    
    filenpa_script=os.path.realpath(__file__)
    direpa_script=os.path.dirname(filenpa_script)
    filenpa_gpm_json=os.path.join(direpa_script, "gpm.json")
    conf=Json_config(filenpa_gpm_json)

    conf_options.data.update(description=conf.data["description"])
    args, this_help=ops.get_args(sys.argv, conf_options.data)

    conf.data["args"]=vars(args)

    if args.help:
        print(this_help)
        sys.exit(0)

    if args.bump_version:
        from dev.bump_version import bump_version
        bump_version(args.bump_version[0])
        sys.exit(0)

    if args.import_pkgs:
        from dev.import_pkgs import import_pkgs
        import_pkgs(conf.data)
        sys.exit(0)

    if args.generate_db:
        from dev.generate_db import generate_db
        generate_db(conf.data)
        sys.exit(0)


    if args.ls_repo:
        from dev.ls_repo import ls_repo
        ls_repo(conf.data)
        sys.exit(0)
        
    if args.set_bump_deploy:
        from dev.set_bump_deploy import set_bump_deploy
        set_bump_deploy(conf.data)
        sys.exit(0)


    if args.switch_bin:
        from dev.switch_bin import switch_bin
        switch_bin(conf.data, vars(args))
        sys.exit(0)

    if args.steps:
        from dev.steps import steps
        steps()
        sys.exit(0)

    if args.export_bin:
        from dev.export import export
        export(conf.data, vars(args))
        sys.exit(0)

    if args.export_rel:
        from dev.export import export
        export(conf.data, vars(args))
        sys.exit(0)

    if args.version is True:
        from modules.message.format_text import Format_text as ft
        lspace="  "
        print(lspace+ft.bold("Name: ")+conf.data["name"])
        print(lspace+ft.bold("Author(s): ")+", ".join(conf.data["authors"]))
        print(lspace+ft.bold("License(s): ")+", ".join(conf.data["licenses"]))
        print(lspace+ft.bold("Version: ")+conf.data["version"])
        sys.exit(0)

