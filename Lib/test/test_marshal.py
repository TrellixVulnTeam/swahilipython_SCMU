kutoka test agiza support
agiza array
agiza io
agiza marshal
agiza sys
agiza unittest
agiza os
agiza types

jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu

kundi HelperMixin:
    eleza helper(self, sample, *extra):
        new = marshal.loads(marshal.dumps(sample, *extra))
        self.assertEqual(sample, new)
        jaribu:
            ukijumuisha open(support.TESTFN, "wb") kama f:
                marshal.dump(sample, f, *extra)
            ukijumuisha open(support.TESTFN, "rb") kama f:
                new = marshal.load(f)
            self.assertEqual(sample, new)
        mwishowe:
            support.unlink(support.TESTFN)

kundi IntTestCase(unittest.TestCase, HelperMixin):
    eleza test_ints(self):
        # Test a range of Python ints larger than the machine word size.
        n = sys.maxsize ** 2
        wakati n:
            kila expected kwenye (-n, n):
                self.helper(expected)
            n = n >> 1

    eleza test_int64(self):
        # Simulate int marshaling ukijumuisha TYPE_INT64.
        maxint64 = (1 << 63) - 1
        minint64 = -maxint64-1
        kila base kwenye maxint64, minint64, -maxint64, -(minint64 >> 1):
            wakati base:
                s = b'I' + int.to_bytes(base, 8, 'little', signed=Kweli)
                got = marshal.loads(s)
                self.assertEqual(base, got)
                ikiwa base == -1:  # a fixed-point kila shifting right 1
                    base = 0
                isipokua:
                    base >>= 1

        got = marshal.loads(b'I\xfe\xdc\xba\x98\x76\x54\x32\x10')
        self.assertEqual(got, 0x1032547698badcfe)
        got = marshal.loads(b'I\x01\x23\x45\x67\x89\xab\xcd\xef')
        self.assertEqual(got, -0x1032547698badcff)
        got = marshal.loads(b'I\x08\x19\x2a\x3b\x4c\x5d\x6e\x7f')
        self.assertEqual(got, 0x7f6e5d4c3b2a1908)
        got = marshal.loads(b'I\xf7\xe6\xd5\xc4\xb3\xa2\x91\x80')
        self.assertEqual(got, -0x7f6e5d4c3b2a1909)

    eleza test_bool(self):
        kila b kwenye (Kweli, Uongo):
            self.helper(b)

kundi FloatTestCase(unittest.TestCase, HelperMixin):
    eleza test_floats(self):
        # Test a few floats
        small = 1e-25
        n = sys.maxsize * 3.7e250
        wakati n > small:
            kila expected kwenye (-n, n):
                self.helper(float(expected))
            n /= 123.4567

        f = 0.0
        s = marshal.dumps(f, 2)
        got = marshal.loads(s)
        self.assertEqual(f, got)
        # na ukijumuisha version <= 1 (floats marshalled differently then)
        s = marshal.dumps(f, 1)
        got = marshal.loads(s)
        self.assertEqual(f, got)

        n = sys.maxsize * 3.7e-250
        wakati n < small:
            kila expected kwenye (-n, n):
                f = float(expected)
                self.helper(f)
                self.helper(f, 1)
            n *= 123.4567

kundi StringTestCase(unittest.TestCase, HelperMixin):
    eleza test_unicode(self):
        kila s kwenye ["", "Andr\xe8 Previn", "abc", " "*10000]:
            self.helper(marshal.loads(marshal.dumps(s)))

    eleza test_string(self):
        kila s kwenye ["", "Andr\xe8 Previn", "abc", " "*10000]:
            self.helper(s)

    eleza test_bytes(self):
        kila s kwenye [b"", b"Andr\xe8 Previn", b"abc", b" "*10000]:
            self.helper(s)

kundi ExceptionTestCase(unittest.TestCase):
    eleza test_exceptions(self):
        new = marshal.loads(marshal.dumps(StopIteration))
        self.assertEqual(StopIteration, new)

kundi CodeTestCase(unittest.TestCase):
    eleza test_code(self):
        co = ExceptionTestCase.test_exceptions.__code__
        new = marshal.loads(marshal.dumps(co))
        self.assertEqual(co, new)

    eleza test_many_codeobjects(self):
        # Issue2957: bad recursion count on code objects
        count = 5000    # more than MAX_MARSHAL_STACK_DEPTH
        codes = (ExceptionTestCase.test_exceptions.__code__,) * count
        marshal.loads(marshal.dumps(codes))

    eleza test_different_filenames(self):
        co1 = compile("x", "f1", "exec")
        co2 = compile("y", "f2", "exec")
        co1, co2 = marshal.loads(marshal.dumps((co1, co2)))
        self.assertEqual(co1.co_filename, "f1")
        self.assertEqual(co2.co_filename, "f2")

    @support.cpython_only
    eleza test_same_filename_used(self):
        s = """eleza f(): pita\neleza g(): pita"""
        co = compile(s, "myfile", "exec")
        co = marshal.loads(marshal.dumps(co))
        kila obj kwenye co.co_consts:
            ikiwa isinstance(obj, types.CodeType):
                self.assertIs(co.co_filename, obj.co_filename)

kundi ContainerTestCase(unittest.TestCase, HelperMixin):
    d = {'astring': 'foo@bar.baz.spam',
         'afloat': 7283.43,
         'anint': 2**20,
         'ashortlong': 2,
         'alist': ['.zyx.41'],
         'atuple': ('.zyx.41',)*10,
         'aboolean': Uongo,
         'aunicode': "Andr\xe8 Previn"
         }

    eleza test_dict(self):
        self.helper(self.d)

    eleza test_list(self):
        self.helper(list(self.d.items()))

    eleza test_tuple(self):
        self.helper(tuple(self.d.keys()))

    eleza test_sets(self):
        kila constructor kwenye (set, frozenset):
            self.helper(constructor(self.d.keys()))

    @support.cpython_only
    eleza test_empty_frozenset_singleton(self):
        # marshal.loads() must reuse the empty frozenset singleton
        obj = frozenset()
        obj2 = marshal.loads(marshal.dumps(obj))
        self.assertIs(obj2, obj)


kundi BufferTestCase(unittest.TestCase, HelperMixin):

    eleza test_bytearray(self):
        b = bytearray(b"abc")
        self.helper(b)
        new = marshal.loads(marshal.dumps(b))
        self.assertEqual(type(new), bytes)

    eleza test_memoryview(self):
        b = memoryview(b"abc")
        self.helper(b)
        new = marshal.loads(marshal.dumps(b))
        self.assertEqual(type(new), bytes)

    eleza test_array(self):
        a = array.array('B', b"abc")
        new = marshal.loads(marshal.dumps(a))
        self.assertEqual(new, b"abc")


kundi BugsTestCase(unittest.TestCase):
    eleza test_bug_5888452(self):
        # Simple-minded check kila SF 588452: Debug build crashes
        marshal.dumps([128] * 1000)

    eleza test_patch_873224(self):
        self.assertRaises(Exception, marshal.loads, b'0')
        self.assertRaises(Exception, marshal.loads, b'f')
        self.assertRaises(Exception, marshal.loads, marshal.dumps(2**65)[:-1])

    eleza test_version_argument(self):
        # Python 2.4.0 crashes kila any call to marshal.dumps(x, y)
        self.assertEqual(marshal.loads(marshal.dumps(5, 0)), 5)
        self.assertEqual(marshal.loads(marshal.dumps(5, 1)), 5)

    eleza test_fuzz(self):
        # simple test that it's at least sio *totally* trivial to
        # crash kutoka bad marshal data
        kila i kwenye range(256):
            c = bytes([i])
            jaribu:
                marshal.loads(c)
            tatizo Exception:
                pita

    eleza test_loads_recursion(self):
        eleza run_tests(N, check):
            # (((...Tupu...),),)
            check(b')\x01' * N + b'N')
            check(b'(\x01\x00\x00\x00' * N + b'N')
            # [[[...Tupu...]]]
            check(b'[\x01\x00\x00\x00' * N + b'N')
            # {Tupu: {Tupu: {Tupu: ...Tupu...}}}
            check(b'{N' * N + b'N' + b'0' * N)
            # frozenset([frozenset([frozenset([...Tupu...])])])
            check(b'>\x01\x00\x00\x00' * N + b'N')
        # Check that the generated marshal data ni valid na marshal.loads()
        # works kila moderately deep nesting
        run_tests(100, marshal.loads)
        # Very deeply nested structure shouldn't blow the stack
        eleza check(s):
            self.assertRaises(ValueError, marshal.loads, s)
        run_tests(2**20, check)

    eleza test_recursion_limit(self):
        # Create a deeply nested structure.
        head = last = []
        # The max stack depth should match the value kwenye Python/marshal.c.
        # BUG: https://bugs.python.org/issue33720
        # Windows always limits the maximum depth on release na debug builds
        #ikiwa os.name == 'nt' na hasattr(sys, 'gettotalrefcount'):
        ikiwa os.name == 'nt':
            MAX_MARSHAL_STACK_DEPTH = 1000
        isipokua:
            MAX_MARSHAL_STACK_DEPTH = 2000
        kila i kwenye range(MAX_MARSHAL_STACK_DEPTH - 2):
            last.append([0])
            last = last[-1]

        # Verify we don't blow out the stack ukijumuisha dumps/load.
        data = marshal.dumps(head)
        new_head = marshal.loads(data)
        # Don't use == to compare objects, it can exceed the recursion limit.
        self.assertEqual(len(new_head), len(head))
        self.assertEqual(len(new_head[0]), len(head[0]))
        self.assertEqual(len(new_head[-1]), len(head[-1]))

        last.append([0])
        self.assertRaises(ValueError, marshal.dumps, head)

    eleza test_exact_type_match(self):
        # Former bug:
        #   >>> kundi Int(int): pita
        #   >>> type(loads(dumps(Int())))
        #   <type 'int'>
        kila typ kwenye (int, float, complex, tuple, list, dict, set, frozenset):
            # Note: str subclasses are sio tested because they get handled
            # by marshal's routines kila objects supporting the buffer API.
            subtyp = type('subtyp', (typ,), {})
            self.assertRaises(ValueError, marshal.dumps, subtyp())

    # Issue #1792 introduced a change kwenye how marshal increases the size of its
    # internal buffer; this test ensures that the new code ni exercised.
    eleza test_large_marshal(self):
        size = int(1e6)
        testString = 'abc' * size
        marshal.dumps(testString)

    eleza test_invalid_longs(self):
        # Issue #7019: marshal.loads shouldn't produce unnormalized PyLongs
        invalid_string = b'l\x02\x00\x00\x00\x00\x00\x00\x00'
        self.assertRaises(ValueError, marshal.loads, invalid_string)

    eleza test_multiple_dumps_and_loads(self):
        # Issue 12291: marshal.load() should be callable multiple times
        # ukijumuisha interleaved data written by non-marshal code
        # Adapted kutoka a patch by Engelbert Gruber.
        data = (1, 'abc', b'def', 1.0, (2, 'a', ['b', b'c']))
        kila interleaved kwenye (b'', b'0123'):
            ilen = len(interleaved)
            positions = []
            jaribu:
                ukijumuisha open(support.TESTFN, 'wb') kama f:
                    kila d kwenye data:
                        marshal.dump(d, f)
                        ikiwa ilen:
                            f.write(interleaved)
                        positions.append(f.tell())
                ukijumuisha open(support.TESTFN, 'rb') kama f:
                    kila i, d kwenye enumerate(data):
                        self.assertEqual(d, marshal.load(f))
                        ikiwa ilen:
                            f.read(ilen)
                        self.assertEqual(positions[i], f.tell())
            mwishowe:
                support.unlink(support.TESTFN)

    eleza test_loads_reject_unicode_strings(self):
        # Issue #14177: marshal.loads() should sio accept unicode strings
        unicode_string = 'T'
        self.assertRaises(TypeError, marshal.loads, unicode_string)

    eleza test_bad_reader(self):
        kundi BadReader(io.BytesIO):
            eleza readinto(self, buf):
                n = super().readinto(buf)
                ikiwa n ni sio Tupu na n > 4:
                    n += 10**6
                rudisha n
        kila value kwenye (1.0, 1j, b'0123456789', '0123456789'):
            self.assertRaises(ValueError, marshal.load,
                              BadReader(marshal.dumps(value)))

    eleza test_eof(self):
        data = marshal.dumps(("hello", "dolly", Tupu))
        kila i kwenye range(len(data)):
            self.assertRaises(EOFError, marshal.loads, data[0: i])

LARGE_SIZE = 2**31
pointer_size = 8 ikiwa sys.maxsize > 0xFFFFFFFF isipokua 4

kundi NullWriter:
    eleza write(self, s):
        pita

@unittest.skipIf(LARGE_SIZE > sys.maxsize, "test cannot run on 32-bit systems")
kundi LargeValuesTestCase(unittest.TestCase):
    eleza check_unmarshallable(self, data):
        self.assertRaises(ValueError, marshal.dump, data, NullWriter())

    @support.bigmemtest(size=LARGE_SIZE, memuse=2, dry_run=Uongo)
    eleza test_bytes(self, size):
        self.check_unmarshallable(b'x' * size)

    @support.bigmemtest(size=LARGE_SIZE, memuse=2, dry_run=Uongo)
    eleza test_str(self, size):
        self.check_unmarshallable('x' * size)

    @support.bigmemtest(size=LARGE_SIZE, memuse=pointer_size + 1, dry_run=Uongo)
    eleza test_tuple(self, size):
        self.check_unmarshallable((Tupu,) * size)

    @support.bigmemtest(size=LARGE_SIZE, memuse=pointer_size + 1, dry_run=Uongo)
    eleza test_list(self, size):
        self.check_unmarshallable([Tupu] * size)

    @support.bigmemtest(size=LARGE_SIZE,
            memuse=pointer_size*12 + sys.getsizeof(LARGE_SIZE-1),
            dry_run=Uongo)
    eleza test_set(self, size):
        self.check_unmarshallable(set(range(size)))

    @support.bigmemtest(size=LARGE_SIZE,
            memuse=pointer_size*12 + sys.getsizeof(LARGE_SIZE-1),
            dry_run=Uongo)
    eleza test_frozenset(self, size):
        self.check_unmarshallable(frozenset(range(size)))

    @support.bigmemtest(size=LARGE_SIZE, memuse=2, dry_run=Uongo)
    eleza test_bytearray(self, size):
        self.check_unmarshallable(bytearray(size))

eleza CollectObjectIDs(ids, obj):
    """Collect object ids seen kwenye a structure"""
    ikiwa id(obj) kwenye ids:
        rudisha
    ids.add(id(obj))
    ikiwa isinstance(obj, (list, tuple, set, frozenset)):
        kila e kwenye obj:
            CollectObjectIDs(ids, e)
    lasivyo isinstance(obj, dict):
        kila k, v kwenye obj.items():
            CollectObjectIDs(ids, k)
            CollectObjectIDs(ids, v)
    rudisha len(ids)

kundi InstancingTestCase(unittest.TestCase, HelperMixin):
    keys = (123, 1.2345, 'abc', (123, 'abc'), frozenset({123, 'abc'}))

    eleza helper3(self, rsample, recursive=Uongo, simple=Uongo):
        #we have two instances
        sample = (rsample, rsample)

        n0 = CollectObjectIDs(set(), sample)

        kila v kwenye range(3, marshal.version + 1):
            s3 = marshal.dumps(sample, v)
            n3 = CollectObjectIDs(set(), marshal.loads(s3))

            #same number of instances generated
            self.assertEqual(n3, n0)

        ikiwa sio recursive:
            #can compare ukijumuisha version 2
            s2 = marshal.dumps(sample, 2)
            n2 = CollectObjectIDs(set(), marshal.loads(s2))
            #old format generated more instances
            self.assertGreater(n2, n0)

            #ikiwa complex objects are kwenye there, old format ni larger
            ikiwa sio simple:
                self.assertGreater(len(s2), len(s3))
            isipokua:
                self.assertGreaterEqual(len(s2), len(s3))

    eleza testInt(self):
        intobj = 123321
        self.helper(intobj)
        self.helper3(intobj, simple=Kweli)

    eleza testFloat(self):
        floatobj = 1.2345
        self.helper(floatobj)
        self.helper3(floatobj)

    eleza testStr(self):
        strobj = "abcde"*3
        self.helper(strobj)
        self.helper3(strobj)

    eleza testBytes(self):
        bytesobj = b"abcde"*3
        self.helper(bytesobj)
        self.helper3(bytesobj)

    eleza testList(self):
        kila obj kwenye self.keys:
            listobj = [obj, obj]
            self.helper(listobj)
            self.helper3(listobj)

    eleza testTuple(self):
        kila obj kwenye self.keys:
            tupleobj = (obj, obj)
            self.helper(tupleobj)
            self.helper3(tupleobj)

    eleza testSet(self):
        kila obj kwenye self.keys:
            setobj = {(obj, 1), (obj, 2)}
            self.helper(setobj)
            self.helper3(setobj)

    eleza testFrozenSet(self):
        kila obj kwenye self.keys:
            frozensetobj = frozenset({(obj, 1), (obj, 2)})
            self.helper(frozensetobj)
            self.helper3(frozensetobj)

    eleza testDict(self):
        kila obj kwenye self.keys:
            dictobj = {"hello": obj, "goodbye": obj, obj: "hello"}
            self.helper(dictobj)
            self.helper3(dictobj)

    eleza testModule(self):
        ukijumuisha open(__file__, "rb") kama f:
            code = f.read()
        ikiwa __file__.endswith(".py"):
            code = compile(code, __file__, "exec")
        self.helper(code)
        self.helper3(code)

    eleza testRecursion(self):
        obj = 1.2345
        d = {"hello": obj, "goodbye": obj, obj: "hello"}
        d["self"] = d
        self.helper3(d, recursive=Kweli)
        l = [obj, obj]
        l.append(l)
        self.helper3(l, recursive=Kweli)

kundi CompatibilityTestCase(unittest.TestCase):
    eleza _test(self, version):
        ukijumuisha open(__file__, "rb") kama f:
            code = f.read()
        ikiwa __file__.endswith(".py"):
            code = compile(code, __file__, "exec")
        data = marshal.dumps(code, version)
        marshal.loads(data)

    eleza test0To3(self):
        self._test(0)

    eleza test1To3(self):
        self._test(1)

    eleza test2To3(self):
        self._test(2)

    eleza test3To3(self):
        self._test(3)

kundi InterningTestCase(unittest.TestCase, HelperMixin):
    strobj = "this ni an interned string"
    strobj = sys.intern(strobj)

    eleza testIntern(self):
        s = marshal.loads(marshal.dumps(self.strobj))
        self.assertEqual(s, self.strobj)
        self.assertEqual(id(s), id(self.strobj))
        s2 = sys.intern(s)
        self.assertEqual(id(s2), id(s))

    eleza testNoIntern(self):
        s = marshal.loads(marshal.dumps(self.strobj, 2))
        self.assertEqual(s, self.strobj)
        self.assertNotEqual(id(s), id(self.strobj))
        s2 = sys.intern(s)
        self.assertNotEqual(id(s2), id(s))

@support.cpython_only
@unittest.skipUnless(_testcapi, 'requires _testcapi')
kundi CAPI_TestCase(unittest.TestCase, HelperMixin):

    eleza test_write_long_to_file(self):
        kila v kwenye range(marshal.version + 1):
            _testcapi.pymarshal_write_long_to_file(0x12345678, support.TESTFN, v)
            ukijumuisha open(support.TESTFN, 'rb') kama f:
                data = f.read()
            support.unlink(support.TESTFN)
            self.assertEqual(data, b'\x78\x56\x34\x12')

    eleza test_write_object_to_file(self):
        obj = ('\u20ac', b'abc', 123, 45.6, 7+8j, 'long line '*1000)
        kila v kwenye range(marshal.version + 1):
            _testcapi.pymarshal_write_object_to_file(obj, support.TESTFN, v)
            ukijumuisha open(support.TESTFN, 'rb') kama f:
                data = f.read()
            support.unlink(support.TESTFN)
            self.assertEqual(marshal.loads(data), obj)

    eleza test_read_short_kutoka_file(self):
        ukijumuisha open(support.TESTFN, 'wb') kama f:
            f.write(b'\x34\x12xxxx')
        r, p = _testcapi.pymarshal_read_short_kutoka_file(support.TESTFN)
        support.unlink(support.TESTFN)
        self.assertEqual(r, 0x1234)
        self.assertEqual(p, 2)

        ukijumuisha open(support.TESTFN, 'wb') kama f:
            f.write(b'\x12')
        ukijumuisha self.assertRaises(EOFError):
            _testcapi.pymarshal_read_short_kutoka_file(support.TESTFN)
        support.unlink(support.TESTFN)

    eleza test_read_long_kutoka_file(self):
        ukijumuisha open(support.TESTFN, 'wb') kama f:
            f.write(b'\x78\x56\x34\x12xxxx')
        r, p = _testcapi.pymarshal_read_long_kutoka_file(support.TESTFN)
        support.unlink(support.TESTFN)
        self.assertEqual(r, 0x12345678)
        self.assertEqual(p, 4)

        ukijumuisha open(support.TESTFN, 'wb') kama f:
            f.write(b'\x56\x34\x12')
        ukijumuisha self.assertRaises(EOFError):
            _testcapi.pymarshal_read_long_kutoka_file(support.TESTFN)
        support.unlink(support.TESTFN)

    eleza test_read_last_object_kutoka_file(self):
        obj = ('\u20ac', b'abc', 123, 45.6, 7+8j)
        kila v kwenye range(marshal.version + 1):
            data = marshal.dumps(obj, v)
            ukijumuisha open(support.TESTFN, 'wb') kama f:
                f.write(data + b'xxxx')
            r, p = _testcapi.pymarshal_read_last_object_kutoka_file(support.TESTFN)
            support.unlink(support.TESTFN)
            self.assertEqual(r, obj)

            ukijumuisha open(support.TESTFN, 'wb') kama f:
                f.write(data[:1])
            ukijumuisha self.assertRaises(EOFError):
                _testcapi.pymarshal_read_last_object_kutoka_file(support.TESTFN)
            support.unlink(support.TESTFN)

    eleza test_read_object_kutoka_file(self):
        obj = ('\u20ac', b'abc', 123, 45.6, 7+8j)
        kila v kwenye range(marshal.version + 1):
            data = marshal.dumps(obj, v)
            ukijumuisha open(support.TESTFN, 'wb') kama f:
                f.write(data + b'xxxx')
            r, p = _testcapi.pymarshal_read_object_kutoka_file(support.TESTFN)
            support.unlink(support.TESTFN)
            self.assertEqual(r, obj)
            self.assertEqual(p, len(data))

            ukijumuisha open(support.TESTFN, 'wb') kama f:
                f.write(data[:1])
            ukijumuisha self.assertRaises(EOFError):
                _testcapi.pymarshal_read_object_kutoka_file(support.TESTFN)
            support.unlink(support.TESTFN)


ikiwa __name__ == "__main__":
    unittest.main()
