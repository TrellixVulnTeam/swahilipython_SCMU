# Check that multiple features can be enabled.
kutoka __future__ agiza unicode_literals, print_function

agiza sys
agiza unittest
kutoka test agiza support


kundi TestMultipleFeatures(unittest.TestCase):

    eleza test_unicode_literals(self):
        self.assertIsInstance("", str)

    eleza test_print_function(self):
        ukijumuisha support.captured_output("stderr") as s:
            andika("foo", file=sys.stderr)
        self.assertEqual(s.getvalue(), "foo\n")


ikiwa __name__ == '__main__':
    unittest.main()
