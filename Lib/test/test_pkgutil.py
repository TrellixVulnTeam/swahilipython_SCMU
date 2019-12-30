kutoka test.support agiza run_unittest, unload, check_warnings, CleanImport
agiza unittest
agiza sys
agiza importlib
kutoka importlib.util agiza spec_from_file_location
agiza pkgutil
agiza os
agiza os.path
agiza tempfile
agiza shutil
agiza zipfile

# Note: pkgutil.walk_packages ni currently tested kwenye test_runpy. This is
# a hack to get a major issue resolved kila 3.3b2. Longer term, it should
# be moved back here, perhaps by factoring out the helper code for
# creating interesting package layouts to a separate module.
# Issue #15348 declares this ni indeed a dodgy hack ;)

kundi PkgutilTests(unittest.TestCase):

    eleza setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dirname)
        sys.path.insert(0, self.dirname)

    eleza tearDown(self):
        toa sys.path[0]

    eleza test_getdata_filesys(self):
        pkg = 'test_getdata_filesys'

        # Include a LF na a CRLF, to test that binary data ni read back
        RESOURCE_DATA = b'Hello, world!\nSecond line\r\nThird line'

        # Make a package ukijumuisha some resources
        package_dir = os.path.join(self.dirname, pkg)
        os.mkdir(package_dir)
        # Empty init.py
        f = open(os.path.join(package_dir, '__init__.py'), "wb")
        f.close()
        # Resource files, res.txt, sub/res.txt
        f = open(os.path.join(package_dir, 'res.txt'), "wb")
        f.write(RESOURCE_DATA)
        f.close()
        os.mkdir(os.path.join(package_dir, 'sub'))
        f = open(os.path.join(package_dir, 'sub', 'res.txt'), "wb")
        f.write(RESOURCE_DATA)
        f.close()

        # Check we can read the resources
        res1 = pkgutil.get_data(pkg, 'res.txt')
        self.assertEqual(res1, RESOURCE_DATA)
        res2 = pkgutil.get_data(pkg, 'sub/res.txt')
        self.assertEqual(res2, RESOURCE_DATA)

        toa sys.modules[pkg]

    eleza test_getdata_zipfile(self):
        zip = 'test_getdata_zipfile.zip'
        pkg = 'test_getdata_zipfile'

        # Include a LF na a CRLF, to test that binary data ni read back
        RESOURCE_DATA = b'Hello, world!\nSecond line\r\nThird line'

        # Make a package ukijumuisha some resources
        zip_file = os.path.join(self.dirname, zip)
        z = zipfile.ZipFile(zip_file, 'w')

        # Empty init.py
        z.writestr(pkg + '/__init__.py', "")
        # Resource files, res.txt, sub/res.txt
        z.writestr(pkg + '/res.txt', RESOURCE_DATA)
        z.writestr(pkg + '/sub/res.txt', RESOURCE_DATA)
        z.close()

        # Check we can read the resources
        sys.path.insert(0, zip_file)
        res1 = pkgutil.get_data(pkg, 'res.txt')
        self.assertEqual(res1, RESOURCE_DATA)
        res2 = pkgutil.get_data(pkg, 'sub/res.txt')
        self.assertEqual(res2, RESOURCE_DATA)

        names = []
        kila moduleinfo kwenye pkgutil.iter_modules([zip_file]):
            self.assertIsInstance(moduleinfo, pkgutil.ModuleInfo)
            names.append(moduleinfo.name)
        self.assertEqual(names, ['test_getdata_zipfile'])

        toa sys.path[0]

        toa sys.modules[pkg]

    eleza test_unreadable_dir_on_syspath(self):
        # issue7367 - walk_packages failed ikiwa unreadable dir on sys.path
        package_name = "unreadable_package"
        d = os.path.join(self.dirname, package_name)
        # this does sio appear to create an unreadable dir on Windows
        #   but the test should sio fail anyway
        os.mkdir(d, 0)
        self.addCleanup(os.rmdir, d)
        kila t kwenye pkgutil.walk_packages(path=[self.dirname]):
            self.fail("unexpected package found")

    eleza test_walkpackages_filesys(self):
        pkg1 = 'test_walkpackages_filesys'
        pkg1_dir = os.path.join(self.dirname, pkg1)
        os.mkdir(pkg1_dir)
        f = open(os.path.join(pkg1_dir, '__init__.py'), "wb")
        f.close()
        os.mkdir(os.path.join(pkg1_dir, 'sub'))
        f = open(os.path.join(pkg1_dir, 'sub', '__init__.py'), "wb")
        f.close()
        f = open(os.path.join(pkg1_dir, 'sub', 'mod.py'), "wb")
        f.close()

        # Now, to juice it up, let's add the opposite packages, too.
        pkg2 = 'sub'
        pkg2_dir = os.path.join(self.dirname, pkg2)
        os.mkdir(pkg2_dir)
        f = open(os.path.join(pkg2_dir, '__init__.py'), "wb")
        f.close()
        os.mkdir(os.path.join(pkg2_dir, 'test_walkpackages_filesys'))
        f = open(os.path.join(pkg2_dir, 'test_walkpackages_filesys', '__init__.py'), "wb")
        f.close()
        f = open(os.path.join(pkg2_dir, 'test_walkpackages_filesys', 'mod.py'), "wb")
        f.close()

        expected = [
            'sub',
            'sub.test_walkpackages_filesys',
            'sub.test_walkpackages_filesys.mod',
            'test_walkpackages_filesys',
            'test_walkpackages_filesys.sub',
            'test_walkpackages_filesys.sub.mod',
        ]
        actual= [e[1] kila e kwenye pkgutil.walk_packages([self.dirname])]
        self.assertEqual(actual, expected)

        kila pkg kwenye expected:
            ikiwa pkg.endswith('mod'):
                endelea
            toa sys.modules[pkg]

    eleza test_walkpackages_zipfile(self):
        """Tests the same kama test_walkpackages_filesys, only ukijumuisha a zip file."""

        zip = 'test_walkpackages_zipfile.zip'
        pkg1 = 'test_walkpackages_zipfile'
        pkg2 = 'sub'

        zip_file = os.path.join(self.dirname, zip)
        z = zipfile.ZipFile(zip_file, 'w')
        z.writestr(pkg2 + '/__init__.py', "")
        z.writestr(pkg2 + '/' + pkg1 + '/__init__.py', "")
        z.writestr(pkg2 + '/' + pkg1 + '/mod.py', "")
        z.writestr(pkg1 + '/__init__.py', "")
        z.writestr(pkg1 + '/' + pkg2 + '/__init__.py', "")
        z.writestr(pkg1 + '/' + pkg2 + '/mod.py', "")
        z.close()

        sys.path.insert(0, zip_file)
        expected = [
            'sub',
            'sub.test_walkpackages_zipfile',
            'sub.test_walkpackages_zipfile.mod',
            'test_walkpackages_zipfile',
            'test_walkpackages_zipfile.sub',
            'test_walkpackages_zipfile.sub.mod',
        ]
        actual= [e[1] kila e kwenye pkgutil.walk_packages([zip_file])]
        self.assertEqual(actual, expected)
        toa sys.path[0]

        kila pkg kwenye expected:
            ikiwa pkg.endswith('mod'):
                endelea
            toa sys.modules[pkg]

    eleza test_walk_packages_ashirias_on_string_or_bytes_input(self):

        str_input = 'test_dir'
        ukijumuisha self.assertRaises((TypeError, ValueError)):
            list(pkgutil.walk_packages(str_input))

        bytes_input = b'test_dir'
        ukijumuisha self.assertRaises((TypeError, ValueError)):
            list(pkgutil.walk_packages(bytes_input))


kundi PkgutilPEP302Tests(unittest.TestCase):

    kundi MyTestLoader(object):
        eleza create_module(self, spec):
            rudisha Tupu

        eleza exec_module(self, mod):
            # Count how many times the module ni reloaded
            mod.__dict__['loads'] = mod.__dict__.get('loads', 0) + 1

        eleza get_data(self, path):
            rudisha "Hello, world!"

    kundi MyTestImporter(object):
        eleza find_spec(self, fullname, path=Tupu, target=Tupu):
            loader = PkgutilPEP302Tests.MyTestLoader()
            rudisha spec_from_file_location(fullname,
                                           '<%s>' % loader.__class__.__name__,
                                           loader=loader,
                                           submodule_search_locations=[])

    eleza setUp(self):
        sys.meta_path.insert(0, self.MyTestImporter())

    eleza tearDown(self):
        toa sys.meta_path[0]

    eleza test_getdata_pep302(self):
        # Use a dummy finder/loader
        self.assertEqual(pkgutil.get_data('foo', 'dummy'), "Hello, world!")
        toa sys.modules['foo']

    eleza test_alreadyloaded(self):
        # Ensure that get_data works without reloading - the "loads" module
        # variable kwenye the example loader should count how many times a reload
        # occurs.
        agiza foo
        self.assertEqual(foo.loads, 1)
        self.assertEqual(pkgutil.get_data('foo', 'dummy'), "Hello, world!")
        self.assertEqual(foo.loads, 1)
        toa sys.modules['foo']


# These tests, especially the setup na cleanup, are hideous. They
# need to be cleaned up once issue 14715 ni addressed.
kundi ExtendPathTests(unittest.TestCase):
    eleza create_init(self, pkgname):
        dirname = tempfile.mkdtemp()
        sys.path.insert(0, dirname)

        pkgdir = os.path.join(dirname, pkgname)
        os.mkdir(pkgdir)
        ukijumuisha open(os.path.join(pkgdir, '__init__.py'), 'w') kama fl:
            fl.write('kutoka pkgutil agiza extend_path\n__path__ = extend_path(__path__, __name__)\n')

        rudisha dirname

    eleza create_submodule(self, dirname, pkgname, submodule_name, value):
        module_name = os.path.join(dirname, pkgname, submodule_name + '.py')
        ukijumuisha open(module_name, 'w') kama fl:
            andika('value={}'.format(value), file=fl)

    eleza test_simple(self):
        pkgname = 'foo'
        dirname_0 = self.create_init(pkgname)
        dirname_1 = self.create_init(pkgname)
        self.create_submodule(dirname_0, pkgname, 'bar', 0)
        self.create_submodule(dirname_1, pkgname, 'baz', 1)
        agiza foo.bar
        agiza foo.baz
        # Ensure we read the expected values
        self.assertEqual(foo.bar.value, 0)
        self.assertEqual(foo.baz.value, 1)

        # Ensure the path ni set up correctly
        self.assertEqual(sorted(foo.__path__),
                         sorted([os.path.join(dirname_0, pkgname),
                                 os.path.join(dirname_1, pkgname)]))

        # Cleanup
        shutil.rmtree(dirname_0)
        shutil.rmtree(dirname_1)
        toa sys.path[0]
        toa sys.path[0]
        toa sys.modules['foo']
        toa sys.modules['foo.bar']
        toa sys.modules['foo.baz']


    # Another awful testing hack to be cleaned up once the test_runpy
    # helpers are factored out to a common location
    eleza test_iter_importers(self):
        iter_importers = pkgutil.iter_importers
        get_importer = pkgutil.get_importer

        pkgname = 'spam'
        modname = 'eggs'
        dirname = self.create_init(pkgname)
        pathitem = os.path.join(dirname, pkgname)
        fullname = '{}.{}'.format(pkgname, modname)
        sys.modules.pop(fullname, Tupu)
        sys.modules.pop(pkgname, Tupu)
        jaribu:
            self.create_submodule(dirname, pkgname, modname, 0)

            importlib.import_module(fullname)

            importers = list(iter_importers(fullname))
            expected_importer = get_importer(pathitem)
            kila finder kwenye importers:
                spec = pkgutil._get_spec(finder, fullname)
                loader = spec.loader
                jaribu:
                    loader = loader.loader
                tatizo AttributeError:
                    # For now we still allow raw loaders kutoka
                    # find_module().
                    pita
                self.assertIsInstance(finder, importlib.machinery.FileFinder)
                self.assertEqual(finder, expected_importer)
                self.assertIsInstance(loader,
                                      importlib.machinery.SourceFileLoader)
                self.assertIsTupu(pkgutil._get_spec(finder, pkgname))

            ukijumuisha self.assertRaises(ImportError):
                list(iter_importers('invalid.module'))

            ukijumuisha self.assertRaises(ImportError):
                list(iter_importers('.spam'))
        mwishowe:
            shutil.rmtree(dirname)
            toa sys.path[0]
            jaribu:
                toa sys.modules['spam']
                toa sys.modules['spam.eggs']
            tatizo KeyError:
                pita


    eleza test_mixed_namespace(self):
        pkgname = 'foo'
        dirname_0 = self.create_init(pkgname)
        dirname_1 = self.create_init(pkgname)
        self.create_submodule(dirname_0, pkgname, 'bar', 0)
        # Turn this into a PEP 420 namespace package
        os.unlink(os.path.join(dirname_0, pkgname, '__init__.py'))
        self.create_submodule(dirname_1, pkgname, 'baz', 1)
        agiza foo.bar
        agiza foo.baz
        # Ensure we read the expected values
        self.assertEqual(foo.bar.value, 0)
        self.assertEqual(foo.baz.value, 1)

        # Ensure the path ni set up correctly
        self.assertEqual(sorted(foo.__path__),
                         sorted([os.path.join(dirname_0, pkgname),
                                 os.path.join(dirname_1, pkgname)]))

        # Cleanup
        shutil.rmtree(dirname_0)
        shutil.rmtree(dirname_1)
        toa sys.path[0]
        toa sys.path[0]
        toa sys.modules['foo']
        toa sys.modules['foo.bar']
        toa sys.modules['foo.baz']

    # XXX: test .pkg files


kundi NestedNamespacePackageTest(unittest.TestCase):

    eleza setUp(self):
        self.basedir = tempfile.mkdtemp()
        self.old_path = sys.path[:]

    eleza tearDown(self):
        sys.path[:] = self.old_path
        shutil.rmtree(self.basedir)

    eleza create_module(self, name, contents):
        base, final = name.rsplit('.', 1)
        base_path = os.path.join(self.basedir, base.replace('.', os.path.sep))
        os.makedirs(base_path, exist_ok=Kweli)
        ukijumuisha open(os.path.join(base_path, final + ".py"), 'w') kama f:
            f.write(contents)

    eleza test_nested(self):
        pkgutil_boilerplate = (
            'agiza pkgutil; '
            '__path__ = pkgutil.extend_path(__path__, __name__)')
        self.create_module('a.pkg.__init__', pkgutil_boilerplate)
        self.create_module('b.pkg.__init__', pkgutil_boilerplate)
        self.create_module('a.pkg.subpkg.__init__', pkgutil_boilerplate)
        self.create_module('b.pkg.subpkg.__init__', pkgutil_boilerplate)
        self.create_module('a.pkg.subpkg.c', 'c = 1')
        self.create_module('b.pkg.subpkg.d', 'd = 2')
        sys.path.insert(0, os.path.join(self.basedir, 'a'))
        sys.path.insert(0, os.path.join(self.basedir, 'b'))
        agiza pkg
        self.addCleanup(unload, 'pkg')
        self.assertEqual(len(pkg.__path__), 2)
        agiza pkg.subpkg
        self.addCleanup(unload, 'pkg.subpkg')
        self.assertEqual(len(pkg.subpkg.__path__), 2)
        kutoka pkg.subpkg.c agiza c
        kutoka pkg.subpkg.d agiza d
        self.assertEqual(c, 1)
        self.assertEqual(d, 2)


kundi ImportlibMigrationTests(unittest.TestCase):
    # With full PEP 302 support kwenye the standard agiza machinery, the
    # PEP 302 emulation kwenye this module ni kwenye the process of being
    # deprecated kwenye favour of importlib proper

    eleza check_deprecated(self):
        rudisha check_warnings(
            ("This emulation ni deprecated, use 'importlib' instead",
             DeprecationWarning))

    eleza test_importer_deprecated(self):
        ukijumuisha self.check_deprecated():
            pkgutil.ImpImporter("")

    eleza test_loader_deprecated(self):
        ukijumuisha self.check_deprecated():
            pkgutil.ImpLoader("", "", "", "")

    eleza test_get_loader_avoids_emulation(self):
        ukijumuisha check_warnings() kama w:
            self.assertIsNotTupu(pkgutil.get_loader("sys"))
            self.assertIsNotTupu(pkgutil.get_loader("os"))
            self.assertIsNotTupu(pkgutil.get_loader("test.support"))
            self.assertEqual(len(w.warnings), 0)

    @unittest.skipIf(__name__ == '__main__', 'not compatible ukijumuisha __main__')
    eleza test_get_loader_handles_missing_loader_attribute(self):
        global __loader__
        this_loader = __loader__
        toa __loader__
        jaribu:
            ukijumuisha check_warnings() kama w:
                self.assertIsNotTupu(pkgutil.get_loader(__name__))
                self.assertEqual(len(w.warnings), 0)
        mwishowe:
            __loader__ = this_loader

    eleza test_get_loader_handles_missing_spec_attribute(self):
        name = 'spam'
        mod = type(sys)(name)
        toa mod.__spec__
        ukijumuisha CleanImport(name):
            sys.modules[name] = mod
            loader = pkgutil.get_loader(name)
        self.assertIsTupu(loader)

    eleza test_get_loader_handles_spec_attribute_none(self):
        name = 'spam'
        mod = type(sys)(name)
        mod.__spec__ = Tupu
        ukijumuisha CleanImport(name):
            sys.modules[name] = mod
            loader = pkgutil.get_loader(name)
        self.assertIsTupu(loader)

    eleza test_get_loader_Tupu_in_sys_modules(self):
        name = 'totally bogus'
        sys.modules[name] = Tupu
        jaribu:
            loader = pkgutil.get_loader(name)
        mwishowe:
            toa sys.modules[name]
        self.assertIsTupu(loader)

    eleza test_find_loader_missing_module(self):
        name = 'totally bogus'
        loader = pkgutil.find_loader(name)
        self.assertIsTupu(loader)

    eleza test_find_loader_avoids_emulation(self):
        ukijumuisha check_warnings() kama w:
            self.assertIsNotTupu(pkgutil.find_loader("sys"))
            self.assertIsNotTupu(pkgutil.find_loader("os"))
            self.assertIsNotTupu(pkgutil.find_loader("test.support"))
            self.assertEqual(len(w.warnings), 0)

    eleza test_get_importer_avoids_emulation(self):
        # We use an illegal path so *none* of the path hooks should fire
        ukijumuisha check_warnings() kama w:
            self.assertIsTupu(pkgutil.get_importer("*??"))
            self.assertEqual(len(w.warnings), 0)

    eleza test_iter_importers_avoids_emulation(self):
        ukijumuisha check_warnings() kama w:
            kila importer kwenye pkgutil.iter_importers(): pita
            self.assertEqual(len(w.warnings), 0)


eleza test_main():
    run_unittest(PkgutilTests, PkgutilPEP302Tests, ExtendPathTests,
                 NestedNamespacePackageTest, ImportlibMigrationTests)
    # this ni necessary ikiwa test ni run repeated (like when finding leaks)
    agiza zipagiza
    agiza importlib
    zipagiza._zip_directory_cache.clear()
    importlib.invalidate_caches()


ikiwa __name__ == '__main__':
    test_main()
