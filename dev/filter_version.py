#!/usr/bin/env python3
# author: Gabriel Auger
# version: 4.4.11
# name: release
# license: MIT
import os, sys
import re
from pprint import pprint
import inspect
import json

from ..gpkgs import message as msg
from ..modules.prompt.prompt import prompt_boolean
from ..modules.json_config.json_config import Json_config
from ..modules.shell_helpers import shell_helpers as shell
from . import regex_obj as ro
from ..gpkgs.sort_separated import sort_separated

def get_preselected(reg_versions, version_component, reg_version_ftr ):
    if version_component == "major":
        if reg_version_ftr.major in  ["l", "L"]:
            latest=sorted([reg_version.major for reg_version in reg_versions])[-1]
            return [reg_version for reg_version in reg_versions if reg_version.major == latest]
        elif reg_version_ftr.major in  ["a", "A"]:
            return reg_versions
        else:
            return [reg_version for reg_version in reg_versions if reg_version.major == reg_version_ftr.major]
    elif version_component == "minor":
        if reg_version_ftr.minor in  ["l", "L"]:
            latest=sorted([reg_version.minor for reg_version in reg_versions])[-1]
            return [reg_version for reg_version in reg_versions if reg_version.minor == latest]
        elif reg_version_ftr.minor in  ["a", "A"]:
            return reg_versions
        else:
            return [reg_version for reg_version in reg_versions if reg_version.minor == reg_version_ftr.minor]
    elif version_component == "patch":
        if reg_version_ftr.patch in  ["l", "L"]:
            latest=sorted([reg_version.patch for reg_version in reg_versions])[-1]
            return [reg_version for reg_version in reg_versions if reg_version.patch == latest]
        elif reg_version_ftr.patch in  ["a", "A"]:
            return reg_versions
        else:
            return [reg_version for reg_version in reg_versions if reg_version.patch == reg_version_ftr.patch]

def filter_version(versions, version_ftr):
    reg_versions=[]
    non_reg_versions=[]
    versions_selected=[]

    for version in versions:
        reg_version=ro.Version_regex(version)
        if reg_version.match:
            reg_versions.append(reg_version)
        else:
            non_reg_versions.append(version)
    
    reg_version_ftr=ro.Version_filter_regex(version_ftr)
    if reg_version_ftr.match:
        if reg_versions:
            if reg_version_ftr.pattern == "numbers":
                if reg_version_ftr.text in [reg_version.text for reg_version in reg_versions]:
                    versions_selected.append(reg_version_ftr.text)
            elif reg_version_ftr.pattern == "last":
                versions_selected.append(sort_separated([reg_version.text for reg_version in reg_versions])[-1])
            elif reg_version_ftr.pattern == "all":
                versions_selected=[reg_version.text for reg_version in reg_versions]
            elif reg_version_ftr.pattern == "mixed":
                preselected_versions=reg_versions
                for component in ["major", "minor", "patch"]:
                    if preselected_versions:
                        preselected_versions=get_preselected(preselected_versions, component, reg_version_ftr)
                
                if preselected_versions:
                    versions_selected=[preselected_version.text for preselected_version in preselected_versions]

    else:
        for non_reg_version in non_reg_versions:
            if non_reg_version == "version_ftr":
                versions_selected.append(non_reg_version)

    return versions_selected
