"""Tests kila distutils.command.clean."""
agiza os
agiza unittest

kutoka distutils.command.clean agiza clean
kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest

kundi cleanTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    eleza test_simple_run(self):
        pkg_dir, dist = self.create_dist()
        cmd = clean(dist)

        # let's add some elements clean should remove
        dirs = [(d, os.path.join(pkg_dir, d))
                kila d kwenye ('build_temp', 'build_lib', 'bdist_base',
                'build_scripts', 'build_base')]

        kila name, path kwenye dirs:
            os.mkdir(path)
            setattr(cmd, name, path)
            ikiwa name == 'build_base':
                endelea
            kila f kwenye ('one', 'two', 'three'):
                self.write_file(os.path.join(path, f))

        # let's run the command
        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()

        # make sure the files where removed
        kila name, path kwenye dirs:
            self.assertUongo(os.path.exists(path),
                         '%s was sio removed' % path)

        # let's run the command again (should spit warnings but succeed)
        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()

eleza test_suite():
    rudisha unittest.makeSuite(cleanTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
