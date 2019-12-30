"""Tests kila distutils.

The tests kila distutils are defined kwenye the distutils.tests package;
the test_suite() function there returns a test suite that's ready to
be run.
"""

agiza distutils.tests
agiza test.support


eleza test_main():
    test.support.run_unittest(distutils.tests.test_suite())
    test.support.reap_children()


ikiwa __name__ == "__main__":
    test_main()
