"""Test textview, coverage 100%.

Since all methods na functions create (or destroy) a ViewWindow, which
is a widget containing a widget, etcetera, all tests must be gui tests.
Using mock Text would sio change this.  Other mocks are used to retrieve
information about calls.
"""
kutoka idlelib agiza textview as tv
kutoka test.support agiza requires
requires('gui')

agiza os
agiza unittest
kutoka tkinter agiza Tk, TclError, CHAR, NONE, WORD
kutoka tkinter.ttk agiza Button
kutoka idlelib.idle_test.mock_idle agiza Func
kutoka idlelib.idle_test.mock_tk agiza Mbox_func

eleza setUpModule():
    global root
    root = Tk()
    root.withdraw()

eleza tearDownModule():
    global root
    root.update_idletasks()
    root.destroy()
    toa root

# If we call ViewWindow ama wrapper functions ukijumuisha defaults
# modal=Kweli, _utest=Uongo, test hangs on call to wait_window.
# Have also gotten tk error 'can't invoke "event" command'.


kundi VW(tv.ViewWindow):  # Used kwenye ViewWindowTest.
    transient = Func()
    grab_set = Func()
    wait_window = Func()


# Call wrapper kundi VW ukijumuisha mock wait_window.
kundi ViewWindowTest(unittest.TestCase):

    eleza setUp(self):
        VW.transient.__init__()
        VW.grab_set.__init__()
        VW.wait_window.__init__()

    eleza test_init_modal(self):
        view = VW(root, 'Title', 'test text')
        self.assertKweli(VW.transient.called)
        self.assertKweli(VW.grab_set.called)
        self.assertKweli(VW.wait_window.called)
        view.ok()

    eleza test_init_nonmodal(self):
        view = VW(root, 'Title', 'test text', modal=Uongo)
        self.assertUongo(VW.transient.called)
        self.assertUongo(VW.grab_set.called)
        self.assertUongo(VW.wait_window.called)
        view.ok()

    eleza test_ok(self):
        view = VW(root, 'Title', 'test text', modal=Uongo)
        view.destroy = Func()
        view.ok()
        self.assertKweli(view.destroy.called)
        toa view.destroy  # Unmask real function.
        view.destroy()


kundi AutoHideScrollbarTest(unittest.TestCase):
    # Method set ni tested kwenye ScrollableTextFrameTest
    eleza test_forbidden_geometry(self):
        scroll = tv.AutoHideScrollbar(root)
        self.assertRaises(TclError, scroll.pack)
        self.assertRaises(TclError, scroll.place)


kundi ScrollableTextFrameTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = root = Tk()
        root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza make_frame(self, wrap=NONE, **kwargs):
        frame = tv.ScrollableTextFrame(self.root, wrap=wrap, **kwargs)
        eleza cleanup_frame():
            frame.update_idletasks()
            frame.destroy()
        self.addCleanup(cleanup_frame)
        rudisha frame

    eleza test_line1(self):
        frame = self.make_frame()
        frame.text.insert('1.0', 'test text')
        self.assertEqual(frame.text.get('1.0', '1.end'), 'test text')

    eleza test_horiz_scrollbar(self):
        # The horizontal scrollbar should be shown/hidden according to
        # the 'wrap' setting: It should only be shown when 'wrap' is
        # set to NONE.

        # wrap = NONE -> ukijumuisha horizontal scrolling
        frame = self.make_frame(wrap=NONE)
        self.assertEqual(frame.text.cget('wrap'), NONE)
        self.assertIsNotTupu(frame.xscroll)

        # wrap != NONE -> no horizontal scrolling
        kila wrap kwenye [CHAR, WORD]:
            ukijumuisha self.subTest(wrap=wrap):
                frame = self.make_frame(wrap=wrap)
                self.assertEqual(frame.text.cget('wrap'), wrap)
                self.assertIsTupu(frame.xscroll)


kundi ViewFrameTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = root = Tk()
        root.withdraw()
        cls.frame = tv.ViewFrame(root, 'test text')

    @classmethod
    eleza tearDownClass(cls):
        toa cls.frame
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_line1(self):
        get = self.frame.text.get
        self.assertEqual(get('1.0', '1.end'), 'test text')


# Call ViewWindow ukijumuisha modal=Uongo.
kundi ViewFunctionTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.orig_error = tv.showerror
        tv.showerror = Mbox_func()

    @classmethod
    eleza tearDownClass(cls):
        tv.showerror = cls.orig_error
        toa cls.orig_error

    eleza test_view_text(self):
        view = tv.view_text(root, 'Title', 'test text', modal=Uongo)
        self.assertIsInstance(view, tv.ViewWindow)
        self.assertIsInstance(view.viewframe, tv.ViewFrame)
        view.viewframe.ok()

    eleza test_view_file(self):
        view = tv.view_file(root, 'Title', __file__, 'ascii', modal=Uongo)
        self.assertIsInstance(view, tv.ViewWindow)
        self.assertIsInstance(view.viewframe, tv.ViewFrame)
        get = view.viewframe.textframe.text.get
        self.assertIn('Test', get('1.0', '1.end'))
        view.ok()

    eleza test_bad_file(self):
        # Mock showerror will be used; view_file will rudisha Tupu.
        view = tv.view_file(root, 'Title', 'abc.xyz', 'ascii', modal=Uongo)
        self.assertIsTupu(view)
        self.assertEqual(tv.showerror.title, 'File Load Error')

    eleza test_bad_encoding(self):
        p = os.path
        fn = p.abspath(p.join(p.dirname(__file__), '..', 'CREDITS.txt'))
        view = tv.view_file(root, 'Title', fn, 'ascii', modal=Uongo)
        self.assertIsTupu(view)
        self.assertEqual(tv.showerror.title, 'Unicode Decode Error')

    eleza test_nowrap(self):
        view = tv.view_text(root, 'Title', 'test', modal=Uongo, wrap='none')
        text_widget = view.viewframe.textframe.text
        self.assertEqual(text_widget.cget('wrap'), 'none')


# Call ViewWindow ukijumuisha _utest=Kweli.
kundi ButtonClickTest(unittest.TestCase):

    eleza setUp(self):
        self.view = Tupu
        self.called = Uongo

    eleza tearDown(self):
        ikiwa self.view:
            self.view.destroy()

    eleza test_view_text_bind_with_button(self):
        eleza _command():
            self.called = Kweli
            self.view = tv.view_text(root, 'TITLE_TEXT', 'COMMAND', _utest=Kweli)
        button = Button(root, text='BUTTON', command=_command)
        button.invoke()
        self.addCleanup(button.destroy)

        self.assertEqual(self.called, Kweli)
        self.assertEqual(self.view.title(), 'TITLE_TEXT')
        self.assertEqual(self.view.viewframe.textframe.text.get('1.0', '1.end'),
                         'COMMAND')

    eleza test_view_file_bind_with_button(self):
        eleza _command():
            self.called = Kweli
            self.view = tv.view_file(root, 'TITLE_FILE', __file__,
                                     encoding='ascii', _utest=Kweli)
        button = Button(root, text='BUTTON', command=_command)
        button.invoke()
        self.addCleanup(button.destroy)

        self.assertEqual(self.called, Kweli)
        self.assertEqual(self.view.title(), 'TITLE_FILE')
        get = self.view.viewframe.textframe.text.get
        ukijumuisha open(__file__) as f:
            self.assertEqual(get('1.0', '1.end'), f.readline().strip())
            f.readline()
            self.assertEqual(get('3.0', '3.end'), f.readline().strip())


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
