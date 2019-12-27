"""Test that sys.modules is used properly by agiza."""
kutoka .. agiza util
agiza sys
kutoka types agiza MethodType
agiza unittest


kundi UseCache:

    """When it comes to sys.modules, agiza prefers it over anything else.

    Once a name has been resolved, sys.modules is checked to see ikiwa it contains
    the module desired. If so, then it is returned [use cache]. If it is not
    found, then the proper steps are taken to perform the agiza, but
    sys.modules is still used to rudisha the imported module (e.g., not what a
    loader returns) [kutoka cache on return]. This also applies to agizas of
    things contained within a package and thus get assigned as an attribute
    [kutoka cache to attribute] or pulled in thanks to a kutokalist agiza
    [kutoka cache for kutokalist]. But ikiwa sys.modules contains None then
    ImportError is raised [None in cache].

    """

    eleza test_using_cache(self):
        # [use cache]
        module_to_use = "some module found!"
        with util.uncache('some_module'):
            sys.modules['some_module'] = module_to_use
            module = self.__import__('some_module')
            self.assertEqual(id(module_to_use), id(module))

    eleza test_None_in_cache(self):
        #[None in cache]
        name = 'using_None'
        with util.uncache(name):
            sys.modules[name] = None
            with self.assertRaises(ImportError) as cm:
                self.__import__(name)
            self.assertEqual(cm.exception.name, name)


(Frozen_UseCache,
 Source_UseCache
 ) = util.test_both(UseCache, __import__=util.__import__)


kundi ImportlibUseCache(UseCache, unittest.TestCase):

    # Pertinent only to PEP 302; exec_module() doesn't rudisha a module.

    __import__ = util.__import__['Source']

    eleza create_mock(self, *names, return_=None):
        mock = util.mock_modules(*names)
        original_load = mock.load_module
        eleza load_module(self, fullname):
            original_load(fullname)
            rudisha return_
        mock.load_module = MethodType(load_module, mock)
        rudisha mock

    # __import__ inconsistent between loaders and built-in agiza when it comes
    #   to when to use the module in sys.modules and when not to.
    eleza test_using_cache_after_loader(self):
        # [kutoka cache on return]
        with self.create_mock('module') as mock:
            with util.import_state(meta_path=[mock]):
                module = self.__import__('module')
                self.assertEqual(id(module), id(sys.modules['module']))

    # See test_using_cache_after_loader() for reasoning.
    eleza test_using_cache_for_assigning_to_attribute(self):
        # [kutoka cache to attribute]
        with self.create_mock('pkg.__init__', 'pkg.module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertTrue(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))

    # See test_using_cache_after_loader() for reasoning.
    eleza test_using_cache_for_kutokalist(self):
        # [kutoka cache for kutokalist]
        with self.create_mock('pkg.__init__', 'pkg.module') as importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', kutokalist=['module'])
                self.assertTrue(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))


ikiwa __name__ == '__main__':
    unittest.main()
