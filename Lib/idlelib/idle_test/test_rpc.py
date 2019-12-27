"Test rpc, coverage 20%."

kutoka idlelib agiza rpc
agiza unittest



kundi CodePicklerTest(unittest.TestCase):

    eleza test_pickle_unpickle(self):
        eleza f(): rudisha a + b + c
        func, (cbytes,) = rpc.pickle_code(f.__code__)
        self.assertIs(func, rpc.unpickle_code)
        self.assertIn(b'test_rpc.py', cbytes)
        code = rpc.unpickle_code(cbytes)
        self.assertEqual(code.co_names, ('a', 'b', 'c'))

    eleza test_code_pickler(self):
        self.assertIn(type((lambda:None).__code__),
                      rpc.CodePickler.dispatch_table)

    eleza test_dumps(self):
        eleza f(): pass
        # The main test here is that pickling code does not raise.
        self.assertIn(b'test_rpc.py', rpc.dumps(f.__code__))


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
