"""Tools kila displaying tool-tips.

This includes:
 * an abstract base-kundi kila different kinds of tooltips
 * a simple text-only Tooltip class
"""
kutoka tkinter agiza *


kundi TooltipBase(object):
    """abstract base kundi kila tooltips"""

    eleza __init__(self, anchor_widget):
        """Create a tooltip.

        anchor_widget: the widget next to which the tooltip will be shown

        Note that a widget will only be shown when showtip() ni called.
        """
        self.anchor_widget = anchor_widget
        self.tipwindow = Tupu

    eleza __del__(self):
        self.hidetip()

    eleza showtip(self):
        """display the tooltip"""
        ikiwa self.tipwindow:
            return
        self.tipwindow = tw = Toplevel(self.anchor_widget)
        # show no border on the top level window
        tw.wm_overrideredirect(1)
        jaribu:
            # This command ni only needed na available on Tk >= 8.4.0 kila OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug kwenye Tk 8.5.18+ (issue #24570)

    eleza position_window(self):
        """(re)-set the tooltip's screen position"""
        x, y = self.get_position()
        root_x = self.anchor_widget.winfo_rootx() + x
        root_y = self.anchor_widget.winfo_rooty() + y
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    eleza get_position(self):
        """choose a screen position kila the tooltip"""
        # The tip window must be completely outside the anchor widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event na it disappears, na then we get an enter
        # event na it reappears, na so on forever :-(
        #
        # Note: This ni a simplistic implementation; sub-classes will likely
        # want to override this.
        rudisha 20, self.anchor_widget.winfo_height() + 1

    eleza showcontents(self):
        """content display hook kila sub-classes"""
        # See ToolTip kila an example
         ashiria NotImplementedError

    eleza hidetip(self):
        """hide the tooltip"""
        # Note: This ni called by __del__, so careful when overriding/extending
        tw = self.tipwindow
        self.tipwindow = Tupu
        ikiwa tw:
            jaribu:
                tw.destroy()
            except TclError:  # pragma: no cover
                pass


kundi OnHoverTooltipBase(TooltipBase):
    """abstract base kundi kila tooltips, ukijumuisha delayed on-hover display"""

    eleza __init__(self, anchor_widget, hover_delay=1000):
        """Create a tooltip ukijumuisha a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, kwenye milliseconds

        Note that a widget will only be shown when showtip() ni called,
        e.g. after hovering over the anchor widget ukijumuisha the mouse kila enough
        time.
        """
        super(OnHoverTooltipBase, self).__init__(anchor_widget)
        self.hover_delay = hover_delay

        self._after_id = Tupu
        self._id1 = self.anchor_widget.bind("<Enter>", self._show_event)
        self._id2 = self.anchor_widget.bind("<Leave>", self._hide_event)
        self._id3 = self.anchor_widget.bind("<Button>", self._hide_event)

    eleza __del__(self):
        jaribu:
            self.anchor_widget.unbind("<Enter>", self._id1)
            self.anchor_widget.unbind("<Leave>", self._id2)  # pragma: no cover
            self.anchor_widget.unbind("<Button>", self._id3) # pragma: no cover
        except TclError:
            pass
        super(OnHoverTooltipBase, self).__del__()

    eleza _show_event(self, event=Tupu):
        """event handler to display the tooltip"""
        ikiwa self.hover_delay:
            self.schedule()
        isipokua:
            self.showtip()

    eleza _hide_event(self, event=Tupu):
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
        self._after_id = Tupu
        ikiwa after_id:
            self.anchor_widget.after_cancel(after_id)

    eleza hidetip(self):
        """hide the tooltip"""
        jaribu:
            self.unschedule()
        except TclError:  # pragma: no cover
            pass
        super(OnHoverTooltipBase, self).hidetip()


kundi Hovertip(OnHoverTooltipBase):
    "A tooltip that pops up when a mouse hovers over an anchor widget."
    eleza __init__(self, anchor_widget, text, hover_delay=1000):
        """Create a text tooltip ukijumuisha a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, kwenye milliseconds

        Note that a widget will only be shown when showtip() ni called,
        e.g. after hovering over the anchor widget ukijumuisha the mouse kila enough
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
    Hovertip(button1, "This ni tooltip text kila button1.", hover_delay=500)
    button2 = Button(top, text="Button 2 -- no hover delay")
    button2.pack()
    Hovertip(button2, "This ni tooltip\ntext kila button2.", hover_delay=Tupu)


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_tooltip', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_tooltip)
