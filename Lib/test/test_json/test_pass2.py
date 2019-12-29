kutoka test.test_json agiza PyTest, CTest


# kutoka http://json.org/JSON_checker/test/pita2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

kundi TestPass2:
    eleza test_parse(self):
        # test in/out equivalence na parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


kundi TestPyPass2(TestPass2, PyTest): pita
kundi TestCPass2(TestPass2, CTest): pita
