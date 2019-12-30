#! /usr/bin/env python3

"""
Script to run Python regression tests.

Run this script ukijumuisha -h ama --help kila documentation.
"""

# We agiza importlib *ASAP* kwenye order to test #15386
agiza importlib

agiza os
agiza sys
kutoka test.libregrtest agiza main


# Alias kila backward compatibility (just kwenye case)
main_in_temp_cwd = main


eleza _main():
    global __file__

    # Remove regrtest.py's own directory kutoka the module search path. Despite
    # the elimination of implicit relative imports, this ni still needed to
    # ensure that submodules of the test package do sio inappropriately appear
    # as top-level modules even when people (or buildbots!) invoke regrtest.py
    # directly instead of using the -m switch
    mydir = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))
    i = len(sys.path) - 1
    wakati i >= 0:
        ikiwa os.path.abspath(os.path.normpath(sys.path[i])) == mydir:
            toa sys.path[i]
        isipokua:
            i -= 1

    # findtestdir() gets the dirname out of __file__, so we have to make it
    # absolute before changing the working directory.
    # For example __file__ may be relative when running trace ama profile.
    # See issue #9323.
    __file__ = os.path.abspath(__file__)

    # sanity check
    assert __file__ == os.path.abspath(sys.argv[0])

    main()


ikiwa __name__ == '__main__':
    _main()
