#!/usr/bin/env python3
# author: Gabriel Auger
# version: 12.2.3
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
    dy_default_direpas=dict(
        bin=os.path.join(os.path.expanduser("~"), "fty", "bin"),
        pkg=os.getcwd(),
        rel=os.path.join(os.path.expanduser("~"), "fty", "rel"),
        src=os.path.join(os.path.expanduser("~"), "fty", "src"),
        wrk=os.path.join(os.path.expanduser("~"), "fty", "wrk"),
    )

    def get_direpa_rel():
        if args.path_rel.here:
            return args.path_rel.value
        else:
            return dy_default_direpas["rel"]

    def get_direpa_deps(direpa_deps, direpa_pkg, diren_pkgs):
        if direpa_deps is None:
            return os.path.join(direpa_pkg, diren_pkgs)
        else:                    
            return direpa_deps

    def check_rel(direpa_rel=None):
        if direpa_rel is None:
            direpa_rel=get_direpa_rel()
        pkg.check_rel(filen_rel_default=dy_app["filen_json_rel"], direpa_rel=direpa_rel)

    def get_direpa_pkg(direpa_pkg, is_not_git):
        is_git=not is_not_git
        if direpa_pkg is None:
            if is_git is True:
                return pkg.get_direpa_root()
            else:
                return os.getcwd()
        return direpa_pkg

    def get_conf_pkg( filenpa_conf, direpa_pkg, filen_json_app):
        if filenpa_conf is None:
            filenpa_conf=os.path.join(direpa_pkg, filen_json_app)
        return pkg.Json_config(filenpa_conf)

    def check_pkg_integrity(conf_pkg, direpa_deps, filen_json_app, restore=False):
        pkg.check_pkg_integrity(
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            filen_json_default=filen_json_app,
            restore=args.restore.here,
        )

    if args.examples.here is True:
        pkg.get_examples()
        sys.exit(0)
            
    if args.restore.here or args.import_pkgs.here:
        check_rel()

        direpa_pkg=get_direpa_pkg(args.path_pkg.value, args.not_git.here)
        direpa_deps=get_direpa_deps(args.path_deps.value, direpa_pkg, dy_app["diren_pkgs"])

        conf_pkg=None
        if args.restore.here is True or ( args.import_pkgs.here and args.no_conf_src.here is False):
            conf_pkg=get_conf_pkg(args.filenpa_conf.value, direpa_pkg, dy_app["filen_json_app"])
            if args.restore.here:
                check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"], args.restore.here)
            elif args.import_pkgs.here:
                check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        direpa_rel=get_direpa_rel()

        pkg_filters=args.package_filters.values
        if args.restore.here:
            for dep in conf_pkg.data["deps"]:
                uuid4, name, version, bound = dep.split("|")
                pkg_filters.append("{},{}".format(name,version))
        
        pkg.import_pkgs(
            conf_db=pkg.Json_config(os.path.join(direpa_rel, dy_app["filen_json_rel"])),
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_rel=direpa_rel,
            filen_json_default=dy_app["filen_json_app"],
            is_template=args.keys.here,
            no_conf_src=args.no_conf_src.here,
            no_conf_dst=args.no_conf_dst.here,
            no_root_dir=args.no_root_dir.here,
            pkg_filters=pkg_filters,
            keys=args.keys.value,
        )
        sys.exit(0)

    if args.remove.here:
        check_rel()

        direpa_pkg=get_direpa_pkg(args.path_pkg.value, args.not_git.here)
        direpa_deps=get_direpa_deps(args.path_deps.value, direpa_pkg, dy_app["diren_pkgs"])

        conf_pkg=None
        if args.no_conf_src.here is False:
            conf_pkg=get_conf_pkg(args.filenpa_conf.value, direpa_pkg, dy_app["filen_json_app"])
            check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        pkg.remove(
            conf_pkg=conf_pkg,
            direpa_pkg=direpa_pkg,
            direpa_deps=direpa_deps,
            no_conf_src=args.no_conf_src.here,
            pkg_filters=args.packages.values,
        )
        sys.exit(0)

    if args.upgrade.here or args.update.here:
        check_rel()

        direpa_pkg=get_direpa_pkg(args.path_pkg.value, args.not_git.here)
        direpa_deps=get_direpa_deps(args.path_deps.value, direpa_pkg, dy_app["diren_pkgs"])
        
        filenpa_conf=os.path.join(direpa_pkg, dy_app["filen_json_app"])
        conf_pkg=pkg.Json_config(filenpa_conf)
        check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        arg_str="upgrade"
        pkg_names=args.upgrade.values
        if args.update.here:
            arg_str="update"
            pkg_names=args.update.values

        pkg.update_upgrade(
            arg_str=arg_str,
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_rel=get_direpa_rel(),
            filen_json_app=dy_app["filen_json_app"],
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_names=pkg_names,
        )

        sys.exit(0)

    if args.set_conf.here is True:
        pkg.set_conf(
            dy_app["filen_json_app"], 
            authors=args.authors.values,
            description=args.description.value,
            filen_main=args.filen_main.value,
            filenpa_conf=args.filenpa_conf.value,
            licenses=args.licenses.values,
            pkg_name=args.pkg_name.value,
            pkg_version=args.pkg_version.value,
            uuid4=args.uuid4.value,
        )
        sys.exit(0)

    if args.generate_db.here is True:
        check_rel()
        pkg.generate_db(
            direpa_rel=get_direpa_rel(),
            filen_json_rel=dy_app["filen_json_rel"],
        )
        sys.exit(0)

    if args.ls_rel.here is True:
        check_rel()
        pkg.ls_rel(
            direpa_rel=get_direpa_rel(),
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_filters=args.package_filters.values, 
            add_deps=args.add_deps.here,
        )
        sys.exit(0)
        
    if args.set_launcher.here is True:
        direpa_project=None
        if args.path_project.here:
            if args.path_project.value is None:
                direpa_project=os.getcwd()
            else:
                direpa_project=args.path_project.value

        pkg.set_launcher(
            app_name=args.set_launcher.value,
            direpa_project=direpa_project,
            overwrite=args.overwrite.here,
            system=dy_app["platform"],
        )
        sys.exit(0)

    if args.bump_version.here is True:
        check_rel()
        increment_type=None
        if args.major.here:
            increment_type="major"
        if args.minor.here:
            increment_type="minor"
        if args.patch.here:
            increment_type="patch"
        pkg.bump_version(
            db_data=pkg.Json_config(os.path.join(get_direpa_rel(), dy_app["filen_json_rel"])).data,
            diren_pkgs=dy_app["diren_pkgs"],
            direpa_rel=get_direpa_rel(),
            filen_json_app=dy_app["filen_json_app"], 
            filenpa_conf=args.filenpa_conf.value,
            increment=args.increment.here,
            increment_type=increment_type,
            is_git=not args.not_git.here,
            only_paths=[],
            pkg_name=args.pkg_name.value,
            direpa_pkg=args.path_pkg.value,
            save_filenpa_conf=True,
            version=args.bump_version.value,
        )
        sys.exit(0)

    if args.switch_bin.here is True:
        direpa_bin=dy_default_direpas["bin"]
        if args.path_bin.here:
            direpa_bin=args.path_bin.value
        pkg.switch_bin(
            direpa_bin=direpa_bin,
            pkg_name=args.pkg_name.value, 
            pkg_version=args.pkg_version.value, 
            system=dy_app["platform"],
        )
        sys.exit(0)

    if args.transfer.here is True:
        not_supported={"from": ["bin", "src", "wrk"], "to":["pkg", "src", "wrk"]}
        not_supported_with_value={"from": [], "to":[]}
        ptypes=["bin", "pkg", "rel", "src", "wrk"]
        directions=["from", "to"]
        dy_locations={"from": {"type": None, "direpa": None}, "to":{"type": None, "direpa": None}}

        for direction in directions:
            froms_tos=[]
            for ptype in ptypes:
                arg_str="{}_{}".format(direction, ptype)
                arg=dy_app["args"][arg_str]
                if arg.here:
                    if ptype in not_supported[direction]:
                        pkg.msg.error("At release --transfer argument not supported yet '{}'.".format(arg.alias), exit=1)
                    else:
                        dy_locations[direction]["type"]=ptype
                        if arg.value is not None:
                            if ptype in not_supported_with_value[direction]:
                                pkg.msg.error("At release --transfer argument not supported yet with a path '{}'.".format(arg.alias), exit=1)
                            else:
                                dy_locations[direction]["direpa"]=arg.value

                    froms_tos.append(arg.alias)
                    if len(froms_tos) > 1:
                        pkg.msg.error("At release --transfer select only one argument from {}".format(froms_tos), exit=1)
            
            if len(froms_tos) == 0:
                pkg.msg.error("At release --transfer select one argument from {}".format(["--"+direction+"-"+ptype for ptype in ptypes]), exit=1)

        check_rel()
        conf_from_rel=None
        if args.conf_from_rel.here is True:
            if args.conf_from_rel.value is None:
                conf_from_rel=True
            else:
                conf_from_rel=args.conf_from_rel.value

        if len([c for c in [args.no_conf.here, args.conf_from_rel.here, args.filenpa_conf.here] if c is True]) > 1:
            pkg.msg.error("You have to choose either --conf-from-rel, --filenpa-conf, or --no-conf", exit=1)


        dy_pkg_filters=[]
        if len(args.package_filters.values) == 0:
            dy_pkg_filters.append(pkg.get_dy_pkg_filter())
        else:
            for pfilter in args.package_filters.values:
                dy_pkg_filters.append(pkg.get_dy_pkg_filter(pfilter))

        for dy_pkg_filter in dy_pkg_filters:
            pkg.transfer(
                add_deps=not args.no_deps.here,
                conf_from_rel=conf_from_rel,
                diren_pkgs=dy_app["diren_pkgs"],
                dy_default_direpas=dy_default_direpas,
                dy_locations=dy_locations,
                dy_pkg_filter=dy_pkg_filter,
                filen_json_app=dy_app["filen_json_app"],
                filen_json_rel=dy_app["filen_json_rel"],
                filen_main=args.filen_main.value,
                filenpa_conf=args.filenpa_conf.value,
                is_beta=args.beta.here,
                is_git=not args.not_git.here,
                no_conf=args.no_conf.here,
                no_symlink=args.no_symlink.here,
                only_paths=args.only_paths.values,
                system=dy_app["platform"],
            )
        sys.exit(0)

    if args.rel_strip.here is True:
        check_rel()
        pkg.rel_strip(
            direpa_rel=get_direpa_rel(),
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_names=args.rel_strip.values,
        )
        sys.exit(0)



#  for arg_str in ["export_bin", "export_rel"]:

#         # "export_bin": {
#         # "aliases": "--export-bin",
#         # "args": "beta,from_rel,filenpa_conf,not_git,no_symlink,only_paths,from_pkg,pkg_name,pkg_version,to_bin",
#         # "info": "Send refined project 'current state' or 'selected version' to {user_profile}/data/bin and create symlink or send to path."
#         # },
#         # "export_rel": {
#         # "aliases": "--export-rel",
#         # "args": "no_deps,filenpa_conf,from_rel,not_git,pkg_name,only_paths,from_pkg,pkg_version,to_bin,to_rel",
#         # "info": "Send refined project 'selected version' to /$project_path/rel or path."
#         # },
#         check_rel()
#         arg=dy_app["args"][arg_str]
#         if arg.here:
#             if args.from_pkg.here is False and args.from_rel.here is False:
#                 pkg.msg.error("--from-pkg or --from-rel missing", exit=1)

#             options=dict(
#                 direpa_pkg=args.from_pkg.value,
#                 diren_pkgs=dy_app["diren_pkgs"],
#                 filen_json_app=dy_app["filen_json_app"],
#                 filen_json_rel=dy_app["filen_json_rel"],
#                 filenpa_conf=args.filenpa_conf.value,
#                 from_pkg=args.from_pkg.here,
#                 is_git=not args.not_git.here,
#                 only_paths=args.only_paths.values,
#                 pkg_name=args.pkg_name.value,
#                 pkg_version=args.pkg_version.value,
#                 system=dy_app["platform"],
#             )

#             direpa_rel_src=dy_default_direpas["rel"]
#             if args.from_rel.here is True:
#                 if args.from_rel.value is not None:
#                     direpa_rel_src=args.from_rel.value

#             if arg_str == "export_bin":
#                 # --export-bin
#                 #     --from-rel|--from-pkg
#                 #     --to-bin

#                 direpa_bin_dst=dy_default_direpas["bin"]
#                 if args.to_bin.here is True:
#                     if args.to_bin.value is None:
#                         direpa_bin_dst=dy_default_direpas["bin"]
#                     else:
#                         direpa_bin_dst=args.to_bin.value

#                 pkg.export(
#                     "export_bin",
#                     direpa_bin_dst=direpa_bin_dst,
#                     direpa_rel_src=direpa_rel_src,
#                     is_beta=args.beta.here,
#                     no_symlink=args.no_symlink.here,
#                     **options,
#                 )
                
#             elif arg_str == "export_rel":
#                 # --export-rel
#                 #     --from-rel|--from-pkg
#                 #     --to-rel

#                 direpa_rel_dst=dy_default_direpas["rel"]
#                 if args.to_rel.here is True:
#                     if args.to_rel.value is not None:
#                         direpa_rel_dst=args.to_rel.value
#                         check_rel(direpa_rel_dst)
#                 pkg.export( 
#                     "export_rel",
#                     add_deps=not args.no_deps.here,
#                     direpa_rel_src=direpa_rel_src,
#                     direpa_rel_dst=direpa_rel_dst,
#                     **options,
#                 )
#             sys.exit(0)
