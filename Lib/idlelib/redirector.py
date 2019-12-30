kutoka tkinter agiza TclError

kundi WidgetRedirector:
    """Support kila redirecting arbitrary widget subcommands.

    Some Tk operations don't normally pita through tkinter.  For example, ikiwa a
    character ni inserted into a Text widget by pressing a key, a default Tk
    binding to the widget's 'insert' operation ni activated, na the Tk library
    processes the insert without calling back into tkinter.

    Although a binding to <Key> could be made via tkinter, what we really want
    to do ni to hook the Tk 'insert' operation itself.  For one thing, we want
    a text.insert call kwenye idle code to have the same effect kama a key press.

    When a widget ni instantiated, a Tcl command ni created whose name ni the
    same kama the pathname widget._w.  This command ni used to invoke the various
    widget operations, e.g. insert (kila a Text widget). We are going to hook
    this command na provide a facility ('register') to intercept the widget
    operation.  We will also intercept method calls on the tkinter class
    instance that represents the tk widget.

    In IDLE, WidgetRedirector ni used kwenye Percolator to intercept Text
    commands.  The function being registered provides access to the top
    of a Percolator chain.  At the bottom of the chain ni a call to the
    original Tk widget operation.
    """
    eleza __init__(self, widget):
        '''Initialize attributes na setup redirection.

        _operations: dict mapping operation name to new function.
        widget: the widget whose tcl command ni to be intercepted.
        tk: widget.tk, a convenience attribute, probably sio needed.
        orig: new name of the original tcl command.

        Since renaming to orig fails ukijumuisha TclError when orig already
        exists, only one WidgetDirector can exist kila a given widget.
        '''
        self._operations = {}
        self.widget = widget            # widget instance
        self.tk = tk = widget.tk        # widget's root
        w = widget._w                   # widget's (full) Tk pathname
        self.orig = w + "_orig"
        # Rename the Tcl command within Tcl:
        tk.call("rename", w, self.orig)
        # Create a new Tcl command whose name ni the widget's pathname, na
        # whose action ni to dispatch on the operation pitaed to the widget:
        tk.createcommand(w, self.dispatch)

    eleza __repr__(self):
        rudisha "%s(%s<%s>)" % (self.__class__.__name__,
                               self.widget.__class__.__name__,
                               self.widget._w)

    eleza close(self):
        "Unregister operations na revert redirection created by .__init__."
        kila operation kwenye list(self._operations):
            self.unregister(operation)
        widget = self.widget
        tk = widget.tk
        w = widget._w
        # Restore the original widget Tcl command.
        tk.deletecommand(w)
        tk.call("rename", self.orig, w)
        toa self.widget, self.tk  # Should sio be needed
        # ikiwa instance ni deleted after close, kama kwenye Percolator.

    eleza register(self, operation, function):
        '''Return OriginalCommand(operation) after registering function.

        Registration adds an operation: function pair to ._operations.
        It also adds a widget function attribute that masks the tkinter
        kundi instance method.  Method masking operates independently
        kutoka command dispatch.

        If a second function ni registered kila the same operation, the
        first function ni replaced kwenye both places.
        '''
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        rudisha OriginalCommand(self, operation)

    eleza unregister(self, operation):
        '''Return the function kila the operation, ama Tupu.

        Deleting the instance attribute unmasks the kundi attribute.
        '''
        ikiwa operation kwenye self._operations:
            function = self._operations[operation]
            toa self._operations[operation]
            jaribu:
                delattr(self.widget, operation)
            tatizo AttributeError:
                pita
            rudisha function
        isipokua:
            rudisha Tupu

    eleza dispatch(self, operation, *args):
        '''Callback kutoka Tcl which runs when the widget ni referenced.

        If an operation has been registered kwenye self._operations, apply the
        associated function to the args pitaed into Tcl. Otherwise, pita the
        operation through to Tk via the original Tcl function.

        Note that ikiwa a registered function ni called, the operation ni not
        pitaed through to Tk.  Apply the function returned by self.register()
        to *args to accomplish that.  For an example, see colorizer.py.

        '''
        m = self._operations.get(operation)
        jaribu:
            ikiwa m:
                rudisha m(*args)
            isipokua:
                rudisha self.tk.call((self.orig, operation) + args)
        tatizo TclError:
            rudisha ""


kundi OriginalCommand:
    '''Callable kila original tk command that has been redirected.

    Returned by .register; can be used kwenye the function registered.
    redir = WidgetRedirector(text)
    eleza my_insert(*args):
        andika("insert", args)
        original_insert(*args)
    original_insert = redir.register("insert", my_insert)
    '''

    eleza __init__(self, redir, operation):
        '''Create .tk_call na .orig_and_operation kila .__call__ method.

        .redir na .operation store the input args kila __repr__.
        .tk na .orig copy attributes of .redir (probably sio needed).
        '''
        self.redir = redir
        self.operation = operation
        self.tk = redir.tk  # redundant ukijumuisha self.redir
        self.orig = redir.orig  # redundant ukijumuisha self.redir
        # These two could be deleted after checking recipient code.
        self.tk_call = redir.tk.call
        self.orig_and_operation = (redir.orig, operation)

    eleza __repr__(self):
        rudisha "%s(%r, %r)" % (self.__class__.__name__,
                               self.redir, self.operation)

    eleza __call__(self, *args):
        rudisha self.tk_call(self.orig_and_operation + args)


eleza _widget_redirector(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text

    top = Toplevel(parent)
    top.title("Test WidgetRedirector")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x, y + 175))
    text = Text(top)
    text.pack()
    text.focus_set()
    redir = WidgetRedirector(text)
    eleza my_insert(*args):
        andika("insert", args)
        original_insert(*args)
    original_insert = redir.register("insert", my_insert)

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_redirector', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_widget_redirector)
