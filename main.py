#!/usr/bin/env python3
if __name__ == "__main__":
    import getpass  
    import importlib
    import platform
    from pprint import pprint
    import json
    import os
    import sys

    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    args=pkg.Nargs(
        metadata=dict(
            executable="release",
        ),
        options_file="config/options.yaml", 
    ).get_args()

    dy_default_direpas=dict(
        bin=os.path.join(os.path.expanduser("~"), "fty", "bin"),
        pkg=os.getcwd(),
        rel=os.path.join(os.path.expanduser("~"), "fty", "rel"),
        src=os.path.join(os.path.expanduser("~"), "fty", "src"),
        wrk=os.path.join(os.path.expanduser("~"), "fty", "wrk"),
    )

    filenpa_json=os.path.join(direpa_script, "gpm.json")
    dy_app:dict
    with open(filenpa_json, "r") as f:
        dy_app=json.load(f)

    def check_direpa_rel(path_rel: str|None):
        tmp_path_rel:str
        if path_rel is None:
            tmp_path_rel=dy_default_direpas["rel"]
        else:
            tmp_path_rel=path_rel
        pkg.check_rel(filen_rel_default=dy_app["filen_json_rel"], direpa_rel=tmp_path_rel)
        return tmp_path_rel
    
    def get_direpa_deps(direpa_deps, direpa_pkg, diren_pkgs):
        if direpa_deps is None:
            return os.path.join(direpa_pkg, diren_pkgs)
        else:                    
            return direpa_deps

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
            restore=restore,
        )

    direpa_rel:str=""
    if args.restore._here:
        direpa_rel=check_direpa_rel(args.restore.path_rel._value)
        direpa_pkg=get_direpa_pkg(args.restore.path_pkg._value, args.restore.not_git._here)
        direpa_deps=get_direpa_deps(args.restore.path_deps._value, direpa_pkg, dy_app["diren_pkgs"])

        conf_pkg=get_conf_pkg(args.restore.filenpa_conf._value, direpa_pkg, dy_app["filen_json_app"])
        check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"], restore=True)

        pkg_filters=[]
        if args.restore._here:
            for dep in conf_pkg.data["deps"]: # type: ignore
                uuid4, alias, version, bound = dep.split("|")
                pkg_filters.append("{},{}".format(alias,version))
        
        pkg.import_pkgs(
            conf_db=pkg.Json_config(os.path.join(direpa_rel, dy_app["filen_json_rel"])),
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_rel=direpa_rel,
            filen_json_default=dy_app["filen_json_app"],
            filter_rules=[],
            is_template=False,
            no_conf_src=False,
            no_conf_dst=False,
            no_root_dir=False,
            pkg_filters=pkg_filters,
            keys=[],
        )

    elif args.import_pkgs._here:
        direpa_rel=check_direpa_rel(args.import_pkgs.path_rel._value)
        direpa_pkg=get_direpa_pkg(args.import_pkgs.path_pkg._value, args.import_pkgs.not_git._here)
        direpa_deps=get_direpa_deps(args.import_pkgs.path_deps._value, direpa_pkg, dy_app["diren_pkgs"])

        conf_pkg=None
        if args.import_pkgs._here and args.import_pkgs.no_conf_src._here is False:
            conf_pkg=get_conf_pkg(args.import_pkgs.filenpa_conf._value, direpa_pkg, dy_app["filen_json_app"])
            check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        pkg.import_pkgs(
            conf_db=pkg.Json_config(os.path.join(direpa_rel, dy_app["filen_json_rel"])),
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_rel=direpa_rel,
            filen_json_default=dy_app["filen_json_app"],
            filter_rules=args.import_pkgs.filter_rules._values,
            is_template=args.import_pkgs.keys._here,
            no_conf_src=args.import_pkgs.no_conf_src._here,
            no_conf_dst=args.import_pkgs.no_conf_dst._here,
            no_root_dir=args.import_pkgs.no_root_dir._here,
            pkg_filters=args.import_pkgs.package_filters._values,
            keys=args.import_pkgs.keys._value,
        )

    elif args.remove._here:
        check_direpa_rel(None)

        direpa_pkg=get_direpa_pkg(args.remove.path_pkg._value, args.remove.not_git._here)
        direpa_deps=get_direpa_deps(args.remove.path_deps._value, direpa_pkg, dy_app["diren_pkgs"])

        conf_pkg=None
        if args.remove.no_conf_src._here is False:
            conf_pkg=get_conf_pkg(args.remove.filenpa_conf._value, direpa_pkg, dy_app["filen_json_app"])
            check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        pkg.remove(
            conf_pkg=conf_pkg,
            direpa_pkg=direpa_pkg,
            direpa_deps=direpa_deps,
            no_conf_src=args.remove.no_conf_src._here,
            pkg_filters=args.remove.packages._values,
        )

    elif args.upgrade._here or args.update._here:
        arg_str:str
        if args.update._here:
            arg_str="update"
        elif args.upgrade._here:
            arg_str="upgrade"
        else:
            raise NotImplementedError()

        direpa_rel=check_direpa_rel(args._[arg_str].path_rel._value)
        direpa_pkg=get_direpa_pkg(args._[arg_str].path_pkg._value, args._[arg_str].not_git._here)
        direpa_deps=get_direpa_deps(args._[arg_str].path_deps._value, direpa_pkg, dy_app["diren_pkgs"])
        
        filenpa_conf=os.path.join(direpa_pkg, dy_app["filen_json_app"])
        conf_pkg=pkg.Json_config(filenpa_conf)
        check_pkg_integrity(conf_pkg, direpa_deps, dy_app["filen_json_app"])

        pkg_aliases=args._[arg_str]._values

        pkg.update_upgrade(
            arg_str=arg_str,
            conf_pkg=conf_pkg,
            direpa_deps=direpa_deps,
            direpa_pkg=direpa_pkg,
            direpa_rel=direpa_rel,
            filen_json_app=dy_app["filen_json_app"],
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_aliases=pkg_aliases,
        )

    elif args.set_conf._here is True:
        pkg.set_conf(
            dy_app["filen_json_app"], 
            authors=args.set_conf.authors._values,
            description=args.set_conf.description._value,
            filen_main=args.set_conf.filen_main._value,
            filenpa_conf=args.set_conf.filenpa_conf._value,
            licenses=args.set_conf.licenses._values,
            pkg_alias=args.set_conf.pkg_alias._value,
            pkg_name=args.set_conf.pkg_name._value,
            pkg_version=args.set_conf.pkg_version._value,
            uuid4=args.set_conf.uuid4._value,
        )
    elif args.generate_db._here is True:
        pkg.generate_db(
            direpa_rel=check_direpa_rel(args.generate_db.path_rel._value),
            filen_json_rel=dy_app["filen_json_rel"],
        )
    elif args.ls_rel._here is True:
        direpa_rel=check_direpa_rel(args.ls_rel.path_rel._value)
        pkg.ls_rel(
            direpa_rel=direpa_rel,
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_filters=args.ls_rel.package_filters._values, 
            add_deps=args.ls_rel.add_deps._here,
        )
    elif args.set_launcher._here is True:
        direpa_project=None
        if args.set_launcher.path_project._here:
            if args.set_launcher.path_project._value is None:
                direpa_project=os.getcwd()
            else:
                direpa_project=args.set_launcher.path_project._value

        pkg.set_launcher(
            pkg_alias=args.set_launcher._value,
            direpa_project=direpa_project,
            overwrite=args.set_launcher.overwrite._here,
            system=platform.system(),
        )
    elif args.switch_bin._here is True:
        direpa_bin=dy_default_direpas["bin"]
        if args.switch_bin.path_bin._here:
            direpa_bin=args.switch_bin.path_bin._value
        pkg.switch_bin(
            direpa_bin=direpa_bin,
            pkg_alias=args.switch_bin.pkg_alias._value,
            pkg_uuid4=args.switch_bin.uuid4._value, 
            pkg_version=args.switch_bin.pkg_version._value, 
            system=platform.system(),
        )
    elif args.transfer._here is True:
        not_supported={"from": ["bin", "src", "wrk"], "to":["pkg", "src", "wrk"]}
        not_supported_with_value: dict={"from": [], "to":[]}
        ptypes=["bin", "pkg", "rel", "src", "wrk"]
        directions=["from", "to"]
        dy_locations={"from": {"type": None, "direpa": None}, "to":{"type": None, "direpa": None}}

        for direction in directions:
            froms_tos=[]
            for ptype in ptypes:
                arg_str="{}_{}".format(direction, ptype)
                arg=args.transfer._[arg_str]
                if arg._here:
                    if ptype in not_supported[direction]:
                        pkg.msg.error("At release --transfer argument not supported yet '{}'.".format(arg.alias), exit=1)
                    else:
                        dy_locations[direction]["type"]=ptype # type: ignore
                        if arg._value is not None:
                            if ptype in not_supported_with_value[direction]:
                                pkg.msg.error("At release --transfer argument not supported yet with a path '{}'.".format(arg.alias), exit=1)
                            else:
                                dy_locations[direction]["direpa"]=arg._value

                    froms_tos.append(arg._alias)
                    if len(froms_tos) > 1:
                        pkg.msg.error("At release --transfer select only one argument from {}".format(froms_tos), exit=1)
            
            if len(froms_tos) == 0:
                pkg.msg.error("At release --transfer select one argument from {}".format(["--"+direction+"-"+ptype for ptype in ptypes]), exit=1)

        check_direpa_rel(None)
        conf_from_rel=None
        if args.transfer.from_pkg.conf_from_rel._here is True:
            if args.transfer.from_pkg.conf_from_rel._value is None:
                conf_from_rel=True
            else:
                conf_from_rel=args.transfer.from_pkg.conf_from_rel._value

        if len([c for c in [args.transfer.from_pkg.no_conf._here, args.transfer.from_pkg.conf_from_rel._here, args.transfer.from_pkg.filenpa_conf._here] if c is True]) > 1:
            pkg.msg.error("You have to choose either --conf-from-rel, --filenpa-conf, or --no-conf", exit=1)


        dy_pkg_filters=[]
        if len(args.transfer.package_filters._values) == 0:
            dy_pkg_filters.append(pkg.get_dy_pkg_filter())
        else:
            for pfilter in args.transfer.package_filters._values:
                dy_pkg_filters.append(pkg.get_dy_pkg_filter(pfilter))

        for dy_pkg_filter in dy_pkg_filters:
            pkg.transfer(
                add_deps=args.transfer.from_rel.no_deps._here is False or args.transfer.to_rel.no_deps._here is False,
                conf_from_rel=conf_from_rel,
                diren_pkgs=dy_app["diren_pkgs"],
                dy_default_direpas=dy_default_direpas,
                dy_locations=dy_locations,
                dy_pkg_filter=dy_pkg_filter,
                filen_json_app=dy_app["filen_json_app"],
                filen_json_rel=dy_app["filen_json_rel"],
                filen_main=args.transfer.to_bin.filen_main._value,
                filenpa_conf=args.transfer.from_pkg.filenpa_conf._value,
                is_beta=args.transfer.to_bin.beta._here,
                is_git=not args.transfer.from_pkg.not_git._here,
                no_conf=args.transfer.from_pkg.no_conf._here,
                no_symlink=args.transfer.to_bin.no_symlink._here,
                only_paths=args.transfer.only_paths._values,
                system=platform.system(),
            )
    elif args.rel_strip._here is True:
        direpa_rel=check_direpa_rel(args.rel_strip.path_rel._value)
        pkg.rel_strip(
            direpa_rel=direpa_rel,
            filen_json_rel=dy_app["filen_json_rel"],
            pkg_aliases=args.rel_strip._values,
        )
