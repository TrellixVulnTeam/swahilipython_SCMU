agiza builtins
agiza os
agiza select
agiza socket
agiza unittest
agiza errno
kutoka errno agiza EEXIST


kundi SubOSError(OSError):
    pass

kundi SubOSErrorWithInit(OSError):
    eleza __init__(self, message, bar):
        self.bar = bar
        super().__init__(message)

kundi SubOSErrorWithNew(OSError):
    eleza __new__(cls, message, baz):
        self = super().__new__(cls, message)
        self.baz = baz
        rudisha self

kundi SubOSErrorCombinedInitFirst(SubOSErrorWithInit, SubOSErrorWithNew):
    pass

kundi SubOSErrorCombinedNewFirst(SubOSErrorWithNew, SubOSErrorWithInit):
    pass

kundi SubOSErrorWithStandaloneInit(OSError):
    eleza __init__(self):
        pass


kundi HierarchyTest(unittest.TestCase):

    eleza test_builtin_errors(self):
        self.assertEqual(OSError.__name__, 'OSError')
        self.assertIs(IOError, OSError)
        self.assertIs(EnvironmentError, OSError)

    eleza test_socket_errors(self):
        self.assertIs(socket.error, IOError)
        self.assertIs(socket.gaierror.__base__, OSError)
        self.assertIs(socket.herror.__base__, OSError)
        self.assertIs(socket.timeout.__base__, OSError)

    eleza test_select_error(self):
        self.assertIs(select.error, OSError)

    # mmap.error is tested in test_mmap

    _pep_map = """
        +-- BlockingIOError        EAGAIN, EALREADY, EWOULDBLOCK, EINPROGRESS
        +-- ChildProcessError                                          ECHILD
        +-- ConnectionError
            +-- BrokenPipeError                              EPIPE, ESHUTDOWN
            +-- ConnectionAbortedError                           ECONNABORTED
            +-- ConnectionRefusedError                           ECONNREFUSED
            +-- ConnectionResetError                               ECONNRESET
        +-- FileExistsError                                            EEXIST
        +-- FileNotFoundError                                          ENOENT
        +-- InterruptedError                                            EINTR
        +-- IsADirectoryError                                          EISDIR
        +-- NotADirectoryError                                        ENOTDIR
        +-- PermissionError                                     EACCES, EPERM
        +-- ProcessLookupError                                          ESRCH
        +-- TimeoutError                                            ETIMEDOUT
    """
    eleza _make_map(s):
        _map = {}
        for line in s.splitlines():
            line = line.strip('+- ')
            ikiwa not line:
                continue
            excname, _, errnames = line.partition(' ')
            for errname in filter(None, errnames.strip().split(', ')):
                _map[getattr(errno, errname)] = getattr(builtins, excname)
        rudisha _map
    _map = _make_map(_pep_map)

    eleza test_errno_mapping(self):
        # The OSError constructor maps errnos to subclasses
        # A sample test for the basic functionality
        e = OSError(EEXIST, "Bad file descriptor")
        self.assertIs(type(e), FileExistsError)
        # Exhaustive testing
        for errcode, exc in self._map.items():
            e = OSError(errcode, "Some message")
            self.assertIs(type(e), exc)
        othercodes = set(errno.errorcode) - set(self._map)
        for errcode in othercodes:
            e = OSError(errcode, "Some message")
            self.assertIs(type(e), OSError)

    eleza test_try_except(self):
        filename = "some_hopefully_non_existing_file"

        # This checks that try .. except checks the concrete exception
        # (FileNotFoundError) and not the base type specified when
        # PyErr_SetFromErrnoWithFilenameObject was called.
        # (it is therefore deliberate that it doesn't use assertRaises)
        try:
            open(filename)
        except FileNotFoundError:
            pass
        else:
            self.fail("should have raised a FileNotFoundError")

        # Another test for PyErr_SetExcFromWindowsErrWithFilenameObject()
        self.assertFalse(os.path.exists(filename))
        try:
            os.unlink(filename)
        except FileNotFoundError:
            pass
        else:
            self.fail("should have raised a FileNotFoundError")


kundi AttributesTest(unittest.TestCase):

    eleza test_windows_error(self):
        ikiwa os.name == "nt":
            self.assertIn('winerror', dir(OSError))
        else:
            self.assertNotIn('winerror', dir(OSError))

    eleza test_posix_error(self):
        e = OSError(EEXIST, "File already exists", "foo.txt")
        self.assertEqual(e.errno, EEXIST)
        self.assertEqual(e.args[0], EEXIST)
        self.assertEqual(e.strerror, "File already exists")
        self.assertEqual(e.filename, "foo.txt")
        ikiwa os.name == "nt":
            self.assertEqual(e.winerror, None)

    @unittest.skipUnless(os.name == "nt", "Windows-specific test")
    eleza test_errno_translation(self):
        # ERROR_ALREADY_EXISTS (183) -> EEXIST
        e = OSError(0, "File already exists", "foo.txt", 183)
        self.assertEqual(e.winerror, 183)
        self.assertEqual(e.errno, EEXIST)
        self.assertEqual(e.args[0], EEXIST)
        self.assertEqual(e.strerror, "File already exists")
        self.assertEqual(e.filename, "foo.txt")

    eleza test_blockingioerror(self):
        args = ("a", "b", "c", "d", "e")
        for n in range(6):
            e = BlockingIOError(*args[:n])
            with self.assertRaises(AttributeError):
                e.characters_written
            with self.assertRaises(AttributeError):
                del e.characters_written
        e = BlockingIOError("a", "b", 3)
        self.assertEqual(e.characters_written, 3)
        e.characters_written = 5
        self.assertEqual(e.characters_written, 5)
        del e.characters_written
        with self.assertRaises(AttributeError):
            e.characters_written


kundi ExplicitSubclassingTest(unittest.TestCase):

    eleza test_errno_mapping(self):
        # When constructing an OSError subclass, errno mapping isn't done
        e = SubOSError(EEXIST, "Bad file descriptor")
        self.assertIs(type(e), SubOSError)

    eleza test_init_overridden(self):
        e = SubOSErrorWithInit("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.args, ("some message",))

    eleza test_init_kwdargs(self):
        e = SubOSErrorWithInit("some message", bar="baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.args, ("some message",))

    eleza test_new_overridden(self):
        e = SubOSErrorWithNew("some message", "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    eleza test_new_kwdargs(self):
        e = SubOSErrorWithNew("some message", baz="baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    eleza test_init_new_overridden(self):
        e = SubOSErrorCombinedInitFirst("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))
        e = SubOSErrorCombinedNewFirst("some message", "baz")
        self.assertEqual(e.bar, "baz")
        self.assertEqual(e.baz, "baz")
        self.assertEqual(e.args, ("some message",))

    eleza test_init_standalone(self):
        # __init__ doesn't propagate to OSError.__init__ (see issue #15229)
        e = SubOSErrorWithStandaloneInit()
        self.assertEqual(e.args, ())
        self.assertEqual(str(e), '')


ikiwa __name__ == "__main__":
    unittest.main()
