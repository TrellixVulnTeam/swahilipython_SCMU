"""A ScrolledText widget feels like a text widget but also has a
vertical scroll bar on its right.  (Later, options may be added to
add a horizontal bar as well, to make the bars disappear
automatically when sio needed, to move them to the other side of the
window, etc.)

Configuration options are passed to the Text widget.
A Frame widget ni inserted between the master na the text, to hold
the Scrollbar widget.
Most methods calls are inherited kutoka the Text widget; Pack, Grid and
Place methods are redirected to the Frame widget however.
"""

__all__ = ['ScrolledText']

kutoka tkinter agiza Frame, Text, Scrollbar, Pack, Grid, Place
kutoka tkinter.constants agiza RIGHT, LEFT, Y, BOTH


kundi ScrolledText(Text):
    eleza __init__(self, master=Tupu, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=Kweli)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        kila m kwenye methods:
            ikiwa m[0] != '_' na m != 'config' na m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    eleza __str__(self):
        rudisha str(self.frame)


eleza example():
    kutoka tkinter.constants agiza END

    stext = ScrolledText(bg='white', height=10)
    stext.insert(END, __doc__)
    stext.pack(fill=BOTH, side=LEFT, expand=Kweli)
    stext.focus_set()
    stext.mainloop()


ikiwa __name__ == "__main__":
    example()
