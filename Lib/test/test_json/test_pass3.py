kutoka test.test_json agiza PyTest, CTest


# kutoka http://json.org/JSON_checker/test/pita3.json
JSON = r'''
{
    "JSON Test Pattern pita3": {
        "The outermost value": "must be an object ama array.",
        "In this test": "It ni an object."
    }
}
'''


kundi TestPass3:
    eleza test_parse(self):
        # test in/out equivalence na parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


kundi TestPyPass3(TestPass3, PyTest): pita
kundi TestCPass3(TestPass3, CTest): pita
