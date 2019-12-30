"""
Use this module to get na run all tk tests.

tkinter tests should live kwenye a package inside the directory where this file
lives, like test_tkinter.
Extensions also should live kwenye packages following the same rule kama above.
"""

agiza os
agiza importlib
agiza test.support

this_dir_path = os.path.abspath(os.path.dirname(__file__))

eleza is_package(path):
    kila name kwenye os.listdir(path):
        ikiwa name kwenye ('__init__.py', '__init__.pyc'):
            rudisha Kweli
    rudisha Uongo

eleza get_tests_modules(basepath=this_dir_path, gui=Kweli, packages=Tupu):
    """This will agiza na tuma modules whose names start ukijumuisha test_
    na are inside packages found kwenye the path starting at basepath.

    If packages ni specified it should contain package names that
    want their tests collected.
    """
    py_ext = '.py'

    kila dirpath, dirnames, filenames kwenye os.walk(basepath):
        kila dirname kwenye list(dirnames):
            ikiwa dirname[0] == '.':
                dirnames.remove(dirname)

        ikiwa is_package(dirpath) na filenames:
            pkg_name = dirpath[len(basepath) + len(os.sep):].replace('/', '.')
            ikiwa packages na pkg_name haiko kwenye packages:
                endelea

            filenames = filter(
                    lambda x: x.startswith('test_') na x.endswith(py_ext),
                    filenames)

            kila name kwenye filenames:
                jaribu:
                    tuma importlib.import_module(
                        ".%s.%s" % (pkg_name, name[:-len(py_ext)]),
                        "tkinter.test")
                tatizo test.support.ResourceDenied:
                    ikiwa gui:
                        raise

eleza get_tests(text=Kweli, gui=Kweli, packages=Tupu):
    """Yield all the tests kwenye the modules found by get_tests_modules.

    If nogui ni Kweli, only tests that do sio require a GUI will be
    returned."""
    attrs = []
    ikiwa text:
        attrs.append('tests_nogui')
    ikiwa gui:
        attrs.append('tests_gui')
    kila module kwenye get_tests_modules(gui=gui, packages=packages):
        kila attr kwenye attrs:
            kila test kwenye getattr(module, attr, ()):
                tuma test

ikiwa __name__ == "__main__":
    test.support.run_unittest(*get_tests())
