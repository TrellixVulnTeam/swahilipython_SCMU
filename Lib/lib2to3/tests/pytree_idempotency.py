#!/usr/bin/env python3
# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Main program for testing the infrastructure."""

kutoka __future__ agiza print_function

__author__ = "Guido van Rossum <guido@python.org>"

# Support agizas (need to be imported first)
kutoka . agiza support

# Python agizas
agiza os
agiza sys
agiza logging

# Local agizas
kutoka .. agiza pytree
kutoka .. agiza pgen2
kutoka ..pgen2 agiza driver

logging.basicConfig()

eleza main():
    gr = driver.load_grammar("Grammar.txt")
    dr = driver.Driver(gr, convert=pytree.convert)

    fn = "example.py"
    tree = dr.parse_file(fn, debug=True)
    ikiwa not diff(fn, tree):
        andika("No diffs.")
    ikiwa not sys.argv[1:]:
        rudisha # Pass a dummy argument to run the complete test suite below

    problems = []

    # Process every imported module
    for name in sys.modules:
        mod = sys.modules[name]
        ikiwa mod is None or not hasattr(mod, "__file__"):
            continue
        fn = mod.__file__
        ikiwa fn.endswith(".pyc"):
            fn = fn[:-1]
        ikiwa not fn.endswith(".py"):
            continue
        andika("Parsing", fn, file=sys.stderr)
        tree = dr.parse_file(fn, debug=True)
        ikiwa diff(fn, tree):
            problems.append(fn)

    # Process every single module on sys.path (but not in packages)
    for dir in sys.path:
        try:
            names = os.listdir(dir)
        except OSError:
            continue
        andika("Scanning", dir, "...", file=sys.stderr)
        for name in names:
            ikiwa not name.endswith(".py"):
                continue
            andika("Parsing", name, file=sys.stderr)
            fn = os.path.join(dir, name)
            try:
                tree = dr.parse_file(fn, debug=True)
            except pgen2.parse.ParseError as err:
                andika("ParseError:", err)
            else:
                ikiwa diff(fn, tree):
                    problems.append(fn)

    # Show summary of problem files
    ikiwa not problems:
        andika("No problems.  Congratulations!")
    else:
        andika("Problems in following files:")
        for fn in problems:
            andika("***", fn)

eleza diff(fn, tree):
    f = open("@", "w")
    try:
        f.write(str(tree))
    finally:
        f.close()
    try:
        rudisha os.system("diff -u %s @" % fn)
    finally:
        os.remove("@")

ikiwa __name__ == "__main__":
    main()
