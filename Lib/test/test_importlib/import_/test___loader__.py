kutoka importlib agiza machinery
agiza sys
agiza types
agiza unittest

kutoka .. agiza util


kundi SpecLoaderMock:

    eleza find_spec(self, fullname, path=None, target=None):
        rudisha machinery.ModuleSpec(fullname, self)

    eleza create_module(self, spec):
        rudisha None

    eleza exec_module(self, module):
        pass


kundi SpecLoaderAttributeTests:

    eleza test___loader__(self):
        loader = SpecLoaderMock()
        with util.uncache('blah'), util.import_state(meta_path=[loader]):
            module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)


(Frozen_SpecTests,
 Source_SpecTests
 ) = util.test_both(SpecLoaderAttributeTests, __import__=util.__import__)


kundi LoaderMock:

    eleza find_module(self, fullname, path=None):
        rudisha self

    eleza load_module(self, fullname):
        sys.modules[fullname] = self.module
        rudisha self.module


kundi LoaderAttributeTests:

    eleza test___loader___missing(self):
        module = types.ModuleType('blah')
        try:
            del module.__loader__
        except AttributeError:
            pass
        loader = LoaderMock()
        loader.module = module
        with util.uncache('blah'), util.import_state(meta_path=[loader]):
            module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)

    eleza test___loader___is_None(self):
        module = types.ModuleType('blah')
        module.__loader__ = None
        loader = LoaderMock()
        loader.module = module
        with util.uncache('blah'), util.import_state(meta_path=[loader]):
            returned_module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)


(Frozen_Tests,
 Source_Tests
 ) = util.test_both(LoaderAttributeTests, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
