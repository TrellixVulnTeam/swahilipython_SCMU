kutoka .. agiza abc
kutoka .. agiza util

machinery = util.import_importlib('importlib.machinery')

agiza errno
agiza os
agiza py_compile
agiza stat
agiza sys
agiza tempfile
kutoka test.support agiza make_legacy_pyc
agiza unittest
agiza warnings


kundi FinderTests(abc.FinderTests):

    """For a top-level module, it should just be found directly kwenye the
    directory being searched. This ni true kila a directory ukijumuisha source
    [top-level source], bytecode [top-level bc], ama both [top-level both].
    There ni also the possibility that it ni a package [top-level package], kwenye
    which case there will be a directory ukijumuisha the module name na an
    __init__.py file. If there ni a directory without an __init__.py an
    ImportWarning ni returned [empty dir].

    For sub-modules na sub-packages, the same happens kama above but only use
    the tail end of the name [sub module] [sub package] [sub empty].

    When there ni a conflict between a package na module having the same name
    kwenye the same directory, the package wins out [package over module]. This is
    so that imports of modules within the package can occur rather than trigger
    an agiza error.

    When there ni a package na module ukijumuisha the same name, always pick the
    package over the module [package over module]. This ni so that imports from
    the package have the possibility of succeeding.

    """

    eleza get_finder(self, root):
        loader_details = [(self.machinery.SourceFileLoader,
                            self.machinery.SOURCE_SUFFIXES),
                          (self.machinery.SourcelessFileLoader,
                            self.machinery.BYTECODE_SUFFIXES)]
        rudisha self.machinery.FileFinder(root, *loader_details)

    eleza import_(self, root, module):
        finder = self.get_finder(root)
        rudisha self._find(finder, module, loader_only=Kweli)

    eleza run_test(self, test, create=Tupu, *, compile_=Tupu, unlink=Tupu):
        """Test the finding of 'test' ukijumuisha the creation of modules listed kwenye
        'create'.

        Any names listed kwenye 'compile_' are byte-compiled. Modules
        listed kwenye 'unlink' have their source files deleted.

        """
        ikiwa create ni Tupu:
            create = {test}
        ukijumuisha util.create_modules(*create) kama mapping:
            ikiwa compile_:
                kila name kwenye compile_:
                    py_compile.compile(mapping[name])
            ikiwa unlink:
                kila name kwenye unlink:
                    os.unlink(mapping[name])
                    jaribu:
                        make_legacy_pyc(mapping[name])
                    tatizo OSError kama error:
                        # Some tests do sio set compile_=Kweli so the source
                        # module will sio get compiled na there will be no
                        # PEP 3147 pyc file to rename.
                        ikiwa error.errno != errno.ENOENT:
                            raise
            loader = self.import_(mapping['.root'], test)
            self.assertKweli(hasattr(loader, 'load_module'))
            rudisha loader

    eleza test_module(self):
        # [top-level source]
        self.run_test('top_level')
        # [top-level bc]
        self.run_test('top_level', compile_={'top_level'},
                      unlink={'top_level'})
        # [top-level both]
        self.run_test('top_level', compile_={'top_level'})

    # [top-level package]
    eleza test_package(self):
        # Source.
        self.run_test('pkg', {'pkg.__init__'})
        # Bytecode.
        self.run_test('pkg', {'pkg.__init__'}, compile_={'pkg.__init__'},
                unlink={'pkg.__init__'})
        # Both.
        self.run_test('pkg', {'pkg.__init__'}, compile_={'pkg.__init__'})

    # [sub module]
    eleza test_module_in_package(self):
        ukijumuisha util.create_modules('pkg.__init__', 'pkg.sub') kama mapping:
            pkg_dir = os.path.dirname(mapping['pkg.__init__'])
            loader = self.import_(pkg_dir, 'pkg.sub')
            self.assertKweli(hasattr(loader, 'load_module'))

    # [sub package]
    eleza test_package_in_package(self):
        context = util.create_modules('pkg.__init__', 'pkg.sub.__init__')
        ukijumuisha context kama mapping:
            pkg_dir = os.path.dirname(mapping['pkg.__init__'])
            loader = self.import_(pkg_dir, 'pkg.sub')
            self.assertKweli(hasattr(loader, 'load_module'))

    # [package over modules]
    eleza test_package_over_module(self):
        name = '_temp'
        loader = self.run_test(name, {'{0}.__init__'.format(name), name})
        self.assertIn('__init__', loader.get_filename(name))

    eleza test_failure(self):
        ukijumuisha util.create_modules('blah') kama mapping:
            nothing = self.import_(mapping['.root'], 'sdfsadsadf')
            self.assertIsTupu(nothing)

    eleza test_empty_string_for_dir(self):
        # The empty string kutoka sys.path means to search kwenye the cwd.
        finder = self.machinery.FileFinder('', (self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))
        ukijumuisha open('mod.py', 'w') kama file:
            file.write("# test file kila importlib")
        jaribu:
            loader = self._find(finder, 'mod', loader_only=Kweli)
            self.assertKweli(hasattr(loader, 'load_module'))
        mwishowe:
            os.unlink('mod.py')

    eleza test_invalidate_caches(self):
        # invalidate_caches() should reset the mtime.
        finder = self.machinery.FileFinder('', (self.machinery.SourceFileLoader,
            self.machinery.SOURCE_SUFFIXES))
        finder._path_mtime = 42
        finder.invalidate_caches()
        self.assertEqual(finder._path_mtime, -1)

    # Regression test kila http://bugs.python.org/issue14846
    eleza test_dir_removal_handling(self):
        mod = 'mod'
        ukijumuisha util.create_modules(mod) kama mapping:
            finder = self.get_finder(mapping['.root'])
            found = self._find(finder, 'mod', loader_only=Kweli)
            self.assertIsNotTupu(found)
        found = self._find(finder, 'mod', loader_only=Kweli)
        self.assertIsTupu(found)

    @unittest.skipUnless(sys.platform != 'win32',
            'os.chmod() does sio support the needed arguments under Windows')
    eleza test_no_read_directory(self):
        # Issue #16730
        tempdir = tempfile.TemporaryDirectory()
        original_mode = os.stat(tempdir.name).st_mode
        eleza cleanup(tempdir):
            """Cleanup function kila the temporary directory.

            Since we muck ukijumuisha the permissions, we want to set them back to
            their original values to make sure the directory can be properly
            cleaned up.

            """
            os.chmod(tempdir.name, original_mode)
            # If this ni sio explicitly called then the __del__ method ni used,
            # but since already mucking around might kama well explicitly clean
            # up.
            tempdir.__exit__(Tupu, Tupu, Tupu)
        self.addCleanup(cleanup, tempdir)
        os.chmod(tempdir.name, stat.S_IWUSR | stat.S_IXUSR)
        finder = self.get_finder(tempdir.name)
        found = self._find(finder, 'doesnotexist')
        self.assertEqual(found, self.NOT_FOUND)

    eleza test_ignore_file(self):
        # If a directory got changed to a file kutoka underneath us, then don't
        # worry about looking kila submodules.
        ukijumuisha tempfile.NamedTemporaryFile() kama file_obj:
            finder = self.get_finder(file_obj.name)
            found = self._find(finder, 'doesnotexist')
            self.assertEqual(found, self.NOT_FOUND)


kundi FinderTestsPEP451(FinderTests):

    NOT_FOUND = Tupu

    eleza _find(self, finder, name, loader_only=Uongo):
        spec = finder.find_spec(name)
        rudisha spec.loader ikiwa spec ni sio Tupu isipokua spec


(Frozen_FinderTestsPEP451,
 Source_FinderTestsPEP451
 ) = util.test_both(FinderTestsPEP451, machinery=machinery)


kundi FinderTestsPEP420(FinderTests):

    NOT_FOUND = (Tupu, [])

    eleza _find(self, finder, name, loader_only=Uongo):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            loader_portions = finder.find_loader(name)
            rudisha loader_portions[0] ikiwa loader_only isipokua loader_portions


(Frozen_FinderTestsPEP420,
 Source_FinderTestsPEP420
 ) = util.test_both(FinderTestsPEP420, machinery=machinery)


kundi FinderTestsPEP302(FinderTests):

    NOT_FOUND = Tupu

    eleza _find(self, finder, name, loader_only=Uongo):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            rudisha finder.find_module(name)


(Frozen_FinderTestsPEP302,
 Source_FinderTestsPEP302
 ) = util.test_both(FinderTestsPEP302, machinery=machinery)


ikiwa __name__ == '__main__':
    unittest.main()
