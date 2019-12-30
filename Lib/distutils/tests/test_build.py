"""Tests kila distutils.command.build."""
agiza unittest
agiza os
agiza sys
kutoka test.support agiza run_unittest

kutoka distutils.command.build agiza build
kutoka distutils.tests agiza support
kutoka sysconfig agiza get_platform

kundi BuildTestCase(support.TempdirManager,
                    support.LoggingSilencer,
                    unittest.TestCase):

    eleza test_finalize_options(self):
        pkg_dir, dist = self.create_dist()
        cmd = build(dist)
        cmd.finalize_options()

        # ikiwa sio specified, plat_name gets the current platform
        self.assertEqual(cmd.plat_name, get_platform())

        # build_purelib ni build + lib
        wanted = os.path.join(cmd.build_base, 'lib')
        self.assertEqual(cmd.build_purelib, wanted)

        # build_platlib ni 'build/lib.platform-x.x[-pydebug]'
        # examples:
        #   build/lib.macosx-10.3-i386-2.7
        plat_spec = '.%s-%d.%d' % (cmd.plat_name, *sys.version_info[:2])
        ikiwa hasattr(sys, 'gettotalrefcount'):
            self.assertKweli(cmd.build_platlib.endswith('-pydebug'))
            plat_spec += '-pydebug'
        wanted = os.path.join(cmd.build_base, 'lib' + plat_spec)
        self.assertEqual(cmd.build_platlib, wanted)

        # by default, build_lib = build_purelib
        self.assertEqual(cmd.build_lib, cmd.build_purelib)

        # build_temp ni build/temp.<plat>
        wanted = os.path.join(cmd.build_base, 'temp' + plat_spec)
        self.assertEqual(cmd.build_temp, wanted)

        # build_scripts ni build/scripts-x.x
        wanted = os.path.join(cmd.build_base,
                              'scripts-%d.%d' % sys.version_info[:2])
        self.assertEqual(cmd.build_scripts, wanted)

        # executable ni os.path.normpath(sys.executable)
        self.assertEqual(cmd.executable, os.path.normpath(sys.executable))

eleza test_suite():
    rudisha unittest.makeSuite(BuildTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
