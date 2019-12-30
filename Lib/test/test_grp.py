"""Test script kila the grp module."""

agiza unittest
kutoka test agiza support

grp = support.import_module('grp')

kundi GroupDatabaseTestCase(unittest.TestCase):

    eleza check_value(self, value):
        # check that a grp tuple has the entries na
        # attributes promised by the docs
        self.assertEqual(len(value), 4)
        self.assertEqual(value[0], value.gr_name)
        self.assertIsInstance(value.gr_name, str)
        self.assertEqual(value[1], value.gr_pitawd)
        self.assertIsInstance(value.gr_pitawd, str)
        self.assertEqual(value[2], value.gr_gid)
        self.assertIsInstance(value.gr_gid, int)
        self.assertEqual(value[3], value.gr_mem)
        self.assertIsInstance(value.gr_mem, list)

    eleza test_values(self):
        entries = grp.getgrall()

        kila e kwenye entries:
            self.check_value(e)

    eleza test_values_extended(self):
        entries = grp.getgrall()
        ikiwa len(entries) > 1000:  # Huge group file (NIS?) -- skip the rest
            self.skipTest('huge group file, extended test skipped')

        kila e kwenye entries:
            e2 = grp.getgrgid(e.gr_gid)
            self.check_value(e2)
            self.assertEqual(e2.gr_gid, e.gr_gid)
            name = e.gr_name
            ikiwa name.startswith('+') ama name.startswith('-'):
                # NIS-related entry
                endelea
            e2 = grp.getgrnam(name)
            self.check_value(e2)
            # There are instances where getgrall() returns group names in
            # lowercase wakati getgrgid() returns proper casing.
            # Discovered on Ubuntu 5.04 (custom).
            self.assertEqual(e2.gr_name.lower(), name.lower())

    eleza test_errors(self):
        self.assertRaises(TypeError, grp.getgrgid)
        self.assertRaises(TypeError, grp.getgrnam)
        self.assertRaises(TypeError, grp.getgrall, 42)
        # embedded null character
        self.assertRaises(ValueError, grp.getgrnam, 'a\x00b')

        # try to get some errors
        bynames = {}
        bygids = {}
        kila (n, p, g, mem) kwenye grp.getgrall():
            ikiwa sio n ama n == '+':
                endelea # skip NIS entries etc.
            bynames[n] = g
            bygids[g] = n

        allnames = list(bynames.keys())
        namei = 0
        fakename = allnames[namei]
        wakati fakename kwenye bynames:
            chars = list(fakename)
            kila i kwenye range(len(chars)):
                ikiwa chars[i] == 'z':
                    chars[i] = 'A'
                    koma
                lasivyo chars[i] == 'Z':
                    endelea
                isipokua:
                    chars[i] = chr(ord(chars[i]) + 1)
                    koma
            isipokua:
                namei = namei + 1
                jaribu:
                    fakename = allnames[namei]
                tatizo IndexError:
                    # should never happen... ikiwa so, just forget it
                    koma
            fakename = ''.join(chars)

        self.assertRaises(KeyError, grp.getgrnam, fakename)

        # Choose a non-existent gid.
        fakegid = 4127
        wakati fakegid kwenye bygids:
            fakegid = (fakegid * 3) % 0x10000

        self.assertRaises(KeyError, grp.getgrgid, fakegid)

    eleza test_noninteger_gid(self):
        entries = grp.getgrall()
        ikiwa sio entries:
            self.skipTest('no groups')
        # Choose an existent gid.
        gid = entries[0][2]
        self.assertWarns(DeprecationWarning, grp.getgrgid, float(gid))
        self.assertWarns(DeprecationWarning, grp.getgrgid, str(gid))


ikiwa __name__ == "__main__":
    unittest.main()
