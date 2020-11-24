"""Filename globbing utility."""

# Modified by Gabriel Auger 2019 added excluded_dirs parameter
# modified to make it work with gitignore rules.

import os
import re
import fnmatch
import sys

__all__ = ["glob", "iglob", "escape"]

def glob(excluded_dirs, pathname, *, recursive=False):
    """Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    return list(iglob(excluded_dirs, pathname, recursive=recursive))

def iglob(excluded_dirs, pathname, *, recursive=False):
    """Return an iterator which yields the paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    """
    it = _iglob(pathname, excluded_dirs,recursive)
    if recursive and _isrecursive(pathname):
        s = next(it)  # skip empty string
        assert not s
    return it

def _iglob(pathname, excluded_dirs, recursive):
    dirname, basename = os.path.split(pathname)


    if not has_magic(pathname):
        if basename:
            if os.path.lexists(pathname):
                yield pathname
        else:
            # Patterns ending with a slash should match only directories
            if os.path.isdir(dirname):
                yield pathname
        return

    

    if not dirname:
        if recursive and _isrecursive(basename):
            yield from glob2(excluded_dirs, dirname, basename)
        else:
            yield from glob1(excluded_dirs, dirname, basename)
        return

    # `os.path.split()` returns the argument itself as a dirname if it is a
    # drive or UNC path.  Prevent an infinite recursion if a drive or UNC path
    # contains magic characters (i.e. r'\\?\C:').
    if dirname != pathname and has_magic(dirname):
        dirs = _iglob(dirname, excluded_dirs, recursive)
    else:
        dirs = [dirname]

    if has_magic(basename):
        if recursive and _isrecursive(basename):
            glob_in_dir = glob2
        else:
            glob_in_dir = glob1
    else:
        glob_in_dir = glob0

    for dirname in dirs:
        for name in glob_in_dir(excluded_dirs, dirname, basename):
            yield os.path.join(dirname, name)

# These 2 helper functions non-recursively glob inside a literal directory.
# They return a list of basenames. `glob1` accepts a pattern while `glob0`
# takes a literal basename (so it only has to check for its existence).

def glob1(excluded_dirs, dirname, pattern):
    if not dirname:
        if isinstance(pattern, bytes):
            dirname = bytes(os.curdir, 'ASCII')
        else:
            dirname = os.curdir

    try:
        tmp_dir=get_dir(dirname)
        names=[]
        if not is_dir_excluded(tmp_dir, excluded_dirs):
            for elem in os.listdir(dirname):
                path=os.path.join(dirname, elem)
                tmp_dir=get_dir(path)
                if not is_dir_excluded(tmp_dir, excluded_dirs):
                    names.append(elem)
    except OSError:
        return []
    # if not _ishidden(pattern):
        # names = [x for x in names if not _ishidden(x)]

    return fnmatch.filter(names, pattern)

def is_dir_excluded(dirname, excluded_dirs):
    excluded=False
    for exdir in excluded_dirs:
        reg_str=r"{}*".format(exdir)
        if re.match(reg_str, dirname):
            return True

    return False

def get_dir(path):
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)

def glob0(excluded_dirs, dirname, basename):
    if not basename:
        # `os.path.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        if os.path.isdir(dirname):
            if not is_dir_excluded(dirname, excluded_dirs):
                return [basename]
    else:
        path=os.path.join(dirname, basename)
        if os.path.lexists(path):
            if not is_dir_excluded(get_dir(path), excluded_dirs):
                return [basename]
    return []

# This helper function recursively yields relative pathnames inside a literal
# directory.

def glob2(excluded_dirs, dirname, pattern):
    assert _isrecursive(pattern)
    yield pattern[:0]
    yield from _rlistdir(excluded_dirs, dirname)

# Recursively yields relative pathnames inside a literal directory.
def _rlistdir(excluded_dirs, dirname):
    if not dirname:
        if isinstance(dirname, bytes):
            dirname = bytes(os.curdir, 'ASCII')
        else:
            dirname = os.curdir

    try:
        tmp_dir=get_dir(dirname)
        names=[]
        if not is_dir_excluded(tmp_dir, excluded_dirs):
            for elem in os.listdir(dirname):
                path=os.path.join(dirname, elem)
                tmp_dir=get_dir(path)
                if not is_dir_excluded(tmp_dir, excluded_dirs):
                    names.append(elem)
    except os.error:
        return
    for x in names:
        # if not _ishidden(x):
        yield x
        path = os.path.join(dirname, x) if dirname else x
        for y in _rlistdir(excluded_dirs, path):
            yield os.path.join(x, y)

magic_check = re.compile('([*?[])')
magic_check_bytes = re.compile(b'([*?[])')

def has_magic(s):
    if isinstance(s, bytes):
        match = magic_check_bytes.search(s)
    else:
        match = magic_check.search(s)
    return match is not None

def _ishidden(path):
    return path[0] in ('.', b'.'[0])

def _isrecursive(pattern):
    if isinstance(pattern, bytes):
        return pattern == b'**'
    else:
        return pattern == '**'

def escape(pathname):
    """Escape all special characters.
    """
    # Escaping is done by wrapping any of "*?[" between square brackets.
    # Metacharacters do not work in the drive part and shouldn't be escaped.
    drive, pathname = os.path.splitdrive(pathname)
    if isinstance(pathname, bytes):
        pathname = magic_check_bytes.sub(br'[\1]', pathname)
    else:
        pathname = magic_check.sub(r'[\1]', pathname)
    return drive + pathname
