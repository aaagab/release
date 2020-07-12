#!/usr/bin/env python3
# author: Gabriel Auger
# version: 9.3.0
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

    
    

    for arg_str in [
        "filenpa_conf",
        "from_repo",
        "path_bin",
        "path_dst",
        "path_deps",
        "path_pkg",
        "path_repo",
        "path_src",
    ]:
        arg=dy_app["args"][arg_str]
        if arg.here is True:
            if arg_str == "path_deps":
                if arg.value is None:
                    arg.value=os.getcwd()
            if arg_str == "from_repo":
                if arg.value is None:
                    continue
            if not os.path.isabs(arg.value):
                arg.value=os.path.abspath(arg.value)
            arg.value=os.path.normpath(arg.value)

    if args.path_repo.here:
        dy_app["direpa_repo"]=args.path_repo.value
    else:
        if dy_app["platform"] == "Linux":
            dy_app["direpa_repo"]="/data/rel"
        elif dy_app["platform"] == "Windows":
            dy_app["direpa_repo"]=r"C:\Users\{}\Desktop\data\rel".format(getpass.getuser())
        
    if args.path_bin.here:
        dy_app["direpa_bin"]=args.path_bin.value
    else:
        if dy_app["platform"] == "Linux":
            dy_app["direpa_bin"]="/data/bin"
        elif dy_app["platform"] == "Windows":
            dy_app["direpa_bin"]=r"C:\Users\{}\Desktop\data\bin".format(getpass.getuser())

    pkg.check_repo(
        filen_repo_default=dy_app["filen_json_repo"],
        direpa_repo=dy_app["direpa_repo"],
    )

    if args.from_repo.value is not None:
        pkg.check_repo(
            filen_repo_default=dy_app["filen_json_repo"],
            direpa_repo=args.from_repo.value,
        )   

    for arg_str in [
        "import_pkgs",
        "remove",
        "restore",
        "update",
        "upgrade"
    ]:
        # "args": "filenpa_conf,not_git,path_deps,path_pkg,path_repo",
        arg=dy_app["args"][arg_str]
        if arg.here:
            pkg.setup_vars(
                arg_str=arg_str,
                dy_app=dy_app,
                direpa_deps=args.path_deps.value,
                direpa_pkg=args.path_pkg.value,
                filenpa_conf=args.filenpa_conf.value,
                is_git=not args.not_git.here,
                is_template=args.keys.here,
                keys=args.keys.value,
                no_conf_src=args.no_conf_src.here,
                no_conf_dst=args.no_conf_dst.here,
                no_root_dir=args.no_root_dir.here,
                pkg_filters=args.packages.values,
                pkg_names=arg.values,
            )

            sys.exit(0)


        if arg.here is True:
            pkg.update_upgrade(
                dy_app, 
                arg_str, 
                arg.values)
            sys.exit(0)


    if args.set_conf.here is True:
        pkg.set_conf(
            dy_app["filen_json_app"], 
            authors=args.authors.values,
            description=args.description.value,
            filen_main=args.filen_main.value,
            filenpa_conf=args.filenpa_conf.value,
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
        
    if args.set_launcher.here is True:
        pkg.set_launcher(
            dy_app,
            app_name=args.set_launcher.value,
        )
        sys.exit(0)

    if args.bump_version.here is True:
        pkg.bump_version(
            db_data=pkg.Json_config(os.path.join(dy_app["direpa_repo"], dy_app["filen_json_repo"])).data,
            direpa_repo=dy_app["direpa_repo"],
            dy_app=dy_app,
            filen_json_app=dy_app["filen_json_app"], 
            filenpa_conf=args.filenpa_conf.value,
            increment=args.increment.here,
            is_git=not args.not_git.here,
            only_paths=[],
            pkg_name=args.pkg_name.value,
            direpa_deps=args.path_deps.value,
            direpa_pkg=args.path_pkg.value,
            save_filenpa_conf=True,
            version=args.bump_version.value,
        )
        sys.exit(0)

    if args.switch_bin.here is True:
        pkg.switch_bin(dy_app, args.pkg_name.value, args.pkg_version.value)
        sys.exit(0)

    if args.steps.here is True:
        pkg.steps()
        sys.exit(0)

    for arg_str in ["export_bin", "export_rel"]:
        arg=dy_app["args"][arg_str]

        if arg.here:
        
            options=dict(
                filenpa_conf=args.filenpa_conf.value,
                is_git=not args.not_git.here,
                only_paths=args.only_paths.values,
                pkg_name=args.pkg_name.value,
                pkg_version=args.pkg_version.value,
                direpa_pkg=args.path_pkg.value,
            )

            if arg_str == "export_bin":
                if args.from_repo.here:
                    if args.from_repo.value is None:
                        args.from_repo.value=dy_app["direpa_repo"]
                    else:
                        dy_app["direpa_repo"]=args.from_repo.value
                options["from_repo"]=args.from_repo.value

                pkg.export(
                    dy_app,
                    "export_bin",
                    direpa_bin=dy_app["direpa_bin"],
                    direpa_repo=dy_app["direpa_repo"],
                    is_beta=args.beta.here,
                    **options,
                )
                
            elif arg_str == "export_rel":
                if args.from_repo.here:
                    if args.from_repo.value is None:
                        pkg.msg.error("--from-repo path must be set")
                        sys.exit(1)
                options["from_repo"]=args.from_repo.value

                pkg.export(dy_app, 
                    "export_rel",
                    add_deps=not args.no_deps.here,
                    direpa_repo=dy_app["direpa_repo"],
                    **options,
                )
            sys.exit(0)

    if args.repo_strip.here is True:
        # print(args.packages.values)
        pkg.repo_strip(dy_app, args.repo_strip.values)
        sys.exit(0)
