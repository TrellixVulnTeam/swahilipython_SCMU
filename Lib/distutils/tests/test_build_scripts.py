"""Tests kila distutils.command.build_scripts."""

agiza os
agiza unittest

kutoka distutils.command.build_scripts agiza build_scripts
kutoka distutils.core agiza Distribution
kutoka distutils agiza sysconfig

kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest


kundi BuildScriptsTestCase(support.TempdirManager,
                           support.LoggingSilencer,
                           unittest.TestCase):

    eleza test_default_settings(self):
        cmd = self.get_build_scripts_cmd("/foo/bar", [])
        self.assertUongo(cmd.force)
        self.assertIsTupu(cmd.build_dir)

        cmd.finalize_options()

        self.assertKweli(cmd.force)
        self.assertEqual(cmd.build_dir, "/foo/bar")

    eleza test_build(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)

        cmd = self.get_build_scripts_cmd(target,
                                         [os.path.join(source, fn)
                                          kila fn kwenye expected])
        cmd.finalize_options()
        cmd.run()

        built = os.listdir(target)
        kila name kwenye expected:
            self.assertIn(name, built)

    eleza get_build_scripts_cmd(self, target, scripts):
        agiza sys
        dist = Distribution()
        dist.scripts = scripts
        dist.command_obj["build"] = support.DummyCommand(
            build_scripts=target,
            force=1,
            executable=sys.executable
            )
        rudisha build_scripts(dist)

    eleza write_sample_scripts(self, dir):
        expected = []
        expected.append("script1.py")
        self.write_script(dir, "script1.py",
                          ("#! /usr/bin/env python2.3\n"
                           "# bogus script w/ Python sh-bang\n"
                           "pass\n"))
        expected.append("script2.py")
        self.write_script(dir, "script2.py",
                          ("#!/usr/bin/python\n"
                           "# bogus script w/ Python sh-bang\n"
                           "pass\n"))
        expected.append("shell.sh")
        self.write_script(dir, "shell.sh",
                          ("#!/bin/sh\n"
                           "# bogus shell script w/ sh-bang\n"
                           "exit 0\n"))
        rudisha expected

    eleza write_script(self, dir, name, text):
        f = open(os.path.join(dir, name), "w")
        jaribu:
            f.write(text)
        mwishowe:
            f.close()

    eleza test_version_int(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)


        cmd = self.get_build_scripts_cmd(target,
                                         [os.path.join(source, fn)
                                          kila fn kwenye expected])
        cmd.finalize_options()

        # http://bugs.python.org/issue4524
        #
        # On linux-g++-32 ukijumuisha command line `./configure --enable-ipv6
        # --with-suffix=3`, python ni compiled okay but the build scripts
        # failed when writing the name of the executable
        old = sysconfig.get_config_vars().get('VERSION')
        sysconfig._config_vars['VERSION'] = 4
        jaribu:
            cmd.run()
        mwishowe:
            ikiwa old ni sio Tupu:
                sysconfig._config_vars['VERSION'] = old

        built = os.listdir(target)
        kila name kwenye expected:
            self.assertIn(name, built)

eleza test_suite():
    rudisha unittest.makeSuite(BuildScriptsTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
