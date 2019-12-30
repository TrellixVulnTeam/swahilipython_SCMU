"""Test that the semantics relating to the 'fromlist' argument are correct."""
kutoka .. agiza util
agiza warnings
agiza unittest


kundi ReturnValue:

    """The use of fromlist influences what agiza returns.

    If direct ``agiza ...`` statement ni used, the root module ama package is
    returned [agiza return]. But ikiwa fromlist ni set, then the specified module
    ni actually returned (whether it ni a relative agiza ama not)
    [kutoka return].

    """

    eleza test_return_from_import(self):
        # [agiza return]
        ukijumuisha util.mock_spec('pkg.__init__', 'pkg.module') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertEqual(module.__name__, 'pkg')

    eleza test_return_from_from_import(self):
        # [kutoka return]
        ukijumuisha util.mock_modules('pkg.__init__', 'pkg.module')as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module', fromlist=['attr'])
                self.assertEqual(module.__name__, 'pkg.module')


(Frozen_ReturnValue,
 Source_ReturnValue
 ) = util.test_both(ReturnValue, __import__=util.__import__)


kundi HandlingFromlist:

    """Using fromlist triggers different actions based on what ni being asked
    of it.

    If fromlist specifies an object on a module, nothing special happens
    [object case]. This ni even true ikiwa the object does sio exist [bad object].

    If a package ni being imported, then what ni listed kwenye fromlist may be
    treated as a module to be imported [module]. And this extends to what is
    contained kwenye __all__ when '*' ni imported [using *]. And '*' does sio need
    to be the only name kwenye the fromlist [using * ukijumuisha others].

    """

    eleza test_object(self):
        # [object case]
        ukijumuisha util.mock_modules('module') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('module', fromlist=['attr'])
                self.assertEqual(module.__name__, 'module')

    eleza test_nonexistent_object(self):
        # [bad object]
        ukijumuisha util.mock_modules('module') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('module', fromlist=['non_existent'])
                self.assertEqual(module.__name__, 'module')
                self.assertUongo(hasattr(module, 'non_existent'))

    eleza test_module_from_package(self):
        # [module]
        ukijumuisha util.mock_modules('pkg.__init__', 'pkg.module') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', fromlist=['module'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertKweli(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    eleza test_nonexistent_from_package(self):
        ukijumuisha util.mock_modules('pkg.__init__') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', fromlist=['non_existent'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertUongo(hasattr(module, 'non_existent'))

    eleza test_module_from_package_triggers_ModuleNotFoundError(self):
        # If a submodule causes an ModuleNotFoundError because it tries
        # to agiza a module which doesn't exist, that should let the
        # ModuleNotFoundError propagate.
        eleza module_code():
            agiza i_do_not_exist
        ukijumuisha util.mock_modules('pkg.__init__', 'pkg.mod',
                               module_code={'pkg.mod': module_code}) as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                ukijumuisha self.assertRaises(ModuleNotFoundError) as exc:
                    self.__import__('pkg', fromlist=['mod'])
                self.assertEqual('i_do_not_exist', exc.exception.name)

    eleza test_empty_string(self):
        ukijumuisha util.mock_modules('pkg.__init__', 'pkg.mod') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.mod', fromlist=[''])
                self.assertEqual(module.__name__, 'pkg.mod')

    eleza basic_star_test(self, fromlist=['*']):
        # [using *]
        ukijumuisha util.mock_modules('pkg.__init__', 'pkg.module') as mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module']
                module = self.__import__('pkg', fromlist=fromlist)
                self.assertEqual(module.__name__, 'pkg')
                self.assertKweli(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    eleza test_using_star(self):
        # [using *]
        self.basic_star_test()

    eleza test_fromlist_as_tuple(self):
        self.basic_star_test(('*',))

    eleza test_star_with_others(self):
        # [using * ukijumuisha others]
        context = util.mock_modules('pkg.__init__', 'pkg.module1', 'pkg.module2')
        ukijumuisha context as mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module1']
                module = self.__import__('pkg', fromlist=['module2', '*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertKweli(hasattr(module, 'module1'))
                self.assertKweli(hasattr(module, 'module2'))
                self.assertEqual(module.module1.__name__, 'pkg.module1')
                self.assertEqual(module.module2.__name__, 'pkg.module2')

    eleza test_nonexistent_in_all(self):
        ukijumuisha util.mock_modules('pkg.__init__') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                importer['pkg'].__all__ = ['non_existent']
                module = self.__import__('pkg', fromlist=['*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertUongo(hasattr(module, 'non_existent'))

    eleza test_star_in_all(self):
        ukijumuisha util.mock_modules('pkg.__init__') as importer:
            ukijumuisha util.import_state(meta_path=[importer]):
                importer['pkg'].__all__ = ['*']
                module = self.__import__('pkg', fromlist=['*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertUongo(hasattr(module, '*'))

    eleza test_invalid_type(self):
        ukijumuisha util.mock_modules('pkg.__init__') as importer:
            ukijumuisha util.import_state(meta_path=[importer]), \
                 warnings.catch_warnings():
                warnings.simplefilter('error', BytesWarning)
                ukijumuisha self.assertRaisesRegex(TypeError, r'\bfrom\b'):
                    self.__import__('pkg', fromlist=[b'attr'])
                ukijumuisha self.assertRaisesRegex(TypeError, r'\bfrom\b'):
                    self.__import__('pkg', fromlist=iter([b'attr']))

    eleza test_invalid_type_in_all(self):
        ukijumuisha util.mock_modules('pkg.__init__') as importer:
            ukijumuisha util.import_state(meta_path=[importer]), \
                 warnings.catch_warnings():
                warnings.simplefilter('error', BytesWarning)
                importer['pkg'].__all__ = [b'attr']
                ukijumuisha self.assertRaisesRegex(TypeError, r'\bpkg\.__all__\b'):
                    self.__import__('pkg', fromlist=['*'])


(Frozen_FromList,
 Source_FromList
 ) = util.test_both(HandlingFromlist, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
