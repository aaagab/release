#!/usr/bin/env python3
import re
import sys
import textwrap

from ..gpkgs import message as msg

class Regex_obj():
    def __init__(self, group_string):
        self.type=""
        self.group_string=group_string
        self.reg_arr=group_string[1:-1].split(")(")
        self.string="".join(self.reg_arr)
        self.match=False

class Version_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"(^)(\d+)(\.)(\d+)(\.)(\d+)($)")
        self.type="version"
        self.set_text(txt)
        self.description="Only this version is imported. No upgrade."

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.major=self.matching_obj.group(2)
                self.minor=self.matching_obj.group(4)
                self.patch=self.matching_obj.group(6)
                self.major_minor=self.major+"."+self.minor
                self.major_minor_patch=self.major_minor+"."+self.patch             
            else:
                self.match=False
                self.major=""
                self.minor=""
                self.patch=""
                self.major_minor=""
        
        return self

    def equals(self, dct_reg_pkgs):
        if dct_reg_pkgs["reg_version"].major_minor_patch == self.major_minor_patch:
            return True
        else:
            return False

    def compare(self, reg_pkg):
        if self.major < reg_pkg.major:
            return "smaller"
        elif self.major == reg_pkg.major:
            if self.minor < reg_pkg.minor:
                return "smaller"
            elif self.minor == reg_pkg.minor:
                if self.patch < reg_pkg.patch:
                    return "smaller"
                elif self.patch == reg_pkg.patch:
                    return "equals"
                elif self.patch > reg_pkg.patch:
                    return "bigger"
            elif self.minor > reg_pkg.minor:
                return "bigger"
        elif self.major > reg_pkg.major:
            return "bigger"

    def print_error(self):
        msg.error("'{}' does not follow regex '{}'".format(self.text, self.string))

class Version_major_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"(^)(\d+)(\.)(X)(\.)(X)($)")
        self.type="major"
        self.set_text(txt)
        self.description="Only this major version is imported. upgrade can be at minor or patch level."

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.major=self.matching_obj.group(2)
            else:
                self.match=False

        return self

    def equals(self, dct_reg_pkgs):
        if dct_reg_pkgs["reg_version"].major == self.major:
            return True
        else:
            return False

class Version_latest_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"(^)(X)(\.)(X)(\.)(X)($)")
        self.type="latest"
        self.set_text(txt)
        self.description="Only latest version is imported. upgrade can be at minor or patch level."

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.major=self.matching_obj.group(2)
            else:
                self.match=False

        return self

    def equals(self, dct_reg_pkgs):
        if dct_reg_pkgs["reg_version"].text == dct_reg_pkgs["versions"][-1]:
            return True
        else:
            return False

class Version_minor_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"(^)(\d+)(\.)(\d+)(\.)(X)($)")
        self.type="minor"
        self.set_text(txt)
        self.description="Only this major and minor version is imported. upgrade can be at patch level."

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.major=self.matching_obj.group(2)
                self.minor=self.matching_obj.group(4)
                self.major_minor=self.major+"."+self.minor
            else:
                self.match=False

        return self

    def equals(self, dct_reg_pkgs):
        if dct_reg_pkgs["reg_version"].major_minor == self.major_minor:
            return True
        else:
            return False

class Package_name_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"^[A-Za-z][A-Za-z0-9_-]*$")
        self.set_text(txt)

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            self.match=False
            if not self.matching_obj:
                msg.warning(
                    "Package name '{}' syntax error".format(self.text),
                    "Authorized syntax is '{}'".format(self.string)
                )
            else:
                self.match=True
                if len(self.text) > 128:
                    self.match=False
                    msg.warning(
                        "Package name '{}' syntax error, length is '{}'".format(self.text, len(self.text)),
                        "Minimum length is '1' character",
                        "Maximum length is '128' characters",
                    )
                
                reg_uuid4=Uuid4_regex(self.text)
                if reg_uuid4.match:
                    self.match=False
                    msg.warning(
                        "Package name '{}' syntax error".format(self.text),
                        "Format can't be similar to uuid format.",
                        "'{}'".format(reg_uuid4.string)
                    )

        return self

class Uuid4_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"^[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}$")
        self.set_text(txt)

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
            else:
                self.match=False

        return self

    def print_error(self):
        msg.error("'{}' does not follow uuid4 regex '{}'".format(self.text, self.string))

class Version_filter_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"(^)([\d+|A|a|L|l])(\.)([\d+|A|a|L|l])(\.)([\d+|A|a|L|l])($)")
        self.type="filter_version"
        self.set_text(txt)
        self.description="Filter to search accurately a version. L means last, A means any."

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.major=self.matching_obj.group(2)
                self.minor=self.matching_obj.group(4)
                self.patch=self.matching_obj.group(6)
                self.major_minor=self.major+"."+self.minor
                self.major_minor_patch=self.major_minor+"."+self.patch
                # print(self.major, isinstance(self.minor, int))
                # if isinstance(self.major, int) and isinstance(self.minor, int) and isinstance(self.patch, int):
                    # print("mike")
                if self.major.isdigit() and self.minor.isdigit() and self.patch.isdigit():
                    self.pattern="numbers"
                elif self.major in ["L", "l"] and self.minor in ["L", "l"] and self.patch in ["L", "l"]:
                    self.pattern="last"
                elif self.major in ["A", "a"] and self.minor in ["A", "a"] and self.patch in ["A", "a"]:
                    self.pattern="all"
                else:
                    self.pattern="mixed"
            else:
                self.match=False
                self.major=""
                self.minor=""
                self.patch=""
                self.major_minor=""
                self.major_minor_patch=""
                self.pattern=""
        
        return self

    def equals(self, reg_pkg):
        if reg_pkg.major_minor_patch == self.major_minor_patch:
            return True
        else:
            return False     

    def print_error(self):
        msg.error("'{}' does not follow regex '{}'".format(self.text, self.string))

class Diren_index_regex(Regex_obj):
    def __init__(self, txt=""):
        Regex_obj.__init__(self, r"^([_lg])([0-9a-fA-F]+)$")
        self.set_text(txt)

    def set_text(self, txt):
        if txt != "":
            self.text=txt
            self.matching_obj=re.match(self.group_string, txt)
            if self.matching_obj:
                self.match=True
                self.prefix=self.matching_obj.group(1)
                self.index=int(self.matching_obj.group(2), 16)
            else:
                self.match=False
                self.index=""
                self.prefix=""

        return self

def get_all_version_type_regex(text=""):
    regexes=[]

    regexes.append(Version_major_regex(text))
    regexes.append(Version_minor_regex(text))
    regexes.append(Version_regex(text))
    regexes.append(Version_latest_regex(text))

    return regexes

def get_obj_version_type_regex(text):
    regexes=get_all_version_type_regex(text)

    for reg in regexes:
        if reg.match:
            return reg

    return False

    # txt_regexes=""
    # prefix="\t  "
    # for reg in regexes:
    #     txt_regexes+="\ttype: {}\n\t{}\n{}\n\n".format(
    #         reg.type,
    #         reg.string,
    #         "\n".join(textwrap.wrap(reg.description, initial_indent=prefix+"- ", subsequent_indent=prefix))
    #         )

    # msg.error(
    #     "Version type '"+regexes[0].text+"' unknown.",
    #     "Authorized Version types are :\n"+txt_regexes,
    # )
    # sys.exit(1)

def get_copy_regex_obj(version_type):
    for obj in get_all_version_type_regex():
        if obj.type == version_type:
            return obj
    