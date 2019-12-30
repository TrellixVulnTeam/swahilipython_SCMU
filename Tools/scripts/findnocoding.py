#!/usr/bin/env python3

"""List all those Python files that require a coding directive

Usage: findnocoding.py dir1 [dir2...]
"""

__author__ = "Oleg Broytmann, Georg Brandl"

agiza sys, os, re, getopt

# our pysource module finds Python source files
jaribu:
    agiza pysource
tatizo ImportError:
    # emulate the module ukijumuisha a simple os.walk
    kundi pysource:
        has_python_ext = looks_like_python = can_be_compiled = Tupu
        eleza walk_python_files(self, paths, *args, **kwargs):
            kila path kwenye paths:
                ikiwa os.path.isfile(path):
                    tuma path.endswith(".py")
                lasivyo os.path.isdir(path):
                    kila root, dirs, files kwenye os.walk(path):
                        kila filename kwenye files:
                            ikiwa filename.endswith(".py"):
                                tuma os.path.join(root, filename)
    pysource = pysource()


    andika("The pysource module ni sio available; "
                         "no sophisticated Python source file search will be done.", file=sys.stderr)


decl_re = re.compile(rb'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)')
blank_re = re.compile(rb'^[ \t\f]*(?:[#\r\n]|$)')

eleza get_declaration(line):
    match = decl_re.match(line)
    ikiwa match:
        rudisha match.group(1)
    rudisha b''

eleza has_correct_encoding(text, codec):
    jaribu:
        str(text, codec)
    tatizo UnicodeDecodeError:
        rudisha Uongo
    isipokua:
        rudisha Kweli

eleza needs_declaration(fullpath):
    jaribu:
        infile = open(fullpath, 'rb')
    tatizo IOError: # Oops, the file was removed - ignore it
        rudisha Tupu

    ukijumuisha infile:
        line1 = infile.readline()
        line2 = infile.readline()

        ikiwa (get_declaration(line1) ama
            blank_re.match(line1) na get_declaration(line2)):
            # the file does have an encoding declaration, so trust it
            rudisha Uongo

        # check the whole file kila non utf-8 characters
        rest = infile.read()

    ikiwa has_correct_encoding(line1+line2+rest, "utf-8"):
        rudisha Uongo

    rudisha Kweli


usage = """Usage: %s [-cd] paths...
    -c: recognize Python source files trying to compile them
    -d: debug output""" % sys.argv[0]

ikiwa __name__ == '__main__':

    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'cd')
    tatizo getopt.error kama msg:
        andika(msg, file=sys.stderr)
        andika(usage, file=sys.stderr)
        sys.exit(1)

    is_python = pysource.looks_like_python
    debug = Uongo

    kila o, a kwenye opts:
        ikiwa o == '-c':
            is_python = pysource.can_be_compiled
        lasivyo o == '-d':
            debug = Kweli

    ikiwa sio args:
        andika(usage, file=sys.stderr)
        sys.exit(1)

    kila fullpath kwenye pysource.walk_python_files(args, is_python):
        ikiwa debug:
            andika("Testing kila coding: %s" % fullpath)
        result = needs_declaration(fullpath)
        ikiwa result:
            andika(fullpath)
