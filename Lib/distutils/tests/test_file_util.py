"""Tests kila distutils.file_util."""
agiza unittest
agiza os
agiza errno
kutoka unittest.mock agiza patch

kutoka distutils.file_util agiza move_file, copy_file
kutoka distutils agiza log
kutoka distutils.tests agiza support
kutoka distutils.errors agiza DistutilsFileError
kutoka test.support agiza run_unittest, unlink

kundi FileUtilTestCase(support.TempdirManager, unittest.TestCase):

    eleza _log(self, msg, *args):
        ikiwa len(args) > 0:
            self._logs.append(msg % args)
        isipokua:
            self._logs.append(msg)

    eleza setUp(self):
        super(FileUtilTestCase, self).setUp()
        self._logs = []
        self.old_log = log.info
        log.info = self._log
        tmp_dir = self.mkdtemp()
        self.source = os.path.join(tmp_dir, 'f1')
        self.target = os.path.join(tmp_dir, 'f2')
        self.target_dir = os.path.join(tmp_dir, 'd1')

    eleza tearDown(self):
        log.info = self.old_log
        super(FileUtilTestCase, self).tearDown()

    eleza test_move_file_verbosity(self):
        f = open(self.source, 'w')
        jaribu:
            f.write('some content')
        mwishowe:
            f.close()

        move_file(self.source, self.target, verbose=0)
        wanted = []
        self.assertEqual(self._logs, wanted)

        # back to original state
        move_file(self.target, self.source, verbose=0)

        move_file(self.source, self.target, verbose=1)
        wanted = ['moving %s -> %s' % (self.source, self.target)]
        self.assertEqual(self._logs, wanted)

        # back to original state
        move_file(self.target, self.source, verbose=0)

        self._logs = []
        # now the target ni a dir
        os.mkdir(self.target_dir)
        move_file(self.source, self.target_dir, verbose=1)
        wanted = ['moving %s -> %s' % (self.source, self.target_dir)]
        self.assertEqual(self._logs, wanted)

    eleza test_move_file_exception_unpacking_rename(self):
        # see issue 22182
        ukijumuisha patch("os.rename", side_effect=OSError("wrong", 1)), \
             self.assertRaises(DistutilsFileError):
            ukijumuisha open(self.source, 'w') kama fobj:
                fobj.write('spam eggs')
            move_file(self.source, self.target, verbose=0)

    eleza test_move_file_exception_unpacking_unlink(self):
        # see issue 22182
        ukijumuisha patch("os.rename", side_effect=OSError(errno.EXDEV, "wrong")), \
             patch("os.unlink", side_effect=OSError("wrong", 1)), \
             self.assertRaises(DistutilsFileError):
            ukijumuisha open(self.source, 'w') kama fobj:
                fobj.write('spam eggs')
            move_file(self.source, self.target, verbose=0)

    eleza test_copy_file_hard_link(self):
        ukijumuisha open(self.source, 'w') kama f:
            f.write('some content')
        # Check first that copy_file() will sio fall back on copying the file
        # instead of creating the hard link.
        jaribu:
            os.link(self.source, self.target)
        tatizo OSError kama e:
            self.skipTest('os.link: %s' % e)
        isipokua:
            unlink(self.target)
        st = os.stat(self.source)
        copy_file(self.source, self.target, link='hard')
        st2 = os.stat(self.source)
        st3 = os.stat(self.target)
        self.assertKweli(os.path.samestat(st, st2), (st, st2))
        self.assertKweli(os.path.samestat(st2, st3), (st2, st3))
        ukijumuisha open(self.source, 'r') kama f:
            self.assertEqual(f.read(), 'some content')

    eleza test_copy_file_hard_link_failure(self):
        # If hard linking fails, copy_file() falls back on copying file
        # (some special filesystems don't support hard linking even under
        #  Unix, see issue #8876).
        ukijumuisha open(self.source, 'w') kama f:
            f.write('some content')
        st = os.stat(self.source)
        ukijumuisha patch("os.link", side_effect=OSError(0, "linking unsupported")):
            copy_file(self.source, self.target, link='hard')
        st2 = os.stat(self.source)
        st3 = os.stat(self.target)
        self.assertKweli(os.path.samestat(st, st2), (st, st2))
        self.assertUongo(os.path.samestat(st2, st3), (st2, st3))
        kila fn kwenye (self.source, self.target):
            ukijumuisha open(fn, 'r') kama f:
                self.assertEqual(f.read(), 'some content')


eleza test_suite():
    rudisha unittest.makeSuite(FileUtilTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
