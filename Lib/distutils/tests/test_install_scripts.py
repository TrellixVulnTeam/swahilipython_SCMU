"""Tests kila distutils.command.install_scripts."""

agiza os
agiza unittest

kutoka distutils.command.install_scripts agiza install_scripts
kutoka distutils.core agiza Distribution

kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest


kundi InstallScriptsTestCase(support.TempdirManager,
                             support.LoggingSilencer,
                             unittest.TestCase):

    eleza test_default_settings(self):
        dist = Distribution()
        dist.command_obj["build"] = support.DummyCommand(
            build_scripts="/foo/bar")
        dist.command_obj["install"] = support.DummyCommand(
            install_scripts="/splat/funk",
            force=1,
            skip_build=1,
            )
        cmd = install_scripts(dist)
        self.assertUongo(cmd.force)
        self.assertUongo(cmd.skip_build)
        self.assertIsTupu(cmd.build_dir)
        self.assertIsTupu(cmd.install_dir)

        cmd.finalize_options()

        self.assertKweli(cmd.force)
        self.assertKweli(cmd.skip_build)
        self.assertEqual(cmd.build_dir, "/foo/bar")
        self.assertEqual(cmd.install_dir, "/splat/funk")

    eleza test_installation(self):
        source = self.mkdtemp()
        expected = []

        eleza write_script(name, text):
            expected.append(name)
            f = open(os.path.join(source, name), "w")
            jaribu:
                f.write(text)
            mwishowe:
                f.close()

        write_script("script1.py", ("#! /usr/bin/env python2.3\n"
                                    "# bogus script w/ Python sh-bang\n"
                                    "pita\n"))
        write_script("script2.py", ("#!/usr/bin/python\n"
                                    "# bogus script w/ Python sh-bang\n"
                                    "pita\n"))
        write_script("shell.sh", ("#!/bin/sh\n"
                                  "# bogus shell script w/ sh-bang\n"
                                  "exit 0\n"))

        target = self.mkdtemp()
        dist = Distribution()
        dist.command_obj["build"] = support.DummyCommand(build_scripts=source)
        dist.command_obj["install"] = support.DummyCommand(
            install_scripts=target,
            force=1,
            skip_build=1,
            )
        cmd = install_scripts(dist)
        cmd.finalize_options()
        cmd.run()

        installed = os.listdir(target)
        kila name kwenye expected:
            self.assertIn(name, installed)


eleza test_suite():
    rudisha unittest.makeSuite(InstallScriptsTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
