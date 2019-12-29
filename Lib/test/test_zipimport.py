agiza sys
agiza os
agiza marshal
agiza importlib
agiza importlib.util
agiza struct
agiza time
agiza unittest

kutoka test agiza support

kutoka zipfile agiza ZipFile, ZipInfo, ZIP_STORED, ZIP_DEFLATED

agiza zipagiza
agiza linecache
agiza doctest
agiza inspect
agiza io
kutoka traceback agiza extract_tb, extract_stack, print_tb
jaribu:
    agiza zlib
tatizo ImportError:
    zlib = Tupu

test_src = """\
eleza get_name():
    rudisha __name__
eleza get_file():
    rudisha __file__
"""
test_co = compile(test_src, "<???>", "exec")
ashiria_src = 'eleza do_ashiria(): ashiria TypeError\n'

eleza make_pyc(co, mtime, size):
    data = marshal.dumps(co)
    ikiwa type(mtime) ni type(0.0):
        # Mac mtimes need a bit of special casing
        ikiwa mtime < 0x7fffffff:
            mtime = int(mtime)
        isipokua:
            mtime = int(-0x100000000 + int(mtime))
    pyc = (importlib.util.MAGIC_NUMBER +
        struct.pack("<iii", 0, int(mtime), size & 0xFFFFFFFF) + data)
    rudisha pyc

eleza module_path_to_dotted_name(path):
    rudisha path.replace(os.sep, '.')

NOW = time.time()
test_pyc = make_pyc(test_co, NOW, len(test_src))


TESTMOD = "ziptestmodule"
TESTPACK = "ziptestpackage"
TESTPACK2 = "ziptestpackage2"
TEMP_DIR = os.path.abspath("junk95142")
TEMP_ZIP = os.path.abspath("junk95142.zip")

pyc_file = importlib.util.cache_kutoka_source(TESTMOD + '.py')
pyc_ext = '.pyc'


kundi ImportHooksBaseTestCase(unittest.TestCase):

    eleza setUp(self):
        self.path = sys.path[:]
        self.meta_path = sys.meta_path[:]
        self.path_hooks = sys.path_hooks[:]
        sys.path_importer_cache.clear()
        self.modules_before = support.modules_setup()

    eleza tearDown(self):
        sys.path[:] = self.path
        sys.meta_path[:] = self.meta_path
        sys.path_hooks[:] = self.path_hooks
        sys.path_importer_cache.clear()
        support.modules_cleanup(*self.modules_before)


kundi UncompressedZipImportTestCase(ImportHooksBaseTestCase):

    compression = ZIP_STORED

    eleza setUp(self):
        # We're reusing the zip archive path, so we must clear the
        # cached directory info na linecache.
        linecache.clearcache()
        zipagiza._zip_directory_cache.clear()
        ImportHooksBaseTestCase.setUp(self)

    eleza makeTree(self, files, dirName=TEMP_DIR):
        # Create a filesystem based set of modules/packages
        # defined by files under the directory dirName.
        self.addCleanup(support.rmtree, dirName)

        kila name, (mtime, data) kwenye files.items():
            path = os.path.join(dirName, name)
            ikiwa path[-1] == os.sep:
                ikiwa sio os.path.isdir(path):
                    os.makedirs(path)
            isipokua:
                dname = os.path.dirname(path)
                ikiwa sio os.path.isdir(dname):
                    os.makedirs(dname)
                with open(path, 'wb') kama fp:
                    fp.write(data)

    eleza makeZip(self, files, zipName=TEMP_ZIP, **kw):
        # Create a zip archive based set of modules/packages
        # defined by files kwenye the zip file zipName.  If the
        # key 'stuff' exists kwenye kw it ni prepended to the archive.
        self.addCleanup(support.unlink, zipName)

        with ZipFile(zipName, "w") kama z:
            kila name, (mtime, data) kwenye files.items():
                zinfo = ZipInfo(name, time.localtime(mtime))
                zinfo.compress_type = self.compression
                z.writestr(zinfo, data)
            comment = kw.get("comment", Tupu)
            ikiwa comment ni sio Tupu:
                z.comment = comment

        stuff = kw.get("stuff", Tupu)
        ikiwa stuff ni sio Tupu:
            # Prepend 'stuff' to the start of the zipfile
            with open(zipName, "rb") kama f:
                data = f.read()
            with open(zipName, "wb") kama f:
                f.write(stuff)
                f.write(data)

    eleza doTest(self, expected_ext, files, *modules, **kw):
        self.makeZip(files, **kw)

        sys.path.insert(0, TEMP_ZIP)

        mod = importlib.import_module(".".join(modules))

        call = kw.get('call')
        ikiwa call ni sio Tupu:
            call(mod)

        ikiwa expected_ext:
            file = mod.get_file()
            self.assertEqual(file, os.path.join(TEMP_ZIP,
                                 *modules) + expected_ext)

    eleza testAFakeZlib(self):
        #
        # This could cause a stack overflow before: agizaing zlib.py
        # kutoka a compressed archive would cause zlib to be imported
        # which would find zlib.py kwenye the archive, which would... etc.
        #
        # This test *must* be executed first: it must be the first one
        # to trigger zipagiza to agiza zlib (zipagiza caches the
        # zlib.decompress function object, after which the problem being
        # tested here wouldn't be a problem anymore...
        # (Hence the 'A' kwenye the test method name: to make it the first
        # item kwenye a list sorted by name, like unittest.makeSuite() does.)
        #
        # This test fails on platforms on which the zlib module is
        # statically linked, but the problem it tests kila can't
        # occur kwenye that case (builtin modules are always found first),
        # so we'll simply skip it then. Bug #765456.
        #
        ikiwa "zlib" kwenye sys.builtin_module_names:
            self.skipTest('zlib ni a builtin module')
        ikiwa "zlib" kwenye sys.modules:
            toa sys.modules["zlib"]
        files = {"zlib.py": (NOW, test_src)}
        jaribu:
            self.doTest(".py", files, "zlib")
        tatizo ImportError:
            ikiwa self.compression != ZIP_DEFLATED:
                self.fail("expected test to sio ashiria ImportError")
        isipokua:
            ikiwa self.compression != ZIP_STORED:
                self.fail("expected test to ashiria ImportError")

    eleza testPy(self):
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD)

    eleza testPyc(self):
        files = {TESTMOD + pyc_ext: (NOW, test_pyc)}
        self.doTest(pyc_ext, files, TESTMOD)

    eleza testBoth(self):
        files = {TESTMOD + ".py": (NOW, test_src),
                 TESTMOD + pyc_ext: (NOW, test_pyc)}
        self.doTest(pyc_ext, files, TESTMOD)

    eleza testUncheckedHashBasedPyc(self):
        source = b"state = 'old'"
        source_hash = importlib.util.source_hash(source)
        bytecode = importlib._bootstrap_external._code_to_hash_pyc(
            compile(source, "???", "exec"),
            source_hash,
            Uongo, # unchecked
        )
        files = {TESTMOD + ".py": (NOW, "state = 'new'"),
                 TESTMOD + ".pyc": (NOW - 20, bytecode)}
        eleza check(mod):
            self.assertEqual(mod.state, 'old')
        self.doTest(Tupu, files, TESTMOD, call=check)

    eleza testEmptyPy(self):
        files = {TESTMOD + ".py": (NOW, "")}
        self.doTest(Tupu, files, TESTMOD)

    eleza testBadMagic(self):
        # make pyc magic word invalid, forcing loading kutoka .py
        badmagic_pyc = bytearray(test_pyc)
        badmagic_pyc[0] ^= 0x04  # flip an arbitrary bit
        files = {TESTMOD + ".py": (NOW, test_src),
                 TESTMOD + pyc_ext: (NOW, badmagic_pyc)}
        self.doTest(".py", files, TESTMOD)

    eleza testBadMagic2(self):
        # make pyc magic word invalid, causing an ImportError
        badmagic_pyc = bytearray(test_pyc)
        badmagic_pyc[0] ^= 0x04  # flip an arbitrary bit
        files = {TESTMOD + pyc_ext: (NOW, badmagic_pyc)}
        jaribu:
            self.doTest(".py", files, TESTMOD)
        tatizo ImportError:
            pita
        isipokua:
            self.fail("expected ImportError; agiza kutoka bad pyc")

    eleza testBadMTime(self):
        badtime_pyc = bytearray(test_pyc)
        # flip the second bit -- sio the first kama that one isn't stored kwenye the
        # .py's mtime kwenye the zip archive.
        badtime_pyc[11] ^= 0x02
        files = {TESTMOD + ".py": (NOW, test_src),
                 TESTMOD + pyc_ext: (NOW, badtime_pyc)}
        self.doTest(".py", files, TESTMOD)

    eleza testPackage(self):
        packdir = TESTPACK + os.sep
        files = {packdir + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir + TESTMOD + pyc_ext: (NOW, test_pyc)}
        self.doTest(pyc_ext, files, TESTPACK, TESTMOD)

    eleza testSubPackage(self):
        # Test that subpackages function when loaded kutoka zip
        # archives.
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        files = {packdir + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir2 + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}
        self.doTest(pyc_ext, files, TESTPACK, TESTPACK2, TESTMOD)

    eleza testSubNamespacePackage(self):
        # Test that implicit namespace subpackages function
        # when loaded kutoka zip archives.
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        # The first two files are just directory entries (so have no data).
        files = {packdir: (NOW, ""),
                 packdir2: (NOW, ""),
                 packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}
        self.doTest(pyc_ext, files, TESTPACK, TESTPACK2, TESTMOD)

    eleza testMixedNamespacePackage(self):
        # Test implicit namespace packages spread between a
        # real filesystem na a zip archive.
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        packdir3 = packdir2 + TESTPACK + '3' + os.sep
        files1 = {packdir: (NOW, ""),
                  packdir + TESTMOD + pyc_ext: (NOW, test_pyc),
                  packdir2: (NOW, ""),
                  packdir3: (NOW, ""),
                  packdir3 + TESTMOD + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + '3' + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}
        files2 = {packdir: (NOW, ""),
                  packdir + TESTMOD + '2' + pyc_ext: (NOW, test_pyc),
                  packdir2: (NOW, ""),
                  packdir2 + TESTMOD + '2' + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}

        zip1 = os.path.abspath("path1.zip")
        self.makeZip(files1, zip1)

        zip2 = TEMP_DIR
        self.makeTree(files2, zip2)

        # zip2 should override zip1.
        sys.path.insert(0, zip1)
        sys.path.insert(0, zip2)

        mod = importlib.import_module(TESTPACK)

        # ikiwa TESTPACK ni functioning kama a namespace pkg then
        # there should be two entries kwenye the __path__.
        # First should be path2 na second path1.
        self.assertEqual(2, len(mod.__path__))
        p1, p2 = mod.__path__
        self.assertEqual(os.path.basename(TEMP_DIR), p1.split(os.sep)[-2])
        self.assertEqual("path1.zip", p2.split(os.sep)[-2])

        # packdir3 should agiza kama a namespace package.
        # Its __path__ ni an iterable of 1 element kutoka zip1.
        mod = importlib.import_module(packdir3.replace(os.sep, '.')[:-1])
        self.assertEqual(1, len(mod.__path__))
        mpath = list(mod.__path__)[0].split('path1.zip' + os.sep)[1]
        self.assertEqual(packdir3[:-1], mpath)

        # TESTPACK/TESTMOD only exists kwenye path1.
        mod = importlib.import_module('.'.join((TESTPACK, TESTMOD)))
        self.assertEqual("path1.zip", mod.__file__.split(os.sep)[-3])

        # And TESTPACK/(TESTMOD + '2') only exists kwenye path2.
        mod = importlib.import_module('.'.join((TESTPACK, TESTMOD + '2')))
        self.assertEqual(os.path.basename(TEMP_DIR),
                         mod.__file__.split(os.sep)[-3])

        # One level deeper...
        subpkg = '.'.join((TESTPACK, TESTPACK2))
        mod = importlib.import_module(subpkg)
        self.assertEqual(2, len(mod.__path__))
        p1, p2 = mod.__path__
        self.assertEqual(os.path.basename(TEMP_DIR), p1.split(os.sep)[-3])
        self.assertEqual("path1.zip", p2.split(os.sep)[-3])

        # subpkg.TESTMOD exists kwenye both zips should load kutoka zip2.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD)))
        self.assertEqual(os.path.basename(TEMP_DIR),
                         mod.__file__.split(os.sep)[-4])

        # subpkg.TESTMOD + '2' only exists kwenye zip2.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD + '2')))
        self.assertEqual(os.path.basename(TEMP_DIR),
                         mod.__file__.split(os.sep)[-4])

        # Finally subpkg.TESTMOD + '3' only exists kwenye zip1.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD + '3')))
        self.assertEqual('path1.zip', mod.__file__.split(os.sep)[-4])

    eleza testNamespacePackage(self):
        # Test implicit namespace packages spread between multiple zip
        # archives.
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        packdir3 = packdir2 + TESTPACK + '3' + os.sep
        files1 = {packdir: (NOW, ""),
                  packdir + TESTMOD + pyc_ext: (NOW, test_pyc),
                  packdir2: (NOW, ""),
                  packdir3: (NOW, ""),
                  packdir3 + TESTMOD + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + '3' + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}
        zip1 = os.path.abspath("path1.zip")
        self.makeZip(files1, zip1)

        files2 = {packdir: (NOW, ""),
                  packdir + TESTMOD + '2' + pyc_ext: (NOW, test_pyc),
                  packdir2: (NOW, ""),
                  packdir2 + TESTMOD + '2' + pyc_ext: (NOW, test_pyc),
                  packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}
        zip2 = os.path.abspath("path2.zip")
        self.makeZip(files2, zip2)

        # zip2 should override zip1.
        sys.path.insert(0, zip1)
        sys.path.insert(0, zip2)

        mod = importlib.import_module(TESTPACK)

        # ikiwa TESTPACK ni functioning kama a namespace pkg then
        # there should be two entries kwenye the __path__.
        # First should be path2 na second path1.
        self.assertEqual(2, len(mod.__path__))
        p1, p2 = mod.__path__
        self.assertEqual("path2.zip", p1.split(os.sep)[-2])
        self.assertEqual("path1.zip", p2.split(os.sep)[-2])

        # packdir3 should agiza kama a namespace package.
        # Tts __path__ ni an iterable of 1 element kutoka zip1.
        mod = importlib.import_module(packdir3.replace(os.sep, '.')[:-1])
        self.assertEqual(1, len(mod.__path__))
        mpath = list(mod.__path__)[0].split('path1.zip' + os.sep)[1]
        self.assertEqual(packdir3[:-1], mpath)

        # TESTPACK/TESTMOD only exists kwenye path1.
        mod = importlib.import_module('.'.join((TESTPACK, TESTMOD)))
        self.assertEqual("path1.zip", mod.__file__.split(os.sep)[-3])

        # And TESTPACK/(TESTMOD + '2') only exists kwenye path2.
        mod = importlib.import_module('.'.join((TESTPACK, TESTMOD + '2')))
        self.assertEqual("path2.zip", mod.__file__.split(os.sep)[-3])

        # One level deeper...
        subpkg = '.'.join((TESTPACK, TESTPACK2))
        mod = importlib.import_module(subpkg)
        self.assertEqual(2, len(mod.__path__))
        p1, p2 = mod.__path__
        self.assertEqual("path2.zip", p1.split(os.sep)[-3])
        self.assertEqual("path1.zip", p2.split(os.sep)[-3])

        # subpkg.TESTMOD exists kwenye both zips should load kutoka zip2.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD)))
        self.assertEqual('path2.zip', mod.__file__.split(os.sep)[-4])

        # subpkg.TESTMOD + '2' only exists kwenye zip2.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD + '2')))
        self.assertEqual('path2.zip', mod.__file__.split(os.sep)[-4])

        # Finally subpkg.TESTMOD + '3' only exists kwenye zip1.
        mod = importlib.import_module('.'.join((subpkg, TESTMOD + '3')))
        self.assertEqual('path1.zip', mod.__file__.split(os.sep)[-4])

    eleza testZipImporterMethods(self):
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        files = {packdir + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir2 + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc),
                 "spam" + pyc_ext: (NOW, test_pyc)}

        self.addCleanup(support.unlink, TEMP_ZIP)
        with ZipFile(TEMP_ZIP, "w") kama z:
            kila name, (mtime, data) kwenye files.items():
                zinfo = ZipInfo(name, time.localtime(mtime))
                zinfo.compress_type = self.compression
                zinfo.comment = b"spam"
                z.writestr(zinfo, data)

        zi = zipagiza.zipimporter(TEMP_ZIP)
        self.assertEqual(zi.archive, TEMP_ZIP)
        self.assertEqual(zi.is_package(TESTPACK), Kweli)

        find_mod = zi.find_module('spam')
        self.assertIsNotTupu(find_mod)
        self.assertIsInstance(find_mod, zipagiza.zipimporter)
        self.assertUongo(find_mod.is_package('spam'))
        load_mod = find_mod.load_module('spam')
        self.assertEqual(find_mod.get_filename('spam'), load_mod.__file__)

        mod = zi.load_module(TESTPACK)
        self.assertEqual(zi.get_filename(TESTPACK), mod.__file__)

        existing_pack_path = importlib.import_module(TESTPACK).__path__[0]
        expected_path_path = os.path.join(TEMP_ZIP, TESTPACK)
        self.assertEqual(existing_pack_path, expected_path_path)

        self.assertEqual(zi.is_package(packdir + '__init__'), Uongo)
        self.assertEqual(zi.is_package(packdir + TESTPACK2), Kweli)
        self.assertEqual(zi.is_package(packdir2 + TESTMOD), Uongo)

        mod_path = packdir2 + TESTMOD
        mod_name = module_path_to_dotted_name(mod_path)
        mod = importlib.import_module(mod_name)
        self.assertKweli(mod_name kwenye sys.modules)
        self.assertEqual(zi.get_source(TESTPACK), Tupu)
        self.assertEqual(zi.get_source(mod_path), Tupu)
        self.assertEqual(zi.get_filename(mod_path), mod.__file__)
        # To pita kwenye the module name instead of the path, we must use the
        # right importer
        loader = mod.__loader__
        self.assertEqual(loader.get_source(mod_name), Tupu)
        self.assertEqual(loader.get_filename(mod_name), mod.__file__)

        # test prefix na archivepath members
        zi2 = zipagiza.zipimporter(TEMP_ZIP + os.sep + TESTPACK)
        self.assertEqual(zi2.archive, TEMP_ZIP)
        self.assertEqual(zi2.prefix, TESTPACK + os.sep)

    eleza testZipImporterMethodsInSubDirectory(self):
        packdir = TESTPACK + os.sep
        packdir2 = packdir + TESTPACK2 + os.sep
        files = {packdir2 + "__init__" + pyc_ext: (NOW, test_pyc),
                 packdir2 + TESTMOD + pyc_ext: (NOW, test_pyc)}

        self.addCleanup(support.unlink, TEMP_ZIP)
        with ZipFile(TEMP_ZIP, "w") kama z:
            kila name, (mtime, data) kwenye files.items():
                zinfo = ZipInfo(name, time.localtime(mtime))
                zinfo.compress_type = self.compression
                zinfo.comment = b"eggs"
                z.writestr(zinfo, data)

        zi = zipagiza.zipimporter(TEMP_ZIP + os.sep + packdir)
        self.assertEqual(zi.archive, TEMP_ZIP)
        self.assertEqual(zi.prefix, packdir)
        self.assertEqual(zi.is_package(TESTPACK2), Kweli)
        mod = zi.load_module(TESTPACK2)
        self.assertEqual(zi.get_filename(TESTPACK2), mod.__file__)

        self.assertEqual(
            zi.is_package(TESTPACK2 + os.sep + '__init__'), Uongo)
        self.assertEqual(
            zi.is_package(TESTPACK2 + os.sep + TESTMOD), Uongo)

        pkg_path = TEMP_ZIP + os.sep + packdir + TESTPACK2
        zi2 = zipagiza.zipimporter(pkg_path)
        find_mod_dotted = zi2.find_module(TESTMOD)
        self.assertIsNotTupu(find_mod_dotted)
        self.assertIsInstance(find_mod_dotted, zipagiza.zipimporter)
        self.assertUongo(zi2.is_package(TESTMOD))
        load_mod = find_mod_dotted.load_module(TESTMOD)
        self.assertEqual(
            find_mod_dotted.get_filename(TESTMOD), load_mod.__file__)

        mod_path = TESTPACK2 + os.sep + TESTMOD
        mod_name = module_path_to_dotted_name(mod_path)
        mod = importlib.import_module(mod_name)
        self.assertKweli(mod_name kwenye sys.modules)
        self.assertEqual(zi.get_source(TESTPACK2), Tupu)
        self.assertEqual(zi.get_source(mod_path), Tupu)
        self.assertEqual(zi.get_filename(mod_path), mod.__file__)
        # To pita kwenye the module name instead of the path, we must use the
        # right importer.
        loader = mod.__loader__
        self.assertEqual(loader.get_source(mod_name), Tupu)
        self.assertEqual(loader.get_filename(mod_name), mod.__file__)

    eleza testGetData(self):
        self.addCleanup(support.unlink, TEMP_ZIP)
        with ZipFile(TEMP_ZIP, "w") kama z:
            z.compression = self.compression
            name = "testdata.dat"
            data = bytes(x kila x kwenye range(256))
            z.writestr(name, data)

        zi = zipagiza.zipimporter(TEMP_ZIP)
        self.assertEqual(data, zi.get_data(name))
        self.assertIn('zipimporter object', repr(zi))

    eleza testImporterAttr(self):
        src = """ikiwa 1:  # indent hack
        eleza get_file():
            rudisha __file__
        ikiwa __loader__.get_data("some.data") != b"some data":
            ashiria AssertionError("bad data")\n"""
        pyc = make_pyc(compile(src, "<???>", "exec"), NOW, len(src))
        files = {TESTMOD + pyc_ext: (NOW, pyc),
                 "some.data": (NOW, "some data")}
        self.doTest(pyc_ext, files, TESTMOD)

    eleza testDefaultOptimizationLevel(self):
        # zipagiza should use the default optimization level (#28131)
        src = """ikiwa 1:  # indent hack
        eleza test(val):
            assert(val)
            rudisha val\n"""
        files = {TESTMOD + '.py': (NOW, src)}
        self.makeZip(files)
        sys.path.insert(0, TEMP_ZIP)
        mod = importlib.import_module(TESTMOD)
        self.assertEqual(mod.test(1), 1)
        self.assertRaises(AssertionError, mod.test, Uongo)

    eleza testImport_WithStuff(self):
        # try agizaing kutoka a zipfile which contains additional
        # stuff at the beginning of the file
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD,
                    stuff=b"Some Stuff"*31)

    eleza assertModuleSource(self, module):
        self.assertEqual(inspect.getsource(module), test_src)

    eleza testGetSource(self):
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD, call=self.assertModuleSource)

    eleza testGetCompiledSource(self):
        pyc = make_pyc(compile(test_src, "<???>", "exec"), NOW, len(test_src))
        files = {TESTMOD + ".py": (NOW, test_src),
                 TESTMOD + pyc_ext: (NOW, pyc)}
        self.doTest(pyc_ext, files, TESTMOD, call=self.assertModuleSource)

    eleza runDoctest(self, callback):
        files = {TESTMOD + ".py": (NOW, test_src),
                 "xyz.txt": (NOW, ">>> log.append(Kweli)\n")}
        self.doTest(".py", files, TESTMOD, call=callback)

    eleza doDoctestFile(self, module):
        log = []
        old_master, doctest.master = doctest.master, Tupu
        jaribu:
            doctest.testfile(
                'xyz.txt', package=module, module_relative=Kweli,
                globs=locals()
            )
        mwishowe:
            doctest.master = old_master
        self.assertEqual(log,[Kweli])

    eleza testDoctestFile(self):
        self.runDoctest(self.doDoctestFile)

    eleza doDoctestSuite(self, module):
        log = []
        doctest.DocFileTest(
            'xyz.txt', package=module, module_relative=Kweli,
            globs=locals()
        ).run()
        self.assertEqual(log,[Kweli])

    eleza testDoctestSuite(self):
        self.runDoctest(self.doDoctestSuite)

    eleza doTraceback(self, module):
        jaribu:
            module.do_ashiria()
        except:
            tb = sys.exc_info()[2].tb_next

            f,lno,n,line = extract_tb(tb, 1)[0]
            self.assertEqual(line, ashiria_src.strip())

            f,lno,n,line = extract_stack(tb.tb_frame, 1)[0]
            self.assertEqual(line, ashiria_src.strip())

            s = io.StringIO()
            print_tb(tb, 1, s)
            self.assertKweli(s.getvalue().endswith(ashiria_src))
        isipokua:
            ashiria AssertionError("This ought to be impossible")

    eleza testTraceback(self):
        files = {TESTMOD + ".py": (NOW, ashiria_src)}
        self.doTest(Tupu, files, TESTMOD, call=self.doTraceback)

    @unittest.skipIf(support.TESTFN_UNENCODABLE ni Tupu,
                     "need an unencodable filename")
    eleza testUnencodable(self):
        filename = support.TESTFN_UNENCODABLE + ".zip"
        self.addCleanup(support.unlink, filename)
        with ZipFile(filename, "w") kama z:
            zinfo = ZipInfo(TESTMOD + ".py", time.localtime(NOW))
            zinfo.compress_type = self.compression
            z.writestr(zinfo, test_src)
        zipagiza.zipimporter(filename).load_module(TESTMOD)

    eleza testBytesPath(self):
        filename = support.TESTFN + ".zip"
        self.addCleanup(support.unlink, filename)
        with ZipFile(filename, "w") kama z:
            zinfo = ZipInfo(TESTMOD + ".py", time.localtime(NOW))
            zinfo.compress_type = self.compression
            z.writestr(zinfo, test_src)

        zipagiza.zipimporter(filename)
        zipagiza.zipimporter(os.fsencode(filename))
        with self.assertRaises(TypeError):
            zipagiza.zipimporter(bytearray(os.fsencode(filename)))
        with self.assertRaises(TypeError):
            zipagiza.zipimporter(memoryview(os.fsencode(filename)))

    eleza testComment(self):
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD, comment=b"comment")

    eleza testBeginningCruftAndComment(self):
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD, stuff=b"cruft" * 64, comment=b"hi")

    eleza testLargestPossibleComment(self):
        files = {TESTMOD + ".py": (NOW, test_src)}
        self.doTest(".py", files, TESTMOD, comment=b"c" * ((1 << 16) - 1))


@support.requires_zlib
kundi CompressedZipImportTestCase(UncompressedZipImportTestCase):
    compression = ZIP_DEFLATED


kundi BadFileZipImportTestCase(unittest.TestCase):
    eleza assertZipFailure(self, filename):
        self.assertRaises(zipagiza.ZipImportError,
                          zipagiza.zipimporter, filename)

    eleza testNoFile(self):
        self.assertZipFailure('AdfjdkFJKDFJjdklfjs')

    eleza testEmptyFilename(self):
        self.assertZipFailure('')

    eleza testBadArgs(self):
        self.assertRaises(TypeError, zipagiza.zipimporter, Tupu)
        self.assertRaises(TypeError, zipagiza.zipimporter, TESTMOD, kwd=Tupu)
        self.assertRaises(TypeError, zipagiza.zipimporter,
                          list(os.fsencode(TESTMOD)))

    eleza testFilenameTooLong(self):
        self.assertZipFailure('A' * 33000)

    eleza testEmptyFile(self):
        support.unlink(TESTMOD)
        support.create_empty_file(TESTMOD)
        self.assertZipFailure(TESTMOD)

    eleza testFileUnreadable(self):
        support.unlink(TESTMOD)
        fd = os.open(TESTMOD, os.O_CREAT, 000)
        jaribu:
            os.close(fd)

            with self.assertRaises(zipagiza.ZipImportError) kama cm:
                zipagiza.zipimporter(TESTMOD)
        mwishowe:
            # If we leave "the read-only bit" set on Windows, nothing can
            # delete TESTMOD, na later tests suffer bogus failures.
            os.chmod(TESTMOD, 0o666)
            support.unlink(TESTMOD)

    eleza testNotZipFile(self):
        support.unlink(TESTMOD)
        fp = open(TESTMOD, 'w+')
        fp.write('a' * 22)
        fp.close()
        self.assertZipFailure(TESTMOD)

    # XXX: disabled until this works on Big-endian machines
    eleza _testBogusZipFile(self):
        support.unlink(TESTMOD)
        fp = open(TESTMOD, 'w+')
        fp.write(struct.pack('=I', 0x06054B50))
        fp.write('a' * 18)
        fp.close()
        z = zipagiza.zipimporter(TESTMOD)

        jaribu:
            self.assertRaises(TypeError, z.find_module, Tupu)
            self.assertRaises(TypeError, z.load_module, Tupu)
            self.assertRaises(TypeError, z.is_package, Tupu)
            self.assertRaises(TypeError, z.get_code, Tupu)
            self.assertRaises(TypeError, z.get_data, Tupu)
            self.assertRaises(TypeError, z.get_source, Tupu)

            error = zipagiza.ZipImportError
            self.assertEqual(z.find_module('abc'), Tupu)

            self.assertRaises(error, z.load_module, 'abc')
            self.assertRaises(error, z.get_code, 'abc')
            self.assertRaises(OSError, z.get_data, 'abc')
            self.assertRaises(error, z.get_source, 'abc')
            self.assertRaises(error, z.is_package, 'abc')
        mwishowe:
            zipagiza._zip_directory_cache.clear()


eleza test_main():
    jaribu:
        support.run_unittest(
              UncompressedZipImportTestCase,
              CompressedZipImportTestCase,
              BadFileZipImportTestCase,
            )
    mwishowe:
        support.unlink(TESTMOD)

ikiwa __name__ == "__main__":
    test_main()
