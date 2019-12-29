"""Pop up a reminder of how to call a function.

Call Tips are floating windows which display function, class, na method
parameter na docstring information when you type an opening parenthesis, and
which disappear when you type a closing parenthesis.
"""
agiza __main__
agiza inspect
agiza re
agiza sys
agiza textwrap
agiza types

kutoka idlelib agiza calltip_w
kutoka idlelib.hyperparser agiza HyperParser


kundi Calltip:

    eleza __init__(self, editwin=Tupu):
        ikiwa editwin ni Tupu:  # subprocess na test
            self.editwin = Tupu
        isipokua:
            self.editwin = editwin
            self.text = editwin.text
            self.active_calltip = Tupu
            self._calltip_window = self._make_tk_calltip_window

    eleza close(self):
        self._calltip_window = Tupu

    eleza _make_tk_calltip_window(self):
        # See __init__ kila usage
        rudisha calltip_w.CalltipWindow(self.text)

    eleza _remove_calltip_window(self, event=Tupu):
        ikiwa self.active_calltip:
            self.active_calltip.hidetip()
            self.active_calltip = Tupu

    eleza force_open_calltip_event(self, event):
        "The user selected the menu entry ama hotkey, open the tip."
        self.open_calltip(Kweli)
        rudisha "koma"

    eleza try_open_calltip_event(self, event):
        """Happens when it would be nice to open a calltip, but sio really
        necessary, kila example after an opening bracket, so function calls
        won't be made.
        """
        self.open_calltip(Uongo)

    eleza refresh_calltip_event(self, event):
        ikiwa self.active_calltip na self.active_calltip.tipwindow:
            self.open_calltip(Uongo)

    eleza open_calltip(self, evalfuncs):
        self._remove_calltip_window()

        hp = HyperParser(self.editwin, "insert")
        sur_paren = hp.get_surrounding_brackets('(')
        ikiwa sio sur_paren:
            rudisha
        hp.set_index(sur_paren[0])
        expression  = hp.get_expression()
        ikiwa sio expression:
            rudisha
        ikiwa sio evalfuncs na (expression.find('(') != -1):
            rudisha
        argspec = self.fetch_tip(expression)
        ikiwa sio argspec:
            rudisha
        self.active_calltip = self._calltip_window()
        self.active_calltip.showtip(argspec, sur_paren[0], sur_paren[1])

    eleza fetch_tip(self, expression):
        """Return the argument list na docstring of a function ama class.

        If there ni a Python subprocess, get the calltip there.  Otherwise,
        either this fetch_tip() ni running kwenye the subprocess ama it was
        called kwenye an IDLE running without the subprocess.

        The subprocess environment ni that of the most recently run script.  If
        two unrelated modules are being edited some calltips kwenye the current
        module may be inoperative ikiwa the module was sio the last to run.

        To find methods, fetch_tip must be fed a fully qualified name.

        """
        jaribu:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        tatizo AttributeError:
            rpcclt = Tupu
        ikiwa rpcclt:
            rudisha rpcclt.remotecall("exec", "get_the_calltip",
                                     (expression,), {})
        isipokua:
            rudisha get_argspec(get_entity(expression))


eleza get_entity(expression):
    """Return the object corresponding to expression evaluated
    kwenye a namespace spanning sys.modules na __main.dict__.
    """
    ikiwa expression:
        namespace = {**sys.modules, **__main__.__dict__}
        jaribu:
            rudisha eval(expression, namespace)  # Only protect user code.
        tatizo BaseException:
            # An uncaught exception closes idle, na eval can ashiria any
            # exception, especially ikiwa user classes are involved.
            rudisha Tupu

# The following are used kwenye get_argspec na some kwenye tests
_MAX_COLS = 85
_MAX_LINES = 5  # enough kila bytes
_INDENT = ' '*4  # kila wrapped signatures
_first_param = re.compile(r'(?<=\()\w*\,?\s*')
_default_callable_argspec = "See source ama doc"
_invalid_method = "invalid method signature"
_argument_positional = "  # '/' marks preceding args kama positional-only."

eleza get_argspec(ob):
    '''Return a string describing the signature of a callable object, ama ''.

    For Python-coded functions na methods, the first line ni introspected.
    Delete 'self' parameter kila classes (.__init__) na bound methods.
    The next lines are the first lines of the doc string up to the first
    empty line ama _MAX_LINES.    For builtins, this typically includes
    the arguments kwenye addition to the rudisha value.
    '''
    argspec = default = ""
    jaribu:
        ob_call = ob.__call__
    tatizo BaseException:
        rudisha default

    fob = ob_call ikiwa isinstance(ob_call, types.MethodType) else ob

    jaribu:
        argspec = str(inspect.signature(fob))
    tatizo ValueError kama err:
        msg = str(err)
        ikiwa msg.startswith(_invalid_method):
            rudisha _invalid_method

    ikiwa '/' kwenye argspec na len(argspec) < _MAX_COLS - len(_argument_positional):
        # Add explanation TODO remove after 3.7, before 3.9.
        argspec += _argument_positional
    ikiwa isinstance(fob, type) na argspec == '()':
        # If fob has no argument, use default callable argspec.
        argspec = _default_callable_argspec

    lines = (textwrap.wrap(argspec, _MAX_COLS, subsequent_indent=_INDENT)
             ikiwa len(argspec) > _MAX_COLS else [argspec] ikiwa argspec else [])

    ikiwa isinstance(ob_call, types.MethodType):
        doc = ob_call.__doc__
    isipokua:
        doc = getattr(ob, "__doc__", "")
    ikiwa doc:
        kila line kwenye doc.split('\n', _MAX_LINES)[:_MAX_LINES]:
            line = line.strip()
            ikiwa sio line:
                koma
            ikiwa len(line) > _MAX_COLS:
                line = line[: _MAX_COLS - 3] + '...'
            lines.append(line)
    argspec = '\n'.join(lines)
    ikiwa sio argspec:
        argspec = _default_callable_argspec
    rudisha argspec


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_calltip', verbosity=2)
