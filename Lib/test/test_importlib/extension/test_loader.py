kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza os.path
agiza sys
agiza types
agiza unittest
agiza importlib.util
agiza importlib
kutoka test.support.script_helper agiza assert_python_failure

kundi LoaderTests(abc.LoaderTests):

    """Test load_module() kila extension modules."""

    eleza setUp(self):
        self.loader = self.machinery.ExtensionFileLoader(util.EXTENSIONS.name,
                                                         util.EXTENSIONS.file_path)

    eleza load_module(self, fullname):
        rudisha self.loader.load_module(fullname)

    eleza test_load_module_API(self):
        # Test the default argument kila load_module().
        self.loader.load_module()
        self.loader.load_module(Tupu)
        ukijumuisha self.assertRaises(ImportError):
            self.load_module('XXX')

    eleza test_equality(self):
        other = self.machinery.ExtensionFileLoader(util.EXTENSIONS.name,
                                                   util.EXTENSIONS.file_path)
        self.assertEqual(self.loader, other)

    eleza test_inequality(self):
        other = self.machinery.ExtensionFileLoader('_' + util.EXTENSIONS.name,
                                                   util.EXTENSIONS.file_path)
        self.assertNotEqual(self.loader, other)

    eleza test_module(self):
        ukijumuisha util.uncache(util.EXTENSIONS.name):
            module = self.load_module(util.EXTENSIONS.name)
            kila attr, value kwenye [('__name__', util.EXTENSIONS.name),
                                ('__file__', util.EXTENSIONS.file_path),
                                ('__package__', '')]:
                self.assertEqual(getattr(module, attr), value)
            self.assertIn(util.EXTENSIONS.name, sys.modules)
            self.assertIsInstance(module.__loader__,
                                  self.machinery.ExtensionFileLoader)

    # No extension module kama __init__ available kila testing.
    test_package = Tupu

    # No extension module kwenye a package available kila testing.
    test_lacking_parent = Tupu

    eleza test_module_reuse(self):
        ukijumuisha util.uncache(util.EXTENSIONS.name):
            module1 = self.load_module(util.EXTENSIONS.name)
            module2 = self.load_module(util.EXTENSIONS.name)
            self.assertIs(module1, module2)

    # No easy way to trigger a failure after a successful agiza.
    test_state_after_failure = Tupu

    eleza test_unloadable(self):
        name = 'asdfjkl;'
        ukijumuisha self.assertRaises(ImportError) kama cm:
            self.load_module(name)
        self.assertEqual(cm.exception.name, name)

    eleza test_is_package(self):
        self.assertUongo(self.loader.is_package(util.EXTENSIONS.name))
        kila suffix kwenye self.machinery.EXTENSION_SUFFIXES:
            path = os.path.join('some', 'path', 'pkg', '__init__' + suffix)
            loader = self.machinery.ExtensionFileLoader('pkg', path)
            self.assertKweli(loader.is_package('pkg'))

(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)

kundi MultiPhaseExtensionModuleTests(abc.LoaderTests):
    """Test loading extension modules ukijumuisha multi-phase initialization (PEP 489)
    """

    eleza setUp(self):
        self.name = '_testmultiphase'
        finder = self.machinery.FileFinder(Tupu)
        self.spec = importlib.util.find_spec(self.name)
        assert self.spec
        self.loader = self.machinery.ExtensionFileLoader(
            self.name, self.spec.origin)

    # No extension module kama __init__ available kila testing.
    test_package = Tupu

    # No extension module kwenye a package available kila testing.
    test_lacking_parent = Tupu

    # Handling failure on reload ni the up to the module.
    test_state_after_failure = Tupu

    eleza test_module(self):
        '''Test loading an extension module'''
        ukijumuisha util.uncache(self.name):
            module = self.load_module()
            kila attr, value kwenye [('__name__', self.name),
                                ('__file__', self.spec.origin),
                                ('__package__', '')]:
                self.assertEqual(getattr(module, attr), value)
            ukijumuisha self.assertRaises(AttributeError):
                module.__path__
            self.assertIs(module, sys.modules[self.name])
            self.assertIsInstance(module.__loader__,
                                  self.machinery.ExtensionFileLoader)

    eleza test_functionality(self):
        '''Test basic functionality of stuff defined kwenye an extension module'''
        ukijumuisha util.uncache(self.name):
            module = self.load_module()
            self.assertIsInstance(module, types.ModuleType)
            ex = module.Example()
            self.assertEqual(ex.demo('abcd'), 'abcd')
            self.assertEqual(ex.demo(), Tupu)
            ukijumuisha self.assertRaises(AttributeError):
                ex.abc
            ex.abc = 0
            self.assertEqual(ex.abc, 0)
            self.assertEqual(module.foo(9, 9), 18)
            self.assertIsInstance(module.Str(), str)
            self.assertEqual(module.Str(1) + '23', '123')
            ukijumuisha self.assertRaises(module.error):
                ashiria module.error()
            self.assertEqual(module.int_const, 1969)
            self.assertEqual(module.str_const, 'something different')

    eleza test_reload(self):
        '''Test that reload didn't re-set the module's attributes'''
        ukijumuisha util.uncache(self.name):
            module = self.load_module()
            ex_kundi = module.Example
            importlib.reload(module)
            self.assertIs(ex_class, module.Example)

    eleza test_try_registration(self):
        '''Assert that the PyState_{Find,Add,Remove}Module C API doesn't work'''
        module = self.load_module()
        ukijumuisha self.subTest('PyState_FindModule'):
            self.assertEqual(module.call_state_registration_func(0), Tupu)
        ukijumuisha self.subTest('PyState_AddModule'):
            ukijumuisha self.assertRaises(SystemError):
                module.call_state_registration_func(1)
        ukijumuisha self.subTest('PyState_RemoveModule'):
            ukijumuisha self.assertRaises(SystemError):
                module.call_state_registration_func(2)

    eleza load_module(self):
        '''Load the module kutoka the test extension'''
        rudisha self.loader.load_module(self.name)

    eleza load_module_by_name(self, fullname):
        '''Load a module kutoka the test extension by name'''
        origin = self.spec.origin
        loader = self.machinery.ExtensionFileLoader(fullname, origin)
        spec = importlib.util.spec_from_loader(fullname, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        rudisha module

    eleza test_load_submodule(self):
        '''Test loading a simulated submodule'''
        module = self.load_module_by_name('pkg.' + self.name)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, 'pkg.' + self.name)
        self.assertEqual(module.str_const, 'something different')

    eleza test_load_short_name(self):
        '''Test loading module ukijumuisha a one-character name'''
        module = self.load_module_by_name('x')
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, 'x')
        self.assertEqual(module.str_const, 'something different')
        self.assertNotIn('x', sys.modules)

    eleza test_load_twice(self):
        '''Test that 2 loads result kwenye 2 module objects'''
        module1 = self.load_module_by_name(self.name)
        module2 = self.load_module_by_name(self.name)
        self.assertIsNot(module1, module2)

    eleza test_unloadable(self):
        '''Test nonexistent module'''
        name = 'asdfjkl;'
        ukijumuisha self.assertRaises(ImportError) kama cm:
            self.load_module_by_name(name)
        self.assertEqual(cm.exception.name, name)

    eleza test_unloadable_nonascii(self):
        '''Test behavior ukijumuisha nonexistent module ukijumuisha non-ASCII name'''
        name = 'fo\xf3'
        ukijumuisha self.assertRaises(ImportError) kama cm:
            self.load_module_by_name(name)
        self.assertEqual(cm.exception.name, name)

    eleza test_nonmodule(self):
        '''Test rudishaing a non-module object kutoka create works'''
        name = self.name + '_nonmodule'
        mod = self.load_module_by_name(name)
        self.assertNotEqual(type(mod), type(unittest))
        self.assertEqual(mod.three, 3)

    # issue 27782
    eleza test_nonmodule_with_methods(self):
        '''Test creating a non-module object ukijumuisha methods defined'''
        name = self.name + '_nonmodule_with_methods'
        mod = self.load_module_by_name(name)
        self.assertNotEqual(type(mod), type(unittest))
        self.assertEqual(mod.three, 3)
        self.assertEqual(mod.bar(10, 1), 9)

    eleza test_null_slots(self):
        '''Test that NULL slots aren't a problem'''
        name = self.name + '_null_slots'
        module = self.load_module_by_name(name)
        self.assertIsInstance(module, types.ModuleType)
        self.assertEqual(module.__name__, name)

    eleza test_bad_modules(self):
        '''Test SystemError ni ashiriad kila misbehaving extensions'''
        kila name_base kwenye [
                'bad_slot_large',
                'bad_slot_negative',
                'create_int_with_state',
                'negative_size',
                'export_null',
                'export_uninitialized',
                'export_ashiria',
                'export_unreported_exception',
                'create_null',
                'create_ashiria',
                'create_unreported_exception',
                'nonmodule_with_exec_slots',
                'exec_err',
                'exec_ashiria',
                'exec_unreported_exception',
                ]:
            ukijumuisha self.subTest(name_base):
                name = self.name + '_' + name_base
                ukijumuisha self.assertRaises(SystemError):
                    self.load_module_by_name(name)

    eleza test_nonascii(self):
        '''Test that modules ukijumuisha non-ASCII names can be loaded'''
        # punycode behaves slightly differently kwenye some-ASCII na no-ASCII
        # cases, so test both
        cases = [
            (self.name + '_zkou\u0161ka_na\u010dten\xed', 'Czech'),
            ('\uff3f\u30a4\u30f3\u30dd\u30fc\u30c8\u30c6\u30b9\u30c8',
             'Japanese'),
            ]
        kila name, lang kwenye cases:
            ukijumuisha self.subTest(name):
                module = self.load_module_by_name(name)
                self.assertEqual(module.__name__, name)
                self.assertEqual(module.__doc__, "Module named kwenye %s" % lang)

    @unittest.skipIf(sio hasattr(sys, 'gettotalrefcount'),
            '--with-pydebug has to be enabled kila this test')
    eleza test_bad_traverse(self):
        ''' Issue #32374: Test that traverse fails when accessing per-module
            state before Py_mod_exec was executed.
            (Multiphase initialization modules only)
        '''
        script = """ikiwa Kweli:
                jaribu:
                    kutoka test agiza support
                    agiza importlib.util kama util
                    spec = util.find_spec('_testmultiphase')
                    spec.name = '_testmultiphase_with_bad_traverse'

                    ukijumuisha support.SuppressCrashReport():
                        m = spec.loader.create_module(spec)
                tatizo:
                    # Prevent Python-level exceptions kutoka
                    # ending the process ukijumuisha non-zero status
                    # (We are testing kila a crash kwenye C-code)
                    pita"""
        assert_python_failure("-c", script)


(Frozen_MultiPhaseExtensionModuleTests,
 Source_MultiPhaseExtensionModuleTests
 ) = util.test_both(MultiPhaseExtensionModuleTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
