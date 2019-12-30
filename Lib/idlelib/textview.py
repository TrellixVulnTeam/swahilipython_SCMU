"""Simple text browser kila IDLE

"""
kutoka tkinter agiza Toplevel, Text, TclError,\
    HORIZONTAL, VERTICAL, NS, EW, NSEW, NONE, WORD, SUNKEN
kutoka tkinter.ttk agiza Frame, Scrollbar, Button
kutoka tkinter.messagebox agiza showerror

kutoka functools agiza update_wrapper
kutoka idlelib.colorizer agiza color_config


kundi AutoHideScrollbar(Scrollbar):
    """A scrollbar that ni automatically hidden when sio needed.

    Only the grid geometry manager ni supported.
    """
    eleza set(self, lo, hi):
        ikiwa float(lo) > 0.0 ama float(hi) < 1.0:
            self.grid()
        isipokua:
            self.grid_remove()
        super().set(lo, hi)

    eleza pack(self, **kwargs):
        ashiria TclError(f'{self.__class__.__name__} does sio support "pack"')

    eleza place(self, **kwargs):
        ashiria TclError(f'{self.__class__.__name__} does sio support "place"')


kundi ScrollableTextFrame(Frame):
    """Display text ukijumuisha scrollbar(s)."""

    eleza __init__(self, master, wrap=NONE, **kwargs):
        """Create a frame kila Textview.

        master - master widget kila this frame
        wrap - type of text wrapping to use ('word', 'char' ama 'none')

        All parameters tatizo kila 'wrap' are pitaed to Frame.__init__().

        The Text widget ni accessible via the 'text' attribute.

        Note: Changing the wrapping mode of the text widget after
        instantiation ni sio supported.
        """
        super().__init__(master, **kwargs)

        text = self.text = Text(self, wrap=wrap)
        text.grid(row=0, column=0, sticky=NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # vertical scrollbar
        self.yscroll = AutoHideScrollbar(self, orient=VERTICAL,
                                         takefocus=Uongo,
                                         command=text.yview)
        self.yscroll.grid(row=0, column=1, sticky=NS)
        text['yscrollcommand'] = self.yscroll.set

        # horizontal scrollbar - only when wrap ni set to NONE
        ikiwa wrap == NONE:
            self.xscroll = AutoHideScrollbar(self, orient=HORIZONTAL,
                                             takefocus=Uongo,
                                             command=text.xview)
            self.xscroll.grid(row=1, column=0, sticky=EW)
            text['xscrollcommand'] = self.xscroll.set
        isipokua:
            self.xscroll = Tupu


kundi ViewFrame(Frame):
    "Display TextFrame na Close button."
    eleza __init__(self, parent, contents, wrap='word'):
        """Create a frame kila viewing text ukijumuisha a "Close" button.

        parent - parent widget kila this frame
        contents - text to display
        wrap - type of text wrapping to use ('word', 'char' ama 'none')

        The Text widget ni accessible via the 'text' attribute.
        """
        super().__init__(parent)
        self.parent = parent
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.ok)
        self.textframe = ScrollableTextFrame(self, relief=SUNKEN, height=700)

        text = self.text = self.textframe.text
        text.insert('1.0', contents)
        text.configure(wrap=wrap, highlightthickness=0, state='disabled')
        color_config(text)
        text.focus_set()

        self.button_ok = button_ok = Button(
                self, text='Close', command=self.ok, takefocus=Uongo)
        self.textframe.pack(side='top', expand=Kweli, fill='both')
        button_ok.pack(side='bottom')

    eleza ok(self, event=Tupu):
        """Dismiss text viewer dialog."""
        self.parent.destroy()


kundi ViewWindow(Toplevel):
    "A simple text viewer dialog kila IDLE."

    eleza __init__(self, parent, title, contents, modal=Kweli, wrap=WORD,
                 *, _htest=Uongo, _utest=Uongo):
        """Show the given text kwenye a scrollable window ukijumuisha a 'close' button.

        If modal ni left Kweli, users cansio interact ukijumuisha other windows
        until the textview window ni closed.

        parent - parent of this dialog
        title - string which ni title of popup dialog
        contents - text to display kwenye dialog
        wrap - type of text wrapping to use ('word', 'char' ama 'none')
        _htest - bool; change box location when running htest.
        _utest - bool; don't wait_window when running unittest.
        """
        super().__init__(parent)
        self['borderwidth'] = 5
        # Place dialog below parent ikiwa running htest.
        x = parent.winfo_rootx() + 10
        y = parent.winfo_rooty() + (10 ikiwa sio _htest isipokua 100)
        self.geometry(f'=750x500+{x}+{y}')

        self.title(title)
        self.viewframe = ViewFrame(self, contents, wrap=wrap)
        self.protocol("WM_DELETE_WINDOW", self.ok)
        self.button_ok = button_ok = Button(self, text='Close',
                                            command=self.ok, takefocus=Uongo)
        self.viewframe.pack(side='top', expand=Kweli, fill='both')

        self.is_modal = modal
        ikiwa self.is_modal:
            self.transient(parent)
            self.grab_set()
            ikiwa sio _utest:
                self.wait_window()

    eleza ok(self, event=Tupu):
        """Dismiss text viewer dialog."""
        ikiwa self.is_modal:
            self.grab_release()
        self.destroy()


eleza view_text(parent, title, contents, modal=Kweli, wrap='word', _utest=Uongo):
    """Create text viewer kila given text.

    parent - parent of this dialog
    title - string which ni the title of popup dialog
    contents - text to display kwenye this dialog
    wrap - type of text wrapping to use ('word', 'char' ama 'none')
    modal - controls ikiwa users can interact ukijumuisha other windows wakati this
            dialog ni displayed
    _utest - bool; controls wait_window on unittest
    """
    rudisha ViewWindow(parent, title, contents, modal, wrap=wrap, _utest=_utest)


eleza view_file(parent, title, filename, encoding, modal=Kweli, wrap='word',
              _utest=Uongo):
    """Create text viewer kila text kwenye filename.

    Return error message ikiwa file cansio be read.  Otherwise calls view_text
    ukijumuisha contents of the file.
    """
    jaribu:
        ukijumuisha open(filename, 'r', encoding=encoding) kama file:
            contents = file.read()
    tatizo OSError:
        showerror(title='File Load Error',
                  message=f'Unable to load file {filename!r} .',
                  parent=parent)
    tatizo UnicodeDecodeError kama err:
        showerror(title='Unicode Decode Error',
                  message=str(err),
                  parent=parent)
    isipokua:
        rudisha view_text(parent, title, contents, modal, wrap=wrap,
                         _utest=_utest)
    rudisha Tupu


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_textview', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(ViewWindow)
