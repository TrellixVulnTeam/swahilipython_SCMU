"""Test that the semantics relating to the 'kutokalist' argument are correct."""
kutoka .. agiza util
agiza warnings
agiza unittest


kundi ReturnValue:

    """The use of kutokalist influences what agiza returns.

    If direct ``agiza ...`` statement is used, the root module or package is
    returned [agiza return]. But ikiwa kutokalist is set, then the specified module
    is actually returned (whether it is a relative agiza or not)
    [kutoka return].

    """

    eleza test_return_kutoka_agiza(self):
        # [agiza return]
        with util.mock_spec('pkg.__init__', 'pkg.module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertEqual(module.__name__, 'pkg')

    eleza test_return_kutoka_kutoka_agiza(self):
        # [kutoka return]
        with util.mock_modules('pkg.__init__', 'pkg.module')as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module', kutokalist=['attr'])
                self.assertEqual(module.__name__, 'pkg.module')


(Frozen_ReturnValue,
 Source_ReturnValue
 ) = util.test_both(ReturnValue, __import__=util.__import__)


kundi HandlingFromlist:

    """Using kutokalist triggers different actions based on what is being asked
    of it.

    If kutokalist specifies an object on a module, nothing special happens
    [object case]. This is even true ikiwa the object does not exist [bad object].

    If a package is being imported, then what is listed in kutokalist may be
    treated as a module to be imported [module]. And this extends to what is
    contained in __all__ when '*' is imported [using *]. And '*' does not need
    to be the only name in the kutokalist [using * with others].

    """

    eleza test_object(self):
        # [object case]
        with util.mock_modules('module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('module', kutokalist=['attr'])
                self.assertEqual(module.__name__, 'module')

    eleza test_nonexistent_object(self):
        # [bad object]
        with util.mock_modules('module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('module', kutokalist=['non_existent'])
                self.assertEqual(module.__name__, 'module')
                self.assertFalse(hasattr(module, 'non_existent'))

    eleza test_module_kutoka_package(self):
        # [module]
        with util.mock_modules('pkg.__init__', 'pkg.module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', kutokalist=['module'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertTrue(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    eleza test_nonexistent_kutoka_package(self):
        with util.mock_modules('pkg.__init__') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', kutokalist=['non_existent'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertFalse(hasattr(module, 'non_existent'))

    eleza test_module_kutoka_package_triggers_ModuleNotFoundError(self):
        # If a submodule causes an ModuleNotFoundError because it tries
        # to agiza a module which doesn't exist, that should let the
        # ModuleNotFoundError propagate.
        eleza module_code():
            agiza i_do_not_exist
        with util.mock_modules('pkg.__init__', 'pkg.mod',
                               module_code={'pkg.mod': module_code}) as importer:
            with util.import_state(meta_path=[importer]):
                with self.assertRaises(ModuleNotFoundError) as exc:
                    self.__import__('pkg', kutokalist=['mod'])
                self.assertEqual('i_do_not_exist', exc.exception.name)

    eleza test_empty_string(self):
        with util.mock_modules('pkg.__init__', 'pkg.mod') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.mod', kutokalist=[''])
                self.assertEqual(module.__name__, 'pkg.mod')

    eleza basic_star_test(self, kutokalist=['*']):
        # [using *]
        with util.mock_modules('pkg.__init__', 'pkg.module') as mock:
            with util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module']
                module = self.__import__('pkg', kutokalist=kutokalist)
                self.assertEqual(module.__name__, 'pkg')
                self.assertTrue(hasattr(module, 'module'))
                self.assertEqual(module.module.__name__, 'pkg.module')

    eleza test_using_star(self):
        # [using *]
        self.basic_star_test()

    eleza test_kutokalist_as_tuple(self):
        self.basic_star_test(('*',))

    eleza test_star_with_others(self):
        # [using * with others]
        context = util.mock_modules('pkg.__init__', 'pkg.module1', 'pkg.module2')
        with context as mock:
            with util.import_state(meta_path=[mock]):
                mock['pkg'].__all__ = ['module1']
                module = self.__import__('pkg', kutokalist=['module2', '*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertTrue(hasattr(module, 'module1'))
                self.assertTrue(hasattr(module, 'module2'))
                self.assertEqual(module.module1.__name__, 'pkg.module1')
                self.assertEqual(module.module2.__name__, 'pkg.module2')

    eleza test_nonexistent_in_all(self):
        with util.mock_modules('pkg.__init__') as importer:
            with util.import_state(meta_path=[importer]):
                importer['pkg'].__all__ = ['non_existent']
                module = self.__import__('pkg', kutokalist=['*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertFalse(hasattr(module, 'non_existent'))

    eleza test_star_in_all(self):
        with util.mock_modules('pkg.__init__') as importer:
            with util.import_state(meta_path=[importer]):
                importer['pkg'].__all__ = ['*']
                module = self.__import__('pkg', kutokalist=['*'])
                self.assertEqual(module.__name__, 'pkg')
                self.assertFalse(hasattr(module, '*'))

    eleza test_invalid_type(self):
        with util.mock_modules('pkg.__init__') as importer:
            with util.import_state(meta_path=[importer]), \
                 warnings.catch_warnings():
                warnings.simplefilter('error', BytesWarning)
                with self.assertRaisesRegex(TypeError, r'\bkutoka\b'):
                    self.__import__('pkg', kutokalist=[b'attr'])
                with self.assertRaisesRegex(TypeError, r'\bkutoka\b'):
                    self.__import__('pkg', kutokalist=iter([b'attr']))

    eleza test_invalid_type_in_all(self):
        with util.mock_modules('pkg.__init__') as importer:
            with util.import_state(meta_path=[importer]), \
                 warnings.catch_warnings():
                warnings.simplefilter('error', BytesWarning)
                importer['pkg'].__all__ = [b'attr']
                with self.assertRaisesRegex(TypeError, r'\bpkg\.__all__\b'):
                    self.__import__('pkg', kutokalist=['*'])


(Frozen_FromList,
 Source_FromList
 ) = util.test_both(HandlingFromlist, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
