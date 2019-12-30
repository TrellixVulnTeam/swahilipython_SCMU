"""TypeinViewer class.

The TypeinViewer ni what you see at the lower right of the main Pynche
widget.  It contains three text entry fields, one each kila red, green, blue.
Input into these windows ni highly constrained; it only allows you to enter
values that are legal kila a color axis.  This usually means 0-255 kila decimal
input na 0x0 - 0xff kila hex input.

You can toggle whether you want to view na input the values kwenye either decimal
or hex by clicking on Hexadecimal.  By clicking on Update wakati typing, the
color selection will be made on every change to the text field.  Otherwise,
you must hit Return ama Tab to select the color.
"""

kutoka tkinter agiza *



kundi TypeinViewer:
    eleza __init__(self, switchboard, master=Tupu):
        # non-gui ivars
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__hexp = BooleanVar()
        self.__hexp.set(optiondb.get('HEXTYPE', 0))
        self.__uwtyping = BooleanVar()
        self.__uwtyping.set(optiondb.get('UPWHILETYPE', 0))
        # create the gui
        self.__frame = Frame(master, relief=RAISED, borderwidth=1)
        self.__frame.grid(row=3, column=1, sticky='NSEW')
        # Red
        self.__xl = Label(self.__frame, text='Red:')
        self.__xl.grid(row=0, column=0, sticky=E)
        subframe = Frame(self.__frame)
        subframe.grid(row=0, column=1)
        self.__xox = Label(subframe, text='0x')
        self.__xox.grid(row=0, column=0, sticky=E)
        self.__xox['font'] = 'courier'
        self.__x = Entry(subframe, width=3)
        self.__x.grid(row=0, column=1)
        self.__x.bindtags(self.__x.bindtags() + ('Normalize', 'Update'))
        self.__x.bind_class('Normalize', '<Key>', self.__normalize)
        self.__x.bind_class('Update'   , '<Key>', self.__maybeupdate)
        # Green
        self.__yl = Label(self.__frame, text='Green:')
        self.__yl.grid(row=1, column=0, sticky=E)
        subframe = Frame(self.__frame)
        subframe.grid(row=1, column=1)
        self.__yox = Label(subframe, text='0x')
        self.__yox.grid(row=0, column=0, sticky=E)
        self.__yox['font'] = 'courier'
        self.__y = Entry(subframe, width=3)
        self.__y.grid(row=0, column=1)
        self.__y.bindtags(self.__y.bindtags() + ('Normalize', 'Update'))
        # Blue
        self.__zl = Label(self.__frame, text='Blue:')
        self.__zl.grid(row=2, column=0, sticky=E)
        subframe = Frame(self.__frame)
        subframe.grid(row=2, column=1)
        self.__zox = Label(subframe, text='0x')
        self.__zox.grid(row=0, column=0, sticky=E)
        self.__zox['font'] = 'courier'
        self.__z = Entry(subframe, width=3)
        self.__z.grid(row=0, column=1)
        self.__z.bindtags(self.__z.bindtags() + ('Normalize', 'Update'))
        # Update wakati typing?
        self.__uwt = Checkbutton(self.__frame,
                                 text='Update wakati typing',
                                 variable=self.__uwtyping)
        self.__uwt.grid(row=3, column=0, columnspan=2, sticky=W)
        # Hex/Dec
        self.__hex = Checkbutton(self.__frame,
                                 text='Hexadecimal',
                                 variable=self.__hexp,
                                 command=self.__togglehex)
        self.__hex.grid(row=4, column=0, columnspan=2, sticky=W)

    eleza __togglehex(self, event=Tupu):
        red, green, blue = self.__sb.current_rgb()
        ikiwa self.__hexp.get():
            label = '0x'
        isipokua:
            label = '  '
        self.__xox['text'] = label
        self.__yox['text'] = label
        self.__zox['text'] = label
        self.update_yourself(red, green, blue)

    eleza __normalize(self, event=Tupu):
        ew = event.widget
        contents = ew.get()
        icursor = ew.index(INSERT)
        ikiwa contents na contents[0] kwenye 'xX' na self.__hexp.get():
            contents = '0' + contents
        # Figure out the contents kwenye the current base.
        jaribu:
            ikiwa self.__hexp.get():
                v = int(contents, 16)
            isipokua:
                v = int(contents)
        tatizo ValueError:
            v = Tupu
        # If value ni sio legal, ama empty, delete the last character inserted
        # na ring the bell.  Don't ring the bell ikiwa the field ni empty (it'll
        # just equal zero.
        ikiwa v ni Tupu:
            pita
        lasivyo v < 0 ama v > 255:
            i = ew.index(INSERT)
            ikiwa event.char:
                contents = contents[:i-1] + contents[i:]
                icursor -= 1
            ew.bell()
        lasivyo self.__hexp.get():
            contents = hex(v)[2:]
        isipokua:
            contents = int(v)
        ew.delete(0, END)
        ew.insert(0, contents)
        ew.icursor(icursor)

    eleza __maybeupdate(self, event=Tupu):
        ikiwa self.__uwtyping.get() ama event.keysym kwenye ('Return', 'Tab'):
            self.__update(event)

    eleza __update(self, event=Tupu):
        redstr = self.__x.get() ama '0'
        greenstr = self.__y.get() ama '0'
        bluestr = self.__z.get() ama '0'
        ikiwa self.__hexp.get():
            base = 16
        isipokua:
            base = 10
        red, green, blue = [int(x, base) kila x kwenye (redstr, greenstr, bluestr)]
        self.__sb.update_views(red, green, blue)

    eleza update_yourself(self, red, green, blue):
        ikiwa self.__hexp.get():
            sred, sgreen, sblue = [hex(x)[2:] kila x kwenye (red, green, blue)]
        isipokua:
            sred, sgreen, sblue = red, green, blue
        x, y, z = self.__x, self.__y, self.__z
        xicursor = x.index(INSERT)
        yicursor = y.index(INSERT)
        zicursor = z.index(INSERT)
        x.delete(0, END)
        y.delete(0, END)
        z.delete(0, END)
        x.insert(0, sred)
        y.insert(0, sgreen)
        z.insert(0, sblue)
        x.icursor(xicursor)
        y.icursor(yicursor)
        z.icursor(zicursor)

    eleza hexp_var(self):
        rudisha self.__hexp

    eleza save_options(self, optiondb):
        optiondb['HEXTYPE'] = self.__hexp.get()
        optiondb['UPWHILETYPE'] = self.__uwtyping.get()
