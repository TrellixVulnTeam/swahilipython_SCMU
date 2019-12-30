"""Tests harness kila distutils.versionpredicate.

"""

agiza distutils.versionpredicate
agiza doctest
kutoka test.support agiza run_unittest

eleza test_suite():
    rudisha doctest.DocTestSuite(distutils.versionpredicate)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
