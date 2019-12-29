agiza os
agiza errno
agiza importlib.machinery
agiza py_compile
agiza shutil
agiza unittest
agiza tempfile

kutoka test agiza support

agiza modulefinder

TEST_DIR = tempfile.mkdtemp()
TEST_PATH = [TEST_DIR, os.path.dirname(tempfile.__file__)]

# Each test description ni a list of 5 items:
#
# 1. a module name that will be imported by modulefinder
# 2. a list of module names that modulefinder ni required to find
# 3. a list of module names that modulefinder should complain
#    about because they are sio found
# 4. a list of module names that modulefinder should complain
#    about because they MAY be sio found
# 5. a string specifying packages to create; the format ni obvious imo.
#
# Each package will be created kwenye TEST_DIR, na TEST_DIR will be
# removed after the tests again.
# Modulefinder searches kwenye a path that contains TEST_DIR, plus
# the standard Lib directory.

maybe_test = [
    "a.module",
    ["a", "a.module", "sys",
     "b"],
    ["c"], ["b.something"],
    """\
a/__init__.py
a/module.py
                                kutoka b agiza something
                                kutoka c agiza something
b/__init__.py
                                kutoka sys agiza *
"""]

maybe_test_new = [
    "a.module",
    ["a", "a.module", "sys",
     "b", "__future__"],
    ["c"], ["b.something"],
    """\
a/__init__.py
a/module.py
                                kutoka b agiza something
                                kutoka c agiza something
b/__init__.py
                                kutoka __future__ agiza absolute_agiza
                                kutoka sys agiza *
"""]

package_test = [
    "a.module",
    ["a", "a.b", "a.c", "a.module", "mymodule", "sys"],
    ["blahblah", "c"], [],
    """\
mymodule.py
a/__init__.py
                                agiza blahblah
                                kutoka a agiza b
                                agiza c
a/module.py
                                agiza sys
                                kutoka a agiza b kama x
                                kutoka a.c agiza sillyname
a/b.py
a/c.py
                                kutoka a.module agiza x
                                agiza mymodule kama sillyname
                                kutoka sys agiza version_info
"""]

absolute_import_test = [
    "a.module",
    ["a", "a.module",
     "b", "b.x", "b.y", "b.z",
     "__future__", "sys", "gc"],
    ["blahblah", "z"], [],
    """\
mymodule.py
a/__init__.py
a/module.py
                                kutoka __future__ agiza absolute_agiza
                                agiza sys # sys
                                agiza blahblah # fails
                                agiza gc # gc
                                agiza b.x # b.x
                                kutoka b agiza y # b.y
                                kutoka b.z agiza * # b.z.*
a/gc.py
a/sys.py
                                agiza mymodule
a/b/__init__.py
a/b/x.py
a/b/y.py
a/b/z.py
b/__init__.py
                                agiza z
b/unused.py
b/x.py
b/y.py
b/z.py
"""]

relative_import_test = [
    "a.module",
    ["__future__",
     "a", "a.module",
     "a.b", "a.b.y", "a.b.z",
     "a.b.c", "a.b.c.moduleC",
     "a.b.c.d", "a.b.c.e",
     "a.b.x",
     "gc"],
    [], [],
    """\
mymodule.py
a/__init__.py
                                kutoka .b agiza y, z # a.b.y, a.b.z
a/module.py
                                kutoka __future__ agiza absolute_agiza # __future__
                                agiza gc # gc
a/gc.py
a/sys.py
a/b/__init__.py
                                kutoka ..b agiza x # a.b.x
                                #kutoka a.b.c agiza moduleC
                                kutoka .c agiza moduleC # a.b.moduleC
a/b/x.py
a/b/y.py
a/b/z.py
a/b/g.py
a/b/c/__init__.py
                                kutoka ..c agiza e # a.b.c.e
a/b/c/moduleC.py
                                kutoka ..c agiza d # a.b.c.d
a/b/c/d.py
a/b/c/e.py
a/b/c/x.py
"""]

relative_import_test_2 = [
    "a.module",
    ["a", "a.module",
     "a.sys",
     "a.b", "a.b.y", "a.b.z",
     "a.b.c", "a.b.c.d",
     "a.b.c.e",
     "a.b.c.moduleC",
     "a.b.c.f",
     "a.b.x",
     "a.another"],
    [], [],
    """\
mymodule.py
a/__init__.py
                                kutoka . agiza sys # a.sys
a/another.py
a/module.py
                                kutoka .b agiza y, z # a.b.y, a.b.z
a/gc.py
a/sys.py
a/b/__init__.py
                                kutoka .c agiza moduleC # a.b.c.moduleC
                                kutoka .c agiza d # a.b.c.d
a/b/x.py
a/b/y.py
a/b/z.py
a/b/c/__init__.py
                                kutoka . agiza e # a.b.c.e
a/b/c/moduleC.py
                                #
                                kutoka . agiza f   # a.b.c.f
                                kutoka .. agiza x  # a.b.x
                                kutoka ... agiza another # a.another
a/b/c/d.py
a/b/c/e.py
a/b/c/f.py
"""]

relative_import_test_3 = [
    "a.module",
    ["a", "a.module"],
    ["a.bar"],
    [],
    """\
a/__init__.py
                                eleza foo(): pita
a/module.py
                                kutoka . agiza foo
                                kutoka . agiza bar
"""]

relative_import_test_4 = [
    "a.module",
    ["a", "a.module"],
    [],
    [],
    """\
a/__init__.py
                                eleza foo(): pita
a/module.py
                                kutoka . agiza *
"""]

bytecode_test = [
    "a",
    ["a"],
    [],
    [],
    ""
]

syntax_error_test = [
    "a.module",
    ["a", "a.module", "b"],
    ["b.module"], [],
    """\
a/__init__.py
a/module.py
                                agiza b.module
b/__init__.py
b/module.py
                                ?  # SyntaxError: invalid syntax
"""]


same_name_as_bad_test = [
    "a.module",
    ["a", "a.module", "b", "b.c"],
    ["c"], [],
    """\
a/__init__.py
a/module.py
                                agiza c
                                kutoka b agiza c
b/__init__.py
b/c.py
"""]


eleza open_file(path):
    dirname = os.path.dirname(path)
    jaribu:
        os.makedirs(dirname)
    tatizo OSError kama e:
        ikiwa e.errno != errno.EEXIST:
            ashiria
    rudisha open(path, "w")


eleza create_package(source):
    ofi = Tupu
    jaribu:
        kila line kwenye source.splitlines():
            ikiwa line.startswith(" ") ama line.startswith("\t"):
                ofi.write(line.strip() + "\n")
            isipokua:
                ikiwa ofi:
                    ofi.close()
                ofi = open_file(os.path.join(TEST_DIR, line.strip()))
    mwishowe:
        ikiwa ofi:
            ofi.close()


kundi ModuleFinderTest(unittest.TestCase):
    eleza _do_test(self, info, report=Uongo, debug=0, replace_paths=[]):
        import_this, modules, missing, maybe_missing, source = info
        create_package(source)
        jaribu:
            mf = modulefinder.ModuleFinder(path=TEST_PATH, debug=debug,
                                           replace_paths=replace_paths)
            mf.import_hook(import_this)
            ikiwa report:
                mf.report()
##                # This wouldn't work kwenye general when executed several times:
##                opath = sys.path[:]
##                sys.path = TEST_PATH
##                jaribu:
##                    __import__(import_this)
##                except:
##                    agiza traceback; traceback.print_exc()
##                sys.path = opath
##                rudisha
            modules = sorted(set(modules))
            found = sorted(mf.modules)
            # check ikiwa we found what we expected, sio more, sio less
            self.assertEqual(found, modules)

            # check kila missing na maybe missing modules
            bad, maybe = mf.any_missing_maybe()
            self.assertEqual(bad, missing)
            self.assertEqual(maybe, maybe_missing)
        mwishowe:
            shutil.rmtree(TEST_DIR)

    eleza test_package(self):
        self._do_test(package_test)

    eleza test_maybe(self):
        self._do_test(maybe_test)

    eleza test_maybe_new(self):
        self._do_test(maybe_test_new)

    eleza test_absolute_agizas(self):
        self._do_test(absolute_import_test)

    eleza test_relative_agizas(self):
        self._do_test(relative_import_test)

    eleza test_relative_agizas_2(self):
        self._do_test(relative_import_test_2)

    eleza test_relative_agizas_3(self):
        self._do_test(relative_import_test_3)

    eleza test_relative_agizas_4(self):
        self._do_test(relative_import_test_4)

    eleza test_syntax_error(self):
        self._do_test(syntax_error_test)

    eleza test_same_name_as_bad(self):
        self._do_test(same_name_as_bad_test)

    eleza test_bytecode(self):
        base_path = os.path.join(TEST_DIR, 'a')
        source_path = base_path + importlib.machinery.SOURCE_SUFFIXES[0]
        bytecode_path = base_path + importlib.machinery.BYTECODE_SUFFIXES[0]
        with open_file(source_path) kama file:
            file.write('testing_modulefinder = Kweli\n')
        py_compile.compile(source_path, cfile=bytecode_path)
        os.remove(source_path)
        self._do_test(bytecode_test)

    eleza test_replace_paths(self):
        old_path = os.path.join(TEST_DIR, 'a', 'module.py')
        new_path = os.path.join(TEST_DIR, 'a', 'spam.py')
        with support.captured_stdout() kama output:
            self._do_test(maybe_test, debug=2,
                          replace_paths=[(old_path, new_path)])
        output = output.getvalue()
        expected = "co_filename %r changed to %r" % (old_path, new_path)
        self.assertIn(expected, output)

    eleza test_extended_opargs(self):
        extended_opargs_test = [
            "a",
            ["a", "b"],
            [], [],
            """\
a.py
                                %r
                                agiza b
b.py
""" % list(range(2**16))]  # 2**16 constants
        self._do_test(extended_opargs_test)


ikiwa __name__ == "__main__":
    unittest.main()
