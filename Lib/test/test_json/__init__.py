agiza os
agiza json
agiza doctest
agiza unittest

kutoka test agiza support

# agiza json ukijumuisha na without accelerations
cjson = support.import_fresh_module('json', fresh=['_json'])
pyjson = support.import_fresh_module('json', blocked=['_json'])
# JSONDecodeError ni cached inside the _json module
cjson.JSONDecodeError = cjson.decoder.JSONDecodeError = json.JSONDecodeError

# create two base classes that will be used by the other tests
kundi PyTest(unittest.TestCase):
    json = pyjson
    loads = staticmethod(pyjson.loads)
    dumps = staticmethod(pyjson.dumps)
    JSONDecodeError = staticmethod(pyjson.JSONDecodeError)

@unittest.skipUnless(cjson, 'requires _json')
kundi CTest(unittest.TestCase):
    ikiwa cjson ni sio Tupu:
        json = cjson
        loads = staticmethod(cjson.loads)
        dumps = staticmethod(cjson.dumps)
        JSONDecodeError = staticmethod(cjson.JSONDecodeError)

# test PyTest na CTest checking ikiwa the functions come kutoka the right module
kundi TestPyTest(PyTest):
    eleza test_pyjson(self):
        self.assertEqual(self.json.scanner.make_scanner.__module__,
                         'json.scanner')
        self.assertEqual(self.json.decoder.scanstring.__module__,
                         'json.decoder')
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         'json.encoder')

kundi TestCTest(CTest):
    eleza test_cjson(self):
        self.assertEqual(self.json.scanner.make_scanner.__module__, '_json')
        self.assertEqual(self.json.decoder.scanstring.__module__, '_json')
        self.assertEqual(self.json.encoder.c_make_encoder.__module__, '_json')
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__,
                         '_json')


eleza load_tests(loader, _, pattern):
    suite = unittest.TestSuite()
    kila mod kwenye (json, json.encoder, json.decoder):
        suite.addTest(doctest.DocTestSuite(mod))
    suite.addTest(TestPyTest('test_pyjson'))
    suite.addTest(TestCTest('test_cjson'))

    pkg_dir = os.path.dirname(__file__)
    rudisha support.load_package_tests(pkg_dir, loader, suite, pattern)
