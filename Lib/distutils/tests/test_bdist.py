"""Tests kila distutils.command.bdist."""
agiza os
agiza unittest
kutoka test.support agiza run_unittest
agiza warnings

kutoka distutils.command.bdist agiza bdist
kutoka distutils.tests agiza support


kundi BuildTestCase(support.TempdirManager,
                    unittest.TestCase):

    eleza test_formats(self):
        # let's create a command na make sure
        # we can set the format
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.formats = ['msi']
        cmd.ensure_finalized()
        self.assertEqual(cmd.formats, ['msi'])

        # what formats does bdist offer?
        formats = ['bztar', 'gztar', 'msi', 'rpm', 'tar',
                   'wininst', 'xztar', 'zip', 'ztar']
        found = sorted(cmd.format_command)
        self.assertEqual(found, formats)

    eleza test_skip_build(self):
        # bug #10946: bdist --skip-build should trickle down to subcommands
        dist = self.create_dist()[1]
        cmd = bdist(dist)
        cmd.skip_build = 1
        cmd.ensure_finalized()
        dist.command_obj['bdist'] = cmd

        names = ['bdist_dumb', 'bdist_wininst']  # bdist_rpm does sio support --skip-build
        ikiwa os.name == 'nt':
            names.append('bdist_msi')

        kila name kwenye names:
            ukijumuisha warnings.catch_warnings():
                warnings.filterwarnings('ignore', 'bdist_wininst command ni deprecated',
                                        DeprecationWarning)
                subcmd = cmd.get_finalized_command(name)
            ikiwa getattr(subcmd, '_unsupported', Uongo):
                # command ni sio supported on this build
                endelea
            self.assertKweli(subcmd.skip_build,
                            '%s should take --skip-build kutoka bdist' % name)


eleza test_suite():
    rudisha unittest.makeSuite(BuildTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
