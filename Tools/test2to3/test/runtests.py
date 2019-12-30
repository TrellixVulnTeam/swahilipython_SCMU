# Fictitious test runner kila the project

agiza sys, os

ikiwa sys.version_info > (3,):
    # copy test suite over to "build/lib" na convert it
    kutoka distutils.util agiza copydir_run_2to3
    testroot = os.path.dirname(__file__)
    newroot = os.path.join(testroot, '..', 'build/lib/test')
    copydir_run_2to3(testroot, newroot)
    # kwenye the following imports, pick up the converted modules
    sys.path[0] = newroot

# run the tests here...

kutoka test_foo agiza FooTest

agiza unittest
unittest.main()
