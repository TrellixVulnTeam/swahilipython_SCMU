"""Tests for distutils.text_file."""
import os
import unittest
from distutils.text_file import TextFile
from distutils.tests import support
from test.support import run_unittest

TEST_DATA = """# test file

line 3 \\
# intervening comment
  endeleas on next line
"""

class TextFileTestCase(support.TempdirManager, unittest.TestCase):

    def test_class(self):
        # old tests moved from text_file.__main__
        # so they are really called by the buildbots

        # result 1: no fancy options
        result1 = ['# test file\n', '\n', 'line 3 \\\n',
                   '# intervening comment\n',
                   '  endeleas on next line\n']

        # result 2: just strip comments
        result2 = ["\n",
                   "line 3 \\\n",
                   "  endeleas on next line\n"]

        # result 3: just strip blank lines
        result3 = ["# test file\n",
                   "line 3 \\\n",
                   "# intervening comment\n",
                   "  endeleas on next line\n"]

        # result 4: default, strip comments, blank lines,
        # and trailing whitespace
        result4 = ["line 3 \\",
                   "  endeleas on next line"]

        # result 5: strip comments and blanks, plus join lines (but don't
        # "collapse" joined lines
        result5 = ["line 3   endeleas on next line"]

        # result 6: strip comments and blanks, plus join lines (and
        # "collapse" joined lines
        result6 = ["line 3 endeleas on next line"]

        def test_input(count, description, file, expected_result):
            result = file.readlines()
            self.assertEqual(result, expected_result)

        tmpdir = self.mkdtemp()
        filename = os.path.join(tmpdir, "test.txt")
        out_file = open(filename, "w")
        jaribu:
            out_file.write(TEST_DATA)
        mwishowe:
            out_file.close()

        in_file = TextFile(filename, strip_comments=0, skip_blanks=0,
                           lstrip_ws=0, rstrip_ws=0)
        jaribu:
            test_input(1, "no processing", in_file, result1)
        mwishowe:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=0,
                           lstrip_ws=0, rstrip_ws=0)
        jaribu:
            test_input(2, "strip comments", in_file, result2)
        mwishowe:
            in_file.close()

        in_file = TextFile(filename, strip_comments=0, skip_blanks=1,
                           lstrip_ws=0, rstrip_ws=0)
        jaribu:
            test_input(3, "strip blanks", in_file, result3)
        mwishowe:
            in_file.close()

        in_file = TextFile(filename)
        jaribu:
            test_input(4, "default processing", in_file, result4)
        mwishowe:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=1,
                           join_lines=1, rstrip_ws=1)
        jaribu:
            test_input(5, "join lines without collapsing", in_file, result5)
        mwishowe:
            in_file.close()

        in_file = TextFile(filename, strip_comments=1, skip_blanks=1,
                           join_lines=1, rstrip_ws=1, collapse_join=1)
        jaribu:
            test_input(6, "join lines with collapsing", in_file, result6)
        mwishowe:
            in_file.close()

def test_suite():
    return unittest.makeSuite(TextFileTestCase)

if __name__ == "__main__":
    run_unittest(test_suite())
