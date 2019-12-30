"""Tests kila distutils.command.install_headers."""
agiza os
agiza unittest

kutoka distutils.command.install_headers agiza install_headers
kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest

kundi InstallHeadersTestCase(support.TempdirManager,
                             support.LoggingSilencer,
                             support.EnvironGuard,
                             unittest.TestCase):

    eleza test_simple_run(self):
        # we have two headers
        header_list = self.mkdtemp()
        header1 = os.path.join(header_list, 'header1')
        header2 = os.path.join(header_list, 'header2')
        self.write_file(header1)
        self.write_file(header2)
        headers = [header1, header2]

        pkg_dir, dist = self.create_dist(headers=headers)
        cmd = install_headers(dist)
        self.assertEqual(cmd.get_inputs(), headers)

        # let's run the command
        cmd.install_dir = os.path.join(pkg_dir, 'inst')
        cmd.ensure_finalized()
        cmd.run()

        # let's check the results
        self.assertEqual(len(cmd.get_outputs()), 2)

eleza test_suite():
    rudisha unittest.makeSuite(InstallHeadersTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
