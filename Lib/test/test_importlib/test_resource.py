agiza sys
agiza unittest

kutoka . agiza data01
kutoka . agiza zipdata01, zipdata02
kutoka . agiza util
kutoka importlib agiza resources, import_module


kundi ResourceTests:
    # Subclasses are expected to set the `data` attribute.

    eleza test_is_resource_good_path(self):
        self.assertKweli(resources.is_resource(self.data, 'binary.file'))

    eleza test_is_resource_missing(self):
        self.assertUongo(resources.is_resource(self.data, 'not-a-file'))

    eleza test_is_resource_subresource_directory(self):
        # Directories are sio resources.
        self.assertUongo(resources.is_resource(self.data, 'subdirectory'))

    eleza test_contents(self):
        contents = set(resources.contents(self.data))
        # There may be cruft kwenye the directory listing of the data directory.
        # Under Python 3 we could have a __pycache__ directory, na under
        # Python 2 we could have .pyc files.  These are both artifacts of the
        # test suite importing these modules na writing these caches.  They
        # aren't germane to this test, so just filter them out.
        contents.discard('__pycache__')
        contents.discard('__init__.pyc')
        contents.discard('__init__.pyo')
        self.assertEqual(contents, {
            '__init__.py',
            'subdirectory',
            'utf-8.file',
            'binary.file',
            'utf-16.file',
            })


kundi ResourceDiskTests(ResourceTests, unittest.TestCase):
    eleza setUp(self):
        self.data = data01


kundi ResourceZipTests(ResourceTests, util.ZipSetup, unittest.TestCase):
    pass


kundi ResourceLoaderTests(unittest.TestCase):
    eleza test_resource_contents(self):
        package = util.create_package(
            file=data01, path=data01.__file__, contents=['A', 'B', 'C'])
        self.assertEqual(
            set(resources.contents(package)),
            {'A', 'B', 'C'})

    eleza test_resource_is_resource(self):
        package = util.create_package(
            file=data01, path=data01.__file__,
            contents=['A', 'B', 'C', 'D/E', 'D/F'])
        self.assertKweli(resources.is_resource(package, 'B'))

    eleza test_resource_directory_is_not_resource(self):
        package = util.create_package(
            file=data01, path=data01.__file__,
            contents=['A', 'B', 'C', 'D/E', 'D/F'])
        self.assertUongo(resources.is_resource(package, 'D'))

    eleza test_resource_missing_is_not_resource(self):
        package = util.create_package(
            file=data01, path=data01.__file__,
            contents=['A', 'B', 'C', 'D/E', 'D/F'])
        self.assertUongo(resources.is_resource(package, 'Z'))


kundi ResourceCornerCaseTests(unittest.TestCase):
    eleza test_package_has_no_reader_fallback(self):
        # Test odd ball packages which:
        # 1. Do sio have a ResourceReader as a loader
        # 2. Are sio on the file system
        # 3. Are sio kwenye a zip file
        module = util.create_package(
            file=data01, path=data01.__file__, contents=['A', 'B', 'C'])
        # Give the module a dummy loader.
        module.__loader__ = object()
        # Give the module a dummy origin.
        module.__file__ = '/path/which/shall/not/be/named'
        ikiwa sys.version_info >= (3,):
            module.__spec__.loader = module.__loader__
            module.__spec__.origin = module.__file__
        self.assertUongo(resources.is_resource(module, 'A'))


kundi ResourceFromZipsTest(util.ZipSetupBase, unittest.TestCase):
    ZIP_MODULE = zipdata02                          # type: ignore

    eleza test_unrelated_contents(self):
        # https://gitlab.com/python-devs/importlib_resources/issues/44
        #
        # Here we have a zip file ukijumuisha two unrelated subpackages.  The bug
        # reports that getting the contents of a resource returns unrelated
        # files.
        self.assertEqual(
            set(resources.contents('ziptestdata.one')),
            {'__init__.py', 'resource1.txt'})
        self.assertEqual(
            set(resources.contents('ziptestdata.two')),
            {'__init__.py', 'resource2.txt'})


kundi SubdirectoryResourceFromZipsTest(util.ZipSetupBase, unittest.TestCase):
    ZIP_MODULE = zipdata01                          # type: ignore

    eleza test_is_submodule_resource(self):
        submodule = import_module('ziptestdata.subdirectory')
        self.assertKweli(
            resources.is_resource(submodule, 'binary.file'))

    eleza test_read_submodule_resource_by_name(self):
        self.assertKweli(
            resources.is_resource('ziptestdata.subdirectory', 'binary.file'))

    eleza test_submodule_contents(self):
        submodule = import_module('ziptestdata.subdirectory')
        self.assertEqual(
            set(resources.contents(submodule)),
            {'__init__.py', 'binary.file'})

    eleza test_submodule_contents_by_name(self):
        self.assertEqual(
            set(resources.contents('ziptestdata.subdirectory')),
            {'__init__.py', 'binary.file'})


kundi NamespaceTest(unittest.TestCase):
    eleza test_namespaces_cannot_have_resources(self):
        contents = resources.contents('test.test_importlib.data03.namespace')
        self.assertUongo(list(contents))
        # Even though there ni a file kwenye the namespace directory, it ni not
        # considered a resource, since namespace packages can't have them.
        self.assertUongo(resources.is_resource(
            'test.test_importlib.data03.namespace',
            'resource1.txt'))
        # We should get an exception ikiwa we try to read it ama open it.
        self.assertRaises(
            FileNotFoundError,
            resources.open_text,
            'test.test_importlib.data03.namespace', 'resource1.txt')
        self.assertRaises(
            FileNotFoundError,
            resources.open_binary,
            'test.test_importlib.data03.namespace', 'resource1.txt')
        self.assertRaises(
            FileNotFoundError,
            resources.read_text,
            'test.test_importlib.data03.namespace', 'resource1.txt')
        self.assertRaises(
            FileNotFoundError,
            resources.read_binary,
            'test.test_importlib.data03.namespace', 'resource1.txt')


ikiwa __name__ == '__main__':
    unittest.main()
