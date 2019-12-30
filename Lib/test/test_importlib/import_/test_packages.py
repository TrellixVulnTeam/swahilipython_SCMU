kutoka .. agiza util
agiza sys
agiza unittest
kutoka test agiza support


kundi ParentModuleTests:

    """Importing a submodule should agiza the parent modules."""

    eleza test_import_parent(self):
        ukijumuisha util.mock_spec('pkg.__init__', 'pkg.module') kama mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                module = self.__import__('pkg.module')
                self.assertIn('pkg', sys.modules)

    eleza test_bad_parent(self):
        ukijumuisha util.mock_spec('pkg.module') kama mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                ukijumuisha self.assertRaises(ImportError) kama cm:
                    self.__import__('pkg.module')
                self.assertEqual(cm.exception.name, 'pkg')

    eleza test_raising_parent_after_importing_child(self):
        eleza __init__():
            agiza pkg.module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.module',
                                 module_code={'pkg': __init__})
        ukijumuisha mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                ukijumuisha self.assertRaises(ZeroDivisionError):
                    self.__import__('pkg')
                self.assertNotIn('pkg', sys.modules)
                self.assertIn('pkg.module', sys.modules)
                ukijumuisha self.assertRaises(ZeroDivisionError):
                    self.__import__('pkg.module')
                self.assertNotIn('pkg', sys.modules)
                self.assertIn('pkg.module', sys.modules)

    eleza test_raising_parent_after_relative_importing_child(self):
        eleza __init__():
            kutoka . agiza module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.module',
                                 module_code={'pkg': __init__})
        ukijumuisha mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                ukijumuisha self.assertRaises((ZeroDivisionError, ImportError)):
                    # This raises ImportError on the "kutoka . agiza module"
                    # line, sio sure why.
                    self.__import__('pkg')
                self.assertNotIn('pkg', sys.modules)
                ukijumuisha self.assertRaises((ZeroDivisionError, ImportError)):
                    self.__import__('pkg.module')
                self.assertNotIn('pkg', sys.modules)
                # XXX Uongo
                #self.assertIn('pkg.module', sys.modules)

    eleza test_raising_parent_after_double_relative_importing_child(self):
        eleza __init__():
            kutoka ..subpkg agiza module
            1/0
        mock = util.mock_spec('pkg.__init__', 'pkg.subpkg.__init__',
                                 'pkg.subpkg.module',
                                 module_code={'pkg.subpkg': __init__})
        ukijumuisha mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                ukijumuisha self.assertRaises((ZeroDivisionError, ImportError)):
                    # This raises ImportError on the "kutoka ..subpkg agiza module"
                    # line, sio sure why.
                    self.__import__('pkg.subpkg')
                self.assertNotIn('pkg.subpkg', sys.modules)
                ukijumuisha self.assertRaises((ZeroDivisionError, ImportError)):
                    self.__import__('pkg.subpkg.module')
                self.assertNotIn('pkg.subpkg', sys.modules)
                # XXX Uongo
                #self.assertIn('pkg.subpkg.module', sys.modules)

    eleza test_module_not_package(self):
        # Try to agiza a submodule kutoka a non-package should ashiria ImportError.
        assert sio hasattr(sys, '__path__')
        ukijumuisha self.assertRaises(ImportError) kama cm:
            self.__import__('sys.no_submodules_here')
        self.assertEqual(cm.exception.name, 'sys.no_submodules_here')

    eleza test_module_not_package_but_side_effects(self):
        # If a module injects something into sys.modules kama a side-effect, then
        # pick up on that fact.
        name = 'mod'
        subname = name + '.b'
        eleza module_injection():
            sys.modules[subname] = 'total bunk'
        mock_spec = util.mock_spec('mod',
                                         module_code={'mod': module_injection})
        ukijumuisha mock_spec kama mock:
            ukijumuisha util.import_state(meta_path=[mock]):
                jaribu:
                    submodule = self.__import__(subname)
                mwishowe:
                    support.unload(subname)


(Frozen_ParentTests,
 Source_ParentTests
 ) = util.test_both(ParentModuleTests, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
