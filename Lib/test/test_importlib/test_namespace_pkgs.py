agiza contextlib
agiza importlib
agiza os
agiza sys
agiza unittest

kutoka test.test_importlib agiza util

# needed tests:
#
# need to test when nested, so that the top-level path isn't sys.path
# need to test dynamic path detection, both at top-level na nested
# ukijumuisha dynamic path, check when a loader ni returned on path reload (that is,
#  trying to switch kutoka a namespace package to a regular package)


@contextlib.contextmanager
eleza sys_modules_context():
    """
    Make sure sys.modules ni the same object na has the same content
    when exiting the context as when entering.

    Similar to importlib.test.util.uncache, but doesn't require explicit
    names.
    """
    sys_modules_saved = sys.modules
    sys_modules_copy = sys.modules.copy()
    jaribu:
        yield
    mwishowe:
        sys.modules = sys_modules_saved
        sys.modules.clear()
        sys.modules.update(sys_modules_copy)


@contextlib.contextmanager
eleza namespace_tree_context(**kwargs):
    """
    Save agiza state na sys.modules cache na restore it on exit.
    Typical usage:

    >>> ukijumuisha namespace_tree_context(path=['/tmp/xxyy/portion1',
    ...         '/tmp/xxyy/portion2']):
    ...     pass
    """
    # use default meta_path na path_hooks unless specified otherwise
    kwargs.setdefault('meta_path', sys.meta_path)
    kwargs.setdefault('path_hooks', sys.path_hooks)
    import_context = util.import_state(**kwargs)
    ukijumuisha import_context, sys_modules_context():
        yield

kundi NamespacePackageTest(unittest.TestCase):
    """
    Subclasses should define self.root na self.paths (under that root)
    to be added to sys.path.
    """
    root = os.path.join(os.path.dirname(__file__), 'namespace_pkgs')

    eleza setUp(self):
        self.resolved_paths = [
            os.path.join(self.root, path) kila path kwenye self.paths
        ]
        self.ctx = namespace_tree_context(path=self.resolved_paths)
        self.ctx.__enter__()

    eleza tearDown(self):
        # TODO: will we ever want to pass exc_info to __exit__?
        self.ctx.__exit__(Tupu, Tupu, Tupu)


kundi SingleNamespacePackage(NamespacePackageTest):
    paths = ['portion1']

    eleza test_simple_package(self):
        agiza foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    eleza test_cant_import_other(self):
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two

    eleza test_module_repr(self):
        agiza foo.one
        self.assertEqual(repr(foo), "<module 'foo' (namespace)>")


kundi DynamicPathNamespacePackage(NamespacePackageTest):
    paths = ['portion1']

    eleza test_dynamic_path(self):
        # Make sure only 'foo.one' can be imported
        agiza foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two

        # Now modify sys.path
        sys.path.append(os.path.join(self.root, 'portion2'))

        # And make sure foo.two ni now importable
        agiza foo.two
        self.assertEqual(foo.two.attr, 'portion2 foo two')


kundi CombinedNamespacePackages(NamespacePackageTest):
    paths = ['both_portions']

    eleza test_imports(self):
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'both_portions foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')


kundi SeparatedNamespacePackages(NamespacePackageTest):
    paths = ['portion1', 'portion2']

    eleza test_imports(self):
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')


kundi SeparatedOverlappingNamespacePackages(NamespacePackageTest):
    paths = ['portion1', 'both_portions']

    eleza test_first_path_wins(self):
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')

    eleza test_first_path_wins_again(self):
        sys.path.reverse()
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'both_portions foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')

    eleza test_first_path_wins_importing_second_first(self):
        agiza foo.two
        agiza foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'both_portions foo two')


kundi SingleZipNamespacePackage(NamespacePackageTest):
    paths = ['top_level_portion1.zip']

    eleza test_simple_package(self):
        agiza foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    eleza test_cant_import_other(self):
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two


kundi SeparatedZipNamespacePackages(NamespacePackageTest):
    paths = ['top_level_portion1.zip', 'portion2']

    eleza test_imports(self):
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')
        self.assertIn('top_level_portion1.zip', foo.one.__file__)
        self.assertNotIn('.zip', foo.two.__file__)


kundi SingleNestedZipNamespacePackage(NamespacePackageTest):
    paths = ['nested_portion1.zip/nested_portion1']

    eleza test_simple_package(self):
        agiza foo.one
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    eleza test_cant_import_other(self):
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two


kundi SeparatedNestedZipNamespacePackages(NamespacePackageTest):
    paths = ['nested_portion1.zip/nested_portion1', 'portion2']

    eleza test_imports(self):
        agiza foo.one
        agiza foo.two
        self.assertEqual(foo.one.attr, 'portion1 foo one')
        self.assertEqual(foo.two.attr, 'portion2 foo two')
        fn = os.path.join('nested_portion1.zip', 'nested_portion1')
        self.assertIn(fn, foo.one.__file__)
        self.assertNotIn('.zip', foo.two.__file__)


kundi LegacySupport(NamespacePackageTest):
    paths = ['not_a_namespace_pkg', 'portion1', 'portion2', 'both_portions']

    eleza test_non_namespace_package_takes_precedence(self):
        agiza foo.one
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two
        self.assertIn('__init__', foo.__file__)
        self.assertNotIn('namespace', str(foo.__loader__).lower())


kundi DynamicPathCalculation(NamespacePackageTest):
    paths = ['project1', 'project2']

    eleza test_project3_fails(self):
        agiza parent.child.one
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)
        agiza parent.child.two
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

        self.assertEqual(parent.child.one.attr, 'parent child one')
        self.assertEqual(parent.child.two.attr, 'parent child two')

        ukijumuisha self.assertRaises(ImportError):
            agiza parent.child.three

        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

    eleza test_project3_succeeds(self):
        agiza parent.child.one
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)
        agiza parent.child.two
        self.assertEqual(len(parent.__path__), 2)
        self.assertEqual(len(parent.child.__path__), 2)

        self.assertEqual(parent.child.one.attr, 'parent child one')
        self.assertEqual(parent.child.two.attr, 'parent child two')

        ukijumuisha self.assertRaises(ImportError):
            agiza parent.child.three

        # now add project3
        sys.path.append(os.path.join(self.root, 'project3'))
        agiza parent.child.three

        # the paths dynamically get longer, to include the new directories
        self.assertEqual(len(parent.__path__), 3)
        self.assertEqual(len(parent.child.__path__), 3)

        self.assertEqual(parent.child.three.attr, 'parent child three')


kundi ZipWithMissingDirectory(NamespacePackageTest):
    paths = ['missing_directory.zip']

    @unittest.expectedFailure
    eleza test_missing_directory(self):
        # This will fail because missing_directory.zip contains:
        #   Length      Date    Time    Name
        # ---------  ---------- -----   ----
        #        29  2012-05-03 18:13   foo/one.py
        #         0  2012-05-03 20:57   bar/
        #        38  2012-05-03 20:57   bar/two.py
        # ---------                     -------
        #        67                     3 files

        # Because there ni no 'foo/', the zipimporter currently doesn't
        #  know that foo ni a namespace package

        agiza foo.one

    eleza test_present_directory(self):
        # This succeeds because there ni a "bar/" kwenye the zip file
        agiza bar.two
        self.assertEqual(bar.two.attr, 'missing_directory foo two')


kundi ModuleAndNamespacePackageInSameDir(NamespacePackageTest):
    paths = ['module_and_namespace_package']

    eleza test_module_before_namespace_package(self):
        # Make sure we find the module kwenye preference to the
        #  namespace package.
        agiza a_test
        self.assertEqual(a_test.attr, 'in module')


kundi ReloadTests(NamespacePackageTest):
    paths = ['portion1']

    eleza test_simple_package(self):
        agiza foo.one
        foo = importlib.reload(foo)
        self.assertEqual(foo.one.attr, 'portion1 foo one')

    eleza test_cant_import_other(self):
        agiza foo
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two
        foo = importlib.reload(foo)
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two

    eleza test_dynamic_path(self):
        agiza foo.one
        ukijumuisha self.assertRaises(ImportError):
            agiza foo.two

        # Now modify sys.path na reload.
        sys.path.append(os.path.join(self.root, 'portion2'))
        foo = importlib.reload(foo)

        # And make sure foo.two ni now importable
        agiza foo.two
        self.assertEqual(foo.two.attr, 'portion2 foo two')


kundi LoaderTests(NamespacePackageTest):
    paths = ['portion1']

    eleza test_namespace_loader_consistency(self):
        # bpo-32303
        agiza foo
        self.assertEqual(foo.__loader__, foo.__spec__.loader)
        self.assertIsNotTupu(foo.__loader__)

    eleza test_namespace_origin_consistency(self):
        # bpo-32305
        agiza foo
        self.assertIsTupu(foo.__spec__.origin)
        self.assertIsTupu(foo.__file__)

    eleza test_path_indexable(self):
        # bpo-35843
        agiza foo
        expected_path = os.path.join(self.root, 'portion1', 'foo')
        self.assertEqual(foo.__path__[0], expected_path)


ikiwa __name__ == "__main__":
    unittest.main()
