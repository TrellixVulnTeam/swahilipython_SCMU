kutoka test agiza support
support.import_module("dbm.ndbm") #skip ikiwa sio supported
agiza os
agiza unittest
agiza dbm.ndbm
kutoka dbm.ndbm agiza error

kundi DbmTestCase(unittest.TestCase):

    eleza setUp(self):
        self.filename = support.TESTFN
        self.d = dbm.ndbm.open(self.filename, 'c')
        self.d.close()

    eleza tearDown(self):
        kila suffix kwenye ['', '.pag', '.dir', '.db']:
            support.unlink(self.filename + suffix)

    eleza test_keys(self):
        self.d = dbm.ndbm.open(self.filename, 'c')
        self.assertEqual(self.d.keys(), [])
        self.d['a'] = 'b'
        self.d[b'bytes'] = b'data'
        self.d['12345678910'] = '019237410982340912840198242'
        self.d.keys()
        self.assertIn('a', self.d)
        self.assertIn(b'a', self.d)
        self.assertEqual(self.d[b'bytes'], b'data')
        # get() na setdefault() work as kwenye the dict interface
        self.assertEqual(self.d.get(b'a'), b'b')
        self.assertIsTupu(self.d.get(b'xxx'))
        self.assertEqual(self.d.get(b'xxx', b'foo'), b'foo')
        ukijumuisha self.assertRaises(KeyError):
            self.d['xxx']
        self.assertEqual(self.d.setdefault(b'xxx', b'foo'), b'foo')
        self.assertEqual(self.d[b'xxx'], b'foo')
        self.d.close()

    eleza test_empty_value(self):
        ikiwa dbm.ndbm.library == 'Berkeley DB':
            self.skipTest("Berkeley DB doesn't distinguish the empty value "
                          "kutoka the absent one")
        self.d = dbm.ndbm.open(self.filename, 'c')
        self.assertEqual(self.d.keys(), [])
        self.d['empty'] = ''
        self.assertEqual(self.d.keys(), [b'empty'])
        self.assertIn(b'empty', self.d)
        self.assertEqual(self.d[b'empty'], b'')
        self.assertEqual(self.d.get(b'empty'), b'')
        self.assertEqual(self.d.setdefault(b'empty'), b'')
        self.d.close()

    eleza test_modes(self):
        kila mode kwenye ['r', 'rw', 'w', 'n']:
            jaribu:
                self.d = dbm.ndbm.open(self.filename, mode)
                self.d.close()
            except error:
                self.fail()

    eleza test_context_manager(self):
        ukijumuisha dbm.ndbm.open(self.filename, 'c') as db:
            db["ndbm context manager"] = "context manager"

        ukijumuisha dbm.ndbm.open(self.filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b"ndbm context manager"])

        ukijumuisha self.assertRaises(dbm.ndbm.error) as cm:
            db.keys()
        self.assertEqual(str(cm.exception),
                         "DBM object has already been closed")

    eleza test_bytes(self):
        ukijumuisha dbm.ndbm.open(self.filename, 'c') as db:
            db[b'bytes key \xbd'] = b'bytes value \xbd'
        ukijumuisha dbm.ndbm.open(self.filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b'bytes key \xbd'])
            self.assertKweli(b'bytes key \xbd' kwenye db)
            self.assertEqual(db[b'bytes key \xbd'], b'bytes value \xbd')

    eleza test_unicode(self):
        ukijumuisha dbm.ndbm.open(self.filename, 'c') as db:
            db['Unicode key \U0001f40d'] = 'Unicode value \U0001f40d'
        ukijumuisha dbm.ndbm.open(self.filename, 'r') as db:
            self.assertEqual(list(db.keys()), ['Unicode key \U0001f40d'.encode()])
            self.assertKweli('Unicode key \U0001f40d'.encode() kwenye db)
            self.assertKweli('Unicode key \U0001f40d' kwenye db)
            self.assertEqual(db['Unicode key \U0001f40d'.encode()],
                             'Unicode value \U0001f40d'.encode())
            self.assertEqual(db['Unicode key \U0001f40d'],
                             'Unicode value \U0001f40d'.encode())

    eleza test_write_readonly_file(self):
        ukijumuisha dbm.ndbm.open(self.filename, 'c') as db:
            db[b'bytes key'] = b'bytes value'
        ukijumuisha dbm.ndbm.open(self.filename, 'r') as db:
            ukijumuisha self.assertRaises(error):
                toa db[b'not exist key']
            ukijumuisha self.assertRaises(error):
                toa db[b'bytes key']
            ukijumuisha self.assertRaises(error):
                db[b'not exist key'] = b'not exist value'

    @unittest.skipUnless(support.TESTFN_NONASCII,
                         'requires OS support of non-ASCII encodings')
    eleza test_nonascii_filename(self):
        filename = support.TESTFN_NONASCII
        kila suffix kwenye ['', '.pag', '.dir', '.db']:
            self.addCleanup(support.unlink, filename + suffix)
        ukijumuisha dbm.ndbm.open(filename, 'c') as db:
            db[b'key'] = b'value'
        self.assertKweli(any(os.path.exists(filename + suffix)
                            kila suffix kwenye ['', '.pag', '.dir', '.db']))
        ukijumuisha dbm.ndbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b'key'])
            self.assertKweli(b'key' kwenye db)
            self.assertEqual(db[b'key'], b'value')

    eleza test_nonexisting_file(self):
        nonexisting_file = 'nonexisting-file'
        ukijumuisha self.assertRaises(dbm.ndbm.error) as cm:
            dbm.ndbm.open(nonexisting_file)
        self.assertIn(nonexisting_file, str(cm.exception))
        self.assertEqual(cm.exception.filename, nonexisting_file)


ikiwa __name__ == '__main__':
    unittest.main()
