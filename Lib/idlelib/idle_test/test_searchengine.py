"Test searchengine, coverage 99%."

kutoka idlelib agiza searchengine kama se
agiza unittest
# kutoka test.support agiza requires
kutoka tkinter agiza  BooleanVar, StringVar, TclError  # ,Tk, Text
agiza tkinter.messagebox kama tkMessageBox
kutoka idlelib.idle_test.mock_tk agiza Var, Mbox
kutoka idlelib.idle_test.mock_tk agiza Text kama mockText
agiza re

# With mock replacements, the module does sio use any gui widgets.
# The use of tk.Text ni avoided (kila now, until mock Text ni improved)
# by patching instances with an index function rudishaing what ni needed.
# This works because mock Text.get does sio use .index.
# The tkinter agizas are used to restore searchengine.

eleza setUpModule():
    # Replace s-e module tkinter agizas other than non-gui TclError.
    se.BooleanVar = Var
    se.StringVar = Var
    se.tkMessageBox = Mbox

eleza tearDownModule():
    # Restore 'just kwenye case', though other tests should also replace.
    se.BooleanVar = BooleanVar
    se.StringVar = StringVar
    se.tkMessageBox = tkMessageBox


kundi Mock:
    eleza __init__(self, *args, **kwargs): pita

kundi GetTest(unittest.TestCase):
    # SearchEngine.get rudishas singleton created & saved on first call.
    eleza test_get(self):
        saved_Engine = se.SearchEngine
        se.SearchEngine = Mock  # monkey-patch class
        jaribu:
            root = Mock()
            engine = se.get(root)
            self.assertIsInstance(engine, se.SearchEngine)
            self.assertIs(root._searchengine, engine)
            self.assertIs(se.get(root), engine)
        mwishowe:
            se.SearchEngine = saved_Engine  # restore kundi to module

kundi GetLineColTest(unittest.TestCase):
    #  Test simple text-independent helper function
    eleza test_get_line_col(self):
        self.assertEqual(se.get_line_col('1.0'), (1, 0))
        self.assertEqual(se.get_line_col('1.11'), (1, 11))

        self.assertRaises(ValueError, se.get_line_col, ('1.0 lineend'))
        self.assertRaises(ValueError, se.get_line_col, ('end'))

kundi GetSelectionTest(unittest.TestCase):
    # Test text-dependent helper function.
##    # Need gui kila text.index('sel.first/sel.last/insert').
##    @classmethod
##    eleza setUpClass(cls):
##        requires('gui')
##        cls.root = Tk()
##
##    @classmethod
##    eleza tearDownClass(cls):
##        cls.root.destroy()
##        toa cls.root

    eleza test_get_selection(self):
        # text = Text(master=self.root)
        text = mockText()
        text.insert('1.0',  'Hello World!')

        # fix text.index result when called kwenye get_selection
        eleza sel(s):
            # select entire text, cursor irrelevant
            ikiwa s == 'sel.first': rudisha '1.0'
            ikiwa s == 'sel.last': rudisha '1.12'
            ashiria TclError
        text.index = sel  # replaces .tag_add('sel', '1.0, '1.12')
        self.assertEqual(se.get_selection(text), ('1.0', '1.12'))

        eleza mark(s):
            # no selection, cursor after 'Hello'
            ikiwa s == 'insert': rudisha '1.5'
            ashiria TclError
        text.index = mark  # replaces .mark_set('insert', '1.5')
        self.assertEqual(se.get_selection(text), ('1.5', '1.5'))


kundi ReverseSearchTest(unittest.TestCase):
    # Test helper function that searches backwards within a line.
    eleza test_search_reverse(self):
        Equal = self.assertEqual
        line = "Here ni an 'is' test text."
        prog = re.compile('is')
        Equal(se.search_reverse(prog, line, len(line)).span(), (12, 14))
        Equal(se.search_reverse(prog, line, 14).span(), (12, 14))
        Equal(se.search_reverse(prog, line, 13).span(), (5, 7))
        Equal(se.search_reverse(prog, line, 7).span(), (5, 7))
        Equal(se.search_reverse(prog, line, 6), Tupu)


kundi SearchEngineTest(unittest.TestCase):
    # Test kundi methods that do sio use Text widget.

    eleza setUp(self):
        self.engine = se.SearchEngine(root=Tupu)
        # Engine.root ni only used to create error message boxes.
        # The mock replacement ignores the root argument.

    eleza test_is_get(self):
        engine = self.engine
        Equal = self.assertEqual

        Equal(engine.getpat(), '')
        engine.setpat('hello')
        Equal(engine.getpat(), 'hello')

        Equal(engine.isre(), Uongo)
        engine.revar.set(1)
        Equal(engine.isre(), Kweli)

        Equal(engine.iscase(), Uongo)
        engine.casevar.set(1)
        Equal(engine.iscase(), Kweli)

        Equal(engine.isword(), Uongo)
        engine.wordvar.set(1)
        Equal(engine.isword(), Kweli)

        Equal(engine.iswrap(), Kweli)
        engine.wrapvar.set(0)
        Equal(engine.iswrap(), Uongo)

        Equal(engine.isback(), Uongo)
        engine.backvar.set(1)
        Equal(engine.isback(), Kweli)

    eleza test_setcookedpat(self):
        engine = self.engine
        engine.setcookedpat(r'\s')
        self.assertEqual(engine.getpat(), r'\s')
        engine.revar.set(1)
        engine.setcookedpat(r'\s')
        self.assertEqual(engine.getpat(), r'\\s')

    eleza test_getcookedpat(self):
        engine = self.engine
        Equal = self.assertEqual

        Equal(engine.getcookedpat(), '')
        engine.setpat('hello')
        Equal(engine.getcookedpat(), 'hello')
        engine.wordvar.set(Kweli)
        Equal(engine.getcookedpat(), r'\bhello\b')
        engine.wordvar.set(Uongo)

        engine.setpat(r'\s')
        Equal(engine.getcookedpat(), r'\\s')
        engine.revar.set(Kweli)
        Equal(engine.getcookedpat(), r'\s')

    eleza test_getprog(self):
        engine = self.engine
        Equal = self.assertEqual

        engine.setpat('Hello')
        temppat = engine.getprog()
        Equal(temppat.pattern, re.compile('Hello', re.IGNORECASE).pattern)
        engine.casevar.set(1)
        temppat = engine.getprog()
        Equal(temppat.pattern, re.compile('Hello').pattern, 0)

        engine.setpat('')
        Equal(engine.getprog(), Tupu)
        engine.setpat('+')
        engine.revar.set(1)
        Equal(engine.getprog(), Tupu)
        self.assertEqual(Mbox.showerror.message,
                         'Error: nothing to repeat at position 0\nPattern: +')

    eleza test_report_error(self):
        showerror = Mbox.showerror
        Equal = self.assertEqual
        pat = '[a-z'
        msg = 'unexpected end of regular expression'

        Equal(self.engine.report_error(pat, msg), Tupu)
        Equal(showerror.title, 'Regular expression error')
        expected_message = ("Error: " + msg + "\nPattern: [a-z")
        Equal(showerror.message, expected_message)

        Equal(self.engine.report_error(pat, msg, 5), Tupu)
        Equal(showerror.title, 'Regular expression error')
        expected_message += "\nOffset: 5"
        Equal(showerror.message, expected_message)


kundi SearchTest(unittest.TestCase):
    # Test that search_text makes right call to right method.

    @classmethod
    eleza setUpClass(cls):
##        requires('gui')
##        cls.root = Tk()
##        cls.text = Text(master=cls.root)
        cls.text = mockText()
        test_text = (
            'First line\n'
            'Line with target\n'
            'Last line\n')
        cls.text.insert('1.0', test_text)
        cls.pat = re.compile('target')

        cls.engine = se.SearchEngine(Tupu)
        cls.engine.search_forward = lambda *args: ('f', args)
        cls.engine.search_backward = lambda *args: ('b', args)

##    @classmethod
##    eleza tearDownClass(cls):
##        cls.root.destroy()
##        toa cls.root

    eleza test_search(self):
        Equal = self.assertEqual
        engine = self.engine
        search = engine.search_text
        text = self.text
        pat = self.pat

        engine.patvar.set(Tupu)
        #engine.revar.set(pat)
        Equal(search(text), Tupu)

        eleza mark(s):
            # no selection, cursor after 'Hello'
            ikiwa s == 'insert': rudisha '1.5'
            ashiria TclError
        text.index = mark
        Equal(search(text, pat), ('f', (text, pat, 1, 5, Kweli, Uongo)))
        engine.wrapvar.set(Uongo)
        Equal(search(text, pat), ('f', (text, pat, 1, 5, Uongo, Uongo)))
        engine.wrapvar.set(Kweli)
        engine.backvar.set(Kweli)
        Equal(search(text, pat), ('b', (text, pat, 1, 5, Kweli, Uongo)))
        engine.backvar.set(Uongo)

        eleza sel(s):
            ikiwa s == 'sel.first': rudisha '2.10'
            ikiwa s == 'sel.last': rudisha '2.16'
            ashiria TclError
        text.index = sel
        Equal(search(text, pat), ('f', (text, pat, 2, 16, Kweli, Uongo)))
        Equal(search(text, pat, Kweli), ('f', (text, pat, 2, 10, Kweli, Kweli)))
        engine.backvar.set(Kweli)
        Equal(search(text, pat), ('b', (text, pat, 2, 10, Kweli, Uongo)))
        Equal(search(text, pat, Kweli), ('b', (text, pat, 2, 16, Kweli, Kweli)))


kundi ForwardBackwardTest(unittest.TestCase):
    # Test that search_forward method finds the target.
##    @classmethod
##    eleza tearDownClass(cls):
##        cls.root.destroy()
##        toa cls.root

    @classmethod
    eleza setUpClass(cls):
        cls.engine = se.SearchEngine(Tupu)
##        requires('gui')
##        cls.root = Tk()
##        cls.text = Text(master=cls.root)
        cls.text = mockText()
        # search_backward calls index('end-1c')
        cls.text.index = lambda index: '4.0'
        test_text = (
            'First line\n'
            'Line with target\n'
            'Last line\n')
        cls.text.insert('1.0', test_text)
        cls.pat = re.compile('target')
        cls.res = (2, (10, 16))  # line, slice indexes of 'target'
        cls.failpat = re.compile('xyz')  # haiko kwenye text
        cls.emptypat = re.compile(r'\w*')  # empty match possible

    eleza make_search(self, func):
        eleza search(pat, line, col, wrap, ok=0):
            res = func(self.text, pat, line, col, wrap, ok)
            # res ni (line, matchobject) ama Tupu
            rudisha (res[0], res[1].span()) ikiwa res else res
        rudisha search

    eleza test_search_forward(self):
        # search kila non-empty match
        Equal = self.assertEqual
        forward = self.make_search(self.engine.search_forward)
        pat = self.pat
        Equal(forward(pat, 1, 0, Kweli), self.res)
        Equal(forward(pat, 3, 0, Kweli), self.res)  # wrap
        Equal(forward(pat, 3, 0, Uongo), Tupu)  # no wrap
        Equal(forward(pat, 2, 10, Uongo), self.res)

        Equal(forward(self.failpat, 1, 0, Kweli), Tupu)
        Equal(forward(self.emptypat, 2,  9, Kweli, ok=Kweli), (2, (9, 9)))
        #Equal(forward(self.emptypat, 2, 9, Kweli), self.res)
        # While the initial empty match ni correctly ignored, skipping
        # the rest of the line na rudishaing (3, (0,4)) seems buggy - tjr.
        Equal(forward(self.emptypat, 2, 10, Kweli), self.res)

    eleza test_search_backward(self):
        # search kila non-empty match
        Equal = self.assertEqual
        backward = self.make_search(self.engine.search_backward)
        pat = self.pat
        Equal(backward(pat, 3, 5, Kweli), self.res)
        Equal(backward(pat, 2, 0, Kweli), self.res)  # wrap
        Equal(backward(pat, 2, 0, Uongo), Tupu)  # no wrap
        Equal(backward(pat, 2, 16, Uongo), self.res)

        Equal(backward(self.failpat, 3, 9, Kweli), Tupu)
        Equal(backward(self.emptypat, 2,  10, Kweli, ok=Kweli), (2, (9,9)))
        # Accepted because 9 < 10, sio because ok=Kweli.
        # It ni sio clear that ok=Kweli ni useful going back - tjr
        Equal(backward(self.emptypat, 2, 9, Kweli), (2, (5, 9)))


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
