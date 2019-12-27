kutoka __future__ agiza unicode_literals
agiza unittest


class Tests(unittest.TestCase):
    def test_unicode_literals(self):
        self.assertIsInstance("literal", str)


if __name__ == "__main__":
    unittest.main()
