"""Tools for displaying tool-tips.

This includes:
 * an abstract base-kundi for different kinds of tooltips
 * a simple text-only Tooltip class
"""
kutoka tkinter agiza *


kundi TooltipBase(object):
    """abstract base kundi for tooltips"""

    eleza __init__(self, anchor_widget):
        """Create a tooltip.

        anchor_widget: the widget next to which the tooltip will be shown

        Note that a widget will only be shown when showtip() is called.
        """
        self.anchor_widget = anchor_widget
        self.tipwindow = None

    eleza __del__(self):
        self.hidetip()

    eleza showtip(self):
        """display the tooltip"""
        ikiwa self.tipwindow:
            return
        self.tipwindow = tw = Toplevel(self.anchor_widget)
        # show no border on the top level window
        tw.wm_overrideredirect(1)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

    eleza position_window(self):
        """(re)-set the tooltip's screen position"""
        x, y = self.get_position()
        root_x = self.anchor_widget.winfo_rootx() + x
        root_y = self.anchor_widget.winfo_rooty() + y
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    eleza get_position(self):
        """choose a screen position for the tooltip"""
        # The tip window must be completely outside the anchor widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        #
        # Note: This is a simplistic implementation; sub-classes will likely
        # want to override this.
        rudisha 20, self.anchor_widget.winfo_height() + 1

    eleza showcontents(self):
        """content display hook for sub-classes"""
        # See ToolTip for an example
        raise NotImplementedError

    eleza hidetip(self):
        """hide the tooltip"""
        # Note: This is called by __del__, so careful when overriding/extending
        tw = self.tipwindow
        self.tipwindow = None
        ikiwa tw:
            try:
                tw.destroy()
            except TclError:  # pragma: no cover
                pass


kundi OnHoverTooltipBase(TooltipBase):
    """abstract base kundi for tooltips, with delayed on-hover display"""

    eleza __init__(self, anchor_widget, hover_delay=1000):
        """Create a tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(OnHoverTooltipBase, self).__init__(anchor_widget)
        self.hover_delay = hover_delay

        self._after_id = None
        self._id1 = self.anchor_widget.bind("<Enter>", self._show_event)
        self._id2 = self.anchor_widget.bind("<Leave>", self._hide_event)
        self._id3 = self.anchor_widget.bind("<Button>", self._hide_event)

    eleza __del__(self):
        try:
            self.anchor_widget.unbind("<Enter>", self._id1)
            self.anchor_widget.unbind("<Leave>", self._id2)  # pragma: no cover
            self.anchor_widget.unbind("<Button>", self._id3) # pragma: no cover
        except TclError:
            pass
        super(OnHoverTooltipBase, self).__del__()

    eleza _show_event(self, event=None):
        """event handler to display the tooltip"""
        ikiwa self.hover_delay:
            self.schedule()
        else:
            self.showtip()

    eleza _hide_event(self, event=None):
        """event handler to hide the tooltip"""
        self.hidetip()

    eleza schedule(self):
        """schedule the future display of the tooltip"""
        self.unschedule()
        self._after_id = self.anchor_widget.after(self.hover_delay,
                                                  self.showtip)

    eleza unschedule(self):
        """cancel the future display of the tooltip"""
        after_id = self._after_id
        self._after_id = None
        ikiwa after_id:
            self.anchor_widget.after_cancel(after_id)

    eleza hidetip(self):
        """hide the tooltip"""
        try:
            self.unschedule()
        except TclError:  # pragma: no cover
            pass
        super(OnHoverTooltipBase, self).hidetip()


kundi Hovertip(OnHoverTooltipBase):
    "A tooltip that pops up when a mouse hovers over an anchor widget."
    eleza __init__(self, anchor_widget, text, hover_delay=1000):
        """Create a text tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text

    eleza showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1)
        label.pack()


eleza _tooltip(parent):  # htest #
    top = Toplevel(parent)
    top.title("Test tooltip")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x, y + 150))
    label = Label(top, text="Place your mouse over buttons")
    label.pack()
    button1 = Button(top, text="Button 1 -- 1/2 second hover delay")
    button1.pack()
    Hovertip(button1, "This is tooltip text for button1.", hover_delay=500)
    button2 = Button(top, text="Button 2 -- no hover delay")
    button2.pack()
    Hovertip(button2, "This is tooltip\ntext for button2.", hover_delay=None)


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_tooltip', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_tooltip)
