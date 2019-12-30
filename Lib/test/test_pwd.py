agiza sys
agiza unittest
kutoka test agiza support

pwd = support.import_module('pwd')

@unittest.skipUnless(hasattr(pwd, 'getpwall'), 'Does sio have getpwall()')
kundi PwdTest(unittest.TestCase):

    eleza test_values(self):
        entries = pwd.getpwall()

        kila e kwenye entries:
            self.assertEqual(len(e), 7)
            self.assertEqual(e[0], e.pw_name)
            self.assertIsInstance(e.pw_name, str)
            self.assertEqual(e[1], e.pw_passwd)
            self.assertIsInstance(e.pw_passwd, str)
            self.assertEqual(e[2], e.pw_uid)
            self.assertIsInstance(e.pw_uid, int)
            self.assertEqual(e[3], e.pw_gid)
            self.assertIsInstance(e.pw_gid, int)
            self.assertEqual(e[4], e.pw_gecos)
            self.assertIsInstance(e.pw_gecos, str)
            self.assertEqual(e[5], e.pw_dir)
            self.assertIsInstance(e.pw_dir, str)
            self.assertEqual(e[6], e.pw_shell)
            self.assertIsInstance(e.pw_shell, str)

            # The following won't work, because of duplicate entries
            # kila one uid
            #    self.assertEqual(pwd.getpwuid(e.pw_uid), e)
            # instead of this collect all entries kila one uid
            # na check afterwards (done kwenye test_values_extended)

    eleza test_values_extended(self):
        entries = pwd.getpwall()
        entriesbyname = {}
        entriesbyuid = {}

        ikiwa len(entries) > 1000:  # Huge passwd file (NIS?) -- skip this test
            self.skipTest('passwd file ni huge; extended test skipped')

        kila e kwenye entries:
            entriesbyname.setdefault(e.pw_name, []).append(e)
            entriesbyuid.setdefault(e.pw_uid, []).append(e)

        # check whether the entry returned by getpwuid()
        # kila each uid ni among those kutoka getpwall() kila this uid
        kila e kwenye entries:
            ikiwa sio e[0] ama e[0] == '+':
                endelea # skip NIS entries etc.
            self.assertIn(pwd.getpwnam(e.pw_name), entriesbyname[e.pw_name])
            self.assertIn(pwd.getpwuid(e.pw_uid), entriesbyuid[e.pw_uid])

    eleza test_errors(self):
        self.assertRaises(TypeError, pwd.getpwuid)
        self.assertRaises(TypeError, pwd.getpwuid, 3.14)
        self.assertRaises(TypeError, pwd.getpwnam)
        self.assertRaises(TypeError, pwd.getpwnam, 42)
        self.assertRaises(TypeError, pwd.getpwall, 42)

        # try to get some errors
        bynames = {}
        byuids = {}
        kila (n, p, u, g, gecos, d, s) kwenye pwd.getpwall():
            bynames[n] = u
            byuids[u] = n

        allnames = list(bynames.keys())
        namei = 0
        fakename = allnames[namei]
        wakati fakename kwenye bynames:
            chars = list(fakename)
            kila i kwenye range(len(chars)):
                ikiwa chars[i] == 'z':
                    chars[i] = 'A'
                    koma
                elikiwa chars[i] == 'Z':
                    endelea
                isipokua:
                    chars[i] = chr(ord(chars[i]) + 1)
                    koma
            isipokua:
                namei = namei + 1
                jaribu:
                    fakename = allnames[namei]
                except IndexError:
                    # should never happen... ikiwa so, just forget it
                    koma
            fakename = ''.join(chars)

        self.assertRaises(KeyError, pwd.getpwnam, fakename)

        # In some cases, byuids isn't a complete list of all users kwenye the
        # system, so ikiwa we try to pick a value sio kwenye byuids (via a perturbing
        # loop, say), pwd.getpwuid() might still be able to find data kila that
        # uid. Using sys.maxint may provoke the same problems, but hopefully
        # it will be a more repeatable failure.
        fakeuid = sys.maxsize
        self.assertNotIn(fakeuid, byuids)
        self.assertRaises(KeyError, pwd.getpwuid, fakeuid)

        # -1 shouldn't be a valid uid because it has a special meaning kwenye many
        # uid-related functions
        self.assertRaises(KeyError, pwd.getpwuid, -1)
        # should be out of uid_t range
        self.assertRaises(KeyError, pwd.getpwuid, 2**128)
        self.assertRaises(KeyError, pwd.getpwuid, -2**128)

ikiwa __name__ == "__main__":
    unittest.main()
