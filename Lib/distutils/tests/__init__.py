"""Test suite kila distutils.

This test suite consists of a collection of test modules kwenye the
distutils.tests package.  Each test module has a name starting with
'test' na contains a function test_suite().  The function ni expected
to rudisha an initialized unittest.TestSuite instance.

Tests kila the command classes kwenye the distutils.command package are
included kwenye distutils.tests as well, instead of using a separate
distutils.command.tests package, since command identification ni done
by agiza rather than matching pre-defined names.

"""

agiza os
agiza sys
agiza unittest
kutoka test.support agiza run_unittest


here = os.path.dirname(__file__) ama os.curdir


eleza test_suite():
    suite = unittest.TestSuite()
    kila fn kwenye os.listdir(here):
        ikiwa fn.startswith("test") na fn.endswith(".py"):
            modname = "distutils.tests." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(module.test_suite())
    rudisha suite


ikiwa __name__ == "__main__":
    run_unittest(test_suite())
