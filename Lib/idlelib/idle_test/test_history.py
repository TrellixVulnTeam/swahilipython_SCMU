" Test history, coverage 100%."

kutoka idlelib.history agiza History
agiza unittest
kutoka test.support agiza requires

agiza tkinter kama tk
kutoka tkinter agiza Text kama tkText
kutoka idlelib.idle_test.mock_tk agiza Text kama mkText
kutoka idlelib.config agiza idleConf

line1 = 'a = 7'
line2 = 'b = a'


kundi StoreTest(unittest.TestCase):
    '''Tests History.__init__ na History.store ukijumuisha mock Text'''

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
        self.assertIsTupu(self.history.prefix)
        self.assertIsTupu(self.history.pointer)
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
        self.assertIsTupu(self.history.prefix)
        self.assertIsTupu(self.history.pointer)


kundi TextWrapper:
    eleza __init__(self, master):
        self.text = tkText(master=master)
        self._bell = Uongo
    eleza __getattr__(self, name):
        rudisha getattr(self.text, name)
    eleza bell(self):
        self._bell = Kweli


kundi FetchTest(unittest.TestCase):
    '''Test History.fetch ukijumuisha wrapped tk.Text.
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
        toa cls.root

    eleza fetch_test(self, reverse, line, prefix, index, *, bell=Uongo):
        # Perform one fetch kama invoked by Alt-N ama Alt-P
        # Test the result. The line test ni the most agizaant.
        # The last two are diagnostic of fetch internals.
        History = self.history
        History.fetch(reverse)

        Equal = self.assertEqual
        Equal(self.text.get('iomark', 'end-1c'), line)
        Equal(self.text._bell, bell)
        ikiwa bell:
            self.text._bell = Uongo
        Equal(History.prefix, prefix)
        Equal(History.pointer, index)
        Equal(self.text.compare("insert", '==', "end-1c"), 1)

    eleza test_fetch_prev_cyclic(self):
        prefix = ''
        test = self.fetch_test
        test(Kweli, line2, prefix, 1)
        test(Kweli, line1, prefix, 0)
        test(Kweli, prefix, Tupu, Tupu, bell=Kweli)

    eleza test_fetch_next_cyclic(self):
        prefix = ''
        test  = self.fetch_test
        test(Uongo, line1, prefix, 0)
        test(Uongo, line2, prefix, 1)
        test(Uongo, prefix, Tupu, Tupu, bell=Kweli)

    # Prefix 'a' tests skip line2, which starts ukijumuisha 'b'
    eleza test_fetch_prev_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(Kweli, line1, prefix, 0)
        self.fetch_test(Kweli, prefix, Tupu, Tupu, bell=Kweli)

    eleza test_fetch_next_prefix(self):
        prefix = 'a'
        self.text.insert('iomark', prefix)
        self.fetch_test(Uongo, line1, prefix, 0)
        self.fetch_test(Uongo, prefix, Tupu, Tupu, bell=Kweli)

    eleza test_fetch_prev_noncyclic(self):
        prefix = ''
        self.history.cyclic = Uongo
        test = self.fetch_test
        test(Kweli, line2, prefix, 1)
        test(Kweli, line1, prefix, 0)
        test(Kweli, line1, prefix, 0, bell=Kweli)

    eleza test_fetch_next_noncyclic(self):
        prefix = ''
        self.history.cyclic = Uongo
        test  = self.fetch_test
        test(Uongo, prefix, Tupu, Tupu, bell=Kweli)
        test(Kweli, line2, prefix, 1)
        test(Uongo, prefix, Tupu, Tupu, bell=Kweli)
        test(Uongo, prefix, Tupu, Tupu, bell=Kweli)

    eleza test_fetch_cursor_move(self):
        # Move cursor after fetch
        self.history.fetch(reverse=Kweli)  # initialization
        self.text.mark_set('insert', 'iomark')
        self.fetch_test(Kweli, line2, Tupu, Tupu, bell=Kweli)

    eleza test_fetch_edit(self):
        # Edit after fetch
        self.history.fetch(reverse=Kweli)  # initialization
        self.text.delete('iomark', 'insert', )
        self.text.insert('iomark', 'a =')
        self.fetch_test(Kweli, line1, 'a =', 0)  # prefix ni reset

    eleza test_history_prev_next(self):
        # Minimally test functions bound to events
        self.history.history_prev('dummy event')
        self.assertEqual(self.history.pointer, 1)
        self.history.history_next('dummy event')
        self.assertEqual(self.history.pointer, Tupu)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
