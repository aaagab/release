#!/usr/bin/env python3
# author: Gabriel Auger
# version: 7.0.0
# name: release
# license: MIT

if __name__ == "__main__":
    import getpass  
    import importlib
    import platform
    from pprint import pprint
    import os
    import sys
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]
    
    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/options.json").get_argsns_dy_app()

    if dy_app["platform"] == "Linux":
        dy_app["direpa_bin"]="/data/bin"
        dy_app["direpa_release"]="/data/rel"
    elif dy_app["platform"] == "Windows":
        dy_app["direpa_bin"]=r"C:\Users\{}\Desktop\data\bin".format(getpass.getuser())
        dy_app["direpa_release"]=r"C:\Users\{}\Desktop\data\rel".format(getpass.getuser())

    pkg.check_repo(dy_app)

    if args.bump_version.here is True:
        pkg.bump_version(args.bump_version.value)
        sys.exit(0)

    if args.import_pkgs.here is True:
        pkg.import_pkgs(dy_app, args.packages.values)
        sys.exit(0)

    if args.init.here is True:
        pkg.init(dy_app, 
            authors=args.authors.values,
            description=args.description.value,
            direpa_root=args.init.value,
            filen_main=args.filen_main.value,
            # get_uuid4=args.get_uuid4.here,
            licenses=args.licenses.values,
            pkg_name=args.pkg_name.value,
            pkg_version=args.pkg_version.value,
            uuid4=args.uuid4.value,
        )
        sys.exit(0)

    if args.generate_db.here is True:
        pkg.generate_db(dy_app)
        sys.exit(0)

    if args.ls_repo.here is True:
        pkg.ls_repo(dy_app, args.packages.values, args.add_deps.here)
        sys.exit(0)
        
    if args.set_bump_deploy.here is True:
        pkg.set_bump_deploy(dy_app)
        sys.exit(0)

    if args.switch_bin.here is True:
        pkg.switch_bin(dy_app, args.pkg_name.value, args.pkg_version.value)
        sys.exit(0)

    if args.steps.here is True:
        pkg.steps()
        sys.exit(0)

    if args.export_bin.here is True:
        pkg.export(dy_app,
            "export_bin",
            from_rel=args.from_rel.here,
            no_symlink=args.no_symlink.here,
            path_src=args.path_src.value,
            path_dst=args.path.value,
            pkg_name=args.pkg_name.value,
            pkg_version=args.pkg_version.value,
        )
        sys.exit(0)

    if args.export_rel.here is True:
        pkg.export(dy_app, 
            "export_rel",
            add_deps=args.add_deps.here,
            path_dst=args.path.value,
            path_src=args.path_src.value,
            pkg_version=args.pkg_version.value,
        )
        sys.exit(0)

    if args.remove.here is True:
        pkg.remove(dy_app, args.remove.values)
        sys.exit(0)

    if args.to_repo.here is True:
        pkg.to_repo(dy_app, args.to_repo.value, args.packages.values)
        sys.exit(0)

    if args.restore.here is True:
        pkg.restore(dy_app)
        sys.exit(0)

    if args.update.here is True:
        pkg.update_upgrade(dy_app, "update", args.update.values)
        sys.exit(0)

    if args.upgrade.here is True:
        pkg.update_upgrade(dy_app, "upgrade", args.upgrade.values)
        sys.exit(0)
