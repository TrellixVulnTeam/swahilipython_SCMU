"""Pop up a reminder of how to call a function.

Call Tips are floating windows which display function, class, and method
parameter and docstring information when you type an opening parenthesis, and
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

    eleza __init__(self, editwin=None):
        ikiwa editwin is None:  # subprocess and test
            self.editwin = None
        else:
            self.editwin = editwin
            self.text = editwin.text
            self.active_calltip = None
            self._calltip_window = self._make_tk_calltip_window

    eleza close(self):
        self._calltip_window = None

    eleza _make_tk_calltip_window(self):
        # See __init__ for usage
        rudisha calltip_w.CalltipWindow(self.text)

    eleza _remove_calltip_window(self, event=None):
        ikiwa self.active_calltip:
            self.active_calltip.hidetip()
            self.active_calltip = None

    eleza force_open_calltip_event(self, event):
        "The user selected the menu entry or hotkey, open the tip."
        self.open_calltip(True)
        rudisha "break"

    eleza try_open_calltip_event(self, event):
        """Happens when it would be nice to open a calltip, but not really
        necessary, for example after an opening bracket, so function calls
        won't be made.
        """
        self.open_calltip(False)

    eleza refresh_calltip_event(self, event):
        ikiwa self.active_calltip and self.active_calltip.tipwindow:
            self.open_calltip(False)

    eleza open_calltip(self, evalfuncs):
        self._remove_calltip_window()

        hp = HyperParser(self.editwin, "insert")
        sur_paren = hp.get_surrounding_brackets('(')
        ikiwa not sur_paren:
            return
        hp.set_index(sur_paren[0])
        expression  = hp.get_expression()
        ikiwa not expression:
            return
        ikiwa not evalfuncs and (expression.find('(') != -1):
            return
        argspec = self.fetch_tip(expression)
        ikiwa not argspec:
            return
        self.active_calltip = self._calltip_window()
        self.active_calltip.showtip(argspec, sur_paren[0], sur_paren[1])

    eleza fetch_tip(self, expression):
        """Return the argument list and docstring of a function or class.

        If there is a Python subprocess, get the calltip there.  Otherwise,
        either this fetch_tip() is running in the subprocess or it was
        called in an IDLE running without the subprocess.

        The subprocess environment is that of the most recently run script.  If
        two unrelated modules are being edited some calltips in the current
        module may be inoperative ikiwa the module was not the last to run.

        To find methods, fetch_tip must be fed a fully qualified name.

        """
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except AttributeError:
            rpcclt = None
        ikiwa rpcclt:
            rudisha rpcclt.remotecall("exec", "get_the_calltip",
                                     (expression,), {})
        else:
            rudisha get_argspec(get_entity(expression))


eleza get_entity(expression):
    """Return the object corresponding to expression evaluated
    in a namespace spanning sys.modules and __main.dict__.
    """
    ikiwa expression:
        namespace = {**sys.modules, **__main__.__dict__}
        try:
            rudisha eval(expression, namespace)  # Only protect user code.
        except BaseException:
            # An uncaught exception closes idle, and eval can raise any
            # exception, especially ikiwa user classes are involved.
            rudisha None

# The following are used in get_argspec and some in tests
_MAX_COLS = 85
_MAX_LINES = 5  # enough for bytes
_INDENT = ' '*4  # for wrapped signatures
_first_param = re.compile(r'(?<=\()\w*\,?\s*')
_default_callable_argspec = "See source or doc"
_invalid_method = "invalid method signature"
_argument_positional = "  # '/' marks preceding args as positional-only."

eleza get_argspec(ob):
    '''Return a string describing the signature of a callable object, or ''.

    For Python-coded functions and methods, the first line is introspected.
    Delete 'self' parameter for classes (.__init__) and bound methods.
    The next lines are the first lines of the doc string up to the first
    empty line or _MAX_LINES.    For builtins, this typically includes
    the arguments in addition to the rudisha value.
    '''
    argspec = default = ""
    try:
        ob_call = ob.__call__
    except BaseException:
        rudisha default

    fob = ob_call ikiwa isinstance(ob_call, types.MethodType) else ob

    try:
        argspec = str(inspect.signature(fob))
    except ValueError as err:
        msg = str(err)
        ikiwa msg.startswith(_invalid_method):
            rudisha _invalid_method

    ikiwa '/' in argspec and len(argspec) < _MAX_COLS - len(_argument_positional):
        # Add explanation TODO remove after 3.7, before 3.9.
        argspec += _argument_positional
    ikiwa isinstance(fob, type) and argspec == '()':
        # If fob has no argument, use default callable argspec.
        argspec = _default_callable_argspec

    lines = (textwrap.wrap(argspec, _MAX_COLS, subsequent_indent=_INDENT)
             ikiwa len(argspec) > _MAX_COLS else [argspec] ikiwa argspec else [])

    ikiwa isinstance(ob_call, types.MethodType):
        doc = ob_call.__doc__
    else:
        doc = getattr(ob, "__doc__", "")
    ikiwa doc:
        for line in doc.split('\n', _MAX_LINES)[:_MAX_LINES]:
            line = line.strip()
            ikiwa not line:
                break
            ikiwa len(line) > _MAX_COLS:
                line = line[: _MAX_COLS - 3] + '...'
            lines.append(line)
    argspec = '\n'.join(lines)
    ikiwa not argspec:
        argspec = _default_callable_argspec
    rudisha argspec


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_calltip', verbosity=2)
