"""Tests kila distutils.command.config."""
agiza unittest
agiza os
agiza sys
kutoka test.support agiza run_unittest, missing_compiler_executable

kutoka distutils.command.config agiza dump_file, config
kutoka distutils.tests agiza support
kutoka distutils agiza log

kundi ConfigTestCase(support.LoggingSilencer,
                     support.TempdirManager,
                     unittest.TestCase):

    eleza _info(self, msg, *args):
        kila line kwenye msg.splitlines():
            self._logs.append(line)

    eleza setUp(self):
        super(ConfigTestCase, self).setUp()
        self._logs = []
        self.old_log = log.info
        log.info = self._info

    eleza tearDown(self):
        log.info = self.old_log
        super(ConfigTestCase, self).tearDown()

    eleza test_dump_file(self):
        this_file = os.path.splitext(__file__)[0] + '.py'
        f = open(this_file)
        jaribu:
            numlines = len(f.readlines())
        mwishowe:
            f.close()

        dump_file(this_file, 'I am the header')
        self.assertEqual(len(self._logs), numlines+1)

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    eleza test_search_cpp(self):
        agiza shutil
        cmd = missing_compiler_executable(['preprocessor'])
        ikiwa cmd ni sio Tupu:
            self.skipTest('The %r command ni sio found' % cmd)
        pkg_dir, dist = self.create_dist()
        cmd = config(dist)
        cmd._check_compiler()
        compiler = cmd.compiler
        is_xlc = shutil.which(compiler.preprocessor[0]).startswith("/usr/vac")
        ikiwa is_xlc:
            self.skipTest('xlc: The -E option overrides the -P, -o, na -qsyntaxonly options')

        # simple pattern searches
        match = cmd.search_cpp(pattern='xxx', body='/* xxx */')
        self.assertEqual(match, 0)

        match = cmd.search_cpp(pattern='_configtest', body='/* xxx */')
        self.assertEqual(match, 1)

    eleza test_finalize_options(self):
        # finalize_options does a bit of transformation
        # on options
        pkg_dir, dist = self.create_dist()
        cmd = config(dist)
        cmd.include_dirs = 'one%stwo' % os.pathsep
        cmd.libraries = 'one'
        cmd.library_dirs = 'three%sfour' % os.pathsep
        cmd.ensure_finalized()

        self.assertEqual(cmd.include_dirs, ['one', 'two'])
        self.assertEqual(cmd.libraries, ['one'])
        self.assertEqual(cmd.library_dirs, ['three', 'four'])

    eleza test_clean(self):
        # _clean removes files
        tmp_dir = self.mkdtemp()
        f1 = os.path.join(tmp_dir, 'one')
        f2 = os.path.join(tmp_dir, 'two')

        self.write_file(f1, 'xxx')
        self.write_file(f2, 'xxx')

        kila f kwenye (f1, f2):
            self.assertKweli(os.path.exists(f))

        pkg_dir, dist = self.create_dist()
        cmd = config(dist)
        cmd._clean(f1, f2)

        kila f kwenye (f1, f2):
            self.assertUongo(os.path.exists(f))

eleza test_suite():
    rudisha unittest.makeSuite(ConfigTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
