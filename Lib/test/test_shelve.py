agiza unittest
agiza shelve
agiza glob
kutoka test agiza support
kutoka collections.abc agiza MutableMapping
kutoka test.test_dbm agiza dbm_iterator

eleza L1(s):
    rudisha s.decode("latin-1")

kundi byteskeydict(MutableMapping):
    "Mapping that supports bytes keys"

    eleza __init__(self):
        self.d = {}

    eleza __getitem__(self, key):
        rudisha self.d[L1(key)]

    eleza __setitem__(self, key, value):
        self.d[L1(key)] = value

    eleza __delitem__(self, key):
        del self.d[L1(key)]

    eleza __len__(self):
        rudisha len(self.d)

    eleza iterkeys(self):
        for k in self.d.keys():
            yield k.encode("latin-1")

    __iter__ = iterkeys

    eleza keys(self):
        rudisha list(self.iterkeys())

    eleza copy(self):
        rudisha byteskeydict(self.d)


kundi TestCase(unittest.TestCase):

    fn = "shelftemp.db"

    eleza tearDown(self):
        for f in glob.glob(self.fn+"*"):
            support.unlink(f)

    eleza test_close(self):
        d1 = {}
        s = shelve.Shelf(d1, protocol=2, writeback=False)
        s['key1'] = [1,2,3,4]
        self.assertEqual(s['key1'], [1,2,3,4])
        self.assertEqual(len(s), 1)
        s.close()
        self.assertRaises(ValueError, len, s)
        try:
            s['key1']
        except ValueError:
            pass
        else:
            self.fail('Closed shelf should not find a key')

    eleza test_ascii_file_shelf(self):
        s = shelve.open(self.fn, protocol=0)
        try:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        finally:
            s.close()

    eleza test_binary_file_shelf(self):
        s = shelve.open(self.fn, protocol=1)
        try:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        finally:
            s.close()

    eleza test_proto2_file_shelf(self):
        s = shelve.open(self.fn, protocol=2)
        try:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        finally:
            s.close()

    eleza test_in_memory_shelf(self):
        d1 = byteskeydict()
        with shelve.Shelf(d1, protocol=0) as s:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))
        d2 = byteskeydict()
        with shelve.Shelf(d2, protocol=1) as s:
            s['key1'] = (1,2,3,4)
            self.assertEqual(s['key1'], (1,2,3,4))

        self.assertEqual(len(d1), 1)
        self.assertEqual(len(d2), 1)
        self.assertNotEqual(d1.items(), d2.items())

    eleza test_mutable_entry(self):
        d1 = byteskeydict()
        with shelve.Shelf(d1, protocol=2, writeback=False) as s:
            s['key1'] = [1,2,3,4]
            self.assertEqual(s['key1'], [1,2,3,4])
            s['key1'].append(5)
            self.assertEqual(s['key1'], [1,2,3,4])

        d2 = byteskeydict()
        with shelve.Shelf(d2, protocol=2, writeback=True) as s:
            s['key1'] = [1,2,3,4]
            self.assertEqual(s['key1'], [1,2,3,4])
            s['key1'].append(5)
            self.assertEqual(s['key1'], [1,2,3,4,5])

        self.assertEqual(len(d1), 1)
        self.assertEqual(len(d2), 1)

    eleza test_keyencoding(self):
        d = {}
        key = 'PÃ¶p'
        # the default keyencoding is utf-8
        shelve.Shelf(d)[key] = [1]
        self.assertIn(key.encode('utf-8'), d)
        # but a different one can be given
        shelve.Shelf(d, keyencoding='latin-1')[key] = [1]
        self.assertIn(key.encode('latin-1'), d)
        # with all consequences
        s = shelve.Shelf(d, keyencoding='ascii')
        self.assertRaises(UnicodeEncodeError, s.__setitem__, key, [1])

    eleza test_writeback_also_writes_immediately(self):
        # Issue 5754
        d = {}
        key = 'key'
        encodedkey = key.encode('utf-8')
        with shelve.Shelf(d, writeback=True) as s:
            s[key] = [1]
            p1 = d[encodedkey]  # Will give a KeyError ikiwa backing store not updated
            s['key'].append(2)
        p2 = d[encodedkey]
        self.assertNotEqual(p1, p2)  # Write creates new object in store

    eleza test_with(self):
        d1 = {}
        with shelve.Shelf(d1, protocol=2, writeback=False) as s:
            s['key1'] = [1,2,3,4]
            self.assertEqual(s['key1'], [1,2,3,4])
            self.assertEqual(len(s), 1)
        self.assertRaises(ValueError, len, s)
        try:
            s['key1']
        except ValueError:
            pass
        else:
            self.fail('Closed shelf should not find a key')

    eleza test_default_protocol(self):
        with shelve.Shelf({}) as s:
            self.assertEqual(s._protocol, 3)

kutoka test agiza mapping_tests

kundi TestShelveBase(mapping_tests.BasicTestMappingProtocol):
    fn = "shelftemp.db"
    counter = 0
    eleza __init__(self, *args, **kw):
        self._db = []
        mapping_tests.BasicTestMappingProtocol.__init__(self, *args, **kw)
    type2test = shelve.Shelf
    eleza _reference(self):
        rudisha {"key1":"value1", "key2":2, "key3":(1,2,3)}
    eleza _empty_mapping(self):
        ikiwa self._in_mem:
            x= shelve.Shelf(byteskeydict(), **self._args)
        else:
            self.counter+=1
            x= shelve.open(self.fn+str(self.counter), **self._args)
        self._db.append(x)
        rudisha x
    eleza tearDown(self):
        for db in self._db:
            db.close()
        self._db = []
        ikiwa not self._in_mem:
            for f in glob.glob(self.fn+"*"):
                support.unlink(f)

kundi TestAsciiFileShelve(TestShelveBase):
    _args={'protocol':0}
    _in_mem = False
kundi TestBinaryFileShelve(TestShelveBase):
    _args={'protocol':1}
    _in_mem = False
kundi TestProto2FileShelve(TestShelveBase):
    _args={'protocol':2}
    _in_mem = False
kundi TestAsciiMemShelve(TestShelveBase):
    _args={'protocol':0}
    _in_mem = True
kundi TestBinaryMemShelve(TestShelveBase):
    _args={'protocol':1}
    _in_mem = True
kundi TestProto2MemShelve(TestShelveBase):
    _args={'protocol':2}
    _in_mem = True

eleza test_main():
    for module in dbm_iterator():
        support.run_unittest(
            TestAsciiFileShelve,
            TestBinaryFileShelve,
            TestProto2FileShelve,
            TestAsciiMemShelve,
            TestBinaryMemShelve,
            TestProto2MemShelve,
            TestCase
        )

ikiwa __name__ == "__main__":
    test_main()
