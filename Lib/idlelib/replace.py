"""Replace dialog for IDLE. Inherits SearchDialogBase for GUI.
Uses idlelib.searchengine.SearchEngine for search capability.
Defines various replace related functions like replace, replace all,
and replace+find.
"""
agiza re

kutoka tkinter agiza StringVar, TclError

kutoka idlelib.searchbase agiza SearchDialogBase
kutoka idlelib agiza searchengine


eleza replace(text):
    """Create or reuse a singleton ReplaceDialog instance.

    The singleton dialog saves user entries and preferences
    across instances.

    Args:
        text: Text widget containing the text to be searched.
    """
    root = text._root()
    engine = searchengine.get(root)
    ikiwa not hasattr(engine, "_replacedialog"):
        engine._replacedialog = ReplaceDialog(root, engine)
    dialog = engine._replacedialog
    dialog.open(text)


kundi ReplaceDialog(SearchDialogBase):
    "Dialog for finding and replacing a pattern in text."

    title = "Replace Dialog"
    icon = "Replace"

    eleza __init__(self, root, engine):
        """Create search dialog for finding and replacing text.

        Uses SearchDialogBase as the basis for the GUI and a
        searchengine instance to prepare the search.

        Attributes:
            replvar: StringVar containing 'Replace with:' value.
            replent: Entry widget for replvar.  Created in
                create_entries().
            ok: Boolean used in searchengine.search_text to indicate
                whether the search includes the selection.
        """
        super().__init__(root, engine)
        self.replvar = StringVar(root)

    eleza open(self, text):
        """Make dialog visible on top of others and ready to use.

        Also, highlight the currently selected text and set the
        search to include the current selection (self.ok).

        Args:
            text: Text widget being searched.
        """
        SearchDialogBase.open(self, text)
        try:
            first = text.index("sel.first")
        except TclError:
            first = None
        try:
            last = text.index("sel.last")
        except TclError:
            last = None
        first = first or text.index("insert")
        last = last or first
        self.show_hit(first, last)
        self.ok = True

    eleza create_entries(self):
        "Create base and additional label and text entry widgets."
        SearchDialogBase.create_entries(self)
        self.replent = self.make_entry("Replace with:", self.replvar)[0]

    eleza create_command_buttons(self):
        """Create base and additional command buttons.

        The additional buttons are for Find, Replace,
        Replace+Find, and Replace All.
        """
        SearchDialogBase.create_command_buttons(self)
        self.make_button("Find", self.find_it)
        self.make_button("Replace", self.replace_it)
        self.make_button("Replace+Find", self.default_command, isdef=True)
        self.make_button("Replace All", self.replace_all)

    eleza find_it(self, event=None):
        "Handle the Find button."
        self.do_find(False)

    eleza replace_it(self, event=None):
        """Handle the Replace button.

        If the find is successful, then perform replace.
        """
        ikiwa self.do_find(self.ok):
            self.do_replace()

    eleza default_command(self, event=None):
        """Handle the Replace+Find button as the default command.

        First performs a replace and then, ikiwa the replace was
        successful, a find next.
        """
        ikiwa self.do_find(self.ok):
            ikiwa self.do_replace():  # Only find next match ikiwa replace succeeded.
                                   # A bad re can cause it to fail.
                self.do_find(False)

    eleza _replace_expand(self, m, repl):
        "Expand replacement text ikiwa regular expression."
        ikiwa self.engine.isre():
            try:
                new = m.expand(repl)
            except re.error:
                self.engine.report_error(repl, 'Invalid Replace Expression')
                new = None
        else:
            new = repl

        rudisha new

    eleza replace_all(self, event=None):
        """Handle the Replace All button.

        Search text for occurrences of the Find value and replace
        each of them.  The 'wrap around' value controls the start
        point for searching.  If wrap isn't set, then the searching
        starts at the first occurrence after the current selection;
        ikiwa wrap is set, the replacement starts at the first line.
        The replacement is always done top-to-bottom in the text.
        """
        prog = self.engine.getprog()
        ikiwa not prog:
            return
        repl = self.replvar.get()
        text = self.text
        res = self.engine.search_text(text, prog)
        ikiwa not res:
            self.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.tag_remove("hit", "1.0", "end")
        line = res[0]
        col = res[1].start()
        ikiwa self.engine.iswrap():
            line = 1
            col = 0
        ok = True
        first = last = None
        # XXX ought to replace circular instead of top-to-bottom when wrapping
        text.undo_block_start()
        while True:
            res = self.engine.search_forward(text, prog, line, col,
                                             wrap=False, ok=ok)
            ikiwa not res:
                break
            line, m = res
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            orig = m.group()
            new = self._replace_expand(m, repl)
            ikiwa new is None:
                break
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            ikiwa new == orig:
                text.mark_set("insert", last)
            else:
                text.mark_set("insert", first)
                ikiwa first != last:
                    text.delete(first, last)
                ikiwa new:
                    text.insert(first, new)
            col = i + len(new)
            ok = False
        text.undo_block_stop()
        ikiwa first and last:
            self.show_hit(first, last)
        self.close()

    eleza do_find(self, ok=False):
        """Search for and highlight next occurrence of pattern in text.

        No text replacement is done with this option.
        """
        ikiwa not self.engine.getprog():
            rudisha False
        text = self.text
        res = self.engine.search_text(text, None, ok)
        ikiwa not res:
            self.bell()
            rudisha False
        line, m = res
        i, j = m.span()
        first = "%d.%d" % (line, i)
        last = "%d.%d" % (line, j)
        self.show_hit(first, last)
        self.ok = True
        rudisha True

    eleza do_replace(self):
        "Replace search pattern in text with replacement value."
        prog = self.engine.getprog()
        ikiwa not prog:
            rudisha False
        text = self.text
        try:
            first = pos = text.index("sel.first")
            last = text.index("sel.last")
        except TclError:
            pos = None
        ikiwa not pos:
            first = last = pos = text.index("insert")
        line, col = searchengine.get_line_col(pos)
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        m = prog.match(chars, col)
        ikiwa not prog:
            rudisha False
        new = self._replace_expand(m, self.replvar.get())
        ikiwa new is None:
            rudisha False
        text.mark_set("insert", first)
        text.undo_block_start()
        ikiwa m.group():
            text.delete(first, last)
        ikiwa new:
            text.insert(first, new)
        text.undo_block_stop()
        self.show_hit(first, text.index("insert"))
        self.ok = False
        rudisha True

    eleza show_hit(self, first, last):
        """Highlight text between first and last indices.

        Text is highlighted via the 'hit' tag and the marked
        section is brought into view.

        The colors kutoka the 'hit' tag aren't currently shown
        when the text is displayed.  This is due to the 'sel'
        tag being added first, so the colors in the 'sel'
        config are seen instead of the colors for 'hit'.
        """
        text = self.text
        text.mark_set("insert", first)
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", first, last)
        text.tag_remove("hit", "1.0", "end")
        ikiwa first == last:
            text.tag_add("hit", first)
        else:
            text.tag_add("hit", first, last)
        text.see("insert")
        text.update_idletasks()

    eleza close(self, event=None):
        "Close the dialog and remove hit tags."
        SearchDialogBase.close(self, event)
        self.text.tag_remove("hit", "1.0", "end")


eleza _replace_dialog(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text, END, SEL
    kutoka tkinter.ttk agiza Frame, Button

    top = Toplevel(parent)
    top.title("Test ReplaceDialog")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x, y + 175))

    # mock undo delegator methods
    eleza undo_block_start():
        pass

    eleza undo_block_stop():
        pass

    frame = Frame(top)
    frame.pack()
    text = Text(frame, inactiveselectbackground='gray')
    text.undo_block_start = undo_block_start
    text.undo_block_stop = undo_block_stop
    text.pack()
    text.insert("insert","This is a sample sTring\nPlus MORE.")
    text.focus_set()

    eleza show_replace():
        text.tag_add(SEL, "1.0", END)
        replace(text)
        text.tag_remove(SEL, "1.0", END)

    button = Button(frame, text="Replace", command=show_replace)
    button.pack()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_replace', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_replace_dialog)
