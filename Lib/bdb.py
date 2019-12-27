"""Debugger basics"""

agiza fnmatch
agiza sys
agiza os
kutoka inspect agiza CO_GENERATOR, CO_COROUTINE, CO_ASYNC_GENERATOR

__all__ = ["BdbQuit", "Bdb", "Breakpoint"]

GENERATOR_AND_COROUTINE_FLAGS = CO_GENERATOR | CO_COROUTINE | CO_ASYNC_GENERATOR


kundi BdbQuit(Exception):
    """Exception to give up completely."""


kundi Bdb:
    """Generic Python debugger base class.

    This kundi takes care of details of the trace facility;
    a derived kundi should implement user interaction.
    The standard debugger kundi (pdb.Pdb) is an example.

    The optional skip argument must be an iterable of glob-style
    module name patterns.  The debugger will not step into frames
    that originate in a module that matches one of these patterns.
    Whether a frame is considered to originate in a certain module
    is determined by the __name__ in the frame globals.
    """

    eleza __init__(self, skip=None):
        self.skip = set(skip) ikiwa skip else None
        self.breaks = {}
        self.fncache = {}
        self.frame_returning = None

    eleza canonic(self, filename):
        """Return canonical form of filename.

        For real filenames, the canonical form is a case-normalized (on
        case insensitive filesystems) absolute path.  'Filenames' with
        angle brackets, such as "<stdin>", generated in interactive
        mode, are returned unchanged.
        """
        ikiwa filename == "<" + filename[1:-1] + ">":
            rudisha filename
        canonic = self.fncache.get(filename)
        ikiwa not canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normcase(canonic)
            self.fncache[filename] = canonic
        rudisha canonic

    eleza reset(self):
        """Set values of attributes as ready to start debugging."""
        agiza linecache
        linecache.checkcache()
        self.botframe = None
        self._set_stopinfo(None, None)

    eleza trace_dispatch(self, frame, event, arg):
        """Dispatch a trace function for debugged frames based on the event.

        This function is installed as the trace function for debugged
        frames. Its rudisha value is the new trace function, which is
        usually itself. The default implementation decides how to
        dispatch a frame, depending on the type of event (passed in as a
        string) that is about to be executed.

        The event can be one of the following:
            line: A new line of code is going to be executed.
            call: A function is about to be called or another code block
                  is entered.
            return: A function or other code block is about to return.
            exception: An exception has occurred.
            c_call: A C function is about to be called.
            c_return: A C function has returned.
            c_exception: A C function has raised an exception.

        For the Python events, specialized functions (see the dispatch_*()
        methods) are called.  For the C events, no action is taken.

        The arg parameter depends on the previous event.
        """
        ikiwa self.quitting:
            rudisha # None
        ikiwa event == 'line':
            rudisha self.dispatch_line(frame)
        ikiwa event == 'call':
            rudisha self.dispatch_call(frame, arg)
        ikiwa event == 'return':
            rudisha self.dispatch_return(frame, arg)
        ikiwa event == 'exception':
            rudisha self.dispatch_exception(frame, arg)
        ikiwa event == 'c_call':
            rudisha self.trace_dispatch
        ikiwa event == 'c_exception':
            rudisha self.trace_dispatch
        ikiwa event == 'c_return':
            rudisha self.trace_dispatch
        andika('bdb.Bdb.dispatch: unknown debugging event:', repr(event))
        rudisha self.trace_dispatch

    eleza dispatch_line(self, frame):
        """Invoke user function and rudisha trace function for line event.

        If the debugger stops on the current line, invoke
        self.user_line(). Raise BdbQuit ikiwa self.quitting is set.
        Return self.trace_dispatch to continue tracing in this scope.
        """
        ikiwa self.stop_here(frame) or self.break_here(frame):
            self.user_line(frame)
            ikiwa self.quitting: raise BdbQuit
        rudisha self.trace_dispatch

    eleza dispatch_call(self, frame, arg):
        """Invoke user function and rudisha trace function for call event.

        If the debugger stops on this function call, invoke
        self.user_call(). Raise BbdQuit ikiwa self.quitting is set.
        Return self.trace_dispatch to continue tracing in this scope.
        """
        # XXX 'arg' is no longer used
        ikiwa self.botframe is None:
            # First call of dispatch since reset()
            self.botframe = frame.f_back # (CT) Note that this may also be None!
            rudisha self.trace_dispatch
        ikiwa not (self.stop_here(frame) or self.break_anywhere(frame)):
            # No need to trace this function
            rudisha # None
        # Ignore call events in generator except when stepping.
        ikiwa self.stopframe and frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
            rudisha self.trace_dispatch
        self.user_call(frame, arg)
        ikiwa self.quitting: raise BdbQuit
        rudisha self.trace_dispatch

    eleza dispatch_return(self, frame, arg):
        """Invoke user function and rudisha trace function for rudisha event.

        If the debugger stops on this function return, invoke
        self.user_return(). Raise BdbQuit ikiwa self.quitting is set.
        Return self.trace_dispatch to continue tracing in this scope.
        """
        ikiwa self.stop_here(frame) or frame == self.returnframe:
            # Ignore rudisha events in generator except when stepping.
            ikiwa self.stopframe and frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
                rudisha self.trace_dispatch
            try:
                self.frame_returning = frame
                self.user_return(frame, arg)
            finally:
                self.frame_returning = None
            ikiwa self.quitting: raise BdbQuit
            # The user issued a 'next' or 'until' command.
            ikiwa self.stopframe is frame and self.stoplineno != -1:
                self._set_stopinfo(None, None)
        rudisha self.trace_dispatch

    eleza dispatch_exception(self, frame, arg):
        """Invoke user function and rudisha trace function for exception event.

        If the debugger stops on this exception, invoke
        self.user_exception(). Raise BdbQuit ikiwa self.quitting is set.
        Return self.trace_dispatch to continue tracing in this scope.
        """
        ikiwa self.stop_here(frame):
            # When stepping with next/until/rudisha in a generator frame, skip
            # the internal StopIteration exception (with no traceback)
            # triggered by a subiterator run with the 'yield kutoka' statement.
            ikiwa not (frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS
                    and arg[0] is StopIteration and arg[2] is None):
                self.user_exception(frame, arg)
                ikiwa self.quitting: raise BdbQuit
        # Stop at the StopIteration or GeneratorExit exception when the user
        # has set stopframe in a generator by issuing a rudisha command, or a
        # next/until command at the last statement in the generator before the
        # exception.
        elikiwa (self.stopframe and frame is not self.stopframe
                and self.stopframe.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS
                and arg[0] in (StopIteration, GeneratorExit)):
            self.user_exception(frame, arg)
            ikiwa self.quitting: raise BdbQuit

        rudisha self.trace_dispatch

    # Normally derived classes don't override the following
    # methods, but they may ikiwa they want to redefine the
    # definition of stopping and breakpoints.

    eleza is_skipped_module(self, module_name):
        "Return True ikiwa module_name matches any skip pattern."
        ikiwa module_name is None:  # some modules do not have names
            rudisha False
        for pattern in self.skip:
            ikiwa fnmatch.fnmatch(module_name, pattern):
                rudisha True
        rudisha False

    eleza stop_here(self, frame):
        "Return True ikiwa frame is below the starting frame in the stack."
        # (CT) stopframe may now also be None, see dispatch_call.
        # (CT) the former test for None is therefore removed kutoka here.
        ikiwa self.skip and \
               self.is_skipped_module(frame.f_globals.get('__name__')):
            rudisha False
        ikiwa frame is self.stopframe:
            ikiwa self.stoplineno == -1:
                rudisha False
            rudisha frame.f_lineno >= self.stoplineno
        ikiwa not self.stopframe:
            rudisha True
        rudisha False

    eleza break_here(self, frame):
        """Return True ikiwa there is an effective breakpoint for this line.

        Check for line or function breakpoint and ikiwa in effect.
        Delete temporary breakpoints ikiwa effective() says to.
        """
        filename = self.canonic(frame.f_code.co_filename)
        ikiwa filename not in self.breaks:
            rudisha False
        lineno = frame.f_lineno
        ikiwa lineno not in self.breaks[filename]:
            # The line itself has no breakpoint, but maybe the line is the
            # first line of a function with breakpoint set by function name.
            lineno = frame.f_code.co_firstlineno
            ikiwa lineno not in self.breaks[filename]:
                rudisha False

        # flag says ok to delete temp. bp
        (bp, flag) = effective(filename, lineno, frame)
        ikiwa bp:
            self.currentbp = bp.number
            ikiwa (flag and bp.temporary):
                self.do_clear(str(bp.number))
            rudisha True
        else:
            rudisha False

    eleza do_clear(self, arg):
        """Remove temporary breakpoint.

        Must implement in derived classes or get NotImplementedError.
        """
        raise NotImplementedError("subkundi of bdb must implement do_clear()")

    eleza break_anywhere(self, frame):
        """Return True ikiwa there is any breakpoint for frame's filename.
        """
        rudisha self.canonic(frame.f_code.co_filename) in self.breaks

    # Derived classes should override the user_* methods
    # to gain control.

    eleza user_call(self, frame, argument_list):
        """Called ikiwa we might stop in a function."""
        pass

    eleza user_line(self, frame):
        """Called when we stop or break at a line."""
        pass

    eleza user_return(self, frame, return_value):
        """Called when a rudisha trap is set here."""
        pass

    eleza user_exception(self, frame, exc_info):
        """Called when we stop on an exception."""
        pass

    eleza _set_stopinfo(self, stopframe, returnframe, stoplineno=0):
        """Set the attributes for stopping.

        If stoplineno is greater than or equal to 0, then stop at line
        greater than or equal to the stopline.  If stoplineno is -1, then
        don't stop at all.
        """
        self.stopframe = stopframe
        self.returnframe = returnframe
        self.quitting = False
        # stoplineno >= 0 means: stop at line >= the stoplineno
        # stoplineno -1 means: don't stop at all
        self.stoplineno = stoplineno

    # Derived classes and clients can call the following methods
    # to affect the stepping state.

    eleza set_until(self, frame, lineno=None):
        """Stop when the line with the lineno greater than the current one is
        reached or when returning kutoka current frame."""
        # the name "until" is borrowed kutoka gdb
        ikiwa lineno is None:
            lineno = frame.f_lineno + 1
        self._set_stopinfo(frame, frame, lineno)

    eleza set_step(self):
        """Stop after one line of code."""
        # Issue #13183: pdb skips frames after hitting a breakpoint and running
        # step commands.
        # Restore the trace function in the caller (that may not have been set
        # for performance reasons) when returning kutoka the current frame.
        ikiwa self.frame_returning:
            caller_frame = self.frame_returning.f_back
            ikiwa caller_frame and not caller_frame.f_trace:
                caller_frame.f_trace = self.trace_dispatch
        self._set_stopinfo(None, None)

    eleza set_next(self, frame):
        """Stop on the next line in or below the given frame."""
        self._set_stopinfo(frame, None)

    eleza set_return(self, frame):
        """Stop when returning kutoka the given frame."""
        ikiwa frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
            self._set_stopinfo(frame, None, -1)
        else:
            self._set_stopinfo(frame.f_back, frame)

    eleza set_trace(self, frame=None):
        """Start debugging kutoka frame.

        If frame is not specified, debugging starts kutoka caller's frame.
        """
        ikiwa frame is None:
            frame = sys._getframe().f_back
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.set_step()
        sys.settrace(self.trace_dispatch)

    eleza set_continue(self):
        """Stop only at breakpoints or when finished.

        If there are no breakpoints, set the system trace function to None.
        """
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)
        ikiwa not self.breaks:
            # no breakpoints; run without debugger overhead
            sys.settrace(None)
            frame = sys._getframe().f_back
            while frame and frame is not self.botframe:
                del frame.f_trace
                frame = frame.f_back

    eleza set_quit(self):
        """Set quitting attribute to True.

        Raises BdbQuit exception in the next call to a dispatch_*() method.
        """
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = True
        sys.settrace(None)

    # Derived classes and clients can call the following methods
    # to manipulate breakpoints.  These methods rudisha an
    # error message ikiwa something went wrong, None ikiwa all is well.
    # Set_break prints out the breakpoint line and file:lineno.
    # Call self.get_*break*() to see the breakpoints or better
    # for bp in Breakpoint.bpbynumber: ikiwa bp: bp.bpandika().

    eleza set_break(self, filename, lineno, temporary=False, cond=None,
                  funcname=None):
        """Set a new breakpoint for filename:lineno.

        If lineno doesn't exist for the filename, rudisha an error message.
        The filename should be in canonical form.
        """
        filename = self.canonic(filename)
        agiza linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        ikiwa not line:
            rudisha 'Line %s:%d does not exist' % (filename, lineno)
        list = self.breaks.setdefault(filename, [])
        ikiwa lineno not in list:
            list.append(lineno)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)
        rudisha None

    eleza _prune_breaks(self, filename, lineno):
        """Prune breakpoints for filename:lineno.

        A list of breakpoints is maintained in the Bdb instance and in
        the Breakpoint class.  If a breakpoint in the Bdb instance no
        longer exists in the Breakpoint class, then it's removed kutoka the
        Bdb instance.
        """
        ikiwa (filename, lineno) not in Breakpoint.bplist:
            self.breaks[filename].remove(lineno)
        ikiwa not self.breaks[filename]:
            del self.breaks[filename]

    eleza clear_break(self, filename, lineno):
        """Delete breakpoints for filename:lineno.

        If no breakpoints were set, rudisha an error message.
        """
        filename = self.canonic(filename)
        ikiwa filename not in self.breaks:
            rudisha 'There are no breakpoints in %s' % filename
        ikiwa lineno not in self.breaks[filename]:
            rudisha 'There is no breakpoint at %s:%d' % (filename, lineno)
        # If there's only one bp in the list for that file,line
        # pair, then remove the breaks entry
        for bp in Breakpoint.bplist[filename, lineno][:]:
            bp.deleteMe()
        self._prune_breaks(filename, lineno)
        rudisha None

    eleza clear_bpbynumber(self, arg):
        """Delete a breakpoint by its index in Breakpoint.bpbynumber.

        If arg is invalid, rudisha an error message.
        """
        try:
            bp = self.get_bpbynumber(arg)
        except ValueError as err:
            rudisha str(err)
        bp.deleteMe()
        self._prune_breaks(bp.file, bp.line)
        rudisha None

    eleza clear_all_file_breaks(self, filename):
        """Delete all breakpoints in filename.

        If none were set, rudisha an error message.
        """
        filename = self.canonic(filename)
        ikiwa filename not in self.breaks:
            rudisha 'There are no breakpoints in %s' % filename
        for line in self.breaks[filename]:
            blist = Breakpoint.bplist[filename, line]
            for bp in blist:
                bp.deleteMe()
        del self.breaks[filename]
        rudisha None

    eleza clear_all_breaks(self):
        """Delete all existing breakpoints.

        If none were set, rudisha an error message.
        """
        ikiwa not self.breaks:
            rudisha 'There are no breakpoints'
        for bp in Breakpoint.bpbynumber:
            ikiwa bp:
                bp.deleteMe()
        self.breaks = {}
        rudisha None

    eleza get_bpbynumber(self, arg):
        """Return a breakpoint by its index in Breakpoint.bybpnumber.

        For invalid arg values or ikiwa the breakpoint doesn't exist,
        raise a ValueError.
        """
        ikiwa not arg:
            raise ValueError('Breakpoint number expected')
        try:
            number = int(arg)
        except ValueError:
            raise ValueError('Non-numeric breakpoint number %s' % arg) kutoka None
        try:
            bp = Breakpoint.bpbynumber[number]
        except IndexError:
            raise ValueError('Breakpoint number %d out of range' % number) kutoka None
        ikiwa bp is None:
            raise ValueError('Breakpoint %d already deleted' % number)
        rudisha bp

    eleza get_break(self, filename, lineno):
        """Return True ikiwa there is a breakpoint for filename:lineno."""
        filename = self.canonic(filename)
        rudisha filename in self.breaks and \
            lineno in self.breaks[filename]

    eleza get_breaks(self, filename, lineno):
        """Return all breakpoints for filename:lineno.

        If no breakpoints are set, rudisha an empty list.
        """
        filename = self.canonic(filename)
        rudisha filename in self.breaks and \
            lineno in self.breaks[filename] and \
            Breakpoint.bplist[filename, lineno] or []

    eleza get_file_breaks(self, filename):
        """Return all lines with breakpoints for filename.

        If no breakpoints are set, rudisha an empty list.
        """
        filename = self.canonic(filename)
        ikiwa filename in self.breaks:
            rudisha self.breaks[filename]
        else:
            rudisha []

    eleza get_all_breaks(self):
        """Return all breakpoints that are set."""
        rudisha self.breaks

    # Derived classes and clients can call the following method
    # to get a data structure representing a stack trace.

    eleza get_stack(self, f, t):
        """Return a list of (frame, lineno) in a stack trace and a size.

        List starts with original calling frame, ikiwa there is one.
        Size may be number of frames above or below f.
        """
        stack = []
        ikiwa t and t.tb_frame is f:
            t = t.tb_next
        while f is not None:
            stack.append((f, f.f_lineno))
            ikiwa f is self.botframe:
                break
            f = f.f_back
        stack.reverse()
        i = max(0, len(stack) - 1)
        while t is not None:
            stack.append((t.tb_frame, t.tb_lineno))
            t = t.tb_next
        ikiwa f is None:
            i = max(0, len(stack) - 1)
        rudisha stack, i

    eleza format_stack_entry(self, frame_lineno, lprefix=': '):
        """Return a string with information about a stack entry.

        The stack entry frame_lineno is a (frame, lineno) tuple.  The
        rudisha string contains the canonical filename, the function name
        or '<lambda>', the input arguments, the rudisha value, and the
        line of code (ikiwa it exists).

        """
        agiza linecache, reprlib
        frame, lineno = frame_lineno
        filename = self.canonic(frame.f_code.co_filename)
        s = '%s(%r)' % (filename, lineno)
        ikiwa frame.f_code.co_name:
            s += frame.f_code.co_name
        else:
            s += "<lambda>"
        ikiwa '__args__' in frame.f_locals:
            args = frame.f_locals['__args__']
        else:
            args = None
        ikiwa args:
            s += reprlib.repr(args)
        else:
            s += '()'
        ikiwa '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            s += '->'
            s += reprlib.repr(rv)
        line = linecache.getline(filename, lineno, frame.f_globals)
        ikiwa line:
            s += lprefix + line.strip()
        rudisha s

    # The following methods can be called by clients to use
    # a debugger to debug a statement or an expression.
    # Both can be given as a string, or a code object.

    eleza run(self, cmd, globals=None, locals=None):
        """Debug a statement executed via the exec() function.

        globals defaults to __main__.dict; locals defaults to globals.
        """
        ikiwa globals is None:
            agiza __main__
            globals = __main__.__dict__
        ikiwa locals is None:
            locals = globals
        self.reset()
        ikiwa isinstance(cmd, str):
            cmd = compile(cmd, "<string>", "exec")
        sys.settrace(self.trace_dispatch)
        try:
            exec(cmd, globals, locals)
        except BdbQuit:
            pass
        finally:
            self.quitting = True
            sys.settrace(None)

    eleza runeval(self, expr, globals=None, locals=None):
        """Debug an expression executed via the eval() function.

        globals defaults to __main__.dict; locals defaults to globals.
        """
        ikiwa globals is None:
            agiza __main__
            globals = __main__.__dict__
        ikiwa locals is None:
            locals = globals
        self.reset()
        sys.settrace(self.trace_dispatch)
        try:
            rudisha eval(expr, globals, locals)
        except BdbQuit:
            pass
        finally:
            self.quitting = True
            sys.settrace(None)

    eleza runctx(self, cmd, globals, locals):
        """For backwards-compatibility.  Defers to run()."""
        # B/W compatibility
        self.run(cmd, globals, locals)

    # This method is more useful to debug a single function call.

    eleza runcall(*args, **kwds):
        """Debug a single function call.

        Return the result of the function call.
        """
        ikiwa len(args) >= 2:
            self, func, *args = args
        elikiwa not args:
            raise TypeError("descriptor 'runcall' of 'Bdb' object "
                            "needs an argument")
        elikiwa 'func' in kwds:
            func = kwds.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError('runcall expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        self.reset()
        sys.settrace(self.trace_dispatch)
        res = None
        try:
            res = func(*args, **kwds)
        except BdbQuit:
            pass
        finally:
            self.quitting = True
            sys.settrace(None)
        rudisha res
    runcall.__text_signature__ = '($self, func, /, *args, **kwds)'


eleza set_trace():
    """Start debugging with a Bdb instance kutoka the caller's frame."""
    Bdb().set_trace()


kundi Breakpoint:
    """Breakpoint class.

    Implements temporary breakpoints, ignore counts, disabling and
    (re)-enabling, and conditionals.

    Breakpoints are indexed by number through bpbynumber and by
    the (file, line) tuple using bplist.  The former points to a
    single instance of kundi Breakpoint.  The latter points to a
    list of such instances since there may be more than one
    breakpoint per line.

    When creating a breakpoint, its associated filename should be
    in canonical form.  If funcname is defined, a breakpoint hit will be
    counted when the first line of that function is executed.  A
    conditional breakpoint always counts a hit.
    """

    # XXX Keeping state in the kundi is a mistake -- this means
    # you cannot have more than one active Bdb instance.

    next = 1        # Next bp to be assigned
    bplist = {}     # indexed by (file, lineno) tuple
    bpbynumber = [None] # Each entry is None or an instance of Bpt
                # index 0 is unused, except for marking an
                # effective break .... see effective()

    eleza __init__(self, file, line, temporary=False, cond=None, funcname=None):
        self.funcname = funcname
        # Needed ikiwa funcname is not None.
        self.func_first_executable_line = None
        self.file = file    # This better be in canonical form!
        self.line = line
        self.temporary = temporary
        self.cond = cond
        self.enabled = True
        self.ignore = 0
        self.hits = 0
        self.number = Breakpoint.next
        Breakpoint.next += 1
        # Build the two lists
        self.bpbynumber.append(self)
        ikiwa (file, line) in self.bplist:
            self.bplist[file, line].append(self)
        else:
            self.bplist[file, line] = [self]

    eleza deleteMe(self):
        """Delete the breakpoint kutoka the list associated to a file:line.

        If it is the last breakpoint in that position, it also deletes
        the entry for the file:line.
        """

        index = (self.file, self.line)
        self.bpbynumber[self.number] = None   # No longer in list
        self.bplist[index].remove(self)
        ikiwa not self.bplist[index]:
            # No more bp for this f:l combo
            del self.bplist[index]

    eleza enable(self):
        """Mark the breakpoint as enabled."""
        self.enabled = True

    eleza disable(self):
        """Mark the breakpoint as disabled."""
        self.enabled = False

    eleza bpandika(self, out=None):
        """Print the output of bpformat().

        The optional out argument directs where the output is sent
        and defaults to standard output.
        """
        ikiwa out is None:
            out = sys.stdout
        andika(self.bpformat(), file=out)

    eleza bpformat(self):
        """Return a string with information about the breakpoint.

        The information includes the breakpoint number, temporary
        status, file:line position, break condition, number of times to
        ignore, and number of times hit.

        """
        ikiwa self.temporary:
            disp = 'del  '
        else:
            disp = 'keep '
        ikiwa self.enabled:
            disp = disp + 'yes  '
        else:
            disp = disp + 'no   '
        ret = '%-4dbreakpoint   %s at %s:%d' % (self.number, disp,
                                                self.file, self.line)
        ikiwa self.cond:
            ret += '\n\tstop only ikiwa %s' % (self.cond,)
        ikiwa self.ignore:
            ret += '\n\tignore next %d hits' % (self.ignore,)
        ikiwa self.hits:
            ikiwa self.hits > 1:
                ss = 's'
            else:
                ss = ''
            ret += '\n\tbreakpoint already hit %d time%s' % (self.hits, ss)
        rudisha ret

    eleza __str__(self):
        "Return a condensed description of the breakpoint."
        rudisha 'breakpoint %s at %s:%s' % (self.number, self.file, self.line)

# -----------end of Breakpoint class----------


eleza checkfuncname(b, frame):
    """Return True ikiwa break should happen here.

    Whether a break should happen depends on the way that b (the breakpoint)
    was set.  If it was set via line number, check ikiwa b.line is the same as
    the one in the frame.  If it was set via function name, check ikiwa this is
    the right function and ikiwa it is on the first executable line.
    """
    ikiwa not b.funcname:
        # Breakpoint was set via line number.
        ikiwa b.line != frame.f_lineno:
            # Breakpoint was set at a line with a eleza statement and the function
            # defined is called: don't break.
            rudisha False
        rudisha True

    # Breakpoint set via function name.
    ikiwa frame.f_code.co_name != b.funcname:
        # It's not a function call, but rather execution of eleza statement.
        rudisha False

    # We are in the right frame.
    ikiwa not b.func_first_executable_line:
        # The function is entered for the 1st time.
        b.func_first_executable_line = frame.f_lineno

    ikiwa b.func_first_executable_line != frame.f_lineno:
        # But we are not at the first line number: don't break.
        rudisha False
    rudisha True


# Determines ikiwa there is an effective (active) breakpoint at this
# line of code.  Returns breakpoint number or 0 ikiwa none
eleza effective(file, line, frame):
    """Determine which breakpoint for this file:line is to be acted upon.

    Called only ikiwa we know there is a breakpoint at this location.  Return
    the breakpoint that was triggered and a boolean that indicates ikiwa it is
    ok to delete a temporary breakpoint.  Return (None, None) ikiwa there is no
    matching breakpoint.
    """
    possibles = Breakpoint.bplist[file, line]
    for b in possibles:
        ikiwa not b.enabled:
            continue
        ikiwa not checkfuncname(b, frame):
            continue
        # Count every hit when bp is enabled
        b.hits += 1
        ikiwa not b.cond:
            # If unconditional, and ignoring go on to next, else break
            ikiwa b.ignore > 0:
                b.ignore -= 1
                continue
            else:
                # breakpoint and marker that it's ok to delete ikiwa temporary
                rudisha (b, True)
        else:
            # Conditional bp.
            # Ignore count applies only to those bpt hits where the
            # condition evaluates to true.
            try:
                val = eval(b.cond, frame.f_globals, frame.f_locals)
                ikiwa val:
                    ikiwa b.ignore > 0:
                        b.ignore -= 1
                        # continue
                    else:
                        rudisha (b, True)
                # else:
                #   continue
            except:
                # ikiwa eval fails, most conservative thing is to stop on
                # breakpoint regardless of ignore count.  Don't delete
                # temporary, as another hint to user.
                rudisha (b, False)
    rudisha (None, None)


# -------------------- testing --------------------

kundi Tdb(Bdb):
    eleza user_call(self, frame, args):
        name = frame.f_code.co_name
        ikiwa not name: name = '???'
        andika('+++ call', name, args)
    eleza user_line(self, frame):
        agiza linecache
        name = frame.f_code.co_name
        ikiwa not name: name = '???'
        fn = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        andika('+++', fn, frame.f_lineno, name, ':', line.strip())
    eleza user_return(self, frame, retval):
        andika('+++ return', retval)
    eleza user_exception(self, frame, exc_stuff):
        andika('+++ exception', exc_stuff)
        self.set_continue()

eleza foo(n):
    andika('foo(', n, ')')
    x = bar(n*10)
    andika('bar returned', x)

eleza bar(a):
    andika('bar(', a, ')')
    rudisha a/2

eleza test():
    t = Tdb()
    t.run('agiza bdb; bdb.foo(10)')
