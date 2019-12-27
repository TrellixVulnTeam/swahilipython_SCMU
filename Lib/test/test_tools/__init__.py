"""Support functions for testing scripts in the Tools directory."""
agiza os
agiza unittest
agiza importlib
kutoka test agiza support

basepath = os.path.dirname(                 # <src/install dir>
                os.path.dirname(                # Lib
                    os.path.dirname(                # test
                        os.path.dirname(__file__))))    # test_tools

toolsdir = os.path.join(basepath, 'Tools')
scriptsdir = os.path.join(toolsdir, 'scripts')

eleza skip_if_missing():
    ikiwa not os.path.isdir(scriptsdir):
        raise unittest.SkipTest('scripts directory could not be found')

eleza import_tool(toolname):
    with support.DirsOnSysPath(scriptsdir):
        rudisha importlib.import_module(toolname)

eleza load_tests(*args):
    rudisha support.load_package_tests(os.path.dirname(__file__), *args)
