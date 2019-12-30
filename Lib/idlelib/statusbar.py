kutoka tkinter agiza Frame, Label


kundi MultiStatusBar(Frame):

    eleza __init__(self, master, **kw):
        Frame.__init__(self, master, **kw)
        self.labels = {}

    eleza set_label(self, name, text='', side='left', width=0):
        ikiwa name haiko kwenye self.labels:
            label = Label(self, borderwidth=0, anchor='w')
            label.pack(side=side, pady=0, padx=4)
            self.labels[name] = label
        isipokua:
            label = self.labels[name]
        ikiwa width != 0:
            label.config(width=width)
        label.config(text=text)


eleza _multistatus_bar(parent):  # htest #
    kutoka tkinter agiza Toplevel, Frame, Text, Button
    top = Toplevel(parent)
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" %(x, y + 175))
    top.title("Test multistatus bar")
    frame = Frame(top)
    text = Text(frame, height=5, width=40)
    text.pack()
    msb = MultiStatusBar(frame)
    msb.set_label("one", "hello")
    msb.set_label("two", "world")
    msb.pack(side='bottom', fill='x')

    eleza change():
        msb.set_label("one", "foo")
        msb.set_label("two", "bar")

    button = Button(top, text="Update status", command=change)
    button.pack(side='bottom')
    frame.pack()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_statusbar', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_multistatus_bar)
