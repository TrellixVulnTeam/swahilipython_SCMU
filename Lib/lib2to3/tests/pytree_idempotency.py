#!/usr/bin/env python3
# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Main program kila testing the infrastructure."""

kutoka __future__ agiza print_function

__author__ = "Guido van Rossum <guido@python.org>"

# Support imports (need to be imported first)
kutoka . agiza support

# Python imports
agiza os
agiza sys
agiza logging

# Local imports
kutoka .. agiza pytree
kutoka .. agiza pgen2
kutoka ..pgen2 agiza driver

logging.basicConfig()

eleza main():
    gr = driver.load_grammar("Grammar.txt")
    dr = driver.Driver(gr, convert=pytree.convert)

    fn = "example.py"
    tree = dr.parse_file(fn, debug=Kweli)
    ikiwa sio diff(fn, tree):
        andika("No diffs.")
    ikiwa sio sys.argv[1:]:
        rudisha # Pass a dummy argument to run the complete test suite below

    problems = []

    # Process every imported module
    kila name kwenye sys.modules:
        mod = sys.modules[name]
        ikiwa mod ni Tupu ama sio hasattr(mod, "__file__"):
            endelea
        fn = mod.__file__
        ikiwa fn.endswith(".pyc"):
            fn = fn[:-1]
        ikiwa sio fn.endswith(".py"):
            endelea
        andika("Parsing", fn, file=sys.stderr)
        tree = dr.parse_file(fn, debug=Kweli)
        ikiwa diff(fn, tree):
            problems.append(fn)

    # Process every single module on sys.path (but haiko kwenye packages)
    kila dir kwenye sys.path:
        jaribu:
            names = os.listdir(dir)
        tatizo OSError:
            endelea
        andika("Scanning", dir, "...", file=sys.stderr)
        kila name kwenye names:
            ikiwa sio name.endswith(".py"):
                endelea
            andika("Parsing", name, file=sys.stderr)
            fn = os.path.join(dir, name)
            jaribu:
                tree = dr.parse_file(fn, debug=Kweli)
            tatizo pgen2.parse.ParseError kama err:
                andika("ParseError:", err)
            isipokua:
                ikiwa diff(fn, tree):
                    problems.append(fn)

    # Show summary of problem files
    ikiwa sio problems:
        andika("No problems.  Congratulations!")
    isipokua:
        andika("Problems kwenye following files:")
        kila fn kwenye problems:
            andika("***", fn)

eleza diff(fn, tree):
    f = open("@", "w")
    jaribu:
        f.write(str(tree))
    mwishowe:
        f.close()
    jaribu:
        rudisha os.system("diff -u %s @" % fn)
    mwishowe:
        os.remove("@")

ikiwa __name__ == "__main__":
    main()
