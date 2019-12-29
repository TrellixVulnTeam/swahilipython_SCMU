agiza importlib
agiza importlib.util
agiza os
agiza os.path
agiza py_compile
agiza sys
kutoka test agiza support
kutoka test.support agiza script_helper
agiza unittest
agiza warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    agiza imp
agiza _imp


eleza requires_load_dynamic(meth):
    """Decorator to skip a test ikiwa sio running under CPython ama lacking
    imp.load_dynamic()."""
    meth = support.cpython_only(meth)
    rudisha unittest.skipIf(not hasattr(imp, 'load_dynamic'),
                           'imp.load_dynamic() required')(meth)


kundi LockTests(unittest.TestCase):

    """Very basic test of agiza lock functions."""

    eleza verify_lock_state(self, expected):
        self.assertEqual(imp.lock_held(), expected,
                             "expected imp.lock_held() to be %r" % expected)
    eleza testLock(self):
        LOOPS = 50

        # The agiza lock may already be held, e.g. ikiwa the test suite ni run
        # via "agiza test.autotest".
        lock_held_at_start = imp.lock_held()
        self.verify_lock_state(lock_held_at_start)

        kila i kwenye range(LOOPS):
            imp.acquire_lock()
            self.verify_lock_state(Kweli)

        kila i kwenye range(LOOPS):
            imp.release_lock()

        # The original state should be restored now.
        self.verify_lock_state(lock_held_at_start)

        ikiwa sio lock_held_at_start:
            jaribu:
                imp.release_lock()
            tatizo RuntimeError:
                pita
            isipokua:
                self.fail("release_lock() without lock should ashiria "
                            "RuntimeError")

kundi ImportTests(unittest.TestCase):
    eleza setUp(self):
        mod = importlib.import_module('test.encoded_modules')
        self.test_strings = mod.test_strings
        self.test_path = mod.__path__

    eleza test_import_encoded_module(self):
        kila modname, encoding, teststr kwenye self.test_strings:
            mod = importlib.import_module('test.encoded_modules.'
                                          'module_' + modname)
            self.assertEqual(teststr, mod.test)

    eleza test_find_module_encoding(self):
        kila mod, encoding, _ kwenye self.test_strings:
            with imp.find_module('module_' + mod, self.test_path)[0] kama fd:
                self.assertEqual(fd.encoding, encoding)

        path = [os.path.dirname(__file__)]
        with self.assertRaises(SyntaxError):
            imp.find_module('badsyntax_pep3120', path)

    eleza test_issue1267(self):
        kila mod, encoding, _ kwenye self.test_strings:
            fp, filename, info  = imp.find_module('module_' + mod,
                                                  self.test_path)
            with fp:
                self.assertNotEqual(fp, Tupu)
                self.assertEqual(fp.encoding, encoding)
                self.assertEqual(fp.tell(), 0)
                self.assertEqual(fp.readline(), '# test %s encoding\n'
                                 % encoding)

        fp, filename, info = imp.find_module("tokenize")
        with fp:
            self.assertNotEqual(fp, Tupu)
            self.assertEqual(fp.encoding, "utf-8")
            self.assertEqual(fp.tell(), 0)
            self.assertEqual(fp.readline(),
                             '"""Tokenization help kila Python programs.\n')

    eleza test_issue3594(self):
        temp_mod_name = 'test_imp_helper'
        sys.path.insert(0, '.')
        jaribu:
            with open(temp_mod_name + '.py', 'w') kama file:
                file.write("# coding: cp1252\nu = 'test.test_imp'\n")
            file, filename, info = imp.find_module(temp_mod_name)
            file.close()
            self.assertEqual(file.encoding, 'cp1252')
        mwishowe:
            toa sys.path[0]
            support.unlink(temp_mod_name + '.py')
            support.unlink(temp_mod_name + '.pyc')

    eleza test_issue5604(self):
        # Test cannot cover imp.load_compiled function.
        # Martin von Loewis note what shared library cannot have non-ascii
        # character because init_xxx function cannot be compiled
        # na issue never happens kila dynamic modules.
        # But sources modified to follow generic way kila processing paths.

        # the rudisha encoding could be uppercase ama Tupu
        fs_encoding = sys.getfilesystemencoding()

        # covers utf-8 na Windows ANSI code pages
        # one non-space symbol kutoka every page
        # (http://en.wikipedia.org/wiki/Code_page)
        known_locales = {
            'utf-8' : b'\xc3\xa4',
            'cp1250' : b'\x8C',
            'cp1251' : b'\xc0',
            'cp1252' : b'\xc0',
            'cp1253' : b'\xc1',
            'cp1254' : b'\xc0',
            'cp1255' : b'\xe0',
            'cp1256' : b'\xe0',
            'cp1257' : b'\xc0',
            'cp1258' : b'\xc0',
            }

        ikiwa sys.platform == 'darwin':
            self.assertEqual(fs_encoding, 'utf-8')
            # Mac OS X uses the Normal Form D decomposition
            # http://developer.apple.com/mac/library/qa/qa2001/qa1173.html
            special_char = b'a\xcc\x88'
        isipokua:
            special_char = known_locales.get(fs_encoding)

        ikiwa sio special_char:
            self.skipTest("can't run this test with %s kama filesystem encoding"
                          % fs_encoding)
        decoded_char = special_char.decode(fs_encoding)
        temp_mod_name = 'test_imp_helper_' + decoded_char
        test_package_name = 'test_imp_helper_package_' + decoded_char
        init_file_name = os.path.join(test_package_name, '__init__.py')
        jaribu:
            # ikiwa the curdir ni haiko kwenye sys.path the test fails when run with
            # ./python ./Lib/test/regrtest.py test_imp
            sys.path.insert(0, os.curdir)
            with open(temp_mod_name + '.py', 'w') kama file:
                file.write('a = 1\n')
            file, filename, info = imp.find_module(temp_mod_name)
            with file:
                self.assertIsNotTupu(file)
                self.assertKweli(filename[:-3].endswith(temp_mod_name))
                self.assertEqual(info[0], '.py')
                self.assertEqual(info[1], 'r')
                self.assertEqual(info[2], imp.PY_SOURCE)

                mod = imp.load_module(temp_mod_name, file, filename, info)
                self.assertEqual(mod.a, 1)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                mod = imp.load_source(temp_mod_name, temp_mod_name + '.py')
            self.assertEqual(mod.a, 1)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                ikiwa sio sys.dont_write_bytecode:
                    mod = imp.load_compiled(
                        temp_mod_name,
                        imp.cache_kutoka_source(temp_mod_name + '.py'))
            self.assertEqual(mod.a, 1)

            ikiwa sio os.path.exists(test_package_name):
                os.mkdir(test_package_name)
            with open(init_file_name, 'w') kama file:
                file.write('b = 2\n')
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                package = imp.load_package(test_package_name, test_package_name)
            self.assertEqual(package.b, 2)
        mwishowe:
            toa sys.path[0]
            kila ext kwenye ('.py', '.pyc'):
                support.unlink(temp_mod_name + ext)
                support.unlink(init_file_name + ext)
            support.rmtree(test_package_name)
            support.rmtree('__pycache__')

    eleza test_issue9319(self):
        path = os.path.dirname(__file__)
        self.assertRaises(SyntaxError,
                          imp.find_module, "badsyntax_pep3120", [path])

    eleza test_load_kutoka_source(self):
        # Verify that the imp module can correctly load na find .py files
        # XXX (ncoghlan): It would be nice to use support.CleanImport
        # here, but that komas because the os module registers some
        # handlers kwenye copy_reg on agiza. Since CleanImport doesn't
        # revert that registration, the module ni left kwenye a broken
        # state after reversion. Reinitialising the module contents
        # na just reverting os.environ to its previous state ni an OK
        # workaround
        orig_path = os.path
        orig_getenv = os.getenv
        with support.EnvironmentVarGuard():
            x = imp.find_module("os")
            self.addCleanup(x[0].close)
            new_os = imp.load_module("os", *x)
            self.assertIs(os, new_os)
            self.assertIs(orig_path, new_os.path)
            self.assertIsNot(orig_getenv, new_os.getenv)

    @requires_load_dynamic
    eleza test_issue15828_load_extensions(self):
        # Issue 15828 picked up that the adapter between the old imp API
        # na importlib couldn't handle C extensions
        example = "_heapq"
        x = imp.find_module(example)
        file_ = x[0]
        ikiwa file_ ni sio Tupu:
            self.addCleanup(file_.close)
        mod = imp.load_module(example, *x)
        self.assertEqual(mod.__name__, example)

    @requires_load_dynamic
    eleza test_issue16421_multiple_modules_in_one_dll(self):
        # Issue 16421: loading several modules kutoka the same compiled file fails
        m = '_testagizamultiple'
        fileobj, pathname, description = imp.find_module(m)
        fileobj.close()
        mod0 = imp.load_dynamic(m, pathname)
        mod1 = imp.load_dynamic('_testagizamultiple_foo', pathname)
        mod2 = imp.load_dynamic('_testagizamultiple_bar', pathname)
        self.assertEqual(mod0.__name__, m)
        self.assertEqual(mod1.__name__, '_testagizamultiple_foo')
        self.assertEqual(mod2.__name__, '_testagizamultiple_bar')
        with self.assertRaises(ImportError):
            imp.load_dynamic('nonexistent', pathname)

    @requires_load_dynamic
    eleza test_load_dynamic_ImportError_path(self):
        # Issue #1559549 added `name` na `path` attributes to ImportError
        # kwenye order to provide better detail. Issue #10854 implemented those
        # attributes on agiza failures of extensions on Windows.
        path = 'bogus file path'
        name = 'extension'
        with self.assertRaises(ImportError) kama err:
            imp.load_dynamic(name, path)
        self.assertIn(path, err.exception.path)
        self.assertEqual(name, err.exception.name)

    @requires_load_dynamic
    eleza test_load_module_extension_file_is_Tupu(self):
        # When loading an extension module na the file ni Tupu, open one
        # on the behalf of imp.load_dynamic().
        # Issue #15902
        name = '_testagizamultiple'
        found = imp.find_module(name)
        ikiwa found[0] ni sio Tupu:
            found[0].close()
        ikiwa found[2][2] != imp.C_EXTENSION:
            self.skipTest("found module doesn't appear to be a C extension")
        imp.load_module(name, Tupu, *found[1:])

    @requires_load_dynamic
    eleza test_issue24748_load_module_skips_sys_modules_check(self):
        name = 'test.imp_dummy'
        jaribu:
            toa sys.modules[name]
        tatizo KeyError:
            pita
        jaribu:
            module = importlib.import_module(name)
            spec = importlib.util.find_spec('_testmultiphase')
            module = imp.load_dynamic(name, spec.origin)
            self.assertEqual(module.__name__, name)
            self.assertEqual(module.__spec__.name, name)
            self.assertEqual(module.__spec__.origin, spec.origin)
            self.assertRaises(AttributeError, getattr, module, 'dummy_name')
            self.assertEqual(module.int_const, 1969)
            self.assertIs(sys.modules[name], module)
        mwishowe:
            jaribu:
                toa sys.modules[name]
            tatizo KeyError:
                pita

    @unittest.skipIf(sys.dont_write_bytecode,
        "test meaningful only when writing bytecode")
    eleza test_bug7732(self):
        with support.temp_cwd():
            source = support.TESTFN + '.py'
            os.mkdir(source)
            self.assertRaisesRegex(ImportError, '^No module',
                imp.find_module, support.TESTFN, ["."])

    eleza test_multiple_calls_to_get_data(self):
        # Issue #18755: make sure multiple calls to get_data() can succeed.
        loader = imp._LoadSourceCompatibility('imp', imp.__file__,
                                              open(imp.__file__))
        loader.get_data(imp.__file__)  # File should be closed
        loader.get_data(imp.__file__)  # Will need to create a newly opened file

    eleza test_load_source(self):
        # Create a temporary module since load_source(name) modifies
        # sys.modules[name] attributes like __loader___
        modname = f"tmp{__name__}"
        mod = type(sys.modules[__name__])(modname)
        with support.swap_item(sys.modules, modname, mod):
            with self.assertRaisesRegex(ValueError, 'embedded null'):
                imp.load_source(modname, __file__ + "\0")

    @support.cpython_only
    eleza test_issue31315(self):
        # There shouldn't be an assertion failure kwenye imp.create_dynamic(),
        # when spec.name ni sio a string.
        create_dynamic = support.get_attribute(imp, 'create_dynamic')
        kundi BadSpec:
            name = Tupu
            origin = 'foo'
        with self.assertRaises(TypeError):
            create_dynamic(BadSpec())

    eleza test_issue_35321(self):
        # Both _frozen_importlib na _frozen_importlib_external
        # should have a spec origin of "frozen" and
        # no need to clean up agizas kwenye this case.

        agiza _frozen_importlib_external
        self.assertEqual(_frozen_importlib_external.__spec__.origin, "frozen")

        agiza _frozen_importlib
        self.assertEqual(_frozen_importlib.__spec__.origin, "frozen")

    eleza test_source_hash(self):
        self.assertEqual(_imp.source_hash(42, b'hi'), b'\xc6\xe7Z\r\x03:}\xab')
        self.assertEqual(_imp.source_hash(43, b'hi'), b'\x85\x9765\xf8\x9a\x8b9')

    eleza test_pyc_invalidation_mode_kutoka_cmdline(self):
        cases = [
            ([], "default"),
            (["--check-hash-based-pycs", "default"], "default"),
            (["--check-hash-based-pycs", "always"], "always"),
            (["--check-hash-based-pycs", "never"], "never"),
        ]
        kila interp_args, expected kwenye cases:
            args = interp_args + [
                "-c",
                "agiza _imp; andika(_imp.check_hash_based_pycs)",
            ]
            res = script_helper.assert_python_ok(*args)
            self.assertEqual(res.out.strip().decode('utf-8'), expected)

    eleza test_find_and_load_checked_pyc(self):
        # issue 34056
        with support.temp_cwd():
            with open('mymod.py', 'wb') kama fp:
                fp.write(b'x = 42\n')
            py_compile.compile(
                'mymod.py',
                doashiria=Kweli,
                invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
            )
            file, path, description = imp.find_module('mymod', path=['.'])
            mod = imp.load_module('mymod', file, path, description)
        self.assertEqual(mod.x, 42)


kundi ReloadTests(unittest.TestCase):

    """Very basic tests to make sure that imp.reload() operates just like
    reload()."""

    eleza test_source(self):
        # XXX (ncoghlan): It would be nice to use test.support.CleanImport
        # here, but that komas because the os module registers some
        # handlers kwenye copy_reg on agiza. Since CleanImport doesn't
        # revert that registration, the module ni left kwenye a broken
        # state after reversion. Reinitialising the module contents
        # na just reverting os.environ to its previous state ni an OK
        # workaround
        with support.EnvironmentVarGuard():
            agiza os
            imp.reload(os)

    eleza test_extension(self):
        with support.CleanImport('time'):
            agiza time
            imp.reload(time)

    eleza test_builtin(self):
        with support.CleanImport('marshal'):
            agiza marshal
            imp.reload(marshal)

    eleza test_with_deleted_parent(self):
        # see #18681
        kutoka html agiza parser
        html = sys.modules.pop('html')
        eleza cleanup():
            sys.modules['html'] = html
        self.addCleanup(cleanup)
        with self.assertRaisesRegex(ImportError, 'html'):
            imp.reload(parser)


kundi PEP3147Tests(unittest.TestCase):
    """Tests of PEP 3147."""

    tag = imp.get_tag()

    @unittest.skipUnless(sys.implementation.cache_tag ni sio Tupu,
                         'requires sys.implementation.cache_tag sio be Tupu')
    eleza test_cache_kutoka_source(self):
        # Given the path to a .py file, rudisha the path to its PEP 3147
        # defined .pyc file (i.e. under __pycache__).
        path = os.path.join('foo', 'bar', 'baz', 'qux.py')
        expect = os.path.join('foo', 'bar', 'baz', '__pycache__',
                              'qux.{}.pyc'.format(self.tag))
        self.assertEqual(imp.cache_kutoka_source(path, Kweli), expect)

    @unittest.skipUnless(sys.implementation.cache_tag ni sio Tupu,
                         'requires sys.implementation.cache_tag to sio be '
                         'Tupu')
    eleza test_source_kutoka_cache(self):
        # Given the path to a PEP 3147 defined .pyc file, rudisha the path to
        # its source.  This tests the good path.
        path = os.path.join('foo', 'bar', 'baz', '__pycache__',
                            'qux.{}.pyc'.format(self.tag))
        expect = os.path.join('foo', 'bar', 'baz', 'qux.py')
        self.assertEqual(imp.source_kutoka_cache(path), expect)


kundi NullImporterTests(unittest.TestCase):
    @unittest.skipIf(support.TESTFN_UNENCODABLE ni Tupu,
                     "Need an undecodeable filename")
    eleza test_unencodeable(self):
        name = support.TESTFN_UNENCODABLE
        os.mkdir(name)
        jaribu:
            self.assertRaises(ImportError, imp.NullImporter, name)
        mwishowe:
            os.rmdir(name)


ikiwa __name__ == "__main__":
    unittest.main()
