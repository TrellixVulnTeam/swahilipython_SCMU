"""Search dialog kila Find, Find Again, na Find Selection
   functionality.

   Inherits kutoka SearchDialogBase kila GUI na uses searchengine
   to prepare search pattern.
"""
kutoka tkinter agiza TclError

kutoka idlelib agiza searchengine
kutoka idlelib.searchbase agiza SearchDialogBase

eleza _setup(text):
    """Return the new ama existing singleton SearchDialog instance.

    The singleton dialog saves user entries na preferences
    across instances.

    Args:
        text: Text widget containing the text to be searched.
    """
    root = text._root()
    engine = searchengine.get(root)
    ikiwa sio hasattr(engine, "_searchdialog"):
        engine._searchdialog = SearchDialog(root, engine)
    rudisha engine._searchdialog

eleza find(text):
    """Open the search dialog.

    Module-level function to access the singleton SearchDialog
    instance na open the dialog.  If text ni selected, it is
    used kama the search phrase; otherwise, the previous entry
    ni used.  No search ni done ukijumuisha this command.
    """
    pat = text.get("sel.first", "sel.last")
    rudisha _setup(text).open(text, pat)  # Open ni inherited kutoka SDBase.

eleza find_again(text):
    """Repeat the search kila the last pattern na preferences.

    Module-level function to access the singleton SearchDialog
    instance to search again using the user entries na preferences
    kutoka the last dialog.  If there was no prior search, open the
    search dialog; otherwise, perform the search without showing the
    dialog.
    """
    rudisha _setup(text).find_again(text)

eleza find_selection(text):
    """Search kila the selected pattern kwenye the text.

    Module-level function to access the singleton SearchDialog
    instance to search using the selected text.  With a text
    selection, perform the search without displaying the dialog.
    Without a selection, use the prior entry kama the search phrase
    na don't display the dialog.  If there has been no prior
    search, open the search dialog.
    """
    rudisha _setup(text).find_selection(text)


kundi SearchDialog(SearchDialogBase):
    "Dialog kila finding a pattern kwenye text."

    eleza create_widgets(self):
        "Create the base search dialog na add a button kila Find Next."
        SearchDialogBase.create_widgets(self)
        # TODO - why ni this here na haiko kwenye a create_command_buttons?
        self.make_button("Find Next", self.default_command, isdef=Kweli)

    eleza default_command(self, event=Tupu):
        "Handle the Find Next button kama the default command."
        ikiwa sio self.engine.getprog():
            rudisha
        self.find_again(self.text)

    eleza find_again(self, text):
        """Repeat the last search.

        If no search was previously run, open a new search dialog.  In
        this case, no search ni done.

        If a search was previously run, the search dialog won't be
        shown na the options kutoka the previous search (including the
        search pattern) will be used to find the next occurrence
        of the pattern.  Next ni relative based on direction.

        Position the window to display the located occurrence kwenye the
        text.

        Return Kweli ikiwa the search was successful na Uongo otherwise.
        """
        ikiwa sio self.engine.getpat():
            self.open(text)
            rudisha Uongo
        ikiwa sio self.engine.getprog():
            rudisha Uongo
        res = self.engine.search_text(text)
        ikiwa res:
            line, m = res
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            jaribu:
                selfirst = text.index("sel.first")
                sellast = text.index("sel.last")
                ikiwa selfirst == first na sellast == last:
                    self.bell()
                    rudisha Uongo
            tatizo TclError:
                pita
            text.tag_remove("sel", "1.0", "end")
            text.tag_add("sel", first, last)
            text.mark_set("insert", self.engine.isback() na first ama last)
            text.see("insert")
            rudisha Kweli
        isipokua:
            self.bell()
            rudisha Uongo

    eleza find_selection(self, text):
        """Search kila selected text ukijumuisha previous dialog preferences.

        Instead of using the same pattern kila searching (as Find
        Again does), this first resets the pattern to the currently
        selected text.  If the selected text isn't changed, then use
        the prior search phrase.
        """
        pat = text.get("sel.first", "sel.last")
        ikiwa pat:
            self.engine.setcookedpat(pat)
        rudisha self.find_again(text)


eleza _search_dialog(parent):  # htest #
    "Display search test box."
    kutoka tkinter agiza Toplevel, Text
    kutoka tkinter.ttk agiza Frame, Button

    top = Toplevel(parent)
    top.title("Test SearchDialog")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x, y + 175))

    frame = Frame(top)
    frame.pack()
    text = Text(frame, inactiveselectbackground='gray')
    text.pack()
    text.insert("insert","This ni a sample string.\n"*5)

    eleza show_find():
        text.tag_add('sel', '1.0', 'end')
        _setup(text).open(text)
        text.tag_remove('sel', '1.0', 'end')

    button = Button(frame, text="Search (selection ignored)", command=show_find)
    button.pack()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_search', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_search_dialog)
