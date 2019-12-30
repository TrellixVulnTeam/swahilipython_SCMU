"""Tests kila the lll script kwenye the Tools/script directory."""

agiza os
agiza sys
agiza tempfile
kutoka test agiza support
kutoka test.test_tools agiza skip_if_missing, import_tool
agiza unittest

skip_if_missing()


kundi lllTests(unittest.TestCase):

    eleza setUp(self):
        self.lll = import_tool('lll')

    @support.skip_unless_symlink
    eleza test_lll_multiple_dirs(self):
        ukijumuisha tempfile.TemporaryDirectory() as dir1, \
             tempfile.TemporaryDirectory() as dir2:
            fn1 = os.path.join(dir1, 'foo1')
            fn2 = os.path.join(dir2, 'foo2')
            kila fn, dir kwenye (fn1, dir1), (fn2, dir2):
                open(fn, 'w').close()
                os.symlink(fn, os.path.join(dir, 'symlink'))

            ukijumuisha support.captured_stdout() as output:
                self.lll.main([dir1, dir2])
            prefix = '\\\\?\\' ikiwa os.name == 'nt' isipokua ''
            self.assertEqual(output.getvalue(),
                f'{dir1}:\n'
                f'symlink -> {prefix}{fn1}\n'
                f'\n'
                f'{dir2}:\n'
                f'symlink -> {prefix}{fn2}\n'
            )


ikiwa __name__ == '__main__':
    unittest.main()
