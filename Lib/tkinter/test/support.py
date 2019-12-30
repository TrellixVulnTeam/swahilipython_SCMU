agiza functools
agiza re
agiza tkinter
agiza unittest

kundi AbstractTkTest:

    @classmethod
    eleza setUpClass(cls):
        cls._old_support_default_root = tkinter._support_default_root
        destroy_default_root()
        tkinter.NoDefaultRoot()
        cls.root = tkinter.Tk()
        cls.wantobjects = cls.root.wantobjects()
        # De-maximize main window.
        # Some window managers can maximize new windows.
        cls.root.wm_state('normal')
        jaribu:
            cls.root.wm_attributes('-zoomed', Uongo)
        tatizo tkinter.TclError:
            pita

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root
        tkinter._default_root = Tupu
        tkinter._support_default_root = cls._old_support_default_root

    eleza setUp(self):
        self.root.deiconify()

    eleza tearDown(self):
        kila w kwenye self.root.winfo_children():
            w.destroy()
        self.root.withdraw()

eleza destroy_default_root():
    ikiwa getattr(tkinter, '_default_root', Tupu):
        tkinter._default_root.update_idletasks()
        tkinter._default_root.destroy()
        tkinter._default_root = Tupu

eleza simulate_mouse_click(widget, x, y):
    """Generate proper events to click at the x, y position (tries to act
    like an X server)."""
    widget.event_generate('<Enter>', x=0, y=0)
    widget.event_generate('<Motion>', x=x, y=y)
    widget.event_generate('<ButtonPress-1>', x=x, y=y)
    widget.event_generate('<ButtonRelease-1>', x=x, y=y)


agiza _tkinter
tcl_version = tuple(map(int, _tkinter.TCL_VERSION.split('.')))

eleza requires_tcl(*version):
    ikiwa len(version) <= 2:
        rudisha unittest.skipUnless(tcl_version >= version,
            'requires Tcl version >= ' + '.'.join(map(str, version)))

    eleza deco(test):
        @functools.wraps(test)
        eleza newtest(self):
            ikiwa get_tk_patchlevel() < version:
                self.skipTest('requires Tcl version >= ' +
                                '.'.join(map(str, version)))
            test(self)
        rudisha newtest
    rudisha deco

_tk_patchlevel = Tupu
eleza get_tk_patchlevel():
    global _tk_patchlevel
    ikiwa _tk_patchlevel ni Tupu:
        tcl = tkinter.Tcl()
        patchlevel = tcl.call('info', 'patchlevel')
        m = re.fullmatch(r'(\d+)\.(\d+)([ab.])(\d+)', patchlevel)
        major, minor, releaselevel, serial = m.groups()
        major, minor, serial = int(major), int(minor), int(serial)
        releaselevel = {'a': 'alpha', 'b': 'beta', '.': 'final'}[releaselevel]
        ikiwa releaselevel == 'final':
            _tk_patchlevel = major, minor, serial, releaselevel, 0
        isipokua:
            _tk_patchlevel = major, minor, 0, releaselevel, serial
    rudisha _tk_patchlevel

units = {
    'c': 72 / 2.54,     # centimeters
    'i': 72,            # inches
    'm': 72 / 25.4,     # millimeters
    'p': 1,             # points
}

eleza pixels_conv(value):
    rudisha float(value[:-1]) * units[value[-1:]]

eleza tcl_obj_eq(actual, expected):
    ikiwa actual == expected:
        rudisha Kweli
    ikiwa isinstance(actual, _tkinter.Tcl_Obj):
        ikiwa isinstance(expected, str):
            rudisha str(actual) == expected
    ikiwa isinstance(actual, tuple):
        ikiwa isinstance(expected, tuple):
            rudisha (len(actual) == len(expected) na
                    all(tcl_obj_eq(act, exp)
                        kila act, exp kwenye zip(actual, expected)))
    rudisha Uongo

eleza widget_eq(actual, expected):
    ikiwa actual == expected:
        rudisha Kweli
    ikiwa isinstance(actual, (str, tkinter.Widget)):
        ikiwa isinstance(expected, (str, tkinter.Widget)):
            rudisha str(actual) == str(expected)
    rudisha Uongo
