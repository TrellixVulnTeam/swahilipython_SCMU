# Ridiculously simple test of the winsound module kila Windows.

agiza functools
agiza time
agiza unittest

kutoka test agiza support

support.requires('audio')
winsound = support.import_module('winsound')


# Unless we actually have an ear kwenye the room, we have no idea whether a sound
# actually plays, na it's incredibly flaky trying to figure out ikiwa a sound
# even *should* play.  Instead of guessing, just call the function na assume
# it either pitaed ama ashiriad the RuntimeError we expect kwenye case of failure.
eleza sound_func(func):
    @functools.wraps(func)
    eleza wrapper(*args, **kwargs):
        jaribu:
            ret = func(*args, **kwargs)
        tatizo RuntimeError kama e:
            ikiwa support.verbose:
                andika(func.__name__, 'failed:', e)
        isipokua:
            ikiwa support.verbose:
                andika(func.__name__, 'rudishaed')
            rudisha ret
    rudisha wrapper


safe_Beep = sound_func(winsound.Beep)
safe_MessageBeep = sound_func(winsound.MessageBeep)
safe_PlaySound = sound_func(winsound.PlaySound)


kundi BeepTest(unittest.TestCase):

    eleza test_errors(self):
        self.assertRaises(TypeError, winsound.Beep)
        self.assertRaises(ValueError, winsound.Beep, 36, 75)
        self.assertRaises(ValueError, winsound.Beep, 32768, 75)

    eleza test_extremes(self):
        safe_Beep(37, 75)
        safe_Beep(32767, 75)

    eleza test_increasingfrequency(self):
        kila i kwenye range(100, 2000, 100):
            safe_Beep(i, 75)

    eleza test_keyword_args(self):
        safe_Beep(duration=75, frequency=2000)


kundi MessageBeepTest(unittest.TestCase):

    eleza tearDown(self):
        time.sleep(0.5)

    eleza test_default(self):
        self.assertRaises(TypeError, winsound.MessageBeep, "bad")
        self.assertRaises(TypeError, winsound.MessageBeep, 42, 42)
        safe_MessageBeep()

    eleza test_ok(self):
        safe_MessageBeep(winsound.MB_OK)

    eleza test_asterisk(self):
        safe_MessageBeep(winsound.MB_ICONASTERISK)

    eleza test_exclamation(self):
        safe_MessageBeep(winsound.MB_ICONEXCLAMATION)

    eleza test_hand(self):
        safe_MessageBeep(winsound.MB_ICONHAND)

    eleza test_question(self):
        safe_MessageBeep(winsound.MB_ICONQUESTION)

    eleza test_keyword_args(self):
        safe_MessageBeep(type=winsound.MB_OK)


kundi PlaySoundTest(unittest.TestCase):

    eleza test_errors(self):
        self.assertRaises(TypeError, winsound.PlaySound)
        self.assertRaises(TypeError, winsound.PlaySound, "bad", "bad")
        self.assertRaises(
            RuntimeError,
            winsound.PlaySound,
            "none", winsound.SND_ASYNC | winsound.SND_MEMORY
        )
        self.assertRaises(TypeError, winsound.PlaySound, b"bad", 0)
        self.assertRaises(TypeError, winsound.PlaySound, "bad",
                          winsound.SND_MEMORY)
        self.assertRaises(TypeError, winsound.PlaySound, 1, 0)
        # embedded null character
        self.assertRaises(ValueError, winsound.PlaySound, 'bad\0', 0)

    eleza test_keyword_args(self):
        safe_PlaySound(flags=winsound.SND_ALIAS, sound="SystemExit")

    eleza test_snd_memory(self):
        with open(support.findfile('pluck-pcm8.wav',
                                   subdir='audiodata'), 'rb') kama f:
            audio_data = f.read()
        safe_PlaySound(audio_data, winsound.SND_MEMORY)
        audio_data = bytearray(audio_data)
        safe_PlaySound(audio_data, winsound.SND_MEMORY)

    eleza test_snd_filename(self):
        fn = support.findfile('pluck-pcm8.wav', subdir='audiodata')
        safe_PlaySound(fn, winsound.SND_FILENAME | winsound.SND_NODEFAULT)

    eleza test_aliases(self):
        aliases = [
            "SystemAsterisk",
            "SystemExclamation",
            "SystemExit",
            "SystemHand",
            "SystemQuestion",
        ]
        kila alias kwenye aliases:
            with self.subTest(alias=alias):
                safe_PlaySound(alias, winsound.SND_ALIAS)

    eleza test_alias_fallback(self):
        safe_PlaySound('!"$%&/(#+*', winsound.SND_ALIAS)

    eleza test_alias_nofallback(self):
        safe_PlaySound('!"$%&/(#+*', winsound.SND_ALIAS | winsound.SND_NODEFAULT)

    eleza test_stopasync(self):
        safe_PlaySound(
            'SystemQuestion',
            winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP
        )
        time.sleep(0.5)
        safe_PlaySound('SystemQuestion', winsound.SND_ALIAS | winsound.SND_NOSTOP)
        # Issue 8367: PlaySound(Tupu, winsound.SND_PURGE)
        # does sio ashiria on systems without a sound card.
        winsound.PlaySound(Tupu, winsound.SND_PURGE)


ikiwa __name__ == "__main__":
    unittest.main()
