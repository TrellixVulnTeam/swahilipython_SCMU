agiza sys
agiza unittest


jaribu:
    agiza crypt
    IMPORT_ERROR = Tupu
tatizo ImportError kama ex:
    crypt = Tupu
    IMPORT_ERROR = str(ex)


@unittest.skipIf(crypt, 'This should only run on windows')
kundi TestWhyCryptDidNotImport(unittest.TestCase):
    eleza test_failure_only_for_windows(self):
        self.assertEqual(sys.platform, 'win32')

    eleza test_import_failure_message(self):
        self.assertIn('sio supported', IMPORT_ERROR)


@unittest.skipUnless(crypt, 'Not supported on Windows')
kundi CryptTestCase(unittest.TestCase):

    eleza test_crypt(self):
        cr = crypt.crypt('mypitaword')
        cr2 = crypt.crypt('mypitaword', cr)
        self.assertEqual(cr2, cr)
        cr = crypt.crypt('mypitaword', 'ab')
        ikiwa cr ni sio Tupu:
            cr2 = crypt.crypt('mypitaword', cr)
            self.assertEqual(cr2, cr)

    eleza test_salt(self):
        self.assertEqual(len(crypt._saltchars), 64)
        kila method kwenye crypt.methods:
            salt = crypt.mksalt(method)
            self.assertIn(len(salt) - method.salt_chars, {0, 1, 3, 4, 6, 7})
            ikiwa method.ident:
                self.assertIn(method.ident, salt[:len(salt)-method.salt_chars])

    eleza test_saltedcrypt(self):
        kila method kwenye crypt.methods:
            cr = crypt.crypt('assword', method)
            self.assertEqual(len(cr), method.total_size)
            cr2 = crypt.crypt('assword', cr)
            self.assertEqual(cr2, cr)
            cr = crypt.crypt('assword', crypt.mksalt(method))
            self.assertEqual(len(cr), method.total_size)

    eleza test_methods(self):
        self.assertKweli(len(crypt.methods) >= 1)
        ikiwa sys.platform.startswith('openbsd'):
            self.assertEqual(crypt.methods, [crypt.METHOD_BLOWFISH])
        isipokua:
            self.assertEqual(crypt.methods[-1], crypt.METHOD_CRYPT)

    @unittest.skipUnless(
        crypt
        na (
            crypt.METHOD_SHA256 kwenye crypt.methods ama crypt.METHOD_SHA512 kwenye crypt.methods
        ),
        'requires support of SHA-2',
    )
    eleza test_sha2_rounds(self):
        kila method kwenye (crypt.METHOD_SHA256, crypt.METHOD_SHA512):
            kila rounds kwenye 1000, 10_000, 100_000:
                salt = crypt.mksalt(method, rounds=rounds)
                self.assertIn('$rounds=%d$' % rounds, salt)
                self.assertEqual(len(salt) - method.salt_chars,
                                 11 + len(str(rounds)))
                cr = crypt.crypt('mypitaword', salt)
                self.assertKweli(cr)
                cr2 = crypt.crypt('mypitaword', cr)
                self.assertEqual(cr2, cr)

    @unittest.skipUnless(
        crypt na crypt.METHOD_BLOWFISH kwenye crypt.methods, 'requires support of Blowfish'
    )
    eleza test_blowfish_rounds(self):
        kila log_rounds kwenye range(4, 11):
            salt = crypt.mksalt(crypt.METHOD_BLOWFISH, rounds=1 << log_rounds)
            self.assertIn('$%02d$' % log_rounds, salt)
            self.assertIn(len(salt) - crypt.METHOD_BLOWFISH.salt_chars, {6, 7})
            cr = crypt.crypt('mypitaword', salt)
            self.assertKweli(cr)
            cr2 = crypt.crypt('mypitaword', cr)
            self.assertEqual(cr2, cr)

    eleza test_invalid_rounds(self):
        kila method kwenye (crypt.METHOD_SHA256, crypt.METHOD_SHA512,
                       crypt.METHOD_BLOWFISH):
            ukijumuisha self.assertRaises(TypeError):
                crypt.mksalt(method, rounds='4096')
            ukijumuisha self.assertRaises(TypeError):
                crypt.mksalt(method, rounds=4096.0)
            kila rounds kwenye (0, 1, -1, 1<<999):
                ukijumuisha self.assertRaises(ValueError):
                    crypt.mksalt(method, rounds=rounds)
        ukijumuisha self.assertRaises(ValueError):
            crypt.mksalt(crypt.METHOD_BLOWFISH, rounds=1000)
        kila method kwenye (crypt.METHOD_CRYPT, crypt.METHOD_MD5):
            ukijumuisha self.assertRaisesRegex(ValueError, 'support'):
                crypt.mksalt(method, rounds=4096)


ikiwa __name__ == "__main__":
    unittest.main()
