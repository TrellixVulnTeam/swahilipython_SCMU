# helper module for test_runner.Test_TextTestRunner.test_warnings

"""
This module has a number of tests that raise different kinds of warnings.
When the tests are run, the warnings are caught and their messages are printed
to stdout.  This module also accepts an arg that is then passed to
unittest.main to affect the behavior of warnings.
Test_TextTestRunner.test_warnings executes this script with different
combinations of warnings args and -W flags and check that the output is correct.
See #10535.
"""

agiza sys
agiza unittest
agiza warnings

eleza warnfun():
    warnings.warn('rw', RuntimeWarning)

kundi TestWarnings(unittest.TestCase):
    # unittest warnings will be printed at most once per type (max one message
    # for the fail* methods, and one for the assert* methods)
    eleza test_assert(self):
        self.assertEquals(2+2, 4)
        self.assertEquals(2*2, 4)
        self.assertEquals(2**2, 4)

    eleza test_fail(self):
        self.failUnless(1)
        self.failUnless(True)

    eleza test_other_unittest(self):
        self.assertAlmostEqual(2+2, 4)
        self.assertNotAlmostEqual(4+4, 2)

    # these warnings are normally silenced, but they are printed in unittest
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
    # only once by default or three times ikiwa the 'always' filter is used
    eleza test_function(self):

        warnfun()
        warnfun()
        warnfun()



ikiwa __name__ == '__main__':
    with warnings.catch_warnings(record=True) as ws:
        # ikiwa an arg is provided pass it to unittest.main as 'warnings'
        ikiwa len(sys.argv) == 2:
            unittest.main(exit=False, warnings=sys.argv.pop())
        else:
            unittest.main(exit=False)

    # print all the warning messages collected
    for w in ws:
        andika(w.message)
