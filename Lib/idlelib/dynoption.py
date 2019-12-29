"""
OptionMenu widget modified to allow dynamic menu reconfiguration
and setting of highlightthickness
"""
agiza copy

kutoka tkinter agiza OptionMenu, _setit, StringVar, Button

kundi DynOptionMenu(OptionMenu):
    """
    unlike OptionMenu, our kwargs can include highlightthickness
    """
    eleza __init__(self, master, variable, value, *values, **kwargs):
        # TODO copy value instead of whole dict
        kwargsCopy=copy.copy(kwargs)
        ikiwa 'highlightthickness' kwenye list(kwargs.keys()):
            del(kwargs['highlightthickness'])
        OptionMenu.__init__(self, master, variable, value, *values, **kwargs)
        self.config(highlightthickness=kwargsCopy.get('highlightthickness'))
        #self.menu=self['menu']
        self.variable=variable
        self.command=kwargs.get('command')

    eleza SetMenu(self,valueList,value=Tupu):
        """
        clear na reload the menu ukijumuisha a new set of options.
        valueList - list of new options
        value - initial value to set the optionmenu's menubutton to
        """
        self['menu'].delete(0,'end')
        kila item kwenye valueList:
            self['menu'].add_command(label=item,
                    command=_setit(self.variable,item,self.command))
        ikiwa value:
            self.variable.set(value)

eleza _dyn_option_menu(parent):  # htest #
    kutoka tkinter agiza Toplevel # + StringVar, Button

    top = Toplevel(parent)
    top.title("Tets dynamic option menu")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("200x100+%d+%d" % (x + 250, y + 175))
    top.focus_set()

    var = StringVar(top)
    var.set("Old option set") #Set the default value
    dyn = DynOptionMenu(top,var, "old1","old2","old3","old4")
    dyn.pack()

    eleza update():
        dyn.SetMenu(["new1","new2","new3","new4"], value="new option set")
    button = Button(top, text="Change option set", command=update)
    button.pack()

ikiwa __name__ == '__main__':
    kutoka idlelib.idle_test.htest agiza run
    run(_dyn_option_menu)
