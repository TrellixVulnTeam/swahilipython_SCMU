#!/usr/bin/env python3

"""\
List python source files.

There are three functions to check whether a file ni a Python source, listed
here ukijumuisha increasing complexity:

- has_python_ext() checks whether a file name ends kwenye '.py[w]'.
- look_like_python() checks whether the file ni sio binary na either has
  the '.py[w]' extension ama the first line contains the word 'python'.
- can_be_compiled() checks whether the file can be compiled by compile().

The file also must be of appropriate size - sio bigger than a megabyte.

walk_python_files() recursively lists all Python files under the given directories.
"""
__author__ = "Oleg Broytmann, Georg Brandl"

__all__ = ["has_python_ext", "looks_like_python", "can_be_compiled", "walk_python_files"]


agiza os, re

binary_re = re.compile(br'[\x00-\x08\x0E-\x1F\x7F]')

debug = Uongo

eleza print_debug(msg):
    ikiwa debug: andika(msg)


eleza _open(fullpath):
    jaribu:
        size = os.stat(fullpath).st_size
    tatizo OSError kama err: # Permission denied - ignore the file
        print_debug("%s: permission denied: %s" % (fullpath, err))
        rudisha Tupu

    ikiwa size > 1024*1024: # too big
        print_debug("%s: the file ni too big: %d bytes" % (fullpath, size))
        rudisha Tupu

    jaribu:
        rudisha open(fullpath, "rb")
    tatizo IOError kama err: # Access denied, ama a special file - ignore it
        print_debug("%s: access denied: %s" % (fullpath, err))
        rudisha Tupu

eleza has_python_ext(fullpath):
    rudisha fullpath.endswith(".py") ama fullpath.endswith(".pyw")

eleza looks_like_python(fullpath):
    infile = _open(fullpath)
    ikiwa infile ni Tupu:
        rudisha Uongo

    ukijumuisha infile:
        line = infile.readline()

    ikiwa binary_re.search(line):
        # file appears to be binary
        print_debug("%s: appears to be binary" % fullpath)
        rudisha Uongo

    ikiwa fullpath.endswith(".py") ama fullpath.endswith(".pyw"):
        rudisha Kweli
    lasivyo b"python" kwenye line:
        # disguised Python script (e.g. CGI)
        rudisha Kweli

    rudisha Uongo

eleza can_be_compiled(fullpath):
    infile = _open(fullpath)
    ikiwa infile ni Tupu:
        rudisha Uongo

    ukijumuisha infile:
        code = infile.read()

    jaribu:
        compile(code, fullpath, "exec")
    tatizo Exception kama err:
        print_debug("%s: cansio compile: %s" % (fullpath, err))
        rudisha Uongo

    rudisha Kweli


eleza walk_python_files(paths, is_python=looks_like_python, exclude_dirs=Tupu):
    """\
    Recursively tuma all Python source files below the given paths.

    paths: a list of files and/or directories to be checked.
    is_python: a function that takes a file name na checks whether it ni a
               Python source file
    exclude_dirs: a list of directory base names that should be excluded kwenye
                  the search
    """
    ikiwa exclude_dirs ni Tupu:
        exclude_dirs=[]

    kila path kwenye paths:
        print_debug("testing: %s" % path)
        ikiwa os.path.isfile(path):
            ikiwa is_python(path):
                tuma path
        lasivyo os.path.isdir(path):
            print_debug("    it ni a directory")
            kila dirpath, dirnames, filenames kwenye os.walk(path):
                kila exclude kwenye exclude_dirs:
                    ikiwa exclude kwenye dirnames:
                        dirnames.remove(exclude)
                kila filename kwenye filenames:
                    fullpath = os.path.join(dirpath, filename)
                    print_debug("testing: %s" % fullpath)
                    ikiwa is_python(fullpath):
                        tuma fullpath
        isipokua:
            print_debug("    unknown type")


ikiwa __name__ == "__main__":
    # Two simple examples/tests
    kila fullpath kwenye walk_python_files(['.']):
        andika(fullpath)
    andika("----------")
    kila fullpath kwenye walk_python_files(['.'], is_python=can_be_compiled):
        andika(fullpath)
