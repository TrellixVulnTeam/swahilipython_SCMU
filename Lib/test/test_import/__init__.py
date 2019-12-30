# We agiza importlib *ASAP* kwenye order to test #15386
agiza importlib
agiza importlib.util
kutoka importlib._bootstrap_external agiza _get_sourcefile
agiza builtins
agiza marshal
agiza os
agiza py_compile
agiza random
agiza shutil
agiza subprocess
agiza stat
agiza sys
agiza threading
agiza time
agiza unittest
agiza unittest.mock kama mock
agiza textwrap
agiza errno
agiza contextlib
agiza glob

agiza test.support
kutoka test.support agiza (
    TESTFN, forget, is_jython,
    make_legacy_pyc, rmtree, swap_attr, swap_item, temp_umask,
    unlink, unload, cpython_only, TESTFN_UNENCODABLE,
    temp_dir, DirsOnSysPath)
kutoka test.support agiza script_helper
kutoka test.test_importlib.util agiza uncache


skip_if_dont_write_bytecode = unittest.skipIf(
        sys.dont_write_bytecode,
        "test meaningful only when writing bytecode")

eleza remove_files(name):
    kila f kwenye (name + ".py",
              name + ".pyc",
              name + ".pyw",
              name + "$py.class"):
        unlink(f)
    rmtree('__pycache__')


@contextlib.contextmanager
eleza _ready_to_import(name=Tupu, source=""):
    # sets up a temporary directory na removes it
    # creates the module file
    # temporarily clears the module kutoka sys.modules (ikiwa any)
    # reverts ama removes the module when cleaning up
    name = name ama "spam"
    ukijumuisha temp_dir() kama tempdir:
        path = script_helper.make_script(tempdir, name, source)
        old_module = sys.modules.pop(name, Tupu)
        jaribu:
            sys.path.insert(0, tempdir)
            tuma name, path
            sys.path.remove(tempdir)
        mwishowe:
            ikiwa old_module ni sio Tupu:
                sys.modules[name] = old_module
            lasivyo name kwenye sys.modules:
                toa sys.modules[name]


kundi ImportTests(unittest.TestCase):

    eleza setUp(self):
        remove_files(TESTFN)
        importlib.invalidate_caches()

    eleza tearDown(self):
        unload(TESTFN)

    eleza test_import_raises_ModuleNotFoundError(self):
        ukijumuisha self.assertRaises(ModuleNotFoundError):
            agiza something_that_should_not_exist_anywhere

    eleza test_from_import_missing_module_raises_ModuleNotFoundError(self):
        ukijumuisha self.assertRaises(ModuleNotFoundError):
            kutoka something_that_should_not_exist_anywhere agiza blah

    eleza test_from_import_missing_attr_raises_ImportError(self):
        ukijumuisha self.assertRaises(ImportError):
            kutoka importlib agiza something_that_should_not_exist_anywhere

    eleza test_from_import_missing_attr_has_name_and_path(self):
        ukijumuisha self.assertRaises(ImportError) kama cm:
            kutoka os agiza i_dont_exist
        self.assertEqual(cm.exception.name, 'os')
        self.assertEqual(cm.exception.path, os.__file__)
        self.assertRegex(str(cm.exception), r"cansio agiza name 'i_dont_exist' kutoka 'os' \(.*os.py\)")

    @cpython_only
    eleza test_from_import_missing_attr_has_name_and_so_path(self):
        agiza _testcapi
        ukijumuisha self.assertRaises(ImportError) kama cm:
            kutoka _testcapi agiza i_dont_exist
        self.assertEqual(cm.exception.name, '_testcapi')
        self.assertEqual(cm.exception.path, _testcapi.__file__)
        self.assertRegex(str(cm.exception), r"cansio agiza name 'i_dont_exist' kutoka '_testcapi' \(.*\.(so|pyd)\)")

    eleza test_from_import_missing_attr_has_name(self):
        ukijumuisha self.assertRaises(ImportError) kama cm:
            # _warning has no path kama it's a built-in module.
            kutoka _warning agiza i_dont_exist
        self.assertEqual(cm.exception.name, '_warning')
        self.assertIsTupu(cm.exception.path)

    eleza test_from_import_missing_attr_path_is_canonical(self):
        ukijumuisha self.assertRaises(ImportError) kama cm:
            kutoka os.path agiza i_dont_exist
        self.assertIn(cm.exception.name, {'posixpath', 'ntpath'})
        self.assertIsNotTupu(cm.exception)

    eleza test_from_import_star_invalid_type(self):
        agiza re
        ukijumuisha _ready_to_import() kama (name, path):
            ukijumuisha open(path, 'w') kama f:
                f.write("__all__ = [b'invalid_type']")
            globals = {}
            ukijumuisha self.assertRaisesRegex(
                TypeError, f"{re.escape(name)}\\.__all__ must be str"
            ):
                exec(f"kutoka {name} agiza *", globals)
            self.assertNotIn(b"invalid_type", globals)
        ukijumuisha _ready_to_import() kama (name, path):
            ukijumuisha open(path, 'w') kama f:
                f.write("globals()[b'invalid_type'] = object()")
            globals = {}
            ukijumuisha self.assertRaisesRegex(
                TypeError, f"{re.escape(name)}\\.__dict__ must be str"
            ):
                exec(f"kutoka {name} agiza *", globals)
            self.assertNotIn(b"invalid_type", globals)

    eleza test_case_sensitivity(self):
        # Brief digression to test that agiza ni case-sensitive:  ikiwa we got
        # this far, we know kila sure that "random" exists.
        ukijumuisha self.assertRaises(ImportError):
            agiza RAnDoM

    eleza test_double_const(self):
        # Another brief digression to test the accuracy of manifest float
        # constants.
        kutoka test agiza double_const  # don't blink -- that *was* the test

    eleza test_import(self):
        eleza test_with_extension(ext):
            # The extension ni normally ".py", perhaps ".pyw".
            source = TESTFN + ext
            ikiwa is_jython:
                pyc = TESTFN + "$py.class"
            isipokua:
                pyc = TESTFN + ".pyc"

            ukijumuisha open(source, "w") kama f:
                andika("# This tests Python's ability to agiza a",
                      ext, "file.", file=f)
                a = random.randrange(1000)
                b = random.randrange(1000)
                andika("a =", a, file=f)
                andika("b =", b, file=f)

            ikiwa TESTFN kwenye sys.modules:
                toa sys.modules[TESTFN]
            importlib.invalidate_caches()
            jaribu:
                jaribu:
                    mod = __import__(TESTFN)
                tatizo ImportError kama err:
                    self.fail("agiza kutoka %s failed: %s" % (ext, err))

                self.assertEqual(mod.a, a,
                    "module loaded (%s) but contents invalid" % mod)
                self.assertEqual(mod.b, b,
                    "module loaded (%s) but contents invalid" % mod)
            mwishowe:
                forget(TESTFN)
                unlink(source)
                unlink(pyc)

        sys.path.insert(0, os.curdir)
        jaribu:
            test_with_extension(".py")
            ikiwa sys.platform.startswith("win"):
                kila ext kwenye [".PY", ".Py", ".pY", ".pyw", ".PYW", ".pYw"]:
                    test_with_extension(ext)
        mwishowe:
            toa sys.path[0]

    eleza test_module_with_large_stack(self, module='longlist'):
        # Regression test kila http://bugs.python.org/issue561858.
        filename = module + '.py'

        # Create a file ukijumuisha a list of 65000 elements.
        ukijumuisha open(filename, 'w') kama f:
            f.write('d = [\n')
            kila i kwenye range(65000):
                f.write('"",\n')
            f.write(']')

        jaribu:
            # Compile & remove .py file; we only need .pyc.
            # Bytecode must be relocated kutoka the PEP 3147 bytecode-only location.
            py_compile.compile(filename)
        mwishowe:
            unlink(filename)

        # Need to be able to load kutoka current dir.
        sys.path.append('')
        importlib.invalidate_caches()

        namespace = {}
        jaribu:
            make_legacy_pyc(filename)
            # This used to crash.
            exec('agiza ' + module, Tupu, namespace)
        mwishowe:
            # Cleanup.
            toa sys.path[-1]
            unlink(filename + 'c')
            unlink(filename + 'o')

            # Remove references to the module (unload the module)
            namespace.clear()
            jaribu:
                toa sys.modules[module]
            tatizo KeyError:
                pita

    eleza test_failing_import_sticks(self):
        source = TESTFN + ".py"
        ukijumuisha open(source, "w") kama f:
            andika("a = 1/0", file=f)

        # New kwenye 2.4, we shouldn't be able to agiza that no matter how often
        # we try.
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        ikiwa TESTFN kwenye sys.modules:
            toa sys.modules[TESTFN]
        jaribu:
            kila i kwenye [1, 2, 3]:
                self.assertRaises(ZeroDivisionError, __import__, TESTFN)
                self.assertNotIn(TESTFN, sys.modules,
                                 "damaged module kwenye sys.modules on %i try" % i)
        mwishowe:
            toa sys.path[0]
            remove_files(TESTFN)

    eleza test_import_name_binding(self):
        # agiza x.y.z binds x kwenye the current namespace
        agiza test kama x
        agiza test.support
        self.assertIs(x, test, x.__name__)
        self.assertKweli(hasattr(test.support, "__file__"))

        # agiza x.y.z kama w binds z kama w
        agiza test.support kama y
        self.assertIs(y, test.support, y.__name__)

    eleza test_issue31286(self):
        # agiza kwenye a 'finally' block resulted kwenye SystemError
        jaribu:
            x = ...
        mwishowe:
            agiza test.support.script_helper kama x

        # agiza kwenye a 'while' loop resulted kwenye stack overflow
        i = 0
        wakati i < 10:
            agiza test.support.script_helper kama x
            i += 1

        # agiza kwenye a 'for' loop resulted kwenye segmentation fault
        kila i kwenye range(2):
            agiza test.support.script_helper kama x

    eleza test_failing_reload(self):
        # A failing reload should leave the module object kwenye sys.modules.
        source = TESTFN + os.extsep + "py"
        ukijumuisha open(source, "w") kama f:
            f.write("a = 1\nb=2\n")

        sys.path.insert(0, os.curdir)
        jaribu:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)
            self.assertEqual(mod.a, 1, "module has wrong attribute values")
            self.assertEqual(mod.b, 2, "module has wrong attribute values")

            # On WinXP, just replacing the .py file wasn't enough to
            # convince reload() to reparse it.  Maybe the timestamp didn't
            # move enough.  We force it to get reparsed by removing the
            # compiled file too.
            remove_files(TESTFN)

            # Now damage the module.
            ukijumuisha open(source, "w") kama f:
                f.write("a = 10\nb=20//0\n")

            self.assertRaises(ZeroDivisionError, importlib.reload, mod)
            # But we still expect the module to be kwenye sys.modules.
            mod = sys.modules.get(TESTFN)
            self.assertIsNotTupu(mod, "expected module to be kwenye sys.modules")

            # We should have replaced a w/ 10, but the old b value should
            # stick.
            self.assertEqual(mod.a, 10, "module has wrong attribute values")
            self.assertEqual(mod.b, 2, "module has wrong attribute values")

        mwishowe:
            toa sys.path[0]
            remove_files(TESTFN)
            unload(TESTFN)

    @skip_if_dont_write_bytecode
    eleza test_file_to_source(self):
        # check ikiwa __file__ points to the source file where available
        source = TESTFN + ".py"
        ukijumuisha open(source, "w") kama f:
            f.write("test = Tupu\n")

        sys.path.insert(0, os.curdir)
        jaribu:
            mod = __import__(TESTFN)
            self.assertKweli(mod.__file__.endswith('.py'))
            os.remove(source)
            toa sys.modules[TESTFN]
            make_legacy_pyc(source)
            importlib.invalidate_caches()
            mod = __import__(TESTFN)
            base, ext = os.path.splitext(mod.__file__)
            self.assertEqual(ext, '.pyc')
        mwishowe:
            toa sys.path[0]
            remove_files(TESTFN)
            ikiwa TESTFN kwenye sys.modules:
                toa sys.modules[TESTFN]

    eleza test_import_by_filename(self):
        path = os.path.abspath(TESTFN)
        encoding = sys.getfilesystemencoding()
        jaribu:
            path.encode(encoding)
        tatizo UnicodeEncodeError:
            self.skipTest('path ni sio encodable to {}'.format(encoding))
        ukijumuisha self.assertRaises(ImportError) kama c:
            __import__(path)

    eleza test_import_in_del_does_not_crash(self):
        # Issue 4236
        testfn = script_helper.make_script('', TESTFN, textwrap.dedent("""\
            agiza sys
            kundi C:
               eleza __del__(self):
                  agiza importlib
            sys.argv.insert(0, C())
            """))
        script_helper.assert_python_ok(testfn)

    @skip_if_dont_write_bytecode
    eleza test_timestamp_overflow(self):
        # A modification timestamp larger than 2**32 should sio be a problem
        # when importing a module (issue #11235).
        sys.path.insert(0, os.curdir)
        jaribu:
            source = TESTFN + ".py"
            compiled = importlib.util.cache_from_source(source)
            ukijumuisha open(source, 'w') kama f:
                pita
            jaribu:
                os.utime(source, (2 ** 33 - 5, 2 ** 33 - 5))
            tatizo OverflowError:
                self.skipTest("cansio set modification time to large integer")
            tatizo OSError kama e:
                ikiwa e.errno haiko kwenye (getattr(errno, 'EOVERFLOW', Tupu),
                                   getattr(errno, 'EINVAL', Tupu)):
                    raise
                self.skipTest("cansio set modification time to large integer ({})".format(e))
            __import__(TESTFN)
            # The pyc file was created.
            os.stat(compiled)
        mwishowe:
            toa sys.path[0]
            remove_files(TESTFN)

    eleza test_bogus_fromlist(self):
        jaribu:
            __import__('http', fromlist=['blah'])
        tatizo ImportError:
            self.fail("fromlist must allow bogus names")

    @cpython_only
    eleza test_delete_builtins_import(self):
        args = ["-c", "toa __builtins__.__import__; agiza os"]
        popen = script_helper.spawn_python(*args)
        stdout, stderr = popen.communicate()
        self.assertIn(b"ImportError", stdout)

    eleza test_from_import_message_for_nonexistent_module(self):
        ukijumuisha self.assertRaisesRegex(ImportError, "^No module named 'bogus'"):
            kutoka bogus agiza foo

    eleza test_from_import_message_for_existing_module(self):
        ukijumuisha self.assertRaisesRegex(ImportError, "^cansio agiza name 'bogus'"):
            kutoka re agiza bogus

    eleza test_from_import_AttributeError(self):
        # Issue #24492: trying to agiza an attribute that raises an
        # AttributeError should lead to an ImportError.
        kundi AlwaysAttributeError:
            eleza __getattr__(self, _):
                ashiria AttributeError

        module_name = 'test_from_import_AttributeError'
        self.addCleanup(unload, module_name)
        sys.modules[module_name] = AlwaysAttributeError()
        ukijumuisha self.assertRaises(ImportError) kama cm:
            kutoka test_from_import_AttributeError agiza does_not_exist

        self.assertEqual(str(cm.exception),
            "cansio agiza name 'does_not_exist' kutoka '<unknown module name>' (unknown location)")

    @cpython_only
    eleza test_issue31492(self):
        # There shouldn't be an assertion failure kwenye case of failing to import
        # kutoka a module ukijumuisha a bad __name__ attribute, ama kwenye case of failing
        # to access an attribute of such a module.
        ukijumuisha swap_attr(os, '__name__', Tupu):
            ukijumuisha self.assertRaises(ImportError):
                kutoka os agiza does_not_exist

            ukijumuisha self.assertRaises(AttributeError):
                os.does_not_exist

    eleza test_concurrency(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data'))
        jaribu:
            exc = Tupu
            eleza run():
                event.wait()
                jaribu:
                    agiza package
                tatizo BaseException kama e:
                    nonlocal exc
                    exc = e

            kila i kwenye range(10):
                event = threading.Event()
                threads = [threading.Thread(target=run) kila x kwenye range(2)]
                jaribu:
                    ukijumuisha test.support.start_threads(threads, event.set):
                        time.sleep(0)
                mwishowe:
                    sys.modules.pop('package', Tupu)
                    sys.modules.pop('package.submodule', Tupu)
                ikiwa exc ni sio Tupu:
                    ashiria exc
        mwishowe:
            toa sys.path[0]

    @unittest.skipUnless(sys.platform == "win32", "Windows-specific")
    eleza test_dll_dependency_import(self):
        kutoka _winapi agiza GetModuleFileName
        dllname = GetModuleFileName(sys.dllhandle)
        pydname = importlib.util.find_spec("_sqlite3").origin
        depname = os.path.join(
            os.path.dirname(pydname),
            "sqlite3{}.dll".format("_d" ikiwa "_d" kwenye pydname isipokua ""))

        ukijumuisha test.support.temp_dir() kama tmp:
            tmp2 = os.path.join(tmp, "DLLs")
            os.mkdir(tmp2)

            pyexe = os.path.join(tmp, os.path.basename(sys.executable))
            shutil.copy(sys.executable, pyexe)
            shutil.copy(dllname, tmp)
            kila f kwenye glob.glob(os.path.join(sys.prefix, "vcruntime*.dll")):
                shutil.copy(f, tmp)

            shutil.copy(pydname, tmp2)

            env = Tupu
            env = {k.upper(): os.environ[k] kila k kwenye os.environ}
            env["PYTHONPATH"] = tmp2 + ";" + os.path.dirname(os.__file__)

            # Test 1: agiza ukijumuisha added DLL directory
            subprocess.check_call([
                pyexe, "-Sc", ";".join([
                    "agiza os",
                    "p = os.add_dll_directory({!r})".format(
                        os.path.dirname(depname)),
                    "agiza _sqlite3",
                    "p.close"
                ])],
                stderr=subprocess.STDOUT,
                env=env,
                cwd=os.path.dirname(pyexe))

            # Test 2: agiza ukijumuisha DLL adjacent to PYD
            shutil.copy(depname, tmp2)
            subprocess.check_call([pyexe, "-Sc", "agiza _sqlite3"],
                                    stderr=subprocess.STDOUT,
                                    env=env,
                                    cwd=os.path.dirname(pyexe))


@skip_if_dont_write_bytecode
kundi FilePermissionTests(unittest.TestCase):
    # tests kila file mode on cached .pyc files

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    eleza test_creation_mode(self):
        mask = 0o022
        ukijumuisha temp_umask(mask), _ready_to_import() kama (name, path):
            cached_path = importlib.util.cache_from_source(path)
            module = __import__(name)
            ikiwa sio os.path.exists(cached_path):
                self.fail("__import__ did sio result kwenye creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        # Check that the umask ni respected, na the executable bits
        # aren't set.
        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)),
                         oct(0o666 & ~mask))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    eleza test_cached_mode_issue_2051(self):
        # permissions of .pyc should match those of .py, regardless of mask
        mode = 0o600
        ukijumuisha temp_umask(0o022), _ready_to_import() kama (name, path):
            cached_path = importlib.util.cache_from_source(path)
            os.chmod(path, mode)
            __import__(name)
            ikiwa sio os.path.exists(cached_path):
                self.fail("__import__ did sio result kwenye creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)), oct(mode))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    eleza test_cached_readonly(self):
        mode = 0o400
        ukijumuisha temp_umask(0o022), _ready_to_import() kama (name, path):
            cached_path = importlib.util.cache_from_source(path)
            os.chmod(path, mode)
            __import__(name)
            ikiwa sio os.path.exists(cached_path):
                self.fail("__import__ did sio result kwenye creation of "
                          "a .pyc file")
            stat_info = os.stat(cached_path)

        expected = mode | 0o200 # Account kila fix kila issue #6074
        self.assertEqual(oct(stat.S_IMODE(stat_info.st_mode)), oct(expected))

    eleza test_pyc_always_writable(self):
        # Initially read-only .pyc files on Windows used to cause problems
        # ukijumuisha later updates, see issue #6074 kila details
        ukijumuisha _ready_to_import() kama (name, path):
            # Write a Python file, make it read-only na agiza it
            ukijumuisha open(path, 'w') kama f:
                f.write("x = 'original'\n")
            # Tweak the mtime of the source to ensure pyc gets updated later
            s = os.stat(path)
            os.utime(path, (s.st_atime, s.st_mtime-100000000))
            os.chmod(path, 0o400)
            m = __import__(name)
            self.assertEqual(m.x, 'original')
            # Change the file na then reagiza it
            os.chmod(path, 0o600)
            ukijumuisha open(path, 'w') kama f:
                f.write("x = 'rewritten'\n")
            unload(name)
            importlib.invalidate_caches()
            m = __import__(name)
            self.assertEqual(m.x, 'rewritten')
            # Now delete the source file na check the pyc was rewritten
            unlink(path)
            unload(name)
            importlib.invalidate_caches()
            bytecode_only = path + "c"
            os.rename(importlib.util.cache_from_source(path), bytecode_only)
            m = __import__(name)
            self.assertEqual(m.x, 'rewritten')


kundi PycRewritingTests(unittest.TestCase):
    # Test that the `co_filename` attribute on code objects always points
    # to the right file, even when various things happen (e.g. both the .py
    # na the .pyc file are renamed).

    module_name = "unlikely_module_name"
    module_source = """
agiza sys
code_filename = sys._getframe().f_code.co_filename
module_filename = __file__
constant = 1
eleza func():
    pita
func_filename = func.__code__.co_filename
"""
    dir_name = os.path.abspath(TESTFN)
    file_name = os.path.join(dir_name, module_name) + os.extsep + "py"
    compiled_name = importlib.util.cache_from_source(file_name)

    eleza setUp(self):
        self.sys_path = sys.path[:]
        self.orig_module = sys.modules.pop(self.module_name, Tupu)
        os.mkdir(self.dir_name)
        ukijumuisha open(self.file_name, "w") kama f:
            f.write(self.module_source)
        sys.path.insert(0, self.dir_name)
        importlib.invalidate_caches()

    eleza tearDown(self):
        sys.path[:] = self.sys_path
        ikiwa self.orig_module ni sio Tupu:
            sys.modules[self.module_name] = self.orig_module
        isipokua:
            unload(self.module_name)
        unlink(self.file_name)
        unlink(self.compiled_name)
        rmtree(self.dir_name)

    eleza import_module(self):
        ns = globals()
        __import__(self.module_name, ns, ns)
        rudisha sys.modules[self.module_name]

    eleza test_basics(self):
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)
        toa sys.modules[self.module_name]
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)

    eleza test_incorrect_code_name(self):
        py_compile.compile(self.file_name, dfile="another_module.py")
        mod = self.import_module()
        self.assertEqual(mod.module_filename, self.file_name)
        self.assertEqual(mod.code_filename, self.file_name)
        self.assertEqual(mod.func_filename, self.file_name)

    eleza test_module_without_source(self):
        target = "another_module.py"
        py_compile.compile(self.file_name, dfile=target)
        os.remove(self.file_name)
        pyc_file = make_legacy_pyc(self.file_name)
        importlib.invalidate_caches()
        mod = self.import_module()
        self.assertEqual(mod.module_filename, pyc_file)
        self.assertEqual(mod.code_filename, target)
        self.assertEqual(mod.func_filename, target)

    eleza test_foreign_code(self):
        py_compile.compile(self.file_name)
        ukijumuisha open(self.compiled_name, "rb") kama f:
            header = f.read(16)
            code = marshal.load(f)
        constants = list(code.co_consts)
        foreign_code = importlib.import_module.__code__
        pos = constants.index(1)
        constants[pos] = foreign_code
        code = code.replace(co_consts=tuple(constants))
        ukijumuisha open(self.compiled_name, "wb") kama f:
            f.write(header)
            marshal.dump(code, f)
        mod = self.import_module()
        self.assertEqual(mod.constant.co_filename, foreign_code.co_filename)


kundi PathsTests(unittest.TestCase):
    SAMPLES = ('test', 'test\u00e4\u00f6\u00fc\u00df', 'test\u00e9\u00e8',
               'test\u00b0\u00b3\u00b2')
    path = TESTFN

    eleza setUp(self):
        os.mkdir(self.path)
        self.syspath = sys.path[:]

    eleza tearDown(self):
        rmtree(self.path)
        sys.path[:] = self.syspath

    # Regression test kila http://bugs.python.org/issue1293.
    eleza test_trailing_slash(self):
        ukijumuisha open(os.path.join(self.path, 'test_trailing_slash.py'), 'w') kama f:
            f.write("testdata = 'test_trailing_slash'")
        sys.path.append(self.path+'/')
        mod = __import__("test_trailing_slash")
        self.assertEqual(mod.testdata, 'test_trailing_slash')
        unload("test_trailing_slash")

    # Regression test kila http://bugs.python.org/issue3677.
    @unittest.skipUnless(sys.platform == 'win32', 'Windows-specific')
    eleza test_UNC_path(self):
        ukijumuisha open(os.path.join(self.path, 'test_unc_path.py'), 'w') kama f:
            f.write("testdata = 'test_unc_path'")
        importlib.invalidate_caches()
        # Create the UNC path, like \\myhost\c$\foo\bar.
        path = os.path.abspath(self.path)
        agiza socket
        hn = socket.gethostname()
        drive = path[0]
        unc = "\\\\%s\\%s$"%(hn, drive)
        unc += path[2:]
        jaribu:
            os.listdir(unc)
        tatizo OSError kama e:
            ikiwa e.errno kwenye (errno.EPERM, errno.EACCES, errno.ENOENT):
                # See issue #15338
                self.skipTest("cansio access administrative share %r" % (unc,))
            raise
        sys.path.insert(0, unc)
        jaribu:
            mod = __import__("test_unc_path")
        tatizo ImportError kama e:
            self.fail("could sio agiza 'test_unc_path' kutoka %r: %r"
                      % (unc, e))
        self.assertEqual(mod.testdata, 'test_unc_path')
        self.assertKweli(mod.__file__.startswith(unc), mod.__file__)
        unload("test_unc_path")


kundi RelativeImportTests(unittest.TestCase):

    eleza tearDown(self):
        unload("test.relimport")
    setUp = tearDown

    eleza test_relimport_star(self):
        # This will agiza * kutoka .test_import.
        kutoka .. agiza relimport
        self.assertKweli(hasattr(relimport, "RelativeImportTests"))

    eleza test_issue3221(self):
        # Note kila mergers: the 'absolute' tests kutoka the 2.x branch
        # are missing kwenye Py3k because implicit relative imports are
        # a thing of the past
        #
        # Regression test kila http://bugs.python.org/issue3221.
        eleza check_relative():
            exec("kutoka . agiza relimport", ns)

        # Check relative agiza OK ukijumuisha __package__ na __name__ correct
        ns = dict(__package__='test', __name__='test.notarealmodule')
        check_relative()

        # Check relative agiza OK ukijumuisha only __name__ wrong
        ns = dict(__package__='test', __name__='notarealpkg.notarealmodule')
        check_relative()

        # Check relative agiza fails ukijumuisha only __package__ wrong
        ns = dict(__package__='foo', __name__='test.notarealmodule')
        self.assertRaises(ModuleNotFoundError, check_relative)

        # Check relative agiza fails ukijumuisha __package__ na __name__ wrong
        ns = dict(__package__='foo', __name__='notarealpkg.notarealmodule')
        self.assertRaises(ModuleNotFoundError, check_relative)

        # Check relative agiza fails ukijumuisha package set to a non-string
        ns = dict(__package__=object())
        self.assertRaises(TypeError, check_relative)

    eleza test_parentless_import_shadowed_by_global(self):
        # Test kama ikiwa this were done kutoka the REPL where this error most commonly occurs (bpo-37409).
        script_helper.assert_python_failure('-W', 'ignore', '-c',
            "foo = 1; kutoka . agiza foo")

    eleza test_absolute_import_without_future(self):
        # If explicit relative agiza syntax ni used, then do sio try
        # to perform an absolute agiza kwenye the face of failure.
        # Issue #7902.
        ukijumuisha self.assertRaises(ImportError):
            kutoka .os agiza sep
            self.fail("explicit relative agiza triggered an "
                      "implicit absolute import")

    eleza test_import_from_non_package(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'package2')
        ukijumuisha uncache('submodule1', 'submodule2'), DirsOnSysPath(path):
            ukijumuisha self.assertRaises(ImportError):
                agiza submodule1
            self.assertNotIn('submodule1', sys.modules)
            self.assertNotIn('submodule2', sys.modules)

    eleza test_import_from_unloaded_package(self):
        ukijumuisha uncache('package2', 'package2.submodule1', 'package2.submodule2'), \
             DirsOnSysPath(os.path.join(os.path.dirname(__file__), 'data')):
            agiza package2.submodule1
            package2.submodule1.submodule2


kundi OverridingImportBuiltinTests(unittest.TestCase):
    eleza test_override_builtin(self):
        # Test that overriding builtins.__import__ can bypita sys.modules.
        agiza os

        eleza foo():
            agiza os
            rudisha os
        self.assertEqual(foo(), os)  # Quick sanity check.

        ukijumuisha swap_attr(builtins, "__import__", lambda *x: 5):
            self.assertEqual(foo(), 5)

        # Test what happens when we shadow __import__ kwenye globals(); this
        # currently does sio impact the agiza process, but ikiwa this changes,
        # other code will need to change, so keep this test kama a tripwire.
        ukijumuisha swap_item(globals(), "__import__", lambda *x: 5):
            self.assertEqual(foo(), os)


kundi PycacheTests(unittest.TestCase):
    # Test the various PEP 3147/488-related behaviors.

    eleza _clean(self):
        forget(TESTFN)
        rmtree('__pycache__')
        unlink(self.source)

    eleza setUp(self):
        self.source = TESTFN + '.py'
        self._clean()
        ukijumuisha open(self.source, 'w') kama fp:
            andika('# This ni a test file written by test_import.py', file=fp)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()

    eleza tearDown(self):
        assert sys.path[0] == os.curdir, 'Unexpected sys.path[0]'
        toa sys.path[0]
        self._clean()

    @skip_if_dont_write_bytecode
    eleza test_import_pyc_path(self):
        self.assertUongo(os.path.exists('__pycache__'))
        __import__(TESTFN)
        self.assertKweli(os.path.exists('__pycache__'))
        pyc_path = importlib.util.cache_from_source(self.source)
        self.assertKweli(os.path.exists(pyc_path),
                        'bytecode file {!r} kila {!r} does sio '
                        'exist'.format(pyc_path, TESTFN))

    @unittest.skipUnless(os.name == 'posix',
                         "test meaningful only on posix systems")
    @unittest.skipIf(hasattr(os, 'geteuid') na os.geteuid() == 0,
            "due to varying filesystem permission semantics (issue #11956)")
    @skip_if_dont_write_bytecode
    eleza test_unwritable_directory(self):
        # When the umask causes the new __pycache__ directory to be
        # unwritable, the agiza still succeeds but no .pyc file ni written.
        ukijumuisha temp_umask(0o222):
            __import__(TESTFN)
        self.assertKweli(os.path.exists('__pycache__'))
        pyc_path = importlib.util.cache_from_source(self.source)
        self.assertUongo(os.path.exists(pyc_path),
                        'bytecode file {!r} kila {!r} '
                        'exists'.format(pyc_path, TESTFN))

    @skip_if_dont_write_bytecode
    eleza test_missing_source(self):
        # With PEP 3147 cache layout, removing the source but leaving the pyc
        # file does sio satisfy the import.
        __import__(TESTFN)
        pyc_file = importlib.util.cache_from_source(self.source)
        self.assertKweli(os.path.exists(pyc_file))
        os.remove(self.source)
        forget(TESTFN)
        importlib.invalidate_caches()
        self.assertRaises(ImportError, __import__, TESTFN)

    @skip_if_dont_write_bytecode
    eleza test_missing_source_legacy(self):
        # Like test_missing_source() tatizo that kila backward compatibility,
        # when the pyc file lives where the py file would have been (and named
        # without the tag), it ni importable.  The __file__ of the imported
        # module ni the pyc location.
        __import__(TESTFN)
        # pyc_file gets removed kwenye _clean() via tearDown().
        pyc_file = make_legacy_pyc(self.source)
        os.remove(self.source)
        unload(TESTFN)
        importlib.invalidate_caches()
        m = __import__(TESTFN)
        jaribu:
            self.assertEqual(m.__file__,
                             os.path.join(os.curdir, os.path.relpath(pyc_file)))
        mwishowe:
            os.remove(pyc_file)

    eleza test___cached__(self):
        # Modules now also have an __cached__ that points to the pyc file.
        m = __import__(TESTFN)
        pyc_file = importlib.util.cache_from_source(TESTFN + '.py')
        self.assertEqual(m.__cached__, os.path.join(os.curdir, pyc_file))

    @skip_if_dont_write_bytecode
    eleza test___cached___legacy_pyc(self):
        # Like test___cached__() tatizo that kila backward compatibility,
        # when the pyc file lives where the py file would have been (and named
        # without the tag), it ni importable.  The __cached__ of the imported
        # module ni the pyc location.
        __import__(TESTFN)
        # pyc_file gets removed kwenye _clean() via tearDown().
        pyc_file = make_legacy_pyc(self.source)
        os.remove(self.source)
        unload(TESTFN)
        importlib.invalidate_caches()
        m = __import__(TESTFN)
        self.assertEqual(m.__cached__,
                         os.path.join(os.curdir, os.path.relpath(pyc_file)))

    @skip_if_dont_write_bytecode
    eleza test_package___cached__(self):
        # Like test___cached__ but kila packages.
        eleza cleanup():
            rmtree('pep3147')
            unload('pep3147.foo')
            unload('pep3147')
        os.mkdir('pep3147')
        self.addCleanup(cleanup)
        # Touch the __init__.py
        ukijumuisha open(os.path.join('pep3147', '__init__.py'), 'w'):
            pita
        ukijumuisha open(os.path.join('pep3147', 'foo.py'), 'w'):
            pita
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        init_pyc = importlib.util.cache_from_source(
            os.path.join('pep3147', '__init__.py'))
        self.assertEqual(m.__cached__, os.path.join(os.curdir, init_pyc))
        foo_pyc = importlib.util.cache_from_source(os.path.join('pep3147', 'foo.py'))
        self.assertEqual(sys.modules['pep3147.foo'].__cached__,
                         os.path.join(os.curdir, foo_pyc))

    eleza test_package___cached___from_pyc(self):
        # Like test___cached__ but ensuring __cached__ when imported kutoka a
        # PEP 3147 pyc file.
        eleza cleanup():
            rmtree('pep3147')
            unload('pep3147.foo')
            unload('pep3147')
        os.mkdir('pep3147')
        self.addCleanup(cleanup)
        # Touch the __init__.py
        ukijumuisha open(os.path.join('pep3147', '__init__.py'), 'w'):
            pita
        ukijumuisha open(os.path.join('pep3147', 'foo.py'), 'w'):
            pita
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        unload('pep3147.foo')
        unload('pep3147')
        importlib.invalidate_caches()
        m = __import__('pep3147.foo')
        init_pyc = importlib.util.cache_from_source(
            os.path.join('pep3147', '__init__.py'))
        self.assertEqual(m.__cached__, os.path.join(os.curdir, init_pyc))
        foo_pyc = importlib.util.cache_from_source(os.path.join('pep3147', 'foo.py'))
        self.assertEqual(sys.modules['pep3147.foo'].__cached__,
                         os.path.join(os.curdir, foo_pyc))

    eleza test_recompute_pyc_same_second(self):
        # Even when the source file doesn't change timestamp, a change kwenye
        # source size ni enough to trigger recomputation of the pyc file.
        __import__(TESTFN)
        unload(TESTFN)
        ukijumuisha open(self.source, 'a') kama fp:
            andika("x = 5", file=fp)
        m = __import__(TESTFN)
        self.assertEqual(m.x, 5)


kundi TestSymbolicallyLinkedPackage(unittest.TestCase):
    package_name = 'sample'
    tagged = package_name + '-tagged'

    eleza setUp(self):
        test.support.rmtree(self.tagged)
        test.support.rmtree(self.package_name)
        self.orig_sys_path = sys.path[:]

        # create a sample package; imagine you have a package ukijumuisha a tag na
        #  you want to symbolically link it kutoka its untagged name.
        os.mkdir(self.tagged)
        self.addCleanup(test.support.rmtree, self.tagged)
        init_file = os.path.join(self.tagged, '__init__.py')
        test.support.create_empty_file(init_file)
        assert os.path.exists(init_file)

        # now create a symlink to the tagged package
        # sample -> sample-tagged
        os.symlink(self.tagged, self.package_name, target_is_directory=Kweli)
        self.addCleanup(test.support.unlink, self.package_name)
        importlib.invalidate_caches()

        self.assertEqual(os.path.isdir(self.package_name), Kweli)

        assert os.path.isfile(os.path.join(self.package_name, '__init__.py'))

    eleza tearDown(self):
        sys.path[:] = self.orig_sys_path

    # regression test kila issue6727
    @unittest.skipUnless(
        sio hasattr(sys, 'getwindowsversion')
        ama sys.getwindowsversion() >= (6, 0),
        "Windows Vista ama later required")
    @test.support.skip_unless_symlink
    eleza test_symlinked_dir_importable(self):
        # make sure sample can only be imported kutoka the current directory.
        sys.path[:] = ['.']
        assert os.path.exists(self.package_name)
        assert os.path.exists(os.path.join(self.package_name, '__init__.py'))

        # Try to agiza the package
        importlib.import_module(self.package_name)


@cpython_only
kundi ImportlibBootstrapTests(unittest.TestCase):
    # These tests check that importlib ni bootstrapped.

    eleza test_frozen_importlib(self):
        mod = sys.modules['_frozen_importlib']
        self.assertKweli(mod)

    eleza test_frozen_importlib_is_bootstrap(self):
        kutoka importlib agiza _bootstrap
        mod = sys.modules['_frozen_importlib']
        self.assertIs(mod, _bootstrap)
        self.assertEqual(mod.__name__, 'importlib._bootstrap')
        self.assertEqual(mod.__package__, 'importlib')
        self.assertKweli(mod.__file__.endswith('_bootstrap.py'), mod.__file__)

    eleza test_frozen_importlib_external_is_bootstrap_external(self):
        kutoka importlib agiza _bootstrap_external
        mod = sys.modules['_frozen_importlib_external']
        self.assertIs(mod, _bootstrap_external)
        self.assertEqual(mod.__name__, 'importlib._bootstrap_external')
        self.assertEqual(mod.__package__, 'importlib')
        self.assertKweli(mod.__file__.endswith('_bootstrap_external.py'), mod.__file__)

    eleza test_there_can_be_only_one(self):
        # Issue #15386 revealed a tricky loophole kwenye the bootstrapping
        # This test ni technically redundant, since the bug caused importing
        # this test module to crash completely, but it helps prove the point
        kutoka importlib agiza machinery
        mod = sys.modules['_frozen_importlib']
        self.assertIs(machinery.ModuleSpec, mod.ModuleSpec)


@cpython_only
kundi GetSourcefileTests(unittest.TestCase):

    """Test importlib._bootstrap_external._get_sourcefile() kama used by the C API.

    Because of the peculiarities of the need of this function, the tests are
    knowingly whitebox tests.

    """

    eleza test_get_sourcefile(self):
        # Given a valid bytecode path, rudisha the path to the corresponding
        # source file ikiwa it exists.
        ukijumuisha mock.patch('importlib._bootstrap_external._path_isfile') kama _path_isfile:
            _path_isfile.return_value = Kweli;
            path = TESTFN + '.pyc'
            expect = TESTFN + '.py'
            self.assertEqual(_get_sourcefile(path), expect)

    eleza test_get_sourcefile_no_source(self):
        # Given a valid bytecode path without a corresponding source path,
        # rudisha the original bytecode path.
        ukijumuisha mock.patch('importlib._bootstrap_external._path_isfile') kama _path_isfile:
            _path_isfile.return_value = Uongo;
            path = TESTFN + '.pyc'
            self.assertEqual(_get_sourcefile(path), path)

    eleza test_get_sourcefile_bad_ext(self):
        # Given a path ukijumuisha an invalid bytecode extension, rudisha the
        # bytecode path pitaed kama the argument.
        path = TESTFN + '.bad_ext'
        self.assertEqual(_get_sourcefile(path), path)


kundi ImportTracebackTests(unittest.TestCase):

    eleza setUp(self):
        os.mkdir(TESTFN)
        self.old_path = sys.path[:]
        sys.path.insert(0, TESTFN)

    eleza tearDown(self):
        sys.path[:] = self.old_path
        rmtree(TESTFN)

    eleza create_module(self, mod, contents, ext=".py"):
        fname = os.path.join(TESTFN, mod + ext)
        ukijumuisha open(fname, "w") kama f:
            f.write(contents)
        self.addCleanup(unload, mod)
        importlib.invalidate_caches()
        rudisha fname

    eleza assert_traceback(self, tb, files):
        deduped_files = []
        wakati tb:
            code = tb.tb_frame.f_code
            fn = code.co_filename
            ikiwa sio deduped_files ama fn != deduped_files[-1]:
                deduped_files.append(fn)
            tb = tb.tb_next
        self.assertEqual(len(deduped_files), len(files), deduped_files)
        kila fn, pat kwenye zip(deduped_files, files):
            self.assertIn(pat, fn)

    eleza test_nonexistent_module(self):
        jaribu:
            # assertRaises() clears __traceback__
            agiza nonexistent_xyzzy
        tatizo ImportError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ImportError should have been raised")
        self.assert_traceback(tb, [__file__])

    eleza test_nonexistent_module_nested(self):
        self.create_module("foo", "agiza nonexistent_xyzzy")
        jaribu:
            agiza foo
        tatizo ImportError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ImportError should have been raised")
        self.assert_traceback(tb, [__file__, 'foo.py'])

    eleza test_exec_failure(self):
        self.create_module("foo", "1/0")
        jaribu:
            agiza foo
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ZeroDivisionError should have been raised")
        self.assert_traceback(tb, [__file__, 'foo.py'])

    eleza test_exec_failure_nested(self):
        self.create_module("foo", "agiza bar")
        self.create_module("bar", "1/0")
        jaribu:
            agiza foo
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ZeroDivisionError should have been raised")
        self.assert_traceback(tb, [__file__, 'foo.py', 'bar.py'])

    # A few more examples kutoka issue #15425
    eleza test_syntax_error(self):
        self.create_module("foo", "invalid syntax ni invalid")
        jaribu:
            agiza foo
        tatizo SyntaxError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("SyntaxError should have been raised")
        self.assert_traceback(tb, [__file__])

    eleza _setup_broken_package(self, parent, child):
        pkg_name = "_parent_foo"
        self.addCleanup(unload, pkg_name)
        pkg_path = os.path.join(TESTFN, pkg_name)
        os.mkdir(pkg_path)
        # Touch the __init__.py
        init_path = os.path.join(pkg_path, '__init__.py')
        ukijumuisha open(init_path, 'w') kama f:
            f.write(parent)
        bar_path = os.path.join(pkg_path, 'bar.py')
        ukijumuisha open(bar_path, 'w') kama f:
            f.write(child)
        importlib.invalidate_caches()
        rudisha init_path, bar_path

    eleza test_broken_submodule(self):
        init_path, bar_path = self._setup_broken_package("", "1/0")
        jaribu:
            agiza _parent_foo.bar
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ZeroDivisionError should have been raised")
        self.assert_traceback(tb, [__file__, bar_path])

    eleza test_broken_from(self):
        init_path, bar_path = self._setup_broken_package("", "1/0")
        jaribu:
            kutoka _parent_foo agiza bar
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ImportError should have been raised")
        self.assert_traceback(tb, [__file__, bar_path])

    eleza test_broken_parent(self):
        init_path, bar_path = self._setup_broken_package("1/0", "")
        jaribu:
            agiza _parent_foo.bar
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ZeroDivisionError should have been raised")
        self.assert_traceback(tb, [__file__, init_path])

    eleza test_broken_parent_from(self):
        init_path, bar_path = self._setup_broken_package("1/0", "")
        jaribu:
            kutoka _parent_foo agiza bar
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
        isipokua:
            self.fail("ZeroDivisionError should have been raised")
        self.assert_traceback(tb, [__file__, init_path])

    @cpython_only
    eleza test_import_bug(self):
        # We simulate a bug kwenye importlib na check that it's sio stripped
        # away kutoka the traceback.
        self.create_module("foo", "")
        importlib = sys.modules['_frozen_importlib_external']
        ikiwa 'load_module' kwenye vars(importlib.SourceLoader):
            old_exec_module = importlib.SourceLoader.exec_module
        isipokua:
            old_exec_module = Tupu
        jaribu:
            eleza exec_module(*args):
                1/0
            importlib.SourceLoader.exec_module = exec_module
            jaribu:
                agiza foo
            tatizo ZeroDivisionError kama e:
                tb = e.__traceback__
            isipokua:
                self.fail("ZeroDivisionError should have been raised")
            self.assert_traceback(tb, [__file__, '<frozen importlib', __file__])
        mwishowe:
            ikiwa old_exec_module ni Tupu:
                toa importlib.SourceLoader.exec_module
            isipokua:
                importlib.SourceLoader.exec_module = old_exec_module

    @unittest.skipUnless(TESTFN_UNENCODABLE, 'need TESTFN_UNENCODABLE')
    eleza test_unencodable_filename(self):
        # Issue #11619: The Python parser na the agiza machinery must sio
        # encode filenames, especially on Windows
        pyname = script_helper.make_script('', TESTFN_UNENCODABLE, 'pita')
        self.addCleanup(unlink, pyname)
        name = pyname[:-3]
        script_helper.assert_python_ok("-c", "mod = __import__(%a)" % name,
                                       __isolated=Uongo)


kundi CircularImportTests(unittest.TestCase):

    """See the docstrings of the modules being imported kila the purpose of the
    test."""

    eleza tearDown(self):
        """Make sure no modules pre-exist kwenye sys.modules which are being used to
        test."""
        kila key kwenye list(sys.modules.keys()):
            ikiwa key.startswith('test.test_import.data.circular_imports'):
                toa sys.modules[key]

    eleza test_direct(self):
        jaribu:
            agiza test.test_import.data.circular_imports.basic
        tatizo ImportError:
            self.fail('circular agiza through relative imports failed')

    eleza test_indirect(self):
        jaribu:
            agiza test.test_import.data.circular_imports.indirect
        tatizo ImportError:
            self.fail('relative agiza kwenye module contributing to circular '
                      'agiza failed')

    eleza test_subpackage(self):
        jaribu:
            agiza test.test_import.data.circular_imports.subpackage
        tatizo ImportError:
            self.fail('circular agiza involving a subpackage failed')

    eleza test_rebinding(self):
        jaribu:
            agiza test.test_import.data.circular_imports.rebinding kama rebinding
        tatizo ImportError:
            self.fail('circular agiza ukijumuisha rebinding of module attribute failed')
        kutoka test.test_import.data.circular_imports.subpkg agiza util
        self.assertIs(util.util, rebinding.util)

    eleza test_binding(self):
        jaribu:
            agiza test.test_import.data.circular_imports.binding
        tatizo ImportError:
            self.fail('circular agiza ukijumuisha binding a submodule to a name failed')

    eleza test_crossreference1(self):
        agiza test.test_import.data.circular_imports.use
        agiza test.test_import.data.circular_imports.source

    eleza test_crossreference2(self):
        ukijumuisha self.assertRaises(AttributeError) kama cm:
            agiza test.test_import.data.circular_imports.source
        errmsg = str(cm.exception)
        self.assertIn('test.test_import.data.circular_imports.source', errmsg)
        self.assertIn('spam', errmsg)
        self.assertIn('partially initialized module', errmsg)
        self.assertIn('circular import', errmsg)

    eleza test_circular_from_import(self):
        ukijumuisha self.assertRaises(ImportError) kama cm:
            agiza test.test_import.data.circular_imports.from_cycle1
        self.assertIn(
            "cansio agiza name 'b' kutoka partially initialized module "
            "'test.test_import.data.circular_imports.from_cycle1' "
            "(most likely due to a circular import)",
            str(cm.exception),
        )


ikiwa __name__ == '__main__':
    # Test needs to be a package, so we can do relative imports.
    unittest.main()
