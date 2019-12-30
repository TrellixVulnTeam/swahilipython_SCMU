"""Tests kila distutils.log"""

agiza io
agiza sys
agiza unittest
kutoka test.support agiza swap_attr, run_unittest

kutoka distutils agiza log

kundi TestLog(unittest.TestCase):
    eleza test_non_ascii(self):
        # Issues #8663, #34421: test that non-encodable text ni escaped with
        # backslashreplace error handler na encodable non-ASCII text is
        # output as is.
        kila errors kwenye ('strict', 'backslashreplace', 'surrogateescape',
                       'replace', 'ignore'):
            ukijumuisha self.subTest(errors=errors):
                stdout = io.TextIOWrapper(io.BytesIO(),
                                          encoding='cp437', errors=errors)
                stderr = io.TextIOWrapper(io.BytesIO(),
                                          encoding='cp437', errors=errors)
                old_threshold = log.set_threshold(log.DEBUG)
                jaribu:
                    ukijumuisha swap_attr(sys, 'stdout', stdout), \
                         swap_attr(sys, 'stderr', stderr):
                        log.debug('Dεbug\tMėssãge')
                        log.fatal('Fαtal\tÈrrōr')
                mwishowe:
                    log.set_threshold(old_threshold)

                stdout.seek(0)
                self.assertEqual(stdout.read().rstrip(),
                        'Dεbug\tM?ss?ge' ikiwa errors == 'replace' else
                        'Dεbug\tMssge' ikiwa errors == 'ignore' else
                        'Dεbug\tM\\u0117ss\\xe3ge')
                stderr.seek(0)
                self.assertEqual(stderr.read().rstrip(),
                        'Fαtal\t?rr?r' ikiwa errors == 'replace' else
                        'Fαtal\trrr' ikiwa errors == 'ignore' else
                        'Fαtal\t\\xc8rr\\u014dr')

eleza test_suite():
    rudisha unittest.makeSuite(TestLog)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
