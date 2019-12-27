"""Test tooltip, coverage 100%.

Coverage is 100% after excluding 6 lines with "# pragma: no cover".
They involve TclErrors that either should or should not happen in a
particular situation, and which are 'pass'ed ikiwa they do.
"""

kutoka idlelib.tooltip agiza TooltipBase, Hovertip
kutoka test.support agiza requires
requires('gui')

kutoka functools agiza wraps
agiza time
kutoka tkinter agiza Button, Tk, Toplevel
agiza unittest


eleza setUpModule():
    global root
    root = Tk()

eleza tearDownModule():
    global root
    root.update_idletasks()
    root.destroy()
    del root


eleza add_call_counting(func):
    @wraps(func)
    eleza wrapped_func(*args, **kwargs):
        wrapped_func.call_args_list.append((args, kwargs))
        rudisha func(*args, **kwargs)
    wrapped_func.call_args_list = []
    rudisha wrapped_func


eleza _make_top_and_button(testobj):
    global root
    top = Toplevel(root)
    testobj.addCleanup(top.destroy)
    top.title("Test tooltip")
    button = Button(top, text='ToolTip test button')
    button.pack()
    testobj.addCleanup(button.destroy)
    top.lift()
    rudisha top, button


kundi ToolTipBaseTest(unittest.TestCase):
    eleza setUp(self):
        self.top, self.button = _make_top_and_button(self)

    eleza test_base_class_is_unusable(self):
        global root
        top = Toplevel(root)
        self.addCleanup(top.destroy)

        button = Button(top, text='ToolTip test button')
        button.pack()
        self.addCleanup(button.destroy)

        with self.assertRaises(NotImplementedError):
            tooltip = TooltipBase(button)
            tooltip.showtip()


kundi HovertipTest(unittest.TestCase):
    eleza setUp(self):
        self.top, self.button = _make_top_and_button(self)

    eleza is_tipwindow_shown(self, tooltip):
        rudisha tooltip.tipwindow and tooltip.tipwindow.winfo_viewable()

    eleza test_showtip(self):
        tooltip = Hovertip(self.button, 'ToolTip text')
        self.addCleanup(tooltip.hidetip)
        self.assertFalse(self.is_tipwindow_shown(tooltip))
        tooltip.showtip()
        self.assertTrue(self.is_tipwindow_shown(tooltip))

    eleza test_showtip_twice(self):
        tooltip = Hovertip(self.button, 'ToolTip text')
        self.addCleanup(tooltip.hidetip)
        self.assertFalse(self.is_tipwindow_shown(tooltip))
        tooltip.showtip()
        self.assertTrue(self.is_tipwindow_shown(tooltip))
        orig_tipwindow = tooltip.tipwindow
        tooltip.showtip()
        self.assertTrue(self.is_tipwindow_shown(tooltip))
        self.assertIs(tooltip.tipwindow, orig_tipwindow)

    eleza test_hidetip(self):
        tooltip = Hovertip(self.button, 'ToolTip text')
        self.addCleanup(tooltip.hidetip)
        tooltip.showtip()
        tooltip.hidetip()
        self.assertFalse(self.is_tipwindow_shown(tooltip))

    eleza test_showtip_on_mouse_enter_no_delay(self):
        tooltip = Hovertip(self.button, 'ToolTip text', hover_delay=None)
        self.addCleanup(tooltip.hidetip)
        tooltip.showtip = add_call_counting(tooltip.showtip)
        root.update()
        self.assertFalse(self.is_tipwindow_shown(tooltip))
        self.button.event_generate('<Enter>', x=0, y=0)
        root.update()
        self.assertTrue(self.is_tipwindow_shown(tooltip))
        self.assertGreater(len(tooltip.showtip.call_args_list), 0)

    eleza test_hover_with_delay(self):
        # Run multiple tests requiring an actual delay simultaneously.

        # Test #1: A hover tip with a non-zero delay appears after the delay.
        tooltip1 = Hovertip(self.button, 'ToolTip text', hover_delay=100)
        self.addCleanup(tooltip1.hidetip)
        tooltip1.showtip = add_call_counting(tooltip1.showtip)
        root.update()
        self.assertFalse(self.is_tipwindow_shown(tooltip1))
        self.button.event_generate('<Enter>', x=0, y=0)
        root.update()
        self.assertFalse(self.is_tipwindow_shown(tooltip1))

        # Test #2: A hover tip with a non-zero delay doesn't appear when
        # the mouse stops hovering over the base widget before the delay
        # expires.
        tooltip2 = Hovertip(self.button, 'ToolTip text', hover_delay=100)
        self.addCleanup(tooltip2.hidetip)
        tooltip2.showtip = add_call_counting(tooltip2.showtip)
        root.update()
        self.button.event_generate('<Enter>', x=0, y=0)
        root.update()
        self.button.event_generate('<Leave>', x=0, y=0)
        root.update()

        time.sleep(0.15)
        root.update()

        # Test #1 assertions.
        self.assertTrue(self.is_tipwindow_shown(tooltip1))
        self.assertGreater(len(tooltip1.showtip.call_args_list), 0)

        # Test #2 assertions.
        self.assertFalse(self.is_tipwindow_shown(tooltip2))
        self.assertEqual(tooltip2.showtip.call_args_list, [])

    eleza test_hidetip_on_mouse_leave(self):
        tooltip = Hovertip(self.button, 'ToolTip text', hover_delay=None)
        self.addCleanup(tooltip.hidetip)
        tooltip.showtip = add_call_counting(tooltip.showtip)
        root.update()
        self.button.event_generate('<Enter>', x=0, y=0)
        root.update()
        self.button.event_generate('<Leave>', x=0, y=0)
        root.update()
        self.assertFalse(self.is_tipwindow_shown(tooltip))
        self.assertGreater(len(tooltip.showtip.call_args_list), 0)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
