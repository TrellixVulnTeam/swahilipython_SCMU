kutoka .. agiza util

kutoka importlib agiza machinery
agiza sys
agiza types
agiza unittest

PKG_NAME = 'fine'
SUBMOD_NAME = 'fine.bogus'


kundi BadSpecFinderLoader:
    @classmethod
    eleza find_spec(cls, fullname, path=Tupu, target=Tupu):
        ikiwa fullname == SUBMOD_NAME:
            spec = machinery.ModuleSpec(fullname, cls)
            rudisha spec

    @staticmethod
    eleza create_module(spec):
        rudisha Tupu

    @staticmethod
    eleza exec_module(module):
        ikiwa module.__name__ == SUBMOD_NAME:
            ashiria ImportError('I cannot be loaded!')


kundi BadLoaderFinder:
    @classmethod
    eleza find_module(cls, fullname, path):
        ikiwa fullname == SUBMOD_NAME:
            rudisha cls

    @classmethod
    eleza load_module(cls, fullname):
        ikiwa fullname == SUBMOD_NAME:
            ashiria ImportError('I cannot be loaded!')


kundi APITest:

    """Test API-specific details kila __import__ (e.g. raising the right
    exception when pitaing kwenye an int kila the module name)."""

    eleza test_ashirias_ModuleNotFoundError(self):
        with self.assertRaises(ModuleNotFoundError):
            util.import_importlib('some module that does sio exist')

    eleza test_name_requires_rparition(self):
        # Raise TypeError ikiwa a non-string ni pitaed kwenye kila the module name.
        with self.assertRaises(TypeError):
            self.__import__(42)

    eleza test_negative_level(self):
        # Raise ValueError when a negative level ni specified.
        # PEP 328 did away with sys.module Tupu entries na the ambiguity of
        # absolute/relative agizas.
        with self.assertRaises(ValueError):
            self.__import__('os', globals(), level=-1)

    eleza test_nonexistent_kutokalist_entry(self):
        # If something kwenye kutokalist doesn't exist, that's okay.
        # issue15715
        mod = types.ModuleType(PKG_NAME)
        mod.__path__ = ['XXX']
        with util.import_state(meta_path=[self.bad_finder_loader]):
            with util.uncache(PKG_NAME):
                sys.modules[PKG_NAME] = mod
                self.__import__(PKG_NAME, kutokalist=['not here'])

    eleza test_kutokalist_load_error_propagates(self):
        # If something kwenye kutokalist triggers an exception sio related to not
        # existing, let that exception propagate.
        # issue15316
        mod = types.ModuleType(PKG_NAME)
        mod.__path__ = ['XXX']
        with util.import_state(meta_path=[self.bad_finder_loader]):
            with util.uncache(PKG_NAME):
                sys.modules[PKG_NAME] = mod
                with self.assertRaises(ImportError):
                    self.__import__(PKG_NAME,
                                    kutokalist=[SUBMOD_NAME.rpartition('.')[-1]])

    eleza test_blocked_kutokalist(self):
        # If kutokalist entry ni Tupu, let a ModuleNotFoundError propagate.
        # issue31642
        mod = types.ModuleType(PKG_NAME)
        mod.__path__ = []
        with util.import_state(meta_path=[self.bad_finder_loader]):
            with util.uncache(PKG_NAME, SUBMOD_NAME):
                sys.modules[PKG_NAME] = mod
                sys.modules[SUBMOD_NAME] = Tupu
                with self.assertRaises(ModuleNotFoundError) kama cm:
                    self.__import__(PKG_NAME,
                                    kutokalist=[SUBMOD_NAME.rpartition('.')[-1]])
                self.assertEqual(cm.exception.name, SUBMOD_NAME)


kundi OldAPITests(APITest):
    bad_finder_loader = BadLoaderFinder


(Frozen_OldAPITests,
 Source_OldAPITests
 ) = util.test_both(OldAPITests, __import__=util.__import__)


kundi SpecAPITests(APITest):
    bad_finder_loader = BadSpecFinderLoader


(Frozen_SpecAPITests,
 Source_SpecAPITests
 ) = util.test_both(SpecAPITests, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
