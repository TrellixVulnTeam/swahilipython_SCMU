"""PEP 366 ("Main module explicit relative agizas") specifies the
semantics for the __package__ attribute on modules. This attribute is
used, when available, to detect which package a module belongs to (instead
of using the typical __path__/__name__ test).

"""
agiza unittest
agiza warnings
kutoka .. agiza util


kundi Using__package__:

    """Use of __package__ supersedes the use of __name__/__path__ to calculate
    what package a module belongs to. The basic algorithm is [__package__]::

      eleza resolve_name(name, package, level):
          level -= 1
          base = package.rsplit('.', level)[0]
          rudisha '{0}.{1}'.format(base, name)

    But since there is no guarantee that __package__ has been set (or not been
    set to None [None]), there has to be a way to calculate the attribute's value
    [__name__]::

      eleza calc_package(caller_name, has___path__):
          ikiwa has__path__:
              rudisha caller_name
          else:
              rudisha caller_name.rsplit('.', 1)[0]

    Then the normal algorithm for relative name agizas can proceed as if
    __package__ had been set.

    """

    eleza import_module(self, globals_):
        with self.mock_modules('pkg.__init__', 'pkg.fake') as importer:
            with util.import_state(meta_path=[importer]):
                self.__import__('pkg.fake')
                module = self.__import__('',
                                         globals=globals_,
                                         kutokalist=['attr'], level=2)
        rudisha module

    eleza test_using___package__(self):
        # [__package__]
        module = self.import_module({'__package__': 'pkg.fake'})
        self.assertEqual(module.__name__, 'pkg')

    eleza test_using___name__(self):
        # [__name__]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            module = self.import_module({'__name__': 'pkg.fake',
                                         '__path__': []})
        self.assertEqual(module.__name__, 'pkg')

    eleza test_warn_when_using___name__(self):
        with self.assertWarns(ImportWarning):
            self.import_module({'__name__': 'pkg.fake', '__path__': []})

    eleza test_None_as___package__(self):
        # [None]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            module = self.import_module({
                '__name__': 'pkg.fake', '__path__': [], '__package__': None })
        self.assertEqual(module.__name__, 'pkg')

    eleza test_spec_fallback(self):
        # If __package__ isn't defined, fall back on __spec__.parent.
        module = self.import_module({'__spec__': FakeSpec('pkg.fake')})
        self.assertEqual(module.__name__, 'pkg')

    eleza test_warn_when_package_and_spec_disagree(self):
        # Raise an ImportWarning ikiwa __package__ != __spec__.parent.
        with self.assertWarns(ImportWarning):
            self.import_module({'__package__': 'pkg.fake',
                                '__spec__': FakeSpec('pkg.fakefake')})

    eleza test_bad__package__(self):
        globals = {'__package__': '<not real>'}
        with self.assertRaises(ModuleNotFoundError):
            self.__import__('', globals, {}, ['relimport'], 1)

    eleza test_bunk__package__(self):
        globals = {'__package__': 42}
        with self.assertRaises(TypeError):
            self.__import__('', globals, {}, ['relimport'], 1)


kundi FakeSpec:
    eleza __init__(self, parent):
        self.parent = parent


kundi Using__package__PEP302(Using__package__):
    mock_modules = util.mock_modules


(Frozen_UsingPackagePEP302,
 Source_UsingPackagePEP302
 ) = util.test_both(Using__package__PEP302, __import__=util.__import__)


kundi Using__package__PEP451(Using__package__):
    mock_modules = util.mock_spec


(Frozen_UsingPackagePEP451,
 Source_UsingPackagePEP451
 ) = util.test_both(Using__package__PEP451, __import__=util.__import__)


kundi Setting__package__:

    """Because __package__ is a new feature, it is not always set by a loader.
    Import will set it as needed to help with the transition to relying on
    __package__.

    For a top-level module, __package__ is set to None [top-level]. For a
    package __name__ is used for __package__ [package]. For submodules the
    value is __name__.rsplit('.', 1)[0] [submodule].

    """

    __import__ = util.__import__['Source']

    # [top-level]
    eleza test_top_level(self):
        with self.mock_modules('top_level') as mock:
            with util.import_state(meta_path=[mock]):
                del mock['top_level'].__package__
                module = self.__import__('top_level')
                self.assertEqual(module.__package__, '')

    # [package]
    eleza test_package(self):
        with self.mock_modules('pkg.__init__') as mock:
            with util.import_state(meta_path=[mock]):
                del mock['pkg'].__package__
                module = self.__import__('pkg')
                self.assertEqual(module.__package__, 'pkg')

    # [submodule]
    eleza test_submodule(self):
        with self.mock_modules('pkg.__init__', 'pkg.mod') as mock:
            with util.import_state(meta_path=[mock]):
                del mock['pkg.mod'].__package__
                pkg = self.__import__('pkg.mod')
                module = getattr(pkg, 'mod')
                self.assertEqual(module.__package__, 'pkg')

kundi Setting__package__PEP302(Setting__package__, unittest.TestCase):
    mock_modules = util.mock_modules

kundi Setting__package__PEP451(Setting__package__, unittest.TestCase):
    mock_modules = util.mock_spec


ikiwa __name__ == '__main__':
    unittest.main()
