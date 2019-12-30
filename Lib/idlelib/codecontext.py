"""codecontext - display the block context above the edit window

Once code has scrolled off the top of a window, it can be difficult to
determine which block you are in.  This extension implements a pane at the top
of each IDLE edit window which provides block structure hints.  These hints are
the lines which contain the block opening keywords, e.g. 'if', kila the
enclosing block.  The number of hint lines ni determined by the maxlines
variable kwenye the codecontext section of config-extensions.def. Lines which do
sio open blocks are sio shown kwenye the context hints pane.

"""
agiza re
kutoka sys agiza maxsize kama INFINITY

agiza tkinter
kutoka tkinter.constants agiza NSEW, SUNKEN

kutoka idlelib.config agiza idleConf

BLOCKOPENERS = {"class", "def", "elif", "else", "except", "finally", "for",
                "if", "try", "while", "with", "async"}


eleza get_spaces_firstword(codeline, c=re.compile(r"^(\s*)(\w*)")):
    "Extract the beginning whitespace na first word kutoka codeline."
    rudisha c.match(codeline).groups()


eleza get_line_info(codeline):
    """Return tuple of (line indent value, codeline, block start keyword).

    The indentation of empty lines (or comment lines) ni INFINITY.
    If the line does sio start a block, the keyword value ni Uongo.
    """
    spaces, firstword = get_spaces_firstword(codeline)
    indent = len(spaces)
    ikiwa len(codeline) == indent ama codeline[indent] == '#':
        indent = INFINITY
    opener = firstword kwenye BLOCKOPENERS na firstword
    rudisha indent, codeline, opener


kundi CodeContext:
    "Display block context above the edit window."
    UPDATEINTERVAL = 100  # millisec

    eleza __init__(self, editwin):
        """Initialize settings kila context block.

        editwin ni the Editor window kila the context block.
        self.text ni the editor window text widget.

        self.context displays the code context text above the editor text.
          Initially Tupu, it ni toggled via <<toggle-code-context>>.
        self.topvisible ni the number of the top text line displayed.
        self.info ni a list of (line number, indent level, line text,
          block keyword) tuples kila the block structure above topvisible.
          self.info[0] ni initialized ukijumuisha a 'dummy' line which
          starts the toplevel 'block' of the module.

        self.t1 na self.t2 are two timer events on the editor text widget to
          monitor kila changes to the context text ama editor font.
        """
        self.editwin = editwin
        self.text = editwin.text
        self._reset()

    eleza _reset(self):
        self.context = Tupu
        self.cell00 = Tupu
        self.t1 = Tupu
        self.topvisible = 1
        self.info = [(0, -1, "", Uongo)]

    @classmethod
    eleza reload(cls):
        "Load kundi variables kutoka config."
        cls.context_depth = idleConf.GetOption("extensions", "CodeContext",
                                               "maxlines", type="int",
                                               default=15)

    eleza __del__(self):
        "Cancel scheduled events."
        ikiwa self.t1 ni sio Tupu:
            jaribu:
                self.text.after_cancel(self.t1)
            tatizo tkinter.TclError:
                pita
            self.t1 = Tupu

    eleza toggle_code_context_event(self, event=Tupu):
        """Toggle code context display.

        If self.context doesn't exist, create it to match the size of the editor
        window text (toggle on).  If it does exist, destroy it (toggle off).
        Return 'koma' to complete the processing of the binding.
        """
        ikiwa self.context ni Tupu:
            # Calculate the border width na horizontal padding required to
            # align the context ukijumuisha the text kwenye the main Text widget.
            #
            # All values are pitaed through getint(), since some
            # values may be pixel objects, which can't simply be added to ints.
            widgets = self.editwin.text, self.editwin.text_frame
            # Calculate the required horizontal padding na border width.
            padx = 0
            border = 0
            kila widget kwenye widgets:
                info = (widget.grid_info()
                        ikiwa widget ni self.editwin.text
                        isipokua widget.pack_info())
                padx += widget.tk.getint(info['padx'])
                padx += widget.tk.getint(widget.cget('padx'))
                border += widget.tk.getint(widget.cget('border'))
            self.context = tkinter.Text(
                self.editwin.text_frame,
                height=1,
                width=1,  # Don't request more than we get.
                highlightthickness=0,
                padx=padx, border=border, relief=SUNKEN, state='disabled')
            self.update_font()
            self.update_highlight_colors()
            self.context.bind('<ButtonRelease-1>', self.jumptoline)
            # Get the current context na initiate the recurring update event.
            self.timer_event()
            # Grid the context widget above the text widget.
            self.context.grid(row=0, column=1, sticky=NSEW)

            line_number_colors = idleConf.GetHighlight(idleConf.CurrentTheme(),
                                                       'linenumber')
            self.cell00 = tkinter.Frame(self.editwin.text_frame,
                                        bg=line_number_colors['background'])
            self.cell00.grid(row=0, column=0, sticky=NSEW)
            menu_status = 'Hide'
        isipokua:
            self.context.destroy()
            self.context = Tupu
            self.cell00.destroy()
            self.cell00 = Tupu
            self.text.after_cancel(self.t1)
            self._reset()
            menu_status = 'Show'
        self.editwin.update_menu_label(menu='options', index='* Code Context',
                                       label=f'{menu_status} Code Context')
        rudisha "koma"

    eleza get_context(self, new_topvisible, stopline=1, stopindent=0):
        """Return a list of block line tuples na the 'last' indent.

        The tuple fields are (linenum, indent, text, opener).
        The list represents header lines kutoka new_topvisible back to
        stopline ukijumuisha successively shorter indents > stopindent.
        The list ni returned ordered by line number.
        Last indent returned ni the smallest indent observed.
        """
        assert stopline > 0
        lines = []
        # The indentation level we are currently in.
        lastindent = INFINITY
        # For a line to be interesting, it must begin ukijumuisha a block opening
        # keyword, na have less indentation than lastindent.
        kila linenum kwenye range(new_topvisible, stopline-1, -1):
            codeline = self.text.get(f'{linenum}.0', f'{linenum}.end')
            indent, text, opener = get_line_info(codeline)
            ikiwa indent < lastindent:
                lastindent = indent
                ikiwa opener kwenye ("else", "elif"):
                    # Also show the ikiwa statement.
                    lastindent += 1
                ikiwa opener na linenum < new_topvisible na indent >= stopindent:
                    lines.append((linenum, indent, text, opener))
                ikiwa lastindent <= stopindent:
                    koma
        lines.reverse()
        rudisha lines, lastindent

    eleza update_code_context(self):
        """Update context information na lines visible kwenye the context pane.

        No update ni done ikiwa the text hasn't been scrolled.  If the text
        was scrolled, the lines that should be shown kwenye the context will
        be retrieved na the context area will be updated ukijumuisha the code,
        up to the number of maxlines.
        """
        new_topvisible = self.editwin.getlineno("@0,0")
        ikiwa self.topvisible == new_topvisible:      # Haven't scrolled.
            rudisha
        ikiwa self.topvisible < new_topvisible:       # Scroll down.
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.topvisible)
            # Retain only context info applicable to the region
            # between topvisible na new_topvisible.
            wakati self.info[-1][1] >= lastindent:
                toa self.info[-1]
        isipokua:  # self.topvisible > new_topvisible: # Scroll up.
            stopindent = self.info[-1][1] + 1
            # Retain only context info associated
            # ukijumuisha lines above new_topvisible.
            wakati self.info[-1][0] >= new_topvisible:
                stopindent = self.info[-1][1]
                toa self.info[-1]
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.info[-1][0]+1,
                                                 stopindent)
        self.info.extend(lines)
        self.topvisible = new_topvisible
        # Last context_depth context lines.
        context_strings = [x[2] kila x kwenye self.info[-self.context_depth:]]
        showfirst = 0 ikiwa context_strings[0] isipokua 1
        # Update widget.
        self.context['height'] = len(context_strings) - showfirst
        self.context['state'] = 'normal'
        self.context.delete('1.0', 'end')
        self.context.insert('end', '\n'.join(context_strings[showfirst:]))
        self.context['state'] = 'disabled'

    eleza jumptoline(self, event=Tupu):
        "Show clicked context line at top of editor."
        lines = len(self.info)
        ikiwa lines == 1:  # No context lines are showing.
            newtop = 1
        isipokua:
            # Line number clicked.
            contextline = int(float(self.context.index('insert')))
            # Lines sio displayed due to maxlines.
            offset = max(1, lines - self.context_depth) - 1
            newtop = self.info[offset + contextline][0]
        self.text.yview(f'{newtop}.0')
        self.update_code_context()

    eleza timer_event(self):
        "Event on editor text widget triggered every UPDATEINTERVAL ms."
        ikiwa self.context ni sio Tupu:
            self.update_code_context()
            self.t1 = self.text.after(self.UPDATEINTERVAL, self.timer_event)

    eleza update_font(self):
        ikiwa self.context ni sio Tupu:
            font = idleConf.GetFont(self.text, 'main', 'EditorWindow')
            self.context['font'] = font

    eleza update_highlight_colors(self):
        ikiwa self.context ni sio Tupu:
            colors = idleConf.GetHighlight(idleConf.CurrentTheme(), 'context')
            self.context['background'] = colors['background']
            self.context['foreground'] = colors['foreground']

        ikiwa self.cell00 ni sio Tupu:
            line_number_colors = idleConf.GetHighlight(idleConf.CurrentTheme(),
                                                       'linenumber')
            self.cell00.config(bg=line_number_colors['background'])


CodeContext.reload()


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_codecontext', verbosity=2, exit=Uongo)

    # Add htest.
