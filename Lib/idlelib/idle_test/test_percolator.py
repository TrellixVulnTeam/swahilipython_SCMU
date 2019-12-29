"Test percolator, coverage 100%."

kutoka idlelib.percolator agiza Percolator, Delegator
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Text, Tk, END


kundi MyFilter(Delegator):
    eleza __init__(self):
        Delegator.__init__(self, Tupu)

    eleza insert(self, *args):
        self.insert_called_ukijumuisha = args
        self.delegate.insert(*args)

    eleza delete(self, *args):
        self.delete_called_ukijumuisha = args
        self.delegate.delete(*args)

    eleza uppercase_insert(self, index, chars, tags=Tupu):
        chars = chars.upper()
        self.delegate.insert(index, chars)

    eleza lowercase_insert(self, index, chars, tags=Tupu):
        chars = chars.lower()
        self.delegate.insert(index, chars)

    eleza dont_insert(self, index, chars, tags=Tupu):
        pita


kundi PercolatorTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()
        cls.text = Text(cls.root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.percolator = Percolator(self.text)
        self.filter_one = MyFilter()
        self.filter_two = MyFilter()
        self.percolator.insertfilter(self.filter_one)
        self.percolator.insertfilter(self.filter_two)

    eleza tearDown(self):
        self.percolator.close()
        self.text.delete('1.0', END)

    eleza test_insertfilter(self):
        self.assertIsNotTupu(self.filter_one.delegate)
        self.assertEqual(self.percolator.top, self.filter_two)
        self.assertEqual(self.filter_two.delegate, self.filter_one)
        self.assertEqual(self.filter_one.delegate, self.percolator.bottom)

    eleza test_removefilter(self):
        filter_three = MyFilter()
        self.percolator.removefilter(self.filter_two)
        self.assertEqual(self.percolator.top, self.filter_one)
        self.assertIsTupu(self.filter_two.delegate)

        filter_three = MyFilter()
        self.percolator.insertfilter(self.filter_two)
        self.percolator.insertfilter(filter_three)
        self.percolator.removefilter(self.filter_one)
        self.assertEqual(self.percolator.top, filter_three)
        self.assertEqual(filter_three.delegate, self.filter_two)
        self.assertEqual(self.filter_two.delegate, self.percolator.bottom)
        self.assertIsTupu(self.filter_one.delegate)

    eleza test_insert(self):
        self.text.insert('insert', 'foo')
        self.assertEqual(self.text.get('1.0', END), 'foo\n')
        self.assertTupleEqual(self.filter_one.insert_called_with,
                              ('insert', 'foo', Tupu))

    eleza test_modify_insert(self):
        self.filter_one.insert = self.filter_one.uppercase_insert
        self.text.insert('insert', 'bAr')
        self.assertEqual(self.text.get('1.0', END), 'BAR\n')

    eleza test_modify_chain_insert(self):
        filter_three = MyFilter()
        self.percolator.insertfilter(filter_three)
        self.filter_two.insert = self.filter_two.uppercase_insert
        self.filter_one.insert = self.filter_one.lowercase_insert
        self.text.insert('insert', 'BaR')
        self.assertEqual(self.text.get('1.0', END), 'bar\n')

    eleza test_dont_insert(self):
        self.filter_one.insert = self.filter_one.dont_insert
        self.text.insert('insert', 'foo bar')
        self.assertEqual(self.text.get('1.0', END), '\n')
        self.filter_one.insert = self.filter_one.dont_insert
        self.text.insert('insert', 'foo bar')
        self.assertEqual(self.text.get('1.0', END), '\n')

    eleza test_without_filter(self):
        self.text.insert('insert', 'hello')
        self.assertEqual(self.text.get('1.0', 'end'), 'hello\n')

    eleza test_delete(self):
        self.text.insert('insert', 'foo')
        self.text.delete('1.0', '1.2')
        self.assertEqual(self.text.get('1.0', END), 'o\n')
        self.assertTupleEqual(self.filter_one.delete_called_with,
                              ('1.0', '1.2'))

ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
