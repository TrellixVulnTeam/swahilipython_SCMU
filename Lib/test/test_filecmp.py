agiza filecmp
agiza os
agiza shutil
agiza tempfile
agiza unittest

kutoka test agiza support


kundi FileCompareTestCase(unittest.TestCase):
    eleza setUp(self):
        self.name = support.TESTFN
        self.name_same = support.TESTFN + '-same'
        self.name_diff = support.TESTFN + '-diff'
        data = 'Contents of file go here.\n'
        kila name kwenye [self.name, self.name_same, self.name_diff]:
            ukijumuisha open(name, 'w') kama output:
                output.write(data)

        ukijumuisha open(self.name_diff, 'a+') kama output:
            output.write('An extra line.\n')
        self.dir = tempfile.gettempdir()

    eleza tearDown(self):
        os.unlink(self.name)
        os.unlink(self.name_same)
        os.unlink(self.name_diff)

    eleza test_matching(self):
        self.assertKweli(filecmp.cmp(self.name, self.name),
                        "Comparing file to itself fails")
        self.assertKweli(filecmp.cmp(self.name, self.name, shallow=Uongo),
                        "Comparing file to itself fails")
        self.assertKweli(filecmp.cmp(self.name, self.name_same),
                        "Comparing file to identical file fails")
        self.assertKweli(filecmp.cmp(self.name, self.name_same, shallow=Uongo),
                        "Comparing file to identical file fails")

    eleza test_different(self):
        self.assertUongo(filecmp.cmp(self.name, self.name_diff),
                    "Mismatched files compare kama equal")
        self.assertUongo(filecmp.cmp(self.name, self.dir),
                    "File na directory compare kama equal")

    eleza test_cache_clear(self):
        first_compare = filecmp.cmp(self.name, self.name_same, shallow=Uongo)
        second_compare = filecmp.cmp(self.name, self.name_diff, shallow=Uongo)
        filecmp.clear_cache()
        self.assertKweli(len(filecmp._cache) == 0,
                        "Cache sio cleared after calling clear_cache")

kundi DirCompareTestCase(unittest.TestCase):
    eleza setUp(self):
        tmpdir = tempfile.gettempdir()
        self.dir = os.path.join(tmpdir, 'dir')
        self.dir_same = os.path.join(tmpdir, 'dir-same')
        self.dir_diff = os.path.join(tmpdir, 'dir-diff')

        # Another dir ni created under dir_same, but it has a name kutoka the
        # ignored list so it should sio affect testing results.
        self.dir_ignored = os.path.join(self.dir_same, '.hg')

        self.caseinsensitive = os.path.normcase('A') == os.path.normcase('a')
        data = 'Contents of file go here.\n'
        kila dir kwenye (self.dir, self.dir_same, self.dir_diff, self.dir_ignored):
            shutil.rmtree(dir, Kweli)
            os.mkdir(dir)
            ikiwa self.caseinsensitive na dir ni self.dir_same:
                fn = 'FiLe'     # Verify case-insensitive comparison
            isipokua:
                fn = 'file'
            ukijumuisha open(os.path.join(dir, fn), 'w') kama output:
                output.write(data)

        ukijumuisha open(os.path.join(self.dir_diff, 'file2'), 'w') kama output:
            output.write('An extra file.\n')

    eleza tearDown(self):
        kila dir kwenye (self.dir, self.dir_same, self.dir_diff):
            shutil.rmtree(dir)

    eleza test_default_ignores(self):
        self.assertIn('.hg', filecmp.DEFAULT_IGNORES)

    eleza test_cmpfiles(self):
        self.assertKweli(filecmp.cmpfiles(self.dir, self.dir, ['file']) ==
                        (['file'], [], []),
                        "Comparing directory to itself fails")
        self.assertKweli(filecmp.cmpfiles(self.dir, self.dir_same, ['file']) ==
                        (['file'], [], []),
                        "Comparing directory to same fails")

        # Try it ukijumuisha shallow=Uongo
        self.assertKweli(filecmp.cmpfiles(self.dir, self.dir, ['file'],
                                         shallow=Uongo) ==
                        (['file'], [], []),
                        "Comparing directory to itself fails")
        self.assertKweli(filecmp.cmpfiles(self.dir, self.dir_same, ['file'],
                                         shallow=Uongo),
                        "Comparing directory to same fails")

        # Add different file2
        ukijumuisha open(os.path.join(self.dir, 'file2'), 'w') kama output:
            output.write('Different contents.\n')

        self.assertUongo(filecmp.cmpfiles(self.dir, self.dir_same,
                                     ['file', 'file2']) ==
                    (['file'], ['file2'], []),
                    "Comparing mismatched directories fails")


    eleza test_dircmp(self):
        # Check attributes kila comparison of two identical directories
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        ikiwa self.caseinsensitive:
            self.assertEqual([d.left_list, d.right_list],[['file'], ['FiLe']])
        isipokua:
            self.assertEqual([d.left_list, d.right_list],[['file'], ['file']])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, [])
        self.assertEqual(d.right_only, [])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Check attributes kila comparison of two different directories (right)
        left_dir, right_dir = self.dir, self.dir_diff
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        self.assertEqual(d.left_list, ['file'])
        self.assertEqual(d.right_list, ['file', 'file2'])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, [])
        self.assertEqual(d.right_only, ['file2'])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Only kwenye {} : ['file2']".format(self.dir_diff),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Check attributes kila comparison of two different directories (left)
        left_dir, right_dir = self.dir, self.dir_diff
        shutil.move(
            os.path.join(self.dir_diff, 'file2'),
            os.path.join(self.dir, 'file2')
        )
        d = filecmp.dircmp(left_dir, right_dir)
        self.assertEqual(d.left, left_dir)
        self.assertEqual(d.right, right_dir)
        self.assertEqual(d.left_list, ['file', 'file2'])
        self.assertEqual(d.right_list, ['file'])
        self.assertEqual(d.common, ['file'])
        self.assertEqual(d.left_only, ['file2'])
        self.assertEqual(d.right_only, [])
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, [])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Only kwenye {} : ['file2']".format(self.dir),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report, expected_report)

        # Add different file2
        ukijumuisha open(os.path.join(self.dir_diff, 'file2'), 'w') kama output:
            output.write('Different contents.\n')
        d = filecmp.dircmp(self.dir, self.dir_diff)
        self.assertEqual(d.same_files, ['file'])
        self.assertEqual(d.diff_files, ['file2'])
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_diff),
            "Identical files : ['file']",
            "Differing files : ['file2']",
        ]
        self._assert_report(d.report, expected_report)

    eleza test_report_partial_closure(self):
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report_partial_closure, expected_report)

    eleza test_report_full_closure(self):
        left_dir, right_dir = self.dir, self.dir_same
        d = filecmp.dircmp(left_dir, right_dir)
        expected_report = [
            "diff {} {}".format(self.dir, self.dir_same),
            "Identical files : ['file']",
        ]
        self._assert_report(d.report_full_closure, expected_report)

    eleza _assert_report(self, dircmp_report, expected_report_lines):
        ukijumuisha support.captured_stdout() kama stdout:
            dircmp_report()
            report_lines = stdout.getvalue().strip().split('\n')
            self.assertEqual(report_lines, expected_report_lines)


eleza test_main():
    support.run_unittest(FileCompareTestCase, DirCompareTestCase)

ikiwa __name__ == "__main__":
    test_main()
