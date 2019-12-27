agiza unittest
agiza copy
agiza pickle
kutoka unittest.mock agiza sentinel, DEFAULT


kundi SentinelTest(unittest.TestCase):

    eleza testSentinels(self):
        self.assertEqual(sentinel.whatever, sentinel.whatever,
                         'sentinel not stored')
        self.assertNotEqual(sentinel.whatever, sentinel.whateverelse,
                            'sentinel should be unique')


    eleza testSentinelName(self):
        self.assertEqual(str(sentinel.whatever), 'sentinel.whatever',
                         'sentinel name incorrect')


    eleza testDEFAULT(self):
        self.assertIs(DEFAULT, sentinel.DEFAULT)

    eleza testBases(self):
        # If this doesn't raise an AttributeError then help(mock) is broken
        self.assertRaises(AttributeError, lambda: sentinel.__bases__)

    eleza testPickle(self):
        for proto in range(pickle.HIGHEST_PROTOCOL+1):
            with self.subTest(protocol=proto):
                pickled = pickle.dumps(sentinel.whatever, proto)
                unpickled = pickle.loads(pickled)
                self.assertIs(unpickled, sentinel.whatever)

    eleza testCopy(self):
        self.assertIs(copy.copy(sentinel.whatever), sentinel.whatever)
        self.assertIs(copy.deepcopy(sentinel.whatever), sentinel.whatever)


ikiwa __name__ == '__main__':
    unittest.main()
