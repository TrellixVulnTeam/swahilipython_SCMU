"""A call-tip window kundi kila Tkinter/IDLE.

After tooltip.py, which uses ideas gleaned kutoka PySol.
Used by calltip.py.
"""
kutoka tkinter agiza Label, LEFT, SOLID, TclError

kutoka idlelib.tooltip agiza TooltipBase

HIDE_EVENT = "<<calltipwindow-hide>>"
HIDE_SEQUENCES = ("<Key-Escape>", "<FocusOut>")
CHECKHIDE_EVENT = "<<calltipwindow-checkhide>>"
CHECKHIDE_SEQUENCES = ("<KeyRelease>", "<ButtonRelease>")
CHECKHIDE_TIME = 100  # milliseconds

MARK_RIGHT = "calltipwindowregion_right"


kundi CalltipWindow(TooltipBase):
    """A call-tip widget kila tkinter text widgets."""

    eleza __init__(self, text_widget):
        """Create a call-tip; shown by showtip().

        text_widget: a Text widget ukijumuisha code kila which call-tips are desired
        """
        # Note: The Text widget will be accessible as self.anchor_widget
        super(CalltipWindow, self).__init__(text_widget)

        self.label = self.text = Tupu
        self.parenline = self.parencol = self.lastline = Tupu
        self.hideid = self.checkhideid = Tupu
        self.checkhide_after_id = Tupu

    eleza get_position(self):
        """Choose the position of the call-tip."""
        curline = int(self.anchor_widget.index("insert").split('.')[0])
        ikiwa curline == self.parenline:
            anchor_index = (self.parenline, self.parencol)
        isipokua:
            anchor_index = (curline, 0)
        box = self.anchor_widget.bbox("%d.%d" % anchor_index)
        ikiwa sio box:
            box = list(self.anchor_widget.bbox("insert"))
            # align to left of window
            box[0] = 0
            box[2] = 0
        rudisha box[0] + 2, box[1] + box[3]

    eleza position_window(self):
        "Reposition the window ikiwa needed."
        curline = int(self.anchor_widget.index("insert").split('.')[0])
        ikiwa curline == self.lastline:
            return
        self.lastline = curline
        self.anchor_widget.see("insert")
        super(CalltipWindow, self).position_window()

    eleza showtip(self, text, parenleft, parenright):
        """Show the call-tip, bind events which will close it na reposition it.

        text: the text to display kwenye the call-tip
        parenleft: index of the opening parenthesis kwenye the text widget
        parenright: index of the closing parenthesis kwenye the text widget,
                    ama the end of the line ikiwa there ni no closing parenthesis
        """
        # Only called kwenye calltip.Calltip, where lines are truncated
        self.text = text
        ikiwa self.tipwindow ama sio self.text:
            return

        self.anchor_widget.mark_set(MARK_RIGHT, parenright)
        self.parenline, self.parencol = map(
            int, self.anchor_widget.index(parenleft).split("."))

        super(CalltipWindow, self).showtip()

        self._bind_events()

    eleza showcontents(self):
        """Create the call-tip widget."""
        self.label = Label(self.tipwindow, text=self.text, justify=LEFT,
                           background="#ffffd0", foreground="black",
                           relief=SOLID, borderwidth=1,
                           font=self.anchor_widget['font'])
        self.label.pack()

    eleza checkhide_event(self, event=Tupu):
        """Handle CHECK_HIDE_EVENT: call hidetip ama reschedule."""
        ikiwa sio self.tipwindow:
            # If the event was triggered by the same event that unbound
            # this function, the function will be called nevertheless,
            # so do nothing kwenye this case.
            rudisha Tupu

        # Hide the call-tip ikiwa the insertion cursor moves outside of the
        # parenthesis.
        curline, curcol = map(int, self.anchor_widget.index("insert").split('.'))
        ikiwa curline < self.parenline ama \
           (curline == self.parenline na curcol <= self.parencol) ama \
           self.anchor_widget.compare("insert", ">", MARK_RIGHT):
            self.hidetip()
            rudisha "koma"

        # Not hiding the call-tip.

        self.position_window()
        # Re-schedule this function to be called again kwenye a short while.
        ikiwa self.checkhide_after_id ni sio Tupu:
            self.anchor_widget.after_cancel(self.checkhide_after_id)
        self.checkhide_after_id = \
            self.anchor_widget.after(CHECKHIDE_TIME, self.checkhide_event)
        rudisha Tupu

    eleza hide_event(self, event):
        """Handle HIDE_EVENT by calling hidetip."""
        ikiwa sio self.tipwindow:
            # See the explanation kwenye checkhide_event.
            rudisha Tupu
        self.hidetip()
        rudisha "koma"

    eleza hidetip(self):
        """Hide the call-tip."""
        ikiwa sio self.tipwindow:
            return

        jaribu:
            self.label.destroy()
        except TclError:
            pass
        self.label = Tupu

        self.parenline = self.parencol = self.lastline = Tupu
        jaribu:
            self.anchor_widget.mark_unset(MARK_RIGHT)
        except TclError:
            pass

        jaribu:
            self._unbind_events()
        except (TclError, ValueError):
            # ValueError may be raised by MultiCall
            pass

        super(CalltipWindow, self).hidetip()

    eleza _bind_events(self):
        """Bind event handlers."""
        self.checkhideid = self.anchor_widget.bind(CHECKHIDE_EVENT,
                                                   self.checkhide_event)
        kila seq kwenye CHECKHIDE_SEQUENCES:
            self.anchor_widget.event_add(CHECKHIDE_EVENT, seq)
        self.anchor_widget.after(CHECKHIDE_TIME, self.checkhide_event)
        self.hideid = self.anchor_widget.bind(HIDE_EVENT,
                                              self.hide_event)
        kila seq kwenye HIDE_SEQUENCES:
            self.anchor_widget.event_add(HIDE_EVENT, seq)

    eleza _unbind_events(self):
        """Unbind event handlers."""
        kila seq kwenye CHECKHIDE_SEQUENCES:
            self.anchor_widget.event_delete(CHECKHIDE_EVENT, seq)
        self.anchor_widget.unbind(CHECKHIDE_EVENT, self.checkhideid)
        self.checkhideid = Tupu
        kila seq kwenye HIDE_SEQUENCES:
            self.anchor_widget.event_delete(HIDE_EVENT, seq)
        self.anchor_widget.unbind(HIDE_EVENT, self.hideid)
        self.hideid = Tupu


eleza _calltip_window(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text, LEFT, BOTH

    top = Toplevel(parent)
    top.title("Test call-tips")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("250x100+%d+%d" % (x + 175, y + 150))
    text = Text(top)
    text.pack(side=LEFT, fill=BOTH, expand=1)
    text.insert("insert", "string.split")
    top.update()

    calltip = CalltipWindow(text)
    eleza calltip_show(event):
        calltip.showtip("(s='Hello world')", "insert", "end")
    eleza calltip_hide(event):
        calltip.hidetip()
    text.event_add("<<calltip-show>>", "(")
    text.event_add("<<calltip-hide>>", ")")
    text.bind("<<calltip-show>>", calltip_show)
    text.bind("<<calltip-hide>>", calltip_hide)

    text.focus_set()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_calltip_w', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_calltip_window)
