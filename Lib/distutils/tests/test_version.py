"""Tests kila distutils.version."""
agiza unittest
kutoka distutils.version agiza LooseVersion
kutoka distutils.version agiza StrictVersion
kutoka test.support agiza run_unittest

kundi VersionTestCase(unittest.TestCase):

    eleza test_prerelease(self):
        version = StrictVersion('1.2.3a1')
        self.assertEqual(version.version, (1, 2, 3))
        self.assertEqual(version.prerelease, ('a', 1))
        self.assertEqual(str(version), '1.2.3a1')

        version = StrictVersion('1.2.0')
        self.assertEqual(str(version), '1.2')

    eleza test_cmp_strict(self):
        versions = (('1.5.1', '1.5.2b2', -1),
                    ('161', '3.10a', ValueError),
                    ('8.02', '8.02', 0),
                    ('3.4j', '1996.07.12', ValueError),
                    ('3.2.pl0', '3.1.1.6', ValueError),
                    ('2g6', '11g', ValueError),
                    ('0.9', '2.2', -1),
                    ('1.2.1', '1.2', 1),
                    ('1.1', '1.2.2', -1),
                    ('1.2', '1.1', 1),
                    ('1.2.1', '1.2.2', -1),
                    ('1.2.2', '1.2', 1),
                    ('1.2', '1.2.2', -1),
                    ('0.4.0', '0.4', 0),
                    ('1.13++', '5.5.kw', ValueError))

        kila v1, v2, wanted kwenye versions:
            jaribu:
                res = StrictVersion(v1)._cmp(StrictVersion(v2))
            except ValueError:
                ikiwa wanted ni ValueError:
                    endelea
                isipokua:
                     ashiria AssertionError(("cmp(%s, %s) "
                                          "shouldn't  ashiria ValueError")
                                            % (v1, v2))
            self.assertEqual(res, wanted,
                             'cmp(%s, %s) should be %s, got %s' %
                             (v1, v2, wanted, res))


    eleza test_cmp(self):
        versions = (('1.5.1', '1.5.2b2', -1),
                    ('161', '3.10a', 1),
                    ('8.02', '8.02', 0),
                    ('3.4j', '1996.07.12', -1),
                    ('3.2.pl0', '3.1.1.6', 1),
                    ('2g6', '11g', -1),
                    ('0.960923', '2.2beta29', -1),
                    ('1.13++', '5.5.kw', -1))


        kila v1, v2, wanted kwenye versions:
            res = LooseVersion(v1)._cmp(LooseVersion(v2))
            self.assertEqual(res, wanted,
                             'cmp(%s, %s) should be %s, got %s' %
                             (v1, v2, wanted, res))

eleza test_suite():
    rudisha unittest.makeSuite(VersionTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
