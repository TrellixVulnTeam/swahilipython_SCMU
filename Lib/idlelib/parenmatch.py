"""ParenMatch -- kila parenthesis matching.

When you hit a right paren, the cursor should move briefly to the left
paren.  Paren here ni used generically; the matching applies to
parentheses, square brackets, na curly braces.
"""
kutoka idlelib.hyperparser agiza HyperParser
kutoka idlelib.config agiza idleConf

_openers = {')':'(',']':'[','}':'{'}
CHECK_DELAY = 100 # milliseconds

kundi ParenMatch:
    """Highlight matching openers na closers, (), [], na {}.

    There are three supported styles of paren matching.  When a right
    paren (opener) ni typed:

    opener -- highlight the matching left paren (closer);
    parens -- highlight the left na right parens (opener na closer);
    expression -- highlight the entire expression kutoka opener to closer.
    (For back compatibility, 'default' ni a synonym kila 'opener').

    Flash-delay ni the maximum milliseconds the highlighting remains.
    Any cursor movement (key press ama click) before that removes the
    highlight.  If flash-delay ni 0, there ni no maximum.

    TODO:
    - Augment bell() with mismatch warning kwenye status window.
    - Highlight when cursor ni moved to the right of a closer.
      This might be too expensive to check.
    """

    RESTORE_VIRTUAL_EVENT_NAME = "<<parenmatch-check-restore>>"
    # We want the restore event be called before the usual rudisha and
    # backspace events.
    RESTORE_SEQUENCES = ("<KeyPress>", "<ButtonPress>",
                         "<Key-Return>", "<Key-BackSpace>")

    eleza __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        # Bind the check-restore event to the function restore_event,
        # so that we can then use activate_restore (which calls event_add)
        # na deactivate_restore (which calls event_delete).
        editwin.text.bind(self.RESTORE_VIRTUAL_EVENT_NAME,
                          self.restore_event)
        self.counter = 0
        self.is_restore_active = 0

    @classmethod
    eleza reload(cls):
        cls.STYLE = idleConf.GetOption(
            'extensions','ParenMatch','style', default='opener')
        cls.FLASH_DELAY = idleConf.GetOption(
                'extensions','ParenMatch','flash-delay', type='int',default=500)
        cls.BELL = idleConf.GetOption(
                'extensions','ParenMatch','bell', type='bool', default=1)
        cls.HILITE_CONFIG = idleConf.GetHighlight(idleConf.CurrentTheme(),
                                                  'hilite')

    eleza activate_restore(self):
        "Activate mechanism to restore text kutoka highlighting."
        ikiwa sio self.is_restore_active:
            kila seq kwenye self.RESTORE_SEQUENCES:
                self.text.event_add(self.RESTORE_VIRTUAL_EVENT_NAME, seq)
            self.is_restore_active = Kweli

    eleza deactivate_restore(self):
        "Remove restore event bindings."
        ikiwa self.is_restore_active:
            kila seq kwenye self.RESTORE_SEQUENCES:
                self.text.event_delete(self.RESTORE_VIRTUAL_EVENT_NAME, seq)
            self.is_restore_active = Uongo

    eleza flash_paren_event(self, event):
        "Handle editor 'show surrounding parens' event (menu ama shortcut)."
        indices = (HyperParser(self.editwin, "insert")
                   .get_surrounding_brackets())
        self.finish_paren_event(indices)
        rudisha "koma"

    eleza paren_closed_event(self, event):
        "Handle user input of closer."
        # If user bound non-closer to <<paren-closed>>, quit.
        closer = self.text.get("insert-1c")
        ikiwa closer haiko kwenye _openers:
            rudisha
        hp = HyperParser(self.editwin, "insert-1c")
        ikiwa sio hp.is_in_code():
            rudisha
        indices = hp.get_surrounding_brackets(_openers[closer], Kweli)
        self.finish_paren_event(indices)
        rudisha  # Allow calltips to see ')'

    eleza finish_paren_event(self, indices):
        ikiwa indices ni Tupu na self.BELL:
            self.text.bell()
            rudisha
        self.activate_restore()
        # self.create_tag(indices)
        self.tagfuncs.get(self.STYLE, self.create_tag_expression)(self, indices)
        # self.set_timeout()
        (self.set_timeout_last ikiwa self.FLASH_DELAY else
                            self.set_timeout_none)()

    eleza restore_event(self, event=Tupu):
        "Remove effect of doing match."
        self.text.tag_delete("paren")
        self.deactivate_restore()
        self.counter += 1   # disable the last timer, ikiwa there ni one.

    eleza handle_restore_timer(self, timer_count):
        ikiwa timer_count == self.counter:
            self.restore_event()

    # any one of the create_tag_XXX methods can be used depending on
    # the style

    eleza create_tag_opener(self, indices):
        """Highlight the single paren that matches"""
        self.text.tag_add("paren", indices[0])
        self.text.tag_config("paren", self.HILITE_CONFIG)

    eleza create_tag_parens(self, indices):
        """Highlight the left na right parens"""
        ikiwa self.text.get(indices[1]) kwenye (')', ']', '}'):
            rightindex = indices[1]+"+1c"
        isipokua:
            rightindex = indices[1]
        self.text.tag_add("paren", indices[0], indices[0]+"+1c", rightindex+"-1c", rightindex)
        self.text.tag_config("paren", self.HILITE_CONFIG)

    eleza create_tag_expression(self, indices):
        """Highlight the entire expression"""
        ikiwa self.text.get(indices[1]) kwenye (')', ']', '}'):
            rightindex = indices[1]+"+1c"
        isipokua:
            rightindex = indices[1]
        self.text.tag_add("paren", indices[0], rightindex)
        self.text.tag_config("paren", self.HILITE_CONFIG)

    tagfuncs = {
        'opener': create_tag_opener,
        'default': create_tag_opener,
        'parens': create_tag_parens,
        'expression': create_tag_expression,
        }

    # any one of the set_timeout_XXX methods can be used depending on
    # the style

    eleza set_timeout_none(self):
        """Highlight will remain until user input turns it off
        ama the insert has moved"""
        # After CHECK_DELAY, call a function which disables the "paren" tag
        # ikiwa the event ni kila the most recent timer na the insert has changed,
        # ama schedules another call kila itself.
        self.counter += 1
        eleza callme(callme, self=self, c=self.counter,
                   index=self.text.index("insert")):
            ikiwa index != self.text.index("insert"):
                self.handle_restore_timer(c)
            isipokua:
                self.editwin.text_frame.after(CHECK_DELAY, callme, callme)
        self.editwin.text_frame.after(CHECK_DELAY, callme, callme)

    eleza set_timeout_last(self):
        """The last highlight created will be removed after FLASH_DELAY millisecs"""
        # associate a counter with an event; only disable the "paren"
        # tag ikiwa the event ni kila the most recent timer.
        self.counter += 1
        self.editwin.text_frame.after(
            self.FLASH_DELAY,
            lambda self=self, c=self.counter: self.handle_restore_timer(c))


ParenMatch.reload()


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_parenmatch', verbosity=2)
