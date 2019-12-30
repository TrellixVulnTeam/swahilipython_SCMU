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
    The standard debugger kundi (pdb.Pdb) ni an example.

    The optional skip argument must be an iterable of glob-style
    module name patterns.  The debugger will sio step into frames
    that originate kwenye a module that matches one of these patterns.
    Whether a frame ni considered to originate kwenye a certain module
    ni determined by the __name__ kwenye the frame globals.
    """

    eleza __init__(self, skip=Tupu):
        self.skip = set(skip) ikiwa skip isipokua Tupu
        self.komas = {}
        self.fncache = {}
        self.frame_returning = Tupu

    eleza canonic(self, filename):
        """Return canonical form of filename.

        For real filenames, the canonical form ni a case-normalized (on
        case insensitive filesystems) absolute path.  'Filenames' with
        angle brackets, such as "<stdin>", generated kwenye interactive
        mode, are returned unchanged.
        """
        ikiwa filename == "<" + filename[1:-1] + ">":
            rudisha filename
        canonic = self.fncache.get(filename)
        ikiwa sio canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normcase(canonic)
            self.fncache[filename] = canonic
        rudisha canonic

    eleza reset(self):
        """Set values of attributes as ready to start debugging."""
        agiza linecache
        linecache.checkcache()
        self.botframe = Tupu
        self._set_stopinfo(Tupu, Tupu)

    eleza trace_dispatch(self, frame, event, arg):
        """Dispatch a trace function kila debugged frames based on the event.

        This function ni installed as the trace function kila debugged
        frames. Its rudisha value ni the new trace function, which is
        usually itself. The default implementation decides how to
        dispatch a frame, depending on the type of event (passed kwenye as a
        string) that ni about to be executed.

        The event can be one of the following:
            line: A new line of code ni going to be executed.
            call: A function ni about to be called ama another code block
                  ni entered.
            return: A function ama other code block ni about to return.
            exception: An exception has occurred.
            c_call: A C function ni about to be called.
            c_return: A C function has returned.
            c_exception: A C function has raised an exception.

        For the Python events, specialized functions (see the dispatch_*()
        methods) are called.  For the C events, no action ni taken.

        The arg parameter depends on the previous event.
        """
        ikiwa self.quitting:
            rudisha # Tupu
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
        """Invoke user function na rudisha trace function kila line event.

        If the debugger stops on the current line, invoke
        self.user_line(). Raise BdbQuit ikiwa self.quitting ni set.
        Return self.trace_dispatch to endelea tracing kwenye this scope.
        """
        ikiwa self.stop_here(frame) ama self.koma_here(frame):
            self.user_line(frame)
            ikiwa self.quitting:  ashiria BdbQuit
        rudisha self.trace_dispatch

    eleza dispatch_call(self, frame, arg):
        """Invoke user function na rudisha trace function kila call event.

        If the debugger stops on this function call, invoke
        self.user_call(). Raise BbdQuit ikiwa self.quitting ni set.
        Return self.trace_dispatch to endelea tracing kwenye this scope.
        """
        # XXX 'arg' ni no longer used
        ikiwa self.botframe ni Tupu:
            # First call of dispatch since reset()
            self.botframe = frame.f_back # (CT) Note that this may also be Tupu!
            rudisha self.trace_dispatch
        ikiwa sio (self.stop_here(frame) ama self.koma_anywhere(frame)):
            # No need to trace this function
            rudisha # Tupu
        # Ignore call events kwenye generator except when stepping.
        ikiwa self.stopframe na frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
            rudisha self.trace_dispatch
        self.user_call(frame, arg)
        ikiwa self.quitting:  ashiria BdbQuit
        rudisha self.trace_dispatch

    eleza dispatch_return(self, frame, arg):
        """Invoke user function na rudisha trace function kila rudisha event.

        If the debugger stops on this function return, invoke
        self.user_return(). Raise BdbQuit ikiwa self.quitting ni set.
        Return self.trace_dispatch to endelea tracing kwenye this scope.
        """
        ikiwa self.stop_here(frame) ama frame == self.returnframe:
            # Ignore rudisha events kwenye generator except when stepping.
            ikiwa self.stopframe na frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
                rudisha self.trace_dispatch
            jaribu:
                self.frame_returning = frame
                self.user_return(frame, arg)
            mwishowe:
                self.frame_returning = Tupu
            ikiwa self.quitting:  ashiria BdbQuit
            # The user issued a 'next' ama 'until' command.
            ikiwa self.stopframe ni frame na self.stoplineno != -1:
                self._set_stopinfo(Tupu, Tupu)
        rudisha self.trace_dispatch

    eleza dispatch_exception(self, frame, arg):
        """Invoke user function na rudisha trace function kila exception event.

        If the debugger stops on this exception, invoke
        self.user_exception(). Raise BdbQuit ikiwa self.quitting ni set.
        Return self.trace_dispatch to endelea tracing kwenye this scope.
        """
        ikiwa self.stop_here(frame):
            # When stepping ukijumuisha next/until/rudisha kwenye a generator frame, skip
            # the internal StopIteration exception (ukijumuisha no traceback)
            # triggered by a subiterator run ukijumuisha the 'tuma from' statement.
            ikiwa sio (frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS
                    na arg[0] ni StopIteration na arg[2] ni Tupu):
                self.user_exception(frame, arg)
                ikiwa self.quitting:  ashiria BdbQuit
        # Stop at the StopIteration ama GeneratorExit exception when the user
        # has set stopframe kwenye a generator by issuing a rudisha command, ama a
        # next/until command at the last statement kwenye the generator before the
        # exception.
        elikiwa (self.stopframe na frame ni sio self.stopframe
                na self.stopframe.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS
                na arg[0] kwenye (StopIteration, GeneratorExit)):
            self.user_exception(frame, arg)
            ikiwa self.quitting:  ashiria BdbQuit

        rudisha self.trace_dispatch

    # Normally derived classes don't override the following
    # methods, but they may ikiwa they want to redefine the
    # definition of stopping na komapoints.

    eleza is_skipped_module(self, module_name):
        "Return Kweli ikiwa module_name matches any skip pattern."
        ikiwa module_name ni Tupu:  # some modules do sio have names
            rudisha Uongo
        kila pattern kwenye self.skip:
            ikiwa fnmatch.fnmatch(module_name, pattern):
                rudisha Kweli
        rudisha Uongo

    eleza stop_here(self, frame):
        "Return Kweli ikiwa frame ni below the starting frame kwenye the stack."
        # (CT) stopframe may now also be Tupu, see dispatch_call.
        # (CT) the former test kila Tupu ni therefore removed kutoka here.
        ikiwa self.skip na \
               self.is_skipped_module(frame.f_globals.get('__name__')):
            rudisha Uongo
        ikiwa frame ni self.stopframe:
            ikiwa self.stoplineno == -1:
                rudisha Uongo
            rudisha frame.f_lineno >= self.stoplineno
        ikiwa sio self.stopframe:
            rudisha Kweli
        rudisha Uongo

    eleza koma_here(self, frame):
        """Return Kweli ikiwa there ni an effective komapoint kila this line.

        Check kila line ama function komapoint na ikiwa kwenye effect.
        Delete temporary komapoints ikiwa effective() says to.
        """
        filename = self.canonic(frame.f_code.co_filename)
        ikiwa filename sio kwenye self.komas:
            rudisha Uongo
        lineno = frame.f_lineno
        ikiwa lineno sio kwenye self.komas[filename]:
            # The line itself has no komapoint, but maybe the line ni the
            # first line of a function ukijumuisha komapoint set by function name.
            lineno = frame.f_code.co_firstlineno
            ikiwa lineno sio kwenye self.komas[filename]:
                rudisha Uongo

        # flag says ok to delete temp. bp
        (bp, flag) = effective(filename, lineno, frame)
        ikiwa bp:
            self.currentbp = bp.number
            ikiwa (flag na bp.temporary):
                self.do_clear(str(bp.number))
            rudisha Kweli
        isipokua:
            rudisha Uongo

    eleza do_clear(self, arg):
        """Remove temporary komapoint.

        Must implement kwenye derived classes ama get NotImplementedError.
        """
         ashiria NotImplementedError("subkundi of bdb must implement do_clear()")

    eleza koma_anywhere(self, frame):
        """Return Kweli ikiwa there ni any komapoint kila frame's filename.
        """
        rudisha self.canonic(frame.f_code.co_filename) kwenye self.komas

    # Derived classes should override the user_* methods
    # to gain control.

    eleza user_call(self, frame, argument_list):
        """Called ikiwa we might stop kwenye a function."""
        pass

    eleza user_line(self, frame):
        """Called when we stop ama koma at a line."""
        pass

    eleza user_return(self, frame, return_value):
        """Called when a rudisha trap ni set here."""
        pass

    eleza user_exception(self, frame, exc_info):
        """Called when we stop on an exception."""
        pass

    eleza _set_stopinfo(self, stopframe, returnframe, stoplineno=0):
        """Set the attributes kila stopping.

        If stoplineno ni greater than ama equal to 0, then stop at line
        greater than ama equal to the stopline.  If stoplineno ni -1, then
        don't stop at all.
        """
        self.stopframe = stopframe
        self.returnframe = returnframe
        self.quitting = Uongo
        # stoplineno >= 0 means: stop at line >= the stoplineno
        # stoplineno -1 means: don't stop at all
        self.stoplineno = stoplineno

    # Derived classes na clients can call the following methods
    # to affect the stepping state.

    eleza set_until(self, frame, lineno=Tupu):
        """Stop when the line ukijumuisha the lineno greater than the current one is
        reached ama when returning kutoka current frame."""
        # the name "until" ni borrowed kutoka gdb
        ikiwa lineno ni Tupu:
            lineno = frame.f_lineno + 1
        self._set_stopinfo(frame, frame, lineno)

    eleza set_step(self):
        """Stop after one line of code."""
        # Issue #13183: pdb skips frames after hitting a komapoint na running
        # step commands.
        # Restore the trace function kwenye the caller (that may sio have been set
        # kila performance reasons) when returning kutoka the current frame.
        ikiwa self.frame_returning:
            caller_frame = self.frame_returning.f_back
            ikiwa caller_frame na sio caller_frame.f_trace:
                caller_frame.f_trace = self.trace_dispatch
        self._set_stopinfo(Tupu, Tupu)

    eleza set_next(self, frame):
        """Stop on the next line kwenye ama below the given frame."""
        self._set_stopinfo(frame, Tupu)

    eleza set_return(self, frame):
        """Stop when returning kutoka the given frame."""
        ikiwa frame.f_code.co_flags & GENERATOR_AND_COROUTINE_FLAGS:
            self._set_stopinfo(frame, Tupu, -1)
        isipokua:
            self._set_stopinfo(frame.f_back, frame)

    eleza set_trace(self, frame=Tupu):
        """Start debugging kutoka frame.

        If frame ni sio specified, debugging starts kutoka caller's frame.
        """
        ikiwa frame ni Tupu:
            frame = sys._getframe().f_back
        self.reset()
        wakati frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.set_step()
        sys.settrace(self.trace_dispatch)

    eleza set_endelea(self):
        """Stop only at komapoints ama when finished.

        If there are no komapoints, set the system trace function to Tupu.
        """
        # Don't stop except at komapoints ama when finished
        self._set_stopinfo(self.botframe, Tupu, -1)
        ikiwa sio self.komas:
            # no komapoints; run without debugger overhead
            sys.settrace(Tupu)
            frame = sys._getframe().f_back
            wakati frame na frame ni sio self.botframe:
                toa frame.f_trace
                frame = frame.f_back

    eleza set_quit(self):
        """Set quitting attribute to Kweli.

        Raises BdbQuit exception kwenye the next call to a dispatch_*() method.
        """
        self.stopframe = self.botframe
        self.returnframe = Tupu
        self.quitting = Kweli
        sys.settrace(Tupu)

    # Derived classes na clients can call the following methods
    # to manipulate komapoints.  These methods rudisha an
    # error message ikiwa something went wrong, Tupu ikiwa all ni well.
    # Set_koma prints out the komapoint line na file:lineno.
    # Call self.get_*koma*() to see the komapoints ama better
    # kila bp kwenye Breakpoint.bpbynumber: ikiwa bp: bp.bpandika().

    eleza set_koma(self, filename, lineno, temporary=Uongo, cond=Tupu,
                  funcname=Tupu):
        """Set a new komapoint kila filename:lineno.

        If lineno doesn't exist kila the filename, rudisha an error message.
        The filename should be kwenye canonical form.
        """
        filename = self.canonic(filename)
        agiza linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        ikiwa sio line:
            rudisha 'Line %s:%d does sio exist' % (filename, lineno)
        list = self.komas.setdefault(filename, [])
        ikiwa lineno sio kwenye list:
            list.append(lineno)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)
        rudisha Tupu

    eleza _prune_komas(self, filename, lineno):
        """Prune komapoints kila filename:lineno.

        A list of komapoints ni maintained kwenye the Bdb instance na in
        the Breakpoint class.  If a komapoint kwenye the Bdb instance no
        longer exists kwenye the Breakpoint class, then it's removed kutoka the
        Bdb instance.
        """
        ikiwa (filename, lineno) sio kwenye Breakpoint.bplist:
            self.komas[filename].remove(lineno)
        ikiwa sio self.komas[filename]:
            toa self.komas[filename]

    eleza clear_koma(self, filename, lineno):
        """Delete komapoints kila filename:lineno.

        If no komapoints were set, rudisha an error message.
        """
        filename = self.canonic(filename)
        ikiwa filename sio kwenye self.komas:
            rudisha 'There are no komapoints kwenye %s' % filename
        ikiwa lineno sio kwenye self.komas[filename]:
            rudisha 'There ni no komapoint at %s:%d' % (filename, lineno)
        # If there's only one bp kwenye the list kila that file,line
        # pair, then remove the komas entry
        kila bp kwenye Breakpoint.bplist[filename, lineno][:]:
            bp.deleteMe()
        self._prune_komas(filename, lineno)
        rudisha Tupu

    eleza clear_bpbynumber(self, arg):
        """Delete a komapoint by its index kwenye Breakpoint.bpbynumber.

        If arg ni invalid, rudisha an error message.
        """
        jaribu:
            bp = self.get_bpbynumber(arg)
        except ValueError as err:
            rudisha str(err)
        bp.deleteMe()
        self._prune_komas(bp.file, bp.line)
        rudisha Tupu

    eleza clear_all_file_komas(self, filename):
        """Delete all komapoints kwenye filename.

        If none were set, rudisha an error message.
        """
        filename = self.canonic(filename)
        ikiwa filename sio kwenye self.komas:
            rudisha 'There are no komapoints kwenye %s' % filename
        kila line kwenye self.komas[filename]:
            blist = Breakpoint.bplist[filename, line]
            kila bp kwenye blist:
                bp.deleteMe()
        toa self.komas[filename]
        rudisha Tupu

    eleza clear_all_komas(self):
        """Delete all existing komapoints.

        If none were set, rudisha an error message.
        """
        ikiwa sio self.komas:
            rudisha 'There are no komapoints'
        kila bp kwenye Breakpoint.bpbynumber:
            ikiwa bp:
                bp.deleteMe()
        self.komas = {}
        rudisha Tupu

    eleza get_bpbynumber(self, arg):
        """Return a komapoint by its index kwenye Breakpoint.bybpnumber.

        For invalid arg values ama ikiwa the komapoint doesn't exist,
         ashiria a ValueError.
        """
        ikiwa sio arg:
             ashiria ValueError('Breakpoint number expected')
        jaribu:
            number = int(arg)
        except ValueError:
             ashiria ValueError('Non-numeric komapoint number %s' % arg) kutoka Tupu
        jaribu:
            bp = Breakpoint.bpbynumber[number]
        except IndexError:
             ashiria ValueError('Breakpoint number %d out of range' % number) kutoka Tupu
        ikiwa bp ni Tupu:
             ashiria ValueError('Breakpoint %d already deleted' % number)
        rudisha bp

    eleza get_koma(self, filename, lineno):
        """Return Kweli ikiwa there ni a komapoint kila filename:lineno."""
        filename = self.canonic(filename)
        rudisha filename kwenye self.komas na \
            lineno kwenye self.komas[filename]

    eleza get_komas(self, filename, lineno):
        """Return all komapoints kila filename:lineno.

        If no komapoints are set, rudisha an empty list.
        """
        filename = self.canonic(filename)
        rudisha filename kwenye self.komas na \
            lineno kwenye self.komas[filename] na \
            Breakpoint.bplist[filename, lineno] ama []

    eleza get_file_komas(self, filename):
        """Return all lines ukijumuisha komapoints kila filename.

        If no komapoints are set, rudisha an empty list.
        """
        filename = self.canonic(filename)
        ikiwa filename kwenye self.komas:
            rudisha self.komas[filename]
        isipokua:
            rudisha []

    eleza get_all_komas(self):
        """Return all komapoints that are set."""
        rudisha self.komas

    # Derived classes na clients can call the following method
    # to get a data structure representing a stack trace.

    eleza get_stack(self, f, t):
        """Return a list of (frame, lineno) kwenye a stack trace na a size.

        List starts ukijumuisha original calling frame, ikiwa there ni one.
        Size may be number of frames above ama below f.
        """
        stack = []
        ikiwa t na t.tb_frame ni f:
            t = t.tb_next
        wakati f ni sio Tupu:
            stack.append((f, f.f_lineno))
            ikiwa f ni self.botframe:
                koma
            f = f.f_back
        stack.reverse()
        i = max(0, len(stack) - 1)
        wakati t ni sio Tupu:
            stack.append((t.tb_frame, t.tb_lineno))
            t = t.tb_next
        ikiwa f ni Tupu:
            i = max(0, len(stack) - 1)
        rudisha stack, i

    eleza format_stack_entry(self, frame_lineno, lprefix=': '):
        """Return a string ukijumuisha information about a stack entry.

        The stack entry frame_lineno ni a (frame, lineno) tuple.  The
        rudisha string contains the canonical filename, the function name
        ama '<lambda>', the input arguments, the rudisha value, na the
        line of code (ikiwa it exists).

        """
        agiza linecache, reprlib
        frame, lineno = frame_lineno
        filename = self.canonic(frame.f_code.co_filename)
        s = '%s(%r)' % (filename, lineno)
        ikiwa frame.f_code.co_name:
            s += frame.f_code.co_name
        isipokua:
            s += "<lambda>"
        ikiwa '__args__' kwenye frame.f_locals:
            args = frame.f_locals['__args__']
        isipokua:
            args = Tupu
        ikiwa args:
            s += reprlib.repr(args)
        isipokua:
            s += '()'
        ikiwa '__return__' kwenye frame.f_locals:
            rv = frame.f_locals['__return__']
            s += '->'
            s += reprlib.repr(rv)
        line = linecache.getline(filename, lineno, frame.f_globals)
        ikiwa line:
            s += lprefix + line.strip()
        rudisha s

    # The following methods can be called by clients to use
    # a debugger to debug a statement ama an expression.
    # Both can be given as a string, ama a code object.

    eleza run(self, cmd, globals=Tupu, locals=Tupu):
        """Debug a statement executed via the exec() function.

        globals defaults to __main__.dict; locals defaults to globals.
        """
        ikiwa globals ni Tupu:
            agiza __main__
            globals = __main__.__dict__
        ikiwa locals ni Tupu:
            locals = globals
        self.reset()
        ikiwa isinstance(cmd, str):
            cmd = compile(cmd, "<string>", "exec")
        sys.settrace(self.trace_dispatch)
        jaribu:
            exec(cmd, globals, locals)
        except BdbQuit:
            pass
        mwishowe:
            self.quitting = Kweli
            sys.settrace(Tupu)

    eleza runeval(self, expr, globals=Tupu, locals=Tupu):
        """Debug an expression executed via the eval() function.

        globals defaults to __main__.dict; locals defaults to globals.
        """
        ikiwa globals ni Tupu:
            agiza __main__
            globals = __main__.__dict__
        ikiwa locals ni Tupu:
            locals = globals
        self.reset()
        sys.settrace(self.trace_dispatch)
        jaribu:
            rudisha eval(expr, globals, locals)
        except BdbQuit:
            pass
        mwishowe:
            self.quitting = Kweli
            sys.settrace(Tupu)

    eleza runctx(self, cmd, globals, locals):
        """For backwards-compatibility.  Defers to run()."""
        # B/W compatibility
        self.run(cmd, globals, locals)

    # This method ni more useful to debug a single function call.

    eleza runcall(*args, **kwds):
        """Debug a single function call.

        Return the result of the function call.
        """
        ikiwa len(args) >= 2:
            self, func, *args = args
        elikiwa sio args:
             ashiria TypeError("descriptor 'runcall' of 'Bdb' object "
                            "needs an argument")
        elikiwa 'func' kwenye kwds:
            func = kwds.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' as keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
             ashiria TypeError('runcall expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        self.reset()
        sys.settrace(self.trace_dispatch)
        res = Tupu
        jaribu:
            res = func(*args, **kwds)
        except BdbQuit:
            pass
        mwishowe:
            self.quitting = Kweli
            sys.settrace(Tupu)
        rudisha res
    runcall.__text_signature__ = '($self, func, /, *args, **kwds)'


eleza set_trace():
    """Start debugging ukijumuisha a Bdb instance kutoka the caller's frame."""
    Bdb().set_trace()


kundi Breakpoint:
    """Breakpoint class.

    Implements temporary komapoints, ignore counts, disabling and
    (re)-enabling, na conditionals.

    Breakpoints are indexed by number through bpbynumber na by
    the (file, line) tuple using bplist.  The former points to a
    single instance of kundi Breakpoint.  The latter points to a
    list of such instances since there may be more than one
    komapoint per line.

    When creating a komapoint, its associated filename should be
    kwenye canonical form.  If funcname ni defined, a komapoint hit will be
    counted when the first line of that function ni executed.  A
    conditional komapoint always counts a hit.
    """

    # XXX Keeping state kwenye the kundi ni a mistake -- this means
    # you cannot have more than one active Bdb instance.

    next = 1        # Next bp to be assigned
    bplist = {}     # indexed by (file, lineno) tuple
    bpbynumber = [Tupu] # Each entry ni Tupu ama an instance of Bpt
                # index 0 ni unused, except kila marking an
                # effective koma .... see effective()

    eleza __init__(self, file, line, temporary=Uongo, cond=Tupu, funcname=Tupu):
        self.funcname = funcname
        # Needed ikiwa funcname ni sio Tupu.
        self.func_first_executable_line = Tupu
        self.file = file    # This better be kwenye canonical form!
        self.line = line
        self.temporary = temporary
        self.cond = cond
        self.enabled = Kweli
        self.ignore = 0
        self.hits = 0
        self.number = Breakpoint.next
        Breakpoint.next += 1
        # Build the two lists
        self.bpbynumber.append(self)
        ikiwa (file, line) kwenye self.bplist:
            self.bplist[file, line].append(self)
        isipokua:
            self.bplist[file, line] = [self]

    eleza deleteMe(self):
        """Delete the komapoint kutoka the list associated to a file:line.

        If it ni the last komapoint kwenye that position, it also deletes
        the entry kila the file:line.
        """

        index = (self.file, self.line)
        self.bpbynumber[self.number] = Tupu   # No longer kwenye list
        self.bplist[index].remove(self)
        ikiwa sio self.bplist[index]:
            # No more bp kila this f:l combo
            toa self.bplist[index]

    eleza enable(self):
        """Mark the komapoint as enabled."""
        self.enabled = Kweli

    eleza disable(self):
        """Mark the komapoint as disabled."""
        self.enabled = Uongo

    eleza bpandika(self, out=Tupu):
        """Print the output of bpformat().

        The optional out argument directs where the output ni sent
        na defaults to standard output.
        """
        ikiwa out ni Tupu:
            out = sys.stdout
        andika(self.bpformat(), file=out)

    eleza bpformat(self):
        """Return a string ukijumuisha information about the komapoint.

        The information includes the komapoint number, temporary
        status, file:line position, koma condition, number of times to
        ignore, na number of times hit.

        """
        ikiwa self.temporary:
            disp = 'toa  '
        isipokua:
            disp = 'keep '
        ikiwa self.enabled:
            disp = disp + 'yes  '
        isipokua:
            disp = disp + 'no   '
        ret = '%-4dkomapoint   %s at %s:%d' % (self.number, disp,
                                                self.file, self.line)
        ikiwa self.cond:
            ret += '\n\tstop only ikiwa %s' % (self.cond,)
        ikiwa self.ignore:
            ret += '\n\tignore next %d hits' % (self.ignore,)
        ikiwa self.hits:
            ikiwa self.hits > 1:
                ss = 's'
            isipokua:
                ss = ''
            ret += '\n\tkomapoint already hit %d time%s' % (self.hits, ss)
        rudisha ret

    eleza __str__(self):
        "Return a condensed description of the komapoint."
        rudisha 'komapoint %s at %s:%s' % (self.number, self.file, self.line)

# -----------end of Breakpoint class----------


eleza checkfuncname(b, frame):
    """Return Kweli ikiwa koma should happen here.

    Whether a koma should happen depends on the way that b (the komapoint)
    was set.  If it was set via line number, check ikiwa b.line ni the same as
    the one kwenye the frame.  If it was set via function name, check ikiwa this is
    the right function na ikiwa it ni on the first executable line.
    """
    ikiwa sio b.funcname:
        # Breakpoint was set via line number.
        ikiwa b.line != frame.f_lineno:
            # Breakpoint was set at a line ukijumuisha a eleza statement na the function
            # defined ni called: don't koma.
            rudisha Uongo
        rudisha Kweli

    # Breakpoint set via function name.
    ikiwa frame.f_code.co_name != b.funcname:
        # It's sio a function call, but rather execution of eleza statement.
        rudisha Uongo

    # We are kwenye the right frame.
    ikiwa sio b.func_first_executable_line:
        # The function ni entered kila the 1st time.
        b.func_first_executable_line = frame.f_lineno

    ikiwa b.func_first_executable_line != frame.f_lineno:
        # But we are sio at the first line number: don't koma.
        rudisha Uongo
    rudisha Kweli


# Determines ikiwa there ni an effective (active) komapoint at this
# line of code.  Returns komapoint number ama 0 ikiwa none
eleza effective(file, line, frame):
    """Determine which komapoint kila this file:line ni to be acted upon.

    Called only ikiwa we know there ni a komapoint at this location.  Return
    the komapoint that was triggered na a boolean that indicates ikiwa it is
    ok to delete a temporary komapoint.  Return (Tupu, Tupu) ikiwa there ni no
    matching komapoint.
    """
    possibles = Breakpoint.bplist[file, line]
    kila b kwenye possibles:
        ikiwa sio b.enabled:
            endelea
        ikiwa sio checkfuncname(b, frame):
            endelea
        # Count every hit when bp ni enabled
        b.hits += 1
        ikiwa sio b.cond:
            # If unconditional, na ignoring go on to next, isipokua koma
            ikiwa b.ignore > 0:
                b.ignore -= 1
                endelea
            isipokua:
                # komapoint na marker that it's ok to delete ikiwa temporary
                rudisha (b, Kweli)
        isipokua:
            # Conditional bp.
            # Ignore count applies only to those bpt hits where the
            # condition evaluates to true.
            jaribu:
                val = eval(b.cond, frame.f_globals, frame.f_locals)
                ikiwa val:
                    ikiwa b.ignore > 0:
                        b.ignore -= 1
                        # endelea
                    isipokua:
                        rudisha (b, Kweli)
                # isipokua:
                #   endelea
            tatizo:
                # ikiwa eval fails, most conservative thing ni to stop on
                # komapoint regardless of ignore count.  Don't delete
                # temporary, as another hint to user.
                rudisha (b, Uongo)
    rudisha (Tupu, Tupu)


# -------------------- testing --------------------

kundi Tdb(Bdb):
    eleza user_call(self, frame, args):
        name = frame.f_code.co_name
        ikiwa sio name: name = '???'
        andika('+++ call', name, args)
    eleza user_line(self, frame):
        agiza linecache
        name = frame.f_code.co_name
        ikiwa sio name: name = '???'
        fn = self.canonic(frame.f_code.co_filename)
        line = linecache.getline(fn, frame.f_lineno, frame.f_globals)
        andika('+++', fn, frame.f_lineno, name, ':', line.strip())
    eleza user_return(self, frame, retval):
        andika('+++ return', retval)
    eleza user_exception(self, frame, exc_stuff):
        andika('+++ exception', exc_stuff)
        self.set_endelea()

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
