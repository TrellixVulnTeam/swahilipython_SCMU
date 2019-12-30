#!/usr/bin/env python3

"""Basic regular expression demonstration facility (Perl style syntax)."""

kutoka tkinter agiza *
agiza re

kundi ReDemo:

    eleza __init__(self, master):
        self.master = master

        self.promptdisplay = Label(self.master, anchor=W,
                text="Enter a Perl-style regular expression:")
        self.promptdisplay.pack(side=TOP, fill=X)

        self.regexdisplay = Entry(self.master)
        self.regexdisplay.pack(fill=X)
        self.regexdisplay.focus_set()

        self.addoptions()

        self.statusdisplay = Label(self.master, text="", anchor=W)
        self.statusdisplay.pack(side=TOP, fill=X)

        self.labeldisplay = Label(self.master, anchor=W,
                text="Enter a string to search:")
        self.labeldisplay.pack(fill=X)
        self.labeldisplay.pack(fill=X)

        self.showframe = Frame(master)
        self.showframe.pack(fill=X, anchor=W)

        self.showvar = StringVar(master)
        self.showvar.set("first")

        self.showfirstradio = Radiobutton(self.showframe,
                                         text="Highlight first match",
                                          variable=self.showvar,
                                          value="first",
                                          command=self.recompile)
        self.showfirstradio.pack(side=LEFT)

        self.showallradio = Radiobutton(self.showframe,
                                        text="Highlight all matches",
                                        variable=self.showvar,
                                        value="all",
                                        command=self.recompile)
        self.showallradio.pack(side=LEFT)

        self.stringdisplay = Text(self.master, width=60, height=4)
        self.stringdisplay.pack(fill=BOTH, expand=1)
        self.stringdisplay.tag_configure("hit", background="yellow")

        self.grouplabel = Label(self.master, text="Groups:", anchor=W)
        self.grouplabel.pack(fill=X)

        self.grouplist = Listbox(self.master)
        self.grouplist.pack(expand=1, fill=BOTH)

        self.regexdisplay.bind('<Key>', self.recompile)
        self.stringdisplay.bind('<Key>', self.reevaluate)

        self.compiled = Tupu
        self.recompile()

        btags = self.regexdisplay.bindtags()
        self.regexdisplay.bindtags(btags[1:] + btags[:1])

        btags = self.stringdisplay.bindtags()
        self.stringdisplay.bindtags(btags[1:] + btags[:1])

    eleza addoptions(self):
        self.frames = []
        self.boxes = []
        self.vars = []
        kila name kwenye ('IGNORECASE',
                     'MULTILINE',
                     'DOTALL',
                     'VERBOSE'):
            ikiwa len(self.boxes) % 3 == 0:
                frame = Frame(self.master)
                frame.pack(fill=X)
                self.frames.append(frame)
            val = getattr(re, name).value
            var = IntVar()
            box = Checkbutton(frame,
                    variable=var, text=name,
                    offvalue=0, onvalue=val,
                    command=self.recompile)
            box.pack(side=LEFT)
            self.boxes.append(box)
            self.vars.append(var)

    eleza getflags(self):
        flags = 0
        kila var kwenye self.vars:
            flags = flags | var.get()
        rudisha flags

    eleza recompile(self, event=Tupu):
        jaribu:
            self.compiled = re.compile(self.regexdisplay.get(),
                                       self.getflags())
            bg = self.promptdisplay['background']
            self.statusdisplay.config(text="", background=bg)
        tatizo re.error kama msg:
            self.compiled = Tupu
            self.statusdisplay.config(
                    text="re.error: %s" % str(msg),
                    background="red")
        self.reevaluate()

    eleza reevaluate(self, event=Tupu):
        jaribu:
            self.stringdisplay.tag_remove("hit", "1.0", END)
        tatizo TclError:
            pita
        jaribu:
            self.stringdisplay.tag_remove("hit0", "1.0", END)
        tatizo TclError:
            pita
        self.grouplist.delete(0, END)
        ikiwa sio self.compiled:
            rudisha
        self.stringdisplay.tag_configure("hit", background="yellow")
        self.stringdisplay.tag_configure("hit0", background="orange")
        text = self.stringdisplay.get("1.0", END)
        last = 0
        nmatches = 0
        wakati last <= len(text):
            m = self.compiled.search(text, last)
            ikiwa m ni Tupu:
                koma
            first, last = m.span()
            ikiwa last == first:
                last = first+1
                tag = "hit0"
            isipokua:
                tag = "hit"
            pfirst = "1.0 + %d chars" % first
            plast = "1.0 + %d chars" % last
            self.stringdisplay.tag_add(tag, pfirst, plast)
            ikiwa nmatches == 0:
                self.stringdisplay.yview_pickplace(pfirst)
                groups = list(m.groups())
                groups.insert(0, m.group())
                kila i kwenye range(len(groups)):
                    g = "%2d: %r" % (i, groups[i])
                    self.grouplist.insert(END, g)
            nmatches = nmatches + 1
            ikiwa self.showvar.get() == "first":
                koma

        ikiwa nmatches == 0:
            self.statusdisplay.config(text="(no match)",
                                      background="yellow")
        isipokua:
            self.statusdisplay.config(text="")


# Main function, run when invoked kama a stand-alone Python program.

eleza main():
    root = Tk()
    demo = ReDemo(root)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()

ikiwa __name__ == '__main__':
    main()
