" Test history, coverage 100%."

kutoka idlelib.history agiza History
agiza unittest
kutoka test.support agiza requires

agiza tkinter as tk
kutoka tkinter agiza Text as tkText
kutoka idlelib.idle_test.mock_tk agiza Text as mkText
kutoka idlelib.config agiza idleConf

line1 = 'a = 7'
line2 = 'b = a'


kundi StoreTest(unittest.TestCase):
    '''Tests History.__init__ and History.store with mock Text'''

    @classmethod
    eleza setUpClass(cls):
        cls.text = mkText()
        cls.history = History(cls.text)

    eleza tearDown(self):
        self.text.delete('1.0', 'end')
        self.history.history = []

    eleza test_init(self):
        self.assertIs(self.history.text, self.text)
        self.assertEqual(self.history.history, [])
        self.assertIsNone(self.history.prefix)
        self.assertIsNone(self.history.pointer)
        self.assertEqual(self.history.cyclic,
                idleConf.GetOption("main", "History",  "cyclic", 1, "bool"))

    eleza test_store_short(self):
        self.history.store('a')
        self.assertEqual(self.history.history, [])
        self.history.store('  a  ')
        self.assertEqual(self.history.history, [])

    eleza test_store_dup(self):
        self.history.store(line1)
        self.assertEqual(self.history.history, [line1])
        self.history.store(line2)
        self.assertEqual(self.history.history, [line1, line2])
        self.history.store(line1)
        self.assertEqual(self.history.history, [line2, line1])

    eleza test_store_reset(self):
        self.history.prefix = line1
        self.history.pointer = 0
        self.history.store(line2)
        self.assertIsNone(self.history.prefix)
        self.assertIsNone(self.history.pointer)


kundi TextWrapper:
    eleza __init__(self, master):
        self.text = tkText(master=master)
        self._bell = False
    eleza __getattr__(self, name):
        rudisha getattr(self.text, name)
    eleza bell(self):
        self._bell = True


kundi FetchTest(unittest.TestCase):
    '''Test History.fetch with wrapped tk.Text.
    '''
    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = tk.Tk()
        cls.root.withdraw()

    eleza setUp(self):
        self.text = text = TextWrapper(self.root)
        text.insert('1.0', ">>> ")
        text.mark_set('iomark', '1.4')
        text.mark_gravity('iomark', 'left')
        self.history = History(text)
        self.history.history = [line1, line2]

    @classmethod
    eleza tearDownClass(cls):
        cls.root.destroy()
        del cls.root

    eleza fetch_test(self, reverse, line, prefix, index, *, bell=False):
        # Perform one fetch as invoked by Alt-N or Alt-P
        # Test the result. The line test is the most agizaant.
        # The last two are diagnostic of fetch internals.
        History = self.history
        History.fetch(reverse)

        Equal = self.assertEqual
        Equal(self.text.get('iomark', 'end-1c'), line)
        Equal(self.text._bell, bell)
        ikiwa bell:
            self.text._bell = False
        Equal(History.prefix, prefix)
        Equal(History.pointer, index)
        Equal(self.text.compare("insert", '==', "end-1c"), 1)

    eleza test_fetch_prev_cyclic(self):
        prefix = ''
        test = self.fetch_test
        test(True, line2, prefix, 1)
        test(True, line1, prefix, 0)
        test(True, prefix, None, None, bell=True)

    eleza test_fetch_next_cyclic(self):
        prefix = ''
        test  = self.fetch_test
        test(False, line1, prefix, 0)
        test(False, line2, prefix, 1)
        test(False, prefix, None, None, bell=True)

    # Prefix 'a' tests skip line2, which starts with 'b'
    eleza test_fetch_prev_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(True, line1, prefix, 0)
        self.fetch_test(True, prefix, None, None, bell=True)

    eleza test_fetch_next_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(False, line1, prefix, 0)
        self.fetch_test(False, prefix, None, None, bell=True)

    eleza test_fetch_prev_noncyclic(self):
        prefix = ''
        self.history.cyclic = False
        test = self.fetch_test
        test(True, line2, prefix, 1)
        test(True, line1, prefix, 0)
        test(True, line1, prefix, 0, bell=True)

    eleza test_fetch_next_noncyclic(self):
        prefix = ''
        self.history.cyclic = False
        test  = self.fetch_test
        test(False, prefix, None, None, bell=True)
        test(True, line2, prefix, 1)
        test(False, prefix, None, None, bell=True)
        test(False, prefix, None, None, bell=True)

    eleza test_fetch_cursor_move(self):
        # Move cursor after fetch
        self.history.fetch(reverse=True)  # initialization
        self.text.mark_set('insert', 'iomark')
        self.fetch_test(True, line2, None, None, bell=True)

    eleza test_fetch_edit(self):
        # Edit after fetch
        self.history.fetch(reverse=True)  # initialization
        self.text.delete('iomark', 'insert', )
        self.text.insert('iomark', 'a =')
        self.fetch_test(True, line1, 'a =', 0)  # prefix is reset

    eleza test_history_prev_next(self):
        # Minimally test functions bound to events
        self.history.history_prev('dummy event')
        self.assertEqual(self.history.pointer, 1)
        self.history.history_next('dummy event')
        self.assertEqual(self.history.pointer, None)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
