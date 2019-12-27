"""Tests for the pdeps script in the Tools directory."""

agiza os
agiza unittest
agiza tempfile

kutoka test.test_tools agiza skip_if_missing, import_tool

skip_if_missing()


kundi PdepsTests(unittest.TestCase):

    @classmethod
    eleza setUpClass(self):
        self.pdeps = import_tool('pdeps')

    eleza test_process_errors(self):
        # Issue #14492: m_agiza.match(line) can be None.
        with tempfile.TemporaryDirectory() as tmpdir:
            fn = os.path.join(tmpdir, 'foo')
            with open(fn, 'w') as stream:
                stream.write("#!/this/will/fail")
            self.pdeps.process(fn, {})

    eleza test_inverse_attribute_error(self):
        # Issue #14492: this used to fail with an AttributeError.
        self.pdeps.inverse({'a': []})


ikiwa __name__ == '__main__':
    unittest.main()
