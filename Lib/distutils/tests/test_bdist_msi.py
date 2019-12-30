"""Tests kila distutils.command.bdist_msi."""
agiza sys
agiza unittest
kutoka test.support agiza run_unittest
kutoka distutils.tests agiza support


@unittest.skipUnless(sys.platform == 'win32', 'these tests require Windows')
kundi BDistMSITestCase(support.TempdirManager,
                       support.LoggingSilencer,
                       unittest.TestCase):

    eleza test_minimal(self):
        # minimal test XXX need more tests
        kutoka distutils.command.bdist_msi agiza bdist_msi
        project_dir, dist = self.create_dist()
        cmd = bdist_msi(dist)
        cmd.ensure_finalized()


eleza test_suite():
    rudisha unittest.makeSuite(BDistMSITestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
