kutoka test.support agiza findfile, TESTFN, unlink
agiza array
agiza io
kutoka unittest agiza mock
agiza pickle


kundi UnseekableIO(io.FileIO):
    eleza tell(self):
        ashiria io.UnsupportedOperation

    eleza seek(self, *args, **kwargs):
        ashiria io.UnsupportedOperation


kundi AudioTests:
    close_fd = Uongo

    eleza setUp(self):
        self.f = self.fout = Tupu

    eleza tearDown(self):
        ikiwa self.f ni sio Tupu:
            self.f.close()
        ikiwa self.fout ni sio Tupu:
            self.fout.close()
        unlink(TESTFN)

    eleza check_params(self, f, nchannels, sampwidth, framerate, nframes,
                     comptype, compname):
        self.assertEqual(f.getnchannels(), nchannels)
        self.assertEqual(f.getsampwidth(), sampwidth)
        self.assertEqual(f.getframerate(), framerate)
        self.assertEqual(f.getnframes(), nframes)
        self.assertEqual(f.getcomptype(), comptype)
        self.assertEqual(f.getcompname(), compname)

        params = f.getparams()
        self.assertEqual(params,
                (nchannels, sampwidth, framerate, nframes, comptype, compname))
        self.assertEqual(params.nchannels, nchannels)
        self.assertEqual(params.sampwidth, sampwidth)
        self.assertEqual(params.framerate, framerate)
        self.assertEqual(params.nframes, nframes)
        self.assertEqual(params.comptype, comptype)
        self.assertEqual(params.compname, compname)

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            dump = pickle.dumps(params, proto)
            self.assertEqual(pickle.loads(dump), params)


kundi AudioMiscTests(AudioTests):

    eleza test_openfp_deprecated(self):
        arg = "arg"
        mode = "mode"
        ukijumuisha mock.patch(f"{self.module.__name__}.open") kama mock_open, \
             self.assertWarns(DeprecationWarning):
            self.module.openfp(arg, mode=mode)
            mock_open.assert_called_with(arg, mode=mode)


kundi AudioWriteTests(AudioTests):

    eleza create_file(self, testfile):
        f = self.fout = self.module.open(testfile, 'wb')
        f.setnchannels(self.nchannels)
        f.setsampwidth(self.sampwidth)
        f.setframerate(self.framerate)
        f.setcomptype(self.comptype, self.compname)
        rudisha f

    eleza check_file(self, testfile, nframes, frames):
        ukijumuisha self.module.open(testfile, 'rb') kama f:
            self.assertEqual(f.getnchannels(), self.nchannels)
            self.assertEqual(f.getsampwidth(), self.sampwidth)
            self.assertEqual(f.getframerate(), self.framerate)
            self.assertEqual(f.getnframes(), nframes)
            self.assertEqual(f.readframes(nframes), frames)

    eleza test_write_params(self):
        f = self.create_file(TESTFN)
        f.setnframes(self.nframes)
        f.writeframes(self.frames)
        self.check_params(f, self.nchannels, self.sampwidth, self.framerate,
                          self.nframes, self.comptype, self.compname)
        f.close()

    eleza test_write_context_manager_calls_close(self):
        # Close checks kila a minimum header na will ashiria an error
        # ikiwa it ni sio set, so this proves that close ni called.
        ukijumuisha self.assertRaises(self.module.Error):
            ukijumuisha self.module.open(TESTFN, 'wb'):
                pita
        ukijumuisha self.assertRaises(self.module.Error):
            ukijumuisha open(TESTFN, 'wb') kama testfile:
                ukijumuisha self.module.open(testfile):
                    pita

    eleza test_context_manager_with_open_file(self):
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            ukijumuisha self.module.open(testfile) kama f:
                f.setnchannels(self.nchannels)
                f.setsampwidth(self.sampwidth)
                f.setframerate(self.framerate)
                f.setcomptype(self.comptype, self.compname)
            self.assertEqual(testfile.closed, self.close_fd)
        ukijumuisha open(TESTFN, 'rb') kama testfile:
            ukijumuisha self.module.open(testfile) kama f:
                self.assertUongo(f.getfp().closed)
                params = f.getparams()
                self.assertEqual(params.nchannels, self.nchannels)
                self.assertEqual(params.sampwidth, self.sampwidth)
                self.assertEqual(params.framerate, self.framerate)
            ikiwa sio self.close_fd:
                self.assertIsTupu(f.getfp())
            self.assertEqual(testfile.closed, self.close_fd)

    eleza test_context_manager_with_filename(self):
        # If the file doesn't get closed, this test won't fail, but it will
        # produce a resource leak warning.
        ukijumuisha self.module.open(TESTFN, 'wb') kama f:
            f.setnchannels(self.nchannels)
            f.setsampwidth(self.sampwidth)
            f.setframerate(self.framerate)
            f.setcomptype(self.comptype, self.compname)
        ukijumuisha self.module.open(TESTFN) kama f:
            self.assertUongo(f.getfp().closed)
            params = f.getparams()
            self.assertEqual(params.nchannels, self.nchannels)
            self.assertEqual(params.sampwidth, self.sampwidth)
            self.assertEqual(params.framerate, self.framerate)
        ikiwa sio self.close_fd:
            self.assertIsTupu(f.getfp())

    eleza test_write(self):
        f = self.create_file(TESTFN)
        f.setnframes(self.nframes)
        f.writeframes(self.frames)
        f.close()

        self.check_file(TESTFN, self.nframes, self.frames)

    eleza test_write_bytearray(self):
        f = self.create_file(TESTFN)
        f.setnframes(self.nframes)
        f.writeframes(bytearray(self.frames))
        f.close()

        self.check_file(TESTFN, self.nframes, self.frames)

    eleza test_write_array(self):
        f = self.create_file(TESTFN)
        f.setnframes(self.nframes)
        f.writeframes(array.array('h', self.frames))
        f.close()

        self.check_file(TESTFN, self.nframes, self.frames)

    eleza test_write_memoryview(self):
        f = self.create_file(TESTFN)
        f.setnframes(self.nframes)
        f.writeframes(memoryview(self.frames))
        f.close()

        self.check_file(TESTFN, self.nframes, self.frames)

    eleza test_incompleted_write(self):
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            f = self.create_file(testfile)
            f.setnframes(self.nframes + 1)
            f.writeframes(self.frames)
            f.close()

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            self.check_file(testfile, self.nframes, self.frames)

    eleza test_multiple_writes(self):
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            f = self.create_file(testfile)
            f.setnframes(self.nframes)
            framesize = self.nchannels * self.sampwidth
            f.writeframes(self.frames[:-framesize])
            f.writeframes(self.frames[-framesize:])
            f.close()

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            self.check_file(testfile, self.nframes, self.frames)

    eleza test_overflowed_write(self):
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            f = self.create_file(testfile)
            f.setnframes(self.nframes - 1)
            f.writeframes(self.frames)
            f.close()

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            self.check_file(testfile, self.nframes, self.frames)

    eleza test_unseekable_read(self):
        ukijumuisha self.create_file(TESTFN) kama f:
            f.setnframes(self.nframes)
            f.writeframes(self.frames)

        ukijumuisha UnseekableIO(TESTFN, 'rb') kama testfile:
            self.check_file(testfile, self.nframes, self.frames)

    eleza test_unseekable_write(self):
        ukijumuisha UnseekableIO(TESTFN, 'wb') kama testfile:
            ukijumuisha self.create_file(testfile) kama f:
                f.setnframes(self.nframes)
                f.writeframes(self.frames)

        self.check_file(TESTFN, self.nframes, self.frames)

    eleza test_unseekable_incompleted_write(self):
        ukijumuisha UnseekableIO(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            f = self.create_file(testfile)
            f.setnframes(self.nframes + 1)
            jaribu:
                f.writeframes(self.frames)
            tatizo OSError:
                pita
            jaribu:
                f.close()
            tatizo OSError:
                pita

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            self.check_file(testfile, self.nframes + 1, self.frames)

    eleza test_unseekable_overflowed_write(self):
        ukijumuisha UnseekableIO(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            f = self.create_file(testfile)
            f.setnframes(self.nframes - 1)
            jaribu:
                f.writeframes(self.frames)
            tatizo OSError:
                pita
            jaribu:
                f.close()
            tatizo OSError:
                pita

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            framesize = self.nchannels * self.sampwidth
            self.check_file(testfile, self.nframes - 1, self.frames[:-framesize])


kundi AudioTestsWithSourceFile(AudioTests):

    @classmethod
    eleza setUpClass(cls):
        cls.sndfilepath = findfile(cls.sndfilename, subdir='audiodata')

    eleza test_read_params(self):
        f = self.f = self.module.open(self.sndfilepath)
        #self.assertEqual(f.getfp().name, self.sndfilepath)
        self.check_params(f, self.nchannels, self.sampwidth, self.framerate,
                          self.sndfilenframes, self.comptype, self.compname)

    eleza test_close(self):
        ukijumuisha open(self.sndfilepath, 'rb') kama testfile:
            f = self.f = self.module.open(testfile)
            self.assertUongo(testfile.closed)
            f.close()
            self.assertEqual(testfile.closed, self.close_fd)
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            fout = self.fout = self.module.open(testfile, 'wb')
            self.assertUongo(testfile.closed)
            ukijumuisha self.assertRaises(self.module.Error):
                fout.close()
            self.assertEqual(testfile.closed, self.close_fd)
            fout.close() # do nothing

    eleza test_read(self):
        framesize = self.nchannels * self.sampwidth
        chunk1 = self.frames[:2 * framesize]
        chunk2 = self.frames[2 * framesize: 4 * framesize]
        f = self.f = self.module.open(self.sndfilepath)
        self.assertEqual(f.readframes(0), b'')
        self.assertEqual(f.tell(), 0)
        self.assertEqual(f.readframes(2), chunk1)
        f.rewind()
        pos0 = f.tell()
        self.assertEqual(pos0, 0)
        self.assertEqual(f.readframes(2), chunk1)
        pos2 = f.tell()
        self.assertEqual(pos2, 2)
        self.assertEqual(f.readframes(2), chunk2)
        f.setpos(pos2)
        self.assertEqual(f.readframes(2), chunk2)
        f.setpos(pos0)
        self.assertEqual(f.readframes(2), chunk1)
        ukijumuisha self.assertRaises(self.module.Error):
            f.setpos(-1)
        ukijumuisha self.assertRaises(self.module.Error):
            f.setpos(f.getnframes() + 1)

    eleza test_copy(self):
        f = self.f = self.module.open(self.sndfilepath)
        fout = self.fout = self.module.open(TESTFN, 'wb')
        fout.setparams(f.getparams())
        i = 0
        n = f.getnframes()
        wakati n > 0:
            i += 1
            fout.writeframes(f.readframes(i))
            n -= i
        fout.close()
        fout = self.fout = self.module.open(TESTFN, 'rb')
        f.rewind()
        self.assertEqual(f.getparams(), fout.getparams())
        self.assertEqual(f.readframes(f.getnframes()),
                         fout.readframes(fout.getnframes()))

    eleza test_read_not_kutoka_start(self):
        ukijumuisha open(TESTFN, 'wb') kama testfile:
            testfile.write(b'ababagalamaga')
            ukijumuisha open(self.sndfilepath, 'rb') kama f:
                testfile.write(f.read())

        ukijumuisha open(TESTFN, 'rb') kama testfile:
            self.assertEqual(testfile.read(13), b'ababagalamaga')
            ukijumuisha self.module.open(testfile, 'rb') kama f:
                self.assertEqual(f.getnchannels(), self.nchannels)
                self.assertEqual(f.getsampwidth(), self.sampwidth)
                self.assertEqual(f.getframerate(), self.framerate)
                self.assertEqual(f.getnframes(), self.sndfilenframes)
                self.assertEqual(f.readframes(self.nframes), self.frames)
