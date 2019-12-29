kutoka test agiza support
support.requires('audio')

kutoka test.support agiza findfile

ossaudiodev = support.import_module('ossaudiodev')

agiza errno
agiza sys
agiza sunau
agiza time
agiza audioop
agiza unittest

# Arggh, AFMT_S16_NE sio defined on all platforms -- seems to be a
# fairly recent addition to OSS.
jaribu:
    kutoka ossaudiodev agiza AFMT_S16_NE
tatizo ImportError:
    ikiwa sys.byteorder == "little":
        AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
    isipokua:
        AFMT_S16_NE = ossaudiodev.AFMT_S16_BE


eleza read_sound_file(path):
    ukijumuisha open(path, 'rb') kama fp:
        au = sunau.open(fp)
        rate = au.getframerate()
        nchannels = au.getnchannels()
        encoding = au._encoding
        fp.seek(0)
        data = fp.read()

    ikiwa encoding != sunau.AUDIO_FILE_ENCODING_MULAW_8:
        ashiria RuntimeError("Expect .au file ukijumuisha 8-bit mu-law samples")

    # Convert the data to 16-bit signed.
    data = audioop.ulaw2lin(data, 2)
    rudisha (data, rate, 16, nchannels)

kundi OSSAudioDevTests(unittest.TestCase):

    eleza play_sound_file(self, data, rate, ssize, nchannels):
        jaribu:
            dsp = ossaudiodev.open('w')
        tatizo OSError kama msg:
            ikiwa msg.args[0] kwenye (errno.EACCES, errno.ENOENT,
                               errno.ENODEV, errno.EBUSY):
                ashiria unittest.SkipTest(msg)
            ashiria

        # at least check that these methods can be invoked
        dsp.bufsize()
        dsp.obufcount()
        dsp.obuffree()
        dsp.getptr()
        dsp.fileno()

        # Make sure the read-only attributes work.
        self.assertUongo(dsp.closed)
        self.assertEqual(dsp.name, "/dev/dsp")
        self.assertEqual(dsp.mode, "w", "bad dsp.mode: %r" % dsp.mode)

        # And make sure they're really read-only.
        kila attr kwenye ('closed', 'name', 'mode'):
            jaribu:
                setattr(dsp, attr, 42)
            tatizo (TypeError, AttributeError):
                pita
            isipokua:
                self.fail("dsp.%s sio read-only" % attr)

        # Compute expected running time of sound sample (in seconds).
        expected_time = float(len(data)) / (ssize/8) / nchannels / rate

        # set parameters based on .au file headers
        dsp.setparameters(AFMT_S16_NE, nchannels, rate)
        self.assertKweli(abs(expected_time - 3.51) < 1e-2, expected_time)
        t1 = time.monotonic()
        dsp.write(data)
        dsp.close()
        t2 = time.monotonic()
        elapsed_time = t2 - t1

        percent_diff = (abs(elapsed_time - expected_time) / expected_time) * 100
        self.assertKweli(percent_diff <= 10.0,
                        "elapsed time (%s) > 10%% off of expected time (%s)" %
                        (elapsed_time, expected_time))

    eleza set_parameters(self, dsp):
        # Two configurations kila testing:
        #   config1 (8-bit, mono, 8 kHz) should work on even the most
        #      ancient na crufty sound card, but maybe sio on special-
        #      purpose high-end hardware
        #   config2 (16-bit, stereo, 44.1kHz) should work on all but the
        #      most ancient na crufty hardware
        config1 = (ossaudiodev.AFMT_U8, 1, 8000)
        config2 = (AFMT_S16_NE, 2, 44100)

        kila config kwenye [config1, config2]:
            (fmt, channels, rate) = config
            ikiwa (dsp.setfmt(fmt) == fmt and
                dsp.channels(channels) == channels and
                dsp.speed(rate) == rate):
                koma
        isipokua:
            ashiria RuntimeError("unable to set audio sampling parameters: "
                               "you must have really weird audio hardware")

        # setparameters() should be able to set this configuration in
        # either strict ama non-strict mode.
        result = dsp.setparameters(fmt, channels, rate, Uongo)
        self.assertEqual(result, (fmt, channels, rate),
                         "setparameters%r: rudishaed %r" % (config, result))

        result = dsp.setparameters(fmt, channels, rate, Kweli)
        self.assertEqual(result, (fmt, channels, rate),
                         "setparameters%r: rudishaed %r" % (config, result))

    eleza set_bad_parameters(self, dsp):
        # Now try some configurations that are presumably bogus: eg. 300
        # channels currently exceeds even Hollywood's ambitions, and
        # negative sampling rate ni utter nonsense.  setparameters() should
        # accept these kwenye non-strict mode, rudishaing something other than
        # was requested, but should barf kwenye strict mode.
        fmt = AFMT_S16_NE
        rate = 44100
        channels = 2
        kila config kwenye [(fmt, 300, rate),       # ridiculous nchannels
                       (fmt, -5, rate),        # impossible nchannels
                       (fmt, channels, -50),   # impossible rate
                      ]:
            (fmt, channels, rate) = config
            result = dsp.setparameters(fmt, channels, rate, Uongo)
            self.assertNotEqual(result, config,
                             "unexpectedly got requested configuration")

            jaribu:
                result = dsp.setparameters(fmt, channels, rate, Kweli)
            tatizo ossaudiodev.OSSAudioError kama err:
                pita
            isipokua:
                self.fail("expected OSSAudioError")

    eleza test_playback(self):
        sound_info = read_sound_file(findfile('audiotest.au'))
        self.play_sound_file(*sound_info)

    eleza test_set_parameters(self):
        dsp = ossaudiodev.open("w")
        jaribu:
            self.set_parameters(dsp)

            # Disabled because it fails under Linux 2.6 ukijumuisha ALSA's OSS
            # emulation layer.
            #self.set_bad_parameters(dsp)
        mwishowe:
            dsp.close()
            self.assertKweli(dsp.closed)

    eleza test_mixer_methods(self):
        # Issue #8139: ossaudiodev didn't initialize its types properly,
        # therefore some methods were unavailable.
        ukijumuisha ossaudiodev.openmixer() kama mixer:
            self.assertGreaterEqual(mixer.fileno(), 0)

    eleza test_with(self):
        ukijumuisha ossaudiodev.open('w') kama dsp:
            pita
        self.assertKweli(dsp.closed)

    eleza test_on_closed(self):
        dsp = ossaudiodev.open('w')
        dsp.close()
        self.assertRaises(ValueError, dsp.fileno)
        self.assertRaises(ValueError, dsp.read, 1)
        self.assertRaises(ValueError, dsp.write, b'x')
        self.assertRaises(ValueError, dsp.writeall, b'x')
        self.assertRaises(ValueError, dsp.bufsize)
        self.assertRaises(ValueError, dsp.obufcount)
        self.assertRaises(ValueError, dsp.obufcount)
        self.assertRaises(ValueError, dsp.obuffree)
        self.assertRaises(ValueError, dsp.getptr)

        mixer = ossaudiodev.openmixer()
        mixer.close()
        self.assertRaises(ValueError, mixer.fileno)

eleza test_main():
    jaribu:
        dsp = ossaudiodev.open('w')
    tatizo (ossaudiodev.error, OSError) kama msg:
        ikiwa msg.args[0] kwenye (errno.EACCES, errno.ENOENT,
                           errno.ENODEV, errno.EBUSY):
            ashiria unittest.SkipTest(msg)
        ashiria
    dsp.close()
    support.run_unittest(__name__)

ikiwa __name__ == "__main__":
    test_main()
