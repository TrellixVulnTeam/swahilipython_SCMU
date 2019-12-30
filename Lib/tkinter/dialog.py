# dialog.py -- Tkinter interface to the tk_dialog script.

kutoka tkinter agiza *
kutoka tkinter agiza _cnfmerge

DIALOG_ICON = 'questhead'


kundi Dialog(Widget):
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        cnf = _cnfmerge((cnf, kw))
        self.widgetName = '__dialog__'
        Widget._setup(self, master, cnf)
        self.num = self.tk.getint(
                self.tk.call(
                      'tk_dialog', self._w,
                      cnf['title'], cnf['text'],
                      cnf['bitmap'], cnf['default'],
                      *cnf['strings']))
        jaribu: Widget.destroy(self)
        tatizo TclError: pita

    eleza destroy(self): pita


eleza _test():
    d = Dialog(Tupu, {'title': 'File Modified',
                      'text':
                      'File "Python.h" has been modified'
                      ' since the last time it was saved.'
                      ' Do you want to save it before'
                      ' exiting the application.',
                      'bitmap': DIALOG_ICON,
                      'default': 0,
                      'strings': ('Save File',
                                  'Discard Changes',
                                  'Return to Editor')})
    andika(d.num)


ikiwa __name__ == '__main__':
    t = Button(Tupu, {'text': 'Test',
                      'command': _test,
                      Pack: {}})
    q = Button(Tupu, {'text': 'Quit',
                      'command': t.quit,
                      Pack: {}})
    t.mainloop()
