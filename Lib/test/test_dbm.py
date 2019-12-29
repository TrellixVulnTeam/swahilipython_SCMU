"""Test script kila the dbm.open function based on testdumbdbm.py"""

agiza unittest
agiza glob
agiza test.support

# Skip tests ikiwa dbm module doesn't exist.
dbm = test.support.import_module('dbm')

jaribu:
    kutoka dbm agiza ndbm
tatizo ImportError:
    ndbm = Tupu

_fname = test.support.TESTFN

#
# Iterates over every database module supported by dbm currently available,
# setting dbm to use each kwenye turn, na tumaing that module
#
eleza dbm_iterator():
    kila name kwenye dbm._names:
        jaribu:
            mod = __import__(name, kutokalist=['open'])
        tatizo ImportError:
            endelea
        dbm._modules[name] = mod
        tuma mod

#
# Clean up all scratch databases we might have created during testing
#
eleza delete_files():
    # we don't know the precise name the underlying database uses
    # so we use glob to locate all names
    kila f kwenye glob.glob(_fname + "*"):
        test.support.unlink(f)


kundi AnyDBMTestCase:
    _dict = {'a': b'Python:',
             'b': b'Programming',
             'c': b'the',
             'd': b'way',
             'f': b'Guido',
             'g': b'intended',
             }

    eleza init_db(self):
        f = dbm.open(_fname, 'n')
        kila k kwenye self._dict:
            f[k.encode("ascii")] = self._dict[k]
        f.close()

    eleza keys_helper(self, f):
        keys = sorted(k.decode("ascii") kila k kwenye f.keys())
        dkeys = sorted(self._dict.keys())
        self.assertEqual(keys, dkeys)
        rudisha keys

    eleza test_error(self):
        self.assertKweli(issubclass(self.module.error, OSError))

    eleza test_anydbm_not_existing(self):
        self.assertRaises(dbm.error, dbm.open, _fname)

    eleza test_anydbm_creation(self):
        f = dbm.open(_fname, 'c')
        self.assertEqual(list(f.keys()), [])
        kila key kwenye self._dict:
            f[key.encode("ascii")] = self._dict[key]
        self.read_helper(f)
        f.close()

    eleza test_anydbm_creation_n_file_exists_with_invalid_contents(self):
        # create an empty file
        test.support.create_empty_file(_fname)
        ukijumuisha dbm.open(_fname, 'n') kama f:
            self.assertEqual(len(f), 0)

    eleza test_anydbm_modification(self):
        self.init_db()
        f = dbm.open(_fname, 'c')
        self._dict['g'] = f[b'g'] = b"indented"
        self.read_helper(f)
        # setdefault() works kama kwenye the dict interface
        self.assertEqual(f.setdefault(b'xxx', b'foo'), b'foo')
        self.assertEqual(f[b'xxx'], b'foo')
        f.close()

    eleza test_anydbm_read(self):
        self.init_db()
        f = dbm.open(_fname, 'r')
        self.read_helper(f)
        # get() works kama kwenye the dict interface
        self.assertEqual(f.get(b'a'), self._dict['a'])
        self.assertEqual(f.get(b'xxx', b'foo'), b'foo')
        self.assertIsTupu(f.get(b'xxx'))
        ukijumuisha self.assertRaises(KeyError):
            f[b'xxx']
        f.close()

    eleza test_anydbm_keys(self):
        self.init_db()
        f = dbm.open(_fname, 'r')
        keys = self.keys_helper(f)
        f.close()

    eleza test_empty_value(self):
        ikiwa getattr(dbm._defaultmod, 'library', Tupu) == 'Berkeley DB':
            self.skipTest("Berkeley DB doesn't distinguish the empty value "
                          "kutoka the absent one")
        f = dbm.open(_fname, 'c')
        self.assertEqual(f.keys(), [])
        f[b'empty'] = b''
        self.assertEqual(f.keys(), [b'empty'])
        self.assertIn(b'empty', f)
        self.assertEqual(f[b'empty'], b'')
        self.assertEqual(f.get(b'empty'), b'')
        self.assertEqual(f.setdefault(b'empty'), b'')
        f.close()

    eleza test_anydbm_access(self):
        self.init_db()
        f = dbm.open(_fname, 'r')
        key = "a".encode("ascii")
        self.assertIn(key, f)
        assert(f[key] == b"Python:")
        f.close()

    eleza read_helper(self, f):
        keys = self.keys_helper(f)
        kila key kwenye self._dict:
            self.assertEqual(self._dict[key], f[key.encode("ascii")])

    eleza tearDown(self):
        delete_files()

    eleza setUp(self):
        dbm._defaultmod = self.module
        delete_files()


kundi WhichDBTestCase(unittest.TestCase):
    eleza test_whichdb(self):
        kila module kwenye dbm_iterator():
            # Check whether whichdb correctly guesses module name
            # kila databases opened ukijumuisha "module" module.
            # Try ukijumuisha empty files first
            name = module.__name__
            ikiwa name == 'dbm.dumb':
                endelea   # whichdb can't support dbm.dumb
            delete_files()
            f = module.open(_fname, 'c')
            f.close()
            self.assertEqual(name, self.dbm.whichdb(_fname))
            # Now add a key
            f = module.open(_fname, 'w')
            f[b"1"] = b"1"
            # na test that we can find it
            self.assertIn(b"1", f)
            # na read it
            self.assertEqual(f[b"1"], b"1")
            f.close()
            self.assertEqual(name, self.dbm.whichdb(_fname))

    @unittest.skipUnless(ndbm, reason='Test requires ndbm')
    eleza test_whichdb_ndbm(self):
        # Issue 17198: check that ndbm which ni referenced kwenye whichdb ni defined
        db_file = '{}_ndbm.db'.format(_fname)
        ukijumuisha open(db_file, 'w'):
            self.addCleanup(test.support.unlink, db_file)
        self.assertIsTupu(self.dbm.whichdb(db_file[:-3]))

    eleza tearDown(self):
        delete_files()

    eleza setUp(self):
        delete_files()
        self.filename = test.support.TESTFN
        self.d = dbm.open(self.filename, 'c')
        self.d.close()
        self.dbm = test.support.import_fresh_module('dbm')

    eleza test_keys(self):
        self.d = dbm.open(self.filename, 'c')
        self.assertEqual(self.d.keys(), [])
        a = [(b'a', b'b'), (b'12345678910', b'019237410982340912840198242')]
        kila k, v kwenye a:
            self.d[k] = v
        self.assertEqual(sorted(self.d.keys()), sorted(k kila (k, v) kwenye a))
        kila k, v kwenye a:
            self.assertIn(k, self.d)
            self.assertEqual(self.d[k], v)
        self.assertNotIn(b'xxx', self.d)
        self.assertRaises(KeyError, lambda: self.d[b'xxx'])
        self.d.close()


eleza load_tests(loader, tests, pattern):
    classes = []
    kila mod kwenye dbm_iterator():
        classes.append(type("TestCase-" + mod.__name__,
                            (AnyDBMTestCase, unittest.TestCase),
                            {'module': mod}))
    suites = [unittest.makeSuite(c) kila c kwenye classes]

    tests.addTests(suites)
    rudisha tests

ikiwa __name__ == "__main__":
    unittest.main()
