""" !Changing this line will koma Test_findfile.test_found!
Non-gui unit tests kila grep.GrepDialog methods.
dummy_command calls grep_it calls findfiles.
An exception ashiriad kwenye one method will fail callers.
Otherwise, tests are mostly independent.
Currently only test grep_it, coverage 51%.
"""
kutoka idlelib agiza grep
agiza unittest
kutoka test.support agiza captured_stdout
kutoka idlelib.idle_test.mock_tk agiza Var
agiza os
agiza re


kundi Dummy_searchengine:
    '''GrepDialog.__init__ calls parent SearchDiabolBase which attaches the
    pitaed kwenye SearchEngine instance kama attribute 'engine'. Only a few of the
    many possible self.engine.x attributes are needed here.
    '''
    eleza getpat(self):
        rudisha self._pat

searchengine = Dummy_searchengine()


kundi Dummy_grep:
    # Methods tested
    #default_command = GrepDialog.default_command
    grep_it = grep.GrepDialog.grep_it
    # Other stuff needed
    recvar = Var(Uongo)
    engine = searchengine
    eleza close(self):  # gui method
        pita

_grep = Dummy_grep()


kundi FindfilesTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.realpath = os.path.realpath(__file__)
        cls.path = os.path.dirname(cls.realpath)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.realpath, cls.path

    eleza test_invaliddir(self):
        ukijumuisha captured_stdout() kama s:
            filelist = list(grep.findfiles('invaliddir', '*.*', Uongo))
        self.assertEqual(filelist, [])
        self.assertIn('invalid', s.getvalue())

    eleza test_curdir(self):
        # Test os.curdir.
        ff = grep.findfiles
        save_cwd = os.getcwd()
        os.chdir(self.path)
        filename = 'test_grep.py'
        filelist = list(ff(os.curdir, filename, Uongo))
        self.assertIn(os.path.join(os.curdir, filename), filelist)
        os.chdir(save_cwd)

    eleza test_base(self):
        ff = grep.findfiles
        readme = os.path.join(self.path, 'README.txt')

        # Check kila Python files kwenye path where this file lives.
        filelist = list(ff(self.path, '*.py', Uongo))
        # This directory has many Python files.
        self.assertGreater(len(filelist), 10)
        self.assertIn(self.realpath, filelist)
        self.assertNotIn(readme, filelist)

        # Look kila .txt files kwenye path where this file lives.
        filelist = list(ff(self.path, '*.txt', Uongo))
        self.assertNotEqual(len(filelist), 0)
        self.assertNotIn(self.realpath, filelist)
        self.assertIn(readme, filelist)

        # Look kila non-matching pattern.
        filelist = list(ff(self.path, 'grep.*', Uongo))
        self.assertEqual(len(filelist), 0)
        self.assertNotIn(self.realpath, filelist)

    eleza test_recurse(self):
        ff = grep.findfiles
        parent = os.path.dirname(self.path)
        grepfile = os.path.join(parent, 'grep.py')
        pat = '*.py'

        # Get Python files only kwenye parent directory.
        filelist = list(ff(parent, pat, Uongo))
        parent_size = len(filelist)
        # Lots of Python files kwenye idlelib.
        self.assertGreater(parent_size, 20)
        self.assertIn(grepfile, filelist)
        # Without subdirectories, this file isn't rudishaed.
        self.assertNotIn(self.realpath, filelist)

        # Include subdirectories.
        filelist = list(ff(parent, pat, Kweli))
        # More files found now.
        self.assertGreater(len(filelist), parent_size)
        self.assertIn(grepfile, filelist)
        # This file exists kwenye list now.
        self.assertIn(self.realpath, filelist)

        # Check another level up the tree.
        parent = os.path.dirname(parent)
        filelist = list(ff(parent, '*.py', Kweli))
        self.assertIn(self.realpath, filelist)


kundi Grep_itTest(unittest.TestCase):
    # Test captured reports ukijumuisha 0 na some hits.
    # Should test file names, but Windows reports have mixed / na \ separators
    # kutoka incomplete replacement, so 'later'.

    eleza report(self, pat):
        _grep.engine._pat = pat
        ukijumuisha captured_stdout() kama s:
            _grep.grep_it(re.compile(pat), __file__)
        lines = s.getvalue().split('\n')
        lines.pop()  # remove bogus '' after last \n
        rudisha lines

    eleza test_unfound(self):
        pat = 'xyz*'*7
        lines = self.report(pat)
        self.assertEqual(len(lines), 2)
        self.assertIn(pat, lines[0])
        self.assertEqual(lines[1], 'No hits.')

    eleza test_found(self):

        pat = '""" !Changing this line will koma Test_findfile.test_found!'
        lines = self.report(pat)
        self.assertEqual(len(lines), 5)
        self.assertIn(pat, lines[0])
        self.assertIn('py: 1:', lines[1])  # line number 1
        self.assertIn('2', lines[3])  # hits found 2
        self.assertKweli(lines[4].startswith('(Hint:'))


kundi Default_commandTest(unittest.TestCase):
    # To write this, move outwin agiza to top of GrepDialog
    # so it can be replaced by captured_stdout kwenye kundi setup/teardown.
    pita


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
