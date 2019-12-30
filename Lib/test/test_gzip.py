"""Test script kila the gzip module.
"""

agiza array
agiza functools
agiza io
agiza os
agiza pathlib
agiza struct
agiza sys
agiza unittest
kutoka subprocess agiza PIPE, Popen
kutoka test agiza support
kutoka test.support agiza _4G, bigmemtest
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure

gzip = support.import_module('gzip')

data1 = b"""  int length=DEFAULTALLOC, err = Z_OK;
  PyObject *RetVal;
  int flushmode = Z_FINISH;
  unsigned long start_total_out;

"""

data2 = b"""/* zlibmodule.c -- gzip-compatible data compression */
/* See http://www.gzip.org/zlib/
/* See http://www.winimage.com/zLibDll kila Windows */
"""


TEMPDIR = os.path.abspath(support.TESTFN) + '-gzdir'


kundi UnseekableIO(io.BytesIO):
    eleza seekable(self):
        rudisha Uongo

    eleza tell(self):
         ashiria io.UnsupportedOperation

    eleza seek(self, *args):
         ashiria io.UnsupportedOperation


kundi BaseTest(unittest.TestCase):
    filename = support.TESTFN

    eleza setUp(self):
        support.unlink(self.filename)

    eleza tearDown(self):
        support.unlink(self.filename)


kundi TestGzip(BaseTest):
    eleza write_and_read_back(self, data, mode='b'):
        b_data = bytes(data)
        ukijumuisha gzip.GzipFile(self.filename, 'w'+mode) as f:
            l = f.write(data)
        self.assertEqual(l, len(b_data))
        ukijumuisha gzip.GzipFile(self.filename, 'r'+mode) as f:
            self.assertEqual(f.read(), b_data)

    eleza test_write(self):
        ukijumuisha gzip.GzipFile(self.filename, 'wb') as f:
            f.write(data1 * 50)

            # Try flush na fileno.
            f.flush()
            f.fileno()
            ikiwa hasattr(os, 'fsync'):
                os.fsync(f.fileno())
            f.close()

        # Test multiple close() calls.
        f.close()

    eleza test_write_read_with_pathlike_file(self):
        filename = pathlib.Path(self.filename)
        ukijumuisha gzip.GzipFile(filename, 'w') as f:
            f.write(data1 * 50)
        self.assertIsInstance(f.name, str)
        ukijumuisha gzip.GzipFile(filename, 'a') as f:
            f.write(data1)
        ukijumuisha gzip.GzipFile(filename) as f:
            d = f.read()
        self.assertEqual(d, data1 * 51)
        self.assertIsInstance(f.name, str)

    # The following test_write_xy methods test that write accepts
    # the corresponding bytes-like object type as input
    # na that the data written equals bytes(xy) kwenye all cases.
    eleza test_write_memoryview(self):
        self.write_and_read_back(memoryview(data1 * 50))
        m = memoryview(bytes(range(256)))
        data = m.cast('B', shape=[8,8,4])
        self.write_and_read_back(data)

    eleza test_write_bytearray(self):
        self.write_and_read_back(bytearray(data1 * 50))

    eleza test_write_array(self):
        self.write_and_read_back(array.array('I', data1 * 40))

    eleza test_write_incompatible_type(self):
        # Test that non-bytes-like types  ashiria TypeError.
        # Issue #21560: attempts to write incompatible types
        # should sio affect the state of the fileobject
        ukijumuisha gzip.GzipFile(self.filename, 'wb') as f:
            ukijumuisha self.assertRaises(TypeError):
                f.write('')
            ukijumuisha self.assertRaises(TypeError):
                f.write([])
            f.write(data1)
        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            self.assertEqual(f.read(), data1)

    eleza test_read(self):
        self.test_write()
        # Try reading.
        ukijumuisha gzip.GzipFile(self.filename, 'r') as f:
            d = f.read()
        self.assertEqual(d, data1*50)

    eleza test_read1(self):
        self.test_write()
        blocks = []
        nread = 0
        ukijumuisha gzip.GzipFile(self.filename, 'r') as f:
            wakati Kweli:
                d = f.read1()
                ikiwa sio d:
                    koma
                blocks.append(d)
                nread += len(d)
                # Check that position was updated correctly (see issue10791).
                self.assertEqual(f.tell(), nread)
        self.assertEqual(b''.join(blocks), data1 * 50)

    @bigmemtest(size=_4G, memuse=1)
    eleza test_read_large(self, size):
        # Read chunk size over UINT_MAX should be supported, despite zlib's
        # limitation per low-level call
        compressed = gzip.compress(data1, compresslevel=1)
        f = gzip.GzipFile(fileobj=io.BytesIO(compressed), mode='rb')
        self.assertEqual(f.read(size), data1)

    eleza test_io_on_closed_object(self):
        # Test that I/O operations on closed GzipFile objects  ashiria a
        # ValueError, just like the corresponding functions on file objects.

        # Write to a file, open it kila reading, then close it.
        self.test_write()
        f = gzip.GzipFile(self.filename, 'r')
        fileobj = f.fileobj
        self.assertUongo(fileobj.closed)
        f.close()
        self.assertKweli(fileobj.closed)
        ukijumuisha self.assertRaises(ValueError):
            f.read(1)
        ukijumuisha self.assertRaises(ValueError):
            f.seek(0)
        ukijumuisha self.assertRaises(ValueError):
            f.tell()
        # Open the file kila writing, then close it.
        f = gzip.GzipFile(self.filename, 'w')
        fileobj = f.fileobj
        self.assertUongo(fileobj.closed)
        f.close()
        self.assertKweli(fileobj.closed)
        ukijumuisha self.assertRaises(ValueError):
            f.write(b'')
        ukijumuisha self.assertRaises(ValueError):
            f.flush()

    eleza test_append(self):
        self.test_write()
        # Append to the previous file
        ukijumuisha gzip.GzipFile(self.filename, 'ab') as f:
            f.write(data2 * 15)

        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            d = f.read()
        self.assertEqual(d, (data1*50) + (data2*15))

    eleza test_many_append(self):
        # Bug #1074261 was triggered when reading a file that contained
        # many, many members.  Create such a file na verify that reading it
        # works.
        ukijumuisha gzip.GzipFile(self.filename, 'wb', 9) as f:
            f.write(b'a')
        kila i kwenye range(0, 200):
            ukijumuisha gzip.GzipFile(self.filename, "ab", 9) as f: # append
                f.write(b'a')

        # Try reading the file
        ukijumuisha gzip.GzipFile(self.filename, "rb") as zgfile:
            contents = b""
            wakati 1:
                ztxt = zgfile.read(8192)
                contents += ztxt
                ikiwa sio ztxt: koma
        self.assertEqual(contents, b'a'*201)

    eleza test_exclusive_write(self):
        ukijumuisha gzip.GzipFile(self.filename, 'xb') as f:
            f.write(data1 * 50)
        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            self.assertEqual(f.read(), data1 * 50)
        ukijumuisha self.assertRaises(FileExistsError):
            gzip.GzipFile(self.filename, 'xb')

    eleza test_buffered_reader(self):
        # Issue #7471: a GzipFile can be wrapped kwenye a BufferedReader for
        # performance.
        self.test_write()

        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            ukijumuisha io.BufferedReader(f) as r:
                lines = [line kila line kwenye r]

        self.assertEqual(lines, 50 * data1.splitlines(keepends=Kweli))

    eleza test_readline(self):
        self.test_write()
        # Try .readline() ukijumuisha varying line lengths

        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            line_length = 0
            wakati 1:
                L = f.readline(line_length)
                ikiwa sio L na line_length != 0: koma
                self.assertKweli(len(L) <= line_length)
                line_length = (line_length + 1) % 50

    eleza test_readlines(self):
        self.test_write()
        # Try .readlines()

        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            L = f.readlines()

        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            wakati 1:
                L = f.readlines(150)
                ikiwa L == []: koma

    eleza test_seek_read(self):
        self.test_write()
        # Try seek, read test

        ukijumuisha gzip.GzipFile(self.filename) as f:
            wakati 1:
                oldpos = f.tell()
                line1 = f.readline()
                ikiwa sio line1: koma
                newpos = f.tell()
                f.seek(oldpos)  # negative seek
                ikiwa len(line1)>10:
                    amount = 10
                isipokua:
                    amount = len(line1)
                line2 = f.read(amount)
                self.assertEqual(line1[:amount], line2)
                f.seek(newpos)  # positive seek

    eleza test_seek_whence(self):
        self.test_write()
        # Try seek(whence=1), read test

        ukijumuisha gzip.GzipFile(self.filename) as f:
            f.read(10)
            f.seek(10, whence=1)
            y = f.read(10)
        self.assertEqual(y, data1[20:30])

    eleza test_seek_write(self):
        # Try seek, write test
        ukijumuisha gzip.GzipFile(self.filename, 'w') as f:
            kila pos kwenye range(0, 256, 16):
                f.seek(pos)
                f.write(b'GZ\n')

    eleza test_mode(self):
        self.test_write()
        ukijumuisha gzip.GzipFile(self.filename, 'r') as f:
            self.assertEqual(f.myfileobj.mode, 'rb')
        support.unlink(self.filename)
        ukijumuisha gzip.GzipFile(self.filename, 'x') as f:
            self.assertEqual(f.myfileobj.mode, 'xb')

    eleza test_1647484(self):
        kila mode kwenye ('wb', 'rb'):
            ukijumuisha gzip.GzipFile(self.filename, mode) as f:
                self.assertKweli(hasattr(f, "name"))
                self.assertEqual(f.name, self.filename)

    eleza test_paddedfile_getattr(self):
        self.test_write()
        ukijumuisha gzip.GzipFile(self.filename, 'rb') as f:
            self.assertKweli(hasattr(f.fileobj, "name"))
            self.assertEqual(f.fileobj.name, self.filename)

    eleza test_mtime(self):
        mtime = 123456789
        ukijumuisha gzip.GzipFile(self.filename, 'w', mtime = mtime) as fWrite:
            fWrite.write(data1)
        ukijumuisha gzip.GzipFile(self.filename) as fRead:
            self.assertKweli(hasattr(fRead, 'mtime'))
            self.assertIsTupu(fRead.mtime)
            dataRead = fRead.read()
            self.assertEqual(dataRead, data1)
            self.assertEqual(fRead.mtime, mtime)

    eleza test_metadata(self):
        mtime = 123456789

        ukijumuisha gzip.GzipFile(self.filename, 'w', mtime = mtime) as fWrite:
            fWrite.write(data1)

        ukijumuisha open(self.filename, 'rb') as fRead:
            # see RFC 1952: http://www.faqs.org/rfcs/rfc1952.html

            idBytes = fRead.read(2)
            self.assertEqual(idBytes, b'\x1f\x8b') # gzip ID

            cmByte = fRead.read(1)
            self.assertEqual(cmByte, b'\x08') # deflate

            flagsByte = fRead.read(1)
            self.assertEqual(flagsByte, b'\x08') # only the FNAME flag ni set

            mtimeBytes = fRead.read(4)
            self.assertEqual(mtimeBytes, struct.pack('<i', mtime)) # little-endian

            xflByte = fRead.read(1)
            self.assertEqual(xflByte, b'\x02') # maximum compression

            osByte = fRead.read(1)
            self.assertEqual(osByte, b'\xff') # OS "unknown" (OS-independent)

            # Since the FNAME flag ni set, the zero-terminated filename follows.
            # RFC 1952 specifies that this ni the name of the input file, ikiwa any.
            # However, the gzip module defaults to storing the name of the output
            # file kwenye this field.
            expected = self.filename.encode('Latin-1') + b'\x00'
            nameBytes = fRead.read(len(expected))
            self.assertEqual(nameBytes, expected)

            # Since no other flags were set, the header ends here.
            # Rather than process the compressed data, let's seek to the trailer.
            fRead.seek(os.stat(self.filename).st_size - 8)

            crc32Bytes = fRead.read(4) # CRC32 of uncompressed data [data1]
            self.assertEqual(crc32Bytes, b'\xaf\xd7d\x83')

            isizeBytes = fRead.read(4)
            self.assertEqual(isizeBytes, struct.pack('<i', len(data1)))

    eleza test_with_open(self):
        # GzipFile supports the context management protocol
        ukijumuisha gzip.GzipFile(self.filename, "wb") as f:
            f.write(b"xxx")
        f = gzip.GzipFile(self.filename, "rb")
        f.close()
        jaribu:
            ukijumuisha f:
                pass
        except ValueError:
            pass
        isipokua:
            self.fail("__enter__ on a closed file didn't  ashiria an exception")
        jaribu:
            ukijumuisha gzip.GzipFile(self.filename, "wb") as f:
                1/0
        except ZeroDivisionError:
            pass
        isipokua:
            self.fail("1/0 didn't  ashiria an exception")

    eleza test_zero_padded_file(self):
        ukijumuisha gzip.GzipFile(self.filename, "wb") as f:
            f.write(data1 * 50)

        # Pad the file ukijumuisha zeroes
        ukijumuisha open(self.filename, "ab") as f:
            f.write(b"\x00" * 50)

        ukijumuisha gzip.GzipFile(self.filename, "rb") as f:
            d = f.read()
            self.assertEqual(d, data1 * 50, "Incorrect data kwenye file")

    eleza test_gzip_BadGzipFile_exception(self):
        self.assertKweli(issubclass(gzip.BadGzipFile, OSError))

    eleza test_bad_gzip_file(self):
        ukijumuisha open(self.filename, 'wb') as file:
            file.write(data1 * 50)
        ukijumuisha gzip.GzipFile(self.filename, 'r') as file:
            self.assertRaises(gzip.BadGzipFile, file.readlines)

    eleza test_non_seekable_file(self):
        uncompressed = data1 * 50
        buf = UnseekableIO()
        ukijumuisha gzip.GzipFile(fileobj=buf, mode="wb") as f:
            f.write(uncompressed)
        compressed = buf.getvalue()
        buf = UnseekableIO(compressed)
        ukijumuisha gzip.GzipFile(fileobj=buf, mode="rb") as f:
            self.assertEqual(f.read(), uncompressed)

    eleza test_peek(self):
        uncompressed = data1 * 200
        ukijumuisha gzip.GzipFile(self.filename, "wb") as f:
            f.write(uncompressed)

        eleza sizes():
            wakati Kweli:
                kila n kwenye range(5, 50, 10):
                    tuma n

        ukijumuisha gzip.GzipFile(self.filename, "rb") as f:
            f.max_read_chunk = 33
            nread = 0
            kila n kwenye sizes():
                s = f.peek(n)
                ikiwa s == b'':
                    koma
                self.assertEqual(f.read(len(s)), s)
                nread += len(s)
            self.assertEqual(f.read(100), b'')
            self.assertEqual(nread, len(uncompressed))

    eleza test_textio_readlines(self):
        # Issue #10791: TextIOWrapper.readlines() fails when wrapping GzipFile.
        lines = (data1 * 50).decode("ascii").splitlines(keepends=Kweli)
        self.test_write()
        ukijumuisha gzip.GzipFile(self.filename, 'r') as f:
            ukijumuisha io.TextIOWrapper(f, encoding="ascii") as t:
                self.assertEqual(t.readlines(), lines)

    eleza test_fileobj_from_fdopen(self):
        # Issue #13781: Opening a GzipFile kila writing fails when using a
        # fileobj created ukijumuisha os.fdopen().
        fd = os.open(self.filename, os.O_WRONLY | os.O_CREAT)
        ukijumuisha os.fdopen(fd, "wb") as f:
            ukijumuisha gzip.GzipFile(fileobj=f, mode="w") as g:
                pass

    eleza test_fileobj_mode(self):
        gzip.GzipFile(self.filename, "wb").close()
        ukijumuisha open(self.filename, "r+b") as f:
            ukijumuisha gzip.GzipFile(fileobj=f, mode='r') as g:
                self.assertEqual(g.mode, gzip.READ)
            ukijumuisha gzip.GzipFile(fileobj=f, mode='w') as g:
                self.assertEqual(g.mode, gzip.WRITE)
            ukijumuisha gzip.GzipFile(fileobj=f, mode='a') as g:
                self.assertEqual(g.mode, gzip.WRITE)
            ukijumuisha gzip.GzipFile(fileobj=f, mode='x') as g:
                self.assertEqual(g.mode, gzip.WRITE)
            ukijumuisha self.assertRaises(ValueError):
                gzip.GzipFile(fileobj=f, mode='z')
        kila mode kwenye "rb", "r+b":
            ukijumuisha open(self.filename, mode) as f:
                ukijumuisha gzip.GzipFile(fileobj=f) as g:
                    self.assertEqual(g.mode, gzip.READ)
        kila mode kwenye "wb", "ab", "xb":
            ikiwa "x" kwenye mode:
                support.unlink(self.filename)
            ukijumuisha open(self.filename, mode) as f:
                ukijumuisha gzip.GzipFile(fileobj=f) as g:
                    self.assertEqual(g.mode, gzip.WRITE)

    eleza test_bytes_filename(self):
        str_filename = self.filename
        jaribu:
            bytes_filename = str_filename.encode("ascii")
        except UnicodeEncodeError:
            self.skipTest("Temporary file name needs to be ASCII")
        ukijumuisha gzip.GzipFile(bytes_filename, "wb") as f:
            f.write(data1 * 50)
        ukijumuisha gzip.GzipFile(bytes_filename, "rb") as f:
            self.assertEqual(f.read(), data1 * 50)
        # Sanity check that we are actually operating on the right file.
        ukijumuisha gzip.GzipFile(str_filename, "rb") as f:
            self.assertEqual(f.read(), data1 * 50)

    eleza test_decompress_limited(self):
        """Decompressed data buffering should be limited"""
        bomb = gzip.compress(b'\0' * int(2e6), compresslevel=9)
        self.assertLess(len(bomb), io.DEFAULT_BUFFER_SIZE)

        bomb = io.BytesIO(bomb)
        decomp = gzip.GzipFile(fileobj=bomb)
        self.assertEqual(decomp.read(1), b'\0')
        max_decomp = 1 + io.DEFAULT_BUFFER_SIZE
        self.assertLessEqual(decomp._buffer.raw.tell(), max_decomp,
            "Excessive amount of data was decompressed")

    # Testing compress/decompress shortcut functions

    eleza test_compress(self):
        kila data kwenye [data1, data2]:
            kila args kwenye [(), (1,), (6,), (9,)]:
                datac = gzip.compress(data, *args)
                self.assertEqual(type(datac), bytes)
                ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(datac), mode="rb") as f:
                    self.assertEqual(f.read(), data)

    eleza test_compress_mtime(self):
        mtime = 123456789
        kila data kwenye [data1, data2]:
            kila args kwenye [(), (1,), (6,), (9,)]:
                ukijumuisha self.subTest(data=data, args=args):
                    datac = gzip.compress(data, *args, mtime=mtime)
                    self.assertEqual(type(datac), bytes)
                    ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(datac), mode="rb") as f:
                        f.read(1) # to set mtime attribute
                        self.assertEqual(f.mtime, mtime)

    eleza test_decompress(self):
        kila data kwenye (data1, data2):
            buf = io.BytesIO()
            ukijumuisha gzip.GzipFile(fileobj=buf, mode="wb") as f:
                f.write(data)
            self.assertEqual(gzip.decompress(buf.getvalue()), data)
            # Roundtrip ukijumuisha compress
            datac = gzip.compress(data)
            self.assertEqual(gzip.decompress(datac), data)

    eleza test_read_truncated(self):
        data = data1*50
        # Drop the CRC (4 bytes) na file size (4 bytes).
        truncated = gzip.compress(data)[:-8]
        ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(truncated)) as f:
            self.assertRaises(EOFError, f.read)
        ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(truncated)) as f:
            self.assertEqual(f.read(len(data)), data)
            self.assertRaises(EOFError, f.read, 1)
        # Incomplete 10-byte header.
        kila i kwenye range(2, 10):
            ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(truncated[:i])) as f:
                self.assertRaises(EOFError, f.read, 1)

    eleza test_read_with_extra(self):
        # Gzip data ukijumuisha an extra field
        gzdata = (b'\x1f\x8b\x08\x04\xb2\x17cQ\x02\xff'
                  b'\x05\x00Extra'
                  b'\x0bI-.\x01\x002\xd1Mx\x04\x00\x00\x00')
        ukijumuisha gzip.GzipFile(fileobj=io.BytesIO(gzdata)) as f:
            self.assertEqual(f.read(), b'Test')

    eleza test_prepend_error(self):
        # See issue #20875
        ukijumuisha gzip.open(self.filename, "wb") as f:
            f.write(data1)
        ukijumuisha gzip.open(self.filename, "rb") as f:
            f._buffer.raw._fp.prepend()

kundi TestOpen(BaseTest):
    eleza test_binary_modes(self):
        uncompressed = data1 * 50

        ukijumuisha gzip.open(self.filename, "wb") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

        ukijumuisha gzip.open(self.filename, "rb") as f:
            self.assertEqual(f.read(), uncompressed)

        ukijumuisha gzip.open(self.filename, "ab") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed * 2)

        ukijumuisha self.assertRaises(FileExistsError):
            gzip.open(self.filename, "xb")
        support.unlink(self.filename)
        ukijumuisha gzip.open(self.filename, "xb") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

    eleza test_pathlike_file(self):
        filename = pathlib.Path(self.filename)
        ukijumuisha gzip.open(filename, "wb") as f:
            f.write(data1 * 50)
        ukijumuisha gzip.open(filename, "ab") as f:
            f.write(data1)
        ukijumuisha gzip.open(filename) as f:
            self.assertEqual(f.read(), data1 * 51)

    eleza test_implicit_binary_modes(self):
        # Test implicit binary modes (no "b" ama "t" kwenye mode string).
        uncompressed = data1 * 50

        ukijumuisha gzip.open(self.filename, "w") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

        ukijumuisha gzip.open(self.filename, "r") as f:
            self.assertEqual(f.read(), uncompressed)

        ukijumuisha gzip.open(self.filename, "a") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed * 2)

        ukijumuisha self.assertRaises(FileExistsError):
            gzip.open(self.filename, "x")
        support.unlink(self.filename)
        ukijumuisha gzip.open(self.filename, "x") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read())
            self.assertEqual(file_data, uncompressed)

    eleza test_text_modes(self):
        uncompressed = data1.decode("ascii") * 50
        uncompressed_raw = uncompressed.replace("\n", os.linesep)
        ukijumuisha gzip.open(self.filename, "wt") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read()).decode("ascii")
            self.assertEqual(file_data, uncompressed_raw)
        ukijumuisha gzip.open(self.filename, "rt") as f:
            self.assertEqual(f.read(), uncompressed)
        ukijumuisha gzip.open(self.filename, "at") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read()).decode("ascii")
            self.assertEqual(file_data, uncompressed_raw * 2)

    eleza test_fileobj(self):
        uncompressed_bytes = data1 * 50
        uncompressed_str = uncompressed_bytes.decode("ascii")
        compressed = gzip.compress(uncompressed_bytes)
        ukijumuisha gzip.open(io.BytesIO(compressed), "r") as f:
            self.assertEqual(f.read(), uncompressed_bytes)
        ukijumuisha gzip.open(io.BytesIO(compressed), "rb") as f:
            self.assertEqual(f.read(), uncompressed_bytes)
        ukijumuisha gzip.open(io.BytesIO(compressed), "rt") as f:
            self.assertEqual(f.read(), uncompressed_str)

    eleza test_bad_params(self):
        # Test invalid parameter combinations.
        ukijumuisha self.assertRaises(TypeError):
            gzip.open(123.456)
        ukijumuisha self.assertRaises(ValueError):
            gzip.open(self.filename, "wbt")
        ukijumuisha self.assertRaises(ValueError):
            gzip.open(self.filename, "xbt")
        ukijumuisha self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", encoding="utf-8")
        ukijumuisha self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", errors="ignore")
        ukijumuisha self.assertRaises(ValueError):
            gzip.open(self.filename, "rb", newline="\n")

    eleza test_encoding(self):
        # Test non-default encoding.
        uncompressed = data1.decode("ascii") * 50
        uncompressed_raw = uncompressed.replace("\n", os.linesep)
        ukijumuisha gzip.open(self.filename, "wt", encoding="utf-16") as f:
            f.write(uncompressed)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = gzip.decompress(f.read()).decode("utf-16")
            self.assertEqual(file_data, uncompressed_raw)
        ukijumuisha gzip.open(self.filename, "rt", encoding="utf-16") as f:
            self.assertEqual(f.read(), uncompressed)

    eleza test_encoding_error_handler(self):
        # Test ukijumuisha non-default encoding error handler.
        ukijumuisha gzip.open(self.filename, "wb") as f:
            f.write(b"foo\xffbar")
        ukijumuisha gzip.open(self.filename, "rt", encoding="ascii", errors="ignore") \
                as f:
            self.assertEqual(f.read(), "foobar")

    eleza test_newline(self):
        # Test ukijumuisha explicit newline (universal newline mode disabled).
        uncompressed = data1.decode("ascii") * 50
        ukijumuisha gzip.open(self.filename, "wt", newline="\n") as f:
            f.write(uncompressed)
        ukijumuisha gzip.open(self.filename, "rt", newline="\r") as f:
            self.assertEqual(f.readlines(), [uncompressed])


eleza create_and_remove_directory(directory):
    eleza decorator(function):
        @functools.wraps(function)
        eleza wrapper(*args, **kwargs):
            os.makedirs(directory)
            jaribu:
                rudisha function(*args, **kwargs)
            mwishowe:
                support.rmtree(directory)
        rudisha wrapper
    rudisha decorator


kundi TestCommandLine(unittest.TestCase):
    data = b'This ni a simple test ukijumuisha gzip'

    eleza test_decompress_stdin_stdout(self):
        ukijumuisha io.BytesIO() as bytes_io:
            ukijumuisha gzip.GzipFile(fileobj=bytes_io, mode='wb') as gzip_file:
                gzip_file.write(self.data)

            args = sys.executable, '-m', 'gzip', '-d'
            ukijumuisha Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                out, err = proc.communicate(bytes_io.getvalue())

        self.assertEqual(err, b'')
        self.assertEqual(out, self.data)

    @create_and_remove_directory(TEMPDIR)
    eleza test_decompress_infile_outfile(self):
        gzipname = os.path.join(TEMPDIR, 'testgzip.gz')
        self.assertUongo(os.path.exists(gzipname))

        ukijumuisha gzip.open(gzipname, mode='wb') as fp:
            fp.write(self.data)
        rc, out, err = assert_python_ok('-m', 'gzip', '-d', gzipname)

        ukijumuisha open(os.path.join(TEMPDIR, "testgzip"), "rb") as gunziped:
            self.assertEqual(gunziped.read(), self.data)

        self.assertKweli(os.path.exists(gzipname))
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    eleza test_decompress_infile_outfile_error(self):
        rc, out, err = assert_python_ok('-m', 'gzip', '-d', 'thisisatest.out')
        self.assertIn(b"filename doesn't end kwenye .gz:", out)
        self.assertEqual(rc, 0)
        self.assertEqual(err, b'')

    @create_and_remove_directory(TEMPDIR)
    eleza test_compress_stdin_outfile(self):
        args = sys.executable, '-m', 'gzip'
        ukijumuisha Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            out, err = proc.communicate(self.data)

        self.assertEqual(err, b'')
        self.assertEqual(out[:2], b"\x1f\x8b")

    @create_and_remove_directory(TEMPDIR)
    eleza test_compress_infile_outfile_default(self):
        local_testgzip = os.path.join(TEMPDIR, 'testgzip')
        gzipname = local_testgzip + '.gz'
        self.assertUongo(os.path.exists(gzipname))

        ukijumuisha open(local_testgzip, 'wb') as fp:
            fp.write(self.data)

        rc, out, err = assert_python_ok('-m', 'gzip', local_testgzip)

        self.assertKweli(os.path.exists(gzipname))
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    @create_and_remove_directory(TEMPDIR)
    eleza test_compress_infile_outfile(self):
        kila compress_level kwenye ('--fast', '--best'):
            ukijumuisha self.subTest(compress_level=compress_level):
                local_testgzip = os.path.join(TEMPDIR, 'testgzip')
                gzipname = local_testgzip + '.gz'
                self.assertUongo(os.path.exists(gzipname))

                ukijumuisha open(local_testgzip, 'wb') as fp:
                    fp.write(self.data)

                rc, out, err = assert_python_ok('-m', 'gzip', compress_level, local_testgzip)

                self.assertKweli(os.path.exists(gzipname))
                self.assertEqual(out, b'')
                self.assertEqual(err, b'')
                os.remove(gzipname)
                self.assertUongo(os.path.exists(gzipname))

    eleza test_compress_fast_best_are_exclusive(self):
        rc, out, err = assert_python_failure('-m', 'gzip', '--fast', '--best')
        self.assertIn(b"error: argument --best: sio allowed ukijumuisha argument --fast", err)
        self.assertEqual(out, b'')

    eleza test_decompress_cannot_have_flags_compression(self):
        rc, out, err = assert_python_failure('-m', 'gzip', '--fast', '-d')
        self.assertIn(b'error: argument -d/--decompress: sio allowed ukijumuisha argument --fast', err)
        self.assertEqual(out, b'')


eleza test_main(verbose=Tupu):
    support.run_unittest(TestGzip, TestOpen, TestCommandLine)


ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
