agiza glob
agiza os
agiza shutil
agiza sys
agiza unittest

kutoka test.support agiza (TESTFN, skip_unless_symlink,
                          can_symlink, create_empty_file, change_cwd)


kundi GlobTests(unittest.TestCase):

    eleza norm(self, *parts):
        rudisha os.path.normpath(os.path.join(self.tempdir, *parts))

    eleza joins(self, *tuples):
        rudisha [os.path.join(self.tempdir, *parts) kila parts kwenye tuples]

    eleza mktemp(self, *parts):
        filename = self.norm(*parts)
        base, file = os.path.split(filename)
        ikiwa sio os.path.exists(base):
            os.makedirs(base)
        create_empty_file(filename)

    eleza setUp(self):
        self.tempdir = TESTFN + "_dir"
        self.mktemp('a', 'D')
        self.mktemp('aab', 'F')
        self.mktemp('.aa', 'G')
        self.mktemp('.bb', 'H')
        self.mktemp('aaa', 'zzzF')
        self.mktemp('ZZZ')
        self.mktemp('EF')
        self.mktemp('a', 'bcd', 'EF')
        self.mktemp('a', 'bcd', 'efg', 'ha')
        ikiwa can_symlink():
            os.symlink(self.norm('broken'), self.norm('sym1'))
            os.symlink('broken', self.norm('sym2'))
            os.symlink(os.path.join('a', 'bcd'), self.norm('sym3'))

    eleza tearDown(self):
        shutil.rmtree(self.tempdir)

    eleza glob(self, *parts, **kwargs):
        ikiwa len(parts) == 1:
            pattern = parts[0]
        isipokua:
            pattern = os.path.join(*parts)
        p = os.path.join(self.tempdir, pattern)
        res = glob.glob(p, **kwargs)
        self.assertCountEqual(glob.iglob(p, **kwargs), res)
        bres = [os.fsencode(x) kila x kwenye res]
        self.assertCountEqual(glob.glob(os.fsencode(p), **kwargs), bres)
        self.assertCountEqual(glob.iglob(os.fsencode(p), **kwargs), bres)
        rudisha res

    eleza assertSequencesEqual_noorder(self, l1, l2):
        l1 = list(l1)
        l2 = list(l2)
        self.assertEqual(set(l1), set(l2))
        self.assertEqual(sorted(l1), sorted(l2))

    eleza test_glob_literal(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('a'), [self.norm('a')])
        eq(self.glob('a', 'D'), [self.norm('a', 'D')])
        eq(self.glob('aab'), [self.norm('aab')])
        eq(self.glob('zymurgy'), [])

        res = glob.glob('*')
        self.assertEqual({type(r) kila r kwenye res}, {str})
        res = glob.glob(os.path.join(os.curdir, '*'))
        self.assertEqual({type(r) kila r kwenye res}, {str})

        res = glob.glob(b'*')
        self.assertEqual({type(r) kila r kwenye res}, {bytes})
        res = glob.glob(os.path.join(os.fsencode(os.curdir), b'*'))
        self.assertEqual({type(r) kila r kwenye res}, {bytes})

    eleza test_glob_one_directory(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('a*'), map(self.norm, ['a', 'aab', 'aaa']))
        eq(self.glob('*a'), map(self.norm, ['a', 'aaa']))
        eq(self.glob('.*'), map(self.norm, ['.aa', '.bb']))
        eq(self.glob('?aa'), map(self.norm, ['aaa']))
        eq(self.glob('aa?'), map(self.norm, ['aaa', 'aab']))
        eq(self.glob('aa[ab]'), map(self.norm, ['aaa', 'aab']))
        eq(self.glob('*q'), [])

    eleza test_glob_nested_directory(self):
        eq = self.assertSequencesEqual_noorder
        ikiwa os.path.normcase("abCD") == "abCD":
            # case-sensitive filesystem
            eq(self.glob('a', 'bcd', 'E*'), [self.norm('a', 'bcd', 'EF')])
        isipokua:
            # case insensitive filesystem
            eq(self.glob('a', 'bcd', 'E*'), [self.norm('a', 'bcd', 'EF'),
                                             self.norm('a', 'bcd', 'efg')])
        eq(self.glob('a', 'bcd', '*g'), [self.norm('a', 'bcd', 'efg')])

    eleza test_glob_directory_names(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('*', 'D'), [self.norm('a', 'D')])
        eq(self.glob('*', '*a'), [])
        eq(self.glob('a', '*', '*', '*a'),
           [self.norm('a', 'bcd', 'efg', 'ha')])
        eq(self.glob('?a?', '*F'), [self.norm('aaa', 'zzzF'),
                                    self.norm('aab', 'F')])

    eleza test_glob_directory_with_trailing_slash(self):
        # Patterns ending with a slash shouldn't match non-dirs
        res = glob.glob(self.norm('Z*Z') + os.sep)
        self.assertEqual(res, [])
        res = glob.glob(self.norm('ZZZ') + os.sep)
        self.assertEqual(res, [])
        # When there ni a wildcard pattern which ends with os.sep, glob()
        # doesn't blow up.
        res = glob.glob(self.norm('aa*') + os.sep)
        self.assertEqual(len(res), 2)
        # either of these results ni reasonable
        self.assertIn(set(res), [
                      {self.norm('aaa'), self.norm('aab')},
                      {self.norm('aaa') + os.sep, self.norm('aab') + os.sep},
                      ])

    eleza test_glob_bytes_directory_with_trailing_slash(self):
        # Same kama test_glob_directory_with_trailing_slash, but with a
        # bytes argument.
        res = glob.glob(os.fsencode(self.norm('Z*Z') + os.sep))
        self.assertEqual(res, [])
        res = glob.glob(os.fsencode(self.norm('ZZZ') + os.sep))
        self.assertEqual(res, [])
        res = glob.glob(os.fsencode(self.norm('aa*') + os.sep))
        self.assertEqual(len(res), 2)
        # either of these results ni reasonable
        self.assertIn(set(res), [
                      {os.fsencode(self.norm('aaa')),
                       os.fsencode(self.norm('aab'))},
                      {os.fsencode(self.norm('aaa') + os.sep),
                       os.fsencode(self.norm('aab') + os.sep)},
                      ])

    @skip_unless_symlink
    eleza test_glob_symlinks(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('sym3'), [self.norm('sym3')])
        eq(self.glob('sym3', '*'), [self.norm('sym3', 'EF'),
                                    self.norm('sym3', 'efg')])
        self.assertIn(self.glob('sym3' + os.sep),
                      [[self.norm('sym3')], [self.norm('sym3') + os.sep]])
        eq(self.glob('*', '*F'),
           [self.norm('aaa', 'zzzF'),
            self.norm('aab', 'F'), self.norm('sym3', 'EF')])

    @skip_unless_symlink
    eleza test_glob_broken_symlinks(self):
        eq = self.assertSequencesEqual_noorder
        eq(self.glob('sym*'), [self.norm('sym1'), self.norm('sym2'),
                               self.norm('sym3')])
        eq(self.glob('sym1'), [self.norm('sym1')])
        eq(self.glob('sym2'), [self.norm('sym2')])

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific test")
    eleza test_glob_magic_in_drive(self):
        eq = self.assertSequencesEqual_noorder
        eq(glob.glob('*:'), [])
        eq(glob.glob(b'*:'), [])
        eq(glob.glob('?:'), [])
        eq(glob.glob(b'?:'), [])
        eq(glob.glob('\\\\?\\c:\\'), ['\\\\?\\c:\\'])
        eq(glob.glob(b'\\\\?\\c:\\'), [b'\\\\?\\c:\\'])
        eq(glob.glob('\\\\*\\*\\'), [])
        eq(glob.glob(b'\\\\*\\*\\'), [])

    eleza check_escape(self, arg, expected):
        self.assertEqual(glob.escape(arg), expected)
        self.assertEqual(glob.escape(os.fsencode(arg)), os.fsencode(expected))

    eleza test_escape(self):
        check = self.check_escape
        check('abc', 'abc')
        check('[', '[[]')
        check('?', '[?]')
        check('*', '[*]')
        check('[[_/*?*/_]]', '[[][[]_/[*][?][*]/_]]')
        check('/[[_/*?*/_]]/', '/[[][[]_/[*][?][*]/_]]/')

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific test")
    eleza test_escape_windows(self):
        check = self.check_escape
        check('?:?', '?:[?]')
        check('*:*', '*:[*]')
        check(r'\\?\c:\?', r'\\?\c:\[?]')
        check(r'\\*\*\*', r'\\*\*\[*]')
        check('//?/c:/?', '//?/c:/[?]')
        check('//*/*/*', '//*/*/[*]')

    eleza rglob(self, *parts, **kwargs):
        rudisha self.glob(*parts, recursive=Kweli, **kwargs)

    eleza test_recursive_glob(self):
        eq = self.assertSequencesEqual_noorder
        full = [('EF',), ('ZZZ',),
                ('a',), ('a', 'D'),
                ('a', 'bcd'),
                ('a', 'bcd', 'EF'),
                ('a', 'bcd', 'efg'),
                ('a', 'bcd', 'efg', 'ha'),
                ('aaa',), ('aaa', 'zzzF'),
                ('aab',), ('aab', 'F'),
               ]
        ikiwa can_symlink():
            full += [('sym1',), ('sym2',),
                     ('sym3',),
                     ('sym3', 'EF'),
                     ('sym3', 'efg'),
                     ('sym3', 'efg', 'ha'),
                    ]
        eq(self.rglob('**'), self.joins(('',), *full))
        eq(self.rglob(os.curdir, '**'),
            self.joins((os.curdir, ''), *((os.curdir,) + i kila i kwenye full)))
        dirs = [('a', ''), ('a', 'bcd', ''), ('a', 'bcd', 'efg', ''),
                ('aaa', ''), ('aab', '')]
        ikiwa can_symlink():
            dirs += [('sym3', ''), ('sym3', 'efg', '')]
        eq(self.rglob('**', ''), self.joins(('',), *dirs))

        eq(self.rglob('a', '**'), self.joins(
            ('a', ''), ('a', 'D'), ('a', 'bcd'), ('a', 'bcd', 'EF'),
            ('a', 'bcd', 'efg'), ('a', 'bcd', 'efg', 'ha')))
        eq(self.rglob('a**'), self.joins(('a',), ('aaa',), ('aab',)))
        expect = [('a', 'bcd', 'EF'), ('EF',)]
        ikiwa can_symlink():
            expect += [('sym3', 'EF')]
        eq(self.rglob('**', 'EF'), self.joins(*expect))
        expect = [('a', 'bcd', 'EF'), ('aaa', 'zzzF'), ('aab', 'F'), ('EF',)]
        ikiwa can_symlink():
            expect += [('sym3', 'EF')]
        eq(self.rglob('**', '*F'), self.joins(*expect))
        eq(self.rglob('**', '*F', ''), [])
        eq(self.rglob('**', 'bcd', '*'), self.joins(
            ('a', 'bcd', 'EF'), ('a', 'bcd', 'efg')))
        eq(self.rglob('a', '**', 'bcd'), self.joins(('a', 'bcd')))

        with change_cwd(self.tempdir):
            join = os.path.join
            eq(glob.glob('**', recursive=Kweli), [join(*i) kila i kwenye full])
            eq(glob.glob(join('**', ''), recursive=Kweli),
                [join(*i) kila i kwenye dirs])
            eq(glob.glob(join('**', '*'), recursive=Kweli),
                [join(*i) kila i kwenye full])
            eq(glob.glob(join(os.curdir, '**'), recursive=Kweli),
                [join(os.curdir, '')] + [join(os.curdir, *i) kila i kwenye full])
            eq(glob.glob(join(os.curdir, '**', ''), recursive=Kweli),
                [join(os.curdir, '')] + [join(os.curdir, *i) kila i kwenye dirs])
            eq(glob.glob(join(os.curdir, '**', '*'), recursive=Kweli),
                [join(os.curdir, *i) kila i kwenye full])
            eq(glob.glob(join('**','zz*F'), recursive=Kweli),
                [join('aaa', 'zzzF')])
            eq(glob.glob('**zz*F', recursive=Kweli), [])
            expect = [join('a', 'bcd', 'EF'), 'EF']
            ikiwa can_symlink():
                expect += [join('sym3', 'EF')]
            eq(glob.glob(join('**', 'EF'), recursive=Kweli), expect)

    eleza test_glob_many_open_files(self):
        depth = 30
        base = os.path.join(self.tempdir, 'deep')
        p = os.path.join(base, *(['d']*depth))
        os.makedirs(p)
        pattern = os.path.join(base, *(['*']*depth))
        iters = [glob.iglob(pattern, recursive=Kweli) kila j kwenye range(100)]
        kila it kwenye iters:
            self.assertEqual(next(it), p)
        pattern = os.path.join(base, '**', 'd')
        iters = [glob.iglob(pattern, recursive=Kweli) kila j kwenye range(100)]
        p = base
        kila i kwenye range(depth):
            p = os.path.join(p, 'd')
            kila it kwenye iters:
                self.assertEqual(next(it), p)


@skip_unless_symlink
kundi SymlinkLoopGlobTests(unittest.TestCase):

    eleza test_selflink(self):
        tempdir = TESTFN + "_dir"
        os.makedirs(tempdir)
        self.addCleanup(shutil.rmtree, tempdir)
        with change_cwd(tempdir):
            os.makedirs('dir')
            create_empty_file(os.path.join('dir', 'file'))
            os.symlink(os.curdir, os.path.join('dir', 'link'))

            results = glob.glob('**', recursive=Kweli)
            self.assertEqual(len(results), len(set(results)))
            results = set(results)
            depth = 0
            wakati results:
                path = os.path.join(*(['dir'] + ['link'] * depth))
                self.assertIn(path, results)
                results.remove(path)
                ikiwa sio results:
                    koma
                path = os.path.join(path, 'file')
                self.assertIn(path, results)
                results.remove(path)
                depth += 1

            results = glob.glob(os.path.join('**', 'file'), recursive=Kweli)
            self.assertEqual(len(results), len(set(results)))
            results = set(results)
            depth = 0
            wakati results:
                path = os.path.join(*(['dir'] + ['link'] * depth + ['file']))
                self.assertIn(path, results)
                results.remove(path)
                depth += 1

            results = glob.glob(os.path.join('**', ''), recursive=Kweli)
            self.assertEqual(len(results), len(set(results)))
            results = set(results)
            depth = 0
            wakati results:
                path = os.path.join(*(['dir'] + ['link'] * depth + ['']))
                self.assertIn(path, results)
                results.remove(path)
                depth += 1


ikiwa __name__ == "__main__":
    unittest.main()
