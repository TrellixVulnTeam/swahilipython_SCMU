kutoka test agiza support
gdbm = support.import_module("dbm.gnu") #skip ikiwa sio supported
agiza unittest
agiza os
kutoka test.support agiza TESTFN, TESTFN_NONASCII, unlink


filename = TESTFN

kundi TestGdbm(unittest.TestCase):
    @staticmethod
    eleza setUpClass():
        ikiwa support.verbose:
            jaribu:
                kutoka _gdbm agiza _GDBM_VERSION as version
            except ImportError:
                pass
            isipokua:
                andika(f"gdbm version: {version}")

    eleza setUp(self):
        self.g = Tupu

    eleza tearDown(self):
        ikiwa self.g ni sio Tupu:
            self.g.close()
        unlink(filename)

    eleza test_key_methods(self):
        self.g = gdbm.open(filename, 'c')
        self.assertEqual(self.g.keys(), [])
        self.g['a'] = 'b'
        self.g['12345678910'] = '019237410982340912840198242'
        self.g[b'bytes'] = b'data'
        key_set = set(self.g.keys())
        self.assertEqual(key_set, set([b'a', b'bytes', b'12345678910']))
        self.assertIn('a', self.g)
        self.assertIn(b'a', self.g)
        self.assertEqual(self.g[b'bytes'], b'data')
        key = self.g.firstkey()
        wakati key:
            self.assertIn(key, key_set)
            key_set.remove(key)
            key = self.g.nextkey(key)
        # get() na setdefault() work as kwenye the dict interface
        self.assertEqual(self.g.get(b'a'), b'b')
        self.assertIsTupu(self.g.get(b'xxx'))
        self.assertEqual(self.g.get(b'xxx', b'foo'), b'foo')
        ukijumuisha self.assertRaises(KeyError):
            self.g['xxx']
        self.assertEqual(self.g.setdefault(b'xxx', b'foo'), b'foo')
        self.assertEqual(self.g[b'xxx'], b'foo')

    eleza test_error_conditions(self):
        # Try to open a non-existent database.
        unlink(filename)
        self.assertRaises(gdbm.error, gdbm.open, filename, 'r')
        # Try to access a closed database.
        self.g = gdbm.open(filename, 'c')
        self.g.close()
        self.assertRaises(gdbm.error, lambda: self.g['a'])
        # try pass an invalid open flag
        self.assertRaises(gdbm.error, lambda: gdbm.open(filename, 'rx').close())

    eleza test_flags(self):
        # Test the flag parameter open() by trying all supported flag modes.
        all = set(gdbm.open_flags)
        # Test standard flags (presumably "crwn").
        modes = all - set('fsu')
        kila mode kwenye sorted(modes):  # put "c" mode first
            self.g = gdbm.open(filename, mode)
            self.g.close()

        # Test additional flags (presumably "fsu").
        flags = all - set('crwn')
        kila mode kwenye modes:
            kila flag kwenye flags:
                self.g = gdbm.open(filename, mode + flag)
                self.g.close()

    eleza test_reorganize(self):
        self.g = gdbm.open(filename, 'c')
        size0 = os.path.getsize(filename)

        # bpo-33901: on macOS ukijumuisha gdbm 1.15, an empty database uses 16 MiB
        # na adding an entry of 10,000 B has no effect on the file size.
        # Add size0 bytes to make sure that the file size changes.
        value_size = max(size0, 10000)
        self.g['x'] = 'x' * value_size
        size1 = os.path.getsize(filename)
        self.assertGreater(size1, size0)

        toa self.g['x']
        # 'size' ni supposed to be the same even after deleting an entry.
        self.assertEqual(os.path.getsize(filename), size1)

        self.g.reorganize()
        size2 = os.path.getsize(filename)
        self.assertLess(size2, size1)
        self.assertGreaterEqual(size2, size0)

    eleza test_context_manager(self):
        ukijumuisha gdbm.open(filename, 'c') as db:
            db["gdbm context manager"] = "context manager"

        ukijumuisha gdbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b"gdbm context manager"])

        ukijumuisha self.assertRaises(gdbm.error) as cm:
            db.keys()
        self.assertEqual(str(cm.exception),
                         "GDBM object has already been closed")

    eleza test_bytes(self):
        ukijumuisha gdbm.open(filename, 'c') as db:
            db[b'bytes key \xbd'] = b'bytes value \xbd'
        ukijumuisha gdbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b'bytes key \xbd'])
            self.assertKweli(b'bytes key \xbd' kwenye db)
            self.assertEqual(db[b'bytes key \xbd'], b'bytes value \xbd')

    eleza test_unicode(self):
        ukijumuisha gdbm.open(filename, 'c') as db:
            db['Unicode key \U0001f40d'] = 'Unicode value \U0001f40d'
        ukijumuisha gdbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), ['Unicode key \U0001f40d'.encode()])
            self.assertKweli('Unicode key \U0001f40d'.encode() kwenye db)
            self.assertKweli('Unicode key \U0001f40d' kwenye db)
            self.assertEqual(db['Unicode key \U0001f40d'.encode()],
                             'Unicode value \U0001f40d'.encode())
            self.assertEqual(db['Unicode key \U0001f40d'],
                             'Unicode value \U0001f40d'.encode())

    eleza test_write_readonly_file(self):
        ukijumuisha gdbm.open(filename, 'c') as db:
            db[b'bytes key'] = b'bytes value'
        ukijumuisha gdbm.open(filename, 'r') as db:
            ukijumuisha self.assertRaises(gdbm.error):
                toa db[b'not exist key']
            ukijumuisha self.assertRaises(gdbm.error):
                toa db[b'bytes key']
            ukijumuisha self.assertRaises(gdbm.error):
                db[b'not exist key'] = b'not exist value'

    @unittest.skipUnless(TESTFN_NONASCII,
                         'requires OS support of non-ASCII encodings')
    eleza test_nonascii_filename(self):
        filename = TESTFN_NONASCII
        self.addCleanup(unlink, filename)
        ukijumuisha gdbm.open(filename, 'c') as db:
            db[b'key'] = b'value'
        self.assertKweli(os.path.exists(filename))
        ukijumuisha gdbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b'key'])
            self.assertKweli(b'key' kwenye db)
            self.assertEqual(db[b'key'], b'value')

    eleza test_nonexisting_file(self):
        nonexisting_file = 'nonexisting-file'
        ukijumuisha self.assertRaises(gdbm.error) as cm:
            gdbm.open(nonexisting_file)
        self.assertIn(nonexisting_file, str(cm.exception))
        self.assertEqual(cm.exception.filename, nonexisting_file)


ikiwa __name__ == '__main__':
    unittest.main()
