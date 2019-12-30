kutoka test.support agiza (TESTFN, import_module, unlink,
                          requires, _2G, _4G, gc_collect, cpython_only)
agiza unittest
agiza os
agiza re
agiza itertools
agiza socket
agiza sys
agiza weakref

# Skip test ikiwa we can't agiza mmap.
mmap = import_module('mmap')

PAGESIZE = mmap.PAGESIZE


kundi MmapTests(unittest.TestCase):

    eleza setUp(self):
        ikiwa os.path.exists(TESTFN):
            os.unlink(TESTFN)

    eleza tearDown(self):
        jaribu:
            os.unlink(TESTFN)
        except OSError:
            pass

    eleza test_basic(self):
        # Test mmap module on Unix systems na Windows

        # Create a file to be mmap'ed.
        f = open(TESTFN, 'bw+')
        jaribu:
            # Write 2 pages worth of data to the file
            f.write(b'\0'* PAGESIZE)
            f.write(b'foo')
            f.write(b'\0'* (PAGESIZE-3) )
            f.flush()
            m = mmap.mmap(f.fileno(), 2 * PAGESIZE)
        mwishowe:
            f.close()

        # Simple sanity checks

        tp = str(type(m))  # SF bug 128713:  segfaulted on Linux
        self.assertEqual(m.find(b'foo'), PAGESIZE)

        self.assertEqual(len(m), 2*PAGESIZE)

        self.assertEqual(m[0], 0)
        self.assertEqual(m[0:3], b'\0\0\0')

        # Shouldn't crash on boundary (Issue #5292)
        self.assertRaises(IndexError, m.__getitem__, len(m))
        self.assertRaises(IndexError, m.__setitem__, len(m), b'\0')

        # Modify the file's content
        m[0] = b'3'[0]
        m[PAGESIZE +3: PAGESIZE +3+3] = b'bar'

        # Check that the modification worked
        self.assertEqual(m[0], b'3'[0])
        self.assertEqual(m[0:3], b'3\0\0')
        self.assertEqual(m[PAGESIZE-1 : PAGESIZE + 7], b'\0foobar\0')

        m.flush()

        # Test doing a regular expression match kwenye an mmap'ed file
        match = re.search(b'[A-Za-z]+', m)
        ikiwa match ni Tupu:
            self.fail('regex match on mmap failed!')
        isipokua:
            start, end = match.span(0)
            length = end - start

            self.assertEqual(start, PAGESIZE)
            self.assertEqual(end, PAGESIZE + 6)

        # test seeking around (try to overflow the seek implementation)
        m.seek(0,0)
        self.assertEqual(m.tell(), 0)
        m.seek(42,1)
        self.assertEqual(m.tell(), 42)
        m.seek(0,2)
        self.assertEqual(m.tell(), len(m))

        # Try to seek to negative position...
        self.assertRaises(ValueError, m.seek, -1)

        # Try to seek beyond end of mmap...
        self.assertRaises(ValueError, m.seek, 1, 2)

        # Try to seek to negative position...
        self.assertRaises(ValueError, m.seek, -len(m)-1, 2)

        # Try resizing map
        jaribu:
            m.resize(512)
        except SystemError:
            # resize() sio supported
            # No messages are printed, since the output of this test suite
            # would then be different across platforms.
            pass
        isipokua:
            # resize() ni supported
            self.assertEqual(len(m), 512)
            # Check that we can no longer seek beyond the new size.
            self.assertRaises(ValueError, m.seek, 513, 0)

            # Check that the underlying file ni truncated too
            # (bug #728515)
            f = open(TESTFN, 'rb')
            jaribu:
                f.seek(0, 2)
                self.assertEqual(f.tell(), 512)
            mwishowe:
                f.close()
            self.assertEqual(m.size(), 512)

        m.close()

    eleza test_access_parameter(self):
        # Test kila "access" keyword parameter
        mapsize = 10
        ukijumuisha open(TESTFN, "wb") as fp:
            fp.write(b"a"*mapsize)
        ukijumuisha open(TESTFN, "rb") as f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_READ)
            self.assertEqual(m[:], b'a'*mapsize, "Readonly memory map data incorrect.")

            # Ensuring that readonly mmap can't be slice assigned
            jaribu:
                m[:] = b'b'*mapsize
            except TypeError:
                pass
            isipokua:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be item assigned
            jaribu:
                m[0] = b'b'
            except TypeError:
                pass
            isipokua:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be write() to
            jaribu:
                m.seek(0,0)
                m.write(b'abc')
            except TypeError:
                pass
            isipokua:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be write_byte() to
            jaribu:
                m.seek(0,0)
                m.write_byte(b'd')
            except TypeError:
                pass
            isipokua:
                self.fail("Able to write to readonly memory map")

            # Ensuring that readonly mmap can't be resized
            jaribu:
                m.resize(2*mapsize)
            except SystemError:   # resize ni sio universally supported
                pass
            except TypeError:
                pass
            isipokua:
                self.fail("Able to resize readonly memory map")
            ukijumuisha open(TESTFN, "rb") as fp:
                self.assertEqual(fp.read(), b'a'*mapsize,
                                 "Readonly memory map data file was modified")

        # Opening mmap ukijumuisha size too big
        ukijumuisha open(TESTFN, "r+b") as f:
            jaribu:
                m = mmap.mmap(f.fileno(), mapsize+1)
            except ValueError:
                # we do sio expect a ValueError on Windows
                # CAUTION:  This also changes the size of the file on disk, and
                # later tests assume that the length hasn't changed.  We need to
                # repair that.
                ikiwa sys.platform.startswith('win'):
                    self.fail("Opening mmap ukijumuisha size+1 should work on Windows.")
            isipokua:
                # we expect a ValueError on Unix, but sio on Windows
                ikiwa sio sys.platform.startswith('win'):
                    self.fail("Opening mmap ukijumuisha size+1 should  ashiria ValueError.")
                m.close()
            ikiwa sys.platform.startswith('win'):
                # Repair damage kutoka the resizing test.
                ukijumuisha open(TESTFN, 'r+b') as f:
                    f.truncate(mapsize)

        # Opening mmap ukijumuisha access=ACCESS_WRITE
        ukijumuisha open(TESTFN, "r+b") as f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_WRITE)
            # Modifying write-through memory map
            m[:] = b'c'*mapsize
            self.assertEqual(m[:], b'c'*mapsize,
                   "Write-through memory map memory sio updated properly.")
            m.flush()
            m.close()
        ukijumuisha open(TESTFN, 'rb') as f:
            stuff = f.read()
        self.assertEqual(stuff, b'c'*mapsize,
               "Write-through memory map data file sio updated properly.")

        # Opening mmap ukijumuisha access=ACCESS_COPY
        ukijumuisha open(TESTFN, "r+b") as f:
            m = mmap.mmap(f.fileno(), mapsize, access=mmap.ACCESS_COPY)
            # Modifying copy-on-write memory map
            m[:] = b'd'*mapsize
            self.assertEqual(m[:], b'd' * mapsize,
                             "Copy-on-write memory map data sio written correctly.")
            m.flush()
            ukijumuisha open(TESTFN, "rb") as fp:
                self.assertEqual(fp.read(), b'c'*mapsize,
                                 "Copy-on-write test data file should sio be modified.")
            # Ensuring copy-on-write maps cannot be resized
            self.assertRaises(TypeError, m.resize, 2*mapsize)
            m.close()

        # Ensuring invalid access parameter raises exception
        ukijumuisha open(TESTFN, "r+b") as f:
            self.assertRaises(ValueError, mmap.mmap, f.fileno(), mapsize, access=4)

        ikiwa os.name == "posix":
            # Try incompatible flags, prot na access parameters.
            ukijumuisha open(TESTFN, "r+b") as f:
                self.assertRaises(ValueError, mmap.mmap, f.fileno(), mapsize,
                                  flags=mmap.MAP_PRIVATE,
                                  prot=mmap.PROT_READ, access=mmap.ACCESS_WRITE)

            # Try writing ukijumuisha PROT_EXEC na without PROT_WRITE
            prot = mmap.PROT_READ | getattr(mmap, 'PROT_EXEC', 0)
            ukijumuisha open(TESTFN, "r+b") as f:
                m = mmap.mmap(f.fileno(), mapsize, prot=prot)
                self.assertRaises(TypeError, m.write, b"abcdef")
                self.assertRaises(TypeError, m.write_byte, 0)
                m.close()

    eleza test_bad_file_desc(self):
        # Try opening a bad file descriptor...
        self.assertRaises(OSError, mmap.mmap, -2, 4096)

    eleza test_tougher_find(self):
        # Do a tougher .find() test.  SF bug 515943 pointed out that, kwenye 2.2,
        # searching kila data ukijumuisha embedded \0 bytes didn't work.
        ukijumuisha open(TESTFN, 'wb+') as f:

            data = b'aabaac\x00deef\x00\x00aa\x00'
            n = len(data)
            f.write(data)
            f.flush()
            m = mmap.mmap(f.fileno(), n)

        kila start kwenye range(n+1):
            kila finish kwenye range(start, n+1):
                slice = data[start : finish]
                self.assertEqual(m.find(slice), data.find(slice))
                self.assertEqual(m.find(slice + b'x'), -1)
        m.close()

    eleza test_find_end(self):
        # test the new 'end' parameter works as expected
        ukijumuisha open(TESTFN, 'wb+') as f:
            data = b'one two ones'
            n = len(data)
            f.write(data)
            f.flush()
            m = mmap.mmap(f.fileno(), n)

        self.assertEqual(m.find(b'one'), 0)
        self.assertEqual(m.find(b'ones'), 8)
        self.assertEqual(m.find(b'one', 0, -1), 0)
        self.assertEqual(m.find(b'one', 1), 8)
        self.assertEqual(m.find(b'one', 1, -1), 8)
        self.assertEqual(m.find(b'one', 1, -2), -1)
        self.assertEqual(m.find(bytearray(b'one')), 0)


    eleza test_rfind(self):
        # test the new 'end' parameter works as expected
        ukijumuisha open(TESTFN, 'wb+') as f:
            data = b'one two ones'
            n = len(data)
            f.write(data)
            f.flush()
            m = mmap.mmap(f.fileno(), n)

        self.assertEqual(m.rfind(b'one'), 8)
        self.assertEqual(m.rfind(b'one '), 0)
        self.assertEqual(m.rfind(b'one', 0, -1), 8)
        self.assertEqual(m.rfind(b'one', 0, -2), 0)
        self.assertEqual(m.rfind(b'one', 1, -1), 8)
        self.assertEqual(m.rfind(b'one', 1, -2), -1)
        self.assertEqual(m.rfind(bytearray(b'one')), 8)


    eleza test_double_close(self):
        # make sure a double close doesn't crash on Solaris (Bug# 665913)
        ukijumuisha open(TESTFN, 'wb+') as f:
            f.write(2**16 * b'a') # Arbitrary character

        ukijumuisha open(TESTFN, 'rb') as f:
            mf = mmap.mmap(f.fileno(), 2**16, access=mmap.ACCESS_READ)
            mf.close()
            mf.close()

    eleza test_entire_file(self):
        # test mapping of entire file by passing 0 kila map length
        ukijumuisha open(TESTFN, "wb+") as f:
            f.write(2**16 * b'm') # Arbitrary character

        ukijumuisha open(TESTFN, "rb+") as f, \
             mmap.mmap(f.fileno(), 0) as mf:
            self.assertEqual(len(mf), 2**16, "Map size should equal file size.")
            self.assertEqual(mf.read(2**16), 2**16 * b"m")

    eleza test_length_0_offset(self):
        # Issue #10916: test mapping of remainder of file by passing 0 for
        # map length ukijumuisha an offset doesn't cause a segfault.
        # NOTE: allocation granularity ni currently 65536 under Win64,
        # na therefore the minimum offset alignment.
        ukijumuisha open(TESTFN, "wb") as f:
            f.write((65536 * 2) * b'm') # Arbitrary character

        ukijumuisha open(TESTFN, "rb") as f:
            ukijumuisha mmap.mmap(f.fileno(), 0, offset=65536, access=mmap.ACCESS_READ) as mf:
                self.assertRaises(IndexError, mf.__getitem__, 80000)

    eleza test_length_0_large_offset(self):
        # Issue #10959: test mapping of a file by passing 0 for
        # map length ukijumuisha a large offset doesn't cause a segfault.
        ukijumuisha open(TESTFN, "wb") as f:
            f.write(115699 * b'm') # Arbitrary character

        ukijumuisha open(TESTFN, "w+b") as f:
            self.assertRaises(ValueError, mmap.mmap, f.fileno(), 0,
                              offset=2147418112)

    eleza test_move(self):
        # make move works everywhere (64-bit format problem earlier)
        ukijumuisha open(TESTFN, 'wb+') as f:

            f.write(b"ABCDEabcde") # Arbitrary character
            f.flush()

            mf = mmap.mmap(f.fileno(), 10)
            mf.move(5, 0, 5)
            self.assertEqual(mf[:], b"ABCDEABCDE", "Map move should have duplicated front 5")
            mf.close()

        # more excessive test
        data = b"0123456789"
        kila dest kwenye range(len(data)):
            kila src kwenye range(len(data)):
                kila count kwenye range(len(data) - max(dest, src)):
                    expected = data[:dest] + data[src:src+count] + data[dest+count:]
                    m = mmap.mmap(-1, len(data))
                    m[:] = data
                    m.move(dest, src, count)
                    self.assertEqual(m[:], expected)
                    m.close()

        # segfault test (Issue 5387)
        m = mmap.mmap(-1, 100)
        offsets = [-100, -1, 0, 1, 100]
        kila source, dest, size kwenye itertools.product(offsets, offsets, offsets):
            jaribu:
                m.move(source, dest, size)
            except ValueError:
                pass

        offsets = [(-1, -1, -1), (-1, -1, 0), (-1, 0, -1), (0, -1, -1),
                   (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
        kila source, dest, size kwenye offsets:
            self.assertRaises(ValueError, m.move, source, dest, size)

        m.close()

        m = mmap.mmap(-1, 1) # single byte
        self.assertRaises(ValueError, m.move, 0, 0, 2)
        self.assertRaises(ValueError, m.move, 1, 0, 1)
        self.assertRaises(ValueError, m.move, 0, 1, 1)
        m.move(0, 0, 1)
        m.move(0, 0, 0)


    eleza test_anonymous(self):
        # anonymous mmap.mmap(-1, PAGE)
        m = mmap.mmap(-1, PAGESIZE)
        kila x kwenye range(PAGESIZE):
            self.assertEqual(m[x], 0,
                             "anonymously mmap'ed contents should be zero")

        kila x kwenye range(PAGESIZE):
            b = x & 0xff
            m[x] = b
            self.assertEqual(m[x], b)

    eleza test_read_all(self):
        m = mmap.mmap(-1, 16)
        self.addCleanup(m.close)

        # With no parameters, ama Tupu ama a negative argument, reads all
        m.write(bytes(range(16)))
        m.seek(0)
        self.assertEqual(m.read(), bytes(range(16)))
        m.seek(8)
        self.assertEqual(m.read(), bytes(range(8, 16)))
        m.seek(16)
        self.assertEqual(m.read(), b'')
        m.seek(3)
        self.assertEqual(m.read(Tupu), bytes(range(3, 16)))
        m.seek(4)
        self.assertEqual(m.read(-1), bytes(range(4, 16)))
        m.seek(5)
        self.assertEqual(m.read(-2), bytes(range(5, 16)))
        m.seek(9)
        self.assertEqual(m.read(-42), bytes(range(9, 16)))

    eleza test_read_invalid_arg(self):
        m = mmap.mmap(-1, 16)
        self.addCleanup(m.close)

        self.assertRaises(TypeError, m.read, 'foo')
        self.assertRaises(TypeError, m.read, 5.5)
        self.assertRaises(TypeError, m.read, [1, 2, 3])

    eleza test_extended_getslice(self):
        # Test extended slicing by comparing ukijumuisha list slicing.
        s = bytes(reversed(range(256)))
        m = mmap.mmap(-1, len(s))
        m[:] = s
        self.assertEqual(m[:], s)
        indices = (0, Tupu, 1, 3, 19, 300, sys.maxsize, -1, -2, -31, -300)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Skip step 0 (invalid)
                kila step kwenye indices[1:]:
                    self.assertEqual(m[start:stop:step],
                                     s[start:stop:step])

    eleza test_extended_set_del_slice(self):
        # Test extended slicing by comparing ukijumuisha list slicing.
        s = bytes(reversed(range(256)))
        m = mmap.mmap(-1, len(s))
        indices = (0, Tupu, 1, 3, 19, 300, sys.maxsize, -1, -2, -31, -300)
        kila start kwenye indices:
            kila stop kwenye indices:
                # Skip invalid step 0
                kila step kwenye indices[1:]:
                    m[:] = s
                    self.assertEqual(m[:], s)
                    L = list(s)
                    # Make sure we have a slice of exactly the right length,
                    # but ukijumuisha different data.
                    data = L[start:stop:step]
                    data = bytes(reversed(data))
                    L[start:stop:step] = data
                    m[start:stop:step] = data
                    self.assertEqual(m[:], bytes(L))

    eleza make_mmap_file (self, f, halfsize):
        # Write 2 pages worth of data to the file
        f.write (b'\0' * halfsize)
        f.write (b'foo')
        f.write (b'\0' * (halfsize - 3))
        f.flush ()
        rudisha mmap.mmap (f.fileno(), 0)

    eleza test_empty_file (self):
        f = open (TESTFN, 'w+b')
        f.close()
        ukijumuisha open(TESTFN, "rb") as f :
            self.assertRaisesRegex(ValueError,
                                   "cannot mmap an empty file",
                                   mmap.mmap, f.fileno(), 0,
                                   access=mmap.ACCESS_READ)

    eleza test_offset (self):
        f = open (TESTFN, 'w+b')

        jaribu: # unlink TESTFN no matter what
            halfsize = mmap.ALLOCATIONGRANULARITY
            m = self.make_mmap_file (f, halfsize)
            m.close ()
            f.close ()

            mapsize = halfsize * 2
            # Try invalid offset
            f = open(TESTFN, "r+b")
            kila offset kwenye [-2, -1, Tupu]:
                jaribu:
                    m = mmap.mmap(f.fileno(), mapsize, offset=offset)
                    self.assertEqual(0, 1)
                except (ValueError, TypeError, OverflowError):
                    pass
                isipokua:
                    self.assertEqual(0, 0)
            f.close()

            # Try valid offset, hopefully 8192 works on all OSes
            f = open(TESTFN, "r+b")
            m = mmap.mmap(f.fileno(), mapsize - halfsize, offset=halfsize)
            self.assertEqual(m[0:3], b'foo')
            f.close()

            # Try resizing map
            jaribu:
                m.resize(512)
            except SystemError:
                pass
            isipokua:
                # resize() ni supported
                self.assertEqual(len(m), 512)
                # Check that we can no longer seek beyond the new size.
                self.assertRaises(ValueError, m.seek, 513, 0)
                # Check that the content ni sio changed
                self.assertEqual(m[0:3], b'foo')

                # Check that the underlying file ni truncated too
                f = open(TESTFN, 'rb')
                f.seek(0, 2)
                self.assertEqual(f.tell(), halfsize + 512)
                f.close()
                self.assertEqual(m.size(), halfsize + 512)

            m.close()

        mwishowe:
            f.close()
            jaribu:
                os.unlink(TESTFN)
            except OSError:
                pass

    eleza test_subclass(self):
        kundi anon_mmap(mmap.mmap):
            eleza __new__(klass, *args, **kwargs):
                rudisha mmap.mmap.__new__(klass, -1, *args, **kwargs)
        anon_mmap(PAGESIZE)

    @unittest.skipUnless(hasattr(mmap, 'PROT_READ'), "needs mmap.PROT_READ")
    eleza test_prot_readonly(self):
        mapsize = 10
        ukijumuisha open(TESTFN, "wb") as fp:
            fp.write(b"a"*mapsize)
        ukijumuisha open(TESTFN, "rb") as f:
            m = mmap.mmap(f.fileno(), mapsize, prot=mmap.PROT_READ)
            self.assertRaises(TypeError, m.write, "foo")

    eleza test_error(self):
        self.assertIs(mmap.error, OSError)

    eleza test_io_methods(self):
        data = b"0123456789"
        ukijumuisha open(TESTFN, "wb") as fp:
            fp.write(b"x"*len(data))
        ukijumuisha open(TESTFN, "r+b") as f:
            m = mmap.mmap(f.fileno(), len(data))
        # Test write_byte()
        kila i kwenye range(len(data)):
            self.assertEqual(m.tell(), i)
            m.write_byte(data[i])
            self.assertEqual(m.tell(), i+1)
        self.assertRaises(ValueError, m.write_byte, b"x"[0])
        self.assertEqual(m[:], data)
        # Test read_byte()
        m.seek(0)
        kila i kwenye range(len(data)):
            self.assertEqual(m.tell(), i)
            self.assertEqual(m.read_byte(), data[i])
            self.assertEqual(m.tell(), i+1)
        self.assertRaises(ValueError, m.read_byte)
        # Test read()
        m.seek(3)
        self.assertEqual(m.read(3), b"345")
        self.assertEqual(m.tell(), 6)
        # Test write()
        m.seek(3)
        m.write(b"bar")
        self.assertEqual(m.tell(), 6)
        self.assertEqual(m[:], b"012bar6789")
        m.write(bytearray(b"baz"))
        self.assertEqual(m.tell(), 9)
        self.assertEqual(m[:], b"012barbaz9")
        self.assertRaises(ValueError, m.write, b"ba")

    eleza test_non_ascii_byte(self):
        kila b kwenye (129, 200, 255): # > 128
            m = mmap.mmap(-1, 1)
            m.write_byte(b)
            self.assertEqual(m[0], b)
            m.seek(0)
            self.assertEqual(m.read_byte(), b)
            m.close()

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    eleza test_tagname(self):
        data1 = b"0123456789"
        data2 = b"abcdefghij"
        assert len(data1) == len(data2)

        # Test same tag
        m1 = mmap.mmap(-1, len(data1), tagname="foo")
        m1[:] = data1
        m2 = mmap.mmap(-1, len(data2), tagname="foo")
        m2[:] = data2
        self.assertEqual(m1[:], data2)
        self.assertEqual(m2[:], data2)
        m2.close()
        m1.close()

        # Test different tag
        m1 = mmap.mmap(-1, len(data1), tagname="foo")
        m1[:] = data1
        m2 = mmap.mmap(-1, len(data2), tagname="boo")
        m2[:] = data2
        self.assertEqual(m1[:], data1)
        self.assertEqual(m2[:], data2)
        m2.close()
        m1.close()

    @cpython_only
    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    eleza test_sizeof(self):
        m1 = mmap.mmap(-1, 100)
        tagname = "foo"
        m2 = mmap.mmap(-1, 100, tagname=tagname)
        self.assertEqual(sys.getsizeof(m2),
                         sys.getsizeof(m1) + len(tagname) + 1)

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    eleza test_crasher_on_windows(self):
        # Should sio crash (Issue 1733986)
        m = mmap.mmap(-1, 1000, tagname="foo")
        jaribu:
            mmap.mmap(-1, 5000, tagname="foo")[:] # same tagname, but larger size
        tatizo:
            pass
        m.close()

        # Should sio crash (Issue 5385)
        ukijumuisha open(TESTFN, "wb") as fp:
            fp.write(b"x"*10)
        f = open(TESTFN, "r+b")
        m = mmap.mmap(f.fileno(), 0)
        f.close()
        jaribu:
            m.resize(0) # will  ashiria OSError
        tatizo:
            pass
        jaribu:
            m[:]
        tatizo:
            pass
        m.close()

    @unittest.skipUnless(os.name == 'nt', 'requires Windows')
    eleza test_invalid_descriptor(self):
        # socket file descriptors are valid, but out of range
        # kila _get_osfhandle, causing a crash when validating the
        # parameters to _get_osfhandle.
        s = socket.socket()
        jaribu:
            ukijumuisha self.assertRaises(OSError):
                m = mmap.mmap(s.fileno(), 10)
        mwishowe:
            s.close()

    eleza test_context_manager(self):
        ukijumuisha mmap.mmap(-1, 10) as m:
            self.assertUongo(m.closed)
        self.assertKweli(m.closed)

    eleza test_context_manager_exception(self):
        # Test that the OSError gets passed through
        ukijumuisha self.assertRaises(Exception) as exc:
            ukijumuisha mmap.mmap(-1, 10) as m:
                 ashiria OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception raised kwenye context manager")
        self.assertKweli(m.closed, "context manager failed")

    eleza test_weakref(self):
        # Check mmap objects are weakrefable
        mm = mmap.mmap(-1, 16)
        wr = weakref.ref(mm)
        self.assertIs(wr(), mm)
        toa mm
        gc_collect()
        self.assertIs(wr(), Tupu)

    eleza test_write_returning_the_number_of_bytes_written(self):
        mm = mmap.mmap(-1, 16)
        self.assertEqual(mm.write(b""), 0)
        self.assertEqual(mm.write(b"x"), 1)
        self.assertEqual(mm.write(b"yz"), 2)
        self.assertEqual(mm.write(b"python"), 6)

    @unittest.skipIf(os.name == 'nt', 'cannot resize anonymous mmaps on Windows')
    eleza test_resize_past_pos(self):
        m = mmap.mmap(-1, 8192)
        self.addCleanup(m.close)
        m.read(5000)
        jaribu:
            m.resize(4096)
        except SystemError:
            self.skipTest("resizing sio supported")
        self.assertEqual(m.read(14), b'')
        self.assertRaises(ValueError, m.read_byte)
        self.assertRaises(ValueError, m.write_byte, 42)
        self.assertRaises(ValueError, m.write, b'abc')

    eleza test_concat_repeat_exception(self):
        m = mmap.mmap(-1, 16)
        ukijumuisha self.assertRaises(TypeError):
            m + m
        ukijumuisha self.assertRaises(TypeError):
            m * 2

    eleza test_flush_return_value(self):
        # mm.flush() should rudisha Tupu on success,  ashiria an
        # exception on error under all platforms.
        mm = mmap.mmap(-1, 16)
        self.addCleanup(mm.close)
        mm.write(b'python')
        result = mm.flush()
        self.assertIsTupu(result)
        ikiwa sys.platform.startswith('linux'):
            # 'offset' must be a multiple of mmap.PAGESIZE on Linux.
            # See bpo-34754 kila details.
            self.assertRaises(OSError, mm.flush, 1, len(b'python'))

    @unittest.skipUnless(hasattr(mmap.mmap, 'madvise'), 'needs madvise')
    eleza test_madvise(self):
        size = 2 * PAGESIZE
        m = mmap.mmap(-1, size)

        ukijumuisha self.assertRaisesRegex(ValueError, "madvise start out of bounds"):
            m.madvise(mmap.MADV_NORMAL, size)
        ukijumuisha self.assertRaisesRegex(ValueError, "madvise start out of bounds"):
            m.madvise(mmap.MADV_NORMAL, -1)
        ukijumuisha self.assertRaisesRegex(ValueError, "madvise length invalid"):
            m.madvise(mmap.MADV_NORMAL, 0, -1)
        ukijumuisha self.assertRaisesRegex(OverflowError, "madvise length too large"):
            m.madvise(mmap.MADV_NORMAL, PAGESIZE, sys.maxsize)
        self.assertEqual(m.madvise(mmap.MADV_NORMAL), Tupu)
        self.assertEqual(m.madvise(mmap.MADV_NORMAL, PAGESIZE), Tupu)
        self.assertEqual(m.madvise(mmap.MADV_NORMAL, PAGESIZE, size), Tupu)
        self.assertEqual(m.madvise(mmap.MADV_NORMAL, 0, 2), Tupu)
        self.assertEqual(m.madvise(mmap.MADV_NORMAL, 0, size), Tupu)


kundi LargeMmapTests(unittest.TestCase):

    eleza setUp(self):
        unlink(TESTFN)

    eleza tearDown(self):
        unlink(TESTFN)

    eleza _make_test_file(self, num_zeroes, tail):
        ikiwa sys.platform[:3] == 'win' ama sys.platform == 'darwin':
            requires('largefile',
                'test requires %s bytes na a long time to run' % str(0x180000000))
        f = open(TESTFN, 'w+b')
        jaribu:
            f.seek(num_zeroes)
            f.write(tail)
            f.flush()
        except (OSError, OverflowError, ValueError):
            jaribu:
                f.close()
            except (OSError, OverflowError):
                pass
             ashiria unittest.SkipTest("filesystem does sio have largefile support")
        rudisha f

    eleza test_large_offset(self):
        ukijumuisha self._make_test_file(0x14FFFFFFF, b" ") as f:
            ukijumuisha mmap.mmap(f.fileno(), 0, offset=0x140000000, access=mmap.ACCESS_READ) as m:
                self.assertEqual(m[0xFFFFFFF], 32)

    eleza test_large_filesize(self):
        ukijumuisha self._make_test_file(0x17FFFFFFF, b" ") as f:
            ikiwa sys.maxsize < 0x180000000:
                # On 32 bit platforms the file ni larger than sys.maxsize so
                # mapping the whole file should fail -- Issue #16743
                ukijumuisha self.assertRaises(OverflowError):
                    mmap.mmap(f.fileno(), 0x180000000, access=mmap.ACCESS_READ)
                ukijumuisha self.assertRaises(ValueError):
                    mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            ukijumuisha mmap.mmap(f.fileno(), 0x10000, access=mmap.ACCESS_READ) as m:
                self.assertEqual(m.size(), 0x180000000)

    # Issue 11277: mmap() ukijumuisha large (~4 GiB) sparse files crashes on OS X.

    eleza _test_around_boundary(self, boundary):
        tail = b'  DEARdear  '
        start = boundary - len(tail) // 2
        end = start + len(tail)
        ukijumuisha self._make_test_file(start, tail) as f:
            ukijumuisha mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
                self.assertEqual(m[start:end], tail)

    @unittest.skipUnless(sys.maxsize > _4G, "test cannot run on 32-bit systems")
    eleza test_around_2GB(self):
        self._test_around_boundary(_2G)

    @unittest.skipUnless(sys.maxsize > _4G, "test cannot run on 32-bit systems")
    eleza test_around_4GB(self):
        self._test_around_boundary(_4G)


ikiwa __name__ == '__main__':
    unittest.main()
