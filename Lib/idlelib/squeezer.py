"""An IDLE extension to avoid having very long texts printed kwenye the shell.

A common problem kwenye IDLE's interactive shell ni printing of large amounts of
text into the shell. This makes looking at the previous history difficult.
Worse, this can cause IDLE to become very slow, even to the point of being
completely unusable.

This extension will automatically replace long texts with a small button.
Double-clicking this button will remove it na insert the original text instead.
Middle-clicking will copy the text to the clipboard. Right-clicking will open
the text kwenye a separate viewing window.

Additionally, any output can be manually "squeezed" by the user. This includes
output written to the standard error stream ("stderr"), such kama exception
messages na their tracebacks.
"""
agiza re

agiza tkinter kama tk
agiza tkinter.messagebox kama tkMessageBox

kutoka idlelib.config agiza idleConf
kutoka idlelib.textview agiza view_text
kutoka idlelib.tooltip agiza Hovertip
kutoka idlelib agiza macosx


eleza count_lines_with_wrapping(s, linewidth=80):
    """Count the number of lines kwenye a given string.

    Lines are counted kama ikiwa the string was wrapped so that lines are never over
    linewidth characters long.

    Tabs are considered tabwidth characters long.
    """
    tabwidth = 8  # Currently always true kwenye Shell.
    pos = 0
    linecount = 1
    current_column = 0

    kila m kwenye re.finditer(r"[\t\n]", s):
        # Process the normal chars up to tab ama newline.
        numchars = m.start() - pos
        pos += numchars
        current_column += numchars

        # Deal with tab ama newline.
        ikiwa s[pos] == '\n':
            # Avoid the `current_column == 0` edge-case, na wakati we're
            # at it, don't bother adding 0.
            ikiwa current_column > linewidth:
                # If the current column was exactly linewidth, divmod
                # would give (1,0), even though a new line hadn't yet
                # been started. The same ni true ikiwa length ni any exact
                # multiple of linewidth. Therefore, subtract 1 before
                # dividing a non-empty line.
                linecount += (current_column - 1) // linewidth
            linecount += 1
            current_column = 0
        isipokua:
            assert s[pos] == '\t'
            current_column += tabwidth - (current_column % tabwidth)

            # If a tab pitaes the end of the line, consider the entire
            # tab kama being on the next line.
            ikiwa current_column > linewidth:
                linecount += 1
                current_column = tabwidth

        pos += 1 # After the tab ama newline.

    # Process remaining chars (no more tabs ama newlines).
    current_column += len(s) - pos
    # Avoid divmod(-1, linewidth).
    ikiwa current_column > 0:
        linecount += (current_column - 1) // linewidth
    isipokua:
        # Text ended with newline; don't count an extra line after it.
        linecount -= 1

    rudisha linecount


kundi ExpandingButton(tk.Button):
    """Class kila the "squeezed" text buttons used by Squeezer

    These buttons are displayed inside a Tk Text widget kwenye place of text. A
    user can then use the button to replace it with the original text, copy
    the original text to the clipboard ama view the original text kwenye a separate
    window.

    Each button ni tied to a Squeezer instance, na it knows to update the
    Squeezer instance when it ni expanded (and therefore removed).
    """
    eleza __init__(self, s, tags, numoflines, squeezer):
        self.s = s
        self.tags = tags
        self.numoflines = numoflines
        self.squeezer = squeezer
        self.editwin = editwin = squeezer.editwin
        self.text = text = editwin.text
        # The base Text widget ni needed to change text before iomark.
        self.base_text = editwin.per.bottom

        line_plurality = "lines" ikiwa numoflines != 1 else "line"
        button_text = f"Squeezed text ({numoflines} {line_plurality})."
        tk.Button.__init__(self, text, text=button_text,
                           background="#FFFFC0", activebackground="#FFFFE0")

        button_tooltip_text = (
            "Double-click to expand, right-click kila more options."
        )
        Hovertip(self, button_tooltip_text, hover_delay=80)

        self.bind("<Double-Button-1>", self.expand)
        ikiwa macosx.isAquaTk():
            # AquaTk defines <2> kama the right button, sio <3>.
            self.bind("<Button-2>", self.context_menu_event)
        isipokua:
            self.bind("<Button-3>", self.context_menu_event)
        self.selection_handle(  # X windows only.
            lambda offset, length: s[int(offset):int(offset) + int(length)])

        self.is_dangerous = Tupu
        self.after_idle(self.set_is_dangerous)

    eleza set_is_dangerous(self):
        dangerous_line_len = 50 * self.text.winfo_width()
        self.is_dangerous = (
            self.numoflines > 1000 or
            len(self.s) > 50000 or
            any(
                len(line_match.group(0)) >= dangerous_line_len
                kila line_match kwenye re.finditer(r'[^\n]+', self.s)
            )
        )

    eleza expand(self, event=Tupu):
        """expand event handler

        This inserts the original text kwenye place of the button kwenye the Text
        widget, removes the button na updates the Squeezer instance.

        If the original text ni dangerously long, i.e. expanding it could
        cause a performance degradation, ask the user kila confirmation.
        """
        ikiwa self.is_dangerous ni Tupu:
            self.set_is_dangerous()
        ikiwa self.is_dangerous:
            confirm = tkMessageBox.askokcancel(
                title="Expand huge output?",
                message="\n\n".join([
                    "The squeezed output ni very long: %d lines, %d chars.",
                    "Expanding it could make IDLE slow ama unresponsive.",
                    "It ni recommended to view ama copy the output instead.",
                    "Really expand?"
                ]) % (self.numoflines, len(self.s)),
                default=tkMessageBox.CANCEL,
                parent=self.text)
            ikiwa sio confirm:
                rudisha "koma"

        self.base_text.insert(self.text.index(self), self.s, self.tags)
        self.base_text.delete(self)
        self.squeezer.expandingbuttons.remove(self)

    eleza copy(self, event=Tupu):
        """copy event handler

        Copy the original text to the clipboard.
        """
        self.clipboard_clear()
        self.clipboard_append(self.s)

    eleza view(self, event=Tupu):
        """view event handler

        View the original text kwenye a separate text viewer window.
        """
        view_text(self.text, "Squeezed Output Viewer", self.s,
                  modal=Uongo, wrap='none')

    rmenu_specs = (
        # Item structure: (label, method_name).
        ('copy', 'copy'),
        ('view', 'view'),
    )

    eleza context_menu_event(self, event):
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        rmenu = tk.Menu(self.text, tearoff=0)
        kila label, method_name kwenye self.rmenu_specs:
            rmenu.add_command(label=label, command=getattr(self, method_name))
        rmenu.tk_popup(event.x_root, event.y_root)
        rudisha "koma"


kundi Squeezer:
    """Replace long outputs kwenye the shell with a simple button.

    This avoids IDLE's shell slowing down considerably, na even becoming
    completely unresponsive, when very long outputs are written.
    """
    @classmethod
    eleza reload(cls):
        """Load kundi variables kutoka config."""
        cls.auto_squeeze_min_lines = idleConf.GetOption(
            "main", "PyShell", "auto-squeeze-min-lines",
            type="int", default=50,
        )

    eleza __init__(self, editwin):
        """Initialize settings kila Squeezer.

        editwin ni the shell's Editor window.
        self.text ni the editor window text widget.
        self.base_test ni the actual editor window Tk text widget, rather than
            EditorWindow's wrapper.
        self.expandingbuttons ni the list of all buttons representing
            "squeezed" output.
        """
        self.editwin = editwin
        self.text = text = editwin.text

        # Get the base Text widget of the PyShell object, used to change
        # text before the iomark. PyShell deliberately disables changing
        # text before the iomark via its 'text' attribute, which is
        # actually a wrapper kila the actual Text widget. Squeezer,
        # however, needs to make such changes.
        self.base_text = editwin.per.bottom

        # Twice the text widget's border width na internal padding;
        # pre-calculated here kila the get_line_width() method.
        self.window_width_delta = 2 * (
            int(text.cget('border')) +
            int(text.cget('padx'))
        )

        self.expandingbuttons = []

        # Replace the PyShell instance's write method with a wrapper,
        # which inserts an ExpandingButton instead of a long text.
        eleza mywrite(s, tags=(), write=editwin.write):
            # Only auto-squeeze text which has just the "stdout" tag.
            ikiwa tags != "stdout":
                rudisha write(s, tags)

            # Only auto-squeeze text with at least the minimum
            # configured number of lines.
            auto_squeeze_min_lines = self.auto_squeeze_min_lines
            # First, a very quick check to skip very short texts.
            ikiwa len(s) < auto_squeeze_min_lines:
                rudisha write(s, tags)
            # Now the full line-count check.
            numoflines = self.count_lines(s)
            ikiwa numoflines < auto_squeeze_min_lines:
                rudisha write(s, tags)

            # Create an ExpandingButton instance.
            expandingbutton = ExpandingButton(s, tags, numoflines, self)

            # Insert the ExpandingButton into the Text widget.
            text.mark_gravity("iomark", tk.RIGHT)
            text.window_create("iomark", window=expandingbutton,
                               padx=3, pady=5)
            text.see("iomark")
            text.update()
            text.mark_gravity("iomark", tk.LEFT)

            # Add the ExpandingButton to the Squeezer's list.
            self.expandingbuttons.append(expandingbutton)

        editwin.write = mywrite

    eleza count_lines(self, s):
        """Count the number of lines kwenye a given text.

        Before calculation, the tab width na line length of the text are
        fetched, so that up-to-date values are used.

        Lines are counted kama ikiwa the string was wrapped so that lines are never
        over linewidth characters long.

        Tabs are considered tabwidth characters long.
        """
        rudisha count_lines_with_wrapping(s, self.editwin.width)

    eleza squeeze_current_text_event(self, event):
        """squeeze-current-text event handler

        Squeeze the block of text inside which contains the "insert" cursor.

        If the insert cursor ni haiko kwenye a squeezable block of text, give the
        user a small warning na do nothing.
        """
        # Set tag_name to the first valid tag found on the "insert" cursor.
        tag_names = self.text.tag_names(tk.INSERT)
        kila tag_name kwenye ("stdout", "stderr"):
            ikiwa tag_name kwenye tag_names:
                koma
        isipokua:
            # The insert cursor doesn't have a "stdout" ama "stderr" tag.
            self.text.bell()
            rudisha "koma"

        # Find the range to squeeze.
        start, end = self.text.tag_prevrange(tag_name, tk.INSERT + "+1c")
        s = self.text.get(start, end)

        # If the last char ni a newline, remove it kutoka the range.
        ikiwa len(s) > 0 na s[-1] == '\n':
            end = self.text.index("%s-1c" % end)
            s = s[:-1]

        # Delete the text.
        self.base_text.delete(start, end)

        # Prepare an ExpandingButton.
        numoflines = self.count_lines(s)
        expandingbutton = ExpandingButton(s, tag_name, numoflines, self)

        # insert the ExpandingButton to the Text
        self.text.window_create(start, window=expandingbutton,
                                padx=3, pady=5)

        # Insert the ExpandingButton to the list of ExpandingButtons,
        # wakati keeping the list ordered according to the position of
        # the buttons kwenye the Text widget.
        i = len(self.expandingbuttons)
        wakati i > 0 na self.text.compare(self.expandingbuttons[i-1],
                                          ">", expandingbutton):
            i -= 1
        self.expandingbuttons.insert(i, expandingbutton)

        rudisha "koma"


Squeezer.reload()


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_squeezer', verbosity=2, exit=Uongo)

    # Add htest.
