kutoka io agiza StringIO
kutoka test.test_json agiza PyTest, CTest

kutoka test.support agiza bigmemtest, _1G

kundi TestDump:
    eleza test_dump(self):
        sio = StringIO()
        self.json.dump({}, sio)
        self.assertEqual(sio.getvalue(), '{}')

    eleza test_dumps(self):
        self.assertEqual(self.dumps({}), '{}')

    eleza test_dump_skipkeys(self):
        v = {b'invalid_key': False, 'valid_key': True}
        with self.assertRaises(TypeError):
            self.json.dumps(v)

        s = self.json.dumps(v, skipkeys=True)
        o = self.json.loads(s)
        self.assertIn('valid_key', o)
        self.assertNotIn(b'invalid_key', o)

    eleza test_encode_truefalse(self):
        self.assertEqual(self.dumps(
                 {True: False, False: True}, sort_keys=True),
                 '{"false": true, "true": false}')
        self.assertEqual(self.dumps(
                {2: 3.0, 4.0: 5, False: 1, 6: True}, sort_keys=True),
                '{"false": 1, "2": 3.0, "4.0": 5, "6": true}')

    # Issue 16228: Crash on encoding resized list
    eleza test_encode_mutated(self):
        a = [object()] * 10
        eleza crasher(obj):
            del a[-1]
        self.assertEqual(self.dumps(a, default=crasher),
                 '[null, null, null, null, null]')

    # Issue 24094
    eleza test_encode_evil_dict(self):
        kundi D(dict):
            eleza keys(self):
                rudisha L

        kundi X:
            eleza __hash__(self):
                del L[0]
                rudisha 1337

            eleza __lt__(self, o):
                rudisha 0

        L = [X() for i in range(1122)]
        d = D()
        d[1337] = "true.dat"
        self.assertEqual(self.dumps(d, sort_keys=True), '{"1337": "true.dat"}')


kundi TestPyDump(TestDump, PyTest): pass

kundi TestCDump(TestDump, CTest):

    # The size requirement here is hopefully over-estimated (actual
    # memory consumption depending on implementation details, and also
    # system memory management, since this may allocate a lot of
    # small objects).

    @bigmemtest(size=_1G, memuse=1)
    eleza test_large_list(self, size):
        N = int(30 * 1024 * 1024 * (size / _1G))
        l = [1] * N
        encoded = self.dumps(l)
        self.assertEqual(len(encoded), N * 3)
        self.assertEqual(encoded[:1], "[")
        self.assertEqual(encoded[-2:], "1]")
        self.assertEqual(encoded[1:-2], "1, " * (N - 1))
