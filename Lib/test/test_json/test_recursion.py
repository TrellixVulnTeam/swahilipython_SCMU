kutoka test.test_json agiza PyTest, CTest


kundi JSONTestObject:
    pass


kundi TestRecursion:
    eleza test_listrecursion(self):
        x = []
        x.append(x)
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on list recursion")
        x = []
        y = [x]
        x.append(y)
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on alternating list recursion")
        y = []
        x = [y, y]
        # ensure that the marker is cleared
        self.dumps(x)

    eleza test_dictrecursion(self):
        x = {}
        x["test"] = x
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on dict recursion")
        x = {}
        y = {"a": x, "b": x}
        # ensure that the marker is cleared
        self.dumps(x)

    eleza test_defaultrecursion(self):
        kundi RecursiveJSONEncoder(self.json.JSONEncoder):
            recurse = False
            eleza default(self, o):
                ikiwa o is JSONTestObject:
                    ikiwa self.recurse:
                        rudisha [JSONTestObject]
                    else:
                        rudisha 'JSONTestObject'
                rudisha pyjson.JSONEncoder.default(o)

        enc = RecursiveJSONEncoder()
        self.assertEqual(enc.encode(JSONTestObject), '"JSONTestObject"')
        enc.recurse = True
        try:
            enc.encode(JSONTestObject)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on default recursion")


    eleza test_highly_nested_objects_decoding(self):
        # test that loading highly-nested objects doesn't segfault when C
        # accelerations are used. See #12017
        with self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '1' + '}' * 100000)
        with self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '[1]' + '}' * 100000)
        with self.assertRaises(RecursionError):
            self.loads('[' * 100000 + '1' + ']' * 100000)

    eleza test_highly_nested_objects_encoding(self):
        # See #12051
        l, d = [], {}
        for x in range(100000):
            l, d = [l], {'k':d}
        with self.assertRaises(RecursionError):
            self.dumps(l)
        with self.assertRaises(RecursionError):
            self.dumps(d)

    eleza test_endless_recursion(self):
        # See #12051
        kundi EndlessJSONEncoder(self.json.JSONEncoder):
            eleza default(self, o):
                """If check_circular is False, this will keep adding another list."""
                rudisha [o]

        with self.assertRaises(RecursionError):
            EndlessJSONEncoder(check_circular=False).encode(5j)


kundi TestPyRecursion(TestRecursion, PyTest): pass
kundi TestCRecursion(TestRecursion, CTest): pass
