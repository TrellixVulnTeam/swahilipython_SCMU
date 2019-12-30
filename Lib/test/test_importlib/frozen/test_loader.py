kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

kutoka test.support agiza captured_stdout
agiza types
agiza unittest
agiza warnings


kundi ExecModuleTests(abc.LoaderTests):

    eleza exec_module(self, name):
        ukijumuisha util.uncache(name), captured_stdout() as stdout:
            spec = self.machinery.ModuleSpec(
                    name, self.machinery.FrozenImporter, origin='frozen',
                    is_package=self.machinery.FrozenImporter.is_package(name))
            module = types.ModuleType(name)
            module.__spec__ = spec
            assert sio hasattr(module, 'initialized')
            self.machinery.FrozenImporter.exec_module(module)
            self.assertKweli(module.initialized)
            self.assertKweli(hasattr(module, '__spec__'))
            self.assertEqual(module.__spec__.origin, 'frozen')
            rudisha module, stdout.getvalue()

    eleza test_module(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        check = {'__name__': name}
        kila attr, value kwenye check.items():
            self.assertEqual(getattr(module, attr), value)
        self.assertEqual(output, 'Hello world!\n')
        self.assertKweli(hasattr(module, '__spec__'))

    eleza test_package(self):
        name = '__phello__'
        module, output = self.exec_module(name)
        check = {'__name__': name}
        kila attr, value kwenye check.items():
            attr_value = getattr(module, attr)
            self.assertEqual(attr_value, value,
                        'kila {name}.{attr}, {given!r} != {expected!r}'.format(
                                 name=name, attr=attr, given=attr_value,
                                 expected=value))
        self.assertEqual(output, 'Hello world!\n')

    eleza test_lacking_parent(self):
        name = '__phello__.spam'
        ukijumuisha util.uncache('__phello__'):
            module, output = self.exec_module(name)
            check = {'__name__': name}
            kila attr, value kwenye check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                        'kila {name}.{attr}, {given} != {expected!r}'.format(
                                 name=name, attr=attr, given=attr_value,
                                 expected=value))
            self.assertEqual(output, 'Hello world!\n')

    eleza test_module_repr(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            repr_str = self.machinery.FrozenImporter.module_repr(module)
        self.assertEqual(repr_str,
                         "<module '__hello__' (frozen)>")

    eleza test_module_repr_indirect(self):
        name = '__hello__'
        module, output = self.exec_module(name)
        self.assertEqual(repr(module),
                         "<module '__hello__' (frozen)>")

    # No way to trigger an error kwenye a frozen module.
    test_state_after_failure = Tupu

    eleza test_unloadable(self):
        assert self.machinery.FrozenImporter.find_module('_not_real') ni Tupu
        ukijumuisha self.assertRaises(ImportError) as cm:
            self.exec_module('_not_real')
        self.assertEqual(cm.exception.name, '_not_real')


(Frozen_ExecModuleTests,
 Source_ExecModuleTests
 ) = util.test_both(ExecModuleTests, machinery=machinery)


kundi LoaderTests(abc.LoaderTests):

    eleza test_module(self):
        ukijumuisha util.uncache('__hello__'), captured_stdout() as stdout:
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__hello__')
            check = {'__name__': '__hello__',
                    '__package__': '',
                    '__loader__': self.machinery.FrozenImporter,
                    }
            kila attr, value kwenye check.items():
                self.assertEqual(getattr(module, attr), value)
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertUongo(hasattr(module, '__file__'))

    eleza test_package(self):
        ukijumuisha util.uncache('__phello__'),  captured_stdout() as stdout:
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__phello__')
            check = {'__name__': '__phello__',
                     '__package__': '__phello__',
                     '__path__': [],
                     '__loader__': self.machinery.FrozenImporter,
                     }
            kila attr, value kwenye check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                                 "kila __phello__.%s, %r != %r" %
                                 (attr, attr_value, value))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertUongo(hasattr(module, '__file__'))

    eleza test_lacking_parent(self):
        ukijumuisha util.uncache('__phello__', '__phello__.spam'), \
             captured_stdout() as stdout:
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__phello__.spam')
            check = {'__name__': '__phello__.spam',
                    '__package__': '__phello__',
                    '__loader__': self.machinery.FrozenImporter,
                    }
            kila attr, value kwenye check.items():
                attr_value = getattr(module, attr)
                self.assertEqual(attr_value, value,
                                 "kila __phello__.spam.%s, %r != %r" %
                                 (attr, attr_value, value))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')
            self.assertUongo(hasattr(module, '__file__'))

    eleza test_module_reuse(self):
        ukijumuisha util.uncache('__hello__'), captured_stdout() as stdout:
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module1 = self.machinery.FrozenImporter.load_module('__hello__')
                module2 = self.machinery.FrozenImporter.load_module('__hello__')
            self.assertIs(module1, module2)
            self.assertEqual(stdout.getvalue(),
                             'Hello world!\nHello world!\n')

    eleza test_module_repr(self):
        ukijumuisha util.uncache('__hello__'), captured_stdout():
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = self.machinery.FrozenImporter.load_module('__hello__')
                repr_str = self.machinery.FrozenImporter.module_repr(module)
            self.assertEqual(repr_str,
                             "<module '__hello__' (frozen)>")

    eleza test_module_repr_indirect(self):
        ukijumuisha util.uncache('__hello__'), captured_stdout():
            module = self.machinery.FrozenImporter.load_module('__hello__')
        self.assertEqual(repr(module),
                         "<module '__hello__' (frozen)>")

    # No way to trigger an error kwenye a frozen module.
    test_state_after_failure = Tupu

    eleza test_unloadable(self):
        assert self.machinery.FrozenImporter.find_module('_not_real') ni Tupu
        ukijumuisha self.assertRaises(ImportError) as cm:
            self.machinery.FrozenImporter.load_module('_not_real')
        self.assertEqual(cm.exception.name, '_not_real')


(Frozen_LoaderTests,
 Source_LoaderTests
 ) = util.test_both(LoaderTests, machinery=machinery)


kundi InspectLoaderTests:

    """Tests kila the InspectLoader methods kila FrozenImporter."""

    eleza test_get_code(self):
        # Make sure that the code object ni good.
        name = '__hello__'
        ukijumuisha captured_stdout() as stdout:
            code = self.machinery.FrozenImporter.get_code(name)
            mod = types.ModuleType(name)
            exec(code, mod.__dict__)
            self.assertKweli(hasattr(mod, 'initialized'))
            self.assertEqual(stdout.getvalue(), 'Hello world!\n')

    eleza test_get_source(self):
        # Should always rudisha Tupu.
        result = self.machinery.FrozenImporter.get_source('__hello__')
        self.assertIsTupu(result)

    eleza test_is_package(self):
        # Should be able to tell what ni a package.
        test_kila = (('__hello__', Uongo), ('__phello__', Kweli),
                    ('__phello__.spam', Uongo))
        kila name, is_package kwenye test_for:
            result = self.machinery.FrozenImporter.is_package(name)
            self.assertEqual(bool(result), is_package)

    eleza test_failure(self):
        # Raise ImportError kila modules that are sio frozen.
        kila meth_name kwenye ('get_code', 'get_source', 'is_package'):
            method = getattr(self.machinery.FrozenImporter, meth_name)
            ukijumuisha self.assertRaises(ImportError) as cm:
                method('importlib')
            self.assertEqual(cm.exception.name, 'importlib')

(Frozen_ILTests,
 Source_ILTests
 ) = util.test_both(InspectLoaderTests, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
