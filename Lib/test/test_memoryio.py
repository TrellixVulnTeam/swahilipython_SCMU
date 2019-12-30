"""Unit tests kila memory-based file-like objects.
StringIO -- kila unicode strings
BytesIO -- kila bytes
"""

agiza unittest
kutoka test agiza support

agiza io
agiza _pyio as pyio
agiza pickle
agiza sys

kundi IntLike:
    eleza __init__(self, num):
        self._num = num
    eleza __index__(self):
        rudisha self._num
    __int__ = __index__

kundi MemorySeekTestMixin:

    eleza testInit(self):
        buf = self.buftype("1234567890")
        bytesIo = self.ioclass(buf)

    eleza testRead(self):
        buf = self.buftype("1234567890")
        bytesIo = self.ioclass(buf)

        self.assertEqual(buf[:1], bytesIo.read(1))
        self.assertEqual(buf[1:5], bytesIo.read(4))
        self.assertEqual(buf[5:], bytesIo.read(900))
        self.assertEqual(self.EOF, bytesIo.read())

    eleza testReadNoArgs(self):
        buf = self.buftype("1234567890")
        bytesIo = self.ioclass(buf)

        self.assertEqual(buf, bytesIo.read())
        self.assertEqual(self.EOF, bytesIo.read())

    eleza testSeek(self):
        buf = self.buftype("1234567890")
        bytesIo = self.ioclass(buf)

        bytesIo.read(5)
        bytesIo.seek(0)
        self.assertEqual(buf, bytesIo.read())

        bytesIo.seek(3)
        self.assertEqual(buf[3:], bytesIo.read())
        self.assertRaises(TypeError, bytesIo.seek, 0.0)

    eleza testTell(self):
        buf = self.buftype("1234567890")
        bytesIo = self.ioclass(buf)

        self.assertEqual(0, bytesIo.tell())
        bytesIo.seek(5)
        self.assertEqual(5, bytesIo.tell())
        bytesIo.seek(10000)
        self.assertEqual(10000, bytesIo.tell())


kundi MemoryTestMixin:

    eleza test_detach(self):
        buf = self.ioclass()
        self.assertRaises(self.UnsupportedOperation, buf.detach)

    eleza write_ops(self, f, t):
        self.assertEqual(f.write(t("blah.")), 5)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(t("Hello.")), 6)
        self.assertEqual(f.tell(), 6)
        self.assertEqual(f.seek(5), 5)
        self.assertEqual(f.tell(), 5)
        self.assertEqual(f.write(t(" world\n\n\n")), 9)
        self.assertEqual(f.seek(0), 0)
        self.assertEqual(f.write(t("h")), 1)
        self.assertEqual(f.truncate(12), 12)
        self.assertEqual(f.tell(), 1)

    eleza test_write(self):
        buf = self.buftype("hello world\n")
        memio = self.ioclass(buf)

        self.write_ops(memio, self.buftype)
        self.assertEqual(memio.getvalue(), buf)
        memio = self.ioclass()
        self.write_ops(memio, self.buftype)
        self.assertEqual(memio.getvalue(), buf)
        self.assertRaises(TypeError, memio.write, Tupu)
        memio.close()
        self.assertRaises(ValueError, memio.write, self.buftype(""))

    eleza test_writelines(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass()

        self.assertEqual(memio.writelines([buf] * 100), Tupu)
        self.assertEqual(memio.getvalue(), buf * 100)
        memio.writelines([])
        self.assertEqual(memio.getvalue(), buf * 100)
        memio = self.ioclass()
        self.assertRaises(TypeError, memio.writelines, [buf] + [1])
        self.assertEqual(memio.getvalue(), buf)
        self.assertRaises(TypeError, memio.writelines, Tupu)
        memio.close()
        self.assertRaises(ValueError, memio.writelines, [])

    eleza test_writelines_error(self):
        memio = self.ioclass()
        eleza error_gen():
            tuma self.buftype('spam')
             ashiria KeyboardInterrupt

        self.assertRaises(KeyboardInterrupt, memio.writelines, error_gen())

    eleza test_truncate(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertRaises(ValueError, memio.truncate, -1)
        self.assertRaises(ValueError, memio.truncate, IntLike(-1))
        memio.seek(6)
        self.assertEqual(memio.truncate(IntLike(8)), 8)
        self.assertEqual(memio.getvalue(), buf[:8])
        self.assertEqual(memio.truncate(), 6)
        self.assertEqual(memio.getvalue(), buf[:6])
        self.assertEqual(memio.truncate(4), 4)
        self.assertEqual(memio.getvalue(), buf[:4])
        self.assertEqual(memio.tell(), 6)
        memio.seek(0, 2)
        memio.write(buf)
        self.assertEqual(memio.getvalue(), buf[:4] + buf)
        pos = memio.tell()
        self.assertEqual(memio.truncate(Tupu), pos)
        self.assertEqual(memio.tell(), pos)
        self.assertRaises(TypeError, memio.truncate, '0')
        memio.close()
        self.assertRaises(ValueError, memio.truncate, 0)
        self.assertRaises(ValueError, memio.truncate, IntLike(0))

    eleza test_init(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)
        self.assertEqual(memio.getvalue(), buf)
        memio = self.ioclass(Tupu)
        self.assertEqual(memio.getvalue(), self.EOF)
        memio.__init__(buf * 2)
        self.assertEqual(memio.getvalue(), buf * 2)
        memio.__init__(buf)
        self.assertEqual(memio.getvalue(), buf)
        self.assertRaises(TypeError, memio.__init__, [])

    eleza test_read(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.read(0), self.EOF)
        self.assertEqual(memio.read(1), buf[:1])
        self.assertEqual(memio.read(4), buf[1:5])
        self.assertEqual(memio.read(900), buf[5:])
        self.assertEqual(memio.read(), self.EOF)
        memio.seek(0)
        self.assertEqual(memio.read(IntLike(0)), self.EOF)
        self.assertEqual(memio.read(IntLike(1)), buf[:1])
        self.assertEqual(memio.read(IntLike(4)), buf[1:5])
        self.assertEqual(memio.read(IntLike(900)), buf[5:])
        memio.seek(0)
        self.assertEqual(memio.read(), buf)
        self.assertEqual(memio.read(), self.EOF)
        self.assertEqual(memio.tell(), 10)
        memio.seek(0)
        self.assertEqual(memio.read(-1), buf)
        memio.seek(0)
        self.assertEqual(memio.read(IntLike(-1)), buf)
        memio.seek(0)
        self.assertEqual(type(memio.read()), type(buf))
        memio.seek(100)
        self.assertEqual(type(memio.read()), type(buf))
        memio.seek(0)
        self.assertEqual(memio.read(Tupu), buf)
        self.assertRaises(TypeError, memio.read, '')
        memio.seek(len(buf) + 1)
        self.assertEqual(memio.read(1), self.EOF)
        memio.seek(len(buf) + 1)
        self.assertEqual(memio.read(IntLike(1)), self.EOF)
        memio.seek(len(buf) + 1)
        self.assertEqual(memio.read(), self.EOF)
        memio.close()
        self.assertRaises(ValueError, memio.read)

    eleza test_readline(self):
        buf = self.buftype("1234567890\n")
        memio = self.ioclass(buf * 2)

        self.assertEqual(memio.readline(0), self.EOF)
        self.assertEqual(memio.readline(IntLike(0)), self.EOF)
        self.assertEqual(memio.readline(), buf)
        self.assertEqual(memio.readline(), buf)
        self.assertEqual(memio.readline(), self.EOF)
        memio.seek(0)
        self.assertEqual(memio.readline(5), buf[:5])
        self.assertEqual(memio.readline(5), buf[5:10])
        self.assertEqual(memio.readline(5), buf[10:15])
        memio.seek(0)
        self.assertEqual(memio.readline(IntLike(5)), buf[:5])
        self.assertEqual(memio.readline(IntLike(5)), buf[5:10])
        self.assertEqual(memio.readline(IntLike(5)), buf[10:15])
        memio.seek(0)
        self.assertEqual(memio.readline(-1), buf)
        memio.seek(0)
        self.assertEqual(memio.readline(IntLike(-1)), buf)
        memio.seek(0)
        self.assertEqual(memio.readline(0), self.EOF)
        self.assertEqual(memio.readline(IntLike(0)), self.EOF)
        # Issue #24989: Buffer overread
        memio.seek(len(buf) * 2 + 1)
        self.assertEqual(memio.readline(), self.EOF)

        buf = self.buftype("1234567890\n")
        memio = self.ioclass((buf * 3)[:-1])
        self.assertEqual(memio.readline(), buf)
        self.assertEqual(memio.readline(), buf)
        self.assertEqual(memio.readline(), buf[:-1])
        self.assertEqual(memio.readline(), self.EOF)
        memio.seek(0)
        self.assertEqual(type(memio.readline()), type(buf))
        self.assertEqual(memio.readline(), buf)
        self.assertRaises(TypeError, memio.readline, '')
        memio.close()
        self.assertRaises(ValueError,  memio.readline)

    eleza test_readlines(self):
        buf = self.buftype("1234567890\n")
        memio = self.ioclass(buf * 10)

        self.assertEqual(memio.readlines(), [buf] * 10)
        memio.seek(5)
        self.assertEqual(memio.readlines(), [buf[5:]] + [buf] * 9)
        memio.seek(0)
        self.assertEqual(memio.readlines(15), [buf] * 2)
        memio.seek(0)
        self.assertEqual(memio.readlines(-1), [buf] * 10)
        memio.seek(0)
        self.assertEqual(memio.readlines(0), [buf] * 10)
        memio.seek(0)
        self.assertEqual(type(memio.readlines()[0]), type(buf))
        memio.seek(0)
        self.assertEqual(memio.readlines(Tupu), [buf] * 10)
        self.assertRaises(TypeError, memio.readlines, '')
        # Issue #24989: Buffer overread
        memio.seek(len(buf) * 10 + 1)
        self.assertEqual(memio.readlines(), [])
        memio.close()
        self.assertRaises(ValueError, memio.readlines)

    eleza test_iterator(self):
        buf = self.buftype("1234567890\n")
        memio = self.ioclass(buf * 10)

        self.assertEqual(iter(memio), memio)
        self.assertKweli(hasattr(memio, '__iter__'))
        self.assertKweli(hasattr(memio, '__next__'))
        i = 0
        kila line kwenye memio:
            self.assertEqual(line, buf)
            i += 1
        self.assertEqual(i, 10)
        memio.seek(0)
        i = 0
        kila line kwenye memio:
            self.assertEqual(line, buf)
            i += 1
        self.assertEqual(i, 10)
        # Issue #24989: Buffer overread
        memio.seek(len(buf) * 10 + 1)
        self.assertEqual(list(memio), [])
        memio = self.ioclass(buf * 2)
        memio.close()
        self.assertRaises(ValueError, memio.__next__)

    eleza test_getvalue(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.getvalue(), buf)
        memio.read()
        self.assertEqual(memio.getvalue(), buf)
        self.assertEqual(type(memio.getvalue()), type(buf))
        memio = self.ioclass(buf * 1000)
        self.assertEqual(memio.getvalue()[-3:], self.buftype("890"))
        memio = self.ioclass(buf)
        memio.close()
        self.assertRaises(ValueError, memio.getvalue)

    eleza test_seek(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        memio.read(5)
        self.assertRaises(ValueError, memio.seek, -1)
        self.assertRaises(ValueError, memio.seek, 1, -1)
        self.assertRaises(ValueError, memio.seek, 1, 3)
        self.assertEqual(memio.seek(0), 0)
        self.assertEqual(memio.seek(0, 0), 0)
        self.assertEqual(memio.read(), buf)
        self.assertEqual(memio.seek(3), 3)
        self.assertEqual(memio.seek(0, 1), 3)
        self.assertEqual(memio.read(), buf[3:])
        self.assertEqual(memio.seek(len(buf)), len(buf))
        self.assertEqual(memio.read(), self.EOF)
        memio.seek(len(buf) + 1)
        self.assertEqual(memio.read(), self.EOF)
        self.assertEqual(memio.seek(0, 2), len(buf))
        self.assertEqual(memio.read(), self.EOF)
        memio.close()
        self.assertRaises(ValueError, memio.seek, 0)

    eleza test_overseek(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.seek(len(buf) + 1), 11)
        self.assertEqual(memio.read(), self.EOF)
        self.assertEqual(memio.tell(), 11)
        self.assertEqual(memio.getvalue(), buf)
        memio.write(self.EOF)
        self.assertEqual(memio.getvalue(), buf)
        memio.write(buf)
        self.assertEqual(memio.getvalue(), buf + self.buftype('\0') + buf)

    eleza test_tell(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.tell(), 0)
        memio.seek(5)
        self.assertEqual(memio.tell(), 5)
        memio.seek(10000)
        self.assertEqual(memio.tell(), 10000)
        memio.close()
        self.assertRaises(ValueError, memio.tell)

    eleza test_flush(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.flush(), Tupu)

    eleza test_flags(self):
        memio = self.ioclass()

        self.assertEqual(memio.writable(), Kweli)
        self.assertEqual(memio.readable(), Kweli)
        self.assertEqual(memio.seekable(), Kweli)
        self.assertEqual(memio.isatty(), Uongo)
        self.assertEqual(memio.closed, Uongo)
        memio.close()
        self.assertRaises(ValueError, memio.writable)
        self.assertRaises(ValueError, memio.readable)
        self.assertRaises(ValueError, memio.seekable)
        self.assertRaises(ValueError, memio.isatty)
        self.assertEqual(memio.closed, Kweli)

    eleza test_subclassing(self):
        buf = self.buftype("1234567890")
        eleza test1():
            kundi MemIO(self.ioclass):
                pass
            m = MemIO(buf)
            rudisha m.getvalue()
        eleza test2():
            kundi MemIO(self.ioclass):
                eleza __init__(me, a, b):
                    self.ioclass.__init__(me, a)
            m = MemIO(buf, Tupu)
            rudisha m.getvalue()
        self.assertEqual(test1(), buf)
        self.assertEqual(test2(), buf)

    eleza test_instance_dict_leak(self):
        # Test case kila issue #6242.
        # This will be caught by regrtest.py -R ikiwa this leak.
        kila _ kwenye range(100):
            memio = self.ioclass()
            memio.foo = 1

    eleza test_pickling(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)
        memio.foo = 42
        memio.seek(2)

        kundi PickleTestMemIO(self.ioclass):
            eleza __init__(me, initvalue, foo):
                self.ioclass.__init__(me, initvalue)
                me.foo = foo
            # __getnewargs__ ni undefined on purpose. This checks that PEP 307
            # ni used to provide pickling support.

        # Pickle expects the kundi to be on the module level. Here we use a
        # little hack to allow the PickleTestMemIO kundi to derive from
        # self.iokundi without having to define all combinations explicitly on
        # the module-level.
        agiza __main__
        PickleTestMemIO.__module__ = '__main__'
        PickleTestMemIO.__qualname__ = PickleTestMemIO.__name__
        __main__.PickleTestMemIO = PickleTestMemIO
        submemio = PickleTestMemIO(buf, 80)
        submemio.seek(2)

        # We only support pickle protocol 2 na onward since we use extended
        # __reduce__ API of PEP 307 to provide pickling support.
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            kila obj kwenye (memio, submemio):
                obj2 = pickle.loads(pickle.dumps(obj, protocol=proto))
                self.assertEqual(obj.getvalue(), obj2.getvalue())
                self.assertEqual(obj.__class__, obj2.__class__)
                self.assertEqual(obj.foo, obj2.foo)
                self.assertEqual(obj.tell(), obj2.tell())
                obj2.close()
                self.assertRaises(ValueError, pickle.dumps, obj2, proto)
        toa __main__.PickleTestMemIO


kundi PyBytesIOTest(MemoryTestMixin, MemorySeekTestMixin, unittest.TestCase):
    # Test _pyio.BytesIO; kundi also inherited kila testing C implementation

    UnsupportedOperation = pyio.UnsupportedOperation

    @staticmethod
    eleza buftype(s):
        rudisha s.encode("ascii")
    iokundi = pyio.BytesIO
    EOF = b""

    eleza test_getbuffer(self):
        memio = self.ioclass(b"1234567890")
        buf = memio.getbuffer()
        self.assertEqual(bytes(buf), b"1234567890")
        memio.seek(5)
        buf = memio.getbuffer()
        self.assertEqual(bytes(buf), b"1234567890")
        # Trying to change the size of the BytesIO wakati a buffer ni exported
        # raises a BufferError.
        self.assertRaises(BufferError, memio.write, b'x' * 100)
        self.assertRaises(BufferError, memio.truncate)
        self.assertRaises(BufferError, memio.close)
        self.assertUongo(memio.closed)
        # Mutating the buffer updates the BytesIO
        buf[3:6] = b"abc"
        self.assertEqual(bytes(buf), b"123abc7890")
        self.assertEqual(memio.getvalue(), b"123abc7890")
        # After the buffer gets released, we can resize na close the BytesIO
        # again
        toa buf
        support.gc_collect()
        memio.truncate()
        memio.close()
        self.assertRaises(ValueError, memio.getbuffer)

    eleza test_read1(self):
        buf = self.buftype("1234567890")
        self.assertEqual(self.ioclass(buf).read1(), buf)
        self.assertEqual(self.ioclass(buf).read1(-1), buf)

    eleza test_readinto(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        b = bytearray(b"hello")
        self.assertEqual(memio.readinto(b), 5)
        self.assertEqual(b, b"12345")
        self.assertEqual(memio.readinto(b), 5)
        self.assertEqual(b, b"67890")
        self.assertEqual(memio.readinto(b), 0)
        self.assertEqual(b, b"67890")
        b = bytearray(b"hello world")
        memio.seek(0)
        self.assertEqual(memio.readinto(b), 10)
        self.assertEqual(b, b"1234567890d")
        b = bytearray(b"")
        memio.seek(0)
        self.assertEqual(memio.readinto(b), 0)
        self.assertEqual(b, b"")
        self.assertRaises(TypeError, memio.readinto, '')
        agiza array
        a = array.array('b', b"hello world")
        memio = self.ioclass(buf)
        memio.readinto(a)
        self.assertEqual(a.tobytes(), b"1234567890d")
        memio.close()
        self.assertRaises(ValueError, memio.readinto, b)
        memio = self.ioclass(b"123")
        b = bytearray()
        memio.seek(42)
        memio.readinto(b)
        self.assertEqual(b, b"")

    eleza test_relative_seek(self):
        buf = self.buftype("1234567890")
        memio = self.ioclass(buf)

        self.assertEqual(memio.seek(-1, 1), 0)
        self.assertEqual(memio.seek(3, 1), 3)
        self.assertEqual(memio.seek(-4, 1), 0)
        self.assertEqual(memio.seek(-1, 2), 9)
        self.assertEqual(memio.seek(1, 1), 10)
        self.assertEqual(memio.seek(1, 2), 11)
        memio.seek(-3, 2)
        self.assertEqual(memio.read(), buf[-3:])
        memio.seek(0)
        memio.seek(1, 1)
        self.assertEqual(memio.read(), buf[1:])

    eleza test_unicode(self):
        memio = self.ioclass()

        self.assertRaises(TypeError, self.ioclass, "1234567890")
        self.assertRaises(TypeError, memio.write, "1234567890")
        self.assertRaises(TypeError, memio.writelines, ["1234567890"])

    eleza test_bytes_array(self):
        buf = b"1234567890"
        agiza array
        a = array.array('b', list(buf))
        memio = self.ioclass(a)
        self.assertEqual(memio.getvalue(), buf)
        self.assertEqual(memio.write(a), 10)
        self.assertEqual(memio.getvalue(), buf)

    eleza test_issue5449(self):
        buf = self.buftype("1234567890")
        self.ioclass(initial_bytes=buf)
        self.assertRaises(TypeError, self.ioclass, buf, foo=Tupu)


kundi TextIOTestMixin:

    eleza test_newlines_property(self):
        memio = self.ioclass(newline=Tupu)
        # The C StringIO decodes newlines kwenye write() calls, but the Python
        # implementation only does when reading.  This function forces them to
        # be decoded kila testing.
        eleza force_decode():
            memio.seek(0)
            memio.read()
        self.assertEqual(memio.newlines, Tupu)
        memio.write("a\n")
        force_decode()
        self.assertEqual(memio.newlines, "\n")
        memio.write("b\r\n")
        force_decode()
        self.assertEqual(memio.newlines, ("\n", "\r\n"))
        memio.write("c\rd")
        force_decode()
        self.assertEqual(memio.newlines, ("\r", "\n", "\r\n"))

    eleza test_relative_seek(self):
        memio = self.ioclass()

        self.assertRaises(OSError, memio.seek, -1, 1)
        self.assertRaises(OSError, memio.seek, 3, 1)
        self.assertRaises(OSError, memio.seek, -3, 1)
        self.assertRaises(OSError, memio.seek, -1, 2)
        self.assertRaises(OSError, memio.seek, 1, 1)
        self.assertRaises(OSError, memio.seek, 1, 2)

    eleza test_textio_properties(self):
        memio = self.ioclass()

        # These are just dummy values but we nevertheless check them kila fear
        # of unexpected komaage.
        self.assertIsTupu(memio.encoding)
        self.assertIsTupu(memio.errors)
        self.assertUongo(memio.line_buffering)

    eleza test_newline_default(self):
        memio = self.ioclass("a\nb\r\nc\rd")
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

        memio = self.ioclass()
        self.assertEqual(memio.write("a\nb\r\nc\rd"), 8)
        memio.seek(0)
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

    eleza test_newline_none(self):
        # newline=Tupu
        memio = self.ioclass("a\nb\r\nc\rd", newline=Tupu)
        self.assertEqual(list(memio), ["a\n", "b\n", "c\n", "d"])
        memio.seek(0)
        self.assertEqual(memio.read(1), "a")
        self.assertEqual(memio.read(2), "\nb")
        self.assertEqual(memio.read(2), "\nc")
        self.assertEqual(memio.read(1), "\n")
        self.assertEqual(memio.getvalue(), "a\nb\nc\nd")

        memio = self.ioclass(newline=Tupu)
        self.assertEqual(2, memio.write("a\n"))
        self.assertEqual(3, memio.write("b\r\n"))
        self.assertEqual(3, memio.write("c\rd"))
        memio.seek(0)
        self.assertEqual(memio.read(), "a\nb\nc\nd")
        self.assertEqual(memio.getvalue(), "a\nb\nc\nd")

        memio = self.ioclass("a\r\nb", newline=Tupu)
        self.assertEqual(memio.read(3), "a\nb")

    eleza test_newline_empty(self):
        # newline=""
        memio = self.ioclass("a\nb\r\nc\rd", newline="")
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\r", "d"])
        memio.seek(0)
        self.assertEqual(memio.read(4), "a\nb\r")
        self.assertEqual(memio.read(2), "\nc")
        self.assertEqual(memio.read(1), "\r")
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

        memio = self.ioclass(newline="")
        self.assertEqual(2, memio.write("a\n"))
        self.assertEqual(2, memio.write("b\r"))
        self.assertEqual(2, memio.write("\nc"))
        self.assertEqual(2, memio.write("\rd"))
        memio.seek(0)
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\r", "d"])
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

    eleza test_newline_lf(self):
        # newline="\n"
        memio = self.ioclass("a\nb\r\nc\rd", newline="\n")
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

        memio = self.ioclass(newline="\n")
        self.assertEqual(memio.write("a\nb\r\nc\rd"), 8)
        memio.seek(0)
        self.assertEqual(list(memio), ["a\n", "b\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\nb\r\nc\rd")

    eleza test_newline_cr(self):
        # newline="\r"
        memio = self.ioclass("a\nb\r\nc\rd", newline="\r")
        self.assertEqual(memio.read(), "a\rb\r\rc\rd")
        memio.seek(0)
        self.assertEqual(list(memio), ["a\r", "b\r", "\r", "c\r", "d"])
        self.assertEqual(memio.getvalue(), "a\rb\r\rc\rd")

        memio = self.ioclass(newline="\r")
        self.assertEqual(memio.write("a\nb\r\nc\rd"), 8)
        memio.seek(0)
        self.assertEqual(list(memio), ["a\r", "b\r", "\r", "c\r", "d"])
        memio.seek(0)
        self.assertEqual(memio.readlines(), ["a\r", "b\r", "\r", "c\r", "d"])
        self.assertEqual(memio.getvalue(), "a\rb\r\rc\rd")

    eleza test_newline_crlf(self):
        # newline="\r\n"
        memio = self.ioclass("a\nb\r\nc\rd", newline="\r\n")
        self.assertEqual(memio.read(), "a\r\nb\r\r\nc\rd")
        memio.seek(0)
        self.assertEqual(list(memio), ["a\r\n", "b\r\r\n", "c\rd"])
        memio.seek(0)
        self.assertEqual(memio.readlines(), ["a\r\n", "b\r\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\r\nb\r\r\nc\rd")

        memio = self.ioclass(newline="\r\n")
        self.assertEqual(memio.write("a\nb\r\nc\rd"), 8)
        memio.seek(0)
        self.assertEqual(list(memio), ["a\r\n", "b\r\r\n", "c\rd"])
        self.assertEqual(memio.getvalue(), "a\r\nb\r\r\nc\rd")

    eleza test_issue5265(self):
        # StringIO can duplicate newlines kwenye universal newlines mode
        memio = self.ioclass("a\r\nb\r\n", newline=Tupu)
        self.assertEqual(memio.read(5), "a\nb\n")
        self.assertEqual(memio.getvalue(), "a\nb\n")

    eleza test_newline_argument(self):
        self.assertRaises(TypeError, self.ioclass, newline=b"\n")
        self.assertRaises(ValueError, self.ioclass, newline="error")
        # These should sio  ashiria an error
        kila newline kwenye (Tupu, "", "\n", "\r", "\r\n"):
            self.ioclass(newline=newline)


kundi PyStringIOTest(MemoryTestMixin, MemorySeekTestMixin,
                     TextIOTestMixin, unittest.TestCase):
    buftype = str
    iokundi = pyio.StringIO
    UnsupportedOperation = pyio.UnsupportedOperation
    EOF = ""

    eleza test_lone_surrogates(self):
        # Issue #20424
        memio = self.ioclass('\ud800')
        self.assertEqual(memio.read(), '\ud800')

        memio = self.ioclass()
        memio.write('\ud800')
        self.assertEqual(memio.getvalue(), '\ud800')


kundi PyStringIOPickleTest(TextIOTestMixin, unittest.TestCase):
    """Test ikiwa pickle restores properly the internal state of StringIO.
    """
    buftype = str
    UnsupportedOperation = pyio.UnsupportedOperation
    EOF = ""

    kundi ioclass(pyio.StringIO):
        eleza __new__(cls, *args, **kwargs):
            rudisha pickle.loads(pickle.dumps(pyio.StringIO(*args, **kwargs)))
        eleza __init__(self, *args, **kwargs):
            pass


kundi CBytesIOTest(PyBytesIOTest):
    iokundi = io.BytesIO
    UnsupportedOperation = io.UnsupportedOperation

    eleza test_getstate(self):
        memio = self.ioclass()
        state = memio.__getstate__()
        self.assertEqual(len(state), 3)
        bytearray(state[0]) # Check ikiwa state[0] supports the buffer interface.
        self.assertIsInstance(state[1], int)
        ikiwa state[2] ni sio Tupu:
            self.assertIsInstance(state[2], dict)
        memio.close()
        self.assertRaises(ValueError, memio.__getstate__)

    eleza test_setstate(self):
        # This checks whether __setstate__ does proper input validation.
        memio = self.ioclass()
        memio.__setstate__((b"no error", 0, Tupu))
        memio.__setstate__((bytearray(b"no error"), 0, Tupu))
        memio.__setstate__((b"no error", 0, {'spam': 3}))
        self.assertRaises(ValueError, memio.__setstate__, (b"", -1, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, ("unicode", 0, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, (b"", 0.0, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, (b"", 0, 0))
        self.assertRaises(TypeError, memio.__setstate__, (b"len-test", 0))
        self.assertRaises(TypeError, memio.__setstate__)
        self.assertRaises(TypeError, memio.__setstate__, 0)
        memio.close()
        self.assertRaises(ValueError, memio.__setstate__, (b"closed", 0, Tupu))

    check_sizeof = support.check_sizeof

    @support.cpython_only
    eleza test_sizeof(self):
        basesize = support.calcobjsize('P2n2Pn')
        check = self.check_sizeof
        self.assertEqual(object.__sizeof__(io.BytesIO()), basesize)
        check(io.BytesIO(), basesize )
        n = 1000  # use a variable to prevent constant folding
        check(io.BytesIO(b'a' * n), basesize + sys.getsizeof(b'a' * n))

    # Various tests of copy-on-write behaviour kila BytesIO.

    eleza _test_cow_mutation(self, mutation):
        # Common code kila all BytesIO copy-on-write mutation tests.
        imm = b' ' * 1024
        old_rc = sys.getrefcount(imm)
        memio = self.ioclass(imm)
        self.assertEqual(sys.getrefcount(imm), old_rc + 1)
        mutation(memio)
        self.assertEqual(sys.getrefcount(imm), old_rc)

    @support.cpython_only
    eleza test_cow_truncate(self):
        # Ensure truncate causes a copy.
        eleza mutation(memio):
            memio.truncate(1)
        self._test_cow_mutation(mutation)

    @support.cpython_only
    eleza test_cow_write(self):
        # Ensure write that would sio cause a resize still results kwenye a copy.
        eleza mutation(memio):
            memio.seek(0)
            memio.write(b'foo')
        self._test_cow_mutation(mutation)

    @support.cpython_only
    eleza test_cow_setstate(self):
        # __setstate__ should cause buffer to be released.
        memio = self.ioclass(b'foooooo')
        state = memio.__getstate__()
        eleza mutation(memio):
            memio.__setstate__(state)
        self._test_cow_mutation(mutation)

    @support.cpython_only
    eleza test_cow_mutable(self):
        # BytesIO should accept only Bytes kila copy-on-write sharing, since
        # arbitrary buffer-exporting objects like bytearray() aren't guaranteed
        # to be immutable.
        ba = bytearray(1024)
        old_rc = sys.getrefcount(ba)
        memio = self.ioclass(ba)
        self.assertEqual(sys.getrefcount(ba), old_rc)

kundi CStringIOTest(PyStringIOTest):
    iokundi = io.StringIO
    UnsupportedOperation = io.UnsupportedOperation

    # XXX: For the Python version of io.StringIO, this ni highly
    # dependent on the encoding used kila the underlying buffer.
    eleza test_widechar(self):
        buf = self.buftype("\U0002030a\U00020347")
        memio = self.ioclass(buf)

        self.assertEqual(memio.getvalue(), buf)
        self.assertEqual(memio.write(buf), len(buf))
        self.assertEqual(memio.tell(), len(buf))
        self.assertEqual(memio.getvalue(), buf)
        self.assertEqual(memio.write(buf), len(buf))
        self.assertEqual(memio.tell(), len(buf) * 2)
        self.assertEqual(memio.getvalue(), buf + buf)

    eleza test_getstate(self):
        memio = self.ioclass()
        state = memio.__getstate__()
        self.assertEqual(len(state), 4)
        self.assertIsInstance(state[0], str)
        self.assertIsInstance(state[1], str)
        self.assertIsInstance(state[2], int)
        ikiwa state[3] ni sio Tupu:
            self.assertIsInstance(state[3], dict)
        memio.close()
        self.assertRaises(ValueError, memio.__getstate__)

    eleza test_setstate(self):
        # This checks whether __setstate__ does proper input validation.
        memio = self.ioclass()
        memio.__setstate__(("no error", "\n", 0, Tupu))
        memio.__setstate__(("no error", "", 0, {'spam': 3}))
        self.assertRaises(ValueError, memio.__setstate__, ("", "f", 0, Tupu))
        self.assertRaises(ValueError, memio.__setstate__, ("", "", -1, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, (b"", "", 0, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, ("", b"", 0, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, ("", "", 0.0, Tupu))
        self.assertRaises(TypeError, memio.__setstate__, ("", "", 0, 0))
        self.assertRaises(TypeError, memio.__setstate__, ("len-test", 0))
        self.assertRaises(TypeError, memio.__setstate__)
        self.assertRaises(TypeError, memio.__setstate__, 0)
        memio.close()
        self.assertRaises(ValueError, memio.__setstate__, ("closed", "", 0, Tupu))


kundi CStringIOPickleTest(PyStringIOPickleTest):
    UnsupportedOperation = io.UnsupportedOperation

    kundi ioclass(io.StringIO):
        eleza __new__(cls, *args, **kwargs):
            rudisha pickle.loads(pickle.dumps(io.StringIO(*args, **kwargs)))
        eleza __init__(self, *args, **kwargs):
            pass


ikiwa __name__ == '__main__':
    unittest.main()
