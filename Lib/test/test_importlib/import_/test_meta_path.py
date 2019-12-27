kutoka .. agiza util
agiza importlib._bootstrap
agiza sys
kutoka types agiza MethodType
agiza unittest
agiza warnings


kundi CallingOrder:

    """Calls to the importers on sys.meta_path happen in order that they are
    specified in the sequence, starting with the first importer
    [first called], and then continuing on down until one is found that doesn't
    rudisha None [continuing]."""


    eleza test_first_called(self):
        # [first called]
        mod = 'top_level'
        with util.mock_spec(mod) as first, util.mock_spec(mod) as second:
            with util.import_state(meta_path=[first, second]):
                self.assertIs(self.__import__(mod), first.modules[mod])

    eleza test_continuing(self):
        # [continuing]
        mod_name = 'for_real'
        with util.mock_spec('nonexistent') as first, \
             util.mock_spec(mod_name) as second:
            first.find_spec = lambda self, fullname, path=None, parent=None: None
            with util.import_state(meta_path=[first, second]):
                self.assertIs(self.__import__(mod_name), second.modules[mod_name])

    eleza test_empty(self):
        # Raise an ImportWarning ikiwa sys.meta_path is empty.
        module_name = 'nothing'
        try:
            del sys.modules[module_name]
        except KeyError:
            pass
        with util.import_state(meta_path=[]):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                self.assertIsNone(importlib._bootstrap._find_spec('nothing',
                                                                  None))
                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[-1].category, ImportWarning))


(Frozen_CallingOrder,
 Source_CallingOrder
 ) = util.test_both(CallingOrder, __import__=util.__import__)


kundi CallSignature:

    """If there is no __path__ entry on the parent module, then 'path' is None
    [no path]. Otherwise, the value for __path__ is passed in for the 'path'
    argument [path set]."""

    eleza log_finder(self, importer):
        fxn = getattr(importer, self.finder_name)
        log = []
        eleza wrapper(self, *args, **kwargs):
            log.append([args, kwargs])
            rudisha fxn(*args, **kwargs)
        rudisha log, wrapper

    eleza test_no_path(self):
        # [no path]
        mod_name = 'top_level'
        assert '.' not in mod_name
        with self.mock_modules(mod_name) as importer:
            log, wrapped_call = self.log_finder(importer)
            setattr(importer, self.finder_name, MethodType(wrapped_call, importer))
            with util.import_state(meta_path=[importer]):
                self.__import__(mod_name)
                assert len(log) == 1
                args = log[0][0]
                # Assuming all arguments are positional.
                self.assertEqual(args[0], mod_name)
                self.assertIsNone(args[1])

    eleza test_with_path(self):
        # [path set]
        pkg_name = 'pkg'
        mod_name = pkg_name + '.module'
        path = [42]
        assert '.' in mod_name
        with self.mock_modules(pkg_name+'.__init__', mod_name) as importer:
            importer.modules[pkg_name].__path__ = path
            log, wrapped_call = self.log_finder(importer)
            setattr(importer, self.finder_name, MethodType(wrapped_call, importer))
            with util.import_state(meta_path=[importer]):
                self.__import__(mod_name)
                assert len(log) == 2
                args = log[1][0]
                kwargs = log[1][1]
                # Assuming all arguments are positional.
                self.assertFalse(kwargs)
                self.assertEqual(args[0], mod_name)
                self.assertIs(args[1], path)


kundi CallSignaturePEP302(CallSignature):
    mock_modules = util.mock_modules
    finder_name = 'find_module'


(Frozen_CallSignaturePEP302,
 Source_CallSignaturePEP302
 ) = util.test_both(CallSignaturePEP302, __import__=util.__import__)


kundi CallSignaturePEP451(CallSignature):
    mock_modules = util.mock_spec
    finder_name = 'find_spec'


(Frozen_CallSignaturePEP451,
 Source_CallSignaturePEP451
 ) = util.test_both(CallSignaturePEP451, __import__=util.__import__)


ikiwa __name__ == '__main__':
    unittest.main()
