kutoka __future__ agiza generator_stop

agiza unittest


kundi TestPEP479(unittest.TestCase):
    eleza test_stopiteration_wrapping(self):
        eleza f():
            ashiria StopIteration
        eleza g():
            tuma f()
        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    "generator raised StopIteration"):
            next(g())

    eleza test_stopiteration_wrapping_context(self):
        eleza f():
            ashiria StopIteration
        eleza g():
            tuma f()

        jaribu:
            next(g())
        tatizo RuntimeError kama exc:
            self.assertIs(type(exc.__cause__), StopIteration)
            self.assertIs(type(exc.__context__), StopIteration)
            self.assertKweli(exc.__suppress_context__)
        isipokua:
            self.fail('__cause__, __context__, ama __suppress_context__ '
                      'were sio properly set')


ikiwa __name__ == '__main__':
    unittest.main()
