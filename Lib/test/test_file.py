agiza sys
agiza os
agiza unittest
kutoka array agiza array
kutoka weakref agiza proxy

agiza io
agiza _pyio kama pyio

kutoka test.support agiza TESTFN
kutoka test agiza support
kutoka collections agiza UserList

kundi AutoFileTests:
    # file tests kila which a test file ni automatically set up

    eleza setUp(self):
        self.f = self.open(TESTFN, 'wb')

    eleza tearDown(self):
        ikiwa self.f:
            self.f.close()
        support.unlink(TESTFN)

    eleza testWeakRefs(self):
        # verify weak references
        p = proxy(self.f)
        p.write(b'teststring')
        self.assertEqual(self.f.tell(), p.tell())
        self.f.close()
        self.f = Tupu
        self.assertRaises(ReferenceError, getattr, p, 'tell')

    eleza testAttributes(self):
        # verify expected attributes exist
        f = self.f
        f.name     # merely shouldn't blow up
        f.mode     # ditto
        f.closed   # ditto

    eleza testReadinto(self):
        # verify readinto
        self.f.write(b'12')
        self.f.close()
        a = array('b', b'x'*10)
        self.f = self.open(TESTFN, 'rb')
        n = self.f.readinto(a)
        self.assertEqual(b'12', a.tobytes()[:n])

    eleza testReadinto_text(self):
        # verify readinto refuses text files
        a = array('b', b'x'*10)
        self.f.close()
        self.f = self.open(TESTFN, 'r')
        ikiwa hasattr(self.f, "readinto"):
            self.assertRaises(TypeError, self.f.readinto, a)

    eleza testWritelinesUserList(self):
        # verify writelines ukijumuisha instance sequence
        l = UserList([b'1', b'2'])
        self.f.writelines(l)
        self.f.close()
        self.f = self.open(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'12')

    eleza testWritelinesIntegers(self):
        # verify writelines ukijumuisha integers
        self.assertRaises(TypeError, self.f.writelines, [1, 2, 3])

    eleza testWritelinesIntegersUserList(self):
        # verify writelines ukijumuisha integers kwenye UserList
        l = UserList([1,2,3])
        self.assertRaises(TypeError, self.f.writelines, l)

    eleza testWritelinesNonString(self):
        # verify writelines ukijumuisha non-string object
        kundi NonString:
            pita

        self.assertRaises(TypeError, self.f.writelines,
                          [NonString(), NonString()])

    eleza testErrors(self):
        f = self.f
        self.assertEqual(f.name, TESTFN)
        self.assertUongo(f.isatty())
        self.assertUongo(f.closed)

        ikiwa hasattr(f, "readinto"):
            self.assertRaises((OSError, TypeError), f.readinto, "")
        f.close()
        self.assertKweli(f.closed)

    eleza testMethods(self):
        methods = [('fileno', ()),
                   ('flush', ()),
                   ('isatty', ()),
                   ('__next__', ()),
                   ('read', ()),
                   ('write', (b"",)),
                   ('readline', ()),
                   ('readlines', ()),
                   ('seek', (0,)),
                   ('tell', ()),
                   ('write', (b"",)),
                   ('writelines', ([],)),
                   ('__iter__', ()),
                   ]
        methods.append(('truncate', ()))

        # __exit__ should close the file
        self.f.__exit__(Tupu, Tupu, Tupu)
        self.assertKweli(self.f.closed)

        kila methodname, args kwenye methods:
            method = getattr(self.f, methodname)
            # should ashiria on closed file
            self.assertRaises(ValueError, method, *args)

        # file ni closed, __exit__ shouldn't do anything
        self.assertEqual(self.f.__exit__(Tupu, Tupu, Tupu), Tupu)
        # it must also rudisha Tupu ikiwa an exception was given
        jaribu:
            1/0
        tatizo:
            self.assertEqual(self.f.__exit__(*sys.exc_info()), Tupu)

    eleza testReadWhenWriting(self):
        self.assertRaises(OSError, self.f.read)

kundi CAutoFileTests(AutoFileTests, unittest.TestCase):
    open = io.open

kundi PyAutoFileTests(AutoFileTests, unittest.TestCase):
    open = staticmethod(pyio.open)


kundi OtherFileTests:

    eleza tearDown(self):
        support.unlink(TESTFN)

    eleza testModeStrings(self):
        # check invalid mode strings
        self.open(TESTFN, 'wb').close()
        kila mode kwenye ("", "aU", "wU+", "U+", "+U", "rU+"):
            jaribu:
                f = self.open(TESTFN, mode)
            tatizo ValueError:
                pita
            isipokua:
                f.close()
                self.fail('%r ni an invalid file mode' % mode)

    eleza testBadModeArgument(self):
        # verify that we get a sensible error message kila bad mode argument
        bad_mode = "qwerty"
        jaribu:
            f = self.open(TESTFN, bad_mode)
        tatizo ValueError kama msg:
            ikiwa msg.args[0] != 0:
                s = str(msg)
                ikiwa TESTFN kwenye s ama bad_mode haiko kwenye s:
                    self.fail("bad error message kila invalid mode: %s" % s)
            # ikiwa msg.args[0] == 0, we're probably on Windows where there may be
            # no obvious way to discover why open() failed.
        isipokua:
            f.close()
            self.fail("no error kila invalid mode: %s" % bad_mode)

    eleza _checkBufferSize(self, s):
        jaribu:
            f = self.open(TESTFN, 'wb', s)
            f.write(str(s).encode("ascii"))
            f.close()
            f.close()
            f = self.open(TESTFN, 'rb', s)
            d = int(f.read().decode("ascii"))
            f.close()
            f.close()
        tatizo OSError kama msg:
            self.fail('error setting buffer size %d: %s' % (s, str(msg)))
        self.assertEqual(d, s)

    eleza testSetBufferSize(self):
        # make sure that explicitly setting the buffer size doesn't cause
        # misbehaviour especially ukijumuisha repeated close() calls
        kila s kwenye (-1, 0, 512):
            ukijumuisha support.check_no_warnings(self,
                                           message='line buffering',
                                           category=RuntimeWarning):
                self._checkBufferSize(s)

        # test that attempts to use line buffering kwenye binary mode cause
        # a warning
        ukijumuisha self.assertWarnsRegex(RuntimeWarning, 'line buffering'):
            self._checkBufferSize(1)

    eleza testTruncateOnWindows(self):
        # SF bug <http://www.python.org/sf/801631>
        # "file.truncate fault on windows"

        f = self.open(TESTFN, 'wb')

        jaribu:
            f.write(b'12345678901')   # 11 bytes
            f.close()

            f = self.open(TESTFN,'rb+')
            data = f.read(5)
            ikiwa data != b'12345':
                self.fail("Read on file opened kila update failed %r" % data)
            ikiwa f.tell() != 5:
                self.fail("File pos after read wrong %d" % f.tell())

            f.truncate()
            ikiwa f.tell() != 5:
                self.fail("File pos after ftruncate wrong %d" % f.tell())

            f.close()
            size = os.path.getsize(TESTFN)
            ikiwa size != 5:
                self.fail("File size after ftruncate wrong %d" % size)
        mwishowe:
            f.close()

    eleza testIteration(self):
        # Test the complex interaction when mixing file-iteration na the
        # various read* methods.
        dataoffset = 16384
        filler = b"ham\n"
        assert sio dataoffset % len(filler), \
            "dataoffset must be multiple of len(filler)"
        nchunks = dataoffset // len(filler)
        testlines = [
            b"spam, spam na eggs\n",
            b"eggs, spam, ham na spam\n",
            b"saussages, spam, spam na eggs\n",
            b"spam, ham, spam na eggs\n",
            b"spam, spam, spam, spam, spam, ham, spam\n",
            b"wonderful spaaaaaam.\n"
        ]
        methods = [("readline", ()), ("read", ()), ("readlines", ()),
                   ("readinto", (array("b", b" "*100),))]

        # Prepare the testfile
        bag = self.open(TESTFN, "wb")
        bag.write(filler * nchunks)
        bag.writelines(testlines)
        bag.close()
        # Test kila appropriate errors mixing read* na iteration
        kila methodname, args kwenye methods:
            f = self.open(TESTFN, 'rb')
            self.assertEqual(next(f), filler)
            meth = getattr(f, methodname)
            meth(*args)  # This simply shouldn't fail
            f.close()

        # Test to see ikiwa harmless (by accident) mixing of read* na
        # iteration still works. This depends on the size of the internal
        # iteration buffer (currently 8192,) but we can test it kwenye a
        # flexible manner.  Each line kwenye the bag o' ham ni 4 bytes
        # ("h", "a", "m", "\n"), so 4096 lines of that should get us
        # exactly on the buffer boundary kila any power-of-2 buffersize
        # between 4 na 16384 (inclusive).
        f = self.open(TESTFN, 'rb')
        kila i kwenye range(nchunks):
            next(f)
        testline = testlines.pop(0)
        jaribu:
            line = f.readline()
        tatizo ValueError:
            self.fail("readline() after next() ukijumuisha supposedly empty "
                        "iteration-buffer failed anyway")
        ikiwa line != testline:
            self.fail("readline() after next() ukijumuisha empty buffer "
                        "failed. Got %r, expected %r" % (line, testline))
        testline = testlines.pop(0)
        buf = array("b", b"\x00" * len(testline))
        jaribu:
            f.readinto(buf)
        tatizo ValueError:
            self.fail("readinto() after next() ukijumuisha supposedly empty "
                        "iteration-buffer failed anyway")
        line = buf.tobytes()
        ikiwa line != testline:
            self.fail("readinto() after next() ukijumuisha empty buffer "
                        "failed. Got %r, expected %r" % (line, testline))

        testline = testlines.pop(0)
        jaribu:
            line = f.read(len(testline))
        tatizo ValueError:
            self.fail("read() after next() ukijumuisha supposedly empty "
                        "iteration-buffer failed anyway")
        ikiwa line != testline:
            self.fail("read() after next() ukijumuisha empty buffer "
                        "failed. Got %r, expected %r" % (line, testline))
        jaribu:
            lines = f.readlines()
        tatizo ValueError:
            self.fail("readlines() after next() ukijumuisha supposedly empty "
                        "iteration-buffer failed anyway")
        ikiwa lines != testlines:
            self.fail("readlines() after next() ukijumuisha empty buffer "
                        "failed. Got %r, expected %r" % (line, testline))
        f.close()

        # Reading after iteration hit EOF shouldn't hurt either
        f = self.open(TESTFN, 'rb')
        jaribu:
            kila line kwenye f:
                pita
            jaribu:
                f.readline()
                f.readinto(buf)
                f.read()
                f.readlines()
            tatizo ValueError:
                self.fail("read* failed after next() consumed file")
        mwishowe:
            f.close()

kundi COtherFileTests(OtherFileTests, unittest.TestCase):
    open = io.open

kundi PyOtherFileTests(OtherFileTests, unittest.TestCase):
    open = staticmethod(pyio.open)


ikiwa __name__ == '__main__':
    unittest.main()
