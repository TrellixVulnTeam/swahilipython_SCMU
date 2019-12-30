agiza builtins
agiza keyword
agiza re
agiza time

kutoka idlelib.config agiza idleConf
kutoka idlelib.delegator agiza Delegator

DEBUG = Uongo

eleza any(name, alternates):
    "Return a named group pattern matching list of alternates."
    rudisha "(?P<%s>" % name + "|".join(alternates) + ")"

eleza make_pat():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) kila name kwenye dir(builtins)
                                        ikiwa sio name.startswith('_') na \
                                        name haiko kwenye keyword.kwlist]
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(?i:r|u|f|fr|rf|b|br|rb)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    rudisha kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])

prog = re.compile(make_pat(), re.S)
idprog = re.compile(r"\s+(\w+)", re.S)

eleza color_config(text):
    """Set color options of Text widget.

    If ColorDelegator ni used, this should be called first.
    """
    # Called kutoka htest, TextFrame, Editor, na Turtledemo.
    # Not automatic because ColorDelegator does sio know 'text'.
    theme = idleConf.CurrentTheme()
    normal_colors = idleConf.GetHighlight(theme, 'normal')
    cursor_color = idleConf.GetHighlight(theme, 'cursor')['foreground']
    select_colors = idleConf.GetHighlight(theme, 'hilite')
    text.config(
        foreground=normal_colors['foreground'],
        background=normal_colors['background'],
        insertbackground=cursor_color,
        selectforeground=select_colors['foreground'],
        selectbackground=select_colors['background'],
        inactiveselectbackground=select_colors['background'],  # new kwenye 8.5
    )


kundi ColorDelegator(Delegator):
    """Delegator kila syntax highlighting (text coloring).

    Instance variables:
        delegate: Delegator below this one kwenye the stack, meaning the
                one this one delegates to.

        Used to track state:
        after_id: Identifier kila scheduled after event, which ni a
                timer kila colorizing the text.
        allow_colorizing: Boolean toggle kila applying colorizing.
        colorizing: Boolean flag when colorizing ni kwenye process.
        stop_colorizing: Boolean flag to end an active colorizing
                process.
    """

    eleza __init__(self):
        Delegator.__init__(self)
        self.init_state()
        self.prog = prog
        self.idprog = idprog
        self.LoadTagDefs()

    eleza init_state(self):
        "Initialize variables that track colorizing state."
        self.after_id = Tupu
        self.allow_colorizing = Kweli
        self.stop_colorizing = Uongo
        self.colorizing = Uongo

    eleza setdelegate(self, delegate):
        """Set the delegate kila this instance.

        A delegate ni an instance of a Delegator kundi na each
        delegate points to the next delegator kwenye the stack.  This
        allows multiple delegators to be chained together kila a
        widget.  The bottom delegate kila a colorizer ni a Text
        widget.

        If there ni a delegate, also start the colorizing process.
        """
        ikiwa self.delegate ni sio Tupu:
            self.unbind("<<toggle-auto-coloring>>")
        Delegator.setdelegate(self, delegate)
        ikiwa delegate ni sio Tupu:
            self.config_colors()
            self.bind("<<toggle-auto-coloring>>", self.toggle_colorize_event)
            self.notify_range("1.0", "end")
        isipokua:
            # No delegate - stop any colorizing.
            self.stop_colorizing = Kweli
            self.allow_colorizing = Uongo

    eleza config_colors(self):
        "Configure text widget tags ukijumuisha colors kutoka tagdefs."
        kila tag, cnf kwenye self.tagdefs.items():
            self.tag_configure(tag, **cnf)
        self.tag_raise('sel')

    eleza LoadTagDefs(self):
        "Create dictionary of tag names to text colors."
        theme = idleConf.CurrentTheme()
        self.tagdefs = {
            "COMMENT": idleConf.GetHighlight(theme, "comment"),
            "KEYWORD": idleConf.GetHighlight(theme, "keyword"),
            "BUILTIN": idleConf.GetHighlight(theme, "builtin"),
            "STRING": idleConf.GetHighlight(theme, "string"),
            "DEFINITION": idleConf.GetHighlight(theme, "definition"),
            "SYNC": {'background':Tupu,'foreground':Tupu},
            "TODO": {'background':Tupu,'foreground':Tupu},
            "ERROR": idleConf.GetHighlight(theme, "error"),
            # The following ni used by ReplaceDialog:
            "hit": idleConf.GetHighlight(theme, "hit"),
            }

        ikiwa DEBUG: andika('tagdefs',self.tagdefs)

    eleza insert(self, index, chars, tags=Tupu):
        "Insert chars into widget at index na mark kila colorizing."
        index = self.index(index)
        self.delegate.insert(index, chars, tags)
        self.notify_range(index, index + "+%dc" % len(chars))

    eleza delete(self, index1, index2=Tupu):
        "Delete chars between indexes na mark kila colorizing."
        index1 = self.index(index1)
        self.delegate.delete(index1, index2)
        self.notify_range(index1)

    eleza notify_range(self, index1, index2=Tupu):
        "Mark text changes kila processing na restart colorizing, ikiwa active."
        self.tag_add("TODO", index1, index2)
        ikiwa self.after_id:
            ikiwa DEBUG: andika("colorizing already scheduled")
            rudisha
        ikiwa self.colorizing:
            self.stop_colorizing = Kweli
            ikiwa DEBUG: andika("stop colorizing")
        ikiwa self.allow_colorizing:
            ikiwa DEBUG: andika("schedule colorizing")
            self.after_id = self.after(1, self.recolorize)
        rudisha

    eleza close(self):
        ikiwa self.after_id:
            after_id = self.after_id
            self.after_id = Tupu
            ikiwa DEBUG: andika("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        self.allow_colorizing = Uongo
        self.stop_colorizing = Kweli

    eleza toggle_colorize_event(self, event=Tupu):
        """Toggle colorizing on na off.

        When toggling off, ikiwa colorizing ni scheduled ama ni kwenye
        process, it will be cancelled and/or stopped.

        When toggling on, colorizing will be scheduled.
        """
        ikiwa self.after_id:
            after_id = self.after_id
            self.after_id = Tupu
            ikiwa DEBUG: andika("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        ikiwa self.allow_colorizing na self.colorizing:
            ikiwa DEBUG: andika("stop colorizing")
            self.stop_colorizing = Kweli
        self.allow_colorizing = sio self.allow_colorizing
        ikiwa self.allow_colorizing na sio self.colorizing:
            self.after_id = self.after(1, self.recolorize)
        ikiwa DEBUG:
            andika("auto colorizing turned",\
                  self.allow_colorizing na "on" ama "off")
        rudisha "koma"

    eleza recolorize(self):
        """Timer event (every 1ms) to colorize text.

        Colorizing ni only attempted when the text widget exists,
        when colorizing ni toggled on, na when the colorizing
        process ni sio already running.

        After colorizing ni complete, some cleanup ni done to
        make sure that all the text has been colorized.
        """
        self.after_id = Tupu
        ikiwa sio self.delegate:
            ikiwa DEBUG: andika("no delegate")
            rudisha
        ikiwa sio self.allow_colorizing:
            ikiwa DEBUG: andika("auto colorizing ni off")
            rudisha
        ikiwa self.colorizing:
            ikiwa DEBUG: andika("already colorizing")
            rudisha
        jaribu:
            self.stop_colorizing = Uongo
            self.colorizing = Kweli
            ikiwa DEBUG: andika("colorizing...")
            t0 = time.perf_counter()
            self.recolorize_main()
            t1 = time.perf_counter()
            ikiwa DEBUG: andika("%.3f seconds" % (t1-t0))
        mwishowe:
            self.colorizing = Uongo
        ikiwa self.allow_colorizing na self.tag_nextrange("TODO", "1.0"):
            ikiwa DEBUG: andika("reschedule colorizing")
            self.after_id = self.after(1, self.recolorize)

    eleza recolorize_main(self):
        "Evaluate text na apply colorizing tags."
        next = "1.0"
        wakati Kweli:
            item = self.tag_nextrange("TODO", next)
            ikiwa sio item:
                koma
            head, tail = item
            self.tag_remove("SYNC", head, tail)
            item = self.tag_prevrange("SYNC", head)
            ikiwa item:
                head = item[1]
            isipokua:
                head = "1.0"

            chars = ""
            next = head
            lines_to_get = 1
            ok = Uongo
            wakati sio ok:
                mark = next
                next = self.index(mark + "+%d lines linestart" %
                                         lines_to_get)
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" kwenye self.tag_names(next + "-1c")
                line = self.get(mark, next)
                ##print head, "get", mark, next, "->", repr(line)
                ikiwa sio line:
                    rudisha
                kila tag kwenye self.tagdefs:
                    self.tag_remove(tag, mark, next)
                chars = chars + line
                m = self.prog.search(chars)
                wakati m:
                    kila key, value kwenye m.groupdict().items():
                        ikiwa value:
                            a, b = m.span(key)
                            self.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            ikiwa value kwenye ("def", "class"):
                                m1 = self.idprog.match(chars, b)
                                ikiwa m1:
                                    a, b = m1.span(1)
                                    self.tag_add("DEFINITION",
                                                 head + "+%dc" % a,
                                                 head + "+%dc" % b)
                    m = self.prog.search(chars, m.end())
                ikiwa "SYNC" kwenye self.tag_names(next + "-1c"):
                    head = next
                    chars = ""
                isipokua:
                    ok = Uongo
                ikiwa sio ok:
                    # We're kwenye an inconsistent state, na the call to
                    # update may tell us to stop.  It may also change
                    # the correct value kila "next" (since this ni a
                    # line.col string, sio a true mark).  So leave a
                    # crumb telling the next invocation to resume here
                    # kwenye case update tells us to leave.
                    self.tag_add("TODO", next)
                self.update()
                ikiwa self.stop_colorizing:
                    ikiwa DEBUG: andika("colorizing stopped")
                    rudisha

    eleza removecolors(self):
        "Remove all colorizing tags."
        kila tag kwenye self.tagdefs:
            self.tag_remove(tag, "1.0", "end")


eleza _color_delegator(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text
    kutoka idlelib.percolator agiza Percolator

    top = Toplevel(parent)
    top.title("Test ColorDelegator")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("700x250+%d+%d" % (x + 20, y + 175))
    source = (
        "ikiwa Kweli: int ('1') # keyword, builtin, string, comment\n"
        "lasivyo Uongo: andika(0)\n"
        "isipokua: float(Tupu)\n"
        "ikiwa iF + If + IF: 'keyword matching must respect case'\n"
        "if'': x or''  # valid string-keyword no-space combinations\n"
        "async eleza f(): await g()\n"
        "# All valid prefixes kila unicode na byte strings should be colored.\n"
        "'x', '''x''', \"x\", \"\"\"x\"\"\"\n"
        "r'x', u'x', R'x', U'x', f'x', F'x'\n"
        "fr'x', Fr'x', fR'x', FR'x', rf'x', rF'x', Rf'x', RF'x'\n"
        "b'x',B'x', br'x',Br'x',bR'x',BR'x', rb'x', rB'x',Rb'x',RB'x'\n"
        "# Invalid combinations of legal characters should be half colored.\n"
        "ur'x', ru'x', uf'x', fu'x', UR'x', ufr'x', rfu'x', xf'x', fx'x'\n"
        )
    text = Text(top, background="white")
    text.pack(expand=1, fill="both")
    text.insert("insert", source)
    text.focus_set()

    color_config(text)
    p = Percolator(text)
    d = ColorDelegator()
    p.insertfilter(d)


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_colorizer', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_color_delegator)
