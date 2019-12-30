"""Replace dialog kila IDLE. Inherits SearchDialogBase kila GUI.
Uses idlelib.searchengine.SearchEngine kila search capability.
Defines various replace related functions like replace, replace all,
and replace+find.
"""
agiza re

kutoka tkinter agiza StringVar, TclError

kutoka idlelib.searchbase agiza SearchDialogBase
kutoka idlelib agiza searchengine


eleza replace(text):
    """Create ama reuse a singleton ReplaceDialog instance.

    The singleton dialog saves user entries na preferences
    across instances.

    Args:
        text: Text widget containing the text to be searched.
    """
    root = text._root()
    engine = searchengine.get(root)
    ikiwa sio hasattr(engine, "_replacedialog"):
        engine._replacedialog = ReplaceDialog(root, engine)
    dialog = engine._replacedialog
    dialog.open(text)


kundi ReplaceDialog(SearchDialogBase):
    "Dialog kila finding na replacing a pattern kwenye text."

    title = "Replace Dialog"
    icon = "Replace"

    eleza __init__(self, root, engine):
        """Create search dialog kila finding na replacing text.

        Uses SearchDialogBase kama the basis kila the GUI na a
        searchengine instance to prepare the search.

        Attributes:
            replvar: StringVar containing 'Replace with:' value.
            replent: Entry widget kila replvar.  Created in
                create_entries().
            ok: Boolean used kwenye searchengine.search_text to indicate
                whether the search includes the selection.
        """
        super().__init__(root, engine)
        self.replvar = StringVar(root)

    eleza open(self, text):
        """Make dialog visible on top of others na ready to use.

        Also, highlight the currently selected text na set the
        search to include the current selection (self.ok).

        Args:
            text: Text widget being searched.
        """
        SearchDialogBase.open(self, text)
        jaribu:
            first = text.index("sel.first")
        tatizo TclError:
            first = Tupu
        jaribu:
            last = text.index("sel.last")
        tatizo TclError:
            last = Tupu
        first = first ama text.index("insert")
        last = last ama first
        self.show_hit(first, last)
        self.ok = Kweli

    eleza create_entries(self):
        "Create base na additional label na text entry widgets."
        SearchDialogBase.create_entries(self)
        self.replent = self.make_entry("Replace with:", self.replvar)[0]

    eleza create_command_buttons(self):
        """Create base na additional command buttons.

        The additional buttons are kila Find, Replace,
        Replace+Find, na Replace All.
        """
        SearchDialogBase.create_command_buttons(self)
        self.make_button("Find", self.find_it)
        self.make_button("Replace", self.replace_it)
        self.make_button("Replace+Find", self.default_command, isdef=Kweli)
        self.make_button("Replace All", self.replace_all)

    eleza find_it(self, event=Tupu):
        "Handle the Find button."
        self.do_find(Uongo)

    eleza replace_it(self, event=Tupu):
        """Handle the Replace button.

        If the find ni successful, then perform replace.
        """
        ikiwa self.do_find(self.ok):
            self.do_replace()

    eleza default_command(self, event=Tupu):
        """Handle the Replace+Find button kama the default command.

        First performs a replace na then, ikiwa the replace was
        successful, a find next.
        """
        ikiwa self.do_find(self.ok):
            ikiwa self.do_replace():  # Only find next match ikiwa replace succeeded.
                                   # A bad re can cause it to fail.
                self.do_find(Uongo)

    eleza _replace_expand(self, m, repl):
        "Expand replacement text ikiwa regular expression."
        ikiwa self.engine.isre():
            jaribu:
                new = m.expand(repl)
            tatizo re.error:
                self.engine.report_error(repl, 'Invalid Replace Expression')
                new = Tupu
        isipokua:
            new = repl

        rudisha new

    eleza replace_all(self, event=Tupu):
        """Handle the Replace All button.

        Search text kila occurrences of the Find value na replace
        each of them.  The 'wrap around' value controls the start
        point kila searching.  If wrap isn't set, then the searching
        starts at the first occurrence after the current selection;
        ikiwa wrap ni set, the replacement starts at the first line.
        The replacement ni always done top-to-bottom kwenye the text.
        """
        prog = self.engine.getprog()
        ikiwa sio prog:
            return
        repl = self.replvar.get()
        text = self.text
        res = self.engine.search_text(text, prog)
        ikiwa sio res:
            self.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.tag_remove("hit", "1.0", "end")
        line = res[0]
        col = res[1].start()
        ikiwa self.engine.iswrap():
            line = 1
            col = 0
        ok = Kweli
        first = last = Tupu
        # XXX ought to replace circular instead of top-to-bottom when wrapping
        text.undo_block_start()
        wakati Kweli:
            res = self.engine.search_forward(text, prog, line, col,
                                             wrap=Uongo, ok=ok)
            ikiwa sio res:
                koma
            line, m = res
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            orig = m.group()
            new = self._replace_expand(m, repl)
            ikiwa new ni Tupu:
                koma
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            ikiwa new == orig:
                text.mark_set("insert", last)
            isipokua:
                text.mark_set("insert", first)
                ikiwa first != last:
                    text.delete(first, last)
                ikiwa new:
                    text.insert(first, new)
            col = i + len(new)
            ok = Uongo
        text.undo_block_stop()
        ikiwa first na last:
            self.show_hit(first, last)
        self.close()

    eleza do_find(self, ok=Uongo):
        """Search kila na highlight next occurrence of pattern kwenye text.

        No text replacement ni done ukijumuisha this option.
        """
        ikiwa sio self.engine.getprog():
            rudisha Uongo
        text = self.text
        res = self.engine.search_text(text, Tupu, ok)
        ikiwa sio res:
            self.bell()
            rudisha Uongo
        line, m = res
        i, j = m.span()
        first = "%d.%d" % (line, i)
        last = "%d.%d" % (line, j)
        self.show_hit(first, last)
        self.ok = Kweli
        rudisha Kweli

    eleza do_replace(self):
        "Replace search pattern kwenye text ukijumuisha replacement value."
        prog = self.engine.getprog()
        ikiwa sio prog:
            rudisha Uongo
        text = self.text
        jaribu:
            first = pos = text.index("sel.first")
            last = text.index("sel.last")
        tatizo TclError:
            pos = Tupu
        ikiwa sio pos:
            first = last = pos = text.index("insert")
        line, col = searchengine.get_line_col(pos)
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        m = prog.match(chars, col)
        ikiwa sio prog:
            rudisha Uongo
        new = self._replace_expand(m, self.replvar.get())
        ikiwa new ni Tupu:
            rudisha Uongo
        text.mark_set("insert", first)
        text.undo_block_start()
        ikiwa m.group():
            text.delete(first, last)
        ikiwa new:
            text.insert(first, new)
        text.undo_block_stop()
        self.show_hit(first, text.index("insert"))
        self.ok = Uongo
        rudisha Kweli

    eleza show_hit(self, first, last):
        """Highlight text between first na last indices.

        Text ni highlighted via the 'hit' tag na the marked
        section ni brought into view.

        The colors kutoka the 'hit' tag aren't currently shown
        when the text ni displayed.  This ni due to the 'sel'
        tag being added first, so the colors kwenye the 'sel'
        config are seen instead of the colors kila 'hit'.
        """
        text = self.text
        text.mark_set("insert", first)
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", first, last)
        text.tag_remove("hit", "1.0", "end")
        ikiwa first == last:
            text.tag_add("hit", first)
        isipokua:
            text.tag_add("hit", first, last)
        text.see("insert")
        text.update_idletasks()

    eleza close(self, event=Tupu):
        "Close the dialog na remove hit tags."
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
        pita

    eleza undo_block_stop():
        pita

    frame = Frame(top)
    frame.pack()
    text = Text(frame, inactiveselectbackground='gray')
    text.undo_block_start = undo_block_start
    text.undo_block_stop = undo_block_stop
    text.pack()
    text.insert("insert","This ni a sample sTring\nPlus MORE.")
    text.focus_set()

    eleza show_replace():
        text.tag_add(SEL, "1.0", END)
        replace(text)
        text.tag_remove(SEL, "1.0", END)

    button = Button(frame, text="Replace", command=show_replace)
    button.pack()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_replace', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_replace_dialog)
