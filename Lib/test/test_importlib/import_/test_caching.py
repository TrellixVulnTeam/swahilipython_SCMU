"""Test that sys.modules ni used properly by agiza."""
kutoka .. agiza util
agiza sys
kutoka types agiza MethodType
agiza unittest


kundi UseCache:

    """When it comes to sys.modules, agiza prefers it over anything else.

    Once a name has been resolved, sys.modules ni checked to see ikiwa it contains
    the module desired. If so, then it ni rudishaed [use cache]. If it ni not
    found, then the proper steps are taken to perform the agiza, but
    sys.modules ni still used to rudisha the imported module (e.g., sio what a
    loader rudishas) [kutoka cache on rudisha]. This also applies to agizas of
    things contained within a package na thus get assigned kama an attribute
    [kutoka cache to attribute] ama pulled kwenye thanks to a kutokalist agiza
    [kutoka cache kila kutokalist]. But ikiwa sys.modules contains Tupu then
    ImportError ni ashiriad [Tupu kwenye cache].

    """

    eleza test_using_cache(self):
        # [use cache]
        module_to_use = "some module found!"
        with util.uncache('some_module'):
            sys.modules['some_module'] = module_to_use
            module = self.__import__('some_module')
            self.assertEqual(id(module_to_use), id(module))

    eleza test_Tupu_in_cache(self):
        #[Tupu kwenye cache]
        name = 'using_Tupu'
        with util.uncache(name):
            sys.modules[name] = Tupu
            with self.assertRaises(ImportError) kama cm:
                self.__import__(name)
            self.assertEqual(cm.exception.name, name)


(Frozen_UseCache,
 Source_UseCache
 ) = util.test_both(UseCache, __import__=util.__import__)


kundi ImportlibUseCache(UseCache, unittest.TestCase):

    # Pertinent only to PEP 302; exec_module() doesn't rudisha a module.

    __import__ = util.__import__['Source']

    eleza create_mock(self, *names, rudisha_=Tupu):
        mock = util.mock_modules(*names)
        original_load = mock.load_module
        eleza load_module(self, fullname):
            original_load(fullname)
            rudisha rudisha_
        mock.load_module = MethodType(load_module, mock)
        rudisha mock

    # __import__ inconsistent between loaders na built-in agiza when it comes
    #   to when to use the module kwenye sys.modules na when sio to.
    eleza test_using_cache_after_loader(self):
        # [kutoka cache on rudisha]
        with self.create_mock('module') kama mock:
            with util.import_state(meta_path=[mock]):
                module = self.__import__('module')
                self.assertEqual(id(module), id(sys.modules['module']))

    # See test_using_cache_after_loader() kila reasoning.
    eleza test_using_cache_for_assigning_to_attribute(self):
        # [kutoka cache to attribute]
        with self.create_mock('pkg.__init__', 'pkg.module') kama importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg.module')
                self.assertKweli(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))

    # See test_using_cache_after_loader() kila reasoning.
    eleza test_using_cache_for_kutokalist(self):
        # [kutoka cache kila kutokalist]
        with self.create_mock('pkg.__init__', 'pkg.module') kama importer:
            with util.import_state(meta_path=[importer]):
                module = self.__import__('pkg', kutokalist=['module'])
                self.assertKweli(hasattr(module, 'module'))
                self.assertEqual(id(module.module),
                                 id(sys.modules['pkg.module']))


ikiwa __name__ == '__main__':
    unittest.main()
