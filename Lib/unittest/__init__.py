"""
Python unit testing framework, based on Erich Gamma's JUnit na Kent Beck's
Smalltalk testing framework (used ukijumuisha permission).

This module contains the core framework classes that form the basis of
specific test cases na suites (TestCase, TestSuite etc.), na also a
text-based utility kundi kila running the tests na reporting the results
 (TextTestRunner).

Simple usage:

    agiza unittest

    kundi IntegerArithmeticTestCase(unittest.TestCase):
        eleza testAdd(self):  # test method names begin ukijumuisha 'test'
            self.assertEqual((1 + 2), 3)
            self.assertEqual(0 + 1, 1)
        eleza testMultiply(self):
            self.assertEqual((0 * 10), 0)
            self.assertEqual((5 * 8), 40)

    ikiwa __name__ == '__main__':
        unittest.main()

Further information ni available kwenye the bundled documentation, na from

  http://docs.python.org/library/unittest.html

Copyright (c) 1999-2003 Steve Purcell
Copyright (c) 2003-2010 Python Software Foundation
This module ni free software, na you may redistribute it and/or modify
it under the same terms as Python itself, so long as this copyright message
and disclaimer are retained kwenye their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__all__ = ['TestResult', 'TestCase', 'IsolatedAsyncioTestCase', 'TestSuite',
           'TextTestRunner', 'TestLoader', 'FunctionTestCase', 'main',
           'defaultTestLoader', 'SkipTest', 'skip', 'skipIf', 'skipUnless',
           'expectedFailure', 'TextTestResult', 'installHandler',
           'registerResult', 'removeResult', 'removeHandler',
           'addModuleCleanup']

# Expose obsolete functions kila backwards compatibility
__all__.extend(['getTestCaseNames', 'makeSuite', 'findTestCases'])

__unittest = Kweli

kutoka .result agiza TestResult
kutoka .async_case agiza IsolatedAsyncioTestCase
kutoka .case agiza (addModuleCleanup, TestCase, FunctionTestCase, SkipTest, skip,
                   skipIf, skipUnless, expectedFailure)
kutoka .suite agiza BaseTestSuite, TestSuite
kutoka .loader agiza (TestLoader, defaultTestLoader, makeSuite, getTestCaseNames,
                     findTestCases)
kutoka .main agiza TestProgram, main
kutoka .runner agiza TextTestRunner, TextTestResult
kutoka .signals agiza installHandler, registerResult, removeResult, removeHandler

# deprecated
_TextTestResult = TextTestResult

# There are no tests here, so don't try to run anything discovered from
# introspecting the symbols (e.g. FunctionTestCase). Instead, all our
# tests come kutoka within unittest.test.
eleza load_tests(loader, tests, pattern):
    agiza os.path
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    rudisha loader.discover(start_dir=this_dir, pattern=pattern)
