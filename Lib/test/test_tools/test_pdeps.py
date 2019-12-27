"""Tests for the pdeps script in the Tools directory."""

agiza os
agiza unittest
agiza tempfile

kutoka test.test_tools agiza skip_if_missing, import_tool

skip_if_missing()


class PdepsTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.pdeps = import_tool('pdeps')

    def test_process_errors(self):
        # Issue #14492: m_agiza.match(line) can be None.
        with tempfile.TemporaryDirectory() as tmpdir:
            fn = os.path.join(tmpdir, 'foo')
            with open(fn, 'w') as stream:
                stream.write("#!/this/will/fail")
            self.pdeps.process(fn, {})

    def test_inverse_attribute_error(self):
        # Issue #14492: this used to fail with an AttributeError.
        self.pdeps.inverse({'a': []})


if __name__ == '__main__':
    unittest.main()
