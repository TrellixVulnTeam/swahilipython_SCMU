#! /usr/bin/env python3

"""
The Python Debugger Pdb
=======================

To use the debugger in its simplest form:

        >>> agiza pdb
        >>> pdb.run('<a statement>')

The debugger's prompt is '(Pdb) '.  This will stop in the first
function call in <a statement>.

Alternatively, ikiwa a statement terminated with an unhandled exception,
you can use pdb's post-mortem facility to inspect the contents of the
traceback:

        >>> <a statement>
        <exception traceback>
        >>> agiza pdb
        >>> pdb.pm()

The commands recognized by the debugger are listed in the next
section.  Most can be abbreviated as indicated; e.g., h(elp) means
that 'help' can be typed as 'h' or 'help' (but not as 'he' or 'hel',
nor as 'H' or 'Help' or 'HELP').  Optional arguments are enclosed in
square brackets.  Alternatives in the command syntax are separated
by a vertical bar (|).

A blank line repeats the previous command literally, except for
'list', where it lists the next 11 lines.

Commands that the debugger doesn't recognize are assumed to be Python
statements and are executed in the context of the program being
debugged.  Python statements can also be prefixed with an exclamation
point ('!').  This is a powerful way to inspect the program being
debugged; it is even possible to change variables or call functions.
When an exception occurs in such a statement, the exception name is
printed but the debugger's state is not changed.

The debugger supports aliases, which can save typing.  And aliases can
have parameters (see the alias help entry) which allows one a certain
level of adaptability to the context under examination.

Multiple commands may be entered on a single line, separated by the
pair ';;'.  No intelligence is applied to separating the commands; the
input is split at the first ';;', even ikiwa it is in the middle of a
quoted string.

If a file ".pdbrc" exists in your home directory or in the current
directory, it is read in and executed as ikiwa it had been typed at the
debugger prompt.  This is particularly useful for aliases.  If both
files exist, the one in the home directory is read first and aliases
defined there can be overridden by the local file.  This behavior can be
disabled by passing the "readrc=False" argument to the Pdb constructor.

Aside kutoka aliases, the debugger is not directly programmable; but it
is implemented as a kundi kutoka which you can derive your own debugger
class, which you can make as fancy as you like.


Debugger commands
=================

"""
# NOTE: the actual command documentation is collected kutoka docstrings of the
# commands and is appended to __doc__ after the kundi has been defined.

agiza os
agiza re
agiza sys
agiza cmd
agiza bdb
agiza dis
agiza code
agiza glob
agiza pprint
agiza signal
agiza inspect
agiza traceback
agiza linecache


kundi Restart(Exception):
    """Causes a debugger to be restarted for the debugged python program."""
    pass

__all__ = ["run", "pm", "Pdb", "runeval", "runctx", "runcall", "set_trace",
           "post_mortem", "help"]

eleza find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % re.escape(funcname))
    try:
        fp = open(filename)
    except OSError:
        rudisha None
    # consumer of this info expects the first line to be 1
    with fp:
        for lineno, line in enumerate(fp, start=1):
            ikiwa cre.match(line):
                rudisha funcname, filename, lineno
    rudisha None

eleza getsourcelines(obj):
    lines, lineno = inspect.findsource(obj)
    ikiwa inspect.isframe(obj) and obj.f_globals is obj.f_locals:
        # must be a module frame: do not try to cut a block out of it
        rudisha lines, 1
    elikiwa inspect.ismodule(obj):
        rudisha lines, 1
    rudisha inspect.getblock(lines[lineno:]), lineno+1

eleza lasti2lineno(code, lasti):
    linestarts = list(dis.findlinestarts(code))
    linestarts.reverse()
    for i, lineno in linestarts:
        ikiwa lasti >= i:
            rudisha lineno
    rudisha 0


kundi _rstr(str):
    """String that doesn't quote its repr."""
    eleza __repr__(self):
        rudisha self


# Interaction prompt line will separate file and call info kutoka code
# text using value of line_prefix string.  A newline and arrow may
# be to your liking.  You can set it once pdb is imported using the
# command "pdb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

kundi Pdb(bdb.Bdb, cmd.Cmd):

    _previous_sigint_handler = None

    eleza __init__(self, completekey='tab', stdin=None, stdout=None, skip=None,
                 nosigint=False, readrc=True):
        bdb.Bdb.__init__(self, skip=skip)
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        sys.audit("pdb.Pdb")
        ikiwa stdout:
            self.use_rawinput = 0
        self.prompt = '(Pdb) '
        self.aliases = {}
        self.displaying = {}
        self.mainpyfile = ''
        self._wait_for_mainpyfile = False
        self.tb_lineno = {}
        # Try to load readline ikiwa it exists
        try:
            agiza readline
            # remove some common file name delimiters
            readline.set_completer_delims(' \t\n`@#$%^&*()=+[{]}\\|;:\'",<>?')
        except ImportError:
            pass
        self.allow_kbdint = False
        self.nosigint = nosigint

        # Read ~/.pdbrc and ./.pdbrc
        self.rcLines = []
        ikiwa readrc:
            try:
                with open(os.path.expanduser('~/.pdbrc')) as rcFile:
                    self.rcLines.extend(rcFile)
            except OSError:
                pass
            try:
                with open(".pdbrc") as rcFile:
                    self.rcLines.extend(rcFile)
            except OSError:
                pass

        self.commands = {} # associates a command list to breakpoint numbers
        self.commands_doprompt = {} # for each bp num, tells ikiwa the prompt
                                    # must be disp. after execing the cmd list
        self.commands_silent = {} # for each bp num, tells ikiwa the stack trace
                                  # must be disp. after execing the cmd list
        self.commands_defining = False # True while in the process of defining
                                       # a command list
        self.commands_bnum = None # The breakpoint number for which we are
                                  # defining a list

    eleza sigint_handler(self, signum, frame):
        ikiwa self.allow_kbdint:
            raise KeyboardInterrupt
        self.message("\nProgram interrupted. (Use 'cont' to resume).")
        self.set_step()
        self.set_trace(frame)

    eleza reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    eleza forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None
        self.tb_lineno.clear()

    eleza setup(self, f, tb):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, tb)
        while tb:
            # when setting up post-mortem debugging with a traceback, save all
            # the original line numbers to be displayed along the current line
            # numbers (which can be different, e.g. due to finally clauses)
            lineno = lasti2lineno(tb.tb_frame.f_code, tb.tb_lasti)
            self.tb_lineno[tb.tb_frame] = lineno
            tb = tb.tb_next
        self.curframe = self.stack[self.curindex][0]
        # The f_locals dictionary is updated kutoka the actual frame
        # locals whenever the .f_locals accessor is called, so we
        # cache it here to ensure that modifications are not overwritten.
        self.curframe_locals = self.curframe.f_locals
        rudisha self.execRcLines()

    # Can be executed earlier than 'setup' ikiwa desired
    eleza execRcLines(self):
        ikiwa not self.rcLines:
            return
        # local copy because of recursion
        rcLines = self.rcLines
        rcLines.reverse()
        # execute every line only once
        self.rcLines = []
        while rcLines:
            line = rcLines.pop().strip()
            ikiwa line and line[0] != '#':
                ikiwa self.onecmd(line):
                    # ikiwa onecmd returns True, the command wants to exit
                    # kutoka the interaction, save leftover rc lines
                    # to execute before next interaction
                    self.rcLines += reversed(rcLines)
                    rudisha True

    # Override Bdb methods

    eleza user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""
        ikiwa self._wait_for_mainpyfile:
            return
        ikiwa self.stop_here(frame):
            self.message('--Call--')
            self.interaction(frame, None)

    eleza user_line(self, frame):
        """This function is called when we stop or break at this line."""
        ikiwa self._wait_for_mainpyfile:
            ikiwa (self.mainpyfile != self.canonic(frame.f_code.co_filename)
                or frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = False
        ikiwa self.bp_commands(frame):
            self.interaction(frame, None)

    eleza bp_commands(self, frame):
        """Call every command that was set for the current active breakpoint
        (ikiwa there is one).

        Returns True ikiwa the normal interaction function must be called,
        False otherwise."""
        # self.currentbp is set in bdb in Bdb.break_here ikiwa a breakpoint was hit
        ikiwa getattr(self, "currentbp", False) and \
               self.currentbp in self.commands:
            currentbp = self.currentbp
            self.currentbp = 0
            lastcmd_back = self.lastcmd
            self.setup(frame, None)
            for line in self.commands[currentbp]:
                self.onecmd(line)
            self.lastcmd = lastcmd_back
            ikiwa not self.commands_silent[currentbp]:
                self.print_stack_entry(self.stack[self.curindex])
            ikiwa self.commands_doprompt[currentbp]:
                self._cmdloop()
            self.forget()
            return
        rudisha 1

    eleza user_return(self, frame, return_value):
        """This function is called when a rudisha trap is set here."""
        ikiwa self._wait_for_mainpyfile:
            return
        frame.f_locals['__return__'] = return_value
        self.message('--Return--')
        self.interaction(frame, None)

    eleza user_exception(self, frame, exc_info):
        """This function is called ikiwa an exception occurs,
        but only ikiwa we are to stop at or just below this level."""
        ikiwa self._wait_for_mainpyfile:
            return
        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value

        # An 'Internal StopIteration' exception is an exception debug event
        # issued by the interpreter when handling a subgenerator run with
        # 'yield kutoka' or a generator controlled by a for loop. No exception has
        # actually occurred in this case. The debugger uses this debug event to
        # stop when the debuggee is returning kutoka such generators.
        prefix = 'Internal ' ikiwa (not exc_traceback
                                    and exc_type is StopIteration) else ''
        self.message('%s%s' % (prefix,
            traceback.format_exception_only(exc_type, exc_value)[-1].strip()))
        self.interaction(frame, exc_traceback)

    # General interaction function
    eleza _cmdloop(self):
        while True:
            try:
                # keyboard interrupts allow for an easy way to cancel
                # the current command, so allow them during interactive input
                self.allow_kbdint = True
                self.cmdloop()
                self.allow_kbdint = False
                break
            except KeyboardInterrupt:
                self.message('--KeyboardInterrupt--')

    # Called before loop, handles display expressions
    eleza preloop(self):
        displaying = self.displaying.get(self.curframe)
        ikiwa displaying:
            for expr, oldvalue in displaying.items():
                newvalue = self._getval_except(expr)
                # check for identity first; this prevents custom __eq__ to
                # be called at every loop, and also prevents instances whose
                # fields are changed to be displayed
                ikiwa newvalue is not oldvalue and newvalue != oldvalue:
                    displaying[expr] = newvalue
                    self.message('display %s: %r  [old: %r]' %
                                 (expr, newvalue, oldvalue))

    eleza interaction(self, frame, traceback):
        # Restore the previous signal handler at the Pdb prompt.
        ikiwa Pdb._previous_sigint_handler:
            try:
                signal.signal(signal.SIGINT, Pdb._previous_sigint_handler)
            except ValueError:  # ValueError: signal only works in main thread
                pass
            else:
                Pdb._previous_sigint_handler = None
        ikiwa self.setup(frame, traceback):
            # no interaction desired at this time (happens ikiwa .pdbrc contains
            # a command like "continue")
            self.forget()
            return
        self.print_stack_entry(self.stack[self.curindex])
        self._cmdloop()
        self.forget()

    eleza displayhook(self, obj):
        """Custom displayhook for the exec in default(), which prevents
        assignment of the _ variable in the builtins.
        """
        # reproduce the behavior of the standard displayhook, not printing None
        ikiwa obj is not None:
            self.message(repr(obj))

    eleza default(self, line):
        ikiwa line[:1] == '!': line = line[1:]
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        try:
            code = compile(line + '\n', '<stdin>', 'single')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                exec(code, globals, locals)
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())

    eleza precmd(self, line):
        """Handle alias expansion and ';;' separator."""
        ikiwa not line.strip():
            rudisha line
        args = line.split()
        while args[0] in self.aliases:
            line = self.aliases[args[0]]
            ii = 1
            for tmpArg in args[1:]:
                line = line.replace("%" + str(ii),
                                      tmpArg)
                ii += 1
            line = line.replace("%*", ' '.join(args[1:]))
            args = line.split()
        # split into ';;' separated commands
        # unless it's an alias command
        ikiwa args[0] != 'alias':
            marker = line.find(';;')
            ikiwa marker >= 0:
                # queue up everything after marker
                next = line[marker+2:].lstrip()
                self.cmdqueue.append(next)
                line = line[:marker].rstrip()
        rudisha line

    eleza onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        Checks whether this line is typed at the normal prompt or in
        a breakpoint command list definition.
        """
        ikiwa not self.commands_defining:
            rudisha cmd.Cmd.onecmd(self, line)
        else:
            rudisha self.handle_command_def(line)

    eleza handle_command_def(self, line):
        """Handles one command line during command list definition."""
        cmd, arg, line = self.parseline(line)
        ikiwa not cmd:
            return
        ikiwa cmd == 'silent':
            self.commands_silent[self.commands_bnum] = True
            rudisha # continue to handle other cmd eleza in the cmd list
        elikiwa cmd == 'end':
            self.cmdqueue = []
            rudisha 1 # end of cmd list
        cmdlist = self.commands[self.commands_bnum]
        ikiwa arg:
            cmdlist.append(cmd+' '+arg)
        else:
            cmdlist.append(cmd)
        # Determine ikiwa we must stop
        try:
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            func = self.default
        # one of the resuming commands
        ikiwa func.__name__ in self.commands_resuming:
            self.commands_doprompt[self.commands_bnum] = False
            self.cmdqueue = []
            rudisha 1
        return

    # interface abstraction functions

    eleza message(self, msg):
        andika(msg, file=self.stdout)

    eleza error(self, msg):
        andika('***', msg, file=self.stdout)

    # Generic completion functions.  Individual complete_foo methods can be
    # assigned below to one of these functions.

    eleza _complete_location(self, text, line, begidx, endidx):
        # Complete a file/module/function location for break/tbreak/clear.
        ikiwa line.strip().endswith((':', ',')):
            # Here comes a line number or a condition which we can't complete.
            rudisha []
        # First, try to find matching functions (i.e. expressions).
        try:
            ret = self._complete_expression(text, line, begidx, endidx)
        except Exception:
            ret = []
        # Then, try to complete file names as well.
        globs = glob.glob(text + '*')
        for fn in globs:
            ikiwa os.path.isdir(fn):
                ret.append(fn + '/')
            elikiwa os.path.isfile(fn) and fn.lower().endswith(('.py', '.pyw')):
                ret.append(fn + ':')
        rudisha ret

    eleza _complete_bpnumber(self, text, line, begidx, endidx):
        # Complete a breakpoint number.  (This would be more helpful ikiwa we could
        # display additional info along with the completions, such as file/line
        # of the breakpoint.)
        rudisha [str(i) for i, bp in enumerate(bdb.Breakpoint.bpbynumber)
                ikiwa bp is not None and str(i).startswith(text)]

    eleza _complete_expression(self, text, line, begidx, endidx):
        # Complete an arbitrary expression.
        ikiwa not self.curframe:
            rudisha []
        # Collect globals and locals.  It is usually not really sensible to also
        # complete builtins, and they clutter the namespace quite heavily, so we
        # leave them out.
        ns = {**self.curframe.f_globals, **self.curframe_locals}
        ikiwa '.' in text:
            # Walk an attribute chain up to the last part, similar to what
            # rlcompleter does.  This will bail ikiwa any of the parts are not
            # simple attribute access, which is what we want.
            dotted = text.split('.')
            try:
                obj = ns[dotted[0]]
                for part in dotted[1:-1]:
                    obj = getattr(obj, part)
            except (KeyError, AttributeError):
                rudisha []
            prefix = '.'.join(dotted[:-1]) + '.'
            rudisha [prefix + n for n in dir(obj) ikiwa n.startswith(dotted[-1])]
        else:
            # Complete a simple name.
            rudisha [n for n in ns.keys() ikiwa n.startswith(text)]

    # Command definitions, called by cmdloop()
    # The argument is the remaining string on the command line
    # Return true to exit kutoka the command loop

    eleza do_commands(self, arg):
        """commands [bpnumber]
        (com) ...
        (com) end
        (Pdb)

        Specify a list of commands for breakpoint number bpnumber.
        The commands themselves are entered on the following lines.
        Type a line containing just 'end' to terminate the commands.
        The commands are executed when the breakpoint is hit.

        To remove all commands kutoka a breakpoint, type commands and
        follow it immediately with end; that is, give no commands.

        With no bpnumber argument, commands refers to the last
        breakpoint set.

        You can use breakpoint commands to start your program up
        again.  Simply use the continue command, or step, or any other
        command that resumes execution.

        Specifying any command resuming execution (currently continue,
        step, next, return, jump, quit and their abbreviations)
        terminates the command list (as ikiwa that command was
        immediately followed by end).  This is because any time you
        resume execution (even with a simple next or step), you may
        encounter another breakpoint -- which could have its own
        command list, leading to ambiguities about which list to
        execute.

        If you use the 'silent' command in the command list, the usual
        message about stopping at a breakpoint is not printed.  This
        may be desirable for breakpoints that are to print a specific
        message and then continue.  If none of the other commands
        print anything, you will see no sign that the breakpoint was
        reached.
        """
        ikiwa not arg:
            bnum = len(bdb.Breakpoint.bpbynumber) - 1
        else:
            try:
                bnum = int(arg)
            except:
                self.error("Usage: commands [bnum]\n        ...\n        end")
                return
        self.commands_bnum = bnum
        # Save old definitions for the case of a keyboard interrupt.
        ikiwa bnum in self.commands:
            old_command_defs = (self.commands[bnum],
                                self.commands_doprompt[bnum],
                                self.commands_silent[bnum])
        else:
            old_command_defs = None
        self.commands[bnum] = []
        self.commands_doprompt[bnum] = True
        self.commands_silent[bnum] = False

        prompt_back = self.prompt
        self.prompt = '(com) '
        self.commands_defining = True
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            # Restore old definitions.
            ikiwa old_command_defs:
                self.commands[bnum] = old_command_defs[0]
                self.commands_doprompt[bnum] = old_command_defs[1]
                self.commands_silent[bnum] = old_command_defs[2]
            else:
                del self.commands[bnum]
                del self.commands_doprompt[bnum]
                del self.commands_silent[bnum]
            self.error('command definition aborted, old commands restored')
        finally:
            self.commands_defining = False
            self.prompt = prompt_back

    complete_commands = _complete_bpnumber

    eleza do_break(self, arg, temporary = 0):
        """b(reak) [ ([filename:]lineno | function) [, condition] ]
        Without argument, list all breaks.

        With a line number argument, set a break at this line in the
        current file.  With a function name, set a break at the first
        executable line of that function.  If a second argument is
        present, it is a string specifying an expression which must
        evaluate to true before the breakpoint is honored.

        The line number may be prefixed with a filename and a colon,
        to specify a breakpoint in another file (probably one that
        hasn't been loaded yet).  The file is searched for on
        sys.path; the .py suffix may be omitted.
        """
        ikiwa not arg:
            ikiwa self.breaks:  # There's at least one
                self.message("Num Type         Disp Enb   Where")
                for bp in bdb.Breakpoint.bpbynumber:
                    ikiwa bp:
                        self.message(bp.bpformat())
            return
        # parse arguments; comma has lowest precedence
        # and cannot occur in filename
        filename = None
        lineno = None
        cond = None
        comma = arg.find(',')
        ikiwa comma > 0:
            # parse stuff after comma: "condition"
            cond = arg[comma+1:].lstrip()
            arg = arg[:comma].rstrip()
        # parse stuff before comma: [filename:]lineno | function
        colon = arg.rfind(':')
        funcname = None
        ikiwa colon >= 0:
            filename = arg[:colon].rstrip()
            f = self.lookupmodule(filename)
            ikiwa not f:
                self.error('%r not found kutoka sys.path' % filename)
                return
            else:
                filename = f
            arg = arg[colon+1:].lstrip()
            try:
                lineno = int(arg)
            except ValueError:
                self.error('Bad lineno: %s' % arg)
                return
        else:
            # no colon; can be lineno or function
            try:
                lineno = int(arg)
            except ValueError:
                try:
                    func = eval(arg,
                                self.curframe.f_globals,
                                self.curframe_locals)
                except:
                    func = arg
                try:
                    ikiwa hasattr(func, '__func__'):
                        func = func.__func__
                    code = func.__code__
                    #use co_name to identify the bkpt (function names
                    #could be aliased, but co_name is invariant)
                    funcname = code.co_name
                    lineno = code.co_firstlineno
                    filename = code.co_filename
                except:
                    # last thing to try
                    (ok, filename, ln) = self.lineinfo(arg)
                    ikiwa not ok:
                        self.error('The specified object %r is not a function '
                                   'or was not found along sys.path.' % arg)
                        return
                    funcname = ok # ok contains a function name
                    lineno = int(ln)
        ikiwa not filename:
            filename = self.defaultFile()
        # Check for reasonable breakpoint
        line = self.checkline(filename, lineno)
        ikiwa line:
            # now set the break point
            err = self.set_break(filename, line, temporary, cond, funcname)
            ikiwa err:
                self.error(err)
            else:
                bp = self.get_breaks(filename, line)[-1]
                self.message("Breakpoint %d at %s:%d" %
                             (bp.number, bp.file, bp.line))

    # To be overridden in derived debuggers
    eleza defaultFile(self):
        """Produce a reasonable default."""
        filename = self.curframe.f_code.co_filename
        ikiwa filename == '<string>' and self.mainpyfile:
            filename = self.mainpyfile
        rudisha filename

    do_b = do_break

    complete_break = _complete_location
    complete_b = _complete_location

    eleza do_tbreak(self, arg):
        """tbreak [ ([filename:]lineno | function) [, condition] ]
        Same arguments as break, but sets a temporary breakpoint: it
        is automatically deleted when first hit.
        """
        self.do_break(arg, 1)

    complete_tbreak = _complete_location

    eleza lineinfo(self, identifier):
        failed = (None, None, None)
        # Input is identifier, may be in single quotes
        idstring = identifier.split("'")
        ikiwa len(idstring) == 1:
            # not in single quotes
            id = idstring[0].strip()
        elikiwa len(idstring) == 3:
            # quoted
            id = idstring[1].strip()
        else:
            rudisha failed
        ikiwa id == '': rudisha failed
        parts = id.split('.')
        # Protection for derived debuggers
        ikiwa parts[0] == 'self':
            del parts[0]
            ikiwa len(parts) == 0:
                rudisha failed
        # Best first guess at file to look at
        fname = self.defaultFile()
        ikiwa len(parts) == 1:
            item = parts[0]
        else:
            # More than one part.
            # First is module, second is method/class
            f = self.lookupmodule(parts[0])
            ikiwa f:
                fname = f
            item = parts[1]
        answer = find_function(item, fname)
        rudisha answer or failed

    eleza checkline(self, filename, lineno):
        """Check whether specified line seems to be executable.

        Return `lineno` ikiwa it is, 0 ikiwa not (e.g. a docstring, comment, blank
        line or EOF). Warning: testing is not comprehensive.
        """
        # this method should be callable before starting debugging, so default
        # to "no globals" ikiwa there is no current frame
        globs = self.curframe.f_globals ikiwa hasattr(self, 'curframe') else None
        line = linecache.getline(filename, lineno, globs)
        ikiwa not line:
            self.message('End of file')
            rudisha 0
        line = line.strip()
        # Don't allow setting breakpoint at a blank line
        ikiwa (not line or (line[0] == '#') or
             (line[:3] == '"""') or line[:3] == "'''"):
            self.error('Blank or comment')
            rudisha 0
        rudisha lineno

    eleza do_enable(self, arg):
        """enable bpnumber [bpnumber ...]
        Enables the breakpoints given as a space separated list of
        breakpoint numbers.
        """
        args = arg.split()
        for i in args:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError as err:
                self.error(err)
            else:
                bp.enable()
                self.message('Enabled %s' % bp)

    complete_enable = _complete_bpnumber

    eleza do_disable(self, arg):
        """disable bpnumber [bpnumber ...]
        Disables the breakpoints given as a space separated list of
        breakpoint numbers.  Disabling a breakpoint means it cannot
        cause the program to stop execution, but unlike clearing a
        breakpoint, it remains in the list of breakpoints and can be
        (re-)enabled.
        """
        args = arg.split()
        for i in args:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError as err:
                self.error(err)
            else:
                bp.disable()
                self.message('Disabled %s' % bp)

    complete_disable = _complete_bpnumber

    eleza do_condition(self, arg):
        """condition bpnumber [condition]
        Set a new condition for the breakpoint, an expression which
        must evaluate to true before the breakpoint is honored.  If
        condition is absent, any existing condition is removed; i.e.,
        the breakpoint is made unconditional.
        """
        args = arg.split(' ', 1)
        try:
            cond = args[1]
        except IndexError:
            cond = None
        try:
            bp = self.get_bpbynumber(args[0].strip())
        except IndexError:
            self.error('Breakpoint number expected')
        except ValueError as err:
            self.error(err)
        else:
            bp.cond = cond
            ikiwa not cond:
                self.message('Breakpoint %d is now unconditional.' % bp.number)
            else:
                self.message('New condition set for breakpoint %d.' % bp.number)

    complete_condition = _complete_bpnumber

    eleza do_ignore(self, arg):
        """ignore bpnumber [count]
        Set the ignore count for the given breakpoint number.  If
        count is omitted, the ignore count is set to 0.  A breakpoint
        becomes active when the ignore count is zero.  When non-zero,
        the count is decremented each time the breakpoint is reached
        and the breakpoint is not disabled and any associated
        condition evaluates to true.
        """
        args = arg.split()
        try:
            count = int(args[1].strip())
        except:
            count = 0
        try:
            bp = self.get_bpbynumber(args[0].strip())
        except IndexError:
            self.error('Breakpoint number expected')
        except ValueError as err:
            self.error(err)
        else:
            bp.ignore = count
            ikiwa count > 0:
                ikiwa count > 1:
                    countstr = '%d crossings' % count
                else:
                    countstr = '1 crossing'
                self.message('Will ignore next %s of breakpoint %d.' %
                             (countstr, bp.number))
            else:
                self.message('Will stop next time breakpoint %d is reached.'
                             % bp.number)

    complete_ignore = _complete_bpnumber

    eleza do_clear(self, arg):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        ikiwa not arg:
            try:
                reply = input('Clear all breaks? ')
            except EOFError:
                reply = 'no'
            reply = reply.strip().lower()
            ikiwa reply in ('y', 'yes'):
                bplist = [bp for bp in bdb.Breakpoint.bpbynumber ikiwa bp]
                self.clear_all_breaks()
                for bp in bplist:
                    self.message('Deleted %s' % bp)
            return
        ikiwa ':' in arg:
            # Make sure it works for "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            try:
                lineno = int(arg)
            except ValueError:
                err = "Invalid line number (%s)" % arg
            else:
                bplist = self.get_breaks(filename, lineno)
                err = self.clear_break(filename, lineno)
            ikiwa err:
                self.error(err)
            else:
                for bp in bplist:
                    self.message('Deleted %s' % bp)
            return
        numberlist = arg.split()
        for i in numberlist:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError as err:
                self.error(err)
            else:
                self.clear_bpbynumber(i)
                self.message('Deleted %s' % bp)
    do_cl = do_clear # 'c' is already an abbreviation for 'continue'

    complete_clear = _complete_location
    complete_cl = _complete_location

    eleza do_where(self, arg):
        """w(here)
        Print a stack trace, with the most recent frame at the bottom.
        An arrow indicates the "current frame", which determines the
        context of most commands.  'bt' is an alias for this command.
        """
        self.print_stack_trace()
    do_w = do_where
    do_bt = do_where

    eleza _select_frame(self, number):
        assert 0 <= number < len(self.stack)
        self.curindex = number
        self.curframe = self.stack[self.curindex][0]
        self.curframe_locals = self.curframe.f_locals
        self.print_stack_entry(self.stack[self.curindex])
        self.lineno = None

    eleza do_up(self, arg):
        """u(p) [count]
        Move the current frame count (default one) levels up in the
        stack trace (to an older frame).
        """
        ikiwa self.curindex == 0:
            self.error('Oldest frame')
            return
        try:
            count = int(arg or 1)
        except ValueError:
            self.error('Invalid frame count (%s)' % arg)
            return
        ikiwa count < 0:
            newframe = 0
        else:
            newframe = max(0, self.curindex - count)
        self._select_frame(newframe)
    do_u = do_up

    eleza do_down(self, arg):
        """d(own) [count]
        Move the current frame count (default one) levels down in the
        stack trace (to a newer frame).
        """
        ikiwa self.curindex + 1 == len(self.stack):
            self.error('Newest frame')
            return
        try:
            count = int(arg or 1)
        except ValueError:
            self.error('Invalid frame count (%s)' % arg)
            return
        ikiwa count < 0:
            newframe = len(self.stack) - 1
        else:
            newframe = min(len(self.stack) - 1, self.curindex + count)
        self._select_frame(newframe)
    do_d = do_down

    eleza do_until(self, arg):
        """unt(il) [lineno]
        Without argument, continue execution until the line with a
        number greater than the current one is reached.  With a line
        number, continue execution until a line with a number greater
        or equal to that is reached.  In both cases, also stop when
        the current frame returns.
        """
        ikiwa arg:
            try:
                lineno = int(arg)
            except ValueError:
                self.error('Error in argument: %r' % arg)
                return
            ikiwa lineno <= self.curframe.f_lineno:
                self.error('"until" line number is smaller than current '
                           'line number')
                return
        else:
            lineno = None
        self.set_until(self.curframe, lineno)
        rudisha 1
    do_unt = do_until

    eleza do_step(self, arg):
        """s(tep)
        Execute the current line, stop at the first possible occasion
        (either in a function that is called or in the current
        function).
        """
        self.set_step()
        rudisha 1
    do_s = do_step

    eleza do_next(self, arg):
        """n(ext)
        Continue execution until the next line in the current function
        is reached or it returns.
        """
        self.set_next(self.curframe)
        rudisha 1
    do_n = do_next

    eleza do_run(self, arg):
        """run [args...]
        Restart the debugged python program. If a string is supplied
        it is split with "shlex", and the result is used as the new
        sys.argv.  History, breakpoints, actions and debugger options
        are preserved.  "restart" is an alias for "run".
        """
        ikiwa arg:
            agiza shlex
            argv0 = sys.argv[0:1]
            sys.argv = shlex.split(arg)
            sys.argv[:0] = argv0
        # this is caught in the main debugger loop
        raise Restart

    do_restart = do_run

    eleza do_return(self, arg):
        """r(eturn)
        Continue execution until the current function returns.
        """
        self.set_return(self.curframe)
        rudisha 1
    do_r = do_return

    eleza do_continue(self, arg):
        """c(ont(inue))
        Continue execution, only stop when a breakpoint is encountered.
        """
        ikiwa not self.nosigint:
            try:
                Pdb._previous_sigint_handler = \
                    signal.signal(signal.SIGINT, self.sigint_handler)
            except ValueError:
                # ValueError happens when do_continue() is invoked kutoka
                # a non-main thread in which case we just continue without
                # SIGINT set. Would printing a message here (once) make
                # sense?
                pass
        self.set_continue()
        rudisha 1
    do_c = do_cont = do_continue

    eleza do_jump(self, arg):
        """j(ump) lineno
        Set the next line that will be executed.  Only available in
        the bottom-most frame.  This lets you jump back and execute
        code again, or jump forward to skip code that you don't want
        to run.

        It should be noted that not all jumps are allowed -- for
        instance it is not possible to jump into the middle of a
        for loop or out of a finally clause.
        """
        ikiwa self.curindex + 1 != len(self.stack):
            self.error('You can only jump within the bottom frame')
            return
        try:
            arg = int(arg)
        except ValueError:
            self.error("The 'jump' command requires a line number")
        else:
            try:
                # Do the jump, fix up our copy of the stack, and display the
                # new position
                self.curframe.f_lineno = arg
                self.stack[self.curindex] = self.stack[self.curindex][0], arg
                self.print_stack_entry(self.stack[self.curindex])
            except ValueError as e:
                self.error('Jump failed: %s' % e)
    do_j = do_jump

    eleza do_debug(self, arg):
        """debug code
        Enter a recursive debugger that steps through the code
        argument (which is an arbitrary expression or statement to be
        executed in the current environment).
        """
        sys.settrace(None)
        globals = self.curframe.f_globals
        locals = self.curframe_locals
        p = Pdb(self.completekey, self.stdin, self.stdout)
        p.prompt = "(%s) " % self.prompt.strip()
        self.message("ENTERING RECURSIVE DEBUGGER")
        try:
            sys.call_tracing(p.run, (arg, globals, locals))
        except Exception:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())
        self.message("LEAVING RECURSIVE DEBUGGER")
        sys.settrace(self.trace_dispatch)
        self.lastcmd = p.lastcmd

    complete_debug = _complete_expression

    eleza do_quit(self, arg):
        """q(uit)\nexit
        Quit kutoka the debugger. The program being executed is aborted.
        """
        self._user_requested_quit = True
        self.set_quit()
        rudisha 1

    do_q = do_quit
    do_exit = do_quit

    eleza do_EOF(self, arg):
        """EOF
        Handles the receipt of EOF as a command.
        """
        self.message('')
        self._user_requested_quit = True
        self.set_quit()
        rudisha 1

    eleza do_args(self, arg):
        """a(rgs)
        Print the argument list of the current function.
        """
        co = self.curframe.f_code
        dict = self.curframe_locals
        n = co.co_argcount + co.co_kwonlyargcount
        ikiwa co.co_flags & inspect.CO_VARARGS: n = n+1
        ikiwa co.co_flags & inspect.CO_VARKEYWORDS: n = n+1
        for i in range(n):
            name = co.co_varnames[i]
            ikiwa name in dict:
                self.message('%s = %r' % (name, dict[name]))
            else:
                self.message('%s = *** undefined ***' % (name,))
    do_a = do_args

    eleza do_retval(self, arg):
        """retval
        Print the rudisha value for the last rudisha of a function.
        """
        ikiwa '__return__' in self.curframe_locals:
            self.message(repr(self.curframe_locals['__return__']))
        else:
            self.error('Not yet returned!')
    do_rv = do_retval

    eleza _getval(self, arg):
        try:
            rudisha eval(arg, self.curframe.f_globals, self.curframe_locals)
        except:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())
            raise

    eleza _getval_except(self, arg, frame=None):
        try:
            ikiwa frame is None:
                rudisha eval(arg, self.curframe.f_globals, self.curframe_locals)
            else:
                rudisha eval(arg, frame.f_globals, frame.f_locals)
        except:
            exc_info = sys.exc_info()[:2]
            err = traceback.format_exception_only(*exc_info)[-1].strip()
            rudisha _rstr('** raised %s **' % err)

    eleza do_p(self, arg):
        """p expression
        Print the value of the expression.
        """
        try:
            self.message(repr(self._getval(arg)))
        except:
            pass

    eleza do_pp(self, arg):
        """pp expression
        Pretty-print the value of the expression.
        """
        try:
            self.message(pprint.pformat(self._getval(arg)))
        except:
            pass

    complete_print = _complete_expression
    complete_p = _complete_expression
    complete_pp = _complete_expression

    eleza do_list(self, arg):
        """l(ist) [first [,last] | .]

        List source code for the current file.  Without arguments,
        list 11 lines around the current line or continue the previous
        listing.  With . as argument, list 11 lines around the current
        line.  With one argument, list 11 lines starting at that line.
        With two arguments, list the given range; ikiwa the second
        argument is less than the first, it is a count.

        The current line in the current frame is indicated by "->".
        If an exception is being debugged, the line where the
        exception was originally raised or propagated is indicated by
        ">>", ikiwa it differs kutoka the current line.
        """
        self.lastcmd = 'list'
        last = None
        ikiwa arg and arg != '.':
            try:
                ikiwa ',' in arg:
                    first, last = arg.split(',')
                    first = int(first.strip())
                    last = int(last.strip())
                    ikiwa last < first:
                        # assume it's a count
                        last = first + last
                else:
                    first = int(arg.strip())
                    first = max(1, first - 5)
            except ValueError:
                self.error('Error in argument: %r' % arg)
                return
        elikiwa self.lineno is None or arg == '.':
            first = max(1, self.curframe.f_lineno - 5)
        else:
            first = self.lineno + 1
        ikiwa last is None:
            last = first + 10
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            lines = linecache.getlines(filename, self.curframe.f_globals)
            self._print_lines(lines[first-1:last], first, breaklist,
                              self.curframe)
            self.lineno = min(last, len(lines))
            ikiwa len(lines) < last:
                self.message('[EOF]')
        except KeyboardInterrupt:
            pass
    do_l = do_list

    eleza do_longlist(self, arg):
        """longlist | ll
        List the whole source code for the current function or frame.
        """
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            lines, lineno = getsourcelines(self.curframe)
        except OSError as err:
            self.error(err)
            return
        self._print_lines(lines, lineno, breaklist, self.curframe)
    do_ll = do_longlist

    eleza do_source(self, arg):
        """source expression
        Try to get source code for the given object and display it.
        """
        try:
            obj = self._getval(arg)
        except:
            return
        try:
            lines, lineno = getsourcelines(obj)
        except (OSError, TypeError) as err:
            self.error(err)
            return
        self._print_lines(lines, lineno)

    complete_source = _complete_expression

    eleza _print_lines(self, lines, start, breaks=(), frame=None):
        """Print a range of lines."""
        ikiwa frame:
            current_lineno = frame.f_lineno
            exc_lineno = self.tb_lineno.get(frame, -1)
        else:
            current_lineno = exc_lineno = -1
        for lineno, line in enumerate(lines, start):
            s = str(lineno).rjust(3)
            ikiwa len(s) < 4:
                s += ' '
            ikiwa lineno in breaks:
                s += 'B'
            else:
                s += ' '
            ikiwa lineno == current_lineno:
                s += '->'
            elikiwa lineno == exc_lineno:
                s += '>>'
            self.message(s + '\t' + line.rstrip())

    eleza do_whatis(self, arg):
        """whatis arg
        Print the type of the argument.
        """
        try:
            value = self._getval(arg)
        except:
            # _getval() already printed the error
            return
        code = None
        # Is it a function?
        try:
            code = value.__code__
        except Exception:
            pass
        ikiwa code:
            self.message('Function %s' % code.co_name)
            return
        # Is it an instance method?
        try:
            code = value.__func__.__code__
        except Exception:
            pass
        ikiwa code:
            self.message('Method %s' % code.co_name)
            return
        # Is it a class?
        ikiwa value.__class__ is type:
            self.message('Class %s.%s' % (value.__module__, value.__qualname__))
            return
        # None of the above...
        self.message(type(value))

    complete_whatis = _complete_expression

    eleza do_display(self, arg):
        """display [expression]

        Display the value of the expression ikiwa it changed, each time execution
        stops in the current frame.

        Without expression, list all display expressions for the current frame.
        """
        ikiwa not arg:
            self.message('Currently displaying:')
            for item in self.displaying.get(self.curframe, {}).items():
                self.message('%s: %r' % item)
        else:
            val = self._getval_except(arg)
            self.displaying.setdefault(self.curframe, {})[arg] = val
            self.message('display %s: %r' % (arg, val))

    complete_display = _complete_expression

    eleza do_undisplay(self, arg):
        """undisplay [expression]

        Do not display the expression any more in the current frame.

        Without expression, clear all display expressions for the current frame.
        """
        ikiwa arg:
            try:
                del self.displaying.get(self.curframe, {})[arg]
            except KeyError:
                self.error('not displaying %s' % arg)
        else:
            self.displaying.pop(self.curframe, None)

    eleza complete_undisplay(self, text, line, begidx, endidx):
        rudisha [e for e in self.displaying.get(self.curframe, {})
                ikiwa e.startswith(text)]

    eleza do_interact(self, arg):
        """interact

        Start an interactive interpreter whose global namespace
        contains all the (global and local) names found in the current scope.
        """
        ns = {**self.curframe.f_globals, **self.curframe_locals}
        code.interact("*interactive*", local=ns)

    eleza do_alias(self, arg):
        """alias [name [command [parameter parameter ...] ]]
        Create an alias called 'name' that executes 'command'.  The
        command must *not* be enclosed in quotes.  Replaceable
        parameters can be indicated by %1, %2, and so on, while %* is
        replaced by all the parameters.  If no command is given, the
        current alias for name is shown. If no name is given, all
        aliases are listed.

        Aliases may be nested and can contain anything that can be
        legally typed at the pdb prompt.  Note!  You *can* override
        internal pdb commands with aliases!  Those internal commands
        are then hidden until the alias is removed.  Aliasing is
        recursively applied to the first word of the command line; all
        other words in the line are left alone.

        As an example, here are two useful aliases (especially when
        placed in the .pdbrc file):

        # Print instance variables (usage "pi classInst")
        alias pi for k in %1.__dict__.keys(): andika("%1.",k,"=",%1.__dict__[k])
        # Print instance variables in self
        alias ps pi self
        """
        args = arg.split()
        ikiwa len(args) == 0:
            keys = sorted(self.aliases.keys())
            for alias in keys:
                self.message("%s = %s" % (alias, self.aliases[alias]))
            return
        ikiwa args[0] in self.aliases and len(args) == 1:
            self.message("%s = %s" % (args[0], self.aliases[args[0]]))
        else:
            self.aliases[args[0]] = ' '.join(args[1:])

    eleza do_unalias(self, arg):
        """unalias name
        Delete the specified alias.
        """
        args = arg.split()
        ikiwa len(args) == 0: return
        ikiwa args[0] in self.aliases:
            del self.aliases[args[0]]

    eleza complete_unalias(self, text, line, begidx, endidx):
        rudisha [a for a in self.aliases ikiwa a.startswith(text)]

    # List of all the commands making the program resume execution.
    commands_resuming = ['do_continue', 'do_step', 'do_next', 'do_return',
                         'do_quit', 'do_jump']

    # Print a traceback starting at the top stack frame.
    # The most recently entered frame is printed last;
    # this is different kutoka dbx and gdb, but consistent with
    # the Python interpreter's stack trace.
    # It is also consistent with the up/down commands (which are
    # compatible with dbx and gdb: up moves towards 'main()'
    # and down moves towards the most recent stack frame).

    eleza print_stack_trace(self):
        try:
            for frame_lineno in self.stack:
                self.print_stack_entry(frame_lineno)
        except KeyboardInterrupt:
            pass

    eleza print_stack_entry(self, frame_lineno, prompt_prefix=line_prefix):
        frame, lineno = frame_lineno
        ikiwa frame is self.curframe:
            prefix = '> '
        else:
            prefix = '  '
        self.message(prefix +
                     self.format_stack_entry(frame_lineno, prompt_prefix))

    # Provide help

    eleza do_help(self, arg):
        """h(elp)
        Without argument, print the list of available commands.
        With a command name as argument, print help about that command.
        "help pdb" shows the full pdb documentation.
        "help exec" gives help on the ! command.
        """
        ikiwa not arg:
            rudisha cmd.Cmd.do_help(self, arg)
        try:
            try:
                topic = getattr(self, 'help_' + arg)
                rudisha topic()
            except AttributeError:
                command = getattr(self, 'do_' + arg)
        except AttributeError:
            self.error('No help for %r' % arg)
        else:
            ikiwa sys.flags.optimize >= 2:
                self.error('No help for %r; please do not run Python with -OO '
                           'ikiwa you need command help' % arg)
                return
            self.message(command.__doc__.rstrip())

    do_h = do_help

    eleza help_exec(self):
        """(!) statement
        Execute the (one-line) statement in the context of the current
        stack frame.  The exclamation point can be omitted unless the
        first word of the statement resembles a debugger command.  To
        assign to a global variable you must always prefix the command
        with a 'global' command, e.g.:
        (Pdb) global list_options; list_options = ['-l']
        (Pdb)
        """
        self.message((self.help_exec.__doc__ or '').strip())

    eleza help_pdb(self):
        help()

    # other helper functions

    eleza lookupmodule(self, filename):
        """Helper function for break/clear parsing -- may be overridden.

        lookupmodule() translates (possibly incomplete) file or module name
        into an absolute file name.
        """
        ikiwa os.path.isabs(filename) and  os.path.exists(filename):
            rudisha filename
        f = os.path.join(sys.path[0], filename)
        ikiwa  os.path.exists(f) and self.canonic(f) == self.mainpyfile:
            rudisha f
        root, ext = os.path.splitext(filename)
        ikiwa ext == '':
            filename = filename + '.py'
        ikiwa os.path.isabs(filename):
            rudisha filename
        for dirname in sys.path:
            while os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            ikiwa os.path.exists(fullname):
                rudisha fullname
        rudisha None

    eleza _runmodule(self, module_name):
        self._wait_for_mainpyfile = True
        self._user_requested_quit = False
        agiza runpy
        mod_name, mod_spec, code = runpy._get_module_details(module_name)
        self.mainpyfile = self.canonic(code.co_filename)
        agiza __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({
            "__name__": "__main__",
            "__file__": self.mainpyfile,
            "__package__": mod_spec.parent,
            "__loader__": mod_spec.loader,
            "__spec__": mod_spec,
            "__builtins__": __builtins__,
        })
        self.run(code)

    eleza _runscript(self, filename):
        # The script has to run in __main__ namespace (or agizas kutoka
        # __main__ will break).
        #
        # So we clear up the __main__ and set several special variables
        # (this gets rid of pdb's globals and cleans old variables on restarts).
        agiza __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": __builtins__,
                                 })

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = False
        with open(filename, "rb") as fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)

# Collect all command help into docstring, ikiwa not run with -OO

ikiwa __doc__ is not None:
    # unfortunately we can't guess this order kutoka the kundi definition
    _help_order = [
        'help', 'where', 'down', 'up', 'break', 'tbreak', 'clear', 'disable',
        'enable', 'ignore', 'condition', 'commands', 'step', 'next', 'until',
        'jump', 'return', 'retval', 'run', 'continue', 'list', 'longlist',
        'args', 'p', 'pp', 'whatis', 'source', 'display', 'undisplay',
        'interact', 'alias', 'unalias', 'debug', 'quit',
    ]

    for _command in _help_order:
        __doc__ += getattr(Pdb, 'do_' + _command).__doc__.strip() + '\n\n'
    __doc__ += Pdb.help_exec.__doc__

    del _help_order, _command


# Simplified interface

eleza run(statement, globals=None, locals=None):
    Pdb().run(statement, globals, locals)

eleza runeval(expression, globals=None, locals=None):
    rudisha Pdb().runeval(expression, globals, locals)

eleza runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

eleza runcall(*args, **kwds):
    rudisha Pdb().runcall(*args, **kwds)

eleza set_trace(*, header=None):
    pdb = Pdb()
    ikiwa header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)

# Post-Mortem interface

eleza post_mortem(t=None):
    # handling the default
    ikiwa t is None:
        # sys.exc_info() returns (type, value, traceback) ikiwa an exception is
        # being handled, otherwise it returns None
        t = sys.exc_info()[2]
    ikiwa t is None:
        raise ValueError("A valid traceback must be passed ikiwa no "
                         "exception is being handled")

    p = Pdb()
    p.reset()
    p.interaction(None, t)

eleza pm():
    post_mortem(sys.last_traceback)


# Main program for testing

TESTCMD = 'agiza x; x.main()'

eleza test():
    run(TESTCMD)

# print help
eleza help():
    agiza pydoc
    pydoc.pager(__doc__)

_usage = """\
usage: pdb.py [-c command] ... [-m module | pyfile] [arg] ...

Debug the Python program given by pyfile. Alternatively,
an executable module or package to debug can be specified using
the -m switch.

Initial commands are read kutoka .pdbrc files in your home directory
and in the current directory, ikiwa they exist.  Commands supplied with
-c are executed after commands kutoka .pdbrc files.

To let the script run until an exception occurs, use "-c continue".
To let the script run up to a given line X in the debugged file, use
"-c 'until X'"."""

eleza main():
    agiza getopt

    opts, args = getopt.getopt(sys.argv[1:], 'mhc:', ['help', 'command='])

    ikiwa not args:
        andika(_usage)
        sys.exit(2)

    commands = []
    run_as_module = False
    for opt, optarg in opts:
        ikiwa opt in ['-h', '--help']:
            andika(_usage)
            sys.exit()
        elikiwa opt in ['-c', '--command']:
            commands.append(optarg)
        elikiwa opt in ['-m']:
            run_as_module = True

    mainpyfile = args[0]     # Get script filename
    ikiwa not run_as_module and not os.path.exists(mainpyfile):
        andika('Error:', mainpyfile, 'does not exist')
        sys.exit(1)

    sys.argv[:] = args      # Hide "pdb.py" and pdb options kutoka argument list

    # Replace pdb's dir with script's dir in front of module search path.
    ikiwa not run_as_module:
        sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user kutoka the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = Pdb()
    pdb.rcLines.extend(commands)
    while True:
        try:
            ikiwa run_as_module:
                pdb._runmodule(mainpyfile)
            else:
                pdb._runscript(mainpyfile)
            ikiwa pdb._user_requested_quit:
                break
            andika("The program finished and will be restarted")
        except Restart:
            andika("Restarting", mainpyfile, "with arguments:")
            andika("\t" + " ".join(args))
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            andika("The program exited via sys.exit(). Exit status:", end=' ')
            andika(sys.exc_info()[1])
        except SyntaxError:
            traceback.print_exc()
            sys.exit(1)
        except:
            traceback.print_exc()
            andika("Uncaught exception. Entering post mortem debugging")
            andika("Running 'cont' or 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(None, t)
            andika("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")


# When invoked as main program, invoke the debugger on a script
ikiwa __name__ == '__main__':
    agiza pdb
    pdb.main()
