"""Tests kila distutils.dep_util."""
agiza unittest
agiza os

kutoka distutils.dep_util agiza newer, newer_pairwise, newer_group
kutoka distutils.errors agiza DistutilsFileError
kutoka distutils.tests agiza support
kutoka test.support agiza run_unittest

kundi DepUtilTestCase(support.TempdirManager, unittest.TestCase):

    eleza test_newer(self):

        tmpdir = self.mkdtemp()
        new_file = os.path.join(tmpdir, 'new')
        old_file = os.path.abspath(__file__)

        # Raise DistutilsFileError ikiwa 'new_file' does sio exist.
        self.assertRaises(DistutilsFileError, newer, new_file, old_file)

        # Return true ikiwa 'new_file' exists na ni more recently modified than
        # 'old_file', ama ikiwa 'new_file' exists na 'old_file' doesn't.
        self.write_file(new_file)
        self.assertKweli(newer(new_file, 'I_dont_exist'))
        self.assertKweli(newer(new_file, old_file))

        # Return false ikiwa both exist na 'old_file' ni the same age ama younger
        # than 'new_file'.
        self.assertUongo(newer(old_file, new_file))

    eleza test_newer_pairwise(self):
        tmpdir = self.mkdtemp()
        sources = os.path.join(tmpdir, 'sources')
        targets = os.path.join(tmpdir, 'targets')
        os.mkdir(sources)
        os.mkdir(targets)
        one = os.path.join(sources, 'one')
        two = os.path.join(sources, 'two')
        three = os.path.abspath(__file__)    # I am the old file
        four = os.path.join(targets, 'four')
        self.write_file(one)
        self.write_file(two)
        self.write_file(four)

        self.assertEqual(newer_pairwise([one, two], [three, four]),
                         ([one],[three]))

    eleza test_newer_group(self):
        tmpdir = self.mkdtemp()
        sources = os.path.join(tmpdir, 'sources')
        os.mkdir(sources)
        one = os.path.join(sources, 'one')
        two = os.path.join(sources, 'two')
        three = os.path.join(sources, 'three')
        old_file = os.path.abspath(__file__)

        # rudisha true ikiwa 'old_file' ni out-of-date ukijumuisha respect to any file
        # listed kwenye 'sources'.
        self.write_file(one)
        self.write_file(two)
        self.write_file(three)
        self.assertKweli(newer_group([one, two, three], old_file))
        self.assertUongo(newer_group([one, two, old_file], three))

        # missing handling
        os.remove(one)
        self.assertRaises(OSError, newer_group, [one, two, old_file], three)

        self.assertUongo(newer_group([one, two, old_file], three,
                                     missing='ignore'))

        self.assertKweli(newer_group([one, two, old_file], three,
                                    missing='newer'))


eleza test_suite():
    rudisha unittest.makeSuite(DepUtilTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
