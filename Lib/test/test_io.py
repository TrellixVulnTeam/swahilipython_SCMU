"""Unit tests kila the io module."""

# Tests of io are scattered over the test suite:
# * test_bufio - tests file buffering
# * test_memoryio - tests BytesIO na StringIO
# * test_fileio - tests FileIO
# * test_file - tests the file interface
# * test_io - tests everything isipokua kwenye the io module
# * test_univnewlines - tests universal newline support
# * test_largefile - tests operations on a file greater than 2**32 bytes
#     (only enabled ukijumuisha -ulargefile)

################################################################################
# ATTENTION TEST WRITERS!!!
################################################################################
# When writing tests kila io, it's important to test both the C na Python
# implementations. This ni usually done by writing a base test that refers to
# the type it ni testing as an attribute. Then it provides custom subclasses to
# test both implementations. This file has lots of examples.
################################################################################

agiza abc
agiza array
agiza errno
agiza locale
agiza os
agiza pickle
agiza random
agiza signal
agiza sys
agiza sysconfig
agiza threading
agiza time
agiza unittest
agiza warnings
agiza weakref
kutoka collections agiza deque, UserList
kutoka itertools agiza cycle, count
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok, run_python_until_end
kutoka test.support agiza FakePath

agiza codecs
agiza io  # C implementation of io
agiza _pyio as pyio # Python implementation of io

jaribu:
    agiza ctypes
except ImportError:
    eleza byteslike(*pos, **kw):
        rudisha array.array("b", bytes(*pos, **kw))
isipokua:
    eleza byteslike(*pos, **kw):
        """Create a bytes-like object having no string ama sequence methods"""
        data = bytes(*pos, **kw)
        obj = EmptyStruct()
        ctypes.resize(obj, len(data))
        memoryview(obj).cast("B")[:] = data
        rudisha obj
    kundi EmptyStruct(ctypes.Structure):
        pass

_cflags = sysconfig.get_config_var('CFLAGS') ama ''
_config_args = sysconfig.get_config_var('CONFIG_ARGS') ama ''
MEMORY_SANITIZER = (
    '-fsanitize=memory' kwenye _cflags or
    '--with-memory-sanitizer' kwenye _config_args
)

# Does io.IOBase finalizer log the exception ikiwa the close() method fails?
# The exception ni ignored silently by default kwenye release build.
IOBASE_EMITS_UNRAISABLE = (hasattr(sys, "gettotalrefcount") ama sys.flags.dev_mode)


eleza _default_chunk_size():
    """Get the default TextIOWrapper chunk size"""
    ukijumuisha open(__file__, "r", encoding="latin-1") as f:
        rudisha f._CHUNK_SIZE


kundi MockRawIOWithoutRead:
    """A RawIO implementation without read(), so as to exercise the default
    RawIO.read() which calls readinto()."""

    eleza __init__(self, read_stack=()):
        self._read_stack = list(read_stack)
        self._write_stack = []
        self._reads = 0
        self._extraneous_reads = 0

    eleza write(self, b):
        self._write_stack.append(bytes(b))
        rudisha len(b)

    eleza writable(self):
        rudisha Kweli

    eleza fileno(self):
        rudisha 42

    eleza readable(self):
        rudisha Kweli

    eleza seekable(self):
        rudisha Kweli

    eleza seek(self, pos, whence):
        rudisha 0   # wrong but we gotta rudisha something

    eleza tell(self):
        rudisha 0   # same comment as above

    eleza readinto(self, buf):
        self._reads += 1
        max_len = len(buf)
        jaribu:
            data = self._read_stack[0]
        except IndexError:
            self._extraneous_reads += 1
            rudisha 0
        ikiwa data ni Tupu:
            toa self._read_stack[0]
            rudisha Tupu
        n = len(data)
        ikiwa len(data) <= max_len:
            toa self._read_stack[0]
            buf[:n] = data
            rudisha n
        isipokua:
            buf[:] = data[:max_len]
            self._read_stack[0] = data[max_len:]
            rudisha max_len

    eleza truncate(self, pos=Tupu):
        rudisha pos

kundi CMockRawIOWithoutRead(MockRawIOWithoutRead, io.RawIOBase):
    pass

kundi PyMockRawIOWithoutRead(MockRawIOWithoutRead, pyio.RawIOBase):
    pass


kundi MockRawIO(MockRawIOWithoutRead):

    eleza read(self, n=Tupu):
        self._reads += 1
        jaribu:
            rudisha self._read_stack.pop(0)
        tatizo:
            self._extraneous_reads += 1
            rudisha b""

kundi CMockRawIO(MockRawIO, io.RawIOBase):
    pass

kundi PyMockRawIO(MockRawIO, pyio.RawIOBase):
    pass


kundi MisbehavedRawIO(MockRawIO):
    eleza write(self, b):
        rudisha super().write(b) * 2

    eleza read(self, n=Tupu):
        rudisha super().read(n) * 2

    eleza seek(self, pos, whence):
        rudisha -123

    eleza tell(self):
        rudisha -456

    eleza readinto(self, buf):
        super().readinto(buf)
        rudisha len(buf) * 5

kundi CMisbehavedRawIO(MisbehavedRawIO, io.RawIOBase):
    pass

kundi PyMisbehavedRawIO(MisbehavedRawIO, pyio.RawIOBase):
    pass


kundi SlowFlushRawIO(MockRawIO):
    eleza __init__(self):
        super().__init__()
        self.in_flush = threading.Event()

    eleza flush(self):
        self.in_flush.set()
        time.sleep(0.25)

kundi CSlowFlushRawIO(SlowFlushRawIO, io.RawIOBase):
    pass

kundi PySlowFlushRawIO(SlowFlushRawIO, pyio.RawIOBase):
    pass


kundi CloseFailureIO(MockRawIO):
    closed = 0

    eleza close(self):
        ikiwa sio self.closed:
            self.closed = 1
             ashiria OSError

kundi CCloseFailureIO(CloseFailureIO, io.RawIOBase):
    pass

kundi PyCloseFailureIO(CloseFailureIO, pyio.RawIOBase):
    pass


kundi MockFileIO:

    eleza __init__(self, data):
        self.read_history = []
        super().__init__(data)

    eleza read(self, n=Tupu):
        res = super().read(n)
        self.read_history.append(Tupu ikiwa res ni Tupu isipokua len(res))
        rudisha res

    eleza readinto(self, b):
        res = super().readinto(b)
        self.read_history.append(res)
        rudisha res

kundi CMockFileIO(MockFileIO, io.BytesIO):
    pass

kundi PyMockFileIO(MockFileIO, pyio.BytesIO):
    pass


kundi MockUnseekableIO:
    eleza seekable(self):
        rudisha Uongo

    eleza seek(self, *args):
         ashiria self.UnsupportedOperation("not seekable")

    eleza tell(self, *args):
         ashiria self.UnsupportedOperation("not seekable")

    eleza truncate(self, *args):
         ashiria self.UnsupportedOperation("not seekable")

kundi CMockUnseekableIO(MockUnseekableIO, io.BytesIO):
    UnsupportedOperation = io.UnsupportedOperation

kundi PyMockUnseekableIO(MockUnseekableIO, pyio.BytesIO):
    UnsupportedOperation = pyio.UnsupportedOperation


kundi MockNonBlockWriterIO:

    eleza __init__(self):
        self._write_stack = []
        self._blocker_char = Tupu

    eleza pop_written(self):
        s = b"".join(self._write_stack)
        self._write_stack[:] = []
        rudisha s

    eleza block_on(self, char):
        """Block when a given char ni encountered."""
        self._blocker_char = char

    eleza readable(self):
        rudisha Kweli

    eleza seekable(self):
        rudisha Kweli

    eleza seek(self, pos, whence=0):
        # naive implementation, enough kila tests
        rudisha 0

    eleza writable(self):
        rudisha Kweli

    eleza write(self, b):
        b = bytes(b)
        n = -1
        ikiwa self._blocker_char:
            jaribu:
                n = b.index(self._blocker_char)
            except ValueError:
                pass
            isipokua:
                ikiwa n > 0:
                    # write data up to the first blocker
                    self._write_stack.append(b[:n])
                    rudisha n
                isipokua:
                    # cancel blocker na indicate would block
                    self._blocker_char = Tupu
                    rudisha Tupu
        self._write_stack.append(b)
        rudisha len(b)

kundi CMockNonBlockWriterIO(MockNonBlockWriterIO, io.RawIOBase):
    BlockingIOError = io.BlockingIOError

kundi PyMockNonBlockWriterIO(MockNonBlockWriterIO, pyio.RawIOBase):
    BlockingIOError = pyio.BlockingIOError


kundi IOTest(unittest.TestCase):

    eleza setUp(self):
        support.unlink(support.TESTFN)

    eleza tearDown(self):
        support.unlink(support.TESTFN)

    eleza write_ops(self, f):
        self.assertEqual(f.write(b"blah."), 5)
        f.truncate(0)
        self.assertEqual(f.tell(), 5)
        f.seek(0)

        self.assertEqual(f.write(b"blah."), 5)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"Hello."), 6)
        self.assertEqual(f.tell(), 6)
        self.assertEqual(f.seek(-1, 1), 5)
        self.assertEqual(f.tell(), 5)
        buffer = bytearray(b" world\n\n\n")
        self.assertEqual(f.write(buffer), 9)
        buffer[:] = b"*" * 9  # Overwrite our copy of the data
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(b"h"), 1)
        self.assertEqual(f.seek(-1, 2), 13)
        self.assertEqual(f.tell(), 13)

        self.assertEqual(f.truncate(12), 12)
        self.assertEqual(f.tell(), 13)
        self.assertRaises(TypeError, f.seek, 0.0)

    eleza read_ops(self, f, buffered=Uongo):
        data = f.read(5)
        self.assertEqual(data, b"hello")
        data = byteslike(data)
        self.assertEqual(f.readinto(data), 5)
        self.assertEqual(bytes(data), b" worl")
        data = bytearray(5)
        self.assertEqual(f.readinto(data), 2)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[:2], b"d\n")
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.read(20), b"hello world\n")
        self.assertEqual(f.read(1), b"")
        self.assertEqual(f.readinto(byteslike(b"x")), 0)
        self.assertEqual(f.seek(-6, 2), 6)
        self.assertEqual(f.read(5), b"world")
        self.assertEqual(f.read(0), b"")
        self.assertEqual(f.readinto(byteslike()), 0)
        self.assertEqual(f.seek(-6, 1), 5)
        self.assertEqual(f.read(5), b" worl")
        self.assertEqual(f.tell(), 10)
        self.assertRaises(TypeError, f.seek, 0.0)
        ikiwa buffered:
            f.seek(0)
            self.assertEqual(f.read(), b"hello world\n")
            f.seek(6)
            self.assertEqual(f.read(), b"world\n")
            self.assertEqual(f.read(), b"")
            f.seek(0)
            data = byteslike(5)
            self.assertEqual(f.readinto1(data), 5)
            self.assertEqual(bytes(data), b"hello")

    LARGE = 2**31

    eleza large_file_ops(self, f):
        assert f.readable()
        assert f.writable()
        jaribu:
            self.assertEqual(f.seek(self.LARGE), self.LARGE)
        except (OverflowError, ValueError):
            self.skipTest("no largefile support")
        self.assertEqual(f.tell(), self.LARGE)
        self.assertEqual(f.write(b"xxx"), 3)
        self.assertEqual(f.tell(), self.LARGE + 3)
        self.assertEqual(f.seek(-1, 1), self.LARGE + 2)
        self.assertEqual(f.truncate(), self.LARGE + 2)
        self.assertEqual(f.tell(), self.LARGE + 2)
        self.assertEqual(f.seek(0, 2), self.LARGE + 2)
        self.assertEqual(f.truncate(self.LARGE + 1), self.LARGE + 1)
        self.assertEqual(f.tell(), self.LARGE + 2)
        self.assertEqual(f.seek(0, 2), self.LARGE + 1)
        self.assertEqual(f.seek(-1, 2), self.LARGE)
        self.assertEqual(f.read(2), b"x")

    eleza test_invalid_operations(self):
        # Try writing on a file opened kwenye read mode na vice-versa.
        exc = self.UnsupportedOperation
        kila mode kwenye ("w", "wb"):
            ukijumuisha self.open(support.TESTFN, mode) as fp:
                self.assertRaises(exc, fp.read)
                self.assertRaises(exc, fp.readline)
        ukijumuisha self.open(support.TESTFN, "wb", buffering=0) as fp:
            self.assertRaises(exc, fp.read)
            self.assertRaises(exc, fp.readline)
        ukijumuisha self.open(support.TESTFN, "rb", buffering=0) as fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        ukijumuisha self.open(support.TESTFN, "rb") as fp:
            self.assertRaises(exc, fp.write, b"blah")
            self.assertRaises(exc, fp.writelines, [b"blah\n"])
        ukijumuisha self.open(support.TESTFN, "r") as fp:
            self.assertRaises(exc, fp.write, "blah")
            self.assertRaises(exc, fp.writelines, ["blah\n"])
            # Non-zero seeking kutoka current ama end pos
            self.assertRaises(exc, fp.seek, 1, self.SEEK_CUR)
            self.assertRaises(exc, fp.seek, -1, self.SEEK_END)

    eleza test_optional_abilities(self):
        # Test kila OSError when optional APIs are sio supported
        # The purpose of this test ni to try fileno(), reading, writing and
        # seeking operations ukijumuisha various objects that indicate they do not
        # support these operations.

        eleza pipe_reader():
            [r, w] = os.pipe()
            os.close(w)  # So that read() ni harmless
            rudisha self.FileIO(r, "r")

        eleza pipe_writer():
            [r, w] = os.pipe()
            self.addCleanup(os.close, r)
            # Guarantee that we can write into the pipe without blocking
            thread = threading.Thread(target=os.read, args=(r, 100))
            thread.start()
            self.addCleanup(thread.join)
            rudisha self.FileIO(w, "w")

        eleza buffered_reader():
            rudisha self.BufferedReader(self.MockUnseekableIO())

        eleza buffered_writer():
            rudisha self.BufferedWriter(self.MockUnseekableIO())

        eleza buffered_random():
            rudisha self.BufferedRandom(self.BytesIO())

        eleza buffered_rw_pair():
            rudisha self.BufferedRWPair(self.MockUnseekableIO(),
                self.MockUnseekableIO())

        eleza text_reader():
            kundi UnseekableReader(self.MockUnseekableIO):
                writable = self.BufferedIOBase.writable
                write = self.BufferedIOBase.write
            rudisha self.TextIOWrapper(UnseekableReader(), "ascii")

        eleza text_writer():
            kundi UnseekableWriter(self.MockUnseekableIO):
                readable = self.BufferedIOBase.readable
                read = self.BufferedIOBase.read
            rudisha self.TextIOWrapper(UnseekableWriter(), "ascii")

        tests = (
            (pipe_reader, "fr"), (pipe_writer, "fw"),
            (buffered_reader, "r"), (buffered_writer, "w"),
            (buffered_random, "rws"), (buffered_rw_pair, "rw"),
            (text_reader, "r"), (text_writer, "w"),
            (self.BytesIO, "rws"), (self.StringIO, "rws"),
        )
        kila [test, abilities] kwenye tests:
            ukijumuisha self.subTest(test), test() as obj:
                readable = "r" kwenye abilities
                self.assertEqual(obj.readable(), readable)
                writable = "w" kwenye abilities
                self.assertEqual(obj.writable(), writable)

                ikiwa isinstance(obj, self.TextIOBase):
                    data = "3"
                elikiwa isinstance(obj, (self.BufferedIOBase, self.RawIOBase)):
                    data = b"3"
                isipokua:
                    self.fail("Unknown base class")

                ikiwa "f" kwenye abilities:
                    obj.fileno()
                isipokua:
                    self.assertRaises(OSError, obj.fileno)

                ikiwa readable:
                    obj.read(1)
                    obj.read()
                isipokua:
                    self.assertRaises(OSError, obj.read, 1)
                    self.assertRaises(OSError, obj.read)

                ikiwa writable:
                    obj.write(data)
                isipokua:
                    self.assertRaises(OSError, obj.write, data)

                ikiwa sys.platform.startswith("win") na test kwenye (
                        pipe_reader, pipe_writer):
                    # Pipes seem to appear as seekable on Windows
                    endelea
                seekable = "s" kwenye abilities
                self.assertEqual(obj.seekable(), seekable)

                ikiwa seekable:
                    obj.tell()
                    obj.seek(0)
                isipokua:
                    self.assertRaises(OSError, obj.tell)
                    self.assertRaises(OSError, obj.seek, 0)

                ikiwa writable na seekable:
                    obj.truncate()
                    obj.truncate(0)
                isipokua:
                    self.assertRaises(OSError, obj.truncate)
                    self.assertRaises(OSError, obj.truncate, 0)

    eleza test_open_handles_NUL_chars(self):
        fn_with_NUL = 'foo\0bar'
        self.assertRaises(ValueError, self.open, fn_with_NUL, 'w')

        bytes_fn = bytes(fn_with_NUL, 'ascii')
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertRaises(ValueError, self.open, bytes_fn, 'w')

    eleza test_raw_file_io(self):
        ukijumuisha self.open(support.TESTFN, "wb", buffering=0) as f:
            self.assertEqual(f.readable(), Uongo)
            self.assertEqual(f.writable(), Kweli)
            self.assertEqual(f.seekable(), Kweli)
            self.write_ops(f)
        ukijumuisha self.open(support.TESTFN, "rb", buffering=0) as f:
            self.assertEqual(f.readable(), Kweli)
            self.assertEqual(f.writable(), Uongo)
            self.assertEqual(f.seekable(), Kweli)
            self.read_ops(f)

    eleza test_buffered_file_io(self):
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            self.assertEqual(f.readable(), Uongo)
            self.assertEqual(f.writable(), Kweli)
            self.assertEqual(f.seekable(), Kweli)
            self.write_ops(f)
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.readable(), Kweli)
            self.assertEqual(f.writable(), Uongo)
            self.assertEqual(f.seekable(), Kweli)
            self.read_ops(f, Kweli)

    eleza test_readline(self):
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(b"abc\ndef\nxyzzy\nfoo\x00bar\nanother line")
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.readline(), b"abc\n")
            self.assertEqual(f.readline(10), b"def\n")
            self.assertEqual(f.readline(2), b"xy")
            self.assertEqual(f.readline(4), b"zzy\n")
            self.assertEqual(f.readline(), b"foo\x00bar\n")
            self.assertEqual(f.readline(Tupu), b"another line")
            self.assertRaises(TypeError, f.readline, 5.3)
        ukijumuisha self.open(support.TESTFN, "r") as f:
            self.assertRaises(TypeError, f.readline, 5.3)

    eleza test_readline_nonsizeable(self):
        # Issue #30061
        # Crash when readline() returns an object without __len__
        kundi R(self.IOBase):
            eleza readline(self):
                rudisha Tupu
        self.assertRaises((TypeError, StopIteration), next, R())

    eleza test_next_nonsizeable(self):
        # Issue #30061
        # Crash when __next__() returns an object without __len__
        kundi R(self.IOBase):
            eleza __next__(self):
                rudisha Tupu
        self.assertRaises(TypeError, R().readlines, 1)

    eleza test_raw_bytes_io(self):
        f = self.BytesIO()
        self.write_ops(f)
        data = f.getvalue()
        self.assertEqual(data, b"hello world\n")
        f = self.BytesIO(data)
        self.read_ops(f, Kweli)

    eleza test_large_file_ops(self):
        # On Windows na Mac OSX this test consumes large resources; It takes
        # a long time to build the >2 GiB file na takes >2 GiB of disk space
        # therefore the resource must be enabled to run this test.
        ikiwa sys.platform[:3] == 'win' ama sys.platform == 'darwin':
            support.requires(
                'largefile',
                'test requires %s bytes na a long time to run' % self.LARGE)
        ukijumuisha self.open(support.TESTFN, "w+b", 0) as f:
            self.large_file_ops(f)
        ukijumuisha self.open(support.TESTFN, "w+b") as f:
            self.large_file_ops(f)

    eleza test_with_open(self):
        kila bufsize kwenye (0, 100):
            f = Tupu
            ukijumuisha self.open(support.TESTFN, "wb", bufsize) as f:
                f.write(b"xxx")
            self.assertEqual(f.closed, Kweli)
            f = Tupu
            jaribu:
                ukijumuisha self.open(support.TESTFN, "wb", bufsize) as f:
                    1/0
            except ZeroDivisionError:
                self.assertEqual(f.closed, Kweli)
            isipokua:
                self.fail("1/0 didn't  ashiria an exception")

    # issue 5008
    eleza test_append_mode_tell(self):
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(b"xxx")
        ukijumuisha self.open(support.TESTFN, "ab", buffering=0) as f:
            self.assertEqual(f.tell(), 3)
        ukijumuisha self.open(support.TESTFN, "ab") as f:
            self.assertEqual(f.tell(), 3)
        ukijumuisha self.open(support.TESTFN, "a") as f:
            self.assertGreater(f.tell(), 0)

    eleza test_destructor(self):
        record = []
        kundi MyFileIO(self.FileIO):
            eleza __del__(self):
                record.append(1)
                jaribu:
                    f = super().__del__
                except AttributeError:
                    pass
                isipokua:
                    f()
            eleza close(self):
                record.append(2)
                super().close()
            eleza flush(self):
                record.append(3)
                super().flush()
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            f = MyFileIO(support.TESTFN, "wb")
            f.write(b"xxx")
            toa f
            support.gc_collect()
            self.assertEqual(record, [1, 2, 3])
            ukijumuisha self.open(support.TESTFN, "rb") as f:
                self.assertEqual(f.read(), b"xxx")

    eleza _check_base_destructor(self, base):
        record = []
        kundi MyIO(base):
            eleza __init__(self):
                # This exercises the availability of attributes on object
                # destruction.
                # (in the C version, close() ni called by the tp_dealloc
                # function, sio by __del__)
                self.on_toa = 1
                self.on_close = 2
                self.on_flush = 3
            eleza __del__(self):
                record.append(self.on_del)
                jaribu:
                    f = super().__del__
                except AttributeError:
                    pass
                isipokua:
                    f()
            eleza close(self):
                record.append(self.on_close)
                super().close()
            eleza flush(self):
                record.append(self.on_flush)
                super().flush()
        f = MyIO()
        toa f
        support.gc_collect()
        self.assertEqual(record, [1, 2, 3])

    eleza test_IOBase_destructor(self):
        self._check_base_destructor(self.IOBase)

    eleza test_RawIOBase_destructor(self):
        self._check_base_destructor(self.RawIOBase)

    eleza test_BufferedIOBase_destructor(self):
        self._check_base_destructor(self.BufferedIOBase)

    eleza test_TextIOBase_destructor(self):
        self._check_base_destructor(self.TextIOBase)

    eleza test_close_flushes(self):
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(b"xxx")
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"xxx")

    eleza test_array_writes(self):
        a = array.array('i', range(10))
        n = len(a.tobytes())
        eleza check(f):
            ukijumuisha f:
                self.assertEqual(f.write(a), n)
                f.writelines((a,))
        check(self.BytesIO())
        check(self.FileIO(support.TESTFN, "w"))
        check(self.BufferedWriter(self.MockRawIO()))
        check(self.BufferedRandom(self.MockRawIO()))
        check(self.BufferedRWPair(self.MockRawIO(), self.MockRawIO()))

    eleza test_closefd(self):
        self.assertRaises(ValueError, self.open, support.TESTFN, 'w',
                          closefd=Uongo)

    eleza test_read_closed(self):
        ukijumuisha self.open(support.TESTFN, "w") as f:
            f.write("egg\n")
        ukijumuisha self.open(support.TESTFN, "r") as f:
            file = self.open(f.fileno(), "r", closefd=Uongo)
            self.assertEqual(file.read(), "egg\n")
            file.seek(0)
            file.close()
            self.assertRaises(ValueError, file.read)

    eleza test_no_closefd_with_filename(self):
        # can't use closefd kwenye combination ukijumuisha a file name
        self.assertRaises(ValueError, self.open, support.TESTFN, "r", closefd=Uongo)

    eleza test_closefd_attr(self):
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(b"egg\n")
        ukijumuisha self.open(support.TESTFN, "r") as f:
            self.assertEqual(f.buffer.raw.closefd, Kweli)
            file = self.open(f.fileno(), "r", closefd=Uongo)
            self.assertEqual(file.buffer.raw.closefd, Uongo)

    eleza test_garbage_collection(self):
        # FileIO objects are collected, na collecting them flushes
        # all data to disk.
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            f = self.FileIO(support.TESTFN, "wb")
            f.write(b"abcxxx")
            f.f = f
            wr = weakref.ref(f)
            toa f
            support.gc_collect()
        self.assertIsTupu(wr(), wr)
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"abcxxx")

    eleza test_unbounded_file(self):
        # Issue #1174606: reading kutoka an unbounded stream such as /dev/zero.
        zero = "/dev/zero"
        ikiwa sio os.path.exists(zero):
            self.skipTest("{0} does sio exist".format(zero))
        ikiwa sys.maxsize > 0x7FFFFFFF:
            self.skipTest("test can only run kwenye a 32-bit address space")
        ikiwa support.real_max_memuse < support._2G:
            self.skipTest("test requires at least 2 GiB of memory")
        ukijumuisha self.open(zero, "rb", buffering=0) as f:
            self.assertRaises(OverflowError, f.read)
        ukijumuisha self.open(zero, "rb") as f:
            self.assertRaises(OverflowError, f.read)
        ukijumuisha self.open(zero, "r") as f:
            self.assertRaises(OverflowError, f.read)

    eleza check_flush_error_on_close(self, *args, **kwargs):
        # Test that the file ni closed despite failed flush
        # na that flush() ni called before file closed.
        f = self.open(*args, **kwargs)
        closed = []
        eleza bad_flush():
            closed[:] = [f.closed]
             ashiria OSError()
        f.flush = bad_flush
        self.assertRaises(OSError, f.close) # exception sio swallowed
        self.assertKweli(f.closed)
        self.assertKweli(closed)      # flush() called
        self.assertUongo(closed[0])  # flush() called before file closed
        f.flush = lambda: Tupu  # koma reference loop

    eleza test_flush_error_on_close(self):
        # raw file
        # Issue #5700: io.FileIO calls flush() after file closed
        self.check_flush_error_on_close(support.TESTFN, 'wb', buffering=0)
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', buffering=0)
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', buffering=0, closefd=Uongo)
        os.close(fd)
        # buffered io
        self.check_flush_error_on_close(support.TESTFN, 'wb')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'wb', closefd=Uongo)
        os.close(fd)
        # text io
        self.check_flush_error_on_close(support.TESTFN, 'w')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'w')
        fd = os.open(support.TESTFN, os.O_WRONLY|os.O_CREAT)
        self.check_flush_error_on_close(fd, 'w', closefd=Uongo)
        os.close(fd)

    eleza test_multi_close(self):
        f = self.open(support.TESTFN, "wb", buffering=0)
        f.close()
        f.close()
        f.close()
        self.assertRaises(ValueError, f.flush)

    eleza test_RawIOBase_read(self):
        # Exercise the default limited RawIOBase.read(n) implementation (which
        # calls readinto() internally).
        rawio = self.MockRawIOWithoutRead((b"abc", b"d", Tupu, b"efg", Tupu))
        self.assertEqual(rawio.read(2), b"ab")
        self.assertEqual(rawio.read(2), b"c")
        self.assertEqual(rawio.read(2), b"d")
        self.assertEqual(rawio.read(2), Tupu)
        self.assertEqual(rawio.read(2), b"ef")
        self.assertEqual(rawio.read(2), b"g")
        self.assertEqual(rawio.read(2), Tupu)
        self.assertEqual(rawio.read(2), b"")

    eleza test_types_have_dict(self):
        test = (
            self.IOBase(),
            self.RawIOBase(),
            self.TextIOBase(),
            self.StringIO(),
            self.BytesIO()
        )
        kila obj kwenye test:
            self.assertKweli(hasattr(obj, "__dict__"))

    eleza test_opener(self):
        ukijumuisha self.open(support.TESTFN, "w") as f:
            f.write("egg\n")
        fd = os.open(support.TESTFN, os.O_RDONLY)
        eleza opener(path, flags):
            rudisha fd
        ukijumuisha self.open("non-existent", "r", opener=opener) as f:
            self.assertEqual(f.read(), "egg\n")

    eleza test_bad_opener_negative_1(self):
        # Issue #27066.
        eleza badopener(fname, flags):
            rudisha -1
        ukijumuisha self.assertRaises(ValueError) as cm:
            open('non-existent', 'r', opener=badopener)
        self.assertEqual(str(cm.exception), 'opener returned -1')

    eleza test_bad_opener_other_negative(self):
        # Issue #27066.
        eleza badopener(fname, flags):
            rudisha -2
        ukijumuisha self.assertRaises(ValueError) as cm:
            open('non-existent', 'r', opener=badopener)
        self.assertEqual(str(cm.exception), 'opener returned -2')

    eleza test_fileio_closefd(self):
        # Issue #4841
        ukijumuisha self.open(__file__, 'rb') as f1, \
             self.open(__file__, 'rb') as f2:
            fileio = self.FileIO(f1.fileno(), closefd=Uongo)
            # .__init__() must sio close f1
            fileio.__init__(f2.fileno(), closefd=Uongo)
            f1.readline()
            # .close() must sio close f2
            fileio.close()
            f2.readline()

    eleza test_nonbuffered_textio(self):
        ukijumuisha support.check_no_resource_warning(self):
            ukijumuisha self.assertRaises(ValueError):
                self.open(support.TESTFN, 'w', buffering=0)

    eleza test_invalid_newline(self):
        ukijumuisha support.check_no_resource_warning(self):
            ukijumuisha self.assertRaises(ValueError):
                self.open(support.TESTFN, 'w', newline='invalid')

    eleza test_buffered_readinto_mixin(self):
        # Test the implementation provided by BufferedIOBase
        kundi Stream(self.BufferedIOBase):
            eleza read(self, size):
                rudisha b"12345"
            read1 = read
        stream = Stream()
        kila method kwenye ("readinto", "readinto1"):
            ukijumuisha self.subTest(method):
                buffer = byteslike(5)
                self.assertEqual(getattr(stream, method)(buffer), 5)
                self.assertEqual(bytes(buffer), b"12345")

    eleza test_fspath_support(self):
        eleza check_path_succeeds(path):
            ukijumuisha self.open(path, "w") as f:
                f.write("egg\n")

            ukijumuisha self.open(path, "r") as f:
                self.assertEqual(f.read(), "egg\n")

        check_path_succeeds(FakePath(support.TESTFN))
        check_path_succeeds(FakePath(support.TESTFN.encode('utf-8')))

        ukijumuisha self.open(support.TESTFN, "w") as f:
            bad_path = FakePath(f.fileno())
            ukijumuisha self.assertRaises(TypeError):
                self.open(bad_path, 'w')

        bad_path = FakePath(Tupu)
        ukijumuisha self.assertRaises(TypeError):
            self.open(bad_path, 'w')

        bad_path = FakePath(FloatingPointError)
        ukijumuisha self.assertRaises(FloatingPointError):
            self.open(bad_path, 'w')

        # ensure that refcounting ni correct ukijumuisha some error conditions
        ukijumuisha self.assertRaisesRegex(ValueError, 'read/write/append mode'):
            self.open(FakePath(support.TESTFN), 'rwxa')

    eleza test_RawIOBase_readall(self):
        # Exercise the default unlimited RawIOBase.read() na readall()
        # implementations.
        rawio = self.MockRawIOWithoutRead((b"abc", b"d", b"efg"))
        self.assertEqual(rawio.read(), b"abcdefg")
        rawio = self.MockRawIOWithoutRead((b"abc", b"d", b"efg"))
        self.assertEqual(rawio.readall(), b"abcdefg")

    eleza test_BufferedIOBase_readinto(self):
        # Exercise the default BufferedIOBase.readinto() na readinto1()
        # implementations (which call read() ama read1() internally).
        kundi Reader(self.BufferedIOBase):
            eleza __init__(self, avail):
                self.avail = avail
            eleza read(self, size):
                result = self.avail[:size]
                self.avail = self.avail[size:]
                rudisha result
            eleza read1(self, size):
                """Returns no more than 5 bytes at once"""
                rudisha self.read(min(size, 5))
        tests = (
            # (test method, total data available, read buffer size, expected
            #     read size)
            ("readinto", 10, 5, 5),
            ("readinto", 10, 6, 6),  # More than read1() can return
            ("readinto", 5, 6, 5),  # Buffer larger than total available
            ("readinto", 6, 7, 6),
            ("readinto", 10, 0, 0),  # Empty buffer
            ("readinto1", 10, 5, 5),  # Result limited to single read1() call
            ("readinto1", 10, 6, 5),  # Buffer larger than read1() can return
            ("readinto1", 5, 6, 5),  # Buffer larger than total available
            ("readinto1", 6, 7, 5),
            ("readinto1", 10, 0, 0),  # Empty buffer
        )
        UNUSED_BYTE = 0x81
        kila test kwenye tests:
            ukijumuisha self.subTest(test):
                method, avail, request, result = test
                reader = Reader(bytes(range(avail)))
                buffer = bytearray((UNUSED_BYTE,) * request)
                method = getattr(reader, method)
                self.assertEqual(method(buffer), result)
                self.assertEqual(len(buffer), request)
                self.assertSequenceEqual(buffer[:result], range(result))
                unused = (UNUSED_BYTE,) * (request - result)
                self.assertSequenceEqual(buffer[result:], unused)
                self.assertEqual(len(reader.avail), avail - result)

    eleza test_close_assert(self):
        kundi R(self.IOBase):
            eleza __setattr__(self, name, value):
                pass
            eleza flush(self):
                 ashiria OSError()
        f = R()
        # This would cause an assertion failure.
        self.assertRaises(OSError, f.close)

        # Silence destructor error
        R.flush = lambda self: Tupu


kundi CIOTest(IOTest):

    eleza test_IOBase_finalize(self):
        # Issue #12149: segmentation fault on _PyIOBase_finalize when both a
        # kundi which inherits IOBase na an object of this kundi are caught
        # kwenye a reference cycle na close() ni already kwenye the method cache.
        kundi MyIO(self.IOBase):
            eleza close(self):
                pass

        # create an instance to populate the method cache
        MyIO()
        obj = MyIO()
        obj.obj = obj
        wr = weakref.ref(obj)
        toa MyIO
        toa obj
        support.gc_collect()
        self.assertIsTupu(wr(), wr)

kundi PyIOTest(IOTest):
    pass


@support.cpython_only
kundi APIMismatchTest(unittest.TestCase):

    eleza test_RawIOBase_io_in_pyio_match(self):
        """Test that pyio RawIOBase kundi has all c RawIOBase methods"""
        mismatch = support.detect_api_mismatch(pyio.RawIOBase, io.RawIOBase,
                                               ignore=('__weakref__',))
        self.assertEqual(mismatch, set(), msg='Python RawIOBase does sio have all C RawIOBase methods')

    eleza test_RawIOBase_pyio_in_io_match(self):
        """Test that c RawIOBase kundi has all pyio RawIOBase methods"""
        mismatch = support.detect_api_mismatch(io.RawIOBase, pyio.RawIOBase)
        self.assertEqual(mismatch, set(), msg='C RawIOBase does sio have all Python RawIOBase methods')


kundi CommonBufferedTests:
    # Tests common to BufferedReader, BufferedWriter na BufferedRandom

    eleza test_detach(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        self.assertIs(buf.detach(), raw)
        self.assertRaises(ValueError, buf.detach)

        repr(buf)  # Should still work

    eleza test_fileno(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)

        self.assertEqual(42, bufio.fileno())

    eleza test_invalid_args(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        # Invalid whence
        self.assertRaises(ValueError, bufio.seek, 0, -1)
        self.assertRaises(ValueError, bufio.seek, 0, 9)

    eleza test_override_destructor(self):
        tp = self.tp
        record = []
        kundi MyBufferedIO(tp):
            eleza __del__(self):
                record.append(1)
                jaribu:
                    f = super().__del__
                except AttributeError:
                    pass
                isipokua:
                    f()
            eleza close(self):
                record.append(2)
                super().close()
            eleza flush(self):
                record.append(3)
                super().flush()
        rawio = self.MockRawIO()
        bufio = MyBufferedIO(rawio)
        toa bufio
        support.gc_collect()
        self.assertEqual(record, [1, 2, 3])

    eleza test_context_manager(self):
        # Test usability as a context manager
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        eleza _with():
            ukijumuisha bufio:
                pass
        _with()
        # bufio should now be closed, na using it a second time should raise
        # a ValueError.
        self.assertRaises(ValueError, _with)

    eleza test_error_through_destructor(self):
        # Test that the exception state ni sio modified by a destructor,
        # even ikiwa close() fails.
        rawio = self.CloseFailureIO()
        ukijumuisha support.catch_unraisable_exception() as cm:
            ukijumuisha self.assertRaises(AttributeError):
                self.tp(rawio).xyzzy

            ikiwa sio IOBASE_EMITS_UNRAISABLE:
                self.assertIsTupu(cm.unraisable)
            elikiwa cm.unraisable ni sio Tupu:
                self.assertEqual(cm.unraisable.exc_type, OSError)

    eleza test_repr(self):
        raw = self.MockRawIO()
        b = self.tp(raw)
        clsname = r"(%s\.)?%s" % (self.tp.__module__, self.tp.__qualname__)
        self.assertRegex(repr(b), "<%s>" % clsname)
        raw.name = "dummy"
        self.assertRegex(repr(b), "<%s name='dummy'>" % clsname)
        raw.name = b"dummy"
        self.assertRegex(repr(b), "<%s name=b'dummy'>" % clsname)

    eleza test_recursive_repr(self):
        # Issue #25455
        raw = self.MockRawIO()
        b = self.tp(raw)
        ukijumuisha support.swap_attr(raw, 'name', b):
            jaribu:
                repr(b)  # Should sio crash
            except RuntimeError:
                pass

    eleza test_flush_error_on_close(self):
        # Test that buffered file ni closed despite failed flush
        # na that flush() ni called before file closed.
        raw = self.MockRawIO()
        closed = []
        eleza bad_flush():
            closed[:] = [b.closed, raw.closed]
             ashiria OSError()
        raw.flush = bad_flush
        b = self.tp(raw)
        self.assertRaises(OSError, b.close) # exception sio swallowed
        self.assertKweli(b.closed)
        self.assertKweli(raw.closed)
        self.assertKweli(closed)      # flush() called
        self.assertUongo(closed[0])  # flush() called before file closed
        self.assertUongo(closed[1])
        raw.flush = lambda: Tupu  # koma reference loop

    eleza test_close_error_on_close(self):
        raw = self.MockRawIO()
        eleza bad_flush():
             ashiria OSError('flush')
        eleza bad_close():
             ashiria OSError('close')
        raw.close = bad_close
        b = self.tp(raw)
        b.flush = bad_flush
        ukijumuisha self.assertRaises(OSError) as err: # exception sio swallowed
            b.close()
        self.assertEqual(err.exception.args, ('close',))
        self.assertIsInstance(err.exception.__context__, OSError)
        self.assertEqual(err.exception.__context__.args, ('flush',))
        self.assertUongo(b.closed)

        # Silence destructor error
        raw.close = lambda: Tupu
        b.flush = lambda: Tupu

    eleza test_nonnormalized_close_error_on_close(self):
        # Issue #21677
        raw = self.MockRawIO()
        eleza bad_flush():
             ashiria non_existing_flush
        eleza bad_close():
             ashiria non_existing_close
        raw.close = bad_close
        b = self.tp(raw)
        b.flush = bad_flush
        ukijumuisha self.assertRaises(NameError) as err: # exception sio swallowed
            b.close()
        self.assertIn('non_existing_close', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('non_existing_flush', str(err.exception.__context__))
        self.assertUongo(b.closed)

        # Silence destructor error
        b.flush = lambda: Tupu
        raw.close = lambda: Tupu

    eleza test_multi_close(self):
        raw = self.MockRawIO()
        b = self.tp(raw)
        b.close()
        b.close()
        b.close()
        self.assertRaises(ValueError, b.flush)

    eleza test_unseekable(self):
        bufio = self.tp(self.MockUnseekableIO(b"A" * 10))
        self.assertRaises(self.UnsupportedOperation, bufio.tell)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)

    eleza test_readonly_attributes(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        x = self.MockRawIO()
        ukijumuisha self.assertRaises(AttributeError):
            buf.raw = x


kundi SizeofTest:

    @support.cpython_only
    eleza test_sizeof(self):
        bufsize1 = 4096
        bufsize2 = 8192
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize1)
        size = sys.getsizeof(bufio) - bufsize1
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize2)
        self.assertEqual(sys.getsizeof(bufio), size + bufsize2)

    @support.cpython_only
    eleza test_buffer_freeing(self) :
        bufsize = 4096
        rawio = self.MockRawIO()
        bufio = self.tp(rawio, buffer_size=bufsize)
        size = sys.getsizeof(bufio) - bufsize
        bufio.close()
        self.assertEqual(sys.getsizeof(bufio), size)

kundi BufferedReaderTest(unittest.TestCase, CommonBufferedTests):
    read_mode = "rb"

    eleza test_constructor(self):
        rawio = self.MockRawIO([b"abc"])
        bufio = self.tp(rawio)
        bufio.__init__(rawio)
        bufio.__init__(rawio, buffer_size=1024)
        bufio.__init__(rawio, buffer_size=16)
        self.assertEqual(b"abc", bufio.read())
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        rawio = self.MockRawIO([b"abc"])
        bufio.__init__(rawio)
        self.assertEqual(b"abc", bufio.read())

    eleza test_uninitialized(self):
        bufio = self.tp.__new__(self.tp)
        toa bufio
        bufio = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               bufio.read, 0)
        bufio.__init__(self.MockRawIO())
        self.assertEqual(bufio.read(0), b'')

    eleza test_read(self):
        kila arg kwenye (Tupu, 7):
            rawio = self.MockRawIO((b"abc", b"d", b"efg"))
            bufio = self.tp(rawio)
            self.assertEqual(b"abcdefg", bufio.read(arg))
        # Invalid args
        self.assertRaises(ValueError, bufio.read, -2)

    eleza test_read1(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        self.assertEqual(b"a", bufio.read(1))
        self.assertEqual(b"b", bufio.read1(1))
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(b"", bufio.read1(0))
        self.assertEqual(b"c", bufio.read1(100))
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(b"d", bufio.read1(100))
        self.assertEqual(rawio._reads, 2)
        self.assertEqual(b"efg", bufio.read1(100))
        self.assertEqual(rawio._reads, 3)
        self.assertEqual(b"", bufio.read1(100))
        self.assertEqual(rawio._reads, 4)

    eleza test_read1_arbitrary(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        self.assertEqual(b"a", bufio.read(1))
        self.assertEqual(b"bc", bufio.read1())
        self.assertEqual(b"d", bufio.read1())
        self.assertEqual(b"efg", bufio.read1(-1))
        self.assertEqual(rawio._reads, 3)
        self.assertEqual(b"", bufio.read1())
        self.assertEqual(rawio._reads, 4)

    eleza test_readinto(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        b = bytearray(2)
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"cd")
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ef")
        self.assertEqual(bufio.readinto(b), 1)
        self.assertEqual(b, b"gf")
        self.assertEqual(bufio.readinto(b), 0)
        self.assertEqual(b, b"gf")
        rawio = self.MockRawIO((b"abc", Tupu))
        bufio = self.tp(rawio)
        self.assertEqual(bufio.readinto(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(bufio.readinto(b), 1)
        self.assertEqual(b, b"cb")

    eleza test_readinto1(self):
        buffer_size = 10
        rawio = self.MockRawIO((b"abc", b"de", b"fgh", b"jkl"))
        bufio = self.tp(rawio, buffer_size=buffer_size)
        b = bytearray(2)
        self.assertEqual(bufio.peek(3), b'abc')
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 2)
        self.assertEqual(b, b"ab")
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 1)
        self.assertEqual(b[:1], b"c")
        self.assertEqual(rawio._reads, 1)
        self.assertEqual(bufio.readinto1(b), 2)
        self.assertEqual(b, b"de")
        self.assertEqual(rawio._reads, 2)
        b = bytearray(2*buffer_size)
        self.assertEqual(bufio.peek(3), b'fgh')
        self.assertEqual(rawio._reads, 3)
        self.assertEqual(bufio.readinto1(b), 6)
        self.assertEqual(b[:6], b"fghjkl")
        self.assertEqual(rawio._reads, 4)

    eleza test_readinto_array(self):
        buffer_size = 60
        data = b"a" * 26
        rawio = self.MockRawIO((data,))
        bufio = self.tp(rawio, buffer_size=buffer_size)

        # Create an array ukijumuisha element size > 1 byte
        b = array.array('i', b'x' * 32)
        assert len(b) != 16

        # Read into it. We should get as many *bytes* as we can fit into b
        # (which ni more than the number of elements)
        n = bufio.readinto(b)
        self.assertGreater(n, len(b))

        # Check that old contents of b are preserved
        bm = memoryview(b).cast('B')
        self.assertLess(n, len(bm))
        self.assertEqual(bm[:n], data[:n])
        self.assertEqual(bm[n:], b'x' * (len(bm[n:])))

    eleza test_readinto1_array(self):
        buffer_size = 60
        data = b"a" * 26
        rawio = self.MockRawIO((data,))
        bufio = self.tp(rawio, buffer_size=buffer_size)

        # Create an array ukijumuisha element size > 1 byte
        b = array.array('i', b'x' * 32)
        assert len(b) != 16

        # Read into it. We should get as many *bytes* as we can fit into b
        # (which ni more than the number of elements)
        n = bufio.readinto1(b)
        self.assertGreater(n, len(b))

        # Check that old contents of b are preserved
        bm = memoryview(b).cast('B')
        self.assertLess(n, len(bm))
        self.assertEqual(bm[:n], data[:n])
        self.assertEqual(bm[n:], b'x' * (len(bm[n:])))

    eleza test_readlines(self):
        eleza bufio():
            rawio = self.MockRawIO((b"abc\n", b"d\n", b"ef"))
            rudisha self.tp(rawio)
        self.assertEqual(bufio().readlines(), [b"abc\n", b"d\n", b"ef"])
        self.assertEqual(bufio().readlines(5), [b"abc\n", b"d\n"])
        self.assertEqual(bufio().readlines(Tupu), [b"abc\n", b"d\n", b"ef"])

    eleza test_buffering(self):
        data = b"abcdefghi"
        dlen = len(data)

        tests = [
            [ 100, [ 3, 1, 4, 8 ], [ dlen, 0 ] ],
            [ 100, [ 3, 3, 3],     [ dlen ]    ],
            [   4, [ 1, 2, 4, 2 ], [ 4, 4, 1 ] ],
        ]

        kila bufsize, buf_read_sizes, raw_read_sizes kwenye tests:
            rawio = self.MockFileIO(data)
            bufio = self.tp(rawio, buffer_size=bufsize)
            pos = 0
            kila nbytes kwenye buf_read_sizes:
                self.assertEqual(bufio.read(nbytes), data[pos:pos+nbytes])
                pos += nbytes
            # this ni mildly implementation-dependent
            self.assertEqual(rawio.read_history, raw_read_sizes)

    eleza test_read_non_blocking(self):
        # Inject some Tupu's kwenye there to simulate EWOULDBLOCK
        rawio = self.MockRawIO((b"abc", b"d", Tupu, b"efg", Tupu, Tupu, Tupu))
        bufio = self.tp(rawio)
        self.assertEqual(b"abcd", bufio.read(6))
        self.assertEqual(b"e", bufio.read(1))
        self.assertEqual(b"fg", bufio.read())
        self.assertEqual(b"", bufio.peek(1))
        self.assertIsTupu(bufio.read())
        self.assertEqual(b"", bufio.read())

        rawio = self.MockRawIO((b"a", Tupu, Tupu))
        self.assertEqual(b"a", rawio.readall())
        self.assertIsTupu(rawio.readall())

    eleza test_read_past_eof(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)

        self.assertEqual(b"abcdefg", bufio.read(9000))

    eleza test_read_all(self):
        rawio = self.MockRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)

        self.assertEqual(b"abcdefg", bufio.read())

    @support.requires_resource('cpu')
    eleza test_threads(self):
        jaribu:
            # Write out many bytes ukijumuisha exactly the same number of 0's,
            # 1's... 255's. This will help us check that concurrent reading
            # doesn't duplicate ama forget contents.
            N = 1000
            l = list(range(256)) * N
            random.shuffle(l)
            s = bytes(bytearray(l))
            ukijumuisha self.open(support.TESTFN, "wb") as f:
                f.write(s)
            ukijumuisha self.open(support.TESTFN, self.read_mode, buffering=0) as raw:
                bufio = self.tp(raw, 8)
                errors = []
                results = []
                eleza f():
                    jaribu:
                        # Intra-buffer read then buffer-flushing read
                        kila n kwenye cycle([1, 19]):
                            s = bufio.read(n)
                            ikiwa sio s:
                                koma
                            # list.append() ni atomic
                            results.append(s)
                    except Exception as e:
                        errors.append(e)
                        raise
                threads = [threading.Thread(target=f) kila x kwenye range(20)]
                ukijumuisha support.start_threads(threads):
                    time.sleep(0.02) # yield
                self.assertUongo(errors,
                    "the following exceptions were caught: %r" % errors)
                s = b''.join(results)
                kila i kwenye range(256):
                    c = bytes(bytearray([i]))
                    self.assertEqual(s.count(c), N)
        mwishowe:
            support.unlink(support.TESTFN)

    eleza test_unseekable(self):
        bufio = self.tp(self.MockUnseekableIO(b"A" * 10))
        self.assertRaises(self.UnsupportedOperation, bufio.tell)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)
        bufio.read(1)
        self.assertRaises(self.UnsupportedOperation, bufio.seek, 0)
        self.assertRaises(self.UnsupportedOperation, bufio.tell)

    eleza test_misbehaved_io(self):
        rawio = self.MisbehavedRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        self.assertRaises(OSError, bufio.seek, 0)
        self.assertRaises(OSError, bufio.tell)

        # Silence destructor error
        bufio.close = lambda: Tupu

    eleza test_no_extraneous_read(self):
        # Issue #9550; when the raw IO object has satisfied the read request,
        # we should sio issue any additional reads, otherwise it may block
        # (e.g. socket).
        bufsize = 16
        kila n kwenye (2, bufsize - 1, bufsize, bufsize + 1, bufsize * 2):
            rawio = self.MockRawIO([b"x" * n])
            bufio = self.tp(rawio, bufsize)
            self.assertEqual(bufio.read(n), b"x" * n)
            # Simple case: one raw read ni enough to satisfy the request.
            self.assertEqual(rawio._extraneous_reads, 0,
                             "failed kila {}: {} != 0".format(n, rawio._extraneous_reads))
            # A more complex case where two raw reads are needed to satisfy
            # the request.
            rawio = self.MockRawIO([b"x" * (n - 1), b"x"])
            bufio = self.tp(rawio, bufsize)
            self.assertEqual(bufio.read(n), b"x" * n)
            self.assertEqual(rawio._extraneous_reads, 0,
                             "failed kila {}: {} != 0".format(n, rawio._extraneous_reads))

    eleza test_read_on_closed(self):
        # Issue #23796
        b = io.BufferedReader(io.BytesIO(b"12"))
        b.read(1)
        b.close()
        self.assertRaises(ValueError, b.peek)
        self.assertRaises(ValueError, b.read1, 1)


kundi CBufferedReaderTest(BufferedReaderTest, SizeofTest):
    tp = io.BufferedReader

    @unittest.skipIf(MEMORY_SANITIZER, "MSan defaults to crashing "
                     "instead of returning NULL kila malloc failure.")
    eleza test_constructor(self):
        BufferedReaderTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. ukijumuisha more
        # than 2 GiB RAM na a 64-bit kernel.
        ikiwa sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    eleza test_initialization(self):
        rawio = self.MockRawIO([b"abc"])
        bufio = self.tp(rawio)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.read)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.read)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        self.assertRaises(ValueError, bufio.read)

    eleza test_misbehaved_io_read(self):
        rawio = self.MisbehavedRawIO((b"abc", b"d", b"efg"))
        bufio = self.tp(rawio)
        # _pyio.BufferedReader seems to implement reading different, so that
        # checking this ni sio so easy.
        self.assertRaises(OSError, bufio.read, 10)

    eleza test_garbage_collection(self):
        # C BufferedReader objects are collected.
        # The Python version has __del__, so it ends into gc.garbage instead
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            rawio = self.FileIO(support.TESTFN, "w+b")
            f = self.tp(rawio)
            f.f = f
            wr = weakref.ref(f)
            toa f
            support.gc_collect()
        self.assertIsTupu(wr(), wr)

    eleza test_args_error(self):
        # Issue #17275
        ukijumuisha self.assertRaisesRegex(TypeError, "BufferedReader"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


kundi PyBufferedReaderTest(BufferedReaderTest):
    tp = pyio.BufferedReader


kundi BufferedWriterTest(unittest.TestCase, CommonBufferedTests):
    write_mode = "wb"

    eleza test_constructor(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        bufio.__init__(rawio)
        bufio.__init__(rawio, buffer_size=1024)
        bufio.__init__(rawio, buffer_size=16)
        self.assertEqual(3, bufio.write(b"abc"))
        bufio.flush()
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        bufio.__init__(rawio)
        self.assertEqual(3, bufio.write(b"ghi"))
        bufio.flush()
        self.assertEqual(b"".join(rawio._write_stack), b"abcghi")

    eleza test_uninitialized(self):
        bufio = self.tp.__new__(self.tp)
        toa bufio
        bufio = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               bufio.write, b'')
        bufio.__init__(self.MockRawIO())
        self.assertEqual(bufio.write(b''), 0)

    eleza test_detach_flush(self):
        raw = self.MockRawIO()
        buf = self.tp(raw)
        buf.write(b"howdy!")
        self.assertUongo(raw._write_stack)
        buf.detach()
        self.assertEqual(raw._write_stack, [b"howdy!"])

    eleza test_write(self):
        # Write to the buffered IO but don't overflow the buffer.
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        self.assertUongo(writer._write_stack)
        buffer = bytearray(b"def")
        bufio.write(buffer)
        buffer[:] = b"***"  # Overwrite our copy of the data
        bufio.flush()
        self.assertEqual(b"".join(writer._write_stack), b"abcdef")

    eleza test_write_overflow(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        contents = b"abcdefghijklmnop"
        kila n kwenye range(0, len(contents), 3):
            bufio.write(contents[n:n+3])
        flushed = b"".join(writer._write_stack)
        # At least (total - 8) bytes were implicitly flushed, perhaps more
        # depending on the implementation.
        self.assertKweli(flushed.startswith(contents[:-8]), flushed)

    eleza check_writes(self, intermediate_func):
        # Lots of writes, test the flushed output ni as expected.
        contents = bytes(range(256)) * 1000
        n = 0
        writer = self.MockRawIO()
        bufio = self.tp(writer, 13)
        # Generator of write sizes: repeat each N 15 times then proceed to N+1
        eleza gen_sizes():
            kila size kwenye count(1):
                kila i kwenye range(15):
                    tuma size
        sizes = gen_sizes()
        wakati n < len(contents):
            size = min(next(sizes), len(contents) - n)
            self.assertEqual(bufio.write(contents[n:n+size]), size)
            intermediate_func(bufio)
            n += size
        bufio.flush()
        self.assertEqual(contents, b"".join(writer._write_stack))

    eleza test_writes(self):
        self.check_writes(lambda bufio: Tupu)

    eleza test_writes_and_flushes(self):
        self.check_writes(lambda bufio: bufio.flush())

    eleza test_writes_and_seeks(self):
        eleza _seekabs(bufio):
            pos = bufio.tell()
            bufio.seek(pos + 1, 0)
            bufio.seek(pos - 1, 0)
            bufio.seek(pos, 0)
        self.check_writes(_seekabs)
        eleza _seekrel(bufio):
            pos = bufio.seek(0, 1)
            bufio.seek(+1, 1)
            bufio.seek(-1, 1)
            bufio.seek(pos, 0)
        self.check_writes(_seekrel)

    eleza test_writes_and_truncates(self):
        self.check_writes(lambda bufio: bufio.truncate(bufio.tell()))

    eleza test_write_non_blocking(self):
        raw = self.MockNonBlockWriterIO()
        bufio = self.tp(raw, 8)

        self.assertEqual(bufio.write(b"abcd"), 4)
        self.assertEqual(bufio.write(b"efghi"), 5)
        # 1 byte will be written, the rest will be buffered
        raw.block_on(b"k")
        self.assertEqual(bufio.write(b"jklmn"), 5)

        # 8 bytes will be written, 8 will be buffered na the rest will be lost
        raw.block_on(b"0")
        jaribu:
            bufio.write(b"opqrwxyz0123456789")
        except self.BlockingIOError as e:
            written = e.characters_written
        isipokua:
            self.fail("BlockingIOError should have been raised")
        self.assertEqual(written, 16)
        self.assertEqual(raw.pop_written(),
            b"abcdefghijklmnopqrwxyz")

        self.assertEqual(bufio.write(b"ABCDEFGHI"), 9)
        s = raw.pop_written()
        # Previously buffered bytes were flushed
        self.assertKweli(s.startswith(b"01234567A"), s)

    eleza test_write_and_rewind(self):
        raw = io.BytesIO()
        bufio = self.tp(raw, 4)
        self.assertEqual(bufio.write(b"abcdef"), 6)
        self.assertEqual(bufio.tell(), 6)
        bufio.seek(0, 0)
        self.assertEqual(bufio.write(b"XY"), 2)
        bufio.seek(6, 0)
        self.assertEqual(raw.getvalue(), b"XYcdef")
        self.assertEqual(bufio.write(b"123456"), 6)
        bufio.flush()
        self.assertEqual(raw.getvalue(), b"XYcdef123456")

    eleza test_flush(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        bufio.flush()
        self.assertEqual(b"abc", writer._write_stack[0])

    eleza test_writelines(self):
        l = [b'ab', b'cd', b'ef']
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.writelines(l)
        bufio.flush()
        self.assertEqual(b''.join(writer._write_stack), b'abcdef')

    eleza test_writelines_userlist(self):
        l = UserList([b'ab', b'cd', b'ef'])
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.writelines(l)
        bufio.flush()
        self.assertEqual(b''.join(writer._write_stack), b'abcdef')

    eleza test_writelines_error(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        self.assertRaises(TypeError, bufio.writelines, [1, 2, 3])
        self.assertRaises(TypeError, bufio.writelines, Tupu)
        self.assertRaises(TypeError, bufio.writelines, 'abc')

    eleza test_destructor(self):
        writer = self.MockRawIO()
        bufio = self.tp(writer, 8)
        bufio.write(b"abc")
        toa bufio
        support.gc_collect()
        self.assertEqual(b"abc", writer._write_stack[0])

    eleza test_truncate(self):
        # Truncate implicitly flushes the buffer.
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha self.open(support.TESTFN, self.write_mode, buffering=0) as raw:
            bufio = self.tp(raw, 8)
            bufio.write(b"abcdef")
            self.assertEqual(bufio.truncate(3), 3)
            self.assertEqual(bufio.tell(), 6)
        ukijumuisha self.open(support.TESTFN, "rb", buffering=0) as f:
            self.assertEqual(f.read(), b"abc")

    eleza test_truncate_after_write(self):
        # Ensure that truncate preserves the file position after
        # writes longer than the buffer size.
        # Issue: https://bugs.python.org/issue32228
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            # Fill ukijumuisha some buffer
            f.write(b'\x00' * 10000)
        buffer_sizes = [8192, 4096, 200]
        kila buffer_size kwenye buffer_sizes:
            ukijumuisha self.open(support.TESTFN, "r+b", buffering=buffer_size) as f:
                f.write(b'\x00' * (buffer_size + 1))
                # After write write_pos na write_end are set to 0
                f.read(1)
                # read operation makes sure that pos != raw_pos
                f.truncate()
                self.assertEqual(f.tell(), buffer_size + 2)

    @support.requires_resource('cpu')
    eleza test_threads(self):
        jaribu:
            # Write out many bytes kutoka many threads na test they were
            # all flushed.
            N = 1000
            contents = bytes(range(256)) * N
            sizes = cycle([1, 19])
            n = 0
            queue = deque()
            wakati n < len(contents):
                size = next(sizes)
                queue.append(contents[n:n+size])
                n += size
            toa contents
            # We use a real file object because it allows us to
            # exercise situations where the GIL ni released before
            # writing the buffer to the raw streams. This ni kwenye addition
            # to concurrency issues due to switching threads kwenye the middle
            # of Python code.
            ukijumuisha self.open(support.TESTFN, self.write_mode, buffering=0) as raw:
                bufio = self.tp(raw, 8)
                errors = []
                eleza f():
                    jaribu:
                        wakati Kweli:
                            jaribu:
                                s = queue.popleft()
                            except IndexError:
                                return
                            bufio.write(s)
                    except Exception as e:
                        errors.append(e)
                        raise
                threads = [threading.Thread(target=f) kila x kwenye range(20)]
                ukijumuisha support.start_threads(threads):
                    time.sleep(0.02) # yield
                self.assertUongo(errors,
                    "the following exceptions were caught: %r" % errors)
                bufio.close()
            ukijumuisha self.open(support.TESTFN, "rb") as f:
                s = f.read()
            kila i kwenye range(256):
                self.assertEqual(s.count(bytes([i])), N)
        mwishowe:
            support.unlink(support.TESTFN)

    eleza test_misbehaved_io(self):
        rawio = self.MisbehavedRawIO()
        bufio = self.tp(rawio, 5)
        self.assertRaises(OSError, bufio.seek, 0)
        self.assertRaises(OSError, bufio.tell)
        self.assertRaises(OSError, bufio.write, b"abcdef")

        # Silence destructor error
        bufio.close = lambda: Tupu

    eleza test_max_buffer_size_removal(self):
        ukijumuisha self.assertRaises(TypeError):
            self.tp(self.MockRawIO(), 8, 12)

    eleza test_write_error_on_close(self):
        raw = self.MockRawIO()
        eleza bad_write(b):
             ashiria OSError()
        raw.write = bad_write
        b = self.tp(raw)
        b.write(b'spam')
        self.assertRaises(OSError, b.close) # exception sio swallowed
        self.assertKweli(b.closed)

    eleza test_slow_close_from_thread(self):
        # Issue #31976
        rawio = self.SlowFlushRawIO()
        bufio = self.tp(rawio, 8)
        t = threading.Thread(target=bufio.close)
        t.start()
        rawio.in_flush.wait()
        self.assertRaises(ValueError, bufio.write, b'spam')
        self.assertKweli(bufio.closed)
        t.join()



kundi CBufferedWriterTest(BufferedWriterTest, SizeofTest):
    tp = io.BufferedWriter

    @unittest.skipIf(MEMORY_SANITIZER, "MSan defaults to crashing "
                     "instead of returning NULL kila malloc failure.")
    eleza test_constructor(self):
        BufferedWriterTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. ukijumuisha more
        # than 2 GiB RAM na a 64-bit kernel.
        ikiwa sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    eleza test_initialization(self):
        rawio = self.MockRawIO()
        bufio = self.tp(rawio)
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=0)
        self.assertRaises(ValueError, bufio.write, b"def")
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-16)
        self.assertRaises(ValueError, bufio.write, b"def")
        self.assertRaises(ValueError, bufio.__init__, rawio, buffer_size=-1)
        self.assertRaises(ValueError, bufio.write, b"def")

    eleza test_garbage_collection(self):
        # C BufferedWriter objects are collected, na collecting them flushes
        # all data to disk.
        # The Python version has __del__, so it ends into gc.garbage instead
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            rawio = self.FileIO(support.TESTFN, "w+b")
            f = self.tp(rawio)
            f.write(b"123xxx")
            f.x = f
            wr = weakref.ref(f)
            toa f
            support.gc_collect()
        self.assertIsTupu(wr(), wr)
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"123xxx")

    eleza test_args_error(self):
        # Issue #17275
        ukijumuisha self.assertRaisesRegex(TypeError, "BufferedWriter"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


kundi PyBufferedWriterTest(BufferedWriterTest):
    tp = pyio.BufferedWriter

kundi BufferedRWPairTest(unittest.TestCase):

    eleza test_constructor(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertUongo(pair.closed)

    eleza test_uninitialized(self):
        pair = self.tp.__new__(self.tp)
        toa pair
        pair = self.tp.__new__(self.tp)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               pair.read, 0)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               pair.write, b'')
        pair.__init__(self.MockRawIO(), self.MockRawIO())
        self.assertEqual(pair.read(0), b'')
        self.assertEqual(pair.write(b''), 0)

    eleza test_detach(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertRaises(self.UnsupportedOperation, pair.detach)

    eleza test_constructor_max_buffer_size_removal(self):
        ukijumuisha self.assertRaises(TypeError):
            self.tp(self.MockRawIO(), self.MockRawIO(), 8, 12)

    eleza test_constructor_with_not_readable(self):
        kundi NotReadable(MockRawIO):
            eleza readable(self):
                rudisha Uongo

        self.assertRaises(OSError, self.tp, NotReadable(), self.MockRawIO())

    eleza test_constructor_with_not_writeable(self):
        kundi NotWriteable(MockRawIO):
            eleza writable(self):
                rudisha Uongo

        self.assertRaises(OSError, self.tp, self.MockRawIO(), NotWriteable())

    eleza test_read(self):
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertEqual(pair.read(3), b"abc")
        self.assertEqual(pair.read(1), b"d")
        self.assertEqual(pair.read(), b"ef")
        pair = self.tp(self.BytesIO(b"abc"), self.MockRawIO())
        self.assertEqual(pair.read(Tupu), b"abc")

    eleza test_readlines(self):
        pair = lambda: self.tp(self.BytesIO(b"abc\ndef\nh"), self.MockRawIO())
        self.assertEqual(pair().readlines(), [b"abc\n", b"def\n", b"h"])
        self.assertEqual(pair().readlines(), [b"abc\n", b"def\n", b"h"])
        self.assertEqual(pair().readlines(5), [b"abc\n", b"def\n"])

    eleza test_read1(self):
        # .read1() ni delegated to the underlying reader object, so this test
        # can be shallow.
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertEqual(pair.read1(3), b"abc")
        self.assertEqual(pair.read1(), b"def")

    eleza test_readinto(self):
        kila method kwenye ("readinto", "readinto1"):
            ukijumuisha self.subTest(method):
                pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

                data = byteslike(b'\0' * 5)
                self.assertEqual(getattr(pair, method)(data), 5)
                self.assertEqual(bytes(data), b"abcde")

    eleza test_write(self):
        w = self.MockRawIO()
        pair = self.tp(self.MockRawIO(), w)

        pair.write(b"abc")
        pair.flush()
        buffer = bytearray(b"def")
        pair.write(buffer)
        buffer[:] = b"***"  # Overwrite our copy of the data
        pair.flush()
        self.assertEqual(w._write_stack, [b"abc", b"def"])

    eleza test_peek(self):
        pair = self.tp(self.BytesIO(b"abcdef"), self.MockRawIO())

        self.assertKweli(pair.peek(3).startswith(b"abc"))
        self.assertEqual(pair.read(3), b"abc")

    eleza test_readable(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertKweli(pair.readable())

    eleza test_writeable(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertKweli(pair.writable())

    eleza test_seekable(self):
        # BufferedRWPairs are never seekable, even ikiwa their readers na writers
        # are.
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertUongo(pair.seekable())

    # .flush() ni delegated to the underlying writer object na has been
    # tested kwenye the test_write method.

    eleza test_close_and_closed(self):
        pair = self.tp(self.MockRawIO(), self.MockRawIO())
        self.assertUongo(pair.closed)
        pair.close()
        self.assertKweli(pair.closed)

    eleza test_reader_close_error_on_close(self):
        eleza reader_close():
            reader_non_existing
        reader = self.MockRawIO()
        reader.close = reader_close
        writer = self.MockRawIO()
        pair = self.tp(reader, writer)
        ukijumuisha self.assertRaises(NameError) as err:
            pair.close()
        self.assertIn('reader_non_existing', str(err.exception))
        self.assertKweli(pair.closed)
        self.assertUongo(reader.closed)
        self.assertKweli(writer.closed)

        # Silence destructor error
        reader.close = lambda: Tupu

    eleza test_writer_close_error_on_close(self):
        eleza writer_close():
            writer_non_existing
        reader = self.MockRawIO()
        writer = self.MockRawIO()
        writer.close = writer_close
        pair = self.tp(reader, writer)
        ukijumuisha self.assertRaises(NameError) as err:
            pair.close()
        self.assertIn('writer_non_existing', str(err.exception))
        self.assertUongo(pair.closed)
        self.assertKweli(reader.closed)
        self.assertUongo(writer.closed)

        # Silence destructor error
        writer.close = lambda: Tupu
        writer = Tupu

        # Ignore BufferedWriter (of the BufferedRWPair) unraisable exception
        ukijumuisha support.catch_unraisable_exception():
            # Ignore BufferedRWPair unraisable exception
            ukijumuisha support.catch_unraisable_exception():
                pair = Tupu
                support.gc_collect()
            support.gc_collect()

    eleza test_reader_writer_close_error_on_close(self):
        eleza reader_close():
            reader_non_existing
        eleza writer_close():
            writer_non_existing
        reader = self.MockRawIO()
        reader.close = reader_close
        writer = self.MockRawIO()
        writer.close = writer_close
        pair = self.tp(reader, writer)
        ukijumuisha self.assertRaises(NameError) as err:
            pair.close()
        self.assertIn('reader_non_existing', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('writer_non_existing', str(err.exception.__context__))
        self.assertUongo(pair.closed)
        self.assertUongo(reader.closed)
        self.assertUongo(writer.closed)

        # Silence destructor error
        reader.close = lambda: Tupu
        writer.close = lambda: Tupu

    eleza test_isatty(self):
        kundi SelectableIsAtty(MockRawIO):
            eleza __init__(self, isatty):
                MockRawIO.__init__(self)
                self._isatty = isatty

            eleza isatty(self):
                rudisha self._isatty

        pair = self.tp(SelectableIsAtty(Uongo), SelectableIsAtty(Uongo))
        self.assertUongo(pair.isatty())

        pair = self.tp(SelectableIsAtty(Kweli), SelectableIsAtty(Uongo))
        self.assertKweli(pair.isatty())

        pair = self.tp(SelectableIsAtty(Uongo), SelectableIsAtty(Kweli))
        self.assertKweli(pair.isatty())

        pair = self.tp(SelectableIsAtty(Kweli), SelectableIsAtty(Kweli))
        self.assertKweli(pair.isatty())

    eleza test_weakref_clearing(self):
        brw = self.tp(self.MockRawIO(), self.MockRawIO())
        ref = weakref.ref(brw)
        brw = Tupu
        ref = Tupu # Shouldn't segfault.

kundi CBufferedRWPairTest(BufferedRWPairTest):
    tp = io.BufferedRWPair

kundi PyBufferedRWPairTest(BufferedRWPairTest):
    tp = pyio.BufferedRWPair


kundi BufferedRandomTest(BufferedReaderTest, BufferedWriterTest):
    read_mode = "rb+"
    write_mode = "wb+"

    eleza test_constructor(self):
        BufferedReaderTest.test_constructor(self)
        BufferedWriterTest.test_constructor(self)

    eleza test_uninitialized(self):
        BufferedReaderTest.test_uninitialized(self)
        BufferedWriterTest.test_uninitialized(self)

    eleza test_read_and_write(self):
        raw = self.MockRawIO((b"asdf", b"ghjk"))
        rw = self.tp(raw, 8)

        self.assertEqual(b"as", rw.read(2))
        rw.write(b"ddd")
        rw.write(b"eee")
        self.assertUongo(raw._write_stack) # Buffer writes
        self.assertEqual(b"ghjk", rw.read())
        self.assertEqual(b"dddeee", raw._write_stack[0])

    eleza test_seek_and_tell(self):
        raw = self.BytesIO(b"asdfghjkl")
        rw = self.tp(raw)

        self.assertEqual(b"as", rw.read(2))
        self.assertEqual(2, rw.tell())
        rw.seek(0, 0)
        self.assertEqual(b"asdf", rw.read(4))

        rw.write(b"123f")
        rw.seek(0, 0)
        self.assertEqual(b"asdf123fl", rw.read())
        self.assertEqual(9, rw.tell())
        rw.seek(-4, 2)
        self.assertEqual(5, rw.tell())
        rw.seek(2, 1)
        self.assertEqual(7, rw.tell())
        self.assertEqual(b"fl", rw.read(11))
        rw.flush()
        self.assertEqual(b"asdf123fl", raw.getvalue())

        self.assertRaises(TypeError, rw.seek, 0.0)

    eleza check_flush_and_read(self, read_func):
        raw = self.BytesIO(b"abcdefghi")
        bufio = self.tp(raw)

        self.assertEqual(b"ab", read_func(bufio, 2))
        bufio.write(b"12")
        self.assertEqual(b"ef", read_func(bufio, 2))
        self.assertEqual(6, bufio.tell())
        bufio.flush()
        self.assertEqual(6, bufio.tell())
        self.assertEqual(b"ghi", read_func(bufio))
        raw.seek(0, 0)
        raw.write(b"XYZ")
        # flush() resets the read buffer
        bufio.flush()
        bufio.seek(0, 0)
        self.assertEqual(b"XYZ", read_func(bufio, 3))

    eleza test_flush_and_read(self):
        self.check_flush_and_read(lambda bufio, *args: bufio.read(*args))

    eleza test_flush_and_readinto(self):
        eleza _readinto(bufio, n=-1):
            b = bytearray(n ikiwa n >= 0 isipokua 9999)
            n = bufio.readinto(b)
            rudisha bytes(b[:n])
        self.check_flush_and_read(_readinto)

    eleza test_flush_and_peek(self):
        eleza _peek(bufio, n=-1):
            # This relies on the fact that the buffer can contain the whole
            # raw stream, otherwise peek() can rudisha less.
            b = bufio.peek(n)
            ikiwa n != -1:
                b = b[:n]
            bufio.seek(len(b), 1)
            rudisha b
        self.check_flush_and_read(_peek)

    eleza test_flush_and_write(self):
        raw = self.BytesIO(b"abcdefghi")
        bufio = self.tp(raw)

        bufio.write(b"123")
        bufio.flush()
        bufio.write(b"45")
        bufio.flush()
        bufio.seek(0, 0)
        self.assertEqual(b"12345fghi", raw.getvalue())
        self.assertEqual(b"12345fghi", bufio.read())

    eleza test_threads(self):
        BufferedReaderTest.test_threads(self)
        BufferedWriterTest.test_threads(self)

    eleza test_writes_and_peek(self):
        eleza _peek(bufio):
            bufio.peek(1)
        self.check_writes(_peek)
        eleza _peek(bufio):
            pos = bufio.tell()
            bufio.seek(-1, 1)
            bufio.peek(1)
            bufio.seek(pos, 0)
        self.check_writes(_peek)

    eleza test_writes_and_reads(self):
        eleza _read(bufio):
            bufio.seek(-1, 1)
            bufio.read(1)
        self.check_writes(_read)

    eleza test_writes_and_read1s(self):
        eleza _read1(bufio):
            bufio.seek(-1, 1)
            bufio.read1(1)
        self.check_writes(_read1)

    eleza test_writes_and_readintos(self):
        eleza _read(bufio):
            bufio.seek(-1, 1)
            bufio.readinto(bytearray(1))
        self.check_writes(_read)

    eleza test_write_after_readahead(self):
        # Issue #6629: writing after the buffer was filled by readahead should
        # first rewind the raw stream.
        kila overwrite_size kwenye [1, 5]:
            raw = self.BytesIO(b"A" * 10)
            bufio = self.tp(raw, 4)
            # Trigger readahead
            self.assertEqual(bufio.read(1), b"A")
            self.assertEqual(bufio.tell(), 1)
            # Overwriting should rewind the raw stream ikiwa it needs so
            bufio.write(b"B" * overwrite_size)
            self.assertEqual(bufio.tell(), overwrite_size + 1)
            # If the write size was smaller than the buffer size, flush() and
            # check that rewind happens.
            bufio.flush()
            self.assertEqual(bufio.tell(), overwrite_size + 1)
            s = raw.getvalue()
            self.assertEqual(s,
                b"A" + b"B" * overwrite_size + b"A" * (9 - overwrite_size))

    eleza test_write_rewind_write(self):
        # Various combinations of reading / writing / seeking backwards / writing again
        eleza mutate(bufio, pos1, pos2):
            assert pos2 >= pos1
            # Fill the buffer
            bufio.seek(pos1)
            bufio.read(pos2 - pos1)
            bufio.write(b'\x02')
            # This writes earlier than the previous write, but still inside
            # the buffer.
            bufio.seek(pos1)
            bufio.write(b'\x01')

        b = b"\x80\x81\x82\x83\x84"
        kila i kwenye range(0, len(b)):
            kila j kwenye range(i, len(b)):
                raw = self.BytesIO(b)
                bufio = self.tp(raw, 100)
                mutate(bufio, i, j)
                bufio.flush()
                expected = bytearray(b)
                expected[j] = 2
                expected[i] = 1
                self.assertEqual(raw.getvalue(), expected,
                                 "failed result kila i=%d, j=%d" % (i, j))

    eleza test_truncate_after_read_or_write(self):
        raw = self.BytesIO(b"A" * 10)
        bufio = self.tp(raw, 100)
        self.assertEqual(bufio.read(2), b"AA") # the read buffer gets filled
        self.assertEqual(bufio.truncate(), 2)
        self.assertEqual(bufio.write(b"BB"), 2) # the write buffer increases
        self.assertEqual(bufio.truncate(), 4)

    eleza test_misbehaved_io(self):
        BufferedReaderTest.test_misbehaved_io(self)
        BufferedWriterTest.test_misbehaved_io(self)

    eleza test_interleaved_read_write(self):
        # Test kila issue #12213
        ukijumuisha self.BytesIO(b'abcdefgh') as raw:
            ukijumuisha self.tp(raw, 100) as f:
                f.write(b"1")
                self.assertEqual(f.read(1), b'b')
                f.write(b'2')
                self.assertEqual(f.read1(1), b'd')
                f.write(b'3')
                buf = bytearray(1)
                f.readinto(buf)
                self.assertEqual(buf, b'f')
                f.write(b'4')
                self.assertEqual(f.peek(1), b'h')
                f.flush()
                self.assertEqual(raw.getvalue(), b'1b2d3f4h')

        ukijumuisha self.BytesIO(b'abc') as raw:
            ukijumuisha self.tp(raw, 100) as f:
                self.assertEqual(f.read(1), b'a')
                f.write(b"2")
                self.assertEqual(f.read(1), b'c')
                f.flush()
                self.assertEqual(raw.getvalue(), b'a2c')

    eleza test_interleaved_readline_write(self):
        ukijumuisha self.BytesIO(b'ab\ncdef\ng\n') as raw:
            ukijumuisha self.tp(raw) as f:
                f.write(b'1')
                self.assertEqual(f.readline(), b'b\n')
                f.write(b'2')
                self.assertEqual(f.readline(), b'def\n')
                f.write(b'3')
                self.assertEqual(f.readline(), b'\n')
                f.flush()
                self.assertEqual(raw.getvalue(), b'1b\n2def\n3\n')

    # You can't construct a BufferedRandom over a non-seekable stream.
    test_unseekable = Tupu


kundi CBufferedRandomTest(BufferedRandomTest, SizeofTest):
    tp = io.BufferedRandom

    @unittest.skipIf(MEMORY_SANITIZER, "MSan defaults to crashing "
                     "instead of returning NULL kila malloc failure.")
    eleza test_constructor(self):
        BufferedRandomTest.test_constructor(self)
        # The allocation can succeed on 32-bit builds, e.g. ukijumuisha more
        # than 2 GiB RAM na a 64-bit kernel.
        ikiwa sys.maxsize > 0x7FFFFFFF:
            rawio = self.MockRawIO()
            bufio = self.tp(rawio)
            self.assertRaises((OverflowError, MemoryError, ValueError),
                bufio.__init__, rawio, sys.maxsize)

    eleza test_garbage_collection(self):
        CBufferedReaderTest.test_garbage_collection(self)
        CBufferedWriterTest.test_garbage_collection(self)

    eleza test_args_error(self):
        # Issue #17275
        ukijumuisha self.assertRaisesRegex(TypeError, "BufferedRandom"):
            self.tp(io.BytesIO(), 1024, 1024, 1024)


kundi PyBufferedRandomTest(BufferedRandomTest):
    tp = pyio.BufferedRandom


# To fully exercise seek/tell, the StatefulIncrementalDecoder has these
# properties:
#   - A single output character can correspond to many bytes of input.
#   - The number of input bytes to complete the character can be
#     undetermined until the last input byte ni received.
#   - The number of input bytes can vary depending on previous input.
#   - A single input byte can correspond to many characters of output.
#   - The number of output characters can be undetermined until the
#     last input byte ni received.
#   - The number of output characters can vary depending on previous input.

kundi StatefulIncrementalDecoder(codecs.IncrementalDecoder):
    """
    For testing seek/tell behavior ukijumuisha a stateful, buffering decoder.

    Input ni a sequence of words.  Words may be fixed-length (length set
    by input) ama variable-length (period-terminated).  In variable-length
    mode, extra periods are ignored.  Possible words are:
      - 'i' followed by a number sets the input length, I (maximum 99).
        When I ni set to 0, words are space-terminated.
      - 'o' followed by a number sets the output length, O (maximum 99).
      - Any other word ni converted into a word followed by a period on
        the output.  The output word consists of the input word truncated
        ama padded out ukijumuisha hyphens to make its length equal to O.  If O
        ni 0, the word ni output verbatim without truncating ama padding.
    I na O are initially set to 1.  When I changes, any buffered input is
    re-scanned according to the new I.  EOF also terminates the last word.
    """

    eleza __init__(self, errors='strict'):
        codecs.IncrementalDecoder.__init__(self, errors)
        self.reset()

    eleza __repr__(self):
        rudisha '<SID %x>' % id(self)

    eleza reset(self):
        self.i = 1
        self.o = 1
        self.buffer = bytearray()

    eleza getstate(self):
        i, o = self.i ^ 1, self.o ^ 1 # so that flags = 0 after reset()
        rudisha bytes(self.buffer), i*100 + o

    eleza setstate(self, state):
        buffer, io = state
        self.buffer = bytearray(buffer)
        i, o = divmod(io, 100)
        self.i, self.o = i ^ 1, o ^ 1

    eleza decode(self, input, final=Uongo):
        output = ''
        kila b kwenye input:
            ikiwa self.i == 0: # variable-length, terminated ukijumuisha period
                ikiwa b == ord('.'):
                    ikiwa self.buffer:
                        output += self.process_word()
                isipokua:
                    self.buffer.append(b)
            isipokua: # fixed-length, terminate after self.i bytes
                self.buffer.append(b)
                ikiwa len(self.buffer) == self.i:
                    output += self.process_word()
        ikiwa final na self.buffer: # EOF terminates the last word
            output += self.process_word()
        rudisha output

    eleza process_word(self):
        output = ''
        ikiwa self.buffer[0] == ord('i'):
            self.i = min(99, int(self.buffer[1:] ama 0)) # set input length
        elikiwa self.buffer[0] == ord('o'):
            self.o = min(99, int(self.buffer[1:] ama 0)) # set output length
        isipokua:
            output = self.buffer.decode('ascii')
            ikiwa len(output) < self.o:
                output += '-'*self.o # pad out ukijumuisha hyphens
            ikiwa self.o:
                output = output[:self.o] # truncate to output length
            output += '.'
        self.buffer = bytearray()
        rudisha output

    codecEnabled = Uongo

    @classmethod
    eleza lookupTestDecoder(cls, name):
        ikiwa cls.codecEnabled na name == 'test_decoder':
            latin1 = codecs.lookup('latin-1')
            rudisha codecs.CodecInfo(
                name='test_decoder', encode=latin1.encode, decode=Tupu,
                incrementalencoder=Tupu,
                streamreader=Tupu, streamwriter=Tupu,
                incrementaldecoder=cls)

# Register the previous decoder kila testing.
# Disabled by default, tests will enable it.
codecs.register(StatefulIncrementalDecoder.lookupTestDecoder)


kundi StatefulIncrementalDecoderTest(unittest.TestCase):
    """
    Make sure the StatefulIncrementalDecoder actually works.
    """

    test_cases = [
        # I=1, O=1 (fixed-length input == fixed-length output)
        (b'abcd', Uongo, 'a.b.c.d.'),
        # I=0, O=0 (variable-length input, variable-length output)
        (b'oiabcd', Kweli, 'abcd.'),
        # I=0, O=0 (should ignore extra periods)
        (b'oi...abcd...', Kweli, 'abcd.'),
        # I=0, O=6 (variable-length input, fixed-length output)
        (b'i.o6.x.xyz.toolongtofit.', Uongo, 'x-----.xyz---.toolon.'),
        # I=2, O=6 (fixed-length input < fixed-length output)
        (b'i.i2.o6xyz', Kweli, 'xy----.z-----.'),
        # I=6, O=3 (fixed-length input > fixed-length output)
        (b'i.o3.i6.abcdefghijklmnop', Kweli, 'abc.ghi.mno.'),
        # I=0, then 3; O=29, then 15 (ukijumuisha longer output)
        (b'i.o29.a.b.cde.o15.abcdefghijabcdefghij.i3.a.b.c.d.ei00k.l.m', Kweli,
         'a----------------------------.' +
         'b----------------------------.' +
         'cde--------------------------.' +
         'abcdefghijabcde.' +
         'a.b------------.' +
         '.c.------------.' +
         'd.e------------.' +
         'k--------------.' +
         'l--------------.' +
         'm--------------.')
    ]

    eleza test_decoder(self):
        # Try a few one-shot test cases.
        kila input, eof, output kwenye self.test_cases:
            d = StatefulIncrementalDecoder()
            self.assertEqual(d.decode(input, eof), output)

        # Also test an unfinished decode, followed by forcing EOF.
        d = StatefulIncrementalDecoder()
        self.assertEqual(d.decode(b'oiabcd'), '')
        self.assertEqual(d.decode(b'', 1), 'abcd.')

kundi TextIOWrapperTest(unittest.TestCase):

    eleza setUp(self):
        self.testdata = b"AAA\r\nBBB\rCCC\r\nDDD\nEEE\r\n"
        self.normalized = b"AAA\nBBB\nCCC\nDDD\nEEE\n".decode("ascii")
        support.unlink(support.TESTFN)

    eleza tearDown(self):
        support.unlink(support.TESTFN)

    eleza test_constructor(self):
        r = self.BytesIO(b"\xc3\xa9\n\n")
        b = self.BufferedReader(r, 1000)
        t = self.TextIOWrapper(b)
        t.__init__(b, encoding="latin-1", newline="\r\n")
        self.assertEqual(t.encoding, "latin-1")
        self.assertEqual(t.line_buffering, Uongo)
        t.__init__(b, encoding="utf-8", line_buffering=Kweli)
        self.assertEqual(t.encoding, "utf-8")
        self.assertEqual(t.line_buffering, Kweli)
        self.assertEqual("\xe9\n", t.readline())
        self.assertRaises(TypeError, t.__init__, b, newline=42)
        self.assertRaises(ValueError, t.__init__, b, newline='xyzzy')

    eleza test_uninitialized(self):
        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        toa t
        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        self.assertRaises(Exception, repr, t)
        self.assertRaisesRegex((ValueError, AttributeError),
                               'uninitialized|has no attribute',
                               t.read, 0)
        t.__init__(self.MockRawIO())
        self.assertEqual(t.read(0), '')

    eleza test_non_text_encoding_codecs_are_rejected(self):
        # Ensure the constructor complains ikiwa passed a codec that isn't
        # marked as a text encoding
        # http://bugs.python.org/issue20404
        r = self.BytesIO()
        b = self.BufferedWriter(r)
        ukijumuisha self.assertRaisesRegex(LookupError, "is sio a text encoding"):
            self.TextIOWrapper(b, encoding="hex")

    eleza test_detach(self):
        r = self.BytesIO()
        b = self.BufferedWriter(r)
        t = self.TextIOWrapper(b)
        self.assertIs(t.detach(), b)

        t = self.TextIOWrapper(b, encoding="ascii")
        t.write("howdy")
        self.assertUongo(r.getvalue())
        t.detach()
        self.assertEqual(r.getvalue(), b"howdy")
        self.assertRaises(ValueError, t.detach)

        # Operations independent of the detached stream should still work
        repr(t)
        self.assertEqual(t.encoding, "ascii")
        self.assertEqual(t.errors, "strict")
        self.assertUongo(t.line_buffering)
        self.assertUongo(t.write_through)

    eleza test_repr(self):
        raw = self.BytesIO("hello".encode("utf-8"))
        b = self.BufferedReader(raw)
        t = self.TextIOWrapper(b, encoding="utf-8")
        modname = self.TextIOWrapper.__module__
        self.assertRegex(repr(t),
                         r"<(%s\.)?TextIOWrapper encoding='utf-8'>" % modname)
        raw.name = "dummy"
        self.assertRegex(repr(t),
                         r"<(%s\.)?TextIOWrapper name='dummy' encoding='utf-8'>" % modname)
        t.mode = "r"
        self.assertRegex(repr(t),
                         r"<(%s\.)?TextIOWrapper name='dummy' mode='r' encoding='utf-8'>" % modname)
        raw.name = b"dummy"
        self.assertRegex(repr(t),
                         r"<(%s\.)?TextIOWrapper name=b'dummy' mode='r' encoding='utf-8'>" % modname)

        t.buffer.detach()
        repr(t)  # Should sio  ashiria an exception

    eleza test_recursive_repr(self):
        # Issue #25455
        raw = self.BytesIO()
        t = self.TextIOWrapper(raw)
        ukijumuisha support.swap_attr(raw, 'name', t):
            jaribu:
                repr(t)  # Should sio crash
            except RuntimeError:
                pass

    eleza test_line_buffering(self):
        r = self.BytesIO()
        b = self.BufferedWriter(r, 1000)
        t = self.TextIOWrapper(b, newline="\n", line_buffering=Kweli)
        t.write("X")
        self.assertEqual(r.getvalue(), b"")  # No flush happened
        t.write("Y\nZ")
        self.assertEqual(r.getvalue(), b"XY\nZ")  # All got flushed
        t.write("A\rB")
        self.assertEqual(r.getvalue(), b"XY\nZA\rB")

    eleza test_reconfigure_line_buffering(self):
        r = self.BytesIO()
        b = self.BufferedWriter(r, 1000)
        t = self.TextIOWrapper(b, newline="\n", line_buffering=Uongo)
        t.write("AB\nC")
        self.assertEqual(r.getvalue(), b"")

        t.reconfigure(line_buffering=Kweli)   # implicit flush
        self.assertEqual(r.getvalue(), b"AB\nC")
        t.write("DEF\nG")
        self.assertEqual(r.getvalue(), b"AB\nCDEF\nG")
        t.write("H")
        self.assertEqual(r.getvalue(), b"AB\nCDEF\nG")
        t.reconfigure(line_buffering=Uongo)   # implicit flush
        self.assertEqual(r.getvalue(), b"AB\nCDEF\nGH")
        t.write("IJ")
        self.assertEqual(r.getvalue(), b"AB\nCDEF\nGH")

        # Keeping default value
        t.reconfigure()
        t.reconfigure(line_buffering=Tupu)
        self.assertEqual(t.line_buffering, Uongo)
        t.reconfigure(line_buffering=Kweli)
        t.reconfigure()
        t.reconfigure(line_buffering=Tupu)
        self.assertEqual(t.line_buffering, Kweli)

    @unittest.skipIf(sys.flags.utf8_mode, "utf-8 mode ni enabled")
    eleza test_default_encoding(self):
        old_environ = dict(os.environ)
        jaribu:
            # try to get a user preferred encoding different than the current
            # locale encoding to check that TextIOWrapper() uses the current
            # locale encoding na sio the user preferred encoding
            kila key kwenye ('LC_ALL', 'LANG', 'LC_CTYPE'):
                ikiwa key kwenye os.environ:
                    toa os.environ[key]

            current_locale_encoding = locale.getpreferredencoding(Uongo)
            b = self.BytesIO()
            t = self.TextIOWrapper(b)
            self.assertEqual(t.encoding, current_locale_encoding)
        mwishowe:
            os.environ.clear()
            os.environ.update(old_environ)

    @support.cpython_only
    @unittest.skipIf(sys.flags.utf8_mode, "utf-8 mode ni enabled")
    eleza test_device_encoding(self):
        # Issue 15989
        agiza _testcapi
        b = self.BytesIO()
        b.fileno = lambda: _testcapi.INT_MAX + 1
        self.assertRaises(OverflowError, self.TextIOWrapper, b)
        b.fileno = lambda: _testcapi.UINT_MAX + 1
        self.assertRaises(OverflowError, self.TextIOWrapper, b)

    eleza test_encoding(self):
        # Check the encoding attribute ni always set, na valid
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="utf-8")
        self.assertEqual(t.encoding, "utf-8")
        t = self.TextIOWrapper(b)
        self.assertIsNotTupu(t.encoding)
        codecs.lookup(t.encoding)

    eleza test_encoding_errors_reading(self):
        # (1) default
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii")
        self.assertRaises(UnicodeError, t.read)
        # (2) explicit strict
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="strict")
        self.assertRaises(UnicodeError, t.read)
        # (3) ignore
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="ignore")
        self.assertEqual(t.read(), "abc\n\n")
        # (4) replace
        b = self.BytesIO(b"abc\n\xff\n")
        t = self.TextIOWrapper(b, encoding="ascii", errors="replace")
        self.assertEqual(t.read(), "abc\n\ufffd\n")

    eleza test_encoding_errors_writing(self):
        # (1) default
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii")
        self.assertRaises(UnicodeError, t.write, "\xff")
        # (2) explicit strict
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="strict")
        self.assertRaises(UnicodeError, t.write, "\xff")
        # (3) ignore
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="ignore",
                             newline="\n")
        t.write("abc\xffdef\n")
        t.flush()
        self.assertEqual(b.getvalue(), b"abcdef\n")
        # (4) replace
        b = self.BytesIO()
        t = self.TextIOWrapper(b, encoding="ascii", errors="replace",
                             newline="\n")
        t.write("abc\xffdef\n")
        t.flush()
        self.assertEqual(b.getvalue(), b"abc?def\n")

    eleza test_newlines(self):
        input_lines = [ "unix\n", "windows\r\n", "os9\r", "last\n", "nonl" ]

        tests = [
            [ Tupu, [ 'unix\n', 'windows\n', 'os9\n', 'last\n', 'nonl' ] ],
            [ '', input_lines ],
            [ '\n', [ "unix\n", "windows\r\n", "os9\rlast\n", "nonl" ] ],
            [ '\r\n', [ "unix\nwindows\r\n", "os9\rlast\nnonl" ] ],
            [ '\r', [ "unix\nwindows\r", "\nos9\r", "last\nnonl" ] ],
        ]
        encodings = (
            'utf-8', 'latin-1',
            'utf-16', 'utf-16-le', 'utf-16-be',
            'utf-32', 'utf-32-le', 'utf-32-be',
        )

        # Try a range of buffer sizes to test the case where \r ni the last
        # character kwenye TextIOWrapper._pending_line.
        kila encoding kwenye encodings:
            # XXX: str.encode() should rudisha bytes
            data = bytes(''.join(input_lines).encode(encoding))
            kila do_reads kwenye (Uongo, Kweli):
                kila bufsize kwenye range(1, 10):
                    kila newline, exp_lines kwenye tests:
                        bufio = self.BufferedReader(self.BytesIO(data), bufsize)
                        textio = self.TextIOWrapper(bufio, newline=newline,
                                                  encoding=encoding)
                        ikiwa do_reads:
                            got_lines = []
                            wakati Kweli:
                                c2 = textio.read(2)
                                ikiwa c2 == '':
                                    koma
                                self.assertEqual(len(c2), 2)
                                got_lines.append(c2 + textio.readline())
                        isipokua:
                            got_lines = list(textio)

                        kila got_line, exp_line kwenye zip(got_lines, exp_lines):
                            self.assertEqual(got_line, exp_line)
                        self.assertEqual(len(got_lines), len(exp_lines))

    eleza test_newlines_uliza(self):
        testdata = b"AAA\nBB\x00B\nCCC\rDDD\rEEE\r\nFFF\r\nGGG"
        normalized = testdata.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        kila newline, expected kwenye [
            (Tupu, normalized.decode("ascii").splitlines(keepends=Kweli)),
            ("", testdata.decode("ascii").splitlines(keepends=Kweli)),
            ("\n", ["AAA\n", "BB\x00B\n", "CCC\rDDD\rEEE\r\n", "FFF\r\n", "GGG"]),
            ("\r\n", ["AAA\nBB\x00B\nCCC\rDDD\rEEE\r\n", "FFF\r\n", "GGG"]),
            ("\r",  ["AAA\nBB\x00B\nCCC\r", "DDD\r", "EEE\r", "\nFFF\r", "\nGGG"]),
            ]:
            buf = self.BytesIO(testdata)
            txt = self.TextIOWrapper(buf, encoding="ascii", newline=newline)
            self.assertEqual(txt.readlines(), expected)
            txt.seek(0)
            self.assertEqual(txt.read(), "".join(expected))

    eleza test_newlines_output(self):
        testdict = {
            "": b"AAA\nBBB\nCCC\nX\rY\r\nZ",
            "\n": b"AAA\nBBB\nCCC\nX\rY\r\nZ",
            "\r": b"AAA\rBBB\rCCC\rX\rY\r\rZ",
            "\r\n": b"AAA\r\nBBB\r\nCCC\r\nX\rY\r\r\nZ",
            }
        tests = [(Tupu, testdict[os.linesep])] + sorted(testdict.items())
        kila newline, expected kwenye tests:
            buf = self.BytesIO()
            txt = self.TextIOWrapper(buf, encoding="ascii", newline=newline)
            txt.write("AAA\nB")
            txt.write("BB\nCCC\n")
            txt.write("X\rY\r\nZ")
            txt.flush()
            self.assertEqual(buf.closed, Uongo)
            self.assertEqual(buf.getvalue(), expected)

    eleza test_destructor(self):
        l = []
        base = self.BytesIO
        kundi MyBytesIO(base):
            eleza close(self):
                l.append(self.getvalue())
                base.close(self)
        b = MyBytesIO()
        t = self.TextIOWrapper(b, encoding="ascii")
        t.write("abc")
        toa t
        support.gc_collect()
        self.assertEqual([b"abc"], l)

    eleza test_override_destructor(self):
        record = []
        kundi MyTextIO(self.TextIOWrapper):
            eleza __del__(self):
                record.append(1)
                jaribu:
                    f = super().__del__
                except AttributeError:
                    pass
                isipokua:
                    f()
            eleza close(self):
                record.append(2)
                super().close()
            eleza flush(self):
                record.append(3)
                super().flush()
        b = self.BytesIO()
        t = MyTextIO(b, encoding="ascii")
        toa t
        support.gc_collect()
        self.assertEqual(record, [1, 2, 3])

    eleza test_error_through_destructor(self):
        # Test that the exception state ni sio modified by a destructor,
        # even ikiwa close() fails.
        rawio = self.CloseFailureIO()
        ukijumuisha support.catch_unraisable_exception() as cm:
            ukijumuisha self.assertRaises(AttributeError):
                self.TextIOWrapper(rawio).xyzzy

            ikiwa sio IOBASE_EMITS_UNRAISABLE:
                self.assertIsTupu(cm.unraisable)
            elikiwa cm.unraisable ni sio Tupu:
                self.assertEqual(cm.unraisable.exc_type, OSError)

    # Systematic tests of the text I/O API

    eleza test_basic_io(self):
        kila chunksize kwenye (1, 2, 3, 4, 5, 15, 16, 17, 31, 32, 33, 63, 64, 65):
            kila enc kwenye "ascii", "latin-1", "utf-8" :# , "utf-16-be", "utf-16-le":
                f = self.open(support.TESTFN, "w+", encoding=enc)
                f._CHUNK_SIZE = chunksize
                self.assertEqual(f.write("abc"), 3)
                f.close()
                f = self.open(support.TESTFN, "r+", encoding=enc)
                f._CHUNK_SIZE = chunksize
                self.assertEqual(f.tell(), 0)
                self.assertEqual(f.read(), "abc")
                cookie = f.tell()
                self.assertEqual(f.seek(0), 0)
                self.assertEqual(f.read(Tupu), "abc")
                f.seek(0)
                self.assertEqual(f.read(2), "ab")
                self.assertEqual(f.read(1), "c")
                self.assertEqual(f.read(1), "")
                self.assertEqual(f.read(), "")
                self.assertEqual(f.tell(), cookie)
                self.assertEqual(f.seek(0), 0)
                self.assertEqual(f.seek(0, 2), cookie)
                self.assertEqual(f.write("def"), 3)
                self.assertEqual(f.seek(cookie), cookie)
                self.assertEqual(f.read(), "def")
                ikiwa enc.startswith("utf"):
                    self.multi_line_test(f, enc)
                f.close()

    eleza multi_line_test(self, f, enc):
        f.seek(0)
        f.truncate()
        sample = "s\xff\u0fff\uffff"
        wlines = []
        kila size kwenye (0, 1, 2, 3, 4, 5, 30, 31, 32, 33, 62, 63, 64, 65, 1000):
            chars = []
            kila i kwenye range(size):
                chars.append(sample[i % len(sample)])
            line = "".join(chars) + "\n"
            wlines.append((f.tell(), line))
            f.write(line)
        f.seek(0)
        rlines = []
        wakati Kweli:
            pos = f.tell()
            line = f.readline()
            ikiwa sio line:
                koma
            rlines.append((pos, line))
        self.assertEqual(rlines, wlines)

    eleza test_telling(self):
        f = self.open(support.TESTFN, "w+", encoding="utf-8")
        p0 = f.tell()
        f.write("\xff\n")
        p1 = f.tell()
        f.write("\xff\n")
        p2 = f.tell()
        f.seek(0)
        self.assertEqual(f.tell(), p0)
        self.assertEqual(f.readline(), "\xff\n")
        self.assertEqual(f.tell(), p1)
        self.assertEqual(f.readline(), "\xff\n")
        self.assertEqual(f.tell(), p2)
        f.seek(0)
        kila line kwenye f:
            self.assertEqual(line, "\xff\n")
            self.assertRaises(OSError, f.tell)
        self.assertEqual(f.tell(), p2)
        f.close()

    eleza test_seeking(self):
        chunk_size = _default_chunk_size()
        prefix_size = chunk_size - 2
        u_prefix = "a" * prefix_size
        prefix = bytes(u_prefix.encode("utf-8"))
        self.assertEqual(len(u_prefix), len(prefix))
        u_suffix = "\u8888\n"
        suffix = bytes(u_suffix.encode("utf-8"))
        line = prefix + suffix
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(line*2)
        ukijumuisha self.open(support.TESTFN, "r", encoding="utf-8") as f:
            s = f.read(prefix_size)
            self.assertEqual(s, str(prefix, "ascii"))
            self.assertEqual(f.tell(), prefix_size)
            self.assertEqual(f.readline(), u_suffix)

    eleza test_seeking_too(self):
        # Regression test kila a specific bug
        data = b'\xe0\xbf\xbf\n'
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            f.write(data)
        ukijumuisha self.open(support.TESTFN, "r", encoding="utf-8") as f:
            f._CHUNK_SIZE  # Just test that it exists
            f._CHUNK_SIZE = 2
            f.readline()
            f.tell()

    eleza test_seek_and_tell(self):
        #Test seek/tell using the StatefulIncrementalDecoder.
        # Make test faster by doing smaller seeks
        CHUNK_SIZE = 128

        eleza test_seek_and_tell_with_data(data, min_pos=0):
            """Tell/seek to various points within a data stream na ensure
            that the decoded data returned by read() ni consistent."""
            f = self.open(support.TESTFN, 'wb')
            f.write(data)
            f.close()
            f = self.open(support.TESTFN, encoding='test_decoder')
            f._CHUNK_SIZE = CHUNK_SIZE
            decoded = f.read()
            f.close()

            kila i kwenye range(min_pos, len(decoded) + 1): # seek positions
                kila j kwenye [1, 5, len(decoded) - i]: # read lengths
                    f = self.open(support.TESTFN, encoding='test_decoder')
                    self.assertEqual(f.read(i), decoded[:i])
                    cookie = f.tell()
                    self.assertEqual(f.read(j), decoded[i:i + j])
                    f.seek(cookie)
                    self.assertEqual(f.read(), decoded[i:])
                    f.close()

        # Enable the test decoder.
        StatefulIncrementalDecoder.codecEnabled = 1

        # Run the tests.
        jaribu:
            # Try each test case.
            kila input, _, _ kwenye StatefulIncrementalDecoderTest.test_cases:
                test_seek_and_tell_with_data(input)

            # Position each test case so that it crosses a chunk boundary.
            kila input, _, _ kwenye StatefulIncrementalDecoderTest.test_cases:
                offset = CHUNK_SIZE - len(input)//2
                prefix = b'.'*offset
                # Don't bother seeking into the prefix (takes too long).
                min_pos = offset*2
                test_seek_and_tell_with_data(prefix + input, min_pos)

        # Ensure our test decoder won't interfere ukijumuisha subsequent tests.
        mwishowe:
            StatefulIncrementalDecoder.codecEnabled = 0

    eleza test_multibyte_seek_and_tell(self):
        f = self.open(support.TESTFN, "w", encoding="euc_jp")
        f.write("AB\n\u3046\u3048\n")
        f.close()

        f = self.open(support.TESTFN, "r", encoding="euc_jp")
        self.assertEqual(f.readline(), "AB\n")
        p0 = f.tell()
        self.assertEqual(f.readline(), "\u3046\u3048\n")
        p1 = f.tell()
        f.seek(p0)
        self.assertEqual(f.readline(), "\u3046\u3048\n")
        self.assertEqual(f.tell(), p1)
        f.close()

    eleza test_seek_with_encoder_state(self):
        f = self.open(support.TESTFN, "w", encoding="euc_jis_2004")
        f.write("\u00e6\u0300")
        p0 = f.tell()
        f.write("\u00e6")
        f.seek(p0)
        f.write("\u0300")
        f.close()

        f = self.open(support.TESTFN, "r", encoding="euc_jis_2004")
        self.assertEqual(f.readline(), "\u00e6\u0300\u0300")
        f.close()

    eleza test_encoded_writes(self):
        data = "1234567890"
        tests = ("utf-16",
                 "utf-16-le",
                 "utf-16-be",
                 "utf-32",
                 "utf-32-le",
                 "utf-32-be")
        kila encoding kwenye tests:
            buf = self.BytesIO()
            f = self.TextIOWrapper(buf, encoding=encoding)
            # Check ikiwa the BOM ni written only once (see issue1753).
            f.write(data)
            f.write(data)
            f.seek(0)
            self.assertEqual(f.read(), data * 2)
            f.seek(0)
            self.assertEqual(f.read(), data * 2)
            self.assertEqual(buf.getvalue(), (data * 2).encode(encoding))

    eleza test_unreadable(self):
        kundi UnReadable(self.BytesIO):
            eleza readable(self):
                rudisha Uongo
        txt = self.TextIOWrapper(UnReadable())
        self.assertRaises(OSError, txt.read)

    eleza test_read_one_by_one(self):
        txt = self.TextIOWrapper(self.BytesIO(b"AA\r\nBB"))
        reads = ""
        wakati Kweli:
            c = txt.read(1)
            ikiwa sio c:
                koma
            reads += c
        self.assertEqual(reads, "AA\nBB")

    eleza test_readlines(self):
        txt = self.TextIOWrapper(self.BytesIO(b"AA\nBB\nCC"))
        self.assertEqual(txt.readlines(), ["AA\n", "BB\n", "CC"])
        txt.seek(0)
        self.assertEqual(txt.readlines(Tupu), ["AA\n", "BB\n", "CC"])
        txt.seek(0)
        self.assertEqual(txt.readlines(5), ["AA\n", "BB\n"])

    # read kwenye amounts equal to TextIOWrapper._CHUNK_SIZE which ni 128.
    eleza test_read_by_chunk(self):
        # make sure "\r\n" straddles 128 char boundary.
        txt = self.TextIOWrapper(self.BytesIO(b"A" * 127 + b"\r\nB"))
        reads = ""
        wakati Kweli:
            c = txt.read(128)
            ikiwa sio c:
                koma
            reads += c
        self.assertEqual(reads, "A"*127+"\nB")

    eleza test_writelines(self):
        l = ['ab', 'cd', 'ef']
        buf = self.BytesIO()
        txt = self.TextIOWrapper(buf)
        txt.writelines(l)
        txt.flush()
        self.assertEqual(buf.getvalue(), b'abcdef')

    eleza test_writelines_userlist(self):
        l = UserList(['ab', 'cd', 'ef'])
        buf = self.BytesIO()
        txt = self.TextIOWrapper(buf)
        txt.writelines(l)
        txt.flush()
        self.assertEqual(buf.getvalue(), b'abcdef')

    eleza test_writelines_error(self):
        txt = self.TextIOWrapper(self.BytesIO())
        self.assertRaises(TypeError, txt.writelines, [1, 2, 3])
        self.assertRaises(TypeError, txt.writelines, Tupu)
        self.assertRaises(TypeError, txt.writelines, b'abc')

    eleza test_issue1395_1(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")

        # read one char at a time
        reads = ""
        wakati Kweli:
            c = txt.read(1)
            ikiwa sio c:
                koma
            reads += c
        self.assertEqual(reads, self.normalized)

    eleza test_issue1395_2(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = ""
        wakati Kweli:
            c = txt.read(4)
            ikiwa sio c:
                koma
            reads += c
        self.assertEqual(reads, self.normalized)

    eleza test_issue1395_3(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        reads += txt.read(4)
        reads += txt.readline()
        reads += txt.readline()
        reads += txt.readline()
        self.assertEqual(reads, self.normalized)

    eleza test_issue1395_4(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        reads += txt.read()
        self.assertEqual(reads, self.normalized)

    eleza test_issue1395_5(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt._CHUNK_SIZE = 4

        reads = txt.read(4)
        pos = txt.tell()
        txt.seek(0)
        txt.seek(pos)
        self.assertEqual(txt.read(4), "BBB\n")

    eleza test_issue2282(self):
        buffer = self.BytesIO(self.testdata)
        txt = self.TextIOWrapper(buffer, encoding="ascii")

        self.assertEqual(buffer.seekable(), txt.seekable())

    eleza test_append_bom(self):
        # The BOM ni sio written again when appending to a non-empty file
        filename = support.TESTFN
        kila charset kwenye ('utf-8-sig', 'utf-16', 'utf-32'):
            ukijumuisha self.open(filename, 'w', encoding=charset) as f:
                f.write('aaa')
                pos = f.tell()
            ukijumuisha self.open(filename, 'rb') as f:
                self.assertEqual(f.read(), 'aaa'.encode(charset))

            ukijumuisha self.open(filename, 'a', encoding=charset) as f:
                f.write('xxx')
            ukijumuisha self.open(filename, 'rb') as f:
                self.assertEqual(f.read(), 'aaaxxx'.encode(charset))

    eleza test_seek_bom(self):
        # Same test, but when seeking manually
        filename = support.TESTFN
        kila charset kwenye ('utf-8-sig', 'utf-16', 'utf-32'):
            ukijumuisha self.open(filename, 'w', encoding=charset) as f:
                f.write('aaa')
                pos = f.tell()
            ukijumuisha self.open(filename, 'r+', encoding=charset) as f:
                f.seek(pos)
                f.write('zzz')
                f.seek(0)
                f.write('bbb')
            ukijumuisha self.open(filename, 'rb') as f:
                self.assertEqual(f.read(), 'bbbzzz'.encode(charset))

    eleza test_seek_append_bom(self):
        # Same test, but first seek to the start na then to the end
        filename = support.TESTFN
        kila charset kwenye ('utf-8-sig', 'utf-16', 'utf-32'):
            ukijumuisha self.open(filename, 'w', encoding=charset) as f:
                f.write('aaa')
            ukijumuisha self.open(filename, 'a', encoding=charset) as f:
                f.seek(0)
                f.seek(0, self.SEEK_END)
                f.write('xxx')
            ukijumuisha self.open(filename, 'rb') as f:
                self.assertEqual(f.read(), 'aaaxxx'.encode(charset))

    eleza test_errors_property(self):
        ukijumuisha self.open(support.TESTFN, "w") as f:
            self.assertEqual(f.errors, "strict")
        ukijumuisha self.open(support.TESTFN, "w", errors="replace") as f:
            self.assertEqual(f.errors, "replace")

    @support.no_tracing
    eleza test_threads_write(self):
        # Issue6750: concurrent writes could duplicate data
        event = threading.Event()
        ukijumuisha self.open(support.TESTFN, "w", buffering=1) as f:
            eleza run(n):
                text = "Thread%03d\n" % n
                event.wait()
                f.write(text)
            threads = [threading.Thread(target=run, args=(x,))
                       kila x kwenye range(20)]
            ukijumuisha support.start_threads(threads, event.set):
                time.sleep(0.02)
        ukijumuisha self.open(support.TESTFN) as f:
            content = f.read()
            kila n kwenye range(20):
                self.assertEqual(content.count("Thread%03d\n" % n), 1)

    eleza test_flush_error_on_close(self):
        # Test that text file ni closed despite failed flush
        # na that flush() ni called before file closed.
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        closed = []
        eleza bad_flush():
            closed[:] = [txt.closed, txt.buffer.closed]
             ashiria OSError()
        txt.flush = bad_flush
        self.assertRaises(OSError, txt.close) # exception sio swallowed
        self.assertKweli(txt.closed)
        self.assertKweli(txt.buffer.closed)
        self.assertKweli(closed)      # flush() called
        self.assertUongo(closed[0])  # flush() called before file closed
        self.assertUongo(closed[1])
        txt.flush = lambda: Tupu  # koma reference loop

    eleza test_close_error_on_close(self):
        buffer = self.BytesIO(self.testdata)
        eleza bad_flush():
             ashiria OSError('flush')
        eleza bad_close():
             ashiria OSError('close')
        buffer.close = bad_close
        txt = self.TextIOWrapper(buffer, encoding="ascii")
        txt.flush = bad_flush
        ukijumuisha self.assertRaises(OSError) as err: # exception sio swallowed
            txt.close()
        self.assertEqual(err.exception.args, ('close',))
        self.assertIsInstance(err.exception.__context__, OSError)
        self.assertEqual(err.exception.__context__.args, ('flush',))
        self.assertUongo(txt.closed)

        # Silence destructor error
        buffer.close = lambda: Tupu
        txt.flush = lambda: Tupu

    eleza test_nonnormalized_close_error_on_close(self):
        # Issue #21677
        buffer = self.BytesIO(self.testdata)
        eleza bad_flush():
             ashiria non_existing_flush
        eleza bad_close():
             ashiria non_existing_close
        buffer.close = bad_close
        txt = self.TextIOWrapper(buffer, encoding="ascii")
        txt.flush = bad_flush
        ukijumuisha self.assertRaises(NameError) as err: # exception sio swallowed
            txt.close()
        self.assertIn('non_existing_close', str(err.exception))
        self.assertIsInstance(err.exception.__context__, NameError)
        self.assertIn('non_existing_flush', str(err.exception.__context__))
        self.assertUongo(txt.closed)

        # Silence destructor error
        buffer.close = lambda: Tupu
        txt.flush = lambda: Tupu

    eleza test_multi_close(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        txt.close()
        txt.close()
        txt.close()
        self.assertRaises(ValueError, txt.flush)

    eleza test_unseekable(self):
        txt = self.TextIOWrapper(self.MockUnseekableIO(self.testdata))
        self.assertRaises(self.UnsupportedOperation, txt.tell)
        self.assertRaises(self.UnsupportedOperation, txt.seek, 0)

    eleza test_readonly_attributes(self):
        txt = self.TextIOWrapper(self.BytesIO(self.testdata), encoding="ascii")
        buf = self.BytesIO(self.testdata)
        ukijumuisha self.assertRaises(AttributeError):
            txt.buffer = buf

    eleza test_rawio(self):
        # Issue #12591: TextIOWrapper must work ukijumuisha raw I/O objects, so
        # that subprocess.Popen() can have the required unbuffered
        # semantics ukijumuisha universal_newlines=Kweli.
        raw = self.MockRawIO([b'abc', b'def', b'ghi\njkl\nopq\n'])
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        # Reads
        self.assertEqual(txt.read(4), 'abcd')
        self.assertEqual(txt.readline(), 'efghi\n')
        self.assertEqual(list(txt), ['jkl\n', 'opq\n'])

    eleza test_rawio_write_through(self):
        # Issue #12591: ukijumuisha write_through=Kweli, writes don't need a flush
        raw = self.MockRawIO([b'abc', b'def', b'ghi\njkl\nopq\n'])
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n',
                                 write_through=Kweli)
        txt.write('1')
        txt.write('23\n4')
        txt.write('5')
        self.assertEqual(b''.join(raw._write_stack), b'123\n45')

    eleza test_bufio_write_through(self):
        # Issue #21396: write_through=Kweli doesn't force a flush()
        # on the underlying binary buffered object.
        flush_called, write_called = [], []
        kundi BufferedWriter(self.BufferedWriter):
            eleza flush(self, *args, **kwargs):
                flush_called.append(Kweli)
                rudisha super().flush(*args, **kwargs)
            eleza write(self, *args, **kwargs):
                write_called.append(Kweli)
                rudisha super().write(*args, **kwargs)

        rawio = self.BytesIO()
        data = b"a"
        bufio = BufferedWriter(rawio, len(data)*2)
        textio = self.TextIOWrapper(bufio, encoding='ascii',
                                    write_through=Kweli)
        # write to the buffered io but don't overflow the buffer
        text = data.decode('ascii')
        textio.write(text)

        # buffer.flush ni sio called ukijumuisha write_through=Kweli
        self.assertUongo(flush_called)
        # buffer.write *is* called ukijumuisha write_through=Kweli
        self.assertKweli(write_called)
        self.assertEqual(rawio.getvalue(), b"") # no flush

        write_called = [] # reset
        textio.write(text * 10) # total content ni larger than bufio buffer
        self.assertKweli(write_called)
        self.assertEqual(rawio.getvalue(), data * 11) # all flushed

    eleza test_reconfigure_write_through(self):
        raw = self.MockRawIO([])
        t = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        t.write('1')
        t.reconfigure(write_through=Kweli)  # implied flush
        self.assertEqual(t.write_through, Kweli)
        self.assertEqual(b''.join(raw._write_stack), b'1')
        t.write('23')
        self.assertEqual(b''.join(raw._write_stack), b'123')
        t.reconfigure(write_through=Uongo)
        self.assertEqual(t.write_through, Uongo)
        t.write('45')
        t.flush()
        self.assertEqual(b''.join(raw._write_stack), b'12345')
        # Keeping default value
        t.reconfigure()
        t.reconfigure(write_through=Tupu)
        self.assertEqual(t.write_through, Uongo)
        t.reconfigure(write_through=Kweli)
        t.reconfigure()
        t.reconfigure(write_through=Tupu)
        self.assertEqual(t.write_through, Kweli)

    eleza test_read_nonbytes(self):
        # Issue #17106
        # Crash when underlying read() returns non-bytes
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.read, 1)
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.readline)
        t = self.TextIOWrapper(self.StringIO('a'))
        self.assertRaises(TypeError, t.read)

    eleza test_illegal_encoder(self):
        # Issue 31271: Calling write() wakati the rudisha value of encoder's
        # encode() ni invalid shouldn't cause an assertion failure.
        rot13 = codecs.lookup("rot13")
        ukijumuisha support.swap_attr(rot13, '_is_text_encoding', Kweli):
            t = io.TextIOWrapper(io.BytesIO(b'foo'), encoding="rot13")
        self.assertRaises(TypeError, t.write, 'bar')

    eleza test_illegal_decoder(self):
        # Issue #17106
        # Bypass the early encoding check added kwenye issue 20404
        eleza _make_illegal_wrapper():
            quopri = codecs.lookup("quopri")
            quopri._is_text_encoding = Kweli
            jaribu:
                t = self.TextIOWrapper(self.BytesIO(b'aaaaaa'),
                                       newline='\n', encoding="quopri")
            mwishowe:
                quopri._is_text_encoding = Uongo
            rudisha t
        # Crash when decoder returns non-string
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.read, 1)
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.readline)
        t = _make_illegal_wrapper()
        self.assertRaises(TypeError, t.read)

        # Issue 31243: calling read() wakati the rudisha value of decoder's
        # getstate() ni invalid should neither crash the interpreter nor
        #  ashiria a SystemError.
        eleza _make_very_illegal_wrapper(getstate_ret_val):
            kundi BadDecoder:
                eleza getstate(self):
                    rudisha getstate_ret_val
            eleza _get_bad_decoder(dummy):
                rudisha BadDecoder()
            quopri = codecs.lookup("quopri")
            ukijumuisha support.swap_attr(quopri, 'incrementaldecoder',
                                   _get_bad_decoder):
                rudisha _make_illegal_wrapper()
        t = _make_very_illegal_wrapper(42)
        self.assertRaises(TypeError, t.read, 42)
        t = _make_very_illegal_wrapper(())
        self.assertRaises(TypeError, t.read, 42)
        t = _make_very_illegal_wrapper((1, 2))
        self.assertRaises(TypeError, t.read, 42)

    eleza _check_create_at_shutdown(self, **kwargs):
        # Issue #20037: creating a TextIOWrapper at shutdown
        # shouldn't crash the interpreter.
        iomod = self.io.__name__
        code = """ikiwa 1:
            agiza codecs
            agiza {iomod} as io

            # Avoid looking up codecs at shutdown
            codecs.lookup('utf-8')

            kundi C:
                eleza __init__(self):
                    self.buf = io.BytesIO()
                eleza __del__(self):
                    io.TextIOWrapper(self.buf, **{kwargs})
                    andika("ok")
            c = C()
            """.format(iomod=iomod, kwargs=kwargs)
        rudisha assert_python_ok("-c", code)

    @support.requires_type_collecting
    eleza test_create_at_shutdown_without_encoding(self):
        rc, out, err = self._check_create_at_shutdown()
        ikiwa err:
            # Can error out ukijumuisha a RuntimeError ikiwa the module state
            # isn't found.
            self.assertIn(self.shutdown_error, err.decode())
        isipokua:
            self.assertEqual("ok", out.decode().strip())

    @support.requires_type_collecting
    eleza test_create_at_shutdown_with_encoding(self):
        rc, out, err = self._check_create_at_shutdown(encoding='utf-8',
                                                      errors='strict')
        self.assertUongo(err)
        self.assertEqual("ok", out.decode().strip())

    eleza test_read_byteslike(self):
        r = MemviewBytesIO(b'Just some random string\n')
        t = self.TextIOWrapper(r, 'utf-8')

        # TextIOwrapper will sio read the full string, because
        # we truncate it to a multiple of the native int size
        # so that we can construct a more complex memoryview.
        bytes_val =  _to_memoryview(r.getvalue()).tobytes()

        self.assertEqual(t.read(200), bytes_val.decode('utf-8'))

    eleza test_issue22849(self):
        kundi F(object):
            eleza readable(self): rudisha Kweli
            eleza writable(self): rudisha Kweli
            eleza seekable(self): rudisha Kweli

        kila i kwenye range(10):
            jaribu:
                self.TextIOWrapper(F(), encoding='utf-8')
            except Exception:
                pass

        F.tell = lambda x: 0
        t = self.TextIOWrapper(F(), encoding='utf-8')

    eleza test_reconfigure_encoding_read(self):
        # latin1 -> utf8
        # (latin1 can decode utf-8 encoded string)
        data = 'abc\xe9\n'.encode('latin1') + 'd\xe9f\n'.encode('utf8')
        raw = self.BytesIO(data)
        txt = self.TextIOWrapper(raw, encoding='latin1', newline='\n')
        self.assertEqual(txt.readline(), 'abc\xe9\n')
        ukijumuisha self.assertRaises(self.UnsupportedOperation):
            txt.reconfigure(encoding='utf-8')
        ukijumuisha self.assertRaises(self.UnsupportedOperation):
            txt.reconfigure(newline=Tupu)

    eleza test_reconfigure_write_fromascii(self):
        # ascii has a specific encodefunc kwenye the C implementation,
        # but utf-8-sig has not. Make sure that we get rid of the
        # cached encodefunc when we switch encoders.
        raw = self.BytesIO()
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        txt.write('foo\n')
        txt.reconfigure(encoding='utf-8-sig')
        txt.write('\xe9\n')
        txt.flush()
        self.assertEqual(raw.getvalue(), b'foo\n\xc3\xa9\n')

    eleza test_reconfigure_write(self):
        # latin -> utf8
        raw = self.BytesIO()
        txt = self.TextIOWrapper(raw, encoding='latin1', newline='\n')
        txt.write('abc\xe9\n')
        txt.reconfigure(encoding='utf-8')
        self.assertEqual(raw.getvalue(), b'abc\xe9\n')
        txt.write('d\xe9f\n')
        txt.flush()
        self.assertEqual(raw.getvalue(), b'abc\xe9\nd\xc3\xa9f\n')

        # ascii -> utf-8-sig: ensure that no BOM ni written kwenye the middle of
        # the file
        raw = self.BytesIO()
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        txt.write('abc\n')
        txt.reconfigure(encoding='utf-8-sig')
        txt.write('d\xe9f\n')
        txt.flush()
        self.assertEqual(raw.getvalue(), b'abc\nd\xc3\xa9f\n')

    eleza test_reconfigure_write_non_seekable(self):
        raw = self.BytesIO()
        raw.seekable = lambda: Uongo
        raw.seek = Tupu
        txt = self.TextIOWrapper(raw, encoding='ascii', newline='\n')
        txt.write('abc\n')
        txt.reconfigure(encoding='utf-8-sig')
        txt.write('d\xe9f\n')
        txt.flush()

        # If the raw stream ni sio seekable, there'll be a BOM
        self.assertEqual(raw.getvalue(),  b'abc\n\xef\xbb\xbfd\xc3\xa9f\n')

    eleza test_reconfigure_defaults(self):
        txt = self.TextIOWrapper(self.BytesIO(), 'ascii', 'replace', '\n')
        txt.reconfigure(encoding=Tupu)
        self.assertEqual(txt.encoding, 'ascii')
        self.assertEqual(txt.errors, 'replace')
        txt.write('LF\n')

        txt.reconfigure(newline='\r\n')
        self.assertEqual(txt.encoding, 'ascii')
        self.assertEqual(txt.errors, 'replace')

        txt.reconfigure(errors='ignore')
        self.assertEqual(txt.encoding, 'ascii')
        self.assertEqual(txt.errors, 'ignore')
        txt.write('CRLF\n')

        txt.reconfigure(encoding='utf-8', newline=Tupu)
        self.assertEqual(txt.errors, 'strict')
        txt.seek(0)
        self.assertEqual(txt.read(), 'LF\nCRLF\n')

        self.assertEqual(txt.detach().getvalue(), b'LF\nCRLF\r\n')

    eleza test_reconfigure_newline(self):
        raw = self.BytesIO(b'CR\rEOF')
        txt = self.TextIOWrapper(raw, 'ascii', newline='\n')
        txt.reconfigure(newline=Tupu)
        self.assertEqual(txt.readline(), 'CR\n')
        raw = self.BytesIO(b'CR\rEOF')
        txt = self.TextIOWrapper(raw, 'ascii', newline='\n')
        txt.reconfigure(newline='')
        self.assertEqual(txt.readline(), 'CR\r')
        raw = self.BytesIO(b'CR\rLF\nEOF')
        txt = self.TextIOWrapper(raw, 'ascii', newline='\r')
        txt.reconfigure(newline='\n')
        self.assertEqual(txt.readline(), 'CR\rLF\n')
        raw = self.BytesIO(b'LF\nCR\rEOF')
        txt = self.TextIOWrapper(raw, 'ascii', newline='\n')
        txt.reconfigure(newline='\r')
        self.assertEqual(txt.readline(), 'LF\nCR\r')
        raw = self.BytesIO(b'CR\rCRLF\r\nEOF')
        txt = self.TextIOWrapper(raw, 'ascii', newline='\r')
        txt.reconfigure(newline='\r\n')
        self.assertEqual(txt.readline(), 'CR\rCRLF\r\n')

        txt = self.TextIOWrapper(self.BytesIO(), 'ascii', newline='\r')
        txt.reconfigure(newline=Tupu)
        txt.write('linesep\n')
        txt.reconfigure(newline='')
        txt.write('LF\n')
        txt.reconfigure(newline='\n')
        txt.write('LF\n')
        txt.reconfigure(newline='\r')
        txt.write('CR\n')
        txt.reconfigure(newline='\r\n')
        txt.write('CRLF\n')
        expected = 'linesep' + os.linesep + 'LF\nLF\nCR\rCRLF\r\n'
        self.assertEqual(txt.detach().getvalue().decode('ascii'), expected)

    eleza test_issue25862(self):
        # Assertion failures occurred kwenye tell() after read() na write().
        t = self.TextIOWrapper(self.BytesIO(b'test'), encoding='ascii')
        t.read(1)
        t.read()
        t.tell()
        t = self.TextIOWrapper(self.BytesIO(b'test'), encoding='ascii')
        t.read(1)
        t.write('x')
        t.tell()


kundi MemviewBytesIO(io.BytesIO):
    '''A BytesIO object whose read method returns memoryviews
       rather than bytes'''

    eleza read1(self, len_):
        rudisha _to_memoryview(super().read1(len_))

    eleza read(self, len_):
        rudisha _to_memoryview(super().read(len_))

eleza _to_memoryview(buf):
    '''Convert bytes-object *buf* to a non-trivial memoryview'''

    arr = array.array('i')
    idx = len(buf) - len(buf) % arr.itemsize
    arr.frombytes(buf[:idx])
    rudisha memoryview(arr)


kundi CTextIOWrapperTest(TextIOWrapperTest):
    io = io
    shutdown_error = "RuntimeError: could sio find io module state"

    eleza test_initialization(self):
        r = self.BytesIO(b"\xc3\xa9\n\n")
        b = self.BufferedReader(r, 1000)
        t = self.TextIOWrapper(b)
        self.assertRaises(ValueError, t.__init__, b, newline='xyzzy')
        self.assertRaises(ValueError, t.read)

        t = self.TextIOWrapper.__new__(self.TextIOWrapper)
        self.assertRaises(Exception, repr, t)

    eleza test_garbage_collection(self):
        # C TextIOWrapper objects are collected, na collecting them flushes
        # all data to disk.
        # The Python version has __del__, so it ends kwenye gc.garbage instead.
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            rawio = io.FileIO(support.TESTFN, "wb")
            b = self.BufferedWriter(rawio)
            t = self.TextIOWrapper(b, encoding="ascii")
            t.write("456def")
            t.x = t
            wr = weakref.ref(t)
            toa t
            support.gc_collect()
        self.assertIsTupu(wr(), wr)
        ukijumuisha self.open(support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"456def")

    eleza test_rwpair_cleared_before_textio(self):
        # Issue 13070: TextIOWrapper's finalization would crash when called
        # after the reference to the underlying BufferedRWPair's writer got
        # cleared by the GC.
        kila i kwenye range(1000):
            b1 = self.BufferedRWPair(self.MockRawIO(), self.MockRawIO())
            t1 = self.TextIOWrapper(b1, encoding="ascii")
            b2 = self.BufferedRWPair(self.MockRawIO(), self.MockRawIO())
            t2 = self.TextIOWrapper(b2, encoding="ascii")
            # circular references
            t1.buddy = t2
            t2.buddy = t1
        support.gc_collect()

    eleza test_del__CHUNK_SIZE_SystemError(self):
        t = self.TextIOWrapper(self.BytesIO(), encoding='ascii')
        ukijumuisha self.assertRaises(AttributeError):
            toa t._CHUNK_SIZE


kundi PyTextIOWrapperTest(TextIOWrapperTest):
    io = pyio
    shutdown_error = "LookupError: unknown encoding: ascii"


kundi IncrementalNewlineDecoderTest(unittest.TestCase):

    eleza check_newline_decoding_utf8(self, decoder):
        # UTF-8 specific tests kila a newline decoder
        eleza _check_decode(b, s, **kwargs):
            # We exercise getstate() / setstate() as well as decode()
            state = decoder.getstate()
            self.assertEqual(decoder.decode(b, **kwargs), s)
            decoder.setstate(state)
            self.assertEqual(decoder.decode(b, **kwargs), s)

        _check_decode(b'\xe8\xa2\x88', "\u8888")

        _check_decode(b'\xe8', "")
        _check_decode(b'\xa2', "")
        _check_decode(b'\x88', "\u8888")

        _check_decode(b'\xe8', "")
        _check_decode(b'\xa2', "")
        _check_decode(b'\x88', "\u8888")

        _check_decode(b'\xe8', "")
        self.assertRaises(UnicodeDecodeError, decoder.decode, b'', final=Kweli)

        decoder.reset()
        _check_decode(b'\n', "\n")
        _check_decode(b'\r', "")
        _check_decode(b'', "\n", final=Kweli)
        _check_decode(b'\r', "\n", final=Kweli)

        _check_decode(b'\r', "")
        _check_decode(b'a', "\na")

        _check_decode(b'\r\r\n', "\n\n")
        _check_decode(b'\r', "")
        _check_decode(b'\r', "\n")
        _check_decode(b'\na', "\na")

        _check_decode(b'\xe8\xa2\x88\r\n', "\u8888\n")
        _check_decode(b'\xe8\xa2\x88', "\u8888")
        _check_decode(b'\n', "\n")
        _check_decode(b'\xe8\xa2\x88\r', "\u8888")
        _check_decode(b'\n', "\n")

    eleza check_newline_decoding(self, decoder, encoding):
        result = []
        ikiwa encoding ni sio Tupu:
            encoder = codecs.getincrementalencoder(encoding)()
            eleza _decode_bytewise(s):
                # Decode one byte at a time
                kila b kwenye encoder.encode(s):
                    result.append(decoder.decode(bytes([b])))
        isipokua:
            encoder = Tupu
            eleza _decode_bytewise(s):
                # Decode one char at a time
                kila c kwenye s:
                    result.append(decoder.decode(c))
        self.assertEqual(decoder.newlines, Tupu)
        _decode_bytewise("abc\n\r")
        self.assertEqual(decoder.newlines, '\n')
        _decode_bytewise("\nabc")
        self.assertEqual(decoder.newlines, ('\n', '\r\n'))
        _decode_bytewise("abc\r")
        self.assertEqual(decoder.newlines, ('\n', '\r\n'))
        _decode_bytewise("abc")
        self.assertEqual(decoder.newlines, ('\r', '\n', '\r\n'))
        _decode_bytewise("abc\r")
        self.assertEqual("".join(result), "abc\n\nabcabc\nabcabc")
        decoder.reset()
        input = "abc"
        ikiwa encoder ni sio Tupu:
            encoder.reset()
            input = encoder.encode(input)
        self.assertEqual(decoder.decode(input), "abc")
        self.assertEqual(decoder.newlines, Tupu)

    eleza test_newline_decoder(self):
        encodings = (
            # Tupu meaning the IncrementalNewlineDecoder takes unicode input
            # rather than bytes input
            Tupu, 'utf-8', 'latin-1',
            'utf-16', 'utf-16-le', 'utf-16-be',
            'utf-32', 'utf-32-le', 'utf-32-be',
        )
        kila enc kwenye encodings:
            decoder = enc na codecs.getincrementaldecoder(enc)()
            decoder = self.IncrementalNewlineDecoder(decoder, translate=Kweli)
            self.check_newline_decoding(decoder, enc)
        decoder = codecs.getincrementaldecoder("utf-8")()
        decoder = self.IncrementalNewlineDecoder(decoder, translate=Kweli)
        self.check_newline_decoding_utf8(decoder)
        self.assertRaises(TypeError, decoder.setstate, 42)

    eleza test_newline_bytes(self):
        # Issue 5433: Excessive optimization kwenye IncrementalNewlineDecoder
        eleza _check(dec):
            self.assertEqual(dec.newlines, Tupu)
            self.assertEqual(dec.decode("\u0D00"), "\u0D00")
            self.assertEqual(dec.newlines, Tupu)
            self.assertEqual(dec.decode("\u0A00"), "\u0A00")
            self.assertEqual(dec.newlines, Tupu)
        dec = self.IncrementalNewlineDecoder(Tupu, translate=Uongo)
        _check(dec)
        dec = self.IncrementalNewlineDecoder(Tupu, translate=Kweli)
        _check(dec)

    eleza test_translate(self):
        # issue 35062
        kila translate kwenye (-2, -1, 1, 2):
            decoder = codecs.getincrementaldecoder("utf-8")()
            decoder = self.IncrementalNewlineDecoder(decoder, translate)
            self.check_newline_decoding_utf8(decoder)
        decoder = codecs.getincrementaldecoder("utf-8")()
        decoder = self.IncrementalNewlineDecoder(decoder, translate=0)
        self.assertEqual(decoder.decode(b"\r\r\n"), "\r\r\n")

kundi CIncrementalNewlineDecoderTest(IncrementalNewlineDecoderTest):
    pass

kundi PyIncrementalNewlineDecoderTest(IncrementalNewlineDecoderTest):
    pass


# XXX Tests kila open()

kundi MiscIOTest(unittest.TestCase):

    eleza tearDown(self):
        support.unlink(support.TESTFN)

    eleza test___all__(self):
        kila name kwenye self.io.__all__:
            obj = getattr(self.io, name, Tupu)
            self.assertIsNotTupu(obj, name)
            ikiwa name kwenye ("open", "open_code"):
                endelea
            elikiwa "error" kwenye name.lower() ama name == "UnsupportedOperation":
                self.assertKweli(issubclass(obj, Exception), name)
            elikiwa sio name.startswith("SEEK_"):
                self.assertKweli(issubclass(obj, self.IOBase))

    eleza test_attributes(self):
        f = self.open(support.TESTFN, "wb", buffering=0)
        self.assertEqual(f.mode, "wb")
        f.close()

        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            f = self.open(support.TESTFN, "U")
        self.assertEqual(f.name,            support.TESTFN)
        self.assertEqual(f.buffer.name,     support.TESTFN)
        self.assertEqual(f.buffer.raw.name, support.TESTFN)
        self.assertEqual(f.mode,            "U")
        self.assertEqual(f.buffer.mode,     "rb")
        self.assertEqual(f.buffer.raw.mode, "rb")
        f.close()

        f = self.open(support.TESTFN, "w+")
        self.assertEqual(f.mode,            "w+")
        self.assertEqual(f.buffer.mode,     "rb+") # Does it really matter?
        self.assertEqual(f.buffer.raw.mode, "rb+")

        g = self.open(f.fileno(), "wb", closefd=Uongo)
        self.assertEqual(g.mode,     "wb")
        self.assertEqual(g.raw.mode, "wb")
        self.assertEqual(g.name,     f.fileno())
        self.assertEqual(g.raw.name, f.fileno())
        f.close()
        g.close()

    eleza test_io_after_close(self):
        kila kwargs kwenye [
                {"mode": "w"},
                {"mode": "wb"},
                {"mode": "w", "buffering": 1},
                {"mode": "w", "buffering": 2},
                {"mode": "wb", "buffering": 0},
                {"mode": "r"},
                {"mode": "rb"},
                {"mode": "r", "buffering": 1},
                {"mode": "r", "buffering": 2},
                {"mode": "rb", "buffering": 0},
                {"mode": "w+"},
                {"mode": "w+b"},
                {"mode": "w+", "buffering": 1},
                {"mode": "w+", "buffering": 2},
                {"mode": "w+b", "buffering": 0},
            ]:
            f = self.open(support.TESTFN, **kwargs)
            f.close()
            self.assertRaises(ValueError, f.flush)
            self.assertRaises(ValueError, f.fileno)
            self.assertRaises(ValueError, f.isatty)
            self.assertRaises(ValueError, f.__iter__)
            ikiwa hasattr(f, "peek"):
                self.assertRaises(ValueError, f.peek, 1)
            self.assertRaises(ValueError, f.read)
            ikiwa hasattr(f, "read1"):
                self.assertRaises(ValueError, f.read1, 1024)
                self.assertRaises(ValueError, f.read1)
            ikiwa hasattr(f, "readall"):
                self.assertRaises(ValueError, f.readall)
            ikiwa hasattr(f, "readinto"):
                self.assertRaises(ValueError, f.readinto, bytearray(1024))
            ikiwa hasattr(f, "readinto1"):
                self.assertRaises(ValueError, f.readinto1, bytearray(1024))
            self.assertRaises(ValueError, f.readline)
            self.assertRaises(ValueError, f.readlines)
            self.assertRaises(ValueError, f.readlines, 1)
            self.assertRaises(ValueError, f.seek, 0)
            self.assertRaises(ValueError, f.tell)
            self.assertRaises(ValueError, f.truncate)
            self.assertRaises(ValueError, f.write,
                              b"" ikiwa "b" kwenye kwargs['mode'] isipokua "")
            self.assertRaises(ValueError, f.writelines, [])
            self.assertRaises(ValueError, next, f)

    eleza test_blockingioerror(self):
        # Various BlockingIOError issues
        kundi C(str):
            pass
        c = C("")
        b = self.BlockingIOError(1, c)
        c.b = b
        b.c = c
        wr = weakref.ref(c)
        toa c, b
        support.gc_collect()
        self.assertIsTupu(wr(), wr)

    eleza test_abcs(self):
        # Test the visible base classes are ABCs.
        self.assertIsInstance(self.IOBase, abc.ABCMeta)
        self.assertIsInstance(self.RawIOBase, abc.ABCMeta)
        self.assertIsInstance(self.BufferedIOBase, abc.ABCMeta)
        self.assertIsInstance(self.TextIOBase, abc.ABCMeta)

    eleza _check_abc_inheritance(self, abcmodule):
        ukijumuisha self.open(support.TESTFN, "wb", buffering=0) as f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertIsInstance(f, abcmodule.RawIOBase)
            self.assertNotIsInstance(f, abcmodule.BufferedIOBase)
            self.assertNotIsInstance(f, abcmodule.TextIOBase)
        ukijumuisha self.open(support.TESTFN, "wb") as f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertNotIsInstance(f, abcmodule.RawIOBase)
            self.assertIsInstance(f, abcmodule.BufferedIOBase)
            self.assertNotIsInstance(f, abcmodule.TextIOBase)
        ukijumuisha self.open(support.TESTFN, "w") as f:
            self.assertIsInstance(f, abcmodule.IOBase)
            self.assertNotIsInstance(f, abcmodule.RawIOBase)
            self.assertNotIsInstance(f, abcmodule.BufferedIOBase)
            self.assertIsInstance(f, abcmodule.TextIOBase)

    eleza test_abc_inheritance(self):
        # Test implementations inherit kutoka their respective ABCs
        self._check_abc_inheritance(self)

    eleza test_abc_inheritance_official(self):
        # Test implementations inherit kutoka the official ABCs of the
        # baseline "io" module.
        self._check_abc_inheritance(io)

    eleza _check_warn_on_dealloc(self, *args, **kwargs):
        f = open(*args, **kwargs)
        r = repr(f)
        ukijumuisha self.assertWarns(ResourceWarning) as cm:
            f = Tupu
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))

    eleza test_warn_on_dealloc(self):
        self._check_warn_on_dealloc(support.TESTFN, "wb", buffering=0)
        self._check_warn_on_dealloc(support.TESTFN, "wb")
        self._check_warn_on_dealloc(support.TESTFN, "w")

    eleza _check_warn_on_dealloc_fd(self, *args, **kwargs):
        fds = []
        eleza cleanup_fds():
            kila fd kwenye fds:
                jaribu:
                    os.close(fd)
                except OSError as e:
                    ikiwa e.errno != errno.EBADF:
                        raise
        self.addCleanup(cleanup_fds)
        r, w = os.pipe()
        fds += r, w
        self._check_warn_on_dealloc(r, *args, **kwargs)
        # When using closefd=Uongo, there's no warning
        r, w = os.pipe()
        fds += r, w
        ukijumuisha support.check_no_resource_warning(self):
            open(r, *args, closefd=Uongo, **kwargs)

    eleza test_warn_on_dealloc_fd(self):
        self._check_warn_on_dealloc_fd("rb", buffering=0)
        self._check_warn_on_dealloc_fd("rb")
        self._check_warn_on_dealloc_fd("r")


    eleza test_pickling(self):
        # Pickling file objects ni forbidden
        kila kwargs kwenye [
                {"mode": "w"},
                {"mode": "wb"},
                {"mode": "wb", "buffering": 0},
                {"mode": "r"},
                {"mode": "rb"},
                {"mode": "rb", "buffering": 0},
                {"mode": "w+"},
                {"mode": "w+b"},
                {"mode": "w+b", "buffering": 0},
            ]:
            kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                ukijumuisha self.open(support.TESTFN, **kwargs) as f:
                    self.assertRaises(TypeError, pickle.dumps, f, protocol)

    eleza test_nonblock_pipe_write_bigbuf(self):
        self._test_nonblock_pipe_write(16*1024)

    eleza test_nonblock_pipe_write_smallbuf(self):
        self._test_nonblock_pipe_write(1024)

    @unittest.skipUnless(hasattr(os, 'set_blocking'),
                         'os.set_blocking() required kila this test')
    eleza _test_nonblock_pipe_write(self, bufsize):
        sent = []
        received = []
        r, w = os.pipe()
        os.set_blocking(r, Uongo)
        os.set_blocking(w, Uongo)

        # To exercise all code paths kwenye the C implementation we need
        # to play ukijumuisha buffer sizes.  For instance, ikiwa we choose a
        # buffer size less than ama equal to _PIPE_BUF (4096 on Linux)
        # then we will never get a partial write of the buffer.
        rf = self.open(r, mode='rb', closefd=Kweli, buffering=bufsize)
        wf = self.open(w, mode='wb', closefd=Kweli, buffering=bufsize)

        ukijumuisha rf, wf:
            kila N kwenye 9999, 73, 7574:
                jaribu:
                    i = 0
                    wakati Kweli:
                        msg = bytes([i % 26 + 97]) * N
                        sent.append(msg)
                        wf.write(msg)
                        i += 1

                except self.BlockingIOError as e:
                    self.assertEqual(e.args[0], errno.EAGAIN)
                    self.assertEqual(e.args[2], e.characters_written)
                    sent[-1] = sent[-1][:e.characters_written]
                    received.append(rf.read())
                    msg = b'BLOCKED'
                    wf.write(msg)
                    sent.append(msg)

            wakati Kweli:
                jaribu:
                    wf.flush()
                    koma
                except self.BlockingIOError as e:
                    self.assertEqual(e.args[0], errno.EAGAIN)
                    self.assertEqual(e.args[2], e.characters_written)
                    self.assertEqual(e.characters_written, 0)
                    received.append(rf.read())

            received += iter(rf.read, Tupu)

        sent, received = b''.join(sent), b''.join(received)
        self.assertEqual(sent, received)
        self.assertKweli(wf.closed)
        self.assertKweli(rf.closed)

    eleza test_create_fail(self):
        # 'x' mode fails ikiwa file ni existing
        ukijumuisha self.open(support.TESTFN, 'w'):
            pass
        self.assertRaises(FileExistsError, self.open, support.TESTFN, 'x')

    eleza test_create_writes(self):
        # 'x' mode opens kila writing
        ukijumuisha self.open(support.TESTFN, 'xb') as f:
            f.write(b"spam")
        ukijumuisha self.open(support.TESTFN, 'rb') as f:
            self.assertEqual(b"spam", f.read())

    eleza test_open_allargs(self):
        # there used to be a buffer overflow kwenye the parser kila rawmode
        self.assertRaises(ValueError, self.open, support.TESTFN, 'rwax+')


kundi CMiscIOTest(MiscIOTest):
    io = io

    eleza test_readinto_buffer_overflow(self):
        # Issue #18025
        kundi BadReader(self.io.BufferedIOBase):
            eleza read(self, n=-1):
                rudisha b'x' * 10**6
        bufio = BadReader()
        b = bytearray(2)
        self.assertRaises(ValueError, bufio.readinto, b)

    eleza check_daemon_threads_shutdown_deadlock(self, stream_name):
        # Issue #23309: deadlocks at shutdown should be avoided when a
        # daemon thread na the main thread both write to a file.
        code = """ikiwa 1:
            agiza sys
            agiza time
            agiza threading
            kutoka test.support agiza SuppressCrashReport

            file = sys.{stream_name}

            eleza run():
                wakati Kweli:
                    file.write('.')
                    file.flush()

            crash = SuppressCrashReport()
            crash.__enter__()
            # don't call __exit__(): the crash occurs at Python shutdown

            thread = threading.Thread(target=run)
            thread.daemon = Kweli
            thread.start()

            time.sleep(0.5)
            file.write('!')
            file.flush()
            """.format_map(locals())
        res, _ = run_python_until_end("-c", code)
        err = res.err.decode()
        ikiwa res.rc != 0:
            # Failure: should be a fatal error
            pattern = (r"Fatal Python error: could sio acquire lock "
                       r"kila <(_io\.)?BufferedWriter name='<{stream_name}>'> "
                       r"at interpreter shutdown, possibly due to "
                       r"daemon threads".format_map(locals()))
            self.assertRegex(err, pattern)
        isipokua:
            self.assertUongo(err.strip('.!'))

    eleza test_daemon_threads_shutdown_stdout_deadlock(self):
        self.check_daemon_threads_shutdown_deadlock('stdout')

    eleza test_daemon_threads_shutdown_stderr_deadlock(self):
        self.check_daemon_threads_shutdown_deadlock('stderr')


kundi PyMiscIOTest(MiscIOTest):
    io = pyio


@unittest.skipIf(os.name == 'nt', 'POSIX signals required kila this test.')
kundi SignalsTest(unittest.TestCase):

    eleza setUp(self):
        self.oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)

    eleza tearDown(self):
        signal.signal(signal.SIGALRM, self.oldalrm)

    eleza alarm_interrupt(self, sig, frame):
        1/0

    eleza check_interrupted_write(self, item, bytes, **fdopen_kwargs):
        """Check that a partial write, when it gets interrupted, properly
        invokes the signal handler, na bubbles up the exception raised
        kwenye the latter."""
        read_results = []
        eleza _read():
            s = os.read(r, 1)
            read_results.append(s)

        t = threading.Thread(target=_read)
        t.daemon = Kweli
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Uongo
        large_data = item * (support.PIPE_MAX_SIZE // len(item) + 1)
        jaribu:
            wio = self.io.open(w, **fdopen_kwargs)
            ikiwa hasattr(signal, 'pthread_sigmask'):
                # create the thread ukijumuisha SIGALRM signal blocked
                signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGALRM])
                t.start()
                signal.pthread_sigmask(signal.SIG_UNBLOCK, [signal.SIGALRM])
            isipokua:
                t.start()

            # Fill the pipe enough that the write will be blocking.
            # It will be interrupted by the timer armed above.  Since the
            # other thread has read one byte, the low-level write will
            # rudisha ukijumuisha a successful (partial) result rather than an EINTR.
            # The buffered IO layer must check kila pending signal
            # handlers, which kwenye this case will invoke alarm_interrupt().
            signal.alarm(1)
            jaribu:
                self.assertRaises(ZeroDivisionError, wio.write, large_data)
            mwishowe:
                signal.alarm(0)
                t.join()
            # We got one byte, get another one na check that it isn't a
            # repeat of the first one.
            read_results.append(os.read(r, 1))
            self.assertEqual(read_results, [bytes[0:1], bytes[1:2]])
        mwishowe:
            os.close(w)
            os.close(r)
            # This ni deliberate. If we didn't close the file descriptor
            # before closing wio, wio would try to flush its internal
            # buffer, na block again.
            jaribu:
                wio.close()
            except OSError as e:
                ikiwa e.errno != errno.EBADF:
                    raise

    eleza test_interrupted_write_unbuffered(self):
        self.check_interrupted_write(b"xy", b"xy", mode="wb", buffering=0)

    eleza test_interrupted_write_buffered(self):
        self.check_interrupted_write(b"xy", b"xy", mode="wb")

    eleza test_interrupted_write_text(self):
        self.check_interrupted_write("xy", b"xy", mode="w", encoding="ascii")

    @support.no_tracing
    eleza check_reentrant_write(self, data, **fdopen_kwargs):
        eleza on_alarm(*args):
            # Will be called reentrantly kutoka the same thread
            wio.write(data)
            1/0
        signal.signal(signal.SIGALRM, on_alarm)
        r, w = os.pipe()
        wio = self.io.open(w, **fdopen_kwargs)
        jaribu:
            signal.alarm(1)
            # Either the reentrant call to wio.write() fails ukijumuisha RuntimeError,
            # ama the signal handler raises ZeroDivisionError.
            ukijumuisha self.assertRaises((ZeroDivisionError, RuntimeError)) as cm:
                wakati 1:
                    kila i kwenye range(100):
                        wio.write(data)
                        wio.flush()
                    # Make sure the buffer doesn't fill up na block further writes
                    os.read(r, len(data) * 100)
            exc = cm.exception
            ikiwa isinstance(exc, RuntimeError):
                self.assertKweli(str(exc).startswith("reentrant call"), str(exc))
        mwishowe:
            signal.alarm(0)
            wio.close()
            os.close(r)

    eleza test_reentrant_write_buffered(self):
        self.check_reentrant_write(b"xy", mode="wb")

    eleza test_reentrant_write_text(self):
        self.check_reentrant_write("xy", mode="w", encoding="ascii")

    eleza check_interrupted_read_retry(self, decode, **fdopen_kwargs):
        """Check that a buffered read, when it gets interrupted (either
        returning a partial result ama EINTR), properly invokes the signal
        handler na retries ikiwa the latter returned successfully."""
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Uongo
        eleza alarm_handler(sig, frame):
            os.write(w, b"bar")
        signal.signal(signal.SIGALRM, alarm_handler)
        jaribu:
            rio = self.io.open(r, **fdopen_kwargs)
            os.write(w, b"foo")
            signal.alarm(1)
            # Expected behaviour:
            # - first raw read() returns partial b"foo"
            # - second raw read() returns EINTR
            # - third raw read() returns b"bar"
            self.assertEqual(decode(rio.read(6)), "foobar")
        mwishowe:
            signal.alarm(0)
            rio.close()
            os.close(w)
            os.close(r)

    eleza test_interrupted_read_retry_buffered(self):
        self.check_interrupted_read_retry(lambda x: x.decode('latin1'),
                                          mode="rb")

    eleza test_interrupted_read_retry_text(self):
        self.check_interrupted_read_retry(lambda x: x,
                                          mode="r")

    eleza check_interrupted_write_retry(self, item, **fdopen_kwargs):
        """Check that a buffered write, when it gets interrupted (either
        returning a partial result ama EINTR), properly invokes the signal
        handler na retries ikiwa the latter returned successfully."""
        select = support.import_module("select")

        # A quantity that exceeds the buffer size of an anonymous pipe's
        # write end.
        N = support.PIPE_MAX_SIZE
        r, w = os.pipe()
        fdopen_kwargs["closefd"] = Uongo

        # We need a separate thread to read kutoka the pipe na allow the
        # write() to finish.  This thread ni started after the SIGALRM is
        # received (forcing a first EINTR kwenye write()).
        read_results = []
        write_finished = Uongo
        error = Tupu
        eleza _read():
            jaribu:
                wakati sio write_finished:
                    wakati r kwenye select.select([r], [], [], 1.0)[0]:
                        s = os.read(r, 1024)
                        read_results.append(s)
            except BaseException as exc:
                nonlocal error
                error = exc
        t = threading.Thread(target=_read)
        t.daemon = Kweli
        eleza alarm1(sig, frame):
            signal.signal(signal.SIGALRM, alarm2)
            signal.alarm(1)
        eleza alarm2(sig, frame):
            t.start()

        large_data = item * N
        signal.signal(signal.SIGALRM, alarm1)
        jaribu:
            wio = self.io.open(w, **fdopen_kwargs)
            signal.alarm(1)
            # Expected behaviour:
            # - first raw write() ni partial (because of the limited pipe buffer
            #   na the first alarm)
            # - second raw write() returns EINTR (because of the second alarm)
            # - subsequent write()s are successful (either partial ama complete)
            written = wio.write(large_data)
            self.assertEqual(N, written)

            wio.flush()
            write_finished = Kweli
            t.join()

            self.assertIsTupu(error)
            self.assertEqual(N, sum(len(x) kila x kwenye read_results))
        mwishowe:
            signal.alarm(0)
            write_finished = Kweli
            os.close(w)
            os.close(r)
            # This ni deliberate. If we didn't close the file descriptor
            # before closing wio, wio would try to flush its internal
            # buffer, na could block (in case of failure).
            jaribu:
                wio.close()
            except OSError as e:
                ikiwa e.errno != errno.EBADF:
                    raise

    eleza test_interrupted_write_retry_buffered(self):
        self.check_interrupted_write_retry(b"x", mode="wb")

    eleza test_interrupted_write_retry_text(self):
        self.check_interrupted_write_retry("x", mode="w", encoding="latin1")


kundi CSignalsTest(SignalsTest):
    io = io

kundi PySignalsTest(SignalsTest):
    io = pyio

    # Handling reentrancy issues would slow down _pyio even more, so the
    # tests are disabled.
    test_reentrant_write_buffered = Tupu
    test_reentrant_write_text = Tupu


eleza load_tests(*args):
    tests = (CIOTest, PyIOTest, APIMismatchTest,
             CBufferedReaderTest, PyBufferedReaderTest,
             CBufferedWriterTest, PyBufferedWriterTest,
             CBufferedRWPairTest, PyBufferedRWPairTest,
             CBufferedRandomTest, PyBufferedRandomTest,
             StatefulIncrementalDecoderTest,
             CIncrementalNewlineDecoderTest, PyIncrementalNewlineDecoderTest,
             CTextIOWrapperTest, PyTextIOWrapperTest,
             CMiscIOTest, PyMiscIOTest,
             CSignalsTest, PySignalsTest,
             )

    # Put the namespaces of the IO module we are testing na some useful mock
    # classes kwenye the __dict__ of each test.
    mocks = (MockRawIO, MisbehavedRawIO, MockFileIO, CloseFailureIO,
             MockNonBlockWriterIO, MockUnseekableIO, MockRawIOWithoutRead,
             SlowFlushRawIO)
    all_members = io.__all__ + ["IncrementalNewlineDecoder"]
    c_io_ns = {name : getattr(io, name) kila name kwenye all_members}
    py_io_ns = {name : getattr(pyio, name) kila name kwenye all_members}
    globs = globals()
    c_io_ns.update((x.__name__, globs["C" + x.__name__]) kila x kwenye mocks)
    py_io_ns.update((x.__name__, globs["Py" + x.__name__]) kila x kwenye mocks)
    # Avoid turning open into a bound method.
    py_io_ns["open"] = pyio.OpenWrapper
    kila test kwenye tests:
        ikiwa test.__name__.startswith("C"):
            kila name, obj kwenye c_io_ns.items():
                setattr(test, name, obj)
        elikiwa test.__name__.startswith("Py"):
            kila name, obj kwenye py_io_ns.items():
                setattr(test, name, obj)

    suite = unittest.TestSuite([unittest.makeSuite(test) kila test kwenye tests])
    rudisha suite

ikiwa __name__ == "__main__":
    unittest.main()
