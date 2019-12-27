"""Test relative agizas (PEP 328)."""
kutoka .. agiza util
agiza unittest
agiza warnings


kundi RelativeImports:

    """PEP 328 introduced relative agizas. This allows for agizas to occur
    kutoka within a package without having to specify the actual package name.

    A simple example is to agiza another module within the same package
    [module kutoka module]::

      # From pkg.mod1 with pkg.mod2 being a module.
      kutoka . agiza mod2

    This also works for getting an attribute kutoka a module that is specified
    in a relative fashion [attr kutoka module]::

      # From pkg.mod1.
      kutoka .mod2 agiza attr

    But this is in no way restricted to working between modules; it works
    kutoka [package to module],::

      # From pkg, agizaing pkg.module which is a module.
      kutoka . agiza module

    [module to package],::

      # Pull attr kutoka pkg, called kutoka pkg.module which is a module.
      kutoka . agiza attr

    and [package to package]::

      # From pkg.subpkg1 (both pkg.subpkg[1,2] are packages).
      kutoka .. agiza subpkg2

    The number of dots used is in no way restricted [deep agiza]::

      # Import pkg.attr kutoka pkg.pkg1.pkg2.pkg3.pkg4.pkg5.
      kutoka ...... agiza attr

    To prevent someone kutoka accessing code that is outside of a package, one
    cannot reach the location containing the root package itself::

      # From pkg.__init__ [too high kutoka package]
      kutoka .. agiza top_level

      # From pkg.module [too high kutoka module]
      kutoka .. agiza top_level

     Relative agizas are the only type of agiza that allow for an empty
     module name for an agiza [empty name].

    """

    eleza relative_import_test(self, create, globals_, callback):
        """Abstract out boilerplace for setting up for an agiza test."""
        uncache_names = []
        for name in create:
            ikiwa not name.endswith('.__init__'):
                uncache_names.append(name)
            else:
                uncache_names.append(name[:-len('.__init__')])
        with util.mock_spec(*create) as importer:
            with util.import_state(meta_path=[importer]):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    for global_ in globals_:
                        with util.uncache(*uncache_names):
                            callback(global_)


    eleza test_module_kutoka_module(self):
        # [module kutoka module]
        create = 'pkg.__init__', 'pkg.mod2'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.mod1'}
        eleza callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, kutokalist=['mod2'], level=1)
            self.assertEqual(module.__name__, 'pkg')
            self.assertTrue(hasattr(module, 'mod2'))
            self.assertEqual(module.mod2.attr, 'pkg.mod2')
        self.relative_import_test(create, globals_, callback)

    eleza test_attr_kutoka_module(self):
        # [attr kutoka module]
        create = 'pkg.__init__', 'pkg.mod2'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.mod1'}
        eleza callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('mod2', global_, kutokalist=['attr'],
                                            level=1)
            self.assertEqual(module.__name__, 'pkg.mod2')
            self.assertEqual(module.attr, 'pkg.mod2')
        self.relative_import_test(create, globals_, callback)

    eleza test_package_to_module(self):
        # [package to module]
        create = 'pkg.__init__', 'pkg.module'
        globals_ = ({'__package__': 'pkg'},
                    {'__name__': 'pkg', '__path__': ['blah']})
        eleza callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, kutokalist=['module'],
                             level=1)
            self.assertEqual(module.__name__, 'pkg')
            self.assertTrue(hasattr(module, 'module'))
            self.assertEqual(module.module.attr, 'pkg.module')
        self.relative_import_test(create, globals_, callback)

    eleza test_module_to_package(self):
        # [module to package]
        create = 'pkg.__init__', 'pkg.module'
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.module'}
        eleza callback(global_):
            self.__import__('pkg')  # For __import__().
            module = self.__import__('', global_, kutokalist=['attr'], level=1)
            self.assertEqual(module.__name__, 'pkg')
        self.relative_import_test(create, globals_, callback)

    eleza test_package_to_package(self):
        # [package to package]
        create = ('pkg.__init__', 'pkg.subpkg1.__init__',
                    'pkg.subpkg2.__init__')
        globals_ =  ({'__package__': 'pkg.subpkg1'},
                     {'__name__': 'pkg.subpkg1', '__path__': ['blah']})
        eleza callback(global_):
            module = self.__import__('', global_, kutokalist=['subpkg2'],
                                            level=2)
            self.assertEqual(module.__name__, 'pkg')
            self.assertTrue(hasattr(module, 'subpkg2'))
            self.assertEqual(module.subpkg2.attr, 'pkg.subpkg2.__init__')

    eleza test_deep_agiza(self):
        # [deep agiza]
        create = ['pkg.__init__']
        for count in range(1,6):
            create.append('{0}.pkg{1}.__init__'.format(
                            create[-1][:-len('.__init__')], count))
        globals_ = ({'__package__': 'pkg.pkg1.pkg2.pkg3.pkg4.pkg5'},
                    {'__name__': 'pkg.pkg1.pkg2.pkg3.pkg4.pkg5',
                        '__path__': ['blah']})
        eleza callback(global_):
            self.__import__(globals_[0]['__package__'])
            module = self.__import__('', global_, kutokalist=['attr'], level=6)
            self.assertEqual(module.__name__, 'pkg')
        self.relative_import_test(create, globals_, callback)

    eleza test_too_high_kutoka_package(self):
        # [too high kutoka package]
        create = ['top_level', 'pkg.__init__']
        globals_ = ({'__package__': 'pkg'},
                    {'__name__': 'pkg', '__path__': ['blah']})
        eleza callback(global_):
            self.__import__('pkg')
            with self.assertRaises(ValueError):
                self.__import__('', global_, kutokalist=['top_level'],
                                    level=2)
        self.relative_import_test(create, globals_, callback)

    eleza test_too_high_kutoka_module(self):
        # [too high kutoka module]
        create = ['top_level', 'pkg.__init__', 'pkg.module']
        globals_ = {'__package__': 'pkg'}, {'__name__': 'pkg.module'}
        eleza callback(global_):
            self.__import__('pkg')
            with self.assertRaises(ValueError):
                self.__import__('', global_, kutokalist=['top_level'],
                                    level=2)
        self.relative_import_test(create, globals_, callback)

    eleza test_empty_name_w_level_0(self):
        # [empty name]
        with self.assertRaises(ValueError):
            self.__import__('')

    eleza test_import_kutoka_different_package(self):
        # Test agizaing kutoka a different package than the caller.
        # in pkg.subpkg1.mod
        # kutoka ..subpkg2 agiza mod
        create = ['__runpy_pkg__.__init__',
                    '__runpy_pkg__.__runpy_pkg__.__init__',
                    '__runpy_pkg__.uncle.__init__',
                    '__runpy_pkg__.uncle.cousin.__init__',
                    '__runpy_pkg__.uncle.cousin.nephew']
        globals_ = {'__package__': '__runpy_pkg__.__runpy_pkg__'}
        eleza callback(global_):
            self.__import__('__runpy_pkg__.__runpy_pkg__')
            module = self.__import__('uncle.cousin', globals_, {},
                                    kutokalist=['nephew'],
                                level=2)
            self.assertEqual(module.__name__, '__runpy_pkg__.uncle.cousin')
        self.relative_import_test(create, globals_, callback)

    eleza test_import_relative_import_no_kutokalist(self):
        # Import a relative module w/ no kutokalist.
        create = ['crash.__init__', 'crash.mod']
        globals_ = [{'__package__': 'crash', '__name__': 'crash'}]
        eleza callback(global_):
            self.__import__('crash')
            mod = self.__import__('mod', global_, {}, [], 1)
            self.assertEqual(mod.__name__, 'crash.mod')
        self.relative_import_test(create, globals_, callback)

    eleza test_relative_import_no_globals(self):
        # No globals for a relative agiza is an error.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with self.assertRaises(KeyError):
                self.__import__('sys', level=1)

    eleza test_relative_import_no_package(self):
        with self.assertRaises(ImportError):
            self.__import__('a', {'__package__': '', '__spec__': None},
                            level=1)

    eleza test_relative_import_no_package_exists_absolute(self):
        with self.assertRaises(ImportError):
            self.__import__('sys', {'__package__': '', '__spec__': None},
                            level=1)


(Frozen_RelativeImports,
 Source_RelativeImports
 ) = util.test_both(RelativeImports, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
