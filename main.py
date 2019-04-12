#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.1.0
# name: release
# license: MIT

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]
    
    filenpa_script=os.path.realpath(__file__)
    direpa_script=os.path.dirname(filenpa_script)
    filenpa_ops=os.path.join(direpa_script, "config", "config.json")
    conf_options=pkg.Json_config(filenpa_ops)

    filenpa_gpm_json=os.path.join(direpa_script, "gpm.json")
    conf=pkg.Json_config(filenpa_gpm_json)

    conf_options.data.update(description=conf.data["description"])
    args, this_help=pkg.ops.get_args(sys.argv, conf_options.data)

    conf.data["args"]=vars(args)

    pkg.check_repo(conf.data)

    if args.help:
        print(this_help)
        sys.exit(0)

    if args.bump_version:
        pkg.bump_version(args.bump_version[0])
        sys.exit(0)

    if args.import_pkgs:
        pkg.import_pkgs(conf.data)
        sys.exit(0)

    if args.generate_db:
        pkg.generate_db(conf.data)
        sys.exit(0)

    if args.ls_repo:
        pkg.ls_repo(conf.data)
        sys.exit(0)
        
    if args.set_bump_deploy:
        pkg.set_bump_deploy(conf.data)
        sys.exit(0)

    if args.switch_bin:
        pkg.switch_bin(conf.data, vars(args))
        sys.exit(0)

    if args.steps:
        pkg.steps()
        sys.exit(0)

    if args.export_bin:
        pkg.export(conf.data, vars(args))
        sys.exit(0)

    if args.export_rel:
        pkg.export(conf.data, vars(args))
        sys.exit(0)

    if args.remove:
        pkg.remove(conf.data)
        sys.exit(0)

    if args.update:
        pkg.update_upgrade(conf.data, "update")
        sys.exit(0)

    if args.upgrade:
        pkg.update_upgrade(conf.data, "upgrade")
        sys.exit(0)

    if args.version is True:
        lspace="  "
        print(lspace+pkg.msg.ft.bold("Name: ")+conf.data["name"])
        print(lspace+pkg.msg.ft.bold("Author(s): ")+", ".join(conf.data["authors"]))
        print(lspace+pkg.msg.ft.bold("License(s): ")+", ".join(conf.data["licenses"]))
        print(lspace+pkg.msg.ft.bold("Version: ")+conf.data["version"])
        sys.exit(0)

