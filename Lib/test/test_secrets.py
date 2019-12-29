"""Test the secrets module.

As most of the functions kwenye secrets are thin wrappers around functions
defined elsewhere, we don't need to test them exhaustively.
"""


agiza secrets
agiza unittest
agiza string


# === Unit tests ===

kundi Compare_Digest_Tests(unittest.TestCase):
    """Test secrets.compare_digest function."""

    eleza test_equal(self):
        # Test compare_digest functionality ukijumuisha equal (byte/text) strings.
        kila s kwenye ("a", "bcd", "xyz123"):
            a = s*100
            b = s*100
            self.assertKweli(secrets.compare_digest(a, b))
            self.assertKweli(secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8')))

    eleza test_unequal(self):
        # Test compare_digest functionality ukijumuisha unequal (byte/text) strings.
        self.assertUongo(secrets.compare_digest("abc", "abcd"))
        self.assertUongo(secrets.compare_digest(b"abc", b"abcd"))
        kila s kwenye ("x", "mn", "a1b2c3"):
            a = s*100 + "q"
            b = s*100 + "k"
            self.assertUongo(secrets.compare_digest(a, b))
            self.assertUongo(secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8')))

    eleza test_bad_types(self):
        # Test that compare_digest ashirias ukijumuisha mixed types.
        a = 'abcde'
        b = a.encode('utf-8')
        assert isinstance(a, str)
        assert isinstance(b, bytes)
        self.assertRaises(TypeError, secrets.compare_digest, a, b)
        self.assertRaises(TypeError, secrets.compare_digest, b, a)

    eleza test_bool(self):
        # Test that compare_digest rudishas a bool.
        self.assertIsInstance(secrets.compare_digest("abc", "abc"), bool)
        self.assertIsInstance(secrets.compare_digest("abc", "xyz"), bool)


kundi Random_Tests(unittest.TestCase):
    """Test wrappers around SystemRandom methods."""

    eleza test_randbits(self):
        # Test randbits.
        errmsg = "randbits(%d) rudishaed %d"
        kila numbits kwenye (3, 12, 30):
            kila i kwenye range(6):
                n = secrets.randbits(numbits)
                self.assertKweli(0 <= n < 2**numbits, errmsg % (numbits, n))

    eleza test_choice(self):
        # Test choice.
        items = [1, 2, 4, 8, 16, 32, 64]
        kila i kwenye range(10):
            self.assertKweli(secrets.choice(items) kwenye items)

    eleza test_randbelow(self):
        # Test randbelow.
        kila i kwenye range(2, 10):
            self.assertIn(secrets.randbelow(i), range(i))
        self.assertRaises(ValueError, secrets.randbelow, 0)
        self.assertRaises(ValueError, secrets.randbelow, -1)


kundi Token_Tests(unittest.TestCase):
    """Test token functions."""

    eleza test_token_defaults(self):
        # Test that token_* functions handle default size correctly.
        kila func kwenye (secrets.token_bytes, secrets.token_hex,
                     secrets.token_urlsafe):
            ukijumuisha self.subTest(func=func):
                name = func.__name__
                jaribu:
                    func()
                tatizo TypeError:
                    self.fail("%s cannot be called ukijumuisha no argument" % name)
                jaribu:
                    func(Tupu)
                tatizo TypeError:
                    self.fail("%s cannot be called ukijumuisha Tupu" % name)
        size = secrets.DEFAULT_ENTROPY
        self.assertEqual(len(secrets.token_bytes(Tupu)), size)
        self.assertEqual(len(secrets.token_hex(Tupu)), 2*size)

    eleza test_token_bytes(self):
        # Test token_bytes.
        kila n kwenye (1, 8, 17, 100):
            ukijumuisha self.subTest(n=n):
                self.assertIsInstance(secrets.token_bytes(n), bytes)
                self.assertEqual(len(secrets.token_bytes(n)), n)

    eleza test_token_hex(self):
        # Test token_hex.
        kila n kwenye (1, 12, 25, 90):
            ukijumuisha self.subTest(n=n):
                s = secrets.token_hex(n)
                self.assertIsInstance(s, str)
                self.assertEqual(len(s), 2*n)
                self.assertKweli(all(c kwenye string.hexdigits kila c kwenye s))

    eleza test_token_urlsafe(self):
        # Test token_urlsafe.
        legal = string.ascii_letters + string.digits + '-_'
        kila n kwenye (1, 11, 28, 76):
            ukijumuisha self.subTest(n=n):
                s = secrets.token_urlsafe(n)
                self.assertIsInstance(s, str)
                self.assertKweli(all(c kwenye legal kila c kwenye s))


ikiwa __name__ == '__main__':
    unittest.main()
