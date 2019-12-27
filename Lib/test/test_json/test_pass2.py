kutoka test.test_json agiza PyTest, CTest


# kutoka http://json.org/JSON_checker/test/pass2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

kundi TestPass2:
    eleza test_parse(self):
        # test in/out equivalence and parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


kundi TestPyPass2(TestPass2, PyTest): pass
kundi TestCPass2(TestPass2, CTest): pass
