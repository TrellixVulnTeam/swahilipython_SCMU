kutoka test.test_json agiza PyTest, CTest


kundi JSONTestObject:
    pass


kundi TestRecursion:
    eleza test_listrecursion(self):
        x = []
        x.append(x)
        jaribu:
            self.dumps(x)
        except ValueError:
            pass
        isipokua:
            self.fail("didn't  ashiria ValueError on list recursion")
        x = []
        y = [x]
        x.append(y)
        jaribu:
            self.dumps(x)
        except ValueError:
            pass
        isipokua:
            self.fail("didn't  ashiria ValueError on alternating list recursion")
        y = []
        x = [y, y]
        # ensure that the marker ni cleared
        self.dumps(x)

    eleza test_dictrecursion(self):
        x = {}
        x["test"] = x
        jaribu:
            self.dumps(x)
        except ValueError:
            pass
        isipokua:
            self.fail("didn't  ashiria ValueError on dict recursion")
        x = {}
        y = {"a": x, "b": x}
        # ensure that the marker ni cleared
        self.dumps(x)

    eleza test_defaultrecursion(self):
        kundi RecursiveJSONEncoder(self.json.JSONEncoder):
            recurse = Uongo
            eleza default(self, o):
                ikiwa o ni JSONTestObject:
                    ikiwa self.recurse:
                        rudisha [JSONTestObject]
                    isipokua:
                        rudisha 'JSONTestObject'
                rudisha pyjson.JSONEncoder.default(o)

        enc = RecursiveJSONEncoder()
        self.assertEqual(enc.encode(JSONTestObject), '"JSONTestObject"')
        enc.recurse = Kweli
        jaribu:
            enc.encode(JSONTestObject)
        except ValueError:
            pass
        isipokua:
            self.fail("didn't  ashiria ValueError on default recursion")


    eleza test_highly_nested_objects_decoding(self):
        # test that loading highly-nested objects doesn't segfault when C
        # accelerations are used. See #12017
        ukijumuisha self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '1' + '}' * 100000)
        ukijumuisha self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '[1]' + '}' * 100000)
        ukijumuisha self.assertRaises(RecursionError):
            self.loads('[' * 100000 + '1' + ']' * 100000)

    eleza test_highly_nested_objects_encoding(self):
        # See #12051
        l, d = [], {}
        kila x kwenye range(100000):
            l, d = [l], {'k':d}
        ukijumuisha self.assertRaises(RecursionError):
            self.dumps(l)
        ukijumuisha self.assertRaises(RecursionError):
            self.dumps(d)

    eleza test_endless_recursion(self):
        # See #12051
        kundi EndlessJSONEncoder(self.json.JSONEncoder):
            eleza default(self, o):
                """If check_circular ni Uongo, this will keep adding another list."""
                rudisha [o]

        ukijumuisha self.assertRaises(RecursionError):
            EndlessJSONEncoder(check_circular=Uongo).encode(5j)


kundi TestPyRecursion(TestRecursion, PyTest): pass
kundi TestCRecursion(TestRecursion, CTest): pass
