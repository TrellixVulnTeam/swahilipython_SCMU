# base kundi kila tk common dialogues
#
# this module provides a base kundi kila accessing the common
# dialogues available kwenye Tk 4.2 na newer.  use filedialog,
# colorchooser, na messagebox to access the individual
# dialogs.
#
# written by Fredrik Lundh, May 1997
#

kutoka tkinter agiza *


kundi Dialog:

    command  = Tupu

    eleza __init__(self, master=Tupu, **options):
        self.master  = master
        self.options = options
        ikiwa sio master na options.get('parent'):
            self.master = options['parent']

    eleza _fixoptions(self):
        pass # hook

    eleza _fixresult(self, widget, result):
        rudisha result # hook

    eleza show(self, **options):

        # update instance options
        kila k, v kwenye options.items():
            self.options[k] = v

        self._fixoptions()

        # we need a dummy widget to properly process the options
        # (at least as long as we use Tkinter 1.63)
        w = Frame(self.master)

        jaribu:

            s = w.tk.call(self.command, *w._options(self.options))

            s = self._fixresult(w, s)

        mwishowe:

            jaribu:
                # get rid of the widget
                w.destroy()
            tatizo:
                pass

        rudisha s
