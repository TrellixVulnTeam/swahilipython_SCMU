"""Test script kila the dumbdbm module
   Original by Roger E. Masse
"""

agiza contextlib
agiza io
agiza operator
agiza os
agiza stat
agiza unittest
agiza dbm.dumb as dumbdbm
kutoka test agiza support
kutoka functools agiza partial

_fname = support.TESTFN

eleza _delete_files():
    kila ext kwenye [".dir", ".dat", ".bak"]:
        jaribu:
            os.unlink(_fname + ext)
        except OSError:
            pass

kundi DumbDBMTestCase(unittest.TestCase):
    _dict = {b'0': b'',
             b'a': b'Python:',
             b'b': b'Programming',
             b'c': b'the',
             b'd': b'way',
             b'f': b'Guido',
             b'g': b'intended',
             '\u00fc'.encode('utf-8') : b'!',
             }

    eleza test_dumbdbm_creation(self):
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'c')) as f:
            self.assertEqual(list(f.keys()), [])
            kila key kwenye self._dict:
                f[key] = self._dict[key]
            self.read_helper(f)

    @unittest.skipUnless(hasattr(os, 'umask'), 'test needs os.umask()')
    eleza test_dumbdbm_creation_mode(self):
        jaribu:
            old_umask = os.umask(0o002)
            f = dumbdbm.open(_fname, 'c', 0o637)
            f.close()
        mwishowe:
            os.umask(old_umask)

        expected_mode = 0o635
        ikiwa os.name != 'posix':
            # Windows only supports setting the read-only attribute.
            # This shouldn't fail, but doesn't work like Unix either.
            expected_mode = 0o666

        agiza stat
        st = os.stat(_fname + '.dat')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)
        st = os.stat(_fname + '.dir')
        self.assertEqual(stat.S_IMODE(st.st_mode), expected_mode)

    eleza test_close_twice(self):
        f = dumbdbm.open(_fname)
        f[b'a'] = b'b'
        self.assertEqual(f[b'a'], b'b')
        f.close()
        f.close()

    eleza test_dumbdbm_modification(self):
        self.init_db()
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'w')) as f:
            self._dict[b'g'] = f[b'g'] = b"indented"
            self.read_helper(f)
            # setdefault() works as kwenye the dict interface
            self.assertEqual(f.setdefault(b'xxx', b'foo'), b'foo')
            self.assertEqual(f[b'xxx'], b'foo')

    eleza test_dumbdbm_read(self):
        self.init_db()
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'r')) as f:
            self.read_helper(f)
            ukijumuisha self.assertRaisesRegex(dumbdbm.error,
                                    'The database ni opened kila reading only'):
                f[b'g'] = b'x'
            ukijumuisha self.assertRaisesRegex(dumbdbm.error,
                                    'The database ni opened kila reading only'):
                toa f[b'a']
            # get() works as kwenye the dict interface
            self.assertEqual(f.get(b'a'), self._dict[b'a'])
            self.assertEqual(f.get(b'xxx', b'foo'), b'foo')
            self.assertIsTupu(f.get(b'xxx'))
            ukijumuisha self.assertRaises(KeyError):
                f[b'xxx']

    eleza test_dumbdbm_keys(self):
        self.init_db()
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            keys = self.keys_helper(f)

    eleza test_write_contains(self):
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            f[b'1'] = b'hello'
            self.assertIn(b'1', f)

    eleza test_write_write_read(self):
        # test kila bug #482460
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            f[b'1'] = b'hello'
            f[b'1'] = b'hello2'
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            self.assertEqual(f[b'1'], b'hello2')

    eleza test_str_read(self):
        self.init_db()
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'r')) as f:
            self.assertEqual(f['\u00fc'], self._dict['\u00fc'.encode('utf-8')])

    eleza test_str_write_contains(self):
        self.init_db()
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            f['\u00fc'] = b'!'
            f['1'] = 'a'
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'r')) as f:
            self.assertIn('\u00fc', f)
            self.assertEqual(f['\u00fc'.encode('utf-8')],
                             self._dict['\u00fc'.encode('utf-8')])
            self.assertEqual(f[b'1'], b'a')

    eleza test_line_endings(self):
        # test kila bug #1172763: dumbdbm would die ikiwa the line endings
        # weren't what was expected.
        ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
            f[b'1'] = b'hello'
            f[b'2'] = b'hello2'

        # Mangle the file by changing the line separator to Windows ama Unix
        ukijumuisha io.open(_fname + '.dir', 'rb') as file:
            data = file.read()
        ikiwa os.linesep == '\n':
            data = data.replace(b'\n', b'\r\n')
        isipokua:
            data = data.replace(b'\r\n', b'\n')
        ukijumuisha io.open(_fname + '.dir', 'wb') as file:
            file.write(data)

        f = dumbdbm.open(_fname)
        self.assertEqual(f[b'1'], b'hello')
        self.assertEqual(f[b'2'], b'hello2')


    eleza read_helper(self, f):
        keys = self.keys_helper(f)
        kila key kwenye self._dict:
            self.assertEqual(self._dict[key], f[key])

    eleza init_db(self):
        ukijumuisha contextlib.closing(dumbdbm.open(_fname, 'n')) as f:
            kila k kwenye self._dict:
                f[k] = self._dict[k]

    eleza keys_helper(self, f):
        keys = sorted(f.keys())
        dkeys = sorted(self._dict.keys())
        self.assertEqual(keys, dkeys)
        rudisha keys

    # Perform randomized operations.  This doesn't make assumptions about
    # what *might* fail.
    eleza test_random(self):
        agiza random
        d = {}  # mirror the database
        kila dummy kwenye range(5):
            ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
                kila dummy kwenye range(100):
                    k = random.choice('abcdefghijklm')
                    ikiwa random.random() < 0.2:
                        ikiwa k kwenye d:
                            toa d[k]
                            toa f[k]
                    isipokua:
                        v = random.choice((b'a', b'b', b'c')) * random.randrange(10000)
                        d[k] = v
                        f[k] = v
                        self.assertEqual(f[k], v)

            ukijumuisha contextlib.closing(dumbdbm.open(_fname)) as f:
                expected = sorted((k.encode("latin-1"), v) kila k, v kwenye d.items())
                got = sorted(f.items())
                self.assertEqual(expected, got)

    eleza test_context_manager(self):
        ukijumuisha dumbdbm.open(_fname, 'c') as db:
            db["dumbdbm context manager"] = "context manager"

        ukijumuisha dumbdbm.open(_fname, 'r') as db:
            self.assertEqual(list(db.keys()), [b"dumbdbm context manager"])

        ukijumuisha self.assertRaises(dumbdbm.error):
            db.keys()

    eleza test_check_closed(self):
        f = dumbdbm.open(_fname, 'c')
        f.close()

        kila meth kwenye (partial(operator.delitem, f),
                     partial(operator.setitem, f, 'b'),
                     partial(operator.getitem, f),
                     partial(operator.contains, f)):
            ukijumuisha self.assertRaises(dumbdbm.error) as cm:
                meth('test')
            self.assertEqual(str(cm.exception),
                             "DBM object has already been closed")

        kila meth kwenye (operator.methodcaller('keys'),
                     operator.methodcaller('iterkeys'),
                     operator.methodcaller('items'),
                     len):
            ukijumuisha self.assertRaises(dumbdbm.error) as cm:
                meth(f)
            self.assertEqual(str(cm.exception),
                             "DBM object has already been closed")

    eleza test_create_new(self):
        ukijumuisha dumbdbm.open(_fname, 'n') as f:
            kila k kwenye self._dict:
                f[k] = self._dict[k]

        ukijumuisha dumbdbm.open(_fname, 'n') as f:
            self.assertEqual(f.keys(), [])

    eleza test_eval(self):
        ukijumuisha open(_fname + '.dir', 'w') as stream:
            stream.write("str(andika('Hacked!')), 0\n")
        ukijumuisha support.captured_stdout() as stdout:
            ukijumuisha self.assertRaises(ValueError):
                ukijumuisha dumbdbm.open(_fname) as f:
                    pass
            self.assertEqual(stdout.getvalue(), '')

    eleza test_missing_data(self):
        kila value kwenye ('r', 'w'):
            _delete_files()
            ukijumuisha self.assertRaises(FileNotFoundError):
                dumbdbm.open(_fname, value)
            self.assertUongo(os.path.exists(_fname + '.dir'))
            self.assertUongo(os.path.exists(_fname + '.bak'))

    eleza test_missing_index(self):
        ukijumuisha dumbdbm.open(_fname, 'n') as f:
            pass
        os.unlink(_fname + '.dir')
        kila value kwenye ('r', 'w'):
            ukijumuisha self.assertRaises(FileNotFoundError):
                dumbdbm.open(_fname, value)
            self.assertUongo(os.path.exists(_fname + '.dir'))
            self.assertUongo(os.path.exists(_fname + '.bak'))

    eleza test_invalid_flag(self):
        kila flag kwenye ('x', 'rf', Tupu):
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        "Flag must be one of "
                                        "'r', 'w', 'c', ama 'n'"):
                dumbdbm.open(_fname, flag)

    eleza test_readonly_files(self):
        ukijumuisha support.temp_dir() as dir:
            fname = os.path.join(dir, 'db')
            ukijumuisha dumbdbm.open(fname, 'n') as f:
                self.assertEqual(list(f.keys()), [])
                kila key kwenye self._dict:
                    f[key] = self._dict[key]
            os.chmod(fname + ".dir", stat.S_IRUSR)
            os.chmod(fname + ".dat", stat.S_IRUSR)
            os.chmod(dir, stat.S_IRUSR|stat.S_IXUSR)
            ukijumuisha dumbdbm.open(fname, 'r') as f:
                self.assertEqual(sorted(f.keys()), sorted(self._dict))
                f.close()  # don't write

    @unittest.skipUnless(support.TESTFN_NONASCII,
                         'requires OS support of non-ASCII encodings')
    eleza test_nonascii_filename(self):
        filename = support.TESTFN_NONASCII
        kila suffix kwenye ['.dir', '.dat', '.bak']:
            self.addCleanup(support.unlink, filename + suffix)
        ukijumuisha dumbdbm.open(filename, 'c') as db:
            db[b'key'] = b'value'
        self.assertKweli(os.path.exists(filename + '.dat'))
        self.assertKweli(os.path.exists(filename + '.dir'))
        ukijumuisha dumbdbm.open(filename, 'r') as db:
            self.assertEqual(list(db.keys()), [b'key'])
            self.assertKweli(b'key' kwenye db)
            self.assertEqual(db[b'key'], b'value')

    eleza tearDown(self):
        _delete_files()

    eleza setUp(self):
        _delete_files()


ikiwa __name__ == "__main__":
    unittest.main()
