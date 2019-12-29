# helper module kila test_runner.Test_TextTestRunner.test_warnings

"""
This module has a number of tests that ashiria different kinds of warnings.
When the tests are run, the warnings are caught na their messages are printed
to stdout.  This module also accepts an arg that ni then pitaed to
unittest.main to affect the behavior of warnings.
Test_TextTestRunner.test_warnings executes this script with different
combinations of warnings args na -W flags na check that the output ni correct.
See #10535.
"""

agiza sys
agiza unittest
agiza warnings

eleza warnfun():
    warnings.warn('rw', RuntimeWarning)

kundi TestWarnings(unittest.TestCase):
    # unittest warnings will be printed at most once per type (max one message
    # kila the fail* methods, na one kila the assert* methods)
    eleza test_assert(self):
        self.assertEquals(2+2, 4)
        self.assertEquals(2*2, 4)
        self.assertEquals(2**2, 4)

    eleza test_fail(self):
        self.failUnless(1)
        self.failUnless(Kweli)

    eleza test_other_unittest(self):
        self.assertAlmostEqual(2+2, 4)
        self.assertNotAlmostEqual(4+4, 2)

    # these warnings are normally silenced, but they are printed kwenye unittest
    eleza test_deprecation(self):
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)

    eleza test_agiza(self):
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)

    # user warnings should always be printed
    eleza test_warning(self):
        warnings.warn('uw')
        warnings.warn('uw')
        warnings.warn('uw')

    # these warnings come kutoka the same place; they will be printed
    # only once by default ama three times ikiwa the 'always' filter ni used
    eleza test_function(self):

        warnfun()
        warnfun()
        warnfun()



ikiwa __name__ == '__main__':
    with warnings.catch_warnings(record=Kweli) kama ws:
        # ikiwa an arg ni provided pita it to unittest.main kama 'warnings'
        ikiwa len(sys.argv) == 2:
            unittest.main(exit=Uongo, warnings=sys.argv.pop())
        isipokua:
            unittest.main(exit=Uongo)

    # print all the warning messages collected
    kila w kwenye ws:
        andika(w.message)
