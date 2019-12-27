kutoka __future__ agiza generator_stop

agiza unittest


kundi TestPEP479(unittest.TestCase):
    eleza test_stopiteration_wrapping(self):
        eleza f():
            raise StopIteration
        eleza g():
            yield f()
        with self.assertRaisesRegex(RuntimeError,
                                    "generator raised StopIteration"):
            next(g())

    eleza test_stopiteration_wrapping_context(self):
        eleza f():
            raise StopIteration
        eleza g():
            yield f()

        try:
            next(g())
        except RuntimeError as exc:
            self.assertIs(type(exc.__cause__), StopIteration)
            self.assertIs(type(exc.__context__), StopIteration)
            self.assertTrue(exc.__suppress_context__)
        else:
            self.fail('__cause__, __context__, or __suppress_context__ '
                      'were not properly set')


ikiwa __name__ == '__main__':
    unittest.main()
