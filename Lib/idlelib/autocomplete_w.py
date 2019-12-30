"""
An auto-completion window kila IDLE, used by the autocomplete extension
"""
agiza platform

kutoka tkinter agiza *
kutoka tkinter.ttk agiza Frame, Scrollbar

kutoka idlelib.autocomplete agiza FILES, ATTRS
kutoka idlelib.multicall agiza MC_SHIFT

HIDE_VIRTUAL_EVENT_NAME = "<<autocompletewindow-hide>>"
HIDE_FOCUS_OUT_SEQUENCE = "<FocusOut>"
HIDE_SEQUENCES = (HIDE_FOCUS_OUT_SEQUENCE, "<ButtonPress>")
KEYPRESS_VIRTUAL_EVENT_NAME = "<<autocompletewindow-keypress>>"
# We need to bind event beyond <Key> so that the function will be called
# before the default specific IDLE function
KEYPRESS_SEQUENCES = ("<Key>", "<Key-BackSpace>", "<Key-Return>", "<Key-Tab>",
                      "<Key-Up>", "<Key-Down>", "<Key-Home>", "<Key-End>",
                      "<Key-Prior>", "<Key-Next>")
KEYRELEASE_VIRTUAL_EVENT_NAME = "<<autocompletewindow-keyrelease>>"
KEYRELEASE_SEQUENCE = "<KeyRelease>"
LISTUPDATE_SEQUENCE = "<B1-ButtonRelease>"
WINCONFIG_SEQUENCE = "<Configure>"
DOUBLECLICK_SEQUENCE = "<B1-Double-ButtonRelease>"

kundi AutoCompleteWindow:

    eleza __init__(self, widget):
        # The widget (Text) on which we place the AutoCompleteWindow
        self.widget = widget
        # The widgets we create
        self.autocompletewindow = self.listbox = self.scrollbar = Tupu
        # The default foreground na background of a selection. Saved because
        # they are changed to the regular colors of list items when the
        # completion start ni sio a prefix of the selected completion
        self.origselforeground = self.origselbackground = Tupu
        # The list of completions
        self.completions = Tupu
        # A list ukijumuisha more completions, ama Tupu
        self.morecompletions = Tupu
        # The completion mode, either autocomplete.ATTRS ama .FILES.
        self.mode = Tupu
        # The current completion start, on the text box (a string)
        self.start = Tupu
        # The index of the start of the completion
        self.startindex = Tupu
        # The last typed start, used so that when the selection changes,
        # the new start will be as close as possible to the last typed one.
        self.lasttypedstart = Tupu
        # Do we have an indication that the user wants the completion window
        # (kila example, he clicked the list)
        self.userwantswindow = Tupu
        # event ids
        self.hideid = self.keypressid = self.listupdateid = \
            self.winconfigid = self.keyreleaseid = self.doubleclickid = Tupu
        # Flag set ikiwa last keypress was a tab
        self.lastkey_was_tab = Uongo
        # Flag set to avoid recursive <Configure> callback invocations.
        self.is_configuring = Uongo

    eleza _change_start(self, newstart):
        min_len = min(len(self.start), len(newstart))
        i = 0
        wakati i < min_len na self.start[i] == newstart[i]:
            i += 1
        ikiwa i < len(self.start):
            self.widget.delete("%s+%dc" % (self.startindex, i),
                               "%s+%dc" % (self.startindex, len(self.start)))
        ikiwa i < len(newstart):
            self.widget.insert("%s+%dc" % (self.startindex, i),
                               newstart[i:])
        self.start = newstart

    eleza _binary_search(self, s):
        """Find the first index kwenye self.completions where completions[i] is
        greater ama equal to s, ama the last index ikiwa there ni no such.
        """
        i = 0; j = len(self.completions)
        wakati j > i:
            m = (i + j) // 2
            ikiwa self.completions[m] >= s:
                j = m
            isipokua:
                i = m + 1
        rudisha min(i, len(self.completions)-1)

    eleza _complete_string(self, s):
        """Assuming that s ni the prefix of a string kwenye self.completions,
        rudisha the longest string which ni a prefix of all the strings which
        s ni a prefix of them. If s ni sio a prefix of a string, rudisha s.
        """
        first = self._binary_search(s)
        ikiwa self.completions[first][:len(s)] != s:
            # There ni sio even one completion which s ni a prefix of.
            rudisha s
        # Find the end of the range of completions where s ni a prefix of.
        i = first + 1
        j = len(self.completions)
        wakati j > i:
            m = (i + j) // 2
            ikiwa self.completions[m][:len(s)] != s:
                j = m
            isipokua:
                i = m + 1
        last = i-1

        ikiwa first == last: # only one possible completion
            rudisha self.completions[first]

        # We should rudisha the maximum prefix of first na last
        first_comp = self.completions[first]
        last_comp = self.completions[last]
        min_len = min(len(first_comp), len(last_comp))
        i = len(s)
        wakati i < min_len na first_comp[i] == last_comp[i]:
            i += 1
        rudisha first_comp[:i]

    eleza _selection_changed(self):
        """Call when the selection of the Listbox has changed.

        Updates the Listbox display na calls _change_start.
        """
        cursel = int(self.listbox.curselection()[0])

        self.listbox.see(cursel)

        lts = self.lasttypedstart
        selstart = self.completions[cursel]
        ikiwa self._binary_search(lts) == cursel:
            newstart = lts
        isipokua:
            min_len = min(len(lts), len(selstart))
            i = 0
            wakati i < min_len na lts[i] == selstart[i]:
                i += 1
            newstart = selstart[:i]
        self._change_start(newstart)

        ikiwa self.completions[cursel][:len(self.start)] == self.start:
            # start ni a prefix of the selected completion
            self.listbox.configure(selectbackground=self.origselbackground,
                                   selectforeground=self.origselforeground)
        isipokua:
            self.listbox.configure(selectbackground=self.listbox.cget("bg"),
                                   selectforeground=self.listbox.cget("fg"))
            # If there are more completions, show them, na call me again.
            ikiwa self.morecompletions:
                self.completions = self.morecompletions
                self.morecompletions = Tupu
                self.listbox.delete(0, END)
                kila item kwenye self.completions:
                    self.listbox.insert(END, item)
                self.listbox.select_set(self._binary_search(self.start))
                self._selection_changed()

    eleza show_window(self, comp_lists, index, complete, mode, userWantsWin):
        """Show the autocomplete list, bind events.

        If complete ni Kweli, complete the text, na ikiwa there ni exactly
        one matching completion, don't open a list.
        """
        # Handle the start we already have
        self.completions, self.morecompletions = comp_lists
        self.mode = mode
        self.startindex = self.widget.index(index)
        self.start = self.widget.get(self.startindex, "insert")
        ikiwa complete:
            completed = self._complete_string(self.start)
            start = self.start
            self._change_start(completed)
            i = self._binary_search(completed)
            ikiwa self.completions[i] == completed na \
               (i == len(self.completions)-1 or
                self.completions[i+1][:len(completed)] != completed):
                # There ni exactly one matching completion
                rudisha completed == start
        self.userwantswindow = userWantsWin
        self.lasttypedstart = self.start

        # Put widgets kwenye place
        self.autocompletewindow = acw = Toplevel(self.widget)
        # Put it kwenye a position so that it ni sio seen.
        acw.wm_geometry("+10000+10000")
        # Make it float
        acw.wm_overrideredirect(1)
        jaribu:
            # This command ni only needed na available on Tk >= 8.4.0 kila OSX
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            acw.tk.call("::tk::unsupported::MacWindowStyle", "style", acw._w,
                        "help", "noActivates")
        except TclError:
            pass
        self.scrollbar = scrollbar = Scrollbar(acw, orient=VERTICAL)
        self.listbox = listbox = Listbox(acw, yscrollcommand=scrollbar.set,
                                         exportselection=Uongo)
        kila item kwenye self.completions:
            listbox.insert(END, item)
        self.origselforeground = listbox.cget("selectforeground")
        self.origselbackground = listbox.cget("selectbackground")
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=Kweli)
        acw.lift()  # work around bug kwenye Tk 8.5.18+ (issue #24570)

        # Initialize the listbox selection
        self.listbox.select_set(self._binary_search(self.start))
        self._selection_changed()

        # bind events
        self.hideaid = acw.bind(HIDE_VIRTUAL_EVENT_NAME, self.hide_event)
        self.hidewid = self.widget.bind(HIDE_VIRTUAL_EVENT_NAME, self.hide_event)
        acw.event_add(HIDE_VIRTUAL_EVENT_NAME, HIDE_FOCUS_OUT_SEQUENCE)
        kila seq kwenye HIDE_SEQUENCES:
            self.widget.event_add(HIDE_VIRTUAL_EVENT_NAME, seq)

        self.keypressid = self.widget.bind(KEYPRESS_VIRTUAL_EVENT_NAME,
                                           self.keypress_event)
        kila seq kwenye KEYPRESS_SEQUENCES:
            self.widget.event_add(KEYPRESS_VIRTUAL_EVENT_NAME, seq)
        self.keyreleaseid = self.widget.bind(KEYRELEASE_VIRTUAL_EVENT_NAME,
                                             self.keyrelease_event)
        self.widget.event_add(KEYRELEASE_VIRTUAL_EVENT_NAME,KEYRELEASE_SEQUENCE)
        self.listupdateid = listbox.bind(LISTUPDATE_SEQUENCE,
                                         self.listselect_event)
        self.is_configuring = Uongo
        self.winconfigid = acw.bind(WINCONFIG_SEQUENCE, self.winconfig_event)
        self.doubleclickid = listbox.bind(DOUBLECLICK_SEQUENCE,
                                          self.doubleclick_event)
        rudisha Tupu

    eleza winconfig_event(self, event):
        ikiwa self.is_configuring:
            # Avoid running on recursive <Configure> callback invocations.
            return

        self.is_configuring = Kweli
        ikiwa sio self.is_active():
            return
        # Position the completion list window
        text = self.widget
        text.see(self.startindex)
        x, y, cx, cy = text.bbox(self.startindex)
        acw = self.autocompletewindow
        acw.update()
        acw_width, acw_height = acw.winfo_width(), acw.winfo_height()
        text_width, text_height = text.winfo_width(), text.winfo_height()
        new_x = text.winfo_rootx() + min(x, max(0, text_width - acw_width))
        new_y = text.winfo_rooty() + y
        ikiwa (text_height - (y + cy) >= acw_height # enough height below
            ama y < acw_height): # sio enough height above
            # place acw below current line
            new_y += cy
        isipokua:
            # place acw above current line
            new_y -= acw_height
        acw.wm_geometry("+%d+%d" % (new_x, new_y))

        ikiwa platform.system().startswith('Windows'):
            # See issue 15786. When on Windows platform, Tk will misbehave
            # to call winconfig_event multiple times, we need to prevent this,
            # otherwise mouse button double click will sio be able to used.
            acw.unbind(WINCONFIG_SEQUENCE, self.winconfigid)
            self.winconfigid = Tupu

        self.is_configuring = Uongo

    eleza _hide_event_check(self):
        ikiwa sio self.autocompletewindow:
            return

        jaribu:
            ikiwa sio self.autocompletewindow.focus_get():
                self.hide_window()
        except KeyError:
            # See issue 734176, when user click on menu, acw.focus_get()
            # will get KeyError.
            self.hide_window()

    eleza hide_event(self, event):
        # Hide autocomplete list ikiwa it exists na does sio have focus or
        # mouse click on widget / text area.
        ikiwa self.is_active():
            ikiwa event.type == EventType.FocusOut:
                # On Windows platform, it will need to delay the check for
                # acw.focus_get() when click on acw, otherwise it will return
                # Tupu na close the window
                self.widget.after(1, self._hide_event_check)
            elikiwa event.type == EventType.ButtonPress:
                # ButtonPress event only bind to self.widget
                self.hide_window()

    eleza listselect_event(self, event):
        ikiwa self.is_active():
            self.userwantswindow = Kweli
            cursel = int(self.listbox.curselection()[0])
            self._change_start(self.completions[cursel])

    eleza doubleclick_event(self, event):
        # Put the selected completion kwenye the text, na close the list
        cursel = int(self.listbox.curselection()[0])
        self._change_start(self.completions[cursel])
        self.hide_window()

    eleza keypress_event(self, event):
        ikiwa sio self.is_active():
            rudisha Tupu
        keysym = event.keysym
        ikiwa hasattr(event, "mc_state"):
            state = event.mc_state
        isipokua:
            state = 0
        ikiwa keysym != "Tab":
            self.lastkey_was_tab = Uongo
        ikiwa (len(keysym) == 1 ama keysym kwenye ("underscore", "BackSpace")
            ama (self.mode == FILES na keysym in
                ("period", "minus"))) \
           na sio (state & ~MC_SHIFT):
            # Normal editing of text
            ikiwa len(keysym) == 1:
                self._change_start(self.start + keysym)
            elikiwa keysym == "underscore":
                self._change_start(self.start + '_')
            elikiwa keysym == "period":
                self._change_start(self.start + '.')
            elikiwa keysym == "minus":
                self._change_start(self.start + '-')
            isipokua:
                # keysym == "BackSpace"
                ikiwa len(self.start) == 0:
                    self.hide_window()
                    rudisha Tupu
                self._change_start(self.start[:-1])
            self.lasttypedstart = self.start
            self.listbox.select_clear(0, int(self.listbox.curselection()[0]))
            self.listbox.select_set(self._binary_search(self.start))
            self._selection_changed()
            rudisha "koma"

        elikiwa keysym == "Return":
            self.complete()
            self.hide_window()
            rudisha 'koma'

        elikiwa (self.mode == ATTRS na keysym in
              ("period", "space", "parenleft", "parenright", "bracketleft",
               "bracketright")) ama \
             (self.mode == FILES na keysym in
              ("slash", "backslash", "quotedbl", "apostrophe")) \
             na sio (state & ~MC_SHIFT):
            # If start ni a prefix of the selection, but ni sio '' when
            # completing file names, put the whole
            # selected completion. Anyway, close the list.
            cursel = int(self.listbox.curselection()[0])
            ikiwa self.completions[cursel][:len(self.start)] == self.start \
               na (self.mode == ATTRS ama self.start):
                self._change_start(self.completions[cursel])
            self.hide_window()
            rudisha Tupu

        elikiwa keysym kwenye ("Home", "End", "Prior", "Next", "Up", "Down") na \
             sio state:
            # Move the selection kwenye the listbox
            self.userwantswindow = Kweli
            cursel = int(self.listbox.curselection()[0])
            ikiwa keysym == "Home":
                newsel = 0
            elikiwa keysym == "End":
                newsel = len(self.completions)-1
            elikiwa keysym kwenye ("Prior", "Next"):
                jump = self.listbox.nearest(self.listbox.winfo_height()) - \
                       self.listbox.nearest(0)
                ikiwa keysym == "Prior":
                    newsel = max(0, cursel-jump)
                isipokua:
                    assert keysym == "Next"
                    newsel = min(len(self.completions)-1, cursel+jump)
            elikiwa keysym == "Up":
                newsel = max(0, cursel-1)
            isipokua:
                assert keysym == "Down"
                newsel = min(len(self.completions)-1, cursel+1)
            self.listbox.select_clear(cursel)
            self.listbox.select_set(newsel)
            self._selection_changed()
            self._change_start(self.completions[newsel])
            rudisha "koma"

        elikiwa (keysym == "Tab" na sio state):
            ikiwa self.lastkey_was_tab:
                # two tabs kwenye a row; insert current selection na close acw
                cursel = int(self.listbox.curselection()[0])
                self._change_start(self.completions[cursel])
                self.hide_window()
                rudisha "koma"
            isipokua:
                # first tab; let AutoComplete handle the completion
                self.userwantswindow = Kweli
                self.lastkey_was_tab = Kweli
                rudisha Tupu

        elikiwa any(s kwenye keysym kila s kwenye ("Shift", "Control", "Alt",
                                       "Meta", "Command", "Option")):
            # A modifier key, so ignore
            rudisha Tupu

        elikiwa event.char na event.char >= ' ':
            # Regular character ukijumuisha a non-length-1 keycode
            self._change_start(self.start + event.char)
            self.lasttypedstart = self.start
            self.listbox.select_clear(0, int(self.listbox.curselection()[0]))
            self.listbox.select_set(self._binary_search(self.start))
            self._selection_changed()
            rudisha "koma"

        isipokua:
            # Unknown event, close the window na let it through.
            self.hide_window()
            rudisha Tupu

    eleza keyrelease_event(self, event):
        ikiwa sio self.is_active():
            return
        ikiwa self.widget.index("insert") != \
           self.widget.index("%s+%dc" % (self.startindex, len(self.start))):
            # If we didn't catch an event which moved the insert, close window
            self.hide_window()

    eleza is_active(self):
        rudisha self.autocompletewindow ni sio Tupu

    eleza complete(self):
        self._change_start(self._complete_string(self.start))
        # The selection doesn't change.

    eleza hide_window(self):
        ikiwa sio self.is_active():
            return

        # unbind events
        self.autocompletewindow.event_delete(HIDE_VIRTUAL_EVENT_NAME,
                                             HIDE_FOCUS_OUT_SEQUENCE)
        kila seq kwenye HIDE_SEQUENCES:
            self.widget.event_delete(HIDE_VIRTUAL_EVENT_NAME, seq)

        self.autocompletewindow.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hideaid)
        self.widget.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hidewid)
        self.hideaid = Tupu
        self.hidewid = Tupu
        kila seq kwenye KEYPRESS_SEQUENCES:
            self.widget.event_delete(KEYPRESS_VIRTUAL_EVENT_NAME, seq)
        self.widget.unbind(KEYPRESS_VIRTUAL_EVENT_NAME, self.keypressid)
        self.keypressid = Tupu
        self.widget.event_delete(KEYRELEASE_VIRTUAL_EVENT_NAME,
                                 KEYRELEASE_SEQUENCE)
        self.widget.unbind(KEYRELEASE_VIRTUAL_EVENT_NAME, self.keyreleaseid)
        self.keyreleaseid = Tupu
        self.listbox.unbind(LISTUPDATE_SEQUENCE, self.listupdateid)
        self.listupdateid = Tupu
        ikiwa self.winconfigid:
            self.autocompletewindow.unbind(WINCONFIG_SEQUENCE, self.winconfigid)
            self.winconfigid = Tupu

        # Re-focusOn frame.text (See issue #15786)
        self.widget.focus_set()

        # destroy widgets
        self.scrollbar.destroy()
        self.scrollbar = Tupu
        self.listbox.destroy()
        self.listbox = Tupu
        self.autocompletewindow.destroy()
        self.autocompletewindow = Tupu


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_autocomplete_w', verbosity=2, exit=Uongo)

# TODO: autocomplete/w htest here
