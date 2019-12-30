"""Wrapper functions kila Tcl/Tk.

Tkinter provides classes which allow the display, positioning na
control of widgets. Toplevel widgets are Tk na Toplevel. Other
widgets are Frame, Label, Entry, Text, Canvas, Button, Radiobutton,
Checkbutton, Scale, Listbox, Scrollbar, OptionMenu, Spinbox
LabelFrame na PanedWindow.

Properties of the widgets are specified ukijumuisha keyword arguments.
Keyword arguments have the same name kama the corresponding resource
under Tk.

Widgets are positioned ukijumuisha one of the geometry managers Place, Pack
or Grid. These managers can be called ukijumuisha methods place, pack, grid
available kwenye every Widget.

Actions are bound to events by resources (e.g. keyword argument
command) ama ukijumuisha the method bind.

Example (Hello, World):
agiza tkinter
kutoka tkinter.constants agiza *
tk = tkinter.Tk()
frame = tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
frame.pack(fill=BOTH,expand=1)
label = tkinter.Label(frame, text="Hello, World")
label.pack(fill=X, expand=1)
button = tkinter.Button(frame,text="Exit",command=tk.destroy)
button.pack(side=BOTTOM)
tk.mainloop()
"""

agiza enum
agiza sys

agiza _tkinter # If this fails your Python may sio be configured kila Tk
TclError = _tkinter.TclError
kutoka tkinter.constants agiza *
agiza re


wantobjects = 1

TkVersion = float(_tkinter.TK_VERSION)
TclVersion = float(_tkinter.TCL_VERSION)

READABLE = _tkinter.READABLE
WRITABLE = _tkinter.WRITABLE
EXCEPTION = _tkinter.EXCEPTION


_magic_re = re.compile(r'([\\{}])')
_space_re = re.compile(r'([\s])', re.ASCII)


eleza _join(value):
    """Internal function."""
    rudisha ' '.join(map(_stringify, value))


eleza _stringify(value):
    """Internal function."""
    ikiwa isinstance(value, (list, tuple)):
        ikiwa len(value) == 1:
            value = _stringify(value[0])
            ikiwa _magic_re.search(value):
                value = '{%s}' % value
        isipokua:
            value = '{%s}' % _join(value)
    isipokua:
        value = str(value)
        ikiwa sio value:
            value = '{}'
        lasivyo _magic_re.search(value):
            # add '\' before special characters na spaces
            value = _magic_re.sub(r'\\\1', value)
            value = value.replace('\n', r'\n')
            value = _space_re.sub(r'\\\1', value)
            ikiwa value[0] == '"':
                value = '\\' + value
        lasivyo value[0] == '"' ama _space_re.search(value):
            value = '{%s}' % value
    rudisha value


eleza _flatten(seq):
    """Internal function."""
    res = ()
    kila item kwenye seq:
        ikiwa isinstance(item, (tuple, list)):
            res = res + _flatten(item)
        lasivyo item ni sio Tupu:
            res = res + (item,)
    rudisha res


jaribu: _flatten = _tkinter._flatten
tatizo AttributeError: pita


eleza _cnfmerge(cnfs):
    """Internal function."""
    ikiwa isinstance(cnfs, dict):
        rudisha cnfs
    lasivyo isinstance(cnfs, (type(Tupu), str)):
        rudisha cnfs
    isipokua:
        cnf = {}
        kila c kwenye _flatten(cnfs):
            jaribu:
                cnf.update(c)
            tatizo (AttributeError, TypeError) kama msg:
                andika("_cnfmerge: fallback due to:", msg)
                kila k, v kwenye c.items():
                    cnf[k] = v
        rudisha cnf


jaribu: _cnfmerge = _tkinter._cnfmerge
tatizo AttributeError: pita


eleza _splitdict(tk, v, cut_minus=Kweli, conv=Tupu):
    """Return a properly formatted dict built kutoka Tcl list pairs.

    If cut_minus ni Kweli, the supposed '-' prefix will be removed from
    keys. If conv ni specified, it ni used to convert values.

    Tcl list ni expected to contain an even number of elements.
    """
    t = tk.splitlist(v)
    ikiwa len(t) % 2:
        ashiria RuntimeError('Tcl list representing a dict ni expected '
                           'to contain an even number of elements')
    it = iter(t)
    dict = {}
    kila key, value kwenye zip(it, it):
        key = str(key)
        ikiwa cut_minus na key[0] == '-':
            key = key[1:]
        ikiwa conv:
            value = conv(value)
        dict[key] = value
    rudisha dict


kundi EventType(str, enum.Enum):
    KeyPress = '2'
    Key = KeyPress,
    KeyRelease = '3'
    ButtonPress = '4'
    Button = ButtonPress,
    ButtonRelease = '5'
    Motion = '6'
    Enter = '7'
    Leave = '8'
    FocusIn = '9'
    FocusOut = '10'
    Keymap = '11'           # undocumented
    Expose = '12'
    GraphicsExpose = '13'   # undocumented
    NoExpose = '14'         # undocumented
    Visibility = '15'
    Create = '16'
    Destroy = '17'
    Unmap = '18'
    Map = '19'
    MapRequest = '20'
    Reparent = '21'
    Configure = '22'
    ConfigureRequest = '23'
    Gravity = '24'
    ResizeRequest = '25'
    Circulate = '26'
    CirculateRequest = '27'
    Property = '28'
    SelectionClear = '29'   # undocumented
    SelectionRequest = '30' # undocumented
    Selection = '31'        # undocumented
    Colormap = '32'
    ClientMessage = '33'    # undocumented
    Mapping = '34'          # undocumented
    VirtualEvent = '35',    # undocumented
    Activate = '36',
    Deactivate = '37',
    MouseWheel = '38',

    eleza __str__(self):
        rudisha self.name


kundi Event:
    """Container kila the properties of an event.

    Instances of this type are generated ikiwa one of the following events occurs:

    KeyPress, KeyRelease - kila keyboard events
    ButtonPress, ButtonRelease, Motion, Enter, Leave, MouseWheel - kila mouse events
    Visibility, Unmap, Map, Expose, FocusIn, FocusOut, Circulate,
    Colormap, Gravity, Reparent, Property, Destroy, Activate,
    Deactivate - kila window events.

    If a callback function kila one of these events ni registered
    using bind, bind_all, bind_class, ama tag_bind, the callback is
    called ukijumuisha an Event kama first argument. It will have the
    following attributes (in braces are the event types kila which
    the attribute ni valid):

        serial - serial number of event
    num - mouse button pressed (ButtonPress, ButtonRelease)
    focus - whether the window has the focus (Enter, Leave)
    height - height of the exposed window (Configure, Expose)
    width - width of the exposed window (Configure, Expose)
    keycode - keycode of the pressed key (KeyPress, KeyRelease)
    state - state of the event kama a number (ButtonPress, ButtonRelease,
                            Enter, KeyPress, KeyRelease,
                            Leave, Motion)
    state - state kama a string (Visibility)
    time - when the event occurred
    x - x-position of the mouse
    y - y-position of the mouse
    x_root - x-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    y_root - y-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    char - pressed character (KeyPress, KeyRelease)
    send_event - see X/Windows documentation
    keysym - keysym of the event kama a string (KeyPress, KeyRelease)
    keysym_num - keysym of the event kama a number (KeyPress, KeyRelease)
    type - type of the event kama a number
    widget - widget kwenye which the event occurred
    delta - delta of wheel movement (MouseWheel)
    """

    eleza __repr__(self):
        attrs = {k: v kila k, v kwenye self.__dict__.items() ikiwa v != '??'}
        ikiwa sio self.char:
            toa attrs['char']
        lasivyo self.char != '??':
            attrs['char'] = repr(self.char)
        ikiwa sio getattr(self, 'send_event', Kweli):
            toa attrs['send_event']
        ikiwa self.state == 0:
            toa attrs['state']
        lasivyo isinstance(self.state, int):
            state = self.state
            mods = ('Shift', 'Lock', 'Control',
                    'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Mod5',
                    'Button1', 'Button2', 'Button3', 'Button4', 'Button5')
            s = []
            kila i, n kwenye enumerate(mods):
                ikiwa state & (1 << i):
                    s.append(n)
            state = state & ~((1<< len(mods)) - 1)
            ikiwa state ama sio s:
                s.append(hex(state))
            attrs['state'] = '|'.join(s)
        ikiwa self.delta == 0:
            toa attrs['delta']
        # widget usually ni known
        # serial na time are sio very interesting
        # keysym_num duplicates keysym
        # x_root na y_root mostly duplicate x na y
        keys = ('send_event',
                'state', 'keysym', 'keycode', 'char',
                'num', 'delta', 'focus',
                'x', 'y', 'width', 'height')
        rudisha '<%s event%s>' % (
            self.type,
            ''.join(' %s=%s' % (k, attrs[k]) kila k kwenye keys ikiwa k kwenye attrs)
        )


_support_default_root = 1
_default_root = Tupu


eleza NoDefaultRoot():
    """Inhibit setting of default root window.

    Call this function to inhibit that the first instance of
    Tk ni used kila windows without an explicit parent window.
    """
    global _support_default_root
    _support_default_root = 0
    global _default_root
    _default_root = Tupu
    toa _default_root


eleza _tkerror(err):
    """Internal function."""
    pita


eleza _exit(code=0):
    """Internal function. Calling it will ashiria the exception SystemExit."""
    jaribu:
        code = int(code)
    tatizo ValueError:
        pita
    ashiria SystemExit(code)


_varnum = 0


kundi Variable:
    """Class to define value holders kila e.g. buttons.

    Subclasses StringVar, IntVar, DoubleVar, BooleanVar are specializations
    that constrain the type of the value returned kutoka get()."""
    _default = ""
    _tk = Tupu
    _tclCommands = Tupu

    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        """Construct a variable

        MASTER can be given kama master widget.
        VALUE ni an optional value (defaults to "")
        NAME ni an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable na VALUE ni omitted
        then the existing value ni retained.
        """
        # check kila type of NAME parameter to override weird error message
        # raised kutoka Modules/_tkinter.c:SetVar like:
        # TypeError: setvar() takes exactly 3 arguments (2 given)
        ikiwa name ni sio Tupu na sio isinstance(name, str):
            ashiria TypeError("name must be a string")
        global _varnum
        ikiwa sio master:
            master = _default_root
        self._root = master._root()
        self._tk = master.tk
        ikiwa name:
            self._name = name
        isipokua:
            self._name = 'PY_VAR' + repr(_varnum)
            _varnum += 1
        ikiwa value ni sio Tupu:
            self.initialize(value)
        lasivyo sio self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self.initialize(self._default)

    eleza __del__(self):
        """Unset the variable kwenye Tcl."""
        ikiwa self._tk ni Tupu:
            return
        ikiwa self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self._tk.globalunsetvar(self._name)
        ikiwa self._tclCommands ni sio Tupu:
            kila name kwenye self._tclCommands:
                #print '- Tkinter: deleted command', name
                self._tk.deletecommand(name)
            self._tclCommands = Tupu

    eleza __str__(self):
        """Return the name of the variable kwenye Tcl."""
        rudisha self._name

    eleza set(self, value):
        """Set the variable to VALUE."""
        rudisha self._tk.globalsetvar(self._name, value)

    initialize = set

    eleza get(self):
        """Return value of variable."""
        rudisha self._tk.globalgetvar(self._name)

    eleza _register(self, callback):
        f = CallWrapper(callback, Tupu, self._root).__call__
        cbname = repr(id(f))
        jaribu:
            callback = callback.__func__
        tatizo AttributeError:
            pita
        jaribu:
            cbname = cbname + callback.__name__
        tatizo AttributeError:
            pita
        self._tk.createcommand(cbname, f)
        ikiwa self._tclCommands ni Tupu:
            self._tclCommands = []
        self._tclCommands.append(cbname)
        rudisha cbname

    eleza trace_add(self, mode, callback):
        """Define a trace callback kila the variable.

        Mode ni one of "read", "write", "unset", ama a list ama tuple of
        such strings.
        Callback must be a function which ni called when the variable is
        read, written ama unset.

        Return the name of the callback.
        """
        cbname = self._register(callback)
        self._tk.call('trace', 'add', 'variable',
                      self._name, mode, (cbname,))
        rudisha cbname

    eleza trace_remove(self, mode, cbname):
        """Delete the trace callback kila a variable.

        Mode ni one of "read", "write", "unset" ama a list ama tuple of
        such strings.  Must be same kama were specified kwenye trace_add().
        cbname ni the name of the callback returned kutoka trace_add().
        """
        self._tk.call('trace', 'remove', 'variable',
                      self._name, mode, cbname)
        kila m, ca kwenye self.trace_info():
            ikiwa self._tk.splitlist(ca)[0] == cbname:
                koma
        isipokua:
            self._tk.deletecommand(cbname)
            jaribu:
                self._tclCommands.remove(cbname)
            tatizo ValueError:
                pita

    eleza trace_info(self):
        """Return all trace callback information."""
        splitlist = self._tk.splitlist
        rudisha [(splitlist(k), v) kila k, v kwenye map(splitlist,
            splitlist(self._tk.call('trace', 'info', 'variable', self._name)))]

    eleza trace_variable(self, mode, callback):
        """Define a trace callback kila the variable.

        MODE ni one of "r", "w", "u" kila read, write, undefine.
        CALLBACK must be a function which ni called when
        the variable ni read, written ama undefined.

        Return the name of the callback.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed kwenye the future.  Use trace_add() instead.
        """
        # TODO: Add deprecation warning
        cbname = self._register(callback)
        self._tk.call("trace", "variable", self._name, mode, cbname)
        rudisha cbname

    trace = trace_variable

    eleza trace_vdelete(self, mode, cbname):
        """Delete the trace callback kila a variable.

        MODE ni one of "r", "w", "u" kila read, write, undefine.
        CBNAME ni the name of the callback returned kutoka trace_variable ama trace.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed kwenye the future.  Use trace_remove() instead.
        """
        # TODO: Add deprecation warning
        self._tk.call("trace", "vdelete", self._name, mode, cbname)
        cbname = self._tk.splitlist(cbname)[0]
        kila m, ca kwenye self.trace_info():
            ikiwa self._tk.splitlist(ca)[0] == cbname:
                koma
        isipokua:
            self._tk.deletecommand(cbname)
            jaribu:
                self._tclCommands.remove(cbname)
            tatizo ValueError:
                pita

    eleza trace_vinfo(self):
        """Return all trace callback information.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed kwenye the future.  Use trace_info() instead.
        """
        # TODO: Add deprecation warning
        rudisha [self._tk.splitlist(x) kila x kwenye self._tk.splitlist(
            self._tk.call("trace", "vinfo", self._name))]

    eleza __eq__(self, other):
        """Comparison kila equality (==).

        Note: ikiwa the Variable's master matters to behavior
        also compare self._master == other._master
        """
        rudisha self.__class__.__name__ == other.__class__.__name__ \
            na self._name == other._name


kundi StringVar(Variable):
    """Value holder kila strings variables."""
    _default = ""

    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        """Construct a string variable.

        MASTER can be given kama master widget.
        VALUE ni an optional value (defaults to "")
        NAME ni an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable na VALUE ni omitted
        then the existing value ni retained.
        """
        Variable.__init__(self, master, value, name)

    eleza get(self):
        """Return value of variable kama string."""
        value = self._tk.globalgetvar(self._name)
        ikiwa isinstance(value, str):
            rudisha value
        rudisha str(value)


kundi IntVar(Variable):
    """Value holder kila integer variables."""
    _default = 0

    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        """Construct an integer variable.

        MASTER can be given kama master widget.
        VALUE ni an optional value (defaults to 0)
        NAME ni an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable na VALUE ni omitted
        then the existing value ni retained.
        """
        Variable.__init__(self, master, value, name)

    eleza get(self):
        """Return the value of the variable kama an integer."""
        value = self._tk.globalgetvar(self._name)
        jaribu:
            rudisha self._tk.getint(value)
        tatizo (TypeError, TclError):
            rudisha int(self._tk.getdouble(value))


kundi DoubleVar(Variable):
    """Value holder kila float variables."""
    _default = 0.0

    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        """Construct a float variable.

        MASTER can be given kama master widget.
        VALUE ni an optional value (defaults to 0.0)
        NAME ni an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable na VALUE ni omitted
        then the existing value ni retained.
        """
        Variable.__init__(self, master, value, name)

    eleza get(self):
        """Return the value of the variable kama a float."""
        rudisha self._tk.getdouble(self._tk.globalgetvar(self._name))


kundi BooleanVar(Variable):
    """Value holder kila boolean variables."""
    _default = Uongo

    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        """Construct a boolean variable.

        MASTER can be given kama master widget.
        VALUE ni an optional value (defaults to Uongo)
        NAME ni an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable na VALUE ni omitted
        then the existing value ni retained.
        """
        Variable.__init__(self, master, value, name)

    eleza set(self, value):
        """Set the variable to VALUE."""
        rudisha self._tk.globalsetvar(self._name, self._tk.getboolean(value))

    initialize = set

    eleza get(self):
        """Return the value of the variable kama a bool."""
        jaribu:
            rudisha self._tk.getboolean(self._tk.globalgetvar(self._name))
        tatizo TclError:
            ashiria ValueError("invalid literal kila getboolean()")


eleza mainloop(n=0):
    """Run the main loop of Tcl."""
    _default_root.tk.mainloop(n)


getint = int

getdouble = float


eleza getboolean(s):
    """Convert true na false to integer values 1 na 0."""
    jaribu:
        rudisha _default_root.tk.getboolean(s)
    tatizo TclError:
        ashiria ValueError("invalid literal kila getboolean()")


# Methods defined on both toplevel na interior widgets

kundi Misc:
    """Internal class.

    Base kundi which defines methods common kila interior widgets."""

    # used kila generating child widget names
    _last_child_ids = Tupu

    # XXX font command?
    _tclCommands = Tupu

    eleza destroy(self):
        """Internal function.

        Delete all Tcl commands created for
        this widget kwenye the Tcl interpreter."""
        ikiwa self._tclCommands ni sio Tupu:
            kila name kwenye self._tclCommands:
                #print '- Tkinter: deleted command', name
                self.tk.deletecommand(name)
            self._tclCommands = Tupu

    eleza deletecommand(self, name):
        """Internal function.

        Delete the Tcl command provided kwenye NAME."""
        #print '- Tkinter: deleted command', name
        self.tk.deletecommand(name)
        jaribu:
            self._tclCommands.remove(name)
        tatizo ValueError:
            pita

    eleza tk_strictMotif(self, boolean=Tupu):
        """Set Tcl internal variable, whether the look na feel
        should adhere to Motif.

        A parameter of 1 means adhere to Motikiwa (e.g. no color
        change ikiwa mouse pitaes over slider).
        Returns the set value."""
        rudisha self.tk.getboolean(self.tk.call(
            'set', 'tk_strictMotif', boolean))

    eleza tk_bisque(self):
        """Change the color scheme to light brown kama used kwenye Tk 3.6 na before."""
        self.tk.call('tk_bisque')

    eleza tk_setPalette(self, *args, **kw):
        """Set a new color scheme kila all widget elements.

        A single color kama argument will cause that all colors of Tk
        widget elements are derived kutoka this.
        Alternatively several keyword parameters na its associated
        colors can be given. The following keywords are valid:
        activeBackground, foreground, selectColor,
        activeForeground, highlightBackground, selectBackground,
        background, highlightColor, selectForeground,
        disabledForeground, insertBackground, troughColor."""
        self.tk.call(('tk_setPalette',)
              + _flatten(args) + _flatten(list(kw.items())))

    eleza wait_variable(self, name='PY_VAR'):
        """Wait until the variable ni modified.

        A parameter of type IntVar, StringVar, DoubleVar ama
        BooleanVar must be given."""
        self.tk.call('tkwait', 'variable', name)
    waitvar = wait_variable # XXX b/w compat

    eleza wait_window(self, window=Tupu):
        """Wait until a WIDGET ni destroyed.

        If no parameter ni given self ni used."""
        ikiwa window ni Tupu:
            window = self
        self.tk.call('tkwait', 'window', window._w)

    eleza wait_visibility(self, window=Tupu):
        """Wait until the visibility of a WIDGET changes
        (e.g. it appears).

        If no parameter ni given self ni used."""
        ikiwa window ni Tupu:
            window = self
        self.tk.call('tkwait', 'visibility', window._w)

    eleza setvar(self, name='PY_VAR', value='1'):
        """Set Tcl variable NAME to VALUE."""
        self.tk.setvar(name, value)

    eleza getvar(self, name='PY_VAR'):
        """Return value of Tcl variable NAME."""
        rudisha self.tk.getvar(name)

    eleza getint(self, s):
        jaribu:
            rudisha self.tk.getint(s)
        tatizo TclError kama exc:
            ashiria ValueError(str(exc))

    eleza getdouble(self, s):
        jaribu:
            rudisha self.tk.getdouble(s)
        tatizo TclError kama exc:
            ashiria ValueError(str(exc))

    eleza getboolean(self, s):
        """Return a boolean value kila Tcl boolean values true na false given kama parameter."""
        jaribu:
            rudisha self.tk.getboolean(s)
        tatizo TclError:
            ashiria ValueError("invalid literal kila getboolean()")

    eleza focus_set(self):
        """Direct input focus to this widget.

        If the application currently does sio have the focus
        this widget will get the focus ikiwa the application gets
        the focus through the window manager."""
        self.tk.call('focus', self._w)
    focus = focus_set # XXX b/w compat?

    eleza focus_force(self):
        """Direct input focus to this widget even ikiwa the
        application does sio have the focus. Use with
        caution!"""
        self.tk.call('focus', '-force', self._w)

    eleza focus_get(self):
        """Return the widget which has currently the focus kwenye the
        application.

        Use focus_displayof to allow working ukijumuisha several
        displays. Return Tupu ikiwa application does sio have
        the focus."""
        name = self.tk.call('focus')
        ikiwa name == 'none' ama sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza focus_displayof(self):
        """Return the widget which has currently the focus on the
        display where this widget ni located.

        Return Tupu ikiwa the application does sio have the focus."""
        name = self.tk.call('focus', '-displayof', self._w)
        ikiwa name == 'none' ama sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza focus_lastfor(self):
        """Return the widget which would have the focus ikiwa top level
        kila this widget gets the focus kutoka the window manager."""
        name = self.tk.call('focus', '-lastfor', self._w)
        ikiwa name == 'none' ama sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza tk_focusFollowsMouse(self):
        """The widget under mouse will get automatically focus. Can not
        be disabled easily."""
        self.tk.call('tk_focusFollowsMouse')

    eleza tk_focusNext(self):
        """Return the next widget kwenye the focus order which follows
        widget which has currently the focus.

        The focus order first goes to the next child, then to
        the children of the child recursively na then to the
        next sibling which ni higher kwenye the stacking order.  A
        widget ni omitted ikiwa it has the takefocus resource set
        to 0."""
        name = self.tk.call('tk_focusNext', self._w)
        ikiwa sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza tk_focusPrev(self):
        """Return previous widget kwenye the focus order. See tk_focusNext kila details."""
        name = self.tk.call('tk_focusPrev', self._w)
        ikiwa sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza after(self, ms, func=Tupu, *args):
        """Call function once after given time.

        MS specifies the time kwenye milliseconds. FUNC gives the
        function which shall be called. Additional parameters
        are given kama parameters to the function call.  Return
        identifier to cancel scheduling ukijumuisha after_cancel."""
        ikiwa sio func:
            # I'd rather use time.sleep(ms*0.001)
            self.tk.call('after', ms)
            rudisha Tupu
        isipokua:
            eleza callit():
                jaribu:
                    func(*args)
                mwishowe:
                    jaribu:
                        self.deletecommand(name)
                    tatizo TclError:
                        pita
            callit.__name__ = func.__name__
            name = self._register(callit)
            rudisha self.tk.call('after', ms, name)

    eleza after_idle(self, func, *args):
        """Call FUNC once ikiwa the Tcl main loop has no event to
        process.

        Return an identifier to cancel the scheduling with
        after_cancel."""
        rudisha self.after('idle', func, *args)

    eleza after_cancel(self, id):
        """Cancel scheduling of function identified ukijumuisha ID.

        Identifier returned by after ama after_idle must be
        given kama first parameter.
        """
        ikiwa sio id:
            ashiria ValueError('id must be a valid identifier returned kutoka '
                             'after ama after_idle')
        jaribu:
            data = self.tk.call('after', 'info', id)
            script = self.tk.splitlist(data)[0]
            self.deletecommand(script)
        tatizo TclError:
            pita
        self.tk.call('after', 'cancel', id)

    eleza bell(self, displayof=0):
        """Ring a display's bell."""
        self.tk.call(('bell',) + self._displayof(displayof))

    # Clipboard handling:
    eleza clipboard_get(self, **kw):
        """Retrieve data kutoka the clipboard on window's display.

        The window keyword defaults to the root window of the Tkinter
        application.

        The type keyword specifies the form kwenye which the data is
        to be returned na should be an atom name such kama STRING
        ama FILE_NAME.  Type defaults to STRING, tatizo on X11, where the default
        ni to try UTF8_STRING na fall back to STRING.

        This command ni equivalent to:

        selection_get(CLIPBOARD)
        """
        ikiwa 'type' haiko kwenye kw na self._windowingsystem == 'x11':
            jaribu:
                kw['type'] = 'UTF8_STRING'
                rudisha self.tk.call(('clipboard', 'get') + self._options(kw))
            tatizo TclError:
                toa kw['type']
        rudisha self.tk.call(('clipboard', 'get') + self._options(kw))

    eleza clipboard_clear(self, **kw):
        """Clear the data kwenye the Tk clipboard.

        A widget specified kila the optional displayof keyword
        argument specifies the target display."""
        ikiwa 'displayof' haiko kwenye kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'clear') + self._options(kw))

    eleza clipboard_append(self, string, **kw):
        """Append STRING to the Tk clipboard.

        A widget specified at the optional displayof keyword
        argument specifies the target display. The clipboard
        can be retrieved ukijumuisha selection_get."""
        ikiwa 'displayof' haiko kwenye kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'append') + self._options(kw)
              + ('--', string))
    # XXX grab current w/o window argument

    eleza grab_current(self):
        """Return widget which has currently the grab kwenye this application
        ama Tupu."""
        name = self.tk.call('grab', 'current', self._w)
        ikiwa sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza grab_release(self):
        """Release grab kila this widget ikiwa currently set."""
        self.tk.call('grab', 'release', self._w)

    eleza grab_set(self):
        """Set grab kila this widget.

        A grab directs all events to this na descendant
        widgets kwenye the application."""
        self.tk.call('grab', 'set', self._w)

    eleza grab_set_global(self):
        """Set global grab kila this widget.

        A global grab directs all events to this na
        descendant widgets on the display. Use ukijumuisha caution -
        other applications do sio get events anymore."""
        self.tk.call('grab', 'set', '-global', self._w)

    eleza grab_status(self):
        """Return Tupu, "local" ama "global" ikiwa this widget has
        no, a local ama a global grab."""
        status = self.tk.call('grab', 'status', self._w)
        ikiwa status == 'none': status = Tupu
        rudisha status

    eleza option_add(self, pattern, value, priority = Tupu):
        """Set a VALUE (second parameter) kila an option
        PATTERN (first parameter).

        An optional third parameter gives the numeric priority
        (defaults to 80)."""
        self.tk.call('option', 'add', pattern, value, priority)

    eleza option_clear(self):
        """Clear the option database.

        It will be reloaded ikiwa option_add ni called."""
        self.tk.call('option', 'clear')

    eleza option_get(self, name, className):
        """Return the value kila an option NAME kila this widget
        ukijumuisha CLASSNAME.

        Values ukijumuisha higher priority override lower values."""
        rudisha self.tk.call('option', 'get', self._w, name, className)

    eleza option_readfile(self, fileName, priority = Tupu):
        """Read file FILENAME into the option database.

        An optional second parameter gives the numeric
        priority."""
        self.tk.call('option', 'readfile', fileName, priority)

    eleza selection_clear(self, **kw):
        """Clear the current X selection."""
        ikiwa 'displayof' haiko kwenye kw: kw['displayof'] = self._w
        self.tk.call(('selection', 'clear') + self._options(kw))

    eleza selection_get(self, **kw):
        """Return the contents of the current X selection.

        A keyword parameter selection specifies the name of
        the selection na defaults to PRIMARY.  A keyword
        parameter displayof specifies a widget on the display
        to use. A keyword parameter type specifies the form of data to be
        fetched, defaulting to STRING tatizo on X11, where UTF8_STRING ni tried
        before STRING."""
        ikiwa 'displayof' haiko kwenye kw: kw['displayof'] = self._w
        ikiwa 'type' haiko kwenye kw na self._windowingsystem == 'x11':
            jaribu:
                kw['type'] = 'UTF8_STRING'
                rudisha self.tk.call(('selection', 'get') + self._options(kw))
            tatizo TclError:
                toa kw['type']
        rudisha self.tk.call(('selection', 'get') + self._options(kw))

    eleza selection_handle(self, command, **kw):
        """Specify a function COMMAND to call ikiwa the X
        selection owned by this widget ni queried by another
        application.

        This function must rudisha the contents of the
        selection. The function will be called ukijumuisha the
        arguments OFFSET na LENGTH which allows the chunking
        of very long selections. The following keyword
        parameters can be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        name = self._register(command)
        self.tk.call(('selection', 'handle') + self._options(kw)
              + (self._w, name))

    eleza selection_own(self, **kw):
        """Become owner of X selection.

        A keyword parameter selection specifies the name of
        the selection (default PRIMARY)."""
        self.tk.call(('selection', 'own') +
                 self._options(kw) + (self._w,))

    eleza selection_own_get(self, **kw):
        """Return owner of X selection.

        The following keyword parameter can
        be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        ikiwa 'displayof' haiko kwenye kw: kw['displayof'] = self._w
        name = self.tk.call(('selection', 'own') + self._options(kw))
        ikiwa sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza send(self, interp, cmd, *args):
        """Send Tcl command CMD to different interpreter INTERP to be executed."""
        rudisha self.tk.call(('send', interp, cmd) + args)

    eleza lower(self, belowThis=Tupu):
        """Lower this widget kwenye the stacking order."""
        self.tk.call('lower', self._w, belowThis)

    eleza tkraise(self, aboveThis=Tupu):
        """Raise this widget kwenye the stacking order."""
        self.tk.call('raise', self._w, aboveThis)

    lift = tkraise

    eleza winfo_atom(self, name, displayof=0):
        """Return integer which represents atom NAME."""
        args = ('winfo', 'atom') + self._displayof(displayof) + (name,)
        rudisha self.tk.getint(self.tk.call(args))

    eleza winfo_atomname(self, id, displayof=0):
        """Return name of atom ukijumuisha identifier ID."""
        args = ('winfo', 'atomname') \
               + self._displayof(displayof) + (id,)
        rudisha self.tk.call(args)

    eleza winfo_cells(self):
        """Return number of cells kwenye the colormap kila this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'cells', self._w))

    eleza winfo_children(self):
        """Return a list of all widgets which are children of this widget."""
        result = []
        kila child kwenye self.tk.splitlist(
            self.tk.call('winfo', 'children', self._w)):
            jaribu:
                # Tcl sometimes returns extra windows, e.g. for
                # menus; those need to be skipped
                result.append(self._nametowidget(child))
            tatizo KeyError:
                pita
        rudisha result

    eleza winfo_class(self):
        """Return window kundi name of this widget."""
        rudisha self.tk.call('winfo', 'class', self._w)

    eleza winfo_colormapfull(self):
        """Return true ikiwa at the last color request the colormap was full."""
        rudisha self.tk.getboolean(
            self.tk.call('winfo', 'colormapfull', self._w))

    eleza winfo_containing(self, rootX, rootY, displayof=0):
        """Return the widget which ni at the root coordinates ROOTX, ROOTY."""
        args = ('winfo', 'containing') \
               + self._displayof(displayof) + (rootX, rootY)
        name = self.tk.call(args)
        ikiwa sio name: rudisha Tupu
        rudisha self._nametowidget(name)

    eleza winfo_depth(self):
        """Return the number of bits per pixel."""
        rudisha self.tk.getint(self.tk.call('winfo', 'depth', self._w))

    eleza winfo_exists(self):
        """Return true ikiwa this widget exists."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'exists', self._w))

    eleza winfo_fpixels(self, number):
        """Return the number of pixels kila the given distance NUMBER
        (e.g. "3c") kama float."""
        rudisha self.tk.getdouble(self.tk.call(
            'winfo', 'fpixels', self._w, number))

    eleza winfo_geometry(self):
        """Return geometry string kila this widget kwenye the form "widthxheight+X+Y"."""
        rudisha self.tk.call('winfo', 'geometry', self._w)

    eleza winfo_height(self):
        """Return height of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'height', self._w))

    eleza winfo_id(self):
        """Return identifier ID kila this widget."""
        rudisha int(self.tk.call('winfo', 'id', self._w), 0)

    eleza winfo_interps(self, displayof=0):
        """Return the name of all Tcl interpreters kila this display."""
        args = ('winfo', 'interps') + self._displayof(displayof)
        rudisha self.tk.splitlist(self.tk.call(args))

    eleza winfo_ismapped(self):
        """Return true ikiwa this widget ni mapped."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'ismapped', self._w))

    eleza winfo_manager(self):
        """Return the window manager name kila this widget."""
        rudisha self.tk.call('winfo', 'manager', self._w)

    eleza winfo_name(self):
        """Return the name of this widget."""
        rudisha self.tk.call('winfo', 'name', self._w)

    eleza winfo_parent(self):
        """Return the name of the parent of this widget."""
        rudisha self.tk.call('winfo', 'parent', self._w)

    eleza winfo_pathname(self, id, displayof=0):
        """Return the pathname of the widget given by ID."""
        args = ('winfo', 'pathname') \
               + self._displayof(displayof) + (id,)
        rudisha self.tk.call(args)

    eleza winfo_pixels(self, number):
        """Rounded integer value of winfo_fpixels."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'pixels', self._w, number))

    eleza winfo_pointerx(self):
        """Return the x coordinate of the pointer on the root window."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'pointerx', self._w))

    eleza winfo_pointerxy(self):
        """Return a tuple of x na y coordinates of the pointer on the root window."""
        rudisha self._getints(
            self.tk.call('winfo', 'pointerxy', self._w))

    eleza winfo_pointery(self):
        """Return the y coordinate of the pointer on the root window."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'pointery', self._w))

    eleza winfo_reqheight(self):
        """Return requested height of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'reqheight', self._w))

    eleza winfo_reqwidth(self):
        """Return requested width of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'reqwidth', self._w))

    eleza winfo_rgb(self, color):
        """Return tuple of decimal values kila red, green, blue for
        COLOR kwenye this widget."""
        rudisha self._getints(
            self.tk.call('winfo', 'rgb', self._w, color))

    eleza winfo_rootx(self):
        """Return x coordinate of upper left corner of this widget on the
        root window."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'rootx', self._w))

    eleza winfo_rooty(self):
        """Return y coordinate of upper left corner of this widget on the
        root window."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'rooty', self._w))

    eleza winfo_screen(self):
        """Return the screen name of this widget."""
        rudisha self.tk.call('winfo', 'screen', self._w)

    eleza winfo_screencells(self):
        """Return the number of the cells kwenye the colormap of the screen
        of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screencells', self._w))

    eleza winfo_screendepth(self):
        """Return the number of bits per pixel of the root window of the
        screen of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screendepth', self._w))

    eleza winfo_screenheight(self):
        """Return the number of pixels of the height of the screen of this widget
        kwenye pixel."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screenheight', self._w))

    eleza winfo_screenmmheight(self):
        """Return the number of pixels of the height of the screen of
        this widget kwenye mm."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screenmmheight', self._w))

    eleza winfo_screenmmwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget kwenye mm."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screenmmwidth', self._w))

    eleza winfo_screenvisual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, ama truecolor kila the default
        colormotoa of this screen."""
        rudisha self.tk.call('winfo', 'screenvisual', self._w)

    eleza winfo_screenwidth(self):
        """Return the number of pixels of the width of the screen of
        this widget kwenye pixel."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'screenwidth', self._w))

    eleza winfo_server(self):
        """Return information of the X-Server of the screen of this widget in
        the form "XmajorRminor vendor vendorVersion"."""
        rudisha self.tk.call('winfo', 'server', self._w)

    eleza winfo_toplevel(self):
        """Return the toplevel widget of this widget."""
        rudisha self._nametowidget(self.tk.call(
            'winfo', 'toplevel', self._w))

    eleza winfo_viewable(self):
        """Return true ikiwa the widget na all its higher ancestors are mapped."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'viewable', self._w))

    eleza winfo_visual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, ama truecolor kila the
        colormotoa of this widget."""
        rudisha self.tk.call('winfo', 'visual', self._w)

    eleza winfo_visualid(self):
        """Return the X identifier kila the visual kila this widget."""
        rudisha self.tk.call('winfo', 'visualid', self._w)

    eleza winfo_visualsavailable(self, includeids=Uongo):
        """Return a list of all visuals available kila the screen
        of this widget.

        Each item kwenye the list consists of a visual name (see winfo_visual), a
        depth na ikiwa includeids ni true ni given also the X identifier."""
        data = self.tk.call('winfo', 'visualsavailable', self._w,
                            'includeids' ikiwa includeids isipokua Tupu)
        data = [self.tk.splitlist(x) kila x kwenye self.tk.splitlist(data)]
        rudisha [self.__winfo_parseitem(x) kila x kwenye data]

    eleza __winfo_parseitem(self, t):
        """Internal function."""
        rudisha t[:1] + tuple(map(self.__winfo_getint, t[1:]))

    eleza __winfo_getint(self, x):
        """Internal function."""
        rudisha int(x, 0)

    eleza winfo_vrootheight(self):
        """Return the height of the virtual root window associated ukijumuisha this
        widget kwenye pixels. If there ni no virtual root window rudisha the
        height of the screen."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'vrootheight', self._w))

    eleza winfo_vrootwidth(self):
        """Return the width of the virtual root window associated ukijumuisha this
        widget kwenye pixel. If there ni no virtual root window rudisha the
        width of the screen."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'vrootwidth', self._w))

    eleza winfo_vrootx(self):
        """Return the x offset of the virtual root relative to the root
        window of the screen of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'vrootx', self._w))

    eleza winfo_vrooty(self):
        """Return the y offset of the virtual root relative to the root
        window of the screen of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'vrooty', self._w))

    eleza winfo_width(self):
        """Return the width of this widget."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'width', self._w))

    eleza winfo_x(self):
        """Return the x coordinate of the upper left corner of this widget
        kwenye the parent."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'x', self._w))

    eleza winfo_y(self):
        """Return the y coordinate of the upper left corner of this widget
        kwenye the parent."""
        rudisha self.tk.getint(
            self.tk.call('winfo', 'y', self._w))

    eleza update(self):
        """Enter event loop until all pending events have been processed by Tcl."""
        self.tk.call('update')

    eleza update_idletasks(self):
        """Enter event loop until all idle callbacks have been called. This
        will update the display of windows but sio process events caused by
        the user."""
        self.tk.call('update', 'idletasks')

    eleza bindtags(self, tagList=Tupu):
        """Set ama get the list of bindtags kila this widget.

        With no argument rudisha the list of all bindtags associated with
        this widget. With a list of strings kama argument the bindtags are
        set to this list. The bindtags determine kwenye which order events are
        processed (see bind)."""
        ikiwa tagList ni Tupu:
            rudisha self.tk.splitlist(
                self.tk.call('bindtags', self._w))
        isipokua:
            self.tk.call('bindtags', self._w, tagList)

    eleza _bind(self, what, sequence, func, add, needcleanup=1):
        """Internal function."""
        ikiwa isinstance(func, str):
            self.tk.call(what + (sequence, func))
        lasivyo func:
            funcid = self._register(func, self._substitute,
                        needcleanup)
            cmd = ('%sikiwa {"[%s %s]" == "koma"} koma\n'
                   %
                   (add na '+' ama '',
                funcid, self._subst_format_str))
            self.tk.call(what + (sequence, cmd))
            rudisha funcid
        lasivyo sequence:
            rudisha self.tk.call(what + (sequence,))
        isipokua:
            rudisha self.tk.splitlist(self.tk.call(what))

    eleza bind(self, sequence=Tupu, func=Tupu, add=Tupu):
        """Bind to this widget at event SEQUENCE a call to function FUNC.

        SEQUENCE ni a string of concatenated event
        patterns. An event pattern ni of the form
        <MODIFIER-MODIFIER-TYPE-DETAIL> where MODIFIER ni one
        of Control, Mod2, M2, Shift, Mod3, M3, Lock, Mod4, M4,
        Button1, B1, Mod5, M5 Button2, B2, Meta, M, Button3,
        B3, Alt, Button4, B4, Double, Button5, B5 Triple,
        Mod1, M1. TYPE ni one of Activate, Enter, Map,
        ButtonPress, Button, Expose, Motion, ButtonRelease
        FocusIn, MouseWheel, Circulate, FocusOut, Property,
        Colormap, Gravity Reparent, Configure, KeyPress, Key,
        Unmap, Deactivate, KeyRelease Visibility, Destroy,
        Leave na DETAIL ni the button number kila ButtonPress,
        ButtonRelease na DETAIL ni the Keysym kila KeyPress na
        KeyRelease. Examples are
        <Control-Button-1> kila pressing Control na mouse button 1 ama
        <Alt-A> kila pressing A na the Alt key (KeyPress can be omitted).
        An event pattern can also be a virtual event of the form
        <<AString>> where AString can be arbitrary. This
        event can be generated by event_generate.
        If events are concatenated they must appear shortly
        after each other.

        FUNC will be called ikiwa the event sequence occurs ukijumuisha an
        instance of Event kama argument. If the rudisha value of FUNC is
        "koma" no further bound function ni invoked.

        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function ama whether
        it will replace the previous function.

        Bind will rudisha an identifier to allow deletion of the bound function with
        unbind without memory leak.

        If FUNC ama SEQUENCE ni omitted the bound function ama list
        of bound events are returned."""

        rudisha self._bind(('bind', self._w), sequence, func, add)

    eleza unbind(self, sequence, funcid=Tupu):
        """Unbind kila this widget kila event SEQUENCE  the
        function identified ukijumuisha FUNCID."""
        self.tk.call('bind', self._w, sequence, '')
        ikiwa funcid:
            self.deletecommand(funcid)

    eleza bind_all(self, sequence=Tupu, func=Tupu, add=Tupu):
        """Bind to all widgets at an event SEQUENCE a call to function FUNC.
        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function ama whether
        it will replace the previous function. See bind kila the rudisha value."""
        rudisha self._bind(('bind', 'all'), sequence, func, add, 0)

    eleza unbind_all(self, sequence):
        """Unbind kila all widgets kila event SEQUENCE all functions."""
        self.tk.call('bind', 'all' , sequence, '')

    eleza bind_class(self, className, sequence=Tupu, func=Tupu, add=Tupu):
        """Bind to widgets ukijumuisha bindtag CLASSNAME at event
        SEQUENCE a call of function FUNC. An additional
        boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function ama
        whether it will replace the previous function. See bind for
        the rudisha value."""

        rudisha self._bind(('bind', className), sequence, func, add, 0)

    eleza unbind_class(self, className, sequence):
        """Unbind kila all widgets ukijumuisha bindtag CLASSNAME kila event SEQUENCE
        all functions."""
        self.tk.call('bind', className , sequence, '')

    eleza mainloop(self, n=0):
        """Call the mainloop of Tk."""
        self.tk.mainloop(n)

    eleza quit(self):
        """Quit the Tcl interpreter. All widgets will be destroyed."""
        self.tk.quit()

    eleza _getints(self, string):
        """Internal function."""
        ikiwa string:
            rudisha tuple(map(self.tk.getint, self.tk.splitlist(string)))

    eleza _getdoubles(self, string):
        """Internal function."""
        ikiwa string:
            rudisha tuple(map(self.tk.getdouble, self.tk.splitlist(string)))

    eleza _getboolean(self, string):
        """Internal function."""
        ikiwa string:
            rudisha self.tk.getboolean(string)

    eleza _displayof(self, displayof):
        """Internal function."""
        ikiwa displayof:
            rudisha ('-displayof', displayof)
        ikiwa displayof ni Tupu:
            rudisha ('-displayof', self._w)
        rudisha ()

    @property
    eleza _windowingsystem(self):
        """Internal function."""
        jaribu:
            rudisha self._root()._windowingsystem_cached
        tatizo AttributeError:
            ws = self._root()._windowingsystem_cached = \
                        self.tk.call('tk', 'windowingsystem')
            rudisha ws

    eleza _options(self, cnf, kw = Tupu):
        """Internal function."""
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        isipokua:
            cnf = _cnfmerge(cnf)
        res = ()
        kila k, v kwenye cnf.items():
            ikiwa v ni sio Tupu:
                ikiwa k[-1] == '_': k = k[:-1]
                ikiwa callable(v):
                    v = self._register(v)
                lasivyo isinstance(v, (tuple, list)):
                    nv = []
                    kila item kwenye v:
                        ikiwa isinstance(item, int):
                            nv.append(str(item))
                        lasivyo isinstance(item, str):
                            nv.append(_stringify(item))
                        isipokua:
                            koma
                    isipokua:
                        v = ' '.join(nv)
                res = res + ('-'+k, v)
        rudisha res

    eleza nametowidget(self, name):
        """Return the Tkinter instance of a widget identified by
        its Tcl name NAME."""
        name = str(name).split('.')
        w = self

        ikiwa sio name[0]:
            w = w._root()
            name = name[1:]

        kila n kwenye name:
            ikiwa sio n:
                koma
            w = w.children[n]

        rudisha w

    _nametowidget = nametowidget

    eleza _register(self, func, subst=Tupu, needcleanup=1):
        """Return a newly created Tcl function. If this
        function ni called, the Python function FUNC will
        be executed. An optional function SUBST can
        be given which will be executed before FUNC."""
        f = CallWrapper(func, subst, self).__call__
        name = repr(id(f))
        jaribu:
            func = func.__func__
        tatizo AttributeError:
            pita
        jaribu:
            name = name + func.__name__
        tatizo AttributeError:
            pita
        self.tk.createcommand(name, f)
        ikiwa needcleanup:
            ikiwa self._tclCommands ni Tupu:
                self._tclCommands = []
            self._tclCommands.append(name)
        rudisha name

    register = _register

    eleza _root(self):
        """Internal function."""
        w = self
        wakati w.master: w = w.master
        rudisha w
    _subst_format = ('%#', '%b', '%f', '%h', '%k',
             '%s', '%t', '%w', '%x', '%y',
             '%A', '%E', '%K', '%N', '%W', '%T', '%X', '%Y', '%D')
    _subst_format_str = " ".join(_subst_format)

    eleza _substitute(self, *args):
        """Internal function."""
        ikiwa len(args) != len(self._subst_format): rudisha args
        getboolean = self.tk.getboolean

        getint = self.tk.getint
        eleza getint_event(s):
            """Tk changed behavior kwenye 8.4.2, returning "??" rather more often."""
            jaribu:
                rudisha getint(s)
            tatizo (ValueError, TclError):
                rudisha s

        nsign, b, f, h, k, s, t, w, x, y, A, E, K, N, W, T, X, Y, D = args
        # Missing: (a, c, d, m, o, v, B, R)
        e = Event()
        # serial field: valid kila all events
        # number of button: ButtonPress na ButtonRelease events only
        # height field: Configure, ConfigureRequest, Create,
        # ResizeRequest, na Expose events only
        # keycode field: KeyPress na KeyRelease events only
        # time field: "valid kila events that contain a time field"
        # width field: Configure, ConfigureRequest, Create, ResizeRequest,
        # na Expose events only
        # x field: "valid kila events that contain an x field"
        # y field: "valid kila events that contain a y field"
        # keysym kama decimal: KeyPress na KeyRelease events only
        # x_root, y_root fields: ButtonPress, ButtonRelease, KeyPress,
        # KeyRelease, na Motion events
        e.serial = getint(nsign)
        e.num = getint_event(b)
        jaribu: e.focus = getboolean(f)
        tatizo TclError: pita
        e.height = getint_event(h)
        e.keycode = getint_event(k)
        e.state = getint_event(s)
        e.time = getint_event(t)
        e.width = getint_event(w)
        e.x = getint_event(x)
        e.y = getint_event(y)
        e.char = A
        jaribu: e.send_event = getboolean(E)
        tatizo TclError: pita
        e.keysym = K
        e.keysym_num = getint_event(N)
        jaribu:
            e.type = EventType(T)
        tatizo ValueError:
            e.type = T
        jaribu:
            e.widget = self._nametowidget(W)
        tatizo KeyError:
            e.widget = W
        e.x_root = getint_event(X)
        e.y_root = getint_event(Y)
        jaribu:
            e.delta = getint(D)
        tatizo (ValueError, TclError):
            e.delta = 0
        rudisha (e,)

    eleza _report_exception(self):
        """Internal function."""
        exc, val, tb = sys.exc_info()
        root = self._root()
        root.report_callback_exception(exc, val, tb)

    eleza _getconfigure(self, *args):
        """Call Tcl configure command na rudisha the result kama a dict."""
        cnf = {}
        kila x kwenye self.tk.splitlist(self.tk.call(*args)):
            x = self.tk.splitlist(x)
            cnf[x[0][1:]] = (x[0][1:],) + x[1:]
        rudisha cnf

    eleza _getconfigure1(self, *args):
        x = self.tk.splitlist(self.tk.call(*args))
        rudisha (x[0][1:],) + x[1:]

    eleza _configure(self, cmd, cnf, kw):
        """Internal function."""
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        lasivyo cnf:
            cnf = _cnfmerge(cnf)
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(_flatten((self._w, cmd)))
        ikiwa isinstance(cnf, str):
            rudisha self._getconfigure1(_flatten((self._w, cmd, '-'+cnf)))
        self.tk.call(_flatten((self._w, cmd)) + self._options(cnf))
    # These used to be defined kwenye Widget:

    eleza configure(self, cnf=Tupu, **kw):
        """Configure resources of a widget.

        The values kila resources are specified kama keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """
        rudisha self._configure('configure', cnf, kw)

    config = configure

    eleza cget(self, key):
        """Return the resource value kila a KEY given kama string."""
        rudisha self.tk.call(self._w, 'cget', '-' + key)

    __getitem__ = cget

    eleza __setitem__(self, key, value):
        self.configure({key: value})

    eleza keys(self):
        """Return a list of all resource names of this widget."""
        splitlist = self.tk.splitlist
        rudisha [splitlist(x)[0][1:] kila x in
                splitlist(self.tk.call(self._w, 'configure'))]

    eleza __str__(self):
        """Return the window path name of this widget."""
        rudisha self._w

    eleza __repr__(self):
        rudisha '<%s.%s object %s>' % (
            self.__class__.__module__, self.__class__.__qualname__, self._w)

    # Pack methods that apply to the master
    _noarg_ = ['_noarg_']

    eleza pack_propagate(self, flag=_noarg_):
        """Set ama get the status kila propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        ni given the current setting will be returned.
        """
        ikiwa flag ni Misc._noarg_:
            rudisha self._getboolean(self.tk.call(
                'pack', 'propagate', self._w))
        isipokua:
            self.tk.call('pack', 'propagate', self._w, flag)

    propagate = pack_propagate

    eleza pack_slaves(self):
        """Return a list of all slaves of this widget
        kwenye its packing order."""
        rudisha [self._nametowidget(x) kila x in
                self.tk.splitlist(
                   self.tk.call('pack', 'slaves', self._w))]

    slaves = pack_slaves

    # Place method that applies to the master
    eleza place_slaves(self):
        """Return a list of all slaves of this widget
        kwenye its packing order."""
        rudisha [self._nametowidget(x) kila x in
                self.tk.splitlist(
                   self.tk.call(
                       'place', 'slaves', self._w))]

    # Grid methods that apply to the master

    eleza grid_anchor(self, anchor=Tupu): # new kwenye Tk 8.5
        """The anchor value controls how to place the grid within the
        master when no row/column has any weight.

        The default anchor ni nw."""
        self.tk.call('grid', 'anchor', self._w, anchor)

    anchor = grid_anchor

    eleza grid_bbox(self, column=Tupu, row=Tupu, col2=Tupu, row2=Tupu):
        """Return a tuple of integer coordinates kila the bounding
        box of this widget controlled by the geometry manager grid.

        If COLUMN, ROW ni given the bounding box applies from
        the cell ukijumuisha row na column 0 to the specified
        cell. If COL2 na ROW2 are given the bounding box
        starts at that cell.

        The returned integers specify the offset of the upper left
        corner kwenye the master widget na the width na height.
        """
        args = ('grid', 'bbox', self._w)
        ikiwa column ni sio Tupu na row ni sio Tupu:
            args = args + (column, row)
        ikiwa col2 ni sio Tupu na row2 ni sio Tupu:
            args = args + (col2, row2)
        rudisha self._getints(self.tk.call(*args)) ama Tupu

    bbox = grid_bbox

    eleza _gridconvvalue(self, value):
        ikiwa isinstance(value, (str, _tkinter.Tcl_Obj)):
            jaribu:
                svalue = str(value)
                ikiwa sio svalue:
                    rudisha Tupu
                lasivyo '.' kwenye svalue:
                    rudisha self.tk.getdouble(svalue)
                isipokua:
                    rudisha self.tk.getint(svalue)
            tatizo (ValueError, TclError):
                pita
        rudisha value

    eleza _grid_configure(self, command, index, cnf, kw):
        """Internal function."""
        ikiwa isinstance(cnf, str) na sio kw:
            ikiwa cnf[-1:] == '_':
                cnf = cnf[:-1]
            ikiwa cnf[:1] != '-':
                cnf = '-'+cnf
            options = (cnf,)
        isipokua:
            options = self._options(cnf, kw)
        ikiwa sio options:
            rudisha _splitdict(
                self.tk,
                self.tk.call('grid', command, self._w, index),
                conv=self._gridconvvalue)
        res = self.tk.call(
                  ('grid', command, self._w, index)
                  + options)
        ikiwa len(options) == 1:
            rudisha self._gridconvvalue(res)

    eleza grid_columnconfigure(self, index, cnf={}, **kw):
        """Configure column INDEX of a grid.

        Valid resources are minsize (minimum size of the column),
        weight (how much does additional space propagate to this column)
        na pad (how much space to let additionally)."""
        rudisha self._grid_configure('columnconfigure', index, cnf, kw)

    columnconfigure = grid_columnconfigure

    eleza grid_location(self, x, y):
        """Return a tuple of column na row which identify the cell
        at which the pixel at position X na Y inside the master
        widget ni located."""
        rudisha self._getints(
            self.tk.call(
                'grid', 'location', self._w, x, y)) ama Tupu

    eleza grid_propagate(self, flag=_noarg_):
        """Set ama get the status kila propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        ni given, the current setting will be returned.
        """
        ikiwa flag ni Misc._noarg_:
            rudisha self._getboolean(self.tk.call(
                'grid', 'propagate', self._w))
        isipokua:
            self.tk.call('grid', 'propagate', self._w, flag)

    eleza grid_rowconfigure(self, index, cnf={}, **kw):
        """Configure row INDEX of a grid.

        Valid resources are minsize (minimum size of the row),
        weight (how much does additional space propagate to this row)
        na pad (how much space to let additionally)."""
        rudisha self._grid_configure('rowconfigure', index, cnf, kw)

    rowconfigure = grid_rowconfigure

    eleza grid_size(self):
        """Return a tuple of the number of column na rows kwenye the grid."""
        rudisha self._getints(
            self.tk.call('grid', 'size', self._w)) ama Tupu

    size = grid_size

    eleza grid_slaves(self, row=Tupu, column=Tupu):
        """Return a list of all slaves of this widget
        kwenye its packing order."""
        args = ()
        ikiwa row ni sio Tupu:
            args = args + ('-row', row)
        ikiwa column ni sio Tupu:
            args = args + ('-column', column)
        rudisha [self._nametowidget(x) kila x in
                self.tk.splitlist(self.tk.call(
                   ('grid', 'slaves', self._w) + args))]

    # Support kila the "event" command, new kwenye Tk 4.2.
    # By Case Roole.

    eleza event_add(self, virtual, *sequences):
        """Bind a virtual event VIRTUAL (of the form <<Name>>)
        to an event SEQUENCE such that the virtual event ni triggered
        whenever SEQUENCE occurs."""
        args = ('event', 'add', virtual) + sequences
        self.tk.call(args)

    eleza event_delete(self, virtual, *sequences):
        """Unbind a virtual event VIRTUAL kutoka SEQUENCE."""
        args = ('event', 'delete', virtual) + sequences
        self.tk.call(args)

    eleza event_generate(self, sequence, **kw):
        """Generate an event SEQUENCE. Additional
        keyword arguments specify parameter of the event
        (e.g. x, y, rootx, rooty)."""
        args = ('event', 'generate', self._w, sequence)
        kila k, v kwenye kw.items():
            args = args + ('-%s' % k, str(v))
        self.tk.call(args)

    eleza event_info(self, virtual=Tupu):
        """Return a list of all virtual events ama the information
        about the SEQUENCE bound to the virtual event VIRTUAL."""
        rudisha self.tk.splitlist(
            self.tk.call('event', 'info', virtual))

    # Image related commands

    eleza image_names(self):
        """Return a list of all existing image names."""
        rudisha self.tk.splitlist(self.tk.call('image', 'names'))

    eleza image_types(self):
        """Return a list of all available image types (e.g. photo bitmap)."""
        rudisha self.tk.splitlist(self.tk.call('image', 'types'))


kundi CallWrapper:
    """Internal class. Stores function to call when some user
    defined Tcl function ni called e.g. after an event occurred."""

    eleza __init__(self, func, subst, widget):
        """Store FUNC, SUBST na WIDGET kama members."""
        self.func = func
        self.subst = subst
        self.widget = widget

    eleza __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        jaribu:
            ikiwa self.subst:
                args = self.subst(*args)
            rudisha self.func(*args)
        tatizo SystemExit:
            raise
        tatizo:
            self.widget._report_exception()


kundi XView:
    """Mix-in kundi kila querying na changing the horizontal position
    of a widget's window."""

    eleza xview(self, *args):
        """Query na change the horizontal position of the view."""
        res = self.tk.call(self._w, 'xview', *args)
        ikiwa sio args:
            rudisha self._getdoubles(res)

    eleza xview_moveto(self, fraction):
        """Adjusts the view kwenye the window so that FRACTION of the
        total width of the canvas ni off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)

    eleza xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which ni measured kwenye "units"
        ama "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)


kundi YView:
    """Mix-in kundi kila querying na changing the vertical position
    of a widget's window."""

    eleza yview(self, *args):
        """Query na change the vertical position of the view."""
        res = self.tk.call(self._w, 'yview', *args)
        ikiwa sio args:
            rudisha self._getdoubles(res)

    eleza yview_moveto(self, fraction):
        """Adjusts the view kwenye the window so that FRACTION of the
        total height of the canvas ni off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)

    eleza yview_scroll(self, number, what):
        """Shift the y-view according to NUMBER which ni measured in
        "units" ama "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)


kundi Wm:
    """Provides functions kila the communication ukijumuisha the window manager."""

    eleza wm_aspect(self,
              minNumer=Tupu, minDenom=Tupu,
              maxNumer=Tupu, maxDenom=Tupu):
        """Instruct the window manager to set the aspect ratio (width/height)
        of this widget to be between MINNUMER/MINDENOM na MAXNUMER/MAXDENOM. Return a tuple
        of the actual values ikiwa no argument ni given."""
        rudisha self._getints(
            self.tk.call('wm', 'aspect', self._w,
                     minNumer, minDenom,
                     maxNumer, maxDenom))

    aspect = wm_aspect

    eleza wm_attributes(self, *args):
        """This subcommand returns ama sets platform specific attributes

        The first form returns a list of the platform specific flags na
        their values. The second form returns the value kila the specific
        option. The third form sets one ama more of the values. The values
        are kama follows:

        On Windows, -disabled gets ama sets whether the window ni kwenye a
        disabled state. -toolwindow gets ama sets the style of the window
        to toolwindow (as defined kwenye the MSDN). -topmost gets ama sets
        whether this ni a topmost window (displays above all other
        windows).

        On Macintosh, XXXXX

        On Unix, there are currently no special attribute values.
        """
        args = ('wm', 'attributes', self._w) + args
        rudisha self.tk.call(args)

    attributes = wm_attributes

    eleza wm_client(self, name=Tupu):
        """Store NAME kwenye WM_CLIENT_MACHINE property of this widget. Return
        current value."""
        rudisha self.tk.call('wm', 'client', self._w, name)

    client = wm_client

    eleza wm_colormapwindows(self, *wlist):
        """Store list of window names (WLIST) into WM_COLORMAPWINDOWS property
        of this widget. This list contains windows whose colormaps differ kutoka their
        parents. Return current list of widgets ikiwa WLIST ni empty."""
        ikiwa len(wlist) > 1:
            wlist = (wlist,) # Tk needs a list of windows here
        args = ('wm', 'colormapwindows', self._w) + wlist
        ikiwa wlist:
            self.tk.call(args)
        isipokua:
            rudisha [self._nametowidget(x)
                    kila x kwenye self.tk.splitlist(self.tk.call(args))]

    colormapwindows = wm_colormapwindows

    eleza wm_command(self, value=Tupu):
        """Store VALUE kwenye WM_COMMAND property. It ni the command
        which shall be used to invoke the application. Return current
        command ikiwa VALUE ni Tupu."""
        rudisha self.tk.call('wm', 'command', self._w, value)

    command = wm_command

    eleza wm_deiconify(self):
        """Deiconify this widget. If it was never mapped it will sio be mapped.
        On Windows it will ashiria this widget na give it the focus."""
        rudisha self.tk.call('wm', 'deiconify', self._w)

    deiconify = wm_deiconify

    eleza wm_focusmodel(self, model=Tupu):
        """Set focus motoa to MODEL. "active" means that this widget will claim
        the focus itself, "pitaive" means that the window manager shall give
        the focus. Return current focus motoa ikiwa MODEL ni Tupu."""
        rudisha self.tk.call('wm', 'focusmodel', self._w, model)

    focusmotoa = wm_focusmodel

    eleza wm_forget(self, window): # new kwenye Tk 8.5
        """The window will be unmapped kutoka the screen na will no longer
        be managed by wm. toplevel windows will be treated like frame
        windows once they are no longer managed by wm, however, the menu
        option configuration will be remembered na the menus will return
        once the widget ni managed again."""
        self.tk.call('wm', 'forget', window)

    forget = wm_forget

    eleza wm_frame(self):
        """Return identifier kila decorative frame of this widget ikiwa present."""
        rudisha self.tk.call('wm', 'frame', self._w)

    frame = wm_frame

    eleza wm_geometry(self, newGeometry=Tupu):
        """Set geometry to NEWGEOMETRY of the form =widthxheight+x+y. Return
        current value ikiwa Tupu ni given."""
        rudisha self.tk.call('wm', 'geometry', self._w, newGeometry)

    geometry = wm_geometry

    eleza wm_grid(self,
         baseWidth=Tupu, baseHeight=Tupu,
         widthInc=Tupu, heightInc=Tupu):
        """Instruct the window manager that this widget shall only be
        resized on grid boundaries. WIDTHINC na HEIGHTINC are the width na
        height of a grid unit kwenye pixels. BASEWIDTH na BASEHEIGHT are the
        number of grid units requested kwenye Tk_GeometryRequest."""
        rudisha self._getints(self.tk.call(
            'wm', 'grid', self._w,
            baseWidth, baseHeight, widthInc, heightInc))

    grid = wm_grid

    eleza wm_group(self, pathName=Tupu):
        """Set the group leader widgets kila related widgets to PATHNAME. Return
        the group leader of this widget ikiwa Tupu ni given."""
        rudisha self.tk.call('wm', 'group', self._w, pathName)

    group = wm_group

    eleza wm_iconbitmap(self, bitmap=Tupu, default=Tupu):
        """Set bitmap kila the iconified widget to BITMAP. Return
        the bitmap ikiwa Tupu ni given.

        Under Windows, the DEFAULT parameter can be used to set the icon
        kila the widget na any descendents that don't have an icon set
        explicitly.  DEFAULT can be the relative path to a .ico file
        (example: root.iconbitmap(default='myicon.ico') ).  See Tk
        documentation kila more information."""
        ikiwa default:
            rudisha self.tk.call('wm', 'iconbitmap', self._w, '-default', default)
        isipokua:
            rudisha self.tk.call('wm', 'iconbitmap', self._w, bitmap)

    iconbitmap = wm_iconbitmap

    eleza wm_iconify(self):
        """Display widget kama icon."""
        rudisha self.tk.call('wm', 'iconify', self._w)

    iconify = wm_iconify

    eleza wm_iconmask(self, bitmap=Tupu):
        """Set mask kila the icon bitmap of this widget. Return the
        mask ikiwa Tupu ni given."""
        rudisha self.tk.call('wm', 'iconmask', self._w, bitmap)

    iconmask = wm_iconmask

    eleza wm_iconname(self, newName=Tupu):
        """Set the name of the icon kila this widget. Return the name if
        Tupu ni given."""
        rudisha self.tk.call('wm', 'iconname', self._w, newName)

    iconname = wm_iconname

    eleza wm_iconphoto(self, default=Uongo, *args): # new kwenye Tk 8.5
        """Sets the titlebar icon kila this window based on the named photo
        images pitaed through args. If default ni Kweli, this ni applied to
        all future created toplevels kama well.

        The data kwenye the images ni taken kama a snapshot at the time of
        invocation. If the images are later changed, this ni sio reflected
        to the titlebar icons. Multiple images are accepted to allow
        different images sizes to be provided. The window manager may scale
        provided icons to an appropriate size.

        On Windows, the images are packed into a Windows icon structure.
        This will override an icon specified to wm_iconbitmap, na vice
        versa.

        On X, the images are arranged into the _NET_WM_ICON X property,
        which most modern window managers support. An icon specified by
        wm_iconbitmap may exist simultaneously.

        On Macintosh, this currently does nothing."""
        ikiwa default:
            self.tk.call('wm', 'iconphoto', self._w, "-default", *args)
        isipokua:
            self.tk.call('wm', 'iconphoto', self._w, *args)

    iconphoto = wm_iconphoto

    eleza wm_iconposition(self, x=Tupu, y=Tupu):
        """Set the position of the icon of this widget to X na Y. Return
        a tuple of the current values of X na X ikiwa Tupu ni given."""
        rudisha self._getints(self.tk.call(
            'wm', 'iconposition', self._w, x, y))

    iconposition = wm_iconposition

    eleza wm_iconwindow(self, pathName=Tupu):
        """Set widget PATHNAME to be displayed instead of icon. Return the current
        value ikiwa Tupu ni given."""
        rudisha self.tk.call('wm', 'iconwindow', self._w, pathName)

    iconwindow = wm_iconwindow

    eleza wm_manage(self, widget): # new kwenye Tk 8.5
        """The widget specified will become a stand alone top-level window.
        The window will be decorated ukijumuisha the window managers title bar,
        etc."""
        self.tk.call('wm', 'manage', widget)

    manage = wm_manage

    eleza wm_maxsize(self, width=Tupu, height=Tupu):
        """Set max WIDTH na HEIGHT kila this widget. If the window ni gridded
        the values are given kwenye grid units. Return the current values ikiwa Tupu
        ni given."""
        rudisha self._getints(self.tk.call(
            'wm', 'maxsize', self._w, width, height))

    maxsize = wm_maxsize

    eleza wm_minsize(self, width=Tupu, height=Tupu):
        """Set min WIDTH na HEIGHT kila this widget. If the window ni gridded
        the values are given kwenye grid units. Return the current values ikiwa Tupu
        ni given."""
        rudisha self._getints(self.tk.call(
            'wm', 'minsize', self._w, width, height))

    minsize = wm_minsize

    eleza wm_overrideredirect(self, boolean=Tupu):
        """Instruct the window manager to ignore this widget
        ikiwa BOOLEAN ni given ukijumuisha 1. Return the current value ikiwa Tupu
        ni given."""
        rudisha self._getboolean(self.tk.call(
            'wm', 'overrideredirect', self._w, boolean))

    overrideredirect = wm_overrideredirect

    eleza wm_positionfrom(self, who=Tupu):
        """Instruct the window manager that the position of this widget shall
        be defined by the user ikiwa WHO ni "user", na by its own policy ikiwa WHO is
        "program"."""
        rudisha self.tk.call('wm', 'positionfrom', self._w, who)

    positionkutoka = wm_positionfrom

    eleza wm_protocol(self, name=Tupu, func=Tupu):
        """Bind function FUNC to command NAME kila this widget.
        Return the function bound to NAME ikiwa Tupu ni given. NAME could be
        e.g. "WM_SAVE_YOURSELF" ama "WM_DELETE_WINDOW"."""
        ikiwa callable(func):
            command = self._register(func)
        isipokua:
            command = func
        rudisha self.tk.call(
            'wm', 'protocol', self._w, name, command)

    protocol = wm_protocol

    eleza wm_resizable(self, width=Tupu, height=Tupu):
        """Instruct the window manager whether this width can be resized
        kwenye WIDTH ama HEIGHT. Both values are boolean values."""
        rudisha self.tk.call('wm', 'resizable', self._w, width, height)

    resizable = wm_resizable

    eleza wm_sizefrom(self, who=Tupu):
        """Instruct the window manager that the size of this widget shall
        be defined by the user ikiwa WHO ni "user", na by its own policy ikiwa WHO is
        "program"."""
        rudisha self.tk.call('wm', 'sizefrom', self._w, who)

    sizekutoka = wm_sizefrom

    eleza wm_state(self, newstate=Tupu):
        """Query ama set the state of this widget kama one of normal, icon,
        iconic (see wm_iconwindow), withdrawn, ama zoomed (Windows only)."""
        rudisha self.tk.call('wm', 'state', self._w, newstate)

    state = wm_state

    eleza wm_title(self, string=Tupu):
        """Set the title of this widget."""
        rudisha self.tk.call('wm', 'title', self._w, string)

    title = wm_title

    eleza wm_transient(self, master=Tupu):
        """Instruct the window manager that this widget ni transient
        ukijumuisha regard to widget MASTER."""
        rudisha self.tk.call('wm', 'transient', self._w, master)

    transient = wm_transient

    eleza wm_withdraw(self):
        """Withdraw this widget kutoka the screen such that it ni unmapped
        na forgotten by the window manager. Re-draw it ukijumuisha wm_deiconify."""
        rudisha self.tk.call('wm', 'withdraw', self._w)

    withdraw = wm_withdraw


kundi Tk(Misc, Wm):
    """Toplevel widget of Tk which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    _w = '.'

    eleza __init__(self, screenName=Tupu, baseName=Tupu, className='Tk',
                 useTk=1, sync=0, use=Tupu):
        """Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
        be created. BASENAME will be used kila the identification of the profile file (see
        readprofile).
        It ni constructed kutoka sys.argv[0] without extensions ikiwa Tupu ni given. CLASSNAME
        ni the name of the widget class."""
        self.master = Tupu
        self.children = {}
        self._tkloaded = 0
        # to avoid recursions kwenye the getattr code kwenye case of failure, we
        # ensure that self.tk ni always _something_.
        self.tk = Tupu
        ikiwa baseName ni Tupu:
            agiza os
            baseName = os.path.basename(sys.argv[0])
            baseName, ext = os.path.splitext(baseName)
            ikiwa ext haiko kwenye ('.py', '.pyc'):
                baseName = baseName + ext
        interactive = 0
        self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
        ikiwa useTk:
            self._loadtk()
        ikiwa sio sys.flags.ignore_environment:
            # Issue #16248: Honor the -E flag to avoid code injection.
            self.readprofile(baseName, className)

    eleza loadtk(self):
        ikiwa sio self._tkloaded:
            self.tk.loadtk()
            self._loadtk()

    eleza _loadtk(self):
        self._tkloaded = 1
        global _default_root
        # Version sanity checks
        tk_version = self.tk.getvar('tk_version')
        ikiwa tk_version != _tkinter.TK_VERSION:
            ashiria RuntimeError("tk.h version (%s) doesn't match libtk.a version (%s)"
                               % (_tkinter.TK_VERSION, tk_version))
        # Under unknown circumstances, tcl_version gets coerced to float
        tcl_version = str(self.tk.getvar('tcl_version'))
        ikiwa tcl_version != _tkinter.TCL_VERSION:
            ashiria RuntimeError("tcl.h version (%s) doesn't match libtcl.a version (%s)" \
                               % (_tkinter.TCL_VERSION, tcl_version))
        # Create na register the tkerror na exit commands
        # We need to inline parts of _register here, _ register
        # would register differently-named commands.
        ikiwa self._tclCommands ni Tupu:
            self._tclCommands = []
        self.tk.createcommand('tkerror', _tkerror)
        self.tk.createcommand('exit', _exit)
        self._tclCommands.append('tkerror')
        self._tclCommands.append('exit')
        ikiwa _support_default_root na sio _default_root:
            _default_root = self
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    eleza destroy(self):
        """Destroy this na all descendants widgets. This will
        end the application of this Tcl interpreter."""
        kila c kwenye list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        Misc.destroy(self)
        global _default_root
        ikiwa _support_default_root na _default_root ni self:
            _default_root = Tupu

    eleza readprofile(self, baseName, className):
        """Internal function. It reads BASENAME.tcl na CLASSNAME.tcl into
        the Tcl Interpreter na calls exec on the contents of BASENAME.py na
        CLASSNAME.py ikiwa such a file exists kwenye the home directory."""
        agiza os
        ikiwa 'HOME' kwenye os.environ: home = os.environ['HOME']
        isipokua: home = os.curdir
        class_tcl = os.path.join(home, '.%s.tcl' % className)
        class_py = os.path.join(home, '.%s.py' % className)
        base_tcl = os.path.join(home, '.%s.tcl' % baseName)
        base_py = os.path.join(home, '.%s.py' % baseName)
        dir = {'self': self}
        exec('kutoka tkinter agiza *', dir)
        ikiwa os.path.isfile(class_tcl):
            self.tk.call('source', class_tcl)
        ikiwa os.path.isfile(class_py):
            exec(open(class_py).read(), dir)
        ikiwa os.path.isfile(base_tcl):
            self.tk.call('source', base_tcl)
        ikiwa os.path.isfile(base_py):
            exec(open(base_py).read(), dir)

    eleza report_callback_exception(self, exc, val, tb):
        """Report callback exception on sys.stderr.

        Applications may want to override this internal function, na
        should when sys.stderr ni Tupu."""
        agiza traceback
        andika("Exception kwenye Tkinter callback", file=sys.stderr)
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)

    eleza __getattr__(self, attr):
        "Delegate attribute access to the interpreter object"
        rudisha getattr(self.tk, attr)

# Ideally, the classes Pack, Place na Grid disappear, the
# pack/place/grid methods are defined on the Widget class, na
# everybody uses w.pack_whatever(...) instead of Pack.whatever(w,
# ...), ukijumuisha pack(), place() na grid() being short for
# pack_configure(), place_configure() na grid_columnconfigure(), na
# forget() being short kila pack_forget().  As a practical matter, I'm
# afraid that there ni too much code out there that may be using the
# Pack, Place ama Grid class, so I leave them intact -- but only as
# backwards compatibility features.  Also note that those methods that
# take a master kama argument (e.g. pack_propagate) have been moved to
# the Misc kundi (which now incorporates all methods common between
# toplevel na interior widgets).  Again, kila compatibility, these are
# copied into the Pack, Place ama Grid class.


eleza Tcl(screenName=Tupu, baseName=Tupu, className='Tk', useTk=0):
    rudisha Tk(screenName, baseName, className, useTk)


kundi Pack:
    """Geometry manager Pack.

    Base kundi to use the methods pack_* kwenye every widget."""

    eleza pack_configure(self, cnf={}, **kw):
        """Pack a widget kwenye the parent widget. Use kama options:
        after=widget - pack it after you have packed widget
        anchor=NSEW (or subset) - position widget according to
                                  given direction
        before=widget - pack it before you will pack widget
        expand=bool - expand widget ikiwa parent size grows
        fill=NONE ama X ama Y ama BOTH - fill widget ikiwa widget grows
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding kwenye x direction
        ipady=amount - add internal padding kwenye y direction
        padx=amount - add padding kwenye x direction
        pady=amount - add padding kwenye y direction
        side=TOP ama BOTTOM ama LEFT ama RIGHT -  where to add this widget.
        """
        self.tk.call(
              ('pack', 'configure', self._w)
              + self._options(cnf, kw))

    pack = configure = config = pack_configure

    eleza pack_forget(self):
        """Unmap this widget na do sio use it kila the packing order."""
        self.tk.call('pack', 'forget', self._w)

    forget = pack_forget

    eleza pack_info(self):
        """Return information about the packing options
        kila this widget."""
        d = _splitdict(self.tk, self.tk.call('pack', 'info', self._w))
        ikiwa 'in' kwenye d:
            d['in'] = self.nametowidget(d['in'])
        rudisha d

    info = pack_info
    propagate = pack_propagate = Misc.pack_propagate
    slaves = pack_slaves = Misc.pack_slaves


kundi Place:
    """Geometry manager Place.

    Base kundi to use the methods place_* kwenye every widget."""

    eleza place_configure(self, cnf={}, **kw):
        """Place a widget kwenye the parent widget. Use kama options:
        in=master - master relative to which the widget ni placed
        in_=master - see 'in' option description
        x=amount - locate anchor of this widget at position x of master
        y=amount - locate anchor of this widget at position y of master
        relx=amount - locate anchor of this widget between 0.0 na 1.0
                      relative to width of master (1.0 ni right edge)
        rely=amount - locate anchor of this widget between 0.0 na 1.0
                      relative to height of master (1.0 ni bottom edge)
        anchor=NSEW (or subset) - position anchor according to given direction
        width=amount - width of this widget kwenye pixel
        height=amount - height of this widget kwenye pixel
        relwidth=amount - width of this widget between 0.0 na 1.0
                          relative to width of master (1.0 ni the same width
                          kama the master)
        relheight=amount - height of this widget between 0.0 na 1.0
                           relative to height of master (1.0 ni the same
                           height kama the master)
        bordermode="inside" ama "outside" - whether to take border width of
                                           master widget into account
        """
        self.tk.call(
              ('place', 'configure', self._w)
              + self._options(cnf, kw))

    place = configure = config = place_configure

    eleza place_forget(self):
        """Unmap this widget."""
        self.tk.call('place', 'forget', self._w)

    forget = place_forget

    eleza place_info(self):
        """Return information about the placing options
        kila this widget."""
        d = _splitdict(self.tk, self.tk.call('place', 'info', self._w))
        ikiwa 'in' kwenye d:
            d['in'] = self.nametowidget(d['in'])
        rudisha d

    info = place_info
    slaves = place_slaves = Misc.place_slaves


kundi Grid:
    """Geometry manager Grid.

    Base kundi to use the methods grid_* kwenye every widget."""
    # Thanks to Masazumi Yoshikawa (yosikawa@isi.edu)

    eleza grid_configure(self, cnf={}, **kw):
        """Position a widget kwenye the parent widget kwenye a grid. Use kama options:
        column=number - use cell identified ukijumuisha given column (starting ukijumuisha 0)
        columnspan=number - this widget will span several columns
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding kwenye x direction
        ipady=amount - add internal padding kwenye y direction
        padx=amount - add padding kwenye x direction
        pady=amount - add padding kwenye y direction
        row=number - use cell identified ukijumuisha given row (starting ukijumuisha 0)
        rowspan=number - this widget will span several rows
        sticky=NSEW - ikiwa cell ni larger on which sides will this
                      widget stick to the cell boundary
        """
        self.tk.call(
              ('grid', 'configure', self._w)
              + self._options(cnf, kw))

    grid = configure = config = grid_configure
    bbox = grid_bbox = Misc.grid_bbox
    columnconfigure = grid_columnconfigure = Misc.grid_columnconfigure

    eleza grid_forget(self):
        """Unmap this widget."""
        self.tk.call('grid', 'forget', self._w)

    forget = grid_forget

    eleza grid_remove(self):
        """Unmap this widget but remember the grid options."""
        self.tk.call('grid', 'remove', self._w)

    eleza grid_info(self):
        """Return information about the options
        kila positioning this widget kwenye a grid."""
        d = _splitdict(self.tk, self.tk.call('grid', 'info', self._w))
        ikiwa 'in' kwenye d:
            d['in'] = self.nametowidget(d['in'])
        rudisha d

    info = grid_info
    location = grid_location = Misc.grid_location
    propagate = grid_propagate = Misc.grid_propagate
    rowconfigure = grid_rowconfigure = Misc.grid_rowconfigure
    size = grid_size = Misc.grid_size
    slaves = grid_slaves = Misc.grid_slaves


kundi BaseWidget(Misc):
    """Internal class."""

    eleza _setup(self, master, cnf):
        """Internal function. Sets up information about children."""
        ikiwa _support_default_root:
            global _default_root
            ikiwa sio master:
                ikiwa sio _default_root:
                    _default_root = Tk()
                master = _default_root
        self.master = master
        self.tk = master.tk
        name = Tupu
        ikiwa 'name' kwenye cnf:
            name = cnf['name']
            toa cnf['name']
        ikiwa sio name:
            name = self.__class__.__name__.lower()
            ikiwa master._last_child_ids ni Tupu:
                master._last_child_ids = {}
            count = master._last_child_ids.get(name, 0) + 1
            master._last_child_ids[name] = count
            ikiwa count == 1:
                name = '!%s' % (name,)
            isipokua:
                name = '!%s%d' % (name, count)
        self._name = name
        ikiwa master._w=='.':
            self._w = '.' + name
        isipokua:
            self._w = master._w + '.' + name
        self.children = {}
        ikiwa self._name kwenye self.master.children:
            self.master.children[self._name].destroy()
        self.master.children[self._name] = self

    eleza __init__(self, master, widgetName, cnf={}, kw={}, extra=()):
        """Construct a widget ukijumuisha the parent widget MASTER, a name WIDGETNAME
        na appropriate options."""
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        self.widgetName = widgetName
        BaseWidget._setup(self, master, cnf)
        ikiwa self._tclCommands ni Tupu:
            self._tclCommands = []
        classes = [(k, v) kila k, v kwenye cnf.items() ikiwa isinstance(k, type)]
        kila k, v kwenye classes:
            toa cnf[k]
        self.tk.call(
            (widgetName, self._w) + extra + self._options(cnf))
        kila k, v kwenye classes:
            k.configure(self, v)

    eleza destroy(self):
        """Destroy this na all descendants widgets."""
        kila c kwenye list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        ikiwa self._name kwenye self.master.children:
            toa self.master.children[self._name]
        Misc.destroy(self)

    eleza _do(self, name, args=()):
        # XXX Obsolete -- better use self.tk.call directly!
        rudisha self.tk.call((self._w, name) + args)


kundi Widget(BaseWidget, Pack, Place, Grid):
    """Internal class.

    Base kundi kila a widget which can be positioned ukijumuisha the geometry managers
    Pack, Place ama Grid."""
    pita


kundi Toplevel(BaseWidget, Wm):
    """Toplevel widget, e.g. kila dialogs."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a toplevel widget ukijumuisha the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, menu, relief, screen, takefocus,
        use, visual, width."""
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        extra = ()
        kila wmkey kwenye ['screen', 'class_', 'class', 'visual',
                  'colormap']:
            ikiwa wmkey kwenye cnf:
                val = cnf[wmkey]
                # TBD: a hack needed because some keys
                # are sio valid kama keyword arguments
                ikiwa wmkey[-1] == '_': opt = '-'+wmkey[:-1]
                isipokua: opt = '-'+wmkey
                extra = extra + (opt, val)
                toa cnf[wmkey]
        BaseWidget.__init__(self, master, 'toplevel', cnf, {}, extra)
        root = self._root()
        self.iconname(root.iconname())
        self.title(root.title())
        self.protocol("WM_DELETE_WINDOW", self.destroy)


kundi Button(Widget):
    """Button widget."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a button widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, repeatdelay,
            repeatinterval, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            command, compound, default, height,
            overrelief, state, width
        """
        Widget.__init__(self, master, 'button', cnf, kw)

    eleza flash(self):
        """Flash the button.

        This ni accomplished by redisplaying
        the button several times, alternating between active na
        normal colors. At the end of the flash the button ni left
        kwenye the same normal/active state kama when the command was
        invoked. This command ni ignored ikiwa the button's state is
        disabled.
        """
        self.tk.call(self._w, 'flash')

    eleza invoke(self):
        """Invoke the command associated ukijumuisha the button.

        The rudisha value ni the rudisha value kutoka the command,
        ama an empty string ikiwa there ni no command associated with
        the button. This command ni ignored ikiwa the button's state
        ni disabled.
        """
        rudisha self.tk.call(self._w, 'invoke')


kundi Canvas(Widget, XView, YView):
    """Canvas widget to display graphical elements like lines ama text."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a canvas widget ukijumuisha the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, closeenough,
        confine, cursor, height, highlightbackground, highlightcolor,
        highlightthickness, insertbackground, insertborderwidth,
        insertofftime, insertontime, insertwidth, offset, relief,
        scrollregion, selectbackground, selectborderwidth, selectforeground,
        state, takefocus, width, xscrollcommand, xscrollincrement,
        yscrollcommand, yscrollincrement."""
        Widget.__init__(self, master, 'canvas', cnf, kw)

    eleza addtag(self, *args):
        """Internal function."""
        self.tk.call((self._w, 'addtag') + args)

    eleza addtag_above(self, newtag, tagOrId):
        """Add tag NEWTAG to all items above TAGORID."""
        self.addtag(newtag, 'above', tagOrId)

    eleza addtag_all(self, newtag):
        """Add tag NEWTAG to all items."""
        self.addtag(newtag, 'all')

    eleza addtag_below(self, newtag, tagOrId):
        """Add tag NEWTAG to all items below TAGORID."""
        self.addtag(newtag, 'below', tagOrId)

    eleza addtag_closest(self, newtag, x, y, halo=Tupu, start=Tupu):
        """Add tag NEWTAG to item which ni closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START ni specified the next below this tag ni taken."""
        self.addtag(newtag, 'closest', x, y, halo, start)

    eleza addtag_enclosed(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items kwenye the rectangle defined
        by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'enclosed', x1, y1, x2, y2)

    eleza addtag_overlapping(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'overlapping', x1, y1, x2, y2)

    eleza addtag_withtag(self, newtag, tagOrId):
        """Add tag NEWTAG to all items ukijumuisha TAGORID."""
        self.addtag(newtag, 'withtag', tagOrId)

    eleza bbox(self, *args):
        """Return a tuple of X1,Y1,X2,Y2 coordinates kila a rectangle
        which encloses all items ukijumuisha tags specified kama arguments."""
        rudisha self._getints(
            self.tk.call((self._w, 'bbox') + args)) ama Tupu

    eleza tag_unbind(self, tagOrId, sequence, funcid=Tupu):
        """Unbind kila all items ukijumuisha TAGORID kila event SEQUENCE  the
        function identified ukijumuisha FUNCID."""
        self.tk.call(self._w, 'bind', tagOrId, sequence, '')
        ikiwa funcid:
            self.deletecommand(funcid)

    eleza tag_bind(self, tagOrId, sequence=Tupu, func=Tupu, add=Tupu):
        """Bind to all items ukijumuisha TAGORID at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function ama whether it will
        replace the previous function. See bind kila the rudisha value."""
        rudisha self._bind((self._w, 'bind', tagOrId),
                  sequence, func, add)

    eleza canvasx(self, screenx, gridspacing=Tupu):
        """Return the canvas x coordinate of pixel position SCREENX rounded
        to nearest multiple of GRIDSPACING units."""
        rudisha self.tk.getdouble(self.tk.call(
            self._w, 'canvasx', screenx, gridspacing))

    eleza canvasy(self, screeny, gridspacing=Tupu):
        """Return the canvas y coordinate of pixel position SCREENY rounded
        to nearest multiple of GRIDSPACING units."""
        rudisha self.tk.getdouble(self.tk.call(
            self._w, 'canvasy', screeny, gridspacing))

    eleza coords(self, *args):
        """Return a list of coordinates kila the item given kwenye ARGS."""
        # XXX Should use _flatten on args
        rudisha [self.tk.getdouble(x) kila x in
                           self.tk.splitlist(
                   self.tk.call((self._w, 'coords') + args))]

    eleza _create(self, itemType, args, kw): # Args: (val, val, ..., cnf={})
        """Internal function."""
        args = _flatten(args)
        cnf = args[-1]
        ikiwa isinstance(cnf, (dict, tuple)):
            args = args[:-1]
        isipokua:
            cnf = {}
        rudisha self.tk.getint(self.tk.call(
            self._w, 'create', itemType,
            *(args + self._options(cnf, kw))))

    eleza create_arc(self, *args, **kw):
        """Create arc shaped region ukijumuisha coordinates x1,y1,x2,y2."""
        rudisha self._create('arc', args, kw)

    eleza create_bitmap(self, *args, **kw):
        """Create bitmap ukijumuisha coordinates x1,y1."""
        rudisha self._create('bitmap', args, kw)

    eleza create_image(self, *args, **kw):
        """Create image item ukijumuisha coordinates x1,y1."""
        rudisha self._create('image', args, kw)

    eleza create_line(self, *args, **kw):
        """Create line ukijumuisha coordinates x1,y1,...,xn,yn."""
        rudisha self._create('line', args, kw)

    eleza create_oval(self, *args, **kw):
        """Create oval ukijumuisha coordinates x1,y1,x2,y2."""
        rudisha self._create('oval', args, kw)

    eleza create_polygon(self, *args, **kw):
        """Create polygon ukijumuisha coordinates x1,y1,...,xn,yn."""
        rudisha self._create('polygon', args, kw)

    eleza create_rectangle(self, *args, **kw):
        """Create rectangle ukijumuisha coordinates x1,y1,x2,y2."""
        rudisha self._create('rectangle', args, kw)

    eleza create_text(self, *args, **kw):
        """Create text ukijumuisha coordinates x1,y1."""
        rudisha self._create('text', args, kw)

    eleza create_window(self, *args, **kw):
        """Create window ukijumuisha coordinates x1,y1,x2,y2."""
        rudisha self._create('window', args, kw)

    eleza dchars(self, *args):
        """Delete characters of text items identified by tag ama id kwenye ARGS (possibly
        several times) kutoka FIRST to LAST character (including)."""
        self.tk.call((self._w, 'dchars') + args)

    eleza delete(self, *args):
        """Delete items identified by all tag ama ids contained kwenye ARGS."""
        self.tk.call((self._w, 'delete') + args)

    eleza dtag(self, *args):
        """Delete tag ama id given kama last arguments kwenye ARGS kutoka items
        identified by first argument kwenye ARGS."""
        self.tk.call((self._w, 'dtag') + args)

    eleza find(self, *args):
        """Internal function."""
        rudisha self._getints(
            self.tk.call((self._w, 'find') + args)) ama ()

    eleza find_above(self, tagOrId):
        """Return items above TAGORID."""
        rudisha self.find('above', tagOrId)

    eleza find_all(self):
        """Return all items."""
        rudisha self.find('all')

    eleza find_below(self, tagOrId):
        """Return all items below TAGORID."""
        rudisha self.find('below', tagOrId)

    eleza find_closest(self, x, y, halo=Tupu, start=Tupu):
        """Return item which ni closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closest). If START ni specified the next below this tag ni taken."""
        rudisha self.find('closest', x, y, halo, start)

    eleza find_enclosed(self, x1, y1, x2, y2):
        """Return all items kwenye rectangle defined
        by X1,Y1,X2,Y2."""
        rudisha self.find('enclosed', x1, y1, x2, y2)

    eleza find_overlapping(self, x1, y1, x2, y2):
        """Return all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        rudisha self.find('overlapping', x1, y1, x2, y2)

    eleza find_withtag(self, tagOrId):
        """Return all items ukijumuisha TAGORID."""
        rudisha self.find('withtag', tagOrId)

    eleza focus(self, *args):
        """Set focus to the first item specified kwenye ARGS."""
        rudisha self.tk.call((self._w, 'focus') + args)

    eleza gettags(self, *args):
        """Return tags associated ukijumuisha the first item specified kwenye ARGS."""
        rudisha self.tk.splitlist(
            self.tk.call((self._w, 'gettags') + args))

    eleza icursor(self, *args):
        """Set cursor at position POS kwenye the item identified by TAGORID.
        In ARGS TAGORID must be first."""
        self.tk.call((self._w, 'icursor') + args)

    eleza index(self, *args):
        """Return position of cursor kama integer kwenye item specified kwenye ARGS."""
        rudisha self.tk.getint(self.tk.call((self._w, 'index') + args))

    eleza insert(self, *args):
        """Insert TEXT kwenye item TAGORID at position POS. ARGS must
        be TAGORID POS TEXT."""
        self.tk.call((self._w, 'insert') + args)

    eleza itemcget(self, tagOrId, option):
        """Return the resource value kila an OPTION kila item TAGORID."""
        rudisha self.tk.call(
            (self._w, 'itemcget') + (tagOrId, '-'+option))

    eleza itemconfigure(self, tagOrId, cnf=Tupu, **kw):
        """Configure resources of an item TAGORID.

        The values kila resources are specified kama keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method without arguments.
        """
        rudisha self._configure(('itemconfigure', tagOrId), cnf, kw)

    itemconfig = itemconfigure

    # lower, tkraise/lift hide Misc.lower, Misc.tkraise/lift,
    # so the preferred name kila them ni tag_lower, tag_raise
    # (similar to tag_bind, na similar to the Text widget);
    # unfortunately can't delete the old ones yet (maybe kwenye 1.6)
    eleza tag_lower(self, *args):
        """Lower an item TAGORID given kwenye ARGS
        (optional below another item)."""
        self.tk.call((self._w, 'lower') + args)

    lower = tag_lower

    eleza move(self, *args):
        """Move an item TAGORID given kwenye ARGS."""
        self.tk.call((self._w, 'move') + args)

    eleza moveto(self, tagOrId, x='', y=''):
        """Move the items given by TAGORID kwenye the canvas coordinate
        space so that the first coordinate pair of the bottommost
        item ukijumuisha tag TAGORID ni located at position (X,Y).
        X na Y may be the empty string, kwenye which case the
        corresponding coordinate will be unchanged. All items matching
        TAGORID remain kwenye the same positions relative to each other."""
        self.tk.call(self._w, 'moveto', tagOrId, x, y)

    eleza postscript(self, cnf={}, **kw):
        """Print the contents of the canvas to a postscript
        file. Valid options: colormap, colormode, file, fontmap,
        height, pageanchor, pageheight, pagewidth, pagex, pagey,
        rotate, width, x, y."""
        rudisha self.tk.call((self._w, 'postscript') +
                    self._options(cnf, kw))

    eleza tag_raise(self, *args):
        """Raise an item TAGORID given kwenye ARGS
        (optional above another item)."""
        self.tk.call((self._w, 'raise') + args)

    lift = tkashiria = tag_raise

    eleza scale(self, *args):
        """Scale item TAGORID ukijumuisha XORIGIN, YORIGIN, XSCALE, YSCALE."""
        self.tk.call((self._w, 'scale') + args)

    eleza scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    eleza scan_dragto(self, x, y, gain=10):
        """Adjust the view of the canvas to GAIN times the
        difference between X na Y na the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y, gain)

    eleza select_adjust(self, tagOrId, index):
        """Adjust the end of the selection near the cursor of an item TAGORID to index."""
        self.tk.call(self._w, 'select', 'adjust', tagOrId, index)

    eleza select_clear(self):
        """Clear the selection ikiwa it ni kwenye this widget."""
        self.tk.call(self._w, 'select', 'clear')

    eleza select_from(self, tagOrId, index):
        """Set the fixed end of a selection kwenye item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'from', tagOrId, index)

    eleza select_item(self):
        """Return the item which has the selection."""
        rudisha self.tk.call(self._w, 'select', 'item') ama Tupu

    eleza select_to(self, tagOrId, index):
        """Set the variable end of a selection kwenye item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'to', tagOrId, index)

    eleza type(self, tagOrId):
        """Return the type of the item TAGORID."""
        rudisha self.tk.call(self._w, 'type', tagOrId) ama Tupu


kundi Checkbutton(Widget):
    """Checkbutton widget which ni either kwenye on- ama off-state."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a checkbutton widget ukijumuisha the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, offvalue, onvalue, padx, pady, relief,
        selectcolor, selectimage, state, takefocus, text, textvariable,
        underline, variable, width, wraplength."""
        Widget.__init__(self, master, 'checkbutton', cnf, kw)

    eleza deselect(self):
        """Put the button kwenye off-state."""
        self.tk.call(self._w, 'deselect')

    eleza flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')

    eleza invoke(self):
        """Toggle the button na invoke a command ikiwa given kama resource."""
        rudisha self.tk.call(self._w, 'invoke')

    eleza select(self):
        """Put the button kwenye on-state."""
        self.tk.call(self._w, 'select')

    eleza toggle(self):
        """Toggle the button."""
        self.tk.call(self._w, 'toggle')


kundi Entry(Widget, XView):
    """Entry widget which allows displaying simple text."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct an entry widget ukijumuisha the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, highlightbackground,
        highlightcolor, highlightthickness, insertbackground,
        insertborderwidth, insertofftime, insertontime, insertwidth,
        invalidcommand, invcmd, justify, relief, selectbackground,
        selectborderwidth, selectforeground, show, state, takefocus,
        textvariable, validate, validatecommand, vcmd, width,
        xscrollcommand."""
        Widget.__init__(self, master, 'entry', cnf, kw)

    eleza delete(self, first, last=Tupu):
        """Delete text kutoka FIRST to LAST (sio included)."""
        self.tk.call(self._w, 'delete', first, last)

    eleza get(self):
        """Return the text."""
        rudisha self.tk.call(self._w, 'get')

    eleza icursor(self, index):
        """Insert cursor at INDEX."""
        self.tk.call(self._w, 'icursor', index)

    eleza index(self, index):
        """Return position of cursor."""
        rudisha self.tk.getint(self.tk.call(
            self._w, 'index', index))

    eleza insert(self, index, string):
        """Insert STRING at INDEX."""
        self.tk.call(self._w, 'insert', index, string)

    eleza scan_mark(self, x):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x)

    eleza scan_dragto(self, x):
        """Adjust the view of the canvas to 10 times the
        difference between X na Y na the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x)

    eleza selection_adjust(self, index):
        """Adjust the end of the selection near the cursor to INDEX."""
        self.tk.call(self._w, 'selection', 'adjust', index)

    select_adjust = selection_adjust

    eleza selection_clear(self):
        """Clear the selection ikiwa it ni kwenye this widget."""
        self.tk.call(self._w, 'selection', 'clear')

    select_clear = selection_clear

    eleza selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'from', index)

    select_kutoka = selection_from

    eleza selection_present(self):
        """Return Kweli ikiwa there are characters selected kwenye the entry, Uongo
        otherwise."""
        rudisha self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))

    select_present = selection_present

    eleza selection_range(self, start, end):
        """Set the selection kutoka START to END (sio included)."""
        self.tk.call(self._w, 'selection', 'range', start, end)

    select_range = selection_range

    eleza selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'to', index)

    select_to = selection_to


kundi Frame(Widget):
    """Frame widget which may contain other widgets na can have a 3D border."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a frame widget ukijumuisha the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width."""
        cnf = _cnfmerge((cnf, kw))
        extra = ()
        ikiwa 'class_' kwenye cnf:
            extra = ('-class', cnf['class_'])
            toa cnf['class_']
        lasivyo 'class' kwenye cnf:
            extra = ('-class', cnf['class'])
            toa cnf['class']
        Widget.__init__(self, master, 'frame', cnf, {}, extra)


kundi Label(Widget):
    """Label widget which can display text na bitmaps."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a label widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            height, state, width

        """
        Widget.__init__(self, master, 'label', cnf, kw)


kundi Listbox(Widget, XView, YView):
    """Listbox widget which can display a list of strings."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a listbox widget ukijumuisha the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, height, highlightbackground,
        highlightcolor, highlightthickness, relief, selectbackground,
        selectborderwidth, selectforeground, selectmode, setgrid, takefocus,
        width, xscrollcommand, yscrollcommand, listvariable."""
        Widget.__init__(self, master, 'listbox', cnf, kw)

    eleza activate(self, index):
        """Activate item identified by INDEX."""
        self.tk.call(self._w, 'activate', index)

    eleza bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates kila a rectangle
        which encloses the item identified by the given index."""
        rudisha self._getints(self.tk.call(self._w, 'bbox', index)) ama Tupu

    eleza curselection(self):
        """Return the indices of currently selected item."""
        rudisha self._getints(self.tk.call(self._w, 'curselection')) ama ()

    eleza delete(self, first, last=Tupu):
        """Delete items kutoka FIRST to LAST (included)."""
        self.tk.call(self._w, 'delete', first, last)

    eleza get(self, first, last=Tupu):
        """Get list of items kutoka FIRST to LAST (included)."""
        ikiwa last ni sio Tupu:
            rudisha self.tk.splitlist(self.tk.call(
                self._w, 'get', first, last))
        isipokua:
            rudisha self.tk.call(self._w, 'get', first)

    eleza index(self, index):
        """Return index of item identified ukijumuisha INDEX."""
        i = self.tk.call(self._w, 'index', index)
        ikiwa i == 'none': rudisha Tupu
        rudisha self.tk.getint(i)

    eleza insert(self, index, *elements):
        """Insert ELEMENTS at INDEX."""
        self.tk.call((self._w, 'insert', index) + elements)

    eleza nearest(self, y):
        """Get index of item which ni nearest to y coordinate Y."""
        rudisha self.tk.getint(self.tk.call(
            self._w, 'nearest', y))

    eleza scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    eleza scan_dragto(self, x, y):
        """Adjust the view of the listbox to 10 times the
        difference between X na Y na the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)

    eleza see(self, index):
        """Scroll such that INDEX ni visible."""
        self.tk.call(self._w, 'see', index)

    eleza selection_anchor(self, index):
        """Set the fixed end oft the selection to INDEX."""
        self.tk.call(self._w, 'selection', 'anchor', index)

    select_anchor = selection_anchor

    eleza selection_clear(self, first, last=Tupu):
        """Clear the selection kutoka FIRST to LAST (included)."""
        self.tk.call(self._w,
                 'selection', 'clear', first, last)

    select_clear = selection_clear

    eleza selection_includes(self, index):
        """Return 1 ikiwa INDEX ni part of the selection."""
        rudisha self.tk.getboolean(self.tk.call(
            self._w, 'selection', 'includes', index))

    select_includes = selection_includes

    eleza selection_set(self, first, last=Tupu):
        """Set the selection kutoka FIRST to LAST (included) without
        changing the currently selected elements."""
        self.tk.call(self._w, 'selection', 'set', first, last)

    select_set = selection_set

    eleza size(self):
        """Return the number of elements kwenye the listbox."""
        rudisha self.tk.getint(self.tk.call(self._w, 'size'))

    eleza itemcget(self, index, option):
        """Return the resource value kila an ITEM na an OPTION."""
        rudisha self.tk.call(
            (self._w, 'itemcget') + (index, '-'+option))

    eleza itemconfigure(self, index, cnf=Tupu, **kw):
        """Configure resources of an ITEM.

        The values kila resources are specified kama keyword arguments.
        To get an overview about the allowed keyword arguments
        call the method without arguments.
        Valid resource names: background, bg, foreground, fg,
        selectbackground, selectforeground."""
        rudisha self._configure(('itemconfigure', index), cnf, kw)

    itemconfig = itemconfigure


kundi Menu(Widget):
    """Menu widget which allows displaying menu bars, pull-down menus na pop-up menus."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct menu widget ukijumuisha the parent MASTER.

        Valid resource names: activebackground, activeborderwidth,
        activeforeground, background, bd, bg, borderwidth, cursor,
        disabledforeground, fg, font, foreground, postcommand, relief,
        selectcolor, takefocus, tearoff, tearoffcommand, title, type."""
        Widget.__init__(self, master, 'menu', cnf, kw)

    eleza tk_popup(self, x, y, entry=""):
        """Post the menu at position X,Y ukijumuisha entry ENTRY."""
        self.tk.call('tk_popup', self._w, x, y, entry)

    eleza activate(self, index):
        """Activate entry at INDEX."""
        self.tk.call(self._w, 'activate', index)

    eleza add(self, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'add', itemType) +
                 self._options(cnf, kw))

    eleza add_cascade(self, cnf={}, **kw):
        """Add hierarchical menu item."""
        self.add('cascade', cnf ama kw)

    eleza add_checkbutton(self, cnf={}, **kw):
        """Add checkbutton menu item."""
        self.add('checkbutton', cnf ama kw)

    eleza add_command(self, cnf={}, **kw):
        """Add command menu item."""
        self.add('command', cnf ama kw)

    eleza add_radiobutton(self, cnf={}, **kw):
        """Addd radio menu item."""
        self.add('radiobutton', cnf ama kw)

    eleza add_separator(self, cnf={}, **kw):
        """Add separator."""
        self.add('separator', cnf ama kw)

    eleza insert(self, index, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'insert', index, itemType) +
                 self._options(cnf, kw))

    eleza insert_cascade(self, index, cnf={}, **kw):
        """Add hierarchical menu item at INDEX."""
        self.insert(index, 'cascade', cnf ama kw)

    eleza insert_checkbutton(self, index, cnf={}, **kw):
        """Add checkbutton menu item at INDEX."""
        self.insert(index, 'checkbutton', cnf ama kw)

    eleza insert_command(self, index, cnf={}, **kw):
        """Add command menu item at INDEX."""
        self.insert(index, 'command', cnf ama kw)

    eleza insert_radiobutton(self, index, cnf={}, **kw):
        """Addd radio menu item at INDEX."""
        self.insert(index, 'radiobutton', cnf ama kw)

    eleza insert_separator(self, index, cnf={}, **kw):
        """Add separator at INDEX."""
        self.insert(index, 'separator', cnf ama kw)

    eleza delete(self, index1, index2=Tupu):
        """Delete menu items between INDEX1 na INDEX2 (included)."""
        ikiwa index2 ni Tupu:
            index2 = index1

        num_index1, num_index2 = self.index(index1), self.index(index2)
        ikiwa (num_index1 ni Tupu) ama (num_index2 ni Tupu):
            num_index1, num_index2 = 0, -1

        kila i kwenye range(num_index1, num_index2 + 1):
            ikiwa 'command' kwenye self.entryconfig(i):
                c = str(self.entrycget(i, 'command'))
                ikiwa c:
                    self.deletecommand(c)
        self.tk.call(self._w, 'delete', index1, index2)

    eleza entrycget(self, index, option):
        """Return the resource value of a menu item kila OPTION at INDEX."""
        rudisha self.tk.call(self._w, 'entrycget', index, '-' + option)

    eleza entryconfigure(self, index, cnf=Tupu, **kw):
        """Configure a menu item at INDEX."""
        rudisha self._configure(('entryconfigure', index), cnf, kw)

    entryconfig = entryconfigure

    eleza index(self, index):
        """Return the index of a menu item identified by INDEX."""
        i = self.tk.call(self._w, 'index', index)
        ikiwa i == 'none': rudisha Tupu
        rudisha self.tk.getint(i)

    eleza invoke(self, index):
        """Invoke a menu item identified by INDEX na execute
        the associated command."""
        rudisha self.tk.call(self._w, 'invoke', index)

    eleza post(self, x, y):
        """Display a menu at position X,Y."""
        self.tk.call(self._w, 'post', x, y)

    eleza type(self, index):
        """Return the type of the menu item at INDEX."""
        rudisha self.tk.call(self._w, 'type', index)

    eleza unpost(self):
        """Unmap a menu."""
        self.tk.call(self._w, 'unpost')

    eleza xposition(self, index): # new kwenye Tk 8.5
        """Return the x-position of the leftmost pixel of the menu item
        at INDEX."""
        rudisha self.tk.getint(self.tk.call(self._w, 'xposition', index))

    eleza yposition(self, index):
        """Return the y-position of the topmost pixel of the menu item at INDEX."""
        rudisha self.tk.getint(self.tk.call(
            self._w, 'yposition', index))


kundi Menubutton(Widget):
    """Menubutton widget, obsolete since Tk8.0."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        Widget.__init__(self, master, 'menubutton', cnf, kw)


kundi Message(Widget):
    """Message widget to display multiline text. Obsolete since Label does it too."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        Widget.__init__(self, master, 'message', cnf, kw)


kundi Radiobutton(Widget):
    """Radiobutton widget which shows only one of several buttons kwenye on-state."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a radiobutton widget ukijumuisha the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, padx, pady, relief, selectcolor, selectimage,
        state, takefocus, text, textvariable, underline, value, variable,
        width, wraplength."""
        Widget.__init__(self, master, 'radiobutton', cnf, kw)

    eleza deselect(self):
        """Put the button kwenye off-state."""

        self.tk.call(self._w, 'deselect')

    eleza flash(self):
        """Flash the button."""
        self.tk.call(self._w, 'flash')

    eleza invoke(self):
        """Toggle the button na invoke a command ikiwa given kama resource."""
        rudisha self.tk.call(self._w, 'invoke')

    eleza select(self):
        """Put the button kwenye on-state."""
        self.tk.call(self._w, 'select')


kundi Scale(Widget):
    """Scale widget which can display a numerical scale."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a scale widget ukijumuisha the parent MASTER.

        Valid resource names: activebackground, background, bigincrement, bd,
        bg, borderwidth, command, cursor, digits, fg, font, foreground, from,
        highlightbackground, highlightcolor, highlightthickness, label,
        length, orient, relief, repeatdelay, repeatinterval, resolution,
        showvalue, sliderlength, sliderrelief, state, takefocus,
        tickinterval, to, troughcolor, variable, width."""
        Widget.__init__(self, master, 'scale', cnf, kw)

    eleza get(self):
        """Get the current value kama integer ama float."""
        value = self.tk.call(self._w, 'get')
        jaribu:
            rudisha self.tk.getint(value)
        tatizo (ValueError, TypeError, TclError):
            rudisha self.tk.getdouble(value)

    eleza set(self, value):
        """Set the value to VALUE."""
        self.tk.call(self._w, 'set', value)

    eleza coords(self, value=Tupu):
        """Return a tuple (X,Y) of the point along the centerline of the
        trough that corresponds to VALUE ama the current value ikiwa Tupu is
        given."""

        rudisha self._getints(self.tk.call(self._w, 'coords', value))

    eleza identify(self, x, y):
        """Return where the point X,Y lies. Valid rudisha values are "slider",
        "though1" na "though2"."""
        rudisha self.tk.call(self._w, 'identify', x, y)


kundi Scrollbar(Widget):
    """Scrollbar widget which displays a slider at a certain position."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a scrollbar widget ukijumuisha the parent MASTER.

        Valid resource names: activebackground, activerelief,
        background, bd, bg, borderwidth, command, cursor,
        elementborderwidth, highlightbackground,
        highlightcolor, highlightthickness, jump, orient,
        relief, repeatdelay, repeatinterval, takefocus,
        troughcolor, width."""
        Widget.__init__(self, master, 'scrollbar', cnf, kw)

    eleza activate(self, index=Tupu):
        """Marks the element indicated by index kama active.
        The only index values understood by this method are "arrow1",
        "slider", ama "arrow2".  If any other value ni specified then no
        element of the scrollbar will be active.  If index ni sio specified,
        the method returns the name of the element that ni currently active,
        ama Tupu ikiwa no element ni active."""
        rudisha self.tk.call(self._w, 'activate', index) ama Tupu

    eleza delta(self, deltax, deltay):
        """Return the fractional change of the scrollbar setting ikiwa it
        would be moved by DELTAX ama DELTAY pixels."""
        rudisha self.tk.getdouble(
            self.tk.call(self._w, 'delta', deltax, deltay))

    eleza fraction(self, x, y):
        """Return the fractional value which corresponds to a slider
        position of X,Y."""
        rudisha self.tk.getdouble(self.tk.call(self._w, 'fraction', x, y))

    eleza identify(self, x, y):
        """Return the element under position X,Y kama one of
        "arrow1","slider","arrow2" ama ""."""
        rudisha self.tk.call(self._w, 'identify', x, y)

    eleza get(self):
        """Return the current fractional values (upper na lower end)
        of the slider position."""
        rudisha self._getdoubles(self.tk.call(self._w, 'get'))

    eleza set(self, first, last):
        """Set the fractional values of the slider position (upper na
        lower ends kama value between 0 na 1)."""
        self.tk.call(self._w, 'set', first, last)


kundi Text(Widget, XView, YView):
    """Text widget which can display text kwenye various forms."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a text widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor,
            exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, padx, pady,
            relief, selectbackground,
            selectborderwidth, selectforeground,
            setgrid, takefocus,
            xscrollcommand, yscrollcommand,

        WIDGET-SPECIFIC OPTIONS

            autoseparators, height, maxundo,
            spacing1, spacing2, spacing3,
            state, tabs, undo, width, wrap,

        """
        Widget.__init__(self, master, 'text', cnf, kw)

    eleza bbox(self, index):
        """Return a tuple of (x,y,width,height) which gives the bounding
        box of the visible part of the character at the given index."""
        rudisha self._getints(
                self.tk.call(self._w, 'bbox', index)) ama Tupu

    eleza compare(self, index1, op, index2):
        """Return whether between index INDEX1 na index INDEX2 the
        relation OP ni satisfied. OP ni one of <, <=, ==, >=, >, ama !=."""
        rudisha self.tk.getboolean(self.tk.call(
            self._w, 'compare', index1, op, index2))

    eleza count(self, index1, index2, *args): # new kwenye Tk 8.5
        """Counts the number of relevant things between the two indices.
        If index1 ni after index2, the result will be a negative number
        (and this holds kila each of the possible options).

        The actual items which are counted depends on the options given by
        args. The result ni a list of integers, one kila the result of each
        counting option given. Valid counting options are "chars",
        "displaychars", "displayindices", "displaylines", "indices",
        "lines", "xpixels" na "ypixels". There ni an additional possible
        option "update", which ikiwa given then all subsequent options ensure
        that any possible out of date information ni recalculated."""
        args = ['-%s' % arg kila arg kwenye args ikiwa sio arg.startswith('-')]
        args += [index1, index2]
        res = self.tk.call(self._w, 'count', *args) ama Tupu
        ikiwa res ni sio Tupu na len(args) <= 3:
            rudisha (res, )
        isipokua:
            rudisha res

    eleza debug(self, boolean=Tupu):
        """Turn on the internal consistency checks of the B-Tree inside the text
        widget according to BOOLEAN."""
        ikiwa boolean ni Tupu:
            rudisha self.tk.getboolean(self.tk.call(self._w, 'debug'))
        self.tk.call(self._w, 'debug', boolean)

    eleza delete(self, index1, index2=Tupu):
        """Delete the characters between INDEX1 na INDEX2 (sio included)."""
        self.tk.call(self._w, 'delete', index1, index2)

    eleza dlineinfo(self, index):
        """Return tuple (x,y,width,height,baseline) giving the bounding box
        na baseline position of the visible part of the line containing
        the character at INDEX."""
        rudisha self._getints(self.tk.call(self._w, 'dlineinfo', index))

    eleza dump(self, index1, index2=Tupu, command=Tupu, **kw):
        """Return the contents of the widget between index1 na index2.

        The type of contents returned kwenye filtered based on the keyword
        parameters; ikiwa 'all', 'image', 'mark', 'tag', 'text', ama 'window' are
        given na true, then the corresponding items are returned. The result
        ni a list of triples of the form (key, value, index). If none of the
        keywords are true then 'all' ni used by default.

        If the 'command' argument ni given, it ni called once kila each element
        of the list of triples, ukijumuisha the values of each triple serving kama the
        arguments to the function. In this case the list ni sio returned."""
        args = []
        func_name = Tupu
        result = Tupu
        ikiwa sio command:
            # Never call the dump command without the -command flag, since the
            # output could involve Tcl quoting na would be a pain to parse
            # right. Instead just set the command to build a list of triples
            # kama ikiwa we had done the parsing.
            result = []
            eleza append_triple(key, value, index, result=result):
                result.append((key, value, index))
            command = append_triple
        jaribu:
            ikiwa sio isinstance(command, str):
                func_name = command = self._register(command)
            args += ["-command", command]
            kila key kwenye kw:
                ikiwa kw[key]: args.append("-" + key)
            args.append(index1)
            ikiwa index2:
                args.append(index2)
            self.tk.call(self._w, "dump", *args)
            rudisha result
        mwishowe:
            ikiwa func_name:
                self.deletecommand(func_name)

    ## new kwenye tk8.4
    eleza edit(self, *args):
        """Internal method

        This method controls the undo mechanism na
        the modified flag. The exact behavior of the
        command depends on the option argument that
        follows the edit argument. The following forms
        of the command are currently supported:

        edit_modified, edit_redo, edit_reset, edit_separator
        na edit_undo

        """
        rudisha self.tk.call(self._w, 'edit', *args)

    eleza edit_modified(self, arg=Tupu):
        """Get ama Set the modified flag

        If arg ni sio specified, returns the modified
        flag of the widget. The insert, delete, edit undo na
        edit redo commands ama the user can set ama clear the
        modified flag. If boolean ni specified, sets the
        modified flag of the widget to arg.
        """
        rudisha self.edit("modified", arg)

    eleza edit_redo(self):
        """Redo the last undone edit

        When the undo option ni true, reapplies the last
        undone edits provided no other edits were done since
        then. Generates an error when the redo stack ni empty.
        Does nothing when the undo option ni false.
        """
        rudisha self.edit("redo")

    eleza edit_reset(self):
        """Clears the undo na redo stacks
        """
        rudisha self.edit("reset")

    eleza edit_separator(self):
        """Inserts a separator (boundary) on the undo stack.

        Does nothing when the undo option ni false
        """
        rudisha self.edit("separator")

    eleza edit_undo(self):
        """Undoes the last edit action

        If the undo option ni true. An edit action ni defined
        kama all the insert na delete commands that are recorded
        on the undo stack kwenye between two separators. Generates
        an error when the undo stack ni empty. Does nothing
        when the undo option ni false
        """
        rudisha self.edit("undo")

    eleza get(self, index1, index2=Tupu):
        """Return the text kutoka INDEX1 to INDEX2 (sio included)."""
        rudisha self.tk.call(self._w, 'get', index1, index2)
    # (Image commands are new kwenye 8.0)

    eleza image_cget(self, index, option):
        """Return the value of OPTION of an embedded image at INDEX."""
        ikiwa option[:1] != "-":
            option = "-" + option
        ikiwa option[-1:] == "_":
            option = option[:-1]
        rudisha self.tk.call(self._w, "image", "cget", index, option)

    eleza image_configure(self, index, cnf=Tupu, **kw):
        """Configure an embedded image at INDEX."""
        rudisha self._configure(('image', 'configure', index), cnf, kw)

    eleza image_create(self, index, cnf={}, **kw):
        """Create an embedded image at INDEX."""
        rudisha self.tk.call(
                 self._w, "image", "create", index,
                 *self._options(cnf, kw))

    eleza image_names(self):
        """Return all names of embedded images kwenye this widget."""
        rudisha self.tk.call(self._w, "image", "names")

    eleza index(self, index):
        """Return the index kwenye the form line.char kila INDEX."""
        rudisha str(self.tk.call(self._w, 'index', index))

    eleza insert(self, index, chars, *args):
        """Insert CHARS before the characters at INDEX. An additional
        tag can be given kwenye ARGS. Additional CHARS na tags can follow kwenye ARGS."""
        self.tk.call((self._w, 'insert', index, chars) + args)

    eleza mark_gravity(self, markName, direction=Tupu):
        """Change the gravity of a mark MARKNAME to DIRECTION (LEFT ama RIGHT).
        Return the current value ikiwa Tupu ni given kila DIRECTION."""
        rudisha self.tk.call(
            (self._w, 'mark', 'gravity', markName, direction))

    eleza mark_names(self):
        """Return all mark names."""
        rudisha self.tk.splitlist(self.tk.call(
            self._w, 'mark', 'names'))

    eleza mark_set(self, markName, index):
        """Set mark MARKNAME before the character at INDEX."""
        self.tk.call(self._w, 'mark', 'set', markName, index)

    eleza mark_unset(self, *markNames):
        """Delete all marks kwenye MARKNAMES."""
        self.tk.call((self._w, 'mark', 'unset') + markNames)

    eleza mark_next(self, index):
        """Return the name of the next mark after INDEX."""
        rudisha self.tk.call(self._w, 'mark', 'next', index) ama Tupu

    eleza mark_previous(self, index):
        """Return the name of the previous mark before INDEX."""
        rudisha self.tk.call(self._w, 'mark', 'previous', index) ama Tupu

    eleza peer_create(self, newPathName, cnf={}, **kw): # new kwenye Tk 8.5
        """Creates a peer text widget ukijumuisha the given newPathName, na any
        optional standard configuration options. By default the peer will
        have the same start na end line kama the parent widget, but
        these can be overridden ukijumuisha the standard configuration options."""
        self.tk.call(self._w, 'peer', 'create', newPathName,
            *self._options(cnf, kw))

    eleza peer_names(self): # new kwenye Tk 8.5
        """Returns a list of peers of this widget (this does sio include
        the widget itself)."""
        rudisha self.tk.splitlist(self.tk.call(self._w, 'peer', 'names'))

    eleza replace(self, index1, index2, chars, *args): # new kwenye Tk 8.5
        """Replaces the range of characters between index1 na index2 with
        the given characters na tags specified by args.

        See the method insert kila some more information about args, na the
        method delete kila information about the indices."""
        self.tk.call(self._w, 'replace', index1, index2, chars, *args)

    eleza scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    eleza scan_dragto(self, x, y):
        """Adjust the view of the text to 10 times the
        difference between X na Y na the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)

    eleza search(self, pattern, index, stopindex=Tupu,
           forwards=Tupu, backwards=Tupu, exact=Tupu,
           regexp=Tupu, nocase=Tupu, count=Tupu, elide=Tupu):
        """Search PATTERN beginning kutoka INDEX until STOPINDEX.
        Return the index of the first character of a match ama an
        empty string."""
        args = [self._w, 'search']
        ikiwa forwards: args.append('-forwards')
        ikiwa backwards: args.append('-backwards')
        ikiwa exact: args.append('-exact')
        ikiwa regexp: args.append('-regexp')
        ikiwa nocase: args.append('-nocase')
        ikiwa elide: args.append('-elide')
        ikiwa count: args.append('-count'); args.append(count)
        ikiwa pattern na pattern[0] == '-': args.append('--')
        args.append(pattern)
        args.append(index)
        ikiwa stopindex: args.append(stopindex)
        rudisha str(self.tk.call(tuple(args)))

    eleza see(self, index):
        """Scroll such that the character at INDEX ni visible."""
        self.tk.call(self._w, 'see', index)

    eleza tag_add(self, tagName, index1, *args):
        """Add tag TAGNAME to all characters between INDEX1 na index2 kwenye ARGS.
        Additional pairs of indices may follow kwenye ARGS."""
        self.tk.call(
            (self._w, 'tag', 'add', tagName, index1) + args)

    eleza tag_unbind(self, tagName, sequence, funcid=Tupu):
        """Unbind kila all characters ukijumuisha TAGNAME kila event SEQUENCE  the
        function identified ukijumuisha FUNCID."""
        self.tk.call(self._w, 'tag', 'bind', tagName, sequence, '')
        ikiwa funcid:
            self.deletecommand(funcid)

    eleza tag_bind(self, tagName, sequence, func, add=Tupu):
        """Bind to all characters ukijumuisha TAGNAME at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function ama whether it will
        replace the previous function. See bind kila the rudisha value."""
        rudisha self._bind((self._w, 'tag', 'bind', tagName),
                  sequence, func, add)

    eleza tag_cget(self, tagName, option):
        """Return the value of OPTION kila tag TAGNAME."""
        ikiwa option[:1] != '-':
            option = '-' + option
        ikiwa option[-1:] == '_':
            option = option[:-1]
        rudisha self.tk.call(self._w, 'tag', 'cget', tagName, option)

    eleza tag_configure(self, tagName, cnf=Tupu, **kw):
        """Configure a tag TAGNAME."""
        rudisha self._configure(('tag', 'configure', tagName), cnf, kw)

    tag_config = tag_configure

    eleza tag_delete(self, *tagNames):
        """Delete all tags kwenye TAGNAMES."""
        self.tk.call((self._w, 'tag', 'delete') + tagNames)

    eleza tag_lower(self, tagName, belowThis=Tupu):
        """Change the priority of tag TAGNAME such that it ni lower
        than the priority of BELOWTHIS."""
        self.tk.call(self._w, 'tag', 'lower', tagName, belowThis)

    eleza tag_names(self, index=Tupu):
        """Return a list of all tag names."""
        rudisha self.tk.splitlist(
            self.tk.call(self._w, 'tag', 'names', index))

    eleza tag_nextrange(self, tagName, index1, index2=Tupu):
        """Return a list of start na end index kila the first sequence of
        characters between INDEX1 na INDEX2 which all have tag TAGNAME.
        The text ni searched forward kutoka INDEX1."""
        rudisha self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'nextrange', tagName, index1, index2))

    eleza tag_prevrange(self, tagName, index1, index2=Tupu):
        """Return a list of start na end index kila the first sequence of
        characters between INDEX1 na INDEX2 which all have tag TAGNAME.
        The text ni searched backwards kutoka INDEX1."""
        rudisha self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'prevrange', tagName, index1, index2))

    eleza tag_raise(self, tagName, aboveThis=Tupu):
        """Change the priority of tag TAGNAME such that it ni higher
        than the priority of ABOVETHIS."""
        self.tk.call(
            self._w, 'tag', 'raise', tagName, aboveThis)

    eleza tag_ranges(self, tagName):
        """Return a list of ranges of text which have tag TAGNAME."""
        rudisha self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'ranges', tagName))

    eleza tag_remove(self, tagName, index1, index2=Tupu):
        """Remove tag TAGNAME kutoka all characters between INDEX1 na INDEX2."""
        self.tk.call(
            self._w, 'tag', 'remove', tagName, index1, index2)

    eleza window_cget(self, index, option):
        """Return the value of OPTION of an embedded window at INDEX."""
        ikiwa option[:1] != '-':
            option = '-' + option
        ikiwa option[-1:] == '_':
            option = option[:-1]
        rudisha self.tk.call(self._w, 'window', 'cget', index, option)

    eleza window_configure(self, index, cnf=Tupu, **kw):
        """Configure an embedded window at INDEX."""
        rudisha self._configure(('window', 'configure', index), cnf, kw)

    window_config = window_configure

    eleza window_create(self, index, cnf={}, **kw):
        """Create a window at INDEX."""
        self.tk.call(
              (self._w, 'window', 'create', index)
              + self._options(cnf, kw))

    eleza window_names(self):
        """Return all names of embedded windows kwenye this widget."""
        rudisha self.tk.splitlist(
            self.tk.call(self._w, 'window', 'names'))

    eleza yview_pickplace(self, *what):
        """Obsolete function, use see."""
        self.tk.call((self._w, 'yview', '-pickplace') + what)


kundi _setit:
    """Internal class. It wraps the command kwenye the widget OptionMenu."""

    eleza __init__(self, var, value, callback=Tupu):
        self.__value = value
        self.__var = var
        self.__callback = callback

    eleza __call__(self, *args):
        self.__var.set(self.__value)
        ikiwa self.__callback:
            self.__callback(self.__value, *args)


kundi OptionMenu(Menubutton):
    """OptionMenu which allows the user to select a value kutoka a menu."""

    eleza __init__(self, master, variable, value, *values, **kwargs):
        """Construct an optionmenu widget ukijumuisha the parent MASTER, with
        the resource textvariable set to VARIABLE, the initially selected
        value VALUE, the other menu values VALUES na an additional
        keyword argument command."""
        kw = {"borderwidth": 2, "textvariable": variable,
              "indicatoron": 1, "relief": RAISED, "anchor": "c",
              "highlightthickness": 2}
        Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = Menu(self, name="menu", tearoff=0)
        self.menuname = menu._w
        # 'command' ni the only supported keyword
        callback = kwargs.get('command')
        ikiwa 'command' kwenye kwargs:
            toa kwargs['command']
        ikiwa kwargs:
            ashiria TclError('unknown option -'+kwargs.keys()[0])
        menu.add_command(label=value,
                 command=_setit(variable, value, callback))
        kila v kwenye values:
            menu.add_command(label=v,
                     command=_setit(variable, v, callback))
        self["menu"] = menu

    eleza __getitem__(self, name):
        ikiwa name == 'menu':
            rudisha self.__menu
        rudisha Widget.__getitem__(self, name)

    eleza destroy(self):
        """Destroy this widget na the associated menu."""
        Menubutton.destroy(self)
        self.__menu = Tupu


kundi Image:
    """Base kundi kila images."""
    _last_id = 0

    eleza __init__(self, imgtype, name=Tupu, cnf={}, master=Tupu, **kw):
        self.name = Tupu
        ikiwa sio master:
            master = _default_root
            ikiwa sio master:
                ashiria RuntimeError('Too early to create image')
        self.tk = getattr(master, 'tk', master)
        ikiwa sio name:
            Image._last_id += 1
            name = "pyimage%r" % (Image._last_id,) # tk itself would use image<x>
        ikiwa kw na cnf: cnf = _cnfmerge((cnf, kw))
        lasivyo kw: cnf = kw
        options = ()
        kila k, v kwenye cnf.items():
            ikiwa callable(v):
                v = self._register(v)
            options = options + ('-'+k, v)
        self.tk.call(('image', 'create', imgtype, name,) + options)
        self.name = name

    eleza __str__(self): rudisha self.name

    eleza __del__(self):
        ikiwa self.name:
            jaribu:
                self.tk.call('image', 'delete', self.name)
            tatizo TclError:
                # May happen ikiwa the root was destroyed
                pita

    eleza __setitem__(self, key, value):
        self.tk.call(self.name, 'configure', '-'+key, value)

    eleza __getitem__(self, key):
        rudisha self.tk.call(self.name, 'configure', '-'+key)

    eleza configure(self, **kw):
        """Configure the image."""
        res = ()
        kila k, v kwenye _cnfmerge(kw).items():
            ikiwa v ni sio Tupu:
                ikiwa k[-1] == '_': k = k[:-1]
                ikiwa callable(v):
                    v = self._register(v)
                res = res + ('-'+k, v)
        self.tk.call((self.name, 'config') + res)

    config = configure

    eleza height(self):
        """Return the height of the image."""
        rudisha self.tk.getint(
            self.tk.call('image', 'height', self.name))

    eleza type(self):
        """Return the type of the image, e.g. "photo" ama "bitmap"."""
        rudisha self.tk.call('image', 'type', self.name)

    eleza width(self):
        """Return the width of the image."""
        rudisha self.tk.getint(
            self.tk.call('image', 'width', self.name))


kundi PhotoImage(Image):
    """Widget which can display images kwenye PGM, PPM, GIF, PNG format."""

    eleza __init__(self, name=Tupu, cnf={}, master=Tupu, **kw):
        """Create an image ukijumuisha NAME.

        Valid resource names: data, format, file, gamma, height, palette,
        width."""
        Image.__init__(self, 'photo', name, cnf, master, **kw)

    eleza blank(self):
        """Display a transparent image."""
        self.tk.call(self.name, 'blank')

    eleza cget(self, option):
        """Return the value of OPTION."""
        rudisha self.tk.call(self.name, 'cget', '-' + option)
    # XXX config

    eleza __getitem__(self, key):
        rudisha self.tk.call(self.name, 'cget', '-' + key)
    # XXX copy -from, -to, ...?

    eleza copy(self):
        """Return a new PhotoImage ukijumuisha the same image kama this widget."""
        destImage = PhotoImage(master=self.tk)
        self.tk.call(destImage, 'copy', self.name)
        rudisha destImage

    eleza zoom(self, x, y=''):
        """Return a new PhotoImage ukijumuisha the same image kama this widget
        but zoom it ukijumuisha a factor of x kwenye the X direction na y kwenye the Y
        direction.  If y ni sio given, the default value ni the same kama x.
        """
        destImage = PhotoImage(master=self.tk)
        ikiwa y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-zoom',x,y)
        rudisha destImage

    eleza subsample(self, x, y=''):
        """Return a new PhotoImage based on the same image kama this widget
        but use only every Xth ama Yth pixel.  If y ni sio given, the
        default value ni the same kama x.
        """
        destImage = PhotoImage(master=self.tk)
        ikiwa y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-subsample',x,y)
        rudisha destImage

    eleza get(self, x, y):
        """Return the color (red, green, blue) of the pixel at X,Y."""
        rudisha self.tk.call(self.name, 'get', x, y)

    eleza put(self, data, to=Tupu):
        """Put row formatted colors to image starting from
        position TO, e.g. image.put("{red green} {blue yellow}", to=(4,6))"""
        args = (self.name, 'put', data)
        ikiwa to:
            ikiwa to[0] == '-to':
                to = to[1:]
            args = args + ('-to',) + tuple(to)
        self.tk.call(args)
    # XXX read

    eleza write(self, filename, format=Tupu, from_coords=Tupu):
        """Write image to file FILENAME kwenye FORMAT starting from
        position FROM_COORDS."""
        args = (self.name, 'write', filename)
        ikiwa format:
            args = args + ('-format', format)
        ikiwa from_coords:
            args = args + ('-from',) + tuple(from_coords)
        self.tk.call(args)

    eleza transparency_get(self, x, y):
        """Return Kweli ikiwa the pixel at x,y ni transparent."""
        rudisha self.tk.getboolean(self.tk.call(
            self.name, 'transparency', 'get', x, y))

    eleza transparency_set(self, x, y, boolean):
        """Set the transparency of the pixel at x,y."""
        self.tk.call(self.name, 'transparency', 'set', x, y, boolean)


kundi BitmapImage(Image):
    """Widget which can display images kwenye XBM format."""

    eleza __init__(self, name=Tupu, cnf={}, master=Tupu, **kw):
        """Create a bitmap ukijumuisha NAME.

        Valid resource names: background, data, file, foreground, maskdata, maskfile."""
        Image.__init__(self, 'bitmap', name, cnf, master, **kw)


eleza image_names():
    rudisha _default_root.tk.splitlist(_default_root.tk.call('image', 'names'))


eleza image_types():
    rudisha _default_root.tk.splitlist(_default_root.tk.call('image', 'types'))


kundi Spinbox(Widget, XView):
    """spinbox widget."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a spinbox widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            activebackground, background, borderwidth,
            cursor, exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, justify, relief,
            repeatdelay, repeatinterval,
            selectbackground, selectborderwidth
            selectforeground, takefocus, textvariable
            xscrollcommand.

        WIDGET-SPECIFIC OPTIONS

            buttonbackground, buttoncursor,
            buttondownrelief, buttonuprelief,
            command, disabledbackground,
            disabledforeground, format, from,
            invalidcommand, increment,
            readonlybackground, state, to,
            validate, validatecommand values,
            width, wrap,
        """
        Widget.__init__(self, master, 'spinbox', cnf, kw)

    eleza bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates kila a
        rectangle which encloses the character given by index.

        The first two elements of the list give the x na y
        coordinates of the upper-left corner of the screen
        area covered by the character (in pixels relative
        to the widget) na the last two elements give the
        width na height of the character, kwenye pixels. The
        bounding box may refer to a region outside the
        visible area of the window.
        """
        rudisha self._getints(self.tk.call(self._w, 'bbox', index)) ama Tupu

    eleza delete(self, first, last=Tupu):
        """Delete one ama more elements of the spinbox.

        First ni the index of the first character to delete,
        na last ni the index of the character just after
        the last one to delete. If last isn't specified it
        defaults to first+1, i.e. a single character is
        deleted.  This command returns an empty string.
        """
        rudisha self.tk.call(self._w, 'delete', first, last)

    eleza get(self):
        """Returns the spinbox's string"""
        rudisha self.tk.call(self._w, 'get')

    eleza icursor(self, index):
        """Alter the position of the insertion cursor.

        The insertion cursor will be displayed just before
        the character given by index. Returns an empty string
        """
        rudisha self.tk.call(self._w, 'icursor', index)

    eleza identify(self, x, y):
        """Returns the name of the widget at position x, y

        Return value ni one of: none, buttondown, buttonup, entry
        """
        rudisha self.tk.call(self._w, 'identify', x, y)

    eleza index(self, index):
        """Returns the numerical index corresponding to index
        """
        rudisha self.tk.call(self._w, 'index', index)

    eleza insert(self, index, s):
        """Insert string s at index

         Returns an empty string.
        """
        rudisha self.tk.call(self._w, 'insert', index, s)

    eleza invoke(self, element):
        """Causes the specified element to be invoked

        The element could be buttondown ama buttonup
        triggering the action associated ukijumuisha it.
        """
        rudisha self.tk.call(self._w, 'invoke', element)

    eleza scan(self, *args):
        """Internal function."""
        rudisha self._getints(
            self.tk.call((self._w, 'scan') + args)) ama ()

    eleza scan_mark(self, x):
        """Records x na the current view kwenye the spinbox window;

        used kwenye conjunction ukijumuisha later scan dragto commands.
        Typically this command ni associated ukijumuisha a mouse button
        press kwenye the widget. It returns an empty string.
        """
        rudisha self.scan("mark", x)

    eleza scan_dragto(self, x):
        """Compute the difference between the given x argument
        na the x argument to the last scan mark command

        It then adjusts the view left ama right by 10 times the
        difference kwenye x-coordinates. This command ni typically
        associated ukijumuisha mouse motion events kwenye the widget, to
        produce the effect of dragging the spinbox at high speed
        through the window. The rudisha value ni an empty string.
        """
        rudisha self.scan("dragto", x)

    eleza selection(self, *args):
        """Internal function."""
        rudisha self._getints(
            self.tk.call((self._w, 'selection') + args)) ama ()

    eleza selection_adjust(self, index):
        """Locate the end of the selection nearest to the character
        given by index,

        Then adjust that end of the selection to be at index
        (i.e including but sio going beyond index). The other
        end of the selection ni made the anchor point kila future
        select to commands. If the selection isn't currently in
        the spinbox, then a new selection ni created to include
        the characters between index na the most recent selection
        anchor point, inclusive.
        """
        rudisha self.selection("adjust", index)

    eleza selection_clear(self):
        """Clear the selection

        If the selection isn't kwenye this widget then the
        command has no effect.
        """
        rudisha self.selection("clear")

    eleza selection_element(self, element=Tupu):
        """Sets ama gets the currently selected element.

        If a spinbutton element ni specified, it will be
        displayed depressed.
        """
        rudisha self.tk.call(self._w, 'selection', 'element', element)

    eleza selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.selection('from', index)

    eleza selection_present(self):
        """Return Kweli ikiwa there are characters selected kwenye the spinbox, Uongo
        otherwise."""
        rudisha self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))

    eleza selection_range(self, start, end):
        """Set the selection kutoka START to END (sio included)."""
        self.selection('range', start, end)

    eleza selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.selection('to', index)

###########################################################################


kundi LabelFrame(Widget):
    """labelframe widget."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a labelframe widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            borderwidth, cursor, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, padx, pady, relief,
            takefocus, text

        WIDGET-SPECIFIC OPTIONS

            background, class, colormap, container,
            height, labelanchor, labelwidget,
            visual, width
        """
        Widget.__init__(self, master, 'labelframe', cnf, kw)

########################################################################


kundi PanedWindow(Widget):
    """panedwindow widget."""

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        """Construct a panedwindow widget ukijumuisha the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor, height,
            orient, relief, width

        WIDGET-SPECIFIC OPTIONS

            handlepad, handlesize, opaqueresize,
            sashcursor, sashpad, sashrelief,
            sashwidth, showhandle,
        """
        Widget.__init__(self, master, 'panedwindow', cnf, kw)

    eleza add(self, child, **kw):
        """Add a child widget to the panedwindow kwenye a new pane.

        The child argument ni the name of the child widget
        followed by pairs of arguments that specify how to
        manage the windows. The possible options na values
        are the ones accepted by the paneconfigure method.
        """
        self.tk.call((self._w, 'add', child) + self._options(kw))

    eleza remove(self, child):
        """Remove the pane containing child kutoka the panedwindow

        All geometry management options kila child will be forgotten.
        """
        self.tk.call(self._w, 'forget', child)

    forget = remove

    eleza identify(self, x, y):
        """Identify the panedwindow component at point x, y

        If the point ni over a sash ama a sash handle, the result
        ni a two element list containing the index of the sash ama
        handle, na a word indicating whether it ni over a sash
        ama a handle, such kama {0 sash} ama {2 handle}. If the point
        ni over any other part of the panedwindow, the result is
        an empty list.
        """
        rudisha self.tk.call(self._w, 'identify', x, y)

    eleza proxy(self, *args):
        """Internal function."""
        rudisha self._getints(
            self.tk.call((self._w, 'proxy') + args)) ama ()

    eleza proxy_coord(self):
        """Return the x na y pair of the most recent proxy location
        """
        rudisha self.proxy("coord")

    eleza proxy_forget(self):
        """Remove the proxy kutoka the display.
        """
        rudisha self.proxy("forget")

    eleza proxy_place(self, x, y):
        """Place the proxy at the given x na y coordinates.
        """
        rudisha self.proxy("place", x, y)

    eleza sash(self, *args):
        """Internal function."""
        rudisha self._getints(
            self.tk.call((self._w, 'sash') + args)) ama ()

    eleza sash_coord(self, index):
        """Return the current x na y pair kila the sash given by index.

        Index must be an integer between 0 na 1 less than the
        number of panes kwenye the panedwindow. The coordinates given are
        those of the top left corner of the region containing the sash.
        pathName sash dragto index x y This command computes the
        difference between the given coordinates na the coordinates
        given to the last sash coord command kila the given sash. It then
        moves that sash the computed difference. The rudisha value ni the
        empty string.
        """
        rudisha self.sash("coord", index)

    eleza sash_mark(self, index):
        """Records x na y kila the sash given by index;

        Used kwenye conjunction ukijumuisha later dragto commands to move the sash.
        """
        rudisha self.sash("mark", index)

    eleza sash_place(self, index, x, y):
        """Place the sash given by index at the given coordinates
        """
        rudisha self.sash("place", index, x, y)

    eleza panecget(self, child, option):
        """Query a management option kila window.

        Option may be any value allowed by the paneconfigure subcommand
        """
        rudisha self.tk.call(
            (self._w, 'panecget') + (child, '-'+option))

    eleza paneconfigure(self, tagOrId, cnf=Tupu, **kw):
        """Query ama modify the management options kila window.

        If no option ni specified, returns a list describing all
        of the available options kila pathName.  If option is
        specified ukijumuisha no value, then the command returns a list
        describing the one named option (this list will be identical
        to the corresponding sublist of the value returned ikiwa no
        option ni specified). If one ama more option-value pairs are
        specified, then the command modifies the given widget
        option(s) to have the given value(s); kwenye this case the
        command returns an empty string. The following options
        are supported:

        after window
            Insert the window after the window specified. window
            should be the name of a window already managed by pathName.
        before window
            Insert the window before the window specified. window
            should be the name of a window already managed by pathName.
        height size
            Specify a height kila the window. The height will be the
            outer dimension of the window including its border, if
            any. If size ni an empty string, ama ikiwa -height ni not
            specified, then the height requested internally by the
            window will be used initially; the height may later be
            adjusted by the movement of sashes kwenye the panedwindow.
            Size may be any value accepted by Tk_GetPixels.
        minsize n
            Specifies that the size of the window cannot be made
            less than n. This constraint only affects the size of
            the widget kwenye the paned dimension -- the x dimension
            kila horizontal panedwindows, the y dimension for
            vertical panedwindows. May be any value accepted by
            Tk_GetPixels.
        padx n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window in
            the X-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        pady n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window in
            the Y-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        sticky style
            If a window's pane ni larger than the requested
            dimensions of the window, this option may be used
            to position (or stretch) the window within its pane.
            Style ni a string that contains zero ama more of the
            characters n, s, e ama w. The string can optionally
            contains spaces ama commas, but they are ignored. Each
            letter refers to a side (north, south, east, ama west)
            that the window will "stick" to. If both n na s
            (or e na w) are specified, the window will be
            stretched to fill the entire height (or width) of
            its cavity.
        width size
            Specify a width kila the window. The width will be
            the outer dimension of the window including its
            border, ikiwa any. If size ni an empty string, ama
            ikiwa -width ni sio specified, then the width requested
            internally by the window will be used initially; the
            width may later be adjusted by the movement of sashes
            kwenye the panedwindow. Size may be any value accepted by
            Tk_GetPixels.

        """
        ikiwa cnf ni Tupu na sio kw:
            rudisha self._getconfigure(self._w, 'paneconfigure', tagOrId)
        ikiwa isinstance(cnf, str) na sio kw:
            rudisha self._getconfigure1(
                self._w, 'paneconfigure', tagOrId, '-'+cnf)
        self.tk.call((self._w, 'paneconfigure', tagOrId) +
                 self._options(cnf, kw))

    paneconfig = paneconfigure

    eleza panes(self):
        """Returns an ordered list of the child panes."""
        rudisha self.tk.splitlist(self.tk.call(self._w, 'panes'))

# Test:


eleza _test():
    root = Tk()
    text = "This ni Tcl/Tk version %s" % TclVersion
    text += "\nThis should be a cedilla: \xe7"
    label = Label(root, text=text)
    label.pack()
    test = Button(root, text="Click me!",
              command=lambda root=root: root.test.configure(
                  text="[%s]" % root.test['text']))
    test.pack()
    root.test = test
    quit = Button(root, text="QUIT", command=root.destroy)
    quit.pack()
    # The following three commands are needed so the window pops
    # up on top on Windows...
    root.iconify()
    root.update()
    root.deiconify()
    root.mainloop()


ikiwa __name__ == '__main__':
    _test()
