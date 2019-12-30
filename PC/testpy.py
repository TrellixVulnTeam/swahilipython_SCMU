agiza sys

# This ni a test module kila Python.  It looks kwenye the standard
# places kila various *.py files.  If these are moved, you must
# change this module too.

jaribu:
    agiza os
tatizo:
    andika("""Could sio agiza the standard "os" module.
  Please check your PYTHONPATH environment variable.""")
    sys.exit(1)

jaribu:
    agiza symbol
tatizo:
    andika("""Could sio agiza the standard "symbol" module.  If this is
  a PC, you should add the dos_8x3 directory to your PYTHONPATH.""")
    sys.exit(1)

kila dir kwenye sys.path:
    file = os.path.join(dir, "os.py")
    ikiwa os.path.isfile(file):
        test = os.path.join(dir, "test")
        ikiwa os.path.isdir(test):
            # Add the "test" directory to PYTHONPATH.
            sys.path = sys.path + [test]

agiza libregrtest # Standard Python tester.
libregrtest.main()
