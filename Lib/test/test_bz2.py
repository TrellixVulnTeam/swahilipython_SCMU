kutoka test agiza support
kutoka test.support agiza bigmemtest, _4G

agiza unittest
kutoka io agiza BytesIO, DEFAULT_BUFFER_SIZE
agiza os
agiza pickle
agiza glob
agiza tempfile
agiza pathlib
agiza random
agiza shutil
agiza subprocess
agiza threading
kutoka test.support agiza unlink
agiza _compression
agiza sys


# Skip tests ikiwa the bz2 module doesn't exist.
bz2 = support.import_module('bz2')
kutoka bz2 agiza BZ2File, BZ2Compressor, BZ2Decompressor

has_cmdline_bunzip2 = Tupu

eleza ext_decompress(data):
    global has_cmdline_bunzip2
    ikiwa has_cmdline_bunzip2 ni Tupu:
        has_cmdline_bunzip2 = bool(shutil.which('bunzip2'))
    ikiwa has_cmdline_bunzip2:
        rudisha subprocess.check_output(['bunzip2'], input=data)
    isipokua:
        rudisha bz2.decompress(data)

kundi BaseTest(unittest.TestCase):
    "Base kila other testcases."

    TEXT_LINES = [
        b'root:x:0:0:root:/root:/bin/bash\n',
        b'bin:x:1:1:bin:/bin:\n',
        b'daemon:x:2:2:daemon:/sbin:\n',
        b'adm:x:3:4:adm:/var/adm:\n',
        b'lp:x:4:7:lp:/var/spool/lpd:\n',
        b'sync:x:5:0:sync:/sbin:/bin/sync\n',
        b'shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown\n',
        b'halt:x:7:0:halt:/sbin:/sbin/halt\n',
        b'mail:x:8:12:mail:/var/spool/mail:\n',
        b'news:x:9:13:news:/var/spool/news:\n',
        b'uucp:x:10:14:uucp:/var/spool/uucp:\n',
        b'operator:x:11:0:operator:/root:\n',
        b'games:x:12:100:games:/usr/games:\n',
        b'gopher:x:13:30:gopher:/usr/lib/gopher-data:\n',
        b'ftp:x:14:50:FTP User:/var/ftp:/bin/bash\n',
        b'nobody:x:65534:65534:Nobody:/home:\n',
        b'postfix:x:100:101:postfix:/var/spool/postfix:\n',
        b'niemeyer:x:500:500::/home/niemeyer:/bin/bash\n',
        b'postgres:x:101:102:PostgreSQL Server:/var/lib/pgsql:/bin/bash\n',
        b'mysql:x:102:103:MySQL server:/var/lib/mysql:/bin/bash\n',
        b'www:x:103:104::/var/www:/bin/false\n',
        ]
    TEXT = b''.join(TEXT_LINES)
    DATA = b'BZh91AY&SY.\xc8N\x18\x00\x01>_\x80\x00\x10@\x02\xff\xf0\x01\x07n\x00?\xe7\xff\xe00\x01\x99\xaa\x00\xc0\x03F\x86\x8c#&\x83F\x9a\x03\x06\xa6\xd0\xa6\x93M\x0fQ\xa7\xa8\x06\x804hh\x12$\x11\xa4i4\xf14S\xd2<Q\xb5\x0fH\xd3\xd4\xdd\xd5\x87\xbb\xf8\x94\r\x8f\xafI\x12\xe1\xc9\xf8/E\x00pu\x89\x12]\xc9\xbbDL\nQ\x0e\t1\x12\xdf\xa0\xc0\x97\xac2O9\x89\x13\x94\x0e\x1c7\x0ed\x95I\x0c\xaaJ\xa4\x18L\x10\x05#\x9c\xaf\xba\xbc/\x97\x8a#C\xc8\xe1\x8cW\xf9\xe2\xd0\xd6M\xa7\x8bXa<e\x84t\xcbL\xb3\xa7\xd9\xcd\xd1\xcb\x84.\xaf\xb3\xab\xab\xad`n}\xa0lh\tE,\x8eZ\x15\x17VH>\x88\xe5\xcd9gd6\x0b\n\xe9\x9b\xd5\x8a\x99\xf7\x08.K\x8ev\xfb\xf7xw\xbb\xdf\xa1\x92\xf1\xdd|/";\xa2\xba\x9f\xd5\xb1#A\xb6\xf6\xb3o\xc9\xc5y\\\xebO\xe7\x85\x9a\xbc\xb6f8\x952\xd5\xd7"%\x89>V,\xf7\xa6z\xe2\x9f\xa3\xdf\x11\x11"\xd6E)I\xa9\x13^\xca\xf3r\xd0\x03U\x922\xf26\xec\xb6\xed\x8b\xc3U\x13\x9d\xc5\x170\xa4\xfa^\x92\xacDF\x8a\x97\xd6\x19\xfe\xdd\xb8\xbd\x1a\x9a\x19\xa3\x80ankR\x8b\xe5\xd83]\xa9\xc6\x08\x82f\xf6\xb9"6l$\xb8j@\xc0\x8a\xb0l1..\xbak\x83ls\x15\xbc\xf4\xc1\x13\xbe\xf8E\xb8\x9d\r\xa8\x9dk\x84\xd3n\xfa\xacQ\x07\xb1%y\xaav\xb4\x08\xe0z\x1b\x16\xf5\x04\xe9\xcc\xb9\x08z\x1en7.G\xfc]\xc9\x14\xe1B@\xbb!8`'
    EMPTY_DATA = b'BZh9\x17rE8P\x90\x00\x00\x00\x00'
    BAD_DATA = b'this ni sio a valid bzip2 file'

    # Some tests need more than one block of uncompressed data. Since one block
    # ni at least 100,000 bytes, we gather some data dynamically na compress it.
    # Note that this assumes that compression works correctly, so we cannot
    # simply use the bigger test data kila all tests.
    test_size = 0
    BIG_TEXT = bytearray(128*1024)
    kila fname kwenye glob.glob(os.path.join(os.path.dirname(__file__), '*.py')):
        ukijumuisha open(fname, 'rb') as fh:
            test_size += fh.readinto(memoryview(BIG_TEXT)[test_size:])
        ikiwa test_size > 128*1024:
            koma
    BIG_DATA = bz2.compress(BIG_TEXT, compresslevel=1)

    eleza setUp(self):
        fd, self.filename = tempfile.mkstemp()
        os.close(fd)

    eleza tearDown(self):
        unlink(self.filename)


kundi BZ2FileTest(BaseTest):
    "Test the BZ2File class."

    eleza createTempFile(self, streams=1, suffix=b""):
        ukijumuisha open(self.filename, "wb") as f:
            f.write(self.DATA * streams)
            f.write(suffix)

    eleza testBadArgs(self):
        self.assertRaises(TypeError, BZ2File, 123.456)
        self.assertRaises(ValueError, BZ2File, os.devnull, "z")
        self.assertRaises(ValueError, BZ2File, os.devnull, "rx")
        self.assertRaises(ValueError, BZ2File, os.devnull, "rbt")
        self.assertRaises(ValueError, BZ2File, os.devnull, compresslevel=0)
        self.assertRaises(ValueError, BZ2File, os.devnull, compresslevel=10)

    eleza testRead(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, float())
            self.assertEqual(bz2f.read(), self.TEXT)

    eleza testReadBadFile(self):
        self.createTempFile(streams=0, suffix=self.BAD_DATA)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(OSError, bz2f.read)

    eleza testReadMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, float())
            self.assertEqual(bz2f.read(), self.TEXT * 5)

    eleza testReadMonkeyMultiStream(self):
        # Test BZ2File.read() on a multi-stream archive where a stream
        # boundary coincides ukijumuisha the end of the raw read buffer.
        buffer_size = _compression.BUFFER_SIZE
        _compression.BUFFER_SIZE = len(self.DATA)
        jaribu:
            self.createTempFile(streams=5)
            ukijumuisha BZ2File(self.filename) as bz2f:
                self.assertRaises(TypeError, bz2f.read, float())
                self.assertEqual(bz2f.read(), self.TEXT * 5)
        mwishowe:
            _compression.BUFFER_SIZE = buffer_size

    eleza testReadTrailingJunk(self):
        self.createTempFile(suffix=self.BAD_DATA)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(), self.TEXT)

    eleza testReadMultiStreamTrailingJunk(self):
        self.createTempFile(streams=5, suffix=self.BAD_DATA)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(), self.TEXT * 5)

    eleza testRead0(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, float())
            self.assertEqual(bz2f.read(0), b"")

    eleza testReadChunk10(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            text = b''
            wakati Kweli:
                str = bz2f.read(10)
                ikiwa sio str:
                    koma
                text += str
            self.assertEqual(text, self.TEXT)

    eleza testReadChunk10MultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            text = b''
            wakati Kweli:
                str = bz2f.read(10)
                ikiwa sio str:
                    koma
                text += str
            self.assertEqual(text, self.TEXT * 5)

    eleza testRead100(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(100), self.TEXT[:100])

    eleza testPeek(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            pdata = bz2f.peek()
            self.assertNotEqual(len(pdata), 0)
            self.assertKweli(self.TEXT.startswith(pdata))
            self.assertEqual(bz2f.read(), self.TEXT)

    eleza testReadInto(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            n = 128
            b = bytearray(n)
            self.assertEqual(bz2f.readinto(b), n)
            self.assertEqual(b, self.TEXT[:n])
            n = len(self.TEXT) - n
            b = bytearray(len(self.TEXT))
            self.assertEqual(bz2f.readinto(b), n)
            self.assertEqual(b[:n], self.TEXT[-n:])

    eleza testReadLine(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readline, Tupu)
            kila line kwenye self.TEXT_LINES:
                self.assertEqual(bz2f.readline(), line)

    eleza testReadLineMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readline, Tupu)
            kila line kwenye self.TEXT_LINES * 5:
                self.assertEqual(bz2f.readline(), line)

    eleza testReadLines(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readlines, Tupu)
            self.assertEqual(bz2f.readlines(), self.TEXT_LINES)

    eleza testReadLinesMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readlines, Tupu)
            self.assertEqual(bz2f.readlines(), self.TEXT_LINES * 5)

    eleza testIterator(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(list(iter(bz2f)), self.TEXT_LINES)

    eleza testIteratorMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(list(iter(bz2f)), self.TEXT_LINES * 5)

    eleza testClosedIteratorDeadlock(self):
        # Issue #3309: Iteration on a closed BZ2File should release the lock.
        self.createTempFile()
        bz2f = BZ2File(self.filename)
        bz2f.close()
        self.assertRaises(ValueError, next, bz2f)
        # This call will deadlock ikiwa the above call failed to release the lock.
        self.assertRaises(ValueError, bz2f.readlines)

    eleza testWrite(self):
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        ukijumuisha open(self.filename, 'rb') as f:
            self.assertEqual(ext_decompress(f.read()), self.TEXT)

    eleza testWriteChunks10(self):
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            n = 0
            wakati Kweli:
                str = self.TEXT[n*10:(n+1)*10]
                ikiwa sio str:
                    koma
                bz2f.write(str)
                n += 1
        ukijumuisha open(self.filename, 'rb') as f:
            self.assertEqual(ext_decompress(f.read()), self.TEXT)

    eleza testWriteNonDefaultCompressLevel(self):
        expected = bz2.compress(self.TEXT, compresslevel=5)
        ukijumuisha BZ2File(self.filename, "w", compresslevel=5) as bz2f:
            bz2f.write(self.TEXT)
        ukijumuisha open(self.filename, "rb") as f:
            self.assertEqual(f.read(), expected)

    eleza testWriteLines(self):
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.writelines)
            bz2f.writelines(self.TEXT_LINES)
        # Issue #1535500: Calling writelines() on a closed BZ2File
        # should  ashiria an exception.
        self.assertRaises(ValueError, bz2f.writelines, ["a"])
        ukijumuisha open(self.filename, 'rb') as f:
            self.assertEqual(ext_decompress(f.read()), self.TEXT)

    eleza testWriteMethodsOnReadOnlyFile(self):
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            bz2f.write(b"abc")

        ukijumuisha BZ2File(self.filename, "r") as bz2f:
            self.assertRaises(OSError, bz2f.write, b"a")
            self.assertRaises(OSError, bz2f.writelines, [b"a"])

    eleza testAppend(self):
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        ukijumuisha BZ2File(self.filename, "a") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        ukijumuisha open(self.filename, 'rb') as f:
            self.assertEqual(ext_decompress(f.read()), self.TEXT * 2)

    eleza testSeekForward(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.seek)
            bz2f.seek(150)
            self.assertEqual(bz2f.read(), self.TEXT[150:])

    eleza testSeekForwardAcrossStreams(self):
        self.createTempFile(streams=2)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.seek)
            bz2f.seek(len(self.TEXT) + 150)
            self.assertEqual(bz2f.read(), self.TEXT[150:])

    eleza testSeekBackwards(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.read(500)
            bz2f.seek(-150, 1)
            self.assertEqual(bz2f.read(), self.TEXT[500-150:])

    eleza testSeekBackwardsAcrossStreams(self):
        self.createTempFile(streams=2)
        ukijumuisha BZ2File(self.filename) as bz2f:
            readto = len(self.TEXT) + 100
            wakati readto > 0:
                readto -= len(bz2f.read(readto))
            bz2f.seek(-150, 1)
            self.assertEqual(bz2f.read(), self.TEXT[100-150:] + self.TEXT)

    eleza testSeekBackwardsFromEnd(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(-150, 2)
            self.assertEqual(bz2f.read(), self.TEXT[len(self.TEXT)-150:])

    eleza testSeekBackwardsFromEndAcrossStreams(self):
        self.createTempFile(streams=2)
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(-1000, 2)
            self.assertEqual(bz2f.read(), (self.TEXT * 2)[-1000:])

    eleza testSeekPostEnd(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT))
            self.assertEqual(bz2f.read(), b"")

    eleza testSeekPostEndMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT) * 5)
            self.assertEqual(bz2f.read(), b"")

    eleza testSeekPostEndTwice(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT))
            self.assertEqual(bz2f.read(), b"")

    eleza testSeekPostEndTwiceMultiStream(self):
        self.createTempFile(streams=5)
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT) * 5)
            self.assertEqual(bz2f.read(), b"")

    eleza testSeekPreStart(self):
        self.createTempFile()
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(-150)
            self.assertEqual(bz2f.tell(), 0)
            self.assertEqual(bz2f.read(), self.TEXT)

    eleza testSeekPreStartMultiStream(self):
        self.createTempFile(streams=2)
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.seek(-150)
            self.assertEqual(bz2f.tell(), 0)
            self.assertEqual(bz2f.read(), self.TEXT * 2)

    eleza testFileno(self):
        self.createTempFile()
        ukijumuisha open(self.filename, 'rb') as rawf:
            bz2f = BZ2File(rawf)
            jaribu:
                self.assertEqual(bz2f.fileno(), rawf.fileno())
            mwishowe:
                bz2f.close()
        self.assertRaises(ValueError, bz2f.fileno)

    eleza testSeekable(self):
        bz2f = BZ2File(BytesIO(self.DATA))
        jaribu:
            self.assertKweli(bz2f.seekable())
            bz2f.read()
            self.assertKweli(bz2f.seekable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.seekable)

        bz2f = BZ2File(BytesIO(), "w")
        jaribu:
            self.assertUongo(bz2f.seekable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.seekable)

        src = BytesIO(self.DATA)
        src.seekable = lambda: Uongo
        bz2f = BZ2File(src)
        jaribu:
            self.assertUongo(bz2f.seekable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.seekable)

    eleza testReadable(self):
        bz2f = BZ2File(BytesIO(self.DATA))
        jaribu:
            self.assertKweli(bz2f.readable())
            bz2f.read()
            self.assertKweli(bz2f.readable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.readable)

        bz2f = BZ2File(BytesIO(), "w")
        jaribu:
            self.assertUongo(bz2f.readable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.readable)

    eleza testWritable(self):
        bz2f = BZ2File(BytesIO(self.DATA))
        jaribu:
            self.assertUongo(bz2f.writable())
            bz2f.read()
            self.assertUongo(bz2f.writable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.writable)

        bz2f = BZ2File(BytesIO(), "w")
        jaribu:
            self.assertKweli(bz2f.writable())
        mwishowe:
            bz2f.close()
        self.assertRaises(ValueError, bz2f.writable)

    eleza testOpenDel(self):
        self.createTempFile()
        kila i kwenye range(10000):
            o = BZ2File(self.filename)
            toa o

    eleza testOpenTupuxistent(self):
        self.assertRaises(OSError, BZ2File, "/non/existent")

    eleza testReadlinesNoNewline(self):
        # Issue #1191043: readlines() fails on a file containing no newline.
        data = b'BZh91AY&SY\xd9b\x89]\x00\x00\x00\x03\x80\x04\x00\x02\x00\x0c\x00 \x00!\x9ah3M\x13<]\xc9\x14\xe1BCe\x8a%t'
        ukijumuisha open(self.filename, "wb") as f:
            f.write(data)
        ukijumuisha BZ2File(self.filename) as bz2f:
            lines = bz2f.readlines()
        self.assertEqual(lines, [b'Test'])
        ukijumuisha BZ2File(self.filename) as bz2f:
            xlines = list(bz2f.readlines())
        self.assertEqual(xlines, [b'Test'])

    eleza testContextProtocol(self):
        f = Tupu
        ukijumuisha BZ2File(self.filename, "wb") as f:
            f.write(b"xxx")
        f = BZ2File(self.filename, "rb")
        f.close()
        jaribu:
            ukijumuisha f:
                pass
        except ValueError:
            pass
        isipokua:
            self.fail("__enter__ on a closed file didn't  ashiria an exception")
        jaribu:
            ukijumuisha BZ2File(self.filename, "wb") as f:
                1/0
        except ZeroDivisionError:
            pass
        isipokua:
            self.fail("1/0 didn't  ashiria an exception")

    eleza testThreading(self):
        # Issue #7205: Using a BZ2File kutoka several threads shouldn't deadlock.
        data = b"1" * 2**20
        nthreads = 10
        ukijumuisha BZ2File(self.filename, 'wb') as f:
            eleza comp():
                kila i kwenye range(5):
                    f.write(data)
            threads = [threading.Thread(target=comp) kila i kwenye range(nthreads)]
            ukijumuisha support.start_threads(threads):
                pass

    eleza testMixedIterationAndReads(self):
        self.createTempFile()
        linelen = len(self.TEXT_LINES[0])
        halflen = linelen // 2
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.read(halflen)
            self.assertEqual(next(bz2f), self.TEXT_LINES[0][halflen:])
            self.assertEqual(bz2f.read(), self.TEXT[linelen:])
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.readline()
            self.assertEqual(next(bz2f), self.TEXT_LINES[1])
            self.assertEqual(bz2f.readline(), self.TEXT_LINES[2])
        ukijumuisha BZ2File(self.filename) as bz2f:
            bz2f.readlines()
            self.assertRaises(StopIteration, next, bz2f)
            self.assertEqual(bz2f.readlines(), [])

    eleza testMultiStreamOrdering(self):
        # Test the ordering of streams when reading a multi-stream archive.
        data1 = b"foo" * 1000
        data2 = b"bar" * 1000
        ukijumuisha BZ2File(self.filename, "w") as bz2f:
            bz2f.write(data1)
        ukijumuisha BZ2File(self.filename, "a") as bz2f:
            bz2f.write(data2)
        ukijumuisha BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(), data1 + data2)

    eleza testOpenBytesFilename(self):
        str_filename = self.filename
        jaribu:
            bytes_filename = str_filename.encode("ascii")
        except UnicodeEncodeError:
            self.skipTest("Temporary file name needs to be ASCII")
        ukijumuisha BZ2File(bytes_filename, "wb") as f:
            f.write(self.DATA)
        ukijumuisha BZ2File(bytes_filename, "rb") as f:
            self.assertEqual(f.read(), self.DATA)
        # Sanity check that we are actually operating on the right file.
        ukijumuisha BZ2File(str_filename, "rb") as f:
            self.assertEqual(f.read(), self.DATA)

    eleza testOpenPathLikeFilename(self):
        filename = pathlib.Path(self.filename)
        ukijumuisha BZ2File(filename, "wb") as f:
            f.write(self.DATA)
        ukijumuisha BZ2File(filename, "rb") as f:
            self.assertEqual(f.read(), self.DATA)

    eleza testDecompressLimited(self):
        """Decompressed data buffering should be limited"""
        bomb = bz2.compress(b'\0' * int(2e6), compresslevel=9)
        self.assertLess(len(bomb), _compression.BUFFER_SIZE)

        decomp = BZ2File(BytesIO(bomb))
        self.assertEqual(decomp.read(1), b'\0')
        max_decomp = 1 + DEFAULT_BUFFER_SIZE
        self.assertLessEqual(decomp._buffer.raw.tell(), max_decomp,
            "Excessive amount of data was decompressed")


    # Tests kila a BZ2File wrapping another file object:

    eleza testReadBytesIO(self):
        ukijumuisha BytesIO(self.DATA) as bio:
            ukijumuisha BZ2File(bio) as bz2f:
                self.assertRaises(TypeError, bz2f.read, float())
                self.assertEqual(bz2f.read(), self.TEXT)
            self.assertUongo(bio.closed)

    eleza testPeekBytesIO(self):
        ukijumuisha BytesIO(self.DATA) as bio:
            ukijumuisha BZ2File(bio) as bz2f:
                pdata = bz2f.peek()
                self.assertNotEqual(len(pdata), 0)
                self.assertKweli(self.TEXT.startswith(pdata))
                self.assertEqual(bz2f.read(), self.TEXT)

    eleza testWriteBytesIO(self):
        ukijumuisha BytesIO() as bio:
            ukijumuisha BZ2File(bio, "w") as bz2f:
                self.assertRaises(TypeError, bz2f.write)
                bz2f.write(self.TEXT)
            self.assertEqual(ext_decompress(bio.getvalue()), self.TEXT)
            self.assertUongo(bio.closed)

    eleza testSeekForwardBytesIO(self):
        ukijumuisha BytesIO(self.DATA) as bio:
            ukijumuisha BZ2File(bio) as bz2f:
                self.assertRaises(TypeError, bz2f.seek)
                bz2f.seek(150)
                self.assertEqual(bz2f.read(), self.TEXT[150:])

    eleza testSeekBackwardsBytesIO(self):
        ukijumuisha BytesIO(self.DATA) as bio:
            ukijumuisha BZ2File(bio) as bz2f:
                bz2f.read(500)
                bz2f.seek(-150, 1)
                self.assertEqual(bz2f.read(), self.TEXT[500-150:])

    eleza test_read_truncated(self):
        # Drop the eos_magic field (6 bytes) na CRC (4 bytes).
        truncated = self.DATA[:-10]
        ukijumuisha BZ2File(BytesIO(truncated)) as f:
            self.assertRaises(EOFError, f.read)
        ukijumuisha BZ2File(BytesIO(truncated)) as f:
            self.assertEqual(f.read(len(self.TEXT)), self.TEXT)
            self.assertRaises(EOFError, f.read, 1)
        # Incomplete 4-byte file header, na block header of at least 146 bits.
        kila i kwenye range(22):
            ukijumuisha BZ2File(BytesIO(truncated[:i])) as f:
                self.assertRaises(EOFError, f.read, 1)


kundi BZ2CompressorTest(BaseTest):
    eleza testCompress(self):
        bz2c = BZ2Compressor()
        self.assertRaises(TypeError, bz2c.compress)
        data = bz2c.compress(self.TEXT)
        data += bz2c.flush()
        self.assertEqual(ext_decompress(data), self.TEXT)

    eleza testCompressEmptyString(self):
        bz2c = BZ2Compressor()
        data = bz2c.compress(b'')
        data += bz2c.flush()
        self.assertEqual(data, self.EMPTY_DATA)

    eleza testCompressChunks10(self):
        bz2c = BZ2Compressor()
        n = 0
        data = b''
        wakati Kweli:
            str = self.TEXT[n*10:(n+1)*10]
            ikiwa sio str:
                koma
            data += bz2c.compress(str)
            n += 1
        data += bz2c.flush()
        self.assertEqual(ext_decompress(data), self.TEXT)

    @support.skip_if_pgo_task
    @bigmemtest(size=_4G + 100, memuse=2)
    eleza testCompress4G(self, size):
        # "Test BZ2Compressor.compress()/flush() ukijumuisha >4GiB input"
        bz2c = BZ2Compressor()
        data = b"x" * size
        jaribu:
            compressed = bz2c.compress(data)
            compressed += bz2c.flush()
        mwishowe:
            data = Tupu  # Release memory
        data = bz2.decompress(compressed)
        jaribu:
            self.assertEqual(len(data), size)
            self.assertEqual(len(data.strip(b"x")), 0)
        mwishowe:
            data = Tupu

    eleza testPickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises(TypeError):
                pickle.dumps(BZ2Compressor(), proto)


kundi BZ2DecompressorTest(BaseTest):
    eleza test_Constructor(self):
        self.assertRaises(TypeError, BZ2Decompressor, 42)

    eleza testDecompress(self):
        bz2d = BZ2Decompressor()
        self.assertRaises(TypeError, bz2d.decompress)
        text = bz2d.decompress(self.DATA)
        self.assertEqual(text, self.TEXT)

    eleza testDecompressChunks10(self):
        bz2d = BZ2Decompressor()
        text = b''
        n = 0
        wakati Kweli:
            str = self.DATA[n*10:(n+1)*10]
            ikiwa sio str:
                koma
            text += bz2d.decompress(str)
            n += 1
        self.assertEqual(text, self.TEXT)

    eleza testDecompressUnusedData(self):
        bz2d = BZ2Decompressor()
        unused_data = b"this ni unused data"
        text = bz2d.decompress(self.DATA+unused_data)
        self.assertEqual(text, self.TEXT)
        self.assertEqual(bz2d.unused_data, unused_data)

    eleza testEOFError(self):
        bz2d = BZ2Decompressor()
        text = bz2d.decompress(self.DATA)
        self.assertRaises(EOFError, bz2d.decompress, b"anything")
        self.assertRaises(EOFError, bz2d.decompress, b"")

    @support.skip_if_pgo_task
    @bigmemtest(size=_4G + 100, memuse=3.3)
    eleza testDecompress4G(self, size):
        # "Test BZ2Decompressor.decompress() ukijumuisha >4GiB input"
        blocksize = 10 * 1024 * 1024
        block = random.getrandbits(blocksize * 8).to_bytes(blocksize, 'little')
        jaribu:
            data = block * (size // blocksize + 1)
            compressed = bz2.compress(data)
            bz2d = BZ2Decompressor()
            decompressed = bz2d.decompress(compressed)
            self.assertKweli(decompressed == data)
        mwishowe:
            data = Tupu
            compressed = Tupu
            decompressed = Tupu

    eleza testPickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises(TypeError):
                pickle.dumps(BZ2Decompressor(), proto)

    eleza testDecompressorChunksMaxsize(self):
        bzd = BZ2Decompressor()
        max_length = 100
        out = []

        # Feed some input
        len_ = len(self.BIG_DATA) - 64
        out.append(bzd.decompress(self.BIG_DATA[:len_],
                                  max_length=max_length))
        self.assertUongo(bzd.needs_input)
        self.assertEqual(len(out[-1]), max_length)

        # Retrieve more data without providing more input
        out.append(bzd.decompress(b'', max_length=max_length))
        self.assertUongo(bzd.needs_input)
        self.assertEqual(len(out[-1]), max_length)

        # Retrieve more data wakati providing more input
        out.append(bzd.decompress(self.BIG_DATA[len_:],
                                  max_length=max_length))
        self.assertLessEqual(len(out[-1]), max_length)

        # Retrieve remaining uncompressed data
        wakati sio bzd.eof:
            out.append(bzd.decompress(b'', max_length=max_length))
            self.assertLessEqual(len(out[-1]), max_length)

        out = b"".join(out)
        self.assertEqual(out, self.BIG_TEXT)
        self.assertEqual(bzd.unused_data, b"")

    eleza test_decompressor_inputbuf_1(self):
        # Test reusing input buffer after moving existing
        # contents to beginning
        bzd = BZ2Decompressor()
        out = []

        # Create input buffer na fill it
        self.assertEqual(bzd.decompress(self.DATA[:100],
                                        max_length=0), b'')

        # Retrieve some results, freeing capacity at beginning
        # of input buffer
        out.append(bzd.decompress(b'', 2))

        # Add more data that fits into input buffer after
        # moving existing data to beginning
        out.append(bzd.decompress(self.DATA[100:105], 15))

        # Decompress rest of data
        out.append(bzd.decompress(self.DATA[105:]))
        self.assertEqual(b''.join(out), self.TEXT)

    eleza test_decompressor_inputbuf_2(self):
        # Test reusing input buffer by appending data at the
        # end right away
        bzd = BZ2Decompressor()
        out = []

        # Create input buffer na empty it
        self.assertEqual(bzd.decompress(self.DATA[:200],
                                        max_length=0), b'')
        out.append(bzd.decompress(b''))

        # Fill buffer ukijumuisha new data
        out.append(bzd.decompress(self.DATA[200:280], 2))

        # Append some more data, sio enough to require resize
        out.append(bzd.decompress(self.DATA[280:300], 2))

        # Decompress rest of data
        out.append(bzd.decompress(self.DATA[300:]))
        self.assertEqual(b''.join(out), self.TEXT)

    eleza test_decompressor_inputbuf_3(self):
        # Test reusing input buffer after extending it

        bzd = BZ2Decompressor()
        out = []

        # Create almost full input buffer
        out.append(bzd.decompress(self.DATA[:200], 5))

        # Add even more data to it, requiring resize
        out.append(bzd.decompress(self.DATA[200:300], 5))

        # Decompress rest of data
        out.append(bzd.decompress(self.DATA[300:]))
        self.assertEqual(b''.join(out), self.TEXT)

    eleza test_failure(self):
        bzd = BZ2Decompressor()
        self.assertRaises(Exception, bzd.decompress, self.BAD_DATA * 30)
        # Previously, a second call could crash due to internal inconsistency
        self.assertRaises(Exception, bzd.decompress, self.BAD_DATA * 30)

    @support.refcount_test
    eleza test_refleaks_in___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        bzd = BZ2Decompressor()
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            bzd.__init__()
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)


kundi CompressDecompressTest(BaseTest):
    eleza testCompress(self):
        data = bz2.compress(self.TEXT)
        self.assertEqual(ext_decompress(data), self.TEXT)

    eleza testCompressEmptyString(self):
        text = bz2.compress(b'')
        self.assertEqual(text, self.EMPTY_DATA)

    eleza testDecompress(self):
        text = bz2.decompress(self.DATA)
        self.assertEqual(text, self.TEXT)

    eleza testDecompressEmpty(self):
        text = bz2.decompress(b"")
        self.assertEqual(text, b"")

    eleza testDecompressToEmptyString(self):
        text = bz2.decompress(self.EMPTY_DATA)
        self.assertEqual(text, b'')

    eleza testDecompressIncomplete(self):
        self.assertRaises(ValueError, bz2.decompress, self.DATA[:-10])

    eleza testDecompressBadData(self):
        self.assertRaises(OSError, bz2.decompress, self.BAD_DATA)

    eleza testDecompressMultiStream(self):
        text = bz2.decompress(self.DATA * 5)
        self.assertEqual(text, self.TEXT * 5)

    eleza testDecompressTrailingJunk(self):
        text = bz2.decompress(self.DATA + self.BAD_DATA)
        self.assertEqual(text, self.TEXT)

    eleza testDecompressMultiStreamTrailingJunk(self):
        text = bz2.decompress(self.DATA * 5 + self.BAD_DATA)
        self.assertEqual(text, self.TEXT * 5)


kundi OpenTest(BaseTest):
    "Test the open function."

    eleza open(self, *args, **kwargs):
        rudisha bz2.open(*args, **kwargs)

    eleza test_binary_modes(self):
        kila mode kwenye ("wb", "xb"):
            ikiwa mode == "xb":
                unlink(self.filename)
            ukijumuisha self.open(self.filename, mode) as f:
                f.write(self.TEXT)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read())
                self.assertEqual(file_data, self.TEXT)
            ukijumuisha self.open(self.filename, "rb") as f:
                self.assertEqual(f.read(), self.TEXT)
            ukijumuisha self.open(self.filename, "ab") as f:
                f.write(self.TEXT)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read())
                self.assertEqual(file_data, self.TEXT * 2)

    eleza test_implicit_binary_modes(self):
        # Test implicit binary modes (no "b" ama "t" kwenye mode string).
        kila mode kwenye ("w", "x"):
            ikiwa mode == "x":
                unlink(self.filename)
            ukijumuisha self.open(self.filename, mode) as f:
                f.write(self.TEXT)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read())
                self.assertEqual(file_data, self.TEXT)
            ukijumuisha self.open(self.filename, "r") as f:
                self.assertEqual(f.read(), self.TEXT)
            ukijumuisha self.open(self.filename, "a") as f:
                f.write(self.TEXT)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read())
                self.assertEqual(file_data, self.TEXT * 2)

    eleza test_text_modes(self):
        text = self.TEXT.decode("ascii")
        text_native_eol = text.replace("\n", os.linesep)
        kila mode kwenye ("wt", "xt"):
            ikiwa mode == "xt":
                unlink(self.filename)
            ukijumuisha self.open(self.filename, mode) as f:
                f.write(text)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read()).decode("ascii")
                self.assertEqual(file_data, text_native_eol)
            ukijumuisha self.open(self.filename, "rt") as f:
                self.assertEqual(f.read(), text)
            ukijumuisha self.open(self.filename, "at") as f:
                f.write(text)
            ukijumuisha open(self.filename, "rb") as f:
                file_data = ext_decompress(f.read()).decode("ascii")
                self.assertEqual(file_data, text_native_eol * 2)

    eleza test_x_mode(self):
        kila mode kwenye ("x", "xb", "xt"):
            unlink(self.filename)
            ukijumuisha self.open(self.filename, mode) as f:
                pass
            ukijumuisha self.assertRaises(FileExistsError):
                ukijumuisha self.open(self.filename, mode) as f:
                    pass

    eleza test_fileobj(self):
        ukijumuisha self.open(BytesIO(self.DATA), "r") as f:
            self.assertEqual(f.read(), self.TEXT)
        ukijumuisha self.open(BytesIO(self.DATA), "rb") as f:
            self.assertEqual(f.read(), self.TEXT)
        text = self.TEXT.decode("ascii")
        ukijumuisha self.open(BytesIO(self.DATA), "rt") as f:
            self.assertEqual(f.read(), text)

    eleza test_bad_params(self):
        # Test invalid parameter combinations.
        self.assertRaises(ValueError,
                          self.open, self.filename, "wbt")
        self.assertRaises(ValueError,
                          self.open, self.filename, "xbt")
        self.assertRaises(ValueError,
                          self.open, self.filename, "rb", encoding="utf-8")
        self.assertRaises(ValueError,
                          self.open, self.filename, "rb", errors="ignore")
        self.assertRaises(ValueError,
                          self.open, self.filename, "rb", newline="\n")

    eleza test_encoding(self):
        # Test non-default encoding.
        text = self.TEXT.decode("ascii")
        text_native_eol = text.replace("\n", os.linesep)
        ukijumuisha self.open(self.filename, "wt", encoding="utf-16-le") as f:
            f.write(text)
        ukijumuisha open(self.filename, "rb") as f:
            file_data = ext_decompress(f.read()).decode("utf-16-le")
            self.assertEqual(file_data, text_native_eol)
        ukijumuisha self.open(self.filename, "rt", encoding="utf-16-le") as f:
            self.assertEqual(f.read(), text)

    eleza test_encoding_error_handler(self):
        # Test ukijumuisha non-default encoding error handler.
        ukijumuisha self.open(self.filename, "wb") as f:
            f.write(b"foo\xffbar")
        ukijumuisha self.open(self.filename, "rt", encoding="ascii", errors="ignore") \
                as f:
            self.assertEqual(f.read(), "foobar")

    eleza test_newline(self):
        # Test ukijumuisha explicit newline (universal newline mode disabled).
        text = self.TEXT.decode("ascii")
        ukijumuisha self.open(self.filename, "wt", newline="\n") as f:
            f.write(text)
        ukijumuisha self.open(self.filename, "rt", newline="\r") as f:
            self.assertEqual(f.readlines(), [text])


eleza test_main():
    support.run_unittest(
        BZ2FileTest,
        BZ2CompressorTest,
        BZ2DecompressorTest,
        CompressDecompressTest,
        OpenTest,
    )
    support.reap_children()

ikiwa __name__ == '__main__':
    test_main()
