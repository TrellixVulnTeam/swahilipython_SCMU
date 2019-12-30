kutoka .. agiza abc
kutoka .. agiza util

importlib = util.import_importlib('importlib')
importlib_abc = util.import_importlib('importlib.abc')
machinery = util.import_importlib('importlib.machinery')
importlib_util = util.import_importlib('importlib.util')

agiza errno
agiza marshal
agiza os
agiza py_compile
agiza shutil
agiza stat
agiza sys
agiza types
agiza unittest
agiza warnings

kutoka test.support agiza make_legacy_pyc, unload

kutoka test.test_py_compile agiza without_source_date_epoch
kutoka test.test_py_compile agiza SourceDateEpochTestMeta


kundi SimpleTest(abc.LoaderTests):

    """Should have no issue agizaing a source module [basic]. And ikiwa there is
    a syntax error, it should ashiria a SyntaxError [syntax error].

    """

    eleza setUp(self):
        self.name = 'spam'
        self.filepath = os.path.join('ham', self.name + '.py')
        self.loader = self.machinery.SourceFileLoader(self.name, self.filepath)

    eleza test_load_module_API(self):
        kundi Tester(self.abc.FileLoader):
            eleza get_source(self, _): rudisha 'attr = 42'
            eleza is_package(self, _): rudisha Uongo

        loader = Tester('blah', 'blah.py')
        self.addCleanup(unload, 'blah')
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            module = loader.load_module()  # Should sio ashiria an exception.

    eleza test_get_filename_API(self):
        # If fullname ni sio set then assume self.path ni desired.
        kundi Tester(self.abc.FileLoader):
            eleza get_code(self, _): pita
            eleza get_source(self, _): pita
            eleza is_package(self, _): pita
            eleza module_repr(self, _): pita

        path = 'some_path'
        name = 'some_name'
        loader = Tester(name, path)
        self.assertEqual(path, loader.get_filename(name))
        self.assertEqual(path, loader.get_filename())
        self.assertEqual(path, loader.get_filename(Tupu))
        ukijumuisha self.assertRaises(ImportError):
            loader.get_filename(name + 'XXX')

    eleza test_equality(self):
        other = self.machinery.SourceFileLoader(self.name, self.filepath)
        self.assertEqual(self.loader, other)

    eleza test_inequality(self):
        other = self.machinery.SourceFileLoader('_' + self.name, self.filepath)
        self.assertNotEqual(self.loader, other)

    # [basic]
    eleza test_module(self):
        ukijumuisha util.create_modules('_temp') kama mapping:
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            self.assertIn('_temp', sys.modules)
            check = {'__name__': '_temp', '__file__': mapping['_temp'],
                     '__package__': ''}
            kila attr, value kwenye check.items():
                self.assertEqual(getattr(module, attr), value)

    eleza test_package(self):
        ukijumuisha util.create_modules('_pkg.__init__') kama mapping:
            loader = self.machinery.SourceFileLoader('_pkg',
                                                 mapping['_pkg.__init__'])
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_pkg')
            self.assertIn('_pkg', sys.modules)
            check = {'__name__': '_pkg', '__file__': mapping['_pkg.__init__'],
                     '__path__': [os.path.dirname(mapping['_pkg.__init__'])],
                     '__package__': '_pkg'}
            kila attr, value kwenye check.items():
                self.assertEqual(getattr(module, attr), value)


    eleza test_lacking_parent(self):
        ukijumuisha util.create_modules('_pkg.__init__', '_pkg.mod')as mapping:
            loader = self.machinery.SourceFileLoader('_pkg.mod',
                                                    mapping['_pkg.mod'])
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_pkg.mod')
            self.assertIn('_pkg.mod', sys.modules)
            check = {'__name__': '_pkg.mod', '__file__': mapping['_pkg.mod'],
                     '__package__': '_pkg'}
            kila attr, value kwenye check.items():
                self.assertEqual(getattr(module, attr), value)

    eleza fake_mtime(self, fxn):
        """Fake mtime to always be higher than expected."""
        rudisha lambda name: fxn(name) + 1

    eleza test_module_reuse(self):
        ukijumuisha util.create_modules('_temp') kama mapping:
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            module_id = id(module)
            module_dict_id = id(module.__dict__)
            ukijumuisha open(mapping['_temp'], 'w') kama file:
                file.write("testing_var = 42\n")
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = loader.load_module('_temp')
            self.assertIn('testing_var', module.__dict__,
                         "'testing_var' haiko kwenye "
                            "{0}".format(list(module.__dict__.keys())))
            self.assertEqual(module, sys.modules['_temp'])
            self.assertEqual(id(module), module_id)
            self.assertEqual(id(module.__dict__), module_dict_id)

    eleza test_state_after_failure(self):
        # A failed reload should leave the original module intact.
        attributes = ('__file__', '__path__', '__package__')
        value = '<test>'
        name = '_temp'
        ukijumuisha util.create_modules(name) kama mapping:
            orig_module = types.ModuleType(name)
            kila attr kwenye attributes:
                setattr(orig_module, attr, value)
            ukijumuisha open(mapping[name], 'w') kama file:
                file.write('+++ bad syntax +++')
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            ukijumuisha self.assertRaises(SyntaxError):
                loader.exec_module(orig_module)
            kila attr kwenye attributes:
                self.assertEqual(getattr(orig_module, attr), value)
            ukijumuisha self.assertRaises(SyntaxError):
                ukijumuisha warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    loader.load_module(name)
            kila attr kwenye attributes:
                self.assertEqual(getattr(orig_module, attr), value)

    # [syntax error]
    eleza test_bad_syntax(self):
        ukijumuisha util.create_modules('_temp') kama mapping:
            ukijumuisha open(mapping['_temp'], 'w') kama file:
                file.write('=')
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            ukijumuisha self.assertRaises(SyntaxError):
                ukijumuisha warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    loader.load_module('_temp')
            self.assertNotIn('_temp', sys.modules)

    eleza test_file_from_empty_string_dir(self):
        # Loading a module found kutoka an empty string entry on sys.path should
        # sio only work, but keep all attributes relative.
        file_path = '_temp.py'
        ukijumuisha open(file_path, 'w') kama file:
            file.write("# test file kila importlib")
        jaribu:
            ukijumuisha util.uncache('_temp'):
                loader = self.machinery.SourceFileLoader('_temp', file_path)
                ukijumuisha warnings.catch_warnings():
                    warnings.simplefilter('ignore', DeprecationWarning)
                    mod = loader.load_module('_temp')
                self.assertEqual(file_path, mod.__file__)
                self.assertEqual(self.util.cache_from_source(file_path),
                                 mod.__cached__)
        mwishowe:
            os.unlink(file_path)
            pycache = os.path.dirname(self.util.cache_from_source(file_path))
            ikiwa os.path.exists(pycache):
                shutil.rmtree(pycache)

    @util.writes_bytecode_files
    eleza test_timestamp_overflow(self):
        # When a modification timestamp ni larger than 2**32, it should be
        # truncated rather than ashiria an OverflowError.
        ukijumuisha util.create_modules('_temp') kama mapping:
            source = mapping['_temp']
            compiled = self.util.cache_from_source(source)
            ukijumuisha open(source, 'w') kama f:
                f.write("x = 5")
            jaribu:
                os.utime(source, (2 ** 33 - 5, 2 ** 33 - 5))
            tatizo OverflowError:
                self.skipTest("cannot set modification time to large integer")
            tatizo OSError kama e:
                ikiwa e.errno != getattr(errno, 'EOVERFLOW', Tupu):
                    ashiria
                self.skipTest("cannot set modification time to large integer ({})".format(e))
            loader = self.machinery.SourceFileLoader('_temp', mapping['_temp'])
            # PEP 451
            module = types.ModuleType('_temp')
            module.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(module)
            self.assertEqual(module.x, 5)
            self.assertKweli(os.path.exists(compiled))
            os.unlink(compiled)
            # PEP 302
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                mod = loader.load_module('_temp')
            # Sanity checks.
            self.assertEqual(mod.__cached__, compiled)
            self.assertEqual(mod.x, 5)
            # The pyc file was created.
            self.assertKweli(os.path.exists(compiled))

    eleza test_unloadable(self):
        loader = self.machinery.SourceFileLoader('good name', {})
        module = types.ModuleType('bad name')
        module.__spec__ = self.machinery.ModuleSpec('bad name', loader)
        ukijumuisha self.assertRaises(ImportError):
            loader.exec_module(module)
        ukijumuisha self.assertRaises(ImportError):
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                loader.load_module('bad name')

    @util.writes_bytecode_files
    eleza test_checked_hash_based_pyc(self):
        ukijumuisha util.create_modules('_temp') kama mapping:
            source = mapping['_temp']
            pyc = self.util.cache_from_source(source)
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "old"')
            os.utime(source, (50, 50))
            py_compile.compile(
                source,
                invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
            )
            loader = self.machinery.SourceFileLoader('_temp', source)
            mod = types.ModuleType('_temp')
            mod.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')
            # Write a new source ukijumuisha the same mtime na size kama before.
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "new"')
            os.utime(source, (50, 50))
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'new')
            ukijumuisha open(pyc, 'rb') kama fp:
                data = fp.read()
            self.assertEqual(int.kutoka_bytes(data[4:8], 'little'), 0b11)
            self.assertEqual(
                self.util.source_hash(b'state = "new"'),
                data[8:16],
            )

    @util.writes_bytecode_files
    eleza test_overridden_checked_hash_based_pyc(self):
        ukijumuisha util.create_modules('_temp') kama mapping, \
             unittest.mock.patch('_imp.check_hash_based_pycs', 'never'):
            source = mapping['_temp']
            pyc = self.util.cache_from_source(source)
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "old"')
            os.utime(source, (50, 50))
            py_compile.compile(
                source,
                invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
            )
            loader = self.machinery.SourceFileLoader('_temp', source)
            mod = types.ModuleType('_temp')
            mod.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')
            # Write a new source ukijumuisha the same mtime na size kama before.
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "new"')
            os.utime(source, (50, 50))
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')

    @util.writes_bytecode_files
    eleza test_unchecked_hash_based_pyc(self):
        ukijumuisha util.create_modules('_temp') kama mapping:
            source = mapping['_temp']
            pyc = self.util.cache_from_source(source)
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "old"')
            os.utime(source, (50, 50))
            py_compile.compile(
                source,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            loader = self.machinery.SourceFileLoader('_temp', source)
            mod = types.ModuleType('_temp')
            mod.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')
            # Update the source file, which should be ignored.
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "new"')
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')
            ukijumuisha open(pyc, 'rb') kama fp:
                data = fp.read()
            self.assertEqual(int.kutoka_bytes(data[4:8], 'little'), 0b1)
            self.assertEqual(
                self.util.source_hash(b'state = "old"'),
                data[8:16],
            )

    @util.writes_bytecode_files
    eleza test_overridden_unchecked_hash_based_pyc(self):
        ukijumuisha util.create_modules('_temp') kama mapping, \
             unittest.mock.patch('_imp.check_hash_based_pycs', 'always'):
            source = mapping['_temp']
            pyc = self.util.cache_from_source(source)
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "old"')
            os.utime(source, (50, 50))
            py_compile.compile(
                source,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            loader = self.machinery.SourceFileLoader('_temp', source)
            mod = types.ModuleType('_temp')
            mod.__spec__ = self.util.spec_from_loader('_temp', loader)
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'old')
            # Update the source file, which should be ignored.
            ukijumuisha open(source, 'wb') kama fp:
                fp.write(b'state = "new"')
            loader.exec_module(mod)
            self.assertEqual(mod.state, 'new')
            ukijumuisha open(pyc, 'rb') kama fp:
                data = fp.read()
            self.assertEqual(int.kutoka_bytes(data[4:8], 'little'), 0b1)
            self.assertEqual(
                self.util.source_hash(b'state = "new"'),
                data[8:16],
            )


(Frozen_SimpleTest,
 Source_SimpleTest
 ) = util.test_both(SimpleTest, importlib=importlib, machinery=machinery,
                    abc=importlib_abc, util=importlib_util)


kundi SourceDateEpochTestMeta(SourceDateEpochTestMeta,
                              type(Source_SimpleTest)):
    pita


kundi SourceDateEpoch_SimpleTest(Source_SimpleTest,
                                 metaclass=SourceDateEpochTestMeta,
                                 source_date_epoch=Kweli):
    pita


kundi BadBytecodeTest:

    eleza import_(self, file, module_name):
        ashiria NotImplementedError

    eleza manipulate_bytecode(self,
                            name, mapping, manipulator, *,
                            del_source=Uongo,
                            invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP):
        """Manipulate the bytecode of a module by pitaing it into a callable
        that rudishas what to use kama the new bytecode."""
        jaribu:
            toa sys.modules['_temp']
        tatizo KeyError:
            pita
        py_compile.compile(mapping[name], invalidation_mode=invalidation_mode)
        ikiwa sio del_source:
            bytecode_path = self.util.cache_from_source(mapping[name])
        isipokua:
            os.unlink(mapping[name])
            bytecode_path = make_legacy_pyc(mapping[name])
        ikiwa manipulator:
            ukijumuisha open(bytecode_path, 'rb') kama file:
                bc = file.read()
                new_bc = manipulator(bc)
            ukijumuisha open(bytecode_path, 'wb') kama file:
                ikiwa new_bc ni sio Tupu:
                    file.write(new_bc)
        rudisha bytecode_path

    eleza _test_empty_file(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: b'',
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    @util.writes_bytecode_files
    eleza _test_partial_magic(self, test, *, del_source=Uongo):
        # When their are less than 4 bytes to a .pyc, regenerate it if
        # possible, isipokua ashiria ImportError.
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:3],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    eleza _test_magic_only(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:4],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    eleza _test_partial_flags(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                               lambda bc: bc[:7],
                                               del_source=del_source)
            test('_temp', mapping, bc_path)

    eleza _test_partial_hash(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode(
                '_temp',
                mapping,
                lambda bc: bc[:13],
                del_source=del_source,
                invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
            )
            test('_temp', mapping, bc_path)
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode(
                '_temp',
                mapping,
                lambda bc: bc[:13],
                del_source=del_source,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            test('_temp', mapping, bc_path)

    eleza _test_partial_timestamp(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:11],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    eleza _test_partial_size(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:15],
                                                del_source=del_source)
            test('_temp', mapping, bc_path)

    eleza _test_no_marshal(self, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:16],
                                                del_source=del_source)
            file_path = mapping['_temp'] ikiwa sio del_source isipokua bc_path
            ukijumuisha self.assertRaises(EOFError):
                self.import_(file_path, '_temp')

    eleza _test_non_code_marshal(self, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bytecode_path = self.manipulate_bytecode('_temp', mapping,
                                    lambda bc: bc[:16] + marshal.dumps(b'abcd'),
                                    del_source=del_source)
            file_path = mapping['_temp'] ikiwa sio del_source isipokua bytecode_path
            ukijumuisha self.assertRaises(ImportError) kama cm:
                self.import_(file_path, '_temp')
            self.assertEqual(cm.exception.name, '_temp')
            self.assertEqual(cm.exception.path, bytecode_path)

    eleza _test_bad_marshal(self, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bytecode_path = self.manipulate_bytecode('_temp', mapping,
                                                lambda bc: bc[:16] + b'<test>',
                                                del_source=del_source)
            file_path = mapping['_temp'] ikiwa sio del_source isipokua bytecode_path
            ukijumuisha self.assertRaises(EOFError):
                self.import_(file_path, '_temp')

    eleza _test_bad_magic(self, test, *, del_source=Uongo):
        ukijumuisha util.create_modules('_temp') kama mapping:
            bc_path = self.manipulate_bytecode('_temp', mapping,
                                    lambda bc: b'\x00\x00\x00\x00' + bc[4:])
            test('_temp', mapping, bc_path)


kundi BadBytecodeTestPEP451(BadBytecodeTest):

    eleza import_(self, file, module_name):
        loader = self.loader(module_name, file)
        module = types.ModuleType(module_name)
        module.__spec__ = self.util.spec_from_loader(module_name, loader)
        loader.exec_module(module)


kundi BadBytecodeTestPEP302(BadBytecodeTest):

    eleza import_(self, file, module_name):
        loader = self.loader(module_name, file)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            module = loader.load_module(module_name)
        self.assertIn(module_name, sys.modules)


kundi SourceLoaderBadBytecodeTest:

    @classmethod
    eleza setUpClass(cls):
        cls.loader = cls.machinery.SourceFileLoader

    @util.writes_bytecode_files
    eleza test_empty_file(self):
        # When a .pyc ni empty, regenerate it ikiwa possible, isipokua ashiria
        # ImportError.
        eleza test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bytecode_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_empty_file(test)

    eleza test_partial_magic(self):
        eleza test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bytecode_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_partial_magic(test)

    @util.writes_bytecode_files
    eleza test_magic_only(self):
        # When there ni only the magic number, regenerate the .pyc ikiwa possible,
        # isipokua ashiria EOFError.
        eleza test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bytecode_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_magic_only(test)

    @util.writes_bytecode_files
    eleza test_bad_magic(self):
        # When the magic number ni different, the bytecode should be
        # regenerated.
        eleza test(name, mapping, bytecode_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bytecode_path, 'rb') kama bytecode_file:
                self.assertEqual(bytecode_file.read(4),
                                 self.util.MAGIC_NUMBER)

        self._test_bad_magic(test)

    @util.writes_bytecode_files
    eleza test_partial_timestamp(self):
        # When the timestamp ni partial, regenerate the .pyc, ama
        # ashiria EOFError.
        eleza test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bc_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_partial_timestamp(test)

    @util.writes_bytecode_files
    eleza test_partial_flags(self):
        # When the flags ni partial, regenerate the .pyc, isipokua ashiria EOFError.
        eleza test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bc_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_partial_flags(test)

    @util.writes_bytecode_files
    eleza test_partial_hash(self):
        # When the hash ni partial, regenerate the .pyc, isipokua ashiria EOFError.
        eleza test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bc_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_partial_hash(test)

    @util.writes_bytecode_files
    eleza test_partial_size(self):
        # When the size ni partial, regenerate the .pyc, ama
        # ashiria EOFError.
        eleza test(name, mapping, bc_path):
            self.import_(mapping[name], name)
            ukijumuisha open(bc_path, 'rb') kama file:
                self.assertGreater(len(file.read()), 16)

        self._test_partial_size(test)

    @util.writes_bytecode_files
    eleza test_no_marshal(self):
        # When there ni only the magic number na timestamp, ashiria EOFError.
        self._test_no_marshal()

    @util.writes_bytecode_files
    eleza test_non_code_marshal(self):
        self._test_non_code_marshal()
        # XXX ImportError when sourceless

    # [bad marshal]
    @util.writes_bytecode_files
    eleza test_bad_marshal(self):
        # Bad marshal data should ashiria a ValueError.
        self._test_bad_marshal()

    # [bad timestamp]
    @util.writes_bytecode_files
    @without_source_date_epoch
    eleza test_old_timestamp(self):
        # When the timestamp ni older than the source, bytecode should be
        # regenerated.
        zeros = b'\x00\x00\x00\x00'
        ukijumuisha util.create_modules('_temp') kama mapping:
            py_compile.compile(mapping['_temp'])
            bytecode_path = self.util.cache_from_source(mapping['_temp'])
            ukijumuisha open(bytecode_path, 'r+b') kama bytecode_file:
                bytecode_file.seek(8)
                bytecode_file.write(zeros)
            self.import_(mapping['_temp'], '_temp')
            source_mtime = os.path.getmtime(mapping['_temp'])
            source_timestamp = self.importlib._pack_uint32(source_mtime)
            ukijumuisha open(bytecode_path, 'rb') kama bytecode_file:
                bytecode_file.seek(8)
                self.assertEqual(bytecode_file.read(4), source_timestamp)

    # [bytecode read-only]
    @util.writes_bytecode_files
    eleza test_read_only_bytecode(self):
        # When bytecode ni read-only but should be rewritten, fail silently.
        ukijumuisha util.create_modules('_temp') kama mapping:
            # Create bytecode that will need to be re-created.
            py_compile.compile(mapping['_temp'])
            bytecode_path = self.util.cache_from_source(mapping['_temp'])
            ukijumuisha open(bytecode_path, 'r+b') kama bytecode_file:
                bytecode_file.seek(0)
                bytecode_file.write(b'\x00\x00\x00\x00')
            # Make the bytecode read-only.
            os.chmod(bytecode_path,
                        stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            jaribu:
                # Should sio ashiria OSError!
                self.import_(mapping['_temp'], '_temp')
            mwishowe:
                # Make writable kila eventual clean-up.
                os.chmod(bytecode_path, stat.S_IWUSR)


kundi SourceLoaderBadBytecodeTestPEP451(
        SourceLoaderBadBytecodeTest, BadBytecodeTestPEP451):
    pita


(Frozen_SourceBadBytecodePEP451,
 Source_SourceBadBytecodePEP451
 ) = util.test_both(SourceLoaderBadBytecodeTestPEP451, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


kundi SourceLoaderBadBytecodeTestPEP302(
        SourceLoaderBadBytecodeTest, BadBytecodeTestPEP302):
    pita


(Frozen_SourceBadBytecodePEP302,
 Source_SourceBadBytecodePEP302
 ) = util.test_both(SourceLoaderBadBytecodeTestPEP302, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


kundi SourcelessLoaderBadBytecodeTest:

    @classmethod
    eleza setUpClass(cls):
        cls.loader = cls.machinery.SourcelessFileLoader

    eleza test_empty_file(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(ImportError) kama cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)

        self._test_empty_file(test, del_source=Kweli)

    eleza test_partial_magic(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(ImportError) kama cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)
        self._test_partial_magic(test, del_source=Kweli)

    eleza test_magic_only(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_magic_only(test, del_source=Kweli)

    eleza test_bad_magic(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(ImportError) kama cm:
                self.import_(bytecode_path, name)
            self.assertEqual(cm.exception.name, name)
            self.assertEqual(cm.exception.path, bytecode_path)

        self._test_bad_magic(test, del_source=Kweli)

    eleza test_partial_timestamp(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_timestamp(test, del_source=Kweli)

    eleza test_partial_flags(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_flags(test, del_source=Kweli)

    eleza test_partial_hash(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_hash(test, del_source=Kweli)

    eleza test_partial_size(self):
        eleza test(name, mapping, bytecode_path):
            ukijumuisha self.assertRaises(EOFError):
                self.import_(bytecode_path, name)

        self._test_partial_size(test, del_source=Kweli)

    eleza test_no_marshal(self):
        self._test_no_marshal(del_source=Kweli)

    eleza test_non_code_marshal(self):
        self._test_non_code_marshal(del_source=Kweli)


kundi SourcelessLoaderBadBytecodeTestPEP451(SourcelessLoaderBadBytecodeTest,
        BadBytecodeTestPEP451):
    pita


(Frozen_SourcelessBadBytecodePEP451,
 Source_SourcelessBadBytecodePEP451
 ) = util.test_both(SourcelessLoaderBadBytecodeTestPEP451, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


kundi SourcelessLoaderBadBytecodeTestPEP302(SourcelessLoaderBadBytecodeTest,
        BadBytecodeTestPEP302):
    pita


(Frozen_SourcelessBadBytecodePEP302,
 Source_SourcelessBadBytecodePEP302
 ) = util.test_both(SourcelessLoaderBadBytecodeTestPEP302, importlib=importlib,
                    machinery=machinery, abc=importlib_abc,
                    util=importlib_util)


ikiwa __name__ == '__main__':
    unittest.main()
