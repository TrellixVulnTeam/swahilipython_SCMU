#! /usr/bin/env python3

"""
The Python Debugger Pdb
=======================

To use the debugger kwenye its simplest form:

        >>> agiza pdb
        >>> pdb.run('<a statement>')

The debugger's prompt ni '(Pdb) '.  This will stop kwenye the first
function call kwenye <a statement>.

Alternatively, ikiwa a statement terminated with an unhandled exception,
you can use pdb's post-mortem facility to inspect the contents of the
traceback:

        >>> <a statement>
        <exception traceback>
        >>> agiza pdb
        >>> pdb.pm()

The commands recognized by the debugger are listed kwenye the next
section.  Most can be abbreviated kama indicated; e.g., h(elp) means
that 'help' can be typed kama 'h' ama 'help' (but sio kama 'he' ama 'hel',
nor kama 'H' ama 'Help' ama 'HELP').  Optional arguments are enclosed in
square brackets.  Alternatives kwenye the command syntax are separated
by a vertical bar (|).

A blank line repeats the previous command literally, tatizo for
'list', where it lists the next 11 lines.

Commands that the debugger doesn't recognize are assumed to be Python
statements na are executed kwenye the context of the program being
debugged.  Python statements can also be prefixed with an exclamation
point ('!').  This ni a powerful way to inspect the program being
debugged; it ni even possible to change variables ama call functions.
When an exception occurs kwenye such a statement, the exception name is
printed but the debugger's state ni sio changed.

The debugger supports aliases, which can save typing.  And aliases can
have parameters (see the alias help entry) which allows one a certain
level of adaptability to the context under examination.

Multiple commands may be entered on a single line, separated by the
pair ';;'.  No intelligence ni applied to separating the commands; the
input ni split at the first ';;', even ikiwa it ni kwenye the middle of a
quoted string.

If a file ".pdbrc" exists kwenye your home directory ama kwenye the current
directory, it ni read kwenye na executed kama ikiwa it had been typed at the
debugger prompt.  This ni particularly useful kila aliases.  If both
files exist, the one kwenye the home directory ni read first na aliases
defined there can be overridden by the local file.  This behavior can be
disabled by pitaing the "readrc=Uongo" argument to the Pdb constructor.

Aside kutoka aliases, the debugger ni sio directly programmable; but it
is implemented kama a kundi kutoka which you can derive your own debugger
class, which you can make kama fancy kama you like.


Debugger commands
=================

"""
# NOTE: the actual command documentation ni collected kutoka docstrings of the
# commands na ni appended to __doc__ after the kundi has been defined.

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
    """Causes a debugger to be restarted kila the debugged python program."""
    pita

__all__ = ["run", "pm", "Pdb", "runeval", "runctx", "runcall", "set_trace",
           "post_mortem", "help"]

eleza find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % re.escape(funcname))
    jaribu:
        fp = open(filename)
    tatizo OSError:
        rudisha Tupu
    # consumer of this info expects the first line to be 1
    with fp:
        kila lineno, line kwenye enumerate(fp, start=1):
            ikiwa cre.match(line):
                rudisha funcname, filename, lineno
    rudisha Tupu

eleza getsourcelines(obj):
    lines, lineno = inspect.findsource(obj)
    ikiwa inspect.isframe(obj) na obj.f_globals ni obj.f_locals:
        # must be a module frame: do sio try to cut a block out of it
        rudisha lines, 1
    elikiwa inspect.ismodule(obj):
        rudisha lines, 1
    rudisha inspect.getblock(lines[lineno:]), lineno+1

eleza lasti2lineno(code, lasti):
    linestarts = list(dis.findlinestarts(code))
    linestarts.reverse()
    kila i, lineno kwenye linestarts:
        ikiwa lasti >= i:
            rudisha lineno
    rudisha 0


kundi _rstr(str):
    """String that doesn't quote its repr."""
    eleza __repr__(self):
        rudisha self


# Interaction prompt line will separate file na call info kutoka code
# text using value of line_prefix string.  A newline na arrow may
# be to your liking.  You can set it once pdb ni imported using the
# command "pdb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

kundi Pdb(bdb.Bdb, cmd.Cmd):

    _previous_sigint_handler = Tupu

    eleza __init__(self, completekey='tab', stdin=Tupu, stdout=Tupu, skip=Tupu,
                 nosigint=Uongo, readrc=Kweli):
        bdb.Bdb.__init__(self, skip=skip)
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        sys.audit("pdb.Pdb")
        ikiwa stdout:
            self.use_rawinput = 0
        self.prompt = '(Pdb) '
        self.aliases = {}
        self.displaying = {}
        self.mainpyfile = ''
        self._wait_for_mainpyfile = Uongo
        self.tb_lineno = {}
        # Try to load readline ikiwa it exists
        jaribu:
            agiza readline
            # remove some common file name delimiters
            readline.set_completer_delims(' \t\n`@#$%^&*()=+[{]}\\|;:\'",<>?')
        tatizo ImportError:
            pita
        self.allow_kbdint = Uongo
        self.nosigint = nosigint

        # Read ~/.pdbrc na ./.pdbrc
        self.rcLines = []
        ikiwa readrc:
            jaribu:
                with open(os.path.expanduser('~/.pdbrc')) kama rcFile:
                    self.rcLines.extend(rcFile)
            tatizo OSError:
                pita
            jaribu:
                with open(".pdbrc") kama rcFile:
                    self.rcLines.extend(rcFile)
            tatizo OSError:
                pita

        self.commands = {} # associates a command list to komapoint numbers
        self.commands_doprompt = {} # kila each bp num, tells ikiwa the prompt
                                    # must be disp. after execing the cmd list
        self.commands_silent = {} # kila each bp num, tells ikiwa the stack trace
                                  # must be disp. after execing the cmd list
        self.commands_defining = Uongo # Kweli wakati kwenye the process of defining
                                       # a command list
        self.commands_bnum = Tupu # The komapoint number kila which we are
                                  # defining a list

    eleza sigint_handler(self, signum, frame):
        ikiwa self.allow_kbdint:
            ashiria KeyboardInterrupt
        self.message("\nProgram interrupted. (Use 'cont' to resume).")
        self.set_step()
        self.set_trace(frame)

    eleza reset(self):
        bdb.Bdb.reset(self)
        self.forget()

    eleza forget(self):
        self.lineno = Tupu
        self.stack = []
        self.curindex = 0
        self.curframe = Tupu
        self.tb_lineno.clear()

    eleza setup(self, f, tb):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, tb)
        wakati tb:
            # when setting up post-mortem debugging with a traceback, save all
            # the original line numbers to be displayed along the current line
            # numbers (which can be different, e.g. due to finally clauses)
            lineno = lasti2lineno(tb.tb_frame.f_code, tb.tb_lasti)
            self.tb_lineno[tb.tb_frame] = lineno
            tb = tb.tb_next
        self.curframe = self.stack[self.curindex][0]
        # The f_locals dictionary ni updated kutoka the actual frame
        # locals whenever the .f_locals accessor ni called, so we
        # cache it here to ensure that modifications are sio overwritten.
        self.curframe_locals = self.curframe.f_locals
        rudisha self.execRcLines()

    # Can be executed earlier than 'setup' ikiwa desired
    eleza execRcLines(self):
        ikiwa sio self.rcLines:
            rudisha
        # local copy because of recursion
        rcLines = self.rcLines
        rcLines.reverse()
        # execute every line only once
        self.rcLines = []
        wakati rcLines:
            line = rcLines.pop().strip()
            ikiwa line na line[0] != '#':
                ikiwa self.onecmd(line):
                    # ikiwa onecmd rudishas Kweli, the command wants to exit
                    # kutoka the interaction, save leftover rc lines
                    # to execute before next interaction
                    self.rcLines += reversed(rcLines)
                    rudisha Kweli

    # Override Bdb methods

    eleza user_call(self, frame, argument_list):
        """This method ni called when there ni the remote possibility
        that we ever need to stop kwenye this function."""
        ikiwa self._wait_for_mainpyfile:
            rudisha
        ikiwa self.stop_here(frame):
            self.message('--Call--')
            self.interaction(frame, Tupu)

    eleza user_line(self, frame):
        """This function ni called when we stop ama koma at this line."""
        ikiwa self._wait_for_mainpyfile:
            ikiwa (self.mainpyfile != self.canonic(frame.f_code.co_filename)
                ama frame.f_lineno <= 0):
                rudisha
            self._wait_for_mainpyfile = Uongo
        ikiwa self.bp_commands(frame):
            self.interaction(frame, Tupu)

    eleza bp_commands(self, frame):
        """Call every command that was set kila the current active komapoint
        (ikiwa there ni one).

        Returns Kweli ikiwa the normal interaction function must be called,
        Uongo otherwise."""
        # self.currentbp ni set kwenye bdb kwenye Bdb.koma_here ikiwa a komapoint was hit
        ikiwa getattr(self, "currentbp", Uongo) na \
               self.currentbp kwenye self.commands:
            currentbp = self.currentbp
            self.currentbp = 0
            lastcmd_back = self.lastcmd
            self.setup(frame, Tupu)
            kila line kwenye self.commands[currentbp]:
                self.onecmd(line)
            self.lastcmd = lastcmd_back
            ikiwa sio self.commands_silent[currentbp]:
                self.print_stack_entry(self.stack[self.curindex])
            ikiwa self.commands_doprompt[currentbp]:
                self._cmdloop()
            self.forget()
            rudisha
        rudisha 1

    eleza user_rudisha(self, frame, rudisha_value):
        """This function ni called when a rudisha trap ni set here."""
        ikiwa self._wait_for_mainpyfile:
            rudisha
        frame.f_locals['__rudisha__'] = rudisha_value
        self.message('--Return--')
        self.interaction(frame, Tupu)

    eleza user_exception(self, frame, exc_info):
        """This function ni called ikiwa an exception occurs,
        but only ikiwa we are to stop at ama just below this level."""
        ikiwa self._wait_for_mainpyfile:
            rudisha
        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value

        # An 'Internal StopIteration' exception ni an exception debug event
        # issued by the interpreter when handling a subgenerator run with
        # 'tuma kutoka' ama a generator controlled by a kila loop. No exception has
        # actually occurred kwenye this case. The debugger uses this debug event to
        # stop when the debuggee ni rudishaing kutoka such generators.
        prefix = 'Internal ' ikiwa (not exc_traceback
                                    na exc_type ni StopIteration) else ''
        self.message('%s%s' % (prefix,
            traceback.format_exception_only(exc_type, exc_value)[-1].strip()))
        self.interaction(frame, exc_traceback)

    # General interaction function
    eleza _cmdloop(self):
        wakati Kweli:
            jaribu:
                # keyboard interrupts allow kila an easy way to cancel
                # the current command, so allow them during interactive input
                self.allow_kbdint = Kweli
                self.cmdloop()
                self.allow_kbdint = Uongo
                koma
            tatizo KeyboardInterrupt:
                self.message('--KeyboardInterrupt--')

    # Called before loop, handles display expressions
    eleza preloop(self):
        displaying = self.displaying.get(self.curframe)
        ikiwa displaying:
            kila expr, oldvalue kwenye displaying.items():
                newvalue = self._getval_except(expr)
                # check kila identity first; this prevents custom __eq__ to
                # be called at every loop, na also prevents instances whose
                # fields are changed to be displayed
                ikiwa newvalue ni sio oldvalue na newvalue != oldvalue:
                    displaying[expr] = newvalue
                    self.message('display %s: %r  [old: %r]' %
                                 (expr, newvalue, oldvalue))

    eleza interaction(self, frame, traceback):
        # Restore the previous signal handler at the Pdb prompt.
        ikiwa Pdb._previous_sigint_handler:
            jaribu:
                signal.signal(signal.SIGINT, Pdb._previous_sigint_handler)
            tatizo ValueError:  # ValueError: signal only works kwenye main thread
                pita
            isipokua:
                Pdb._previous_sigint_handler = Tupu
        ikiwa self.setup(frame, traceback):
            # no interaction desired at this time (happens ikiwa .pdbrc contains
            # a command like "endelea")
            self.forget()
            rudisha
        self.print_stack_entry(self.stack[self.curindex])
        self._cmdloop()
        self.forget()

    eleza displayhook(self, obj):
        """Custom displayhook kila the exec kwenye default(), which prevents
        assignment of the _ variable kwenye the builtins.
        """
        # reproduce the behavior of the standard displayhook, sio printing Tupu
        ikiwa obj ni sio Tupu:
            self.message(repr(obj))

    eleza default(self, line):
        ikiwa line[:1] == '!': line = line[1:]
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        jaribu:
            code = compile(line + '\n', '<stdin>', 'single')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            jaribu:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                exec(code, globals, locals)
            mwishowe:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())

    eleza precmd(self, line):
        """Handle alias expansion na ';;' separator."""
        ikiwa sio line.strip():
            rudisha line
        args = line.split()
        wakati args[0] kwenye self.aliases:
            line = self.aliases[args[0]]
            ii = 1
            kila tmpArg kwenye args[1:]:
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
        """Interpret the argument kama though it had been typed kwenye response
        to the prompt.

        Checks whether this line ni typed at the normal prompt ama in
        a komapoint command list definition.
        """
        ikiwa sio self.commands_defining:
            rudisha cmd.Cmd.onecmd(self, line)
        isipokua:
            rudisha self.handle_command_def(line)

    eleza handle_command_def(self, line):
        """Handles one command line during command list definition."""
        cmd, arg, line = self.parseline(line)
        ikiwa sio cmd:
            rudisha
        ikiwa cmd == 'silent':
            self.commands_silent[self.commands_bnum] = Kweli
            rudisha # endelea to handle other cmd eleza kwenye the cmd list
        elikiwa cmd == 'end':
            self.cmdqueue = []
            rudisha 1 # end of cmd list
        cmdlist = self.commands[self.commands_bnum]
        ikiwa arg:
            cmdlist.append(cmd+' '+arg)
        isipokua:
            cmdlist.append(cmd)
        # Determine ikiwa we must stop
        jaribu:
            func = getattr(self, 'do_' + cmd)
        tatizo AttributeError:
            func = self.default
        # one of the resuming commands
        ikiwa func.__name__ kwenye self.commands_resuming:
            self.commands_doprompt[self.commands_bnum] = Uongo
            self.cmdqueue = []
            rudisha 1
        rudisha

    # interface abstraction functions

    eleza message(self, msg):
        andika(msg, file=self.stdout)

    eleza error(self, msg):
        andika('***', msg, file=self.stdout)

    # Generic completion functions.  Individual complete_foo methods can be
    # assigned below to one of these functions.

    eleza _complete_location(self, text, line, begidx, endidx):
        # Complete a file/module/function location kila koma/tkoma/clear.
        ikiwa line.strip().endswith((':', ',')):
            # Here comes a line number ama a condition which we can't complete.
            rudisha []
        # First, try to find matching functions (i.e. expressions).
        jaribu:
            ret = self._complete_expression(text, line, begidx, endidx)
        tatizo Exception:
            ret = []
        # Then, try to complete file names kama well.
        globs = glob.glob(text + '*')
        kila fn kwenye globs:
            ikiwa os.path.isdir(fn):
                ret.append(fn + '/')
            elikiwa os.path.isfile(fn) na fn.lower().endswith(('.py', '.pyw')):
                ret.append(fn + ':')
        rudisha ret

    eleza _complete_bpnumber(self, text, line, begidx, endidx):
        # Complete a komapoint number.  (This would be more helpful ikiwa we could
        # display additional info along with the completions, such kama file/line
        # of the komapoint.)
        rudisha [str(i) kila i, bp kwenye enumerate(bdb.Breakpoint.bpbynumber)
                ikiwa bp ni sio Tupu na str(i).startswith(text)]

    eleza _complete_expression(self, text, line, begidx, endidx):
        # Complete an arbitrary expression.
        ikiwa sio self.curframe:
            rudisha []
        # Collect globals na locals.  It ni usually sio really sensible to also
        # complete builtins, na they clutter the namespace quite heavily, so we
        # leave them out.
        ns = {**self.curframe.f_globals, **self.curframe_locals}
        ikiwa '.' kwenye text:
            # Walk an attribute chain up to the last part, similar to what
            # rlcompleter does.  This will bail ikiwa any of the parts are not
            # simple attribute access, which ni what we want.
            dotted = text.split('.')
            jaribu:
                obj = ns[dotted[0]]
                kila part kwenye dotted[1:-1]:
                    obj = getattr(obj, part)
            tatizo (KeyError, AttributeError):
                rudisha []
            prefix = '.'.join(dotted[:-1]) + '.'
            rudisha [prefix + n kila n kwenye dir(obj) ikiwa n.startswith(dotted[-1])]
        isipokua:
            # Complete a simple name.
            rudisha [n kila n kwenye ns.keys() ikiwa n.startswith(text)]

    # Command definitions, called by cmdloop()
    # The argument ni the remaining string on the command line
    # Return true to exit kutoka the command loop

    eleza do_commands(self, arg):
        """commands [bpnumber]
        (com) ...
        (com) end
        (Pdb)

        Specify a list of commands kila komapoint number bpnumber.
        The commands themselves are entered on the following lines.
        Type a line containing just 'end' to terminate the commands.
        The commands are executed when the komapoint ni hit.

        To remove all commands kutoka a komapoint, type commands and
        follow it immediately with end; that is, give no commands.

        With no bpnumber argument, commands refers to the last
        komapoint set.

        You can use komapoint commands to start your program up
        again.  Simply use the endelea command, ama step, ama any other
        command that resumes execution.

        Specifying any command resuming execution (currently endelea,
        step, next, rudisha, jump, quit na their abbreviations)
        terminates the command list (as ikiwa that command was
        immediately followed by end).  This ni because any time you
        resume execution (even with a simple next ama step), you may
        encounter another komapoint -- which could have its own
        command list, leading to ambiguities about which list to
        execute.

        If you use the 'silent' command kwenye the command list, the usual
        message about stopping at a komapoint ni sio printed.  This
        may be desirable kila komapoints that are to print a specific
        message na then endelea.  If none of the other commands
        print anything, you will see no sign that the komapoint was
        reached.
        """
        ikiwa sio arg:
            bnum = len(bdb.Breakpoint.bpbynumber) - 1
        isipokua:
            jaribu:
                bnum = int(arg)
            except:
                self.error("Usage: commands [bnum]\n        ...\n        end")
                rudisha
        self.commands_bnum = bnum
        # Save old definitions kila the case of a keyboard interrupt.
        ikiwa bnum kwenye self.commands:
            old_command_defs = (self.commands[bnum],
                                self.commands_doprompt[bnum],
                                self.commands_silent[bnum])
        isipokua:
            old_command_defs = Tupu
        self.commands[bnum] = []
        self.commands_doprompt[bnum] = Kweli
        self.commands_silent[bnum] = Uongo

        prompt_back = self.prompt
        self.prompt = '(com) '
        self.commands_defining = Kweli
        jaribu:
            self.cmdloop()
        tatizo KeyboardInterrupt:
            # Restore old definitions.
            ikiwa old_command_defs:
                self.commands[bnum] = old_command_defs[0]
                self.commands_doprompt[bnum] = old_command_defs[1]
                self.commands_silent[bnum] = old_command_defs[2]
            isipokua:
                toa self.commands[bnum]
                toa self.commands_doprompt[bnum]
                toa self.commands_silent[bnum]
            self.error('command definition aborted, old commands restored')
        mwishowe:
            self.commands_defining = Uongo
            self.prompt = prompt_back

    complete_commands = _complete_bpnumber

    eleza do_koma(self, arg, temporary = 0):
        """b(reak) [ ([filename:]lineno | function) [, condition] ]
        Without argument, list all komas.

        With a line number argument, set a koma at this line kwenye the
        current file.  With a function name, set a koma at the first
        executable line of that function.  If a second argument is
        present, it ni a string specifying an expression which must
        evaluate to true before the komapoint ni honored.

        The line number may be prefixed with a filename na a colon,
        to specify a komapoint kwenye another file (probably one that
        hasn't been loaded yet).  The file ni searched kila on
        sys.path; the .py suffix may be omitted.
        """
        ikiwa sio arg:
            ikiwa self.komas:  # There's at least one
                self.message("Num Type         Disp Enb   Where")
                kila bp kwenye bdb.Breakpoint.bpbynumber:
                    ikiwa bp:
                        self.message(bp.bpformat())
            rudisha
        # parse arguments; comma has lowest precedence
        # na cannot occur kwenye filename
        filename = Tupu
        lineno = Tupu
        cond = Tupu
        comma = arg.find(',')
        ikiwa comma > 0:
            # parse stuff after comma: "condition"
            cond = arg[comma+1:].lstrip()
            arg = arg[:comma].rstrip()
        # parse stuff before comma: [filename:]lineno | function
        colon = arg.rfind(':')
        funcname = Tupu
        ikiwa colon >= 0:
            filename = arg[:colon].rstrip()
            f = self.lookupmodule(filename)
            ikiwa sio f:
                self.error('%r sio found kutoka sys.path' % filename)
                rudisha
            isipokua:
                filename = f
            arg = arg[colon+1:].lstrip()
            jaribu:
                lineno = int(arg)
            tatizo ValueError:
                self.error('Bad lineno: %s' % arg)
                rudisha
        isipokua:
            # no colon; can be lineno ama function
            jaribu:
                lineno = int(arg)
            tatizo ValueError:
                jaribu:
                    func = eval(arg,
                                self.curframe.f_globals,
                                self.curframe_locals)
                except:
                    func = arg
                jaribu:
                    ikiwa hasattr(func, '__func__'):
                        func = func.__func__
                    code = func.__code__
                    #use co_name to identify the bkpt (function names
                    #could be aliased, but co_name ni invariant)
                    funcname = code.co_name
                    lineno = code.co_firstlineno
                    filename = code.co_filename
                except:
                    # last thing to try
                    (ok, filename, ln) = self.lineinfo(arg)
                    ikiwa sio ok:
                        self.error('The specified object %r ni sio a function '
                                   'or was sio found along sys.path.' % arg)
                        rudisha
                    funcname = ok # ok contains a function name
                    lineno = int(ln)
        ikiwa sio filename:
            filename = self.defaultFile()
        # Check kila reasonable komapoint
        line = self.checkline(filename, lineno)
        ikiwa line:
            # now set the koma point
            err = self.set_koma(filename, line, temporary, cond, funcname)
            ikiwa err:
                self.error(err)
            isipokua:
                bp = self.get_komas(filename, line)[-1]
                self.message("Breakpoint %d at %s:%d" %
                             (bp.number, bp.file, bp.line))

    # To be overridden kwenye derived debuggers
    eleza defaultFile(self):
        """Produce a reasonable default."""
        filename = self.curframe.f_code.co_filename
        ikiwa filename == '<string>' na self.mainpyfile:
            filename = self.mainpyfile
        rudisha filename

    do_b = do_koma

    complete_koma = _complete_location
    complete_b = _complete_location

    eleza do_tkoma(self, arg):
        """tkoma [ ([filename:]lineno | function) [, condition] ]
        Same arguments kama koma, but sets a temporary komapoint: it
        ni automatically deleted when first hit.
        """
        self.do_koma(arg, 1)

    complete_tkoma = _complete_location

    eleza lineinfo(self, identifier):
        failed = (Tupu, Tupu, Tupu)
        # Input ni identifier, may be kwenye single quotes
        idstring = identifier.split("'")
        ikiwa len(idstring) == 1:
            # haiko kwenye single quotes
            id = idstring[0].strip()
        elikiwa len(idstring) == 3:
            # quoted
            id = idstring[1].strip()
        isipokua:
            rudisha failed
        ikiwa id == '': rudisha failed
        parts = id.split('.')
        # Protection kila derived debuggers
        ikiwa parts[0] == 'self':
            toa parts[0]
            ikiwa len(parts) == 0:
                rudisha failed
        # Best first guess at file to look at
        fname = self.defaultFile()
        ikiwa len(parts) == 1:
            item = parts[0]
        isipokua:
            # More than one part.
            # First ni module, second ni method/class
            f = self.lookupmodule(parts[0])
            ikiwa f:
                fname = f
            item = parts[1]
        answer = find_function(item, fname)
        rudisha answer ama failed

    eleza checkline(self, filename, lineno):
        """Check whether specified line seems to be executable.

        Return `lineno` ikiwa it is, 0 ikiwa sio (e.g. a docstring, comment, blank
        line ama EOF). Warning: testing ni sio comprehensive.
        """
        # this method should be callable before starting debugging, so default
        # to "no globals" ikiwa there ni no current frame
        globs = self.curframe.f_globals ikiwa hasattr(self, 'curframe') else Tupu
        line = linecache.getline(filename, lineno, globs)
        ikiwa sio line:
            self.message('End of file')
            rudisha 0
        line = line.strip()
        # Don't allow setting komapoint at a blank line
        ikiwa (not line ama (line[0] == '#') or
             (line[:3] == '"""') ama line[:3] == "'''"):
            self.error('Blank ama comment')
            rudisha 0
        rudisha lineno

    eleza do_enable(self, arg):
        """enable bpnumber [bpnumber ...]
        Enables the komapoints given kama a space separated list of
        komapoint numbers.
        """
        args = arg.split()
        kila i kwenye args:
            jaribu:
                bp = self.get_bpbynumber(i)
            tatizo ValueError kama err:
                self.error(err)
            isipokua:
                bp.enable()
                self.message('Enabled %s' % bp)

    complete_enable = _complete_bpnumber

    eleza do_disable(self, arg):
        """disable bpnumber [bpnumber ...]
        Disables the komapoints given kama a space separated list of
        komapoint numbers.  Disabling a komapoint means it cannot
        cause the program to stop execution, but unlike clearing a
        komapoint, it remains kwenye the list of komapoints na can be
        (re-)enabled.
        """
        args = arg.split()
        kila i kwenye args:
            jaribu:
                bp = self.get_bpbynumber(i)
            tatizo ValueError kama err:
                self.error(err)
            isipokua:
                bp.disable()
                self.message('Disabled %s' % bp)

    complete_disable = _complete_bpnumber

    eleza do_condition(self, arg):
        """condition bpnumber [condition]
        Set a new condition kila the komapoint, an expression which
        must evaluate to true before the komapoint ni honored.  If
        condition ni absent, any existing condition ni removed; i.e.,
        the komapoint ni made unconditional.
        """
        args = arg.split(' ', 1)
        jaribu:
            cond = args[1]
        tatizo IndexError:
            cond = Tupu
        jaribu:
            bp = self.get_bpbynumber(args[0].strip())
        tatizo IndexError:
            self.error('Breakpoint number expected')
        tatizo ValueError kama err:
            self.error(err)
        isipokua:
            bp.cond = cond
            ikiwa sio cond:
                self.message('Breakpoint %d ni now unconditional.' % bp.number)
            isipokua:
                self.message('New condition set kila komapoint %d.' % bp.number)

    complete_condition = _complete_bpnumber

    eleza do_ignore(self, arg):
        """ignore bpnumber [count]
        Set the ignore count kila the given komapoint number.  If
        count ni omitted, the ignore count ni set to 0.  A komapoint
        becomes active when the ignore count ni zero.  When non-zero,
        the count ni decremented each time the komapoint ni reached
        na the komapoint ni sio disabled na any associated
        condition evaluates to true.
        """
        args = arg.split()
        jaribu:
            count = int(args[1].strip())
        except:
            count = 0
        jaribu:
            bp = self.get_bpbynumber(args[0].strip())
        tatizo IndexError:
            self.error('Breakpoint number expected')
        tatizo ValueError kama err:
            self.error(err)
        isipokua:
            bp.ignore = count
            ikiwa count > 0:
                ikiwa count > 1:
                    countstr = '%d crossings' % count
                isipokua:
                    countstr = '1 crossing'
                self.message('Will ignore next %s of komapoint %d.' %
                             (countstr, bp.number))
            isipokua:
                self.message('Will stop next time komapoint %d ni reached.'
                             % bp.number)

    complete_ignore = _complete_bpnumber

    eleza do_clear(self, arg):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of komapoint numbers, clear
        those komapoints.  Without argument, clear all komas (but
        first ask confirmation).  With a filename:lineno argument,
        clear all komas at that line kwenye that file.
        """
        ikiwa sio arg:
            jaribu:
                reply = input('Clear all komas? ')
            tatizo EOFError:
                reply = 'no'
            reply = reply.strip().lower()
            ikiwa reply kwenye ('y', 'yes'):
                bplist = [bp kila bp kwenye bdb.Breakpoint.bpbynumber ikiwa bp]
                self.clear_all_komas()
                kila bp kwenye bplist:
                    self.message('Deleted %s' % bp)
            rudisha
        ikiwa ':' kwenye arg:
            # Make sure it works kila "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            jaribu:
                lineno = int(arg)
            tatizo ValueError:
                err = "Invalid line number (%s)" % arg
            isipokua:
                bplist = self.get_komas(filename, lineno)
                err = self.clear_koma(filename, lineno)
            ikiwa err:
                self.error(err)
            isipokua:
                kila bp kwenye bplist:
                    self.message('Deleted %s' % bp)
            rudisha
        numberlist = arg.split()
        kila i kwenye numberlist:
            jaribu:
                bp = self.get_bpbynumber(i)
            tatizo ValueError kama err:
                self.error(err)
            isipokua:
                self.clear_bpbynumber(i)
                self.message('Deleted %s' % bp)
    do_cl = do_clear # 'c' ni already an abbreviation kila 'endelea'

    complete_clear = _complete_location
    complete_cl = _complete_location

    eleza do_where(self, arg):
        """w(here)
        Print a stack trace, with the most recent frame at the bottom.
        An arrow indicates the "current frame", which determines the
        context of most commands.  'bt' ni an alias kila this command.
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
        self.lineno = Tupu

    eleza do_up(self, arg):
        """u(p) [count]
        Move the current frame count (default one) levels up kwenye the
        stack trace (to an older frame).
        """
        ikiwa self.curindex == 0:
            self.error('Oldest frame')
            rudisha
        jaribu:
            count = int(arg ama 1)
        tatizo ValueError:
            self.error('Invalid frame count (%s)' % arg)
            rudisha
        ikiwa count < 0:
            newframe = 0
        isipokua:
            newframe = max(0, self.curindex - count)
        self._select_frame(newframe)
    do_u = do_up

    eleza do_down(self, arg):
        """d(own) [count]
        Move the current frame count (default one) levels down kwenye the
        stack trace (to a newer frame).
        """
        ikiwa self.curindex + 1 == len(self.stack):
            self.error('Newest frame')
            rudisha
        jaribu:
            count = int(arg ama 1)
        tatizo ValueError:
            self.error('Invalid frame count (%s)' % arg)
            rudisha
        ikiwa count < 0:
            newframe = len(self.stack) - 1
        isipokua:
            newframe = min(len(self.stack) - 1, self.curindex + count)
        self._select_frame(newframe)
    do_d = do_down

    eleza do_until(self, arg):
        """unt(il) [lineno]
        Without argument, endelea execution until the line with a
        number greater than the current one ni reached.  With a line
        number, endelea execution until a line with a number greater
        ama equal to that ni reached.  In both cases, also stop when
        the current frame rudishas.
        """
        ikiwa arg:
            jaribu:
                lineno = int(arg)
            tatizo ValueError:
                self.error('Error kwenye argument: %r' % arg)
                rudisha
            ikiwa lineno <= self.curframe.f_lineno:
                self.error('"until" line number ni smaller than current '
                           'line number')
                rudisha
        isipokua:
            lineno = Tupu
        self.set_until(self.curframe, lineno)
        rudisha 1
    do_unt = do_until

    eleza do_step(self, arg):
        """s(tep)
        Execute the current line, stop at the first possible occasion
        (either kwenye a function that ni called ama kwenye the current
        function).
        """
        self.set_step()
        rudisha 1
    do_s = do_step

    eleza do_next(self, arg):
        """n(ext)
        Continue execution until the next line kwenye the current function
        ni reached ama it rudishas.
        """
        self.set_next(self.curframe)
        rudisha 1
    do_n = do_next

    eleza do_run(self, arg):
        """run [args...]
        Restart the debugged python program. If a string ni supplied
        it ni split with "shlex", na the result ni used kama the new
        sys.argv.  History, komapoints, actions na debugger options
        are preserved.  "restart" ni an alias kila "run".
        """
        ikiwa arg:
            agiza shlex
            argv0 = sys.argv[0:1]
            sys.argv = shlex.split(arg)
            sys.argv[:0] = argv0
        # this ni caught kwenye the main debugger loop
        ashiria Restart

    do_restart = do_run

    eleza do_rudisha(self, arg):
        """r(eturn)
        Continue execution until the current function rudishas.
        """
        self.set_rudisha(self.curframe)
        rudisha 1
    do_r = do_rudisha

    eleza do_endelea(self, arg):
        """c(ont(inue))
        Continue execution, only stop when a komapoint ni encountered.
        """
        ikiwa sio self.nosigint:
            jaribu:
                Pdb._previous_sigint_handler = \
                    signal.signal(signal.SIGINT, self.sigint_handler)
            tatizo ValueError:
                # ValueError happens when do_endelea() ni invoked kutoka
                # a non-main thread kwenye which case we just endelea without
                # SIGINT set. Would printing a message here (once) make
                # sense?
                pita
        self.set_endelea()
        rudisha 1
    do_c = do_cont = do_endelea

    eleza do_jump(self, arg):
        """j(ump) lineno
        Set the next line that will be executed.  Only available in
        the bottom-most frame.  This lets you jump back na execute
        code again, ama jump forward to skip code that you don't want
        to run.

        It should be noted that sio all jumps are allowed -- for
        instance it ni sio possible to jump into the middle of a
        kila loop ama out of a finally clause.
        """
        ikiwa self.curindex + 1 != len(self.stack):
            self.error('You can only jump within the bottom frame')
            rudisha
        jaribu:
            arg = int(arg)
        tatizo ValueError:
            self.error("The 'jump' command requires a line number")
        isipokua:
            jaribu:
                # Do the jump, fix up our copy of the stack, na display the
                # new position
                self.curframe.f_lineno = arg
                self.stack[self.curindex] = self.stack[self.curindex][0], arg
                self.print_stack_entry(self.stack[self.curindex])
            tatizo ValueError kama e:
                self.error('Jump failed: %s' % e)
    do_j = do_jump

    eleza do_debug(self, arg):
        """debug code
        Enter a recursive debugger that steps through the code
        argument (which ni an arbitrary expression ama statement to be
        executed kwenye the current environment).
        """
        sys.settrace(Tupu)
        globals = self.curframe.f_globals
        locals = self.curframe_locals
        p = Pdb(self.completekey, self.stdin, self.stdout)
        p.prompt = "(%s) " % self.prompt.strip()
        self.message("ENTERING RECURSIVE DEBUGGER")
        jaribu:
            sys.call_tracing(p.run, (arg, globals, locals))
        tatizo Exception:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())
        self.message("LEAVING RECURSIVE DEBUGGER")
        sys.settrace(self.trace_dispatch)
        self.lastcmd = p.lastcmd

    complete_debug = _complete_expression

    eleza do_quit(self, arg):
        """q(uit)\nexit
        Quit kutoka the debugger. The program being executed ni aborted.
        """
        self._user_requested_quit = Kweli
        self.set_quit()
        rudisha 1

    do_q = do_quit
    do_exit = do_quit

    eleza do_EOF(self, arg):
        """EOF
        Handles the receipt of EOF kama a command.
        """
        self.message('')
        self._user_requested_quit = Kweli
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
        kila i kwenye range(n):
            name = co.co_varnames[i]
            ikiwa name kwenye dict:
                self.message('%s = %r' % (name, dict[name]))
            isipokua:
                self.message('%s = *** undefined ***' % (name,))
    do_a = do_args

    eleza do_retval(self, arg):
        """retval
        Print the rudisha value kila the last rudisha of a function.
        """
        ikiwa '__rudisha__' kwenye self.curframe_locals:
            self.message(repr(self.curframe_locals['__rudisha__']))
        isipokua:
            self.error('Not yet rudishaed!')
    do_rv = do_retval

    eleza _getval(self, arg):
        jaribu:
            rudisha eval(arg, self.curframe.f_globals, self.curframe_locals)
        except:
            exc_info = sys.exc_info()[:2]
            self.error(traceback.format_exception_only(*exc_info)[-1].strip())
            ashiria

    eleza _getval_except(self, arg, frame=Tupu):
        jaribu:
            ikiwa frame ni Tupu:
                rudisha eval(arg, self.curframe.f_globals, self.curframe_locals)
            isipokua:
                rudisha eval(arg, frame.f_globals, frame.f_locals)
        except:
            exc_info = sys.exc_info()[:2]
            err = traceback.format_exception_only(*exc_info)[-1].strip()
            rudisha _rstr('** ashiriad %s **' % err)

    eleza do_p(self, arg):
        """p expression
        Print the value of the expression.
        """
        jaribu:
            self.message(repr(self._getval(arg)))
        except:
            pita

    eleza do_pp(self, arg):
        """pp expression
        Pretty-print the value of the expression.
        """
        jaribu:
            self.message(pprint.pformat(self._getval(arg)))
        except:
            pita

    complete_print = _complete_expression
    complete_p = _complete_expression
    complete_pp = _complete_expression

    eleza do_list(self, arg):
        """l(ist) [first [,last] | .]

        List source code kila the current file.  Without arguments,
        list 11 lines around the current line ama endelea the previous
        listing.  With . kama argument, list 11 lines around the current
        line.  With one argument, list 11 lines starting at that line.
        With two arguments, list the given range; ikiwa the second
        argument ni less than the first, it ni a count.

        The current line kwenye the current frame ni indicated by "->".
        If an exception ni being debugged, the line where the
        exception was originally ashiriad ama propagated ni indicated by
        ">>", ikiwa it differs kutoka the current line.
        """
        self.lastcmd = 'list'
        last = Tupu
        ikiwa arg na arg != '.':
            jaribu:
                ikiwa ',' kwenye arg:
                    first, last = arg.split(',')
                    first = int(first.strip())
                    last = int(last.strip())
                    ikiwa last < first:
                        # assume it's a count
                        last = first + last
                isipokua:
                    first = int(arg.strip())
                    first = max(1, first - 5)
            tatizo ValueError:
                self.error('Error kwenye argument: %r' % arg)
                rudisha
        elikiwa self.lineno ni Tupu ama arg == '.':
            first = max(1, self.curframe.f_lineno - 5)
        isipokua:
            first = self.lineno + 1
        ikiwa last ni Tupu:
            last = first + 10
        filename = self.curframe.f_code.co_filename
        komalist = self.get_file_komas(filename)
        jaribu:
            lines = linecache.getlines(filename, self.curframe.f_globals)
            self._print_lines(lines[first-1:last], first, komalist,
                              self.curframe)
            self.lineno = min(last, len(lines))
            ikiwa len(lines) < last:
                self.message('[EOF]')
        tatizo KeyboardInterrupt:
            pita
    do_l = do_list

    eleza do_longlist(self, arg):
        """longlist | ll
        List the whole source code kila the current function ama frame.
        """
        filename = self.curframe.f_code.co_filename
        komalist = self.get_file_komas(filename)
        jaribu:
            lines, lineno = getsourcelines(self.curframe)
        tatizo OSError kama err:
            self.error(err)
            rudisha
        self._print_lines(lines, lineno, komalist, self.curframe)
    do_ll = do_longlist

    eleza do_source(self, arg):
        """source expression
        Try to get source code kila the given object na display it.
        """
        jaribu:
            obj = self._getval(arg)
        except:
            rudisha
        jaribu:
            lines, lineno = getsourcelines(obj)
        tatizo (OSError, TypeError) kama err:
            self.error(err)
            rudisha
        self._print_lines(lines, lineno)

    complete_source = _complete_expression

    eleza _print_lines(self, lines, start, komas=(), frame=Tupu):
        """Print a range of lines."""
        ikiwa frame:
            current_lineno = frame.f_lineno
            exc_lineno = self.tb_lineno.get(frame, -1)
        isipokua:
            current_lineno = exc_lineno = -1
        kila lineno, line kwenye enumerate(lines, start):
            s = str(lineno).rjust(3)
            ikiwa len(s) < 4:
                s += ' '
            ikiwa lineno kwenye komas:
                s += 'B'
            isipokua:
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
        jaribu:
            value = self._getval(arg)
        except:
            # _getval() already printed the error
            rudisha
        code = Tupu
        # Is it a function?
        jaribu:
            code = value.__code__
        tatizo Exception:
            pita
        ikiwa code:
            self.message('Function %s' % code.co_name)
            rudisha
        # Is it an instance method?
        jaribu:
            code = value.__func__.__code__
        tatizo Exception:
            pita
        ikiwa code:
            self.message('Method %s' % code.co_name)
            rudisha
        # Is it a class?
        ikiwa value.__class__ ni type:
            self.message('Class %s.%s' % (value.__module__, value.__qualname__))
            rudisha
        # Tupu of the above...
        self.message(type(value))

    complete_whatis = _complete_expression

    eleza do_display(self, arg):
        """display [expression]

        Display the value of the expression ikiwa it changed, each time execution
        stops kwenye the current frame.

        Without expression, list all display expressions kila the current frame.
        """
        ikiwa sio arg:
            self.message('Currently displaying:')
            kila item kwenye self.displaying.get(self.curframe, {}).items():
                self.message('%s: %r' % item)
        isipokua:
            val = self._getval_except(arg)
            self.displaying.setdefault(self.curframe, {})[arg] = val
            self.message('display %s: %r' % (arg, val))

    complete_display = _complete_expression

    eleza do_undisplay(self, arg):
        """undisplay [expression]

        Do sio display the expression any more kwenye the current frame.

        Without expression, clear all display expressions kila the current frame.
        """
        ikiwa arg:
            jaribu:
                toa self.displaying.get(self.curframe, {})[arg]
            tatizo KeyError:
                self.error('not displaying %s' % arg)
        isipokua:
            self.displaying.pop(self.curframe, Tupu)

    eleza complete_undisplay(self, text, line, begidx, endidx):
        rudisha [e kila e kwenye self.displaying.get(self.curframe, {})
                ikiwa e.startswith(text)]

    eleza do_interact(self, arg):
        """interact

        Start an interactive interpreter whose global namespace
        contains all the (global na local) names found kwenye the current scope.
        """
        ns = {**self.curframe.f_globals, **self.curframe_locals}
        code.interact("*interactive*", local=ns)

    eleza do_alias(self, arg):
        """alias [name [command [parameter parameter ...] ]]
        Create an alias called 'name' that executes 'command'.  The
        command must *not* be enclosed kwenye quotes.  Replaceable
        parameters can be indicated by %1, %2, na so on, wakati %* is
        replaced by all the parameters.  If no command ni given, the
        current alias kila name ni shown. If no name ni given, all
        aliases are listed.

        Aliases may be nested na can contain anything that can be
        legally typed at the pdb prompt.  Note!  You *can* override
        internal pdb commands with aliases!  Those internal commands
        are then hidden until the alias ni removed.  Aliasing is
        recursively applied to the first word of the command line; all
        other words kwenye the line are left alone.

        As an example, here are two useful aliases (especially when
        placed kwenye the .pdbrc file):

        # Print instance variables (usage "pi classInst")
        alias pi kila k kwenye %1.__dict__.keys(): andika("%1.",k,"=",%1.__dict__[k])
        # Print instance variables kwenye self
        alias ps pi self
        """
        args = arg.split()
        ikiwa len(args) == 0:
            keys = sorted(self.aliases.keys())
            kila alias kwenye keys:
                self.message("%s = %s" % (alias, self.aliases[alias]))
            rudisha
        ikiwa args[0] kwenye self.aliases na len(args) == 1:
            self.message("%s = %s" % (args[0], self.aliases[args[0]]))
        isipokua:
            self.aliases[args[0]] = ' '.join(args[1:])

    eleza do_unalias(self, arg):
        """unalias name
        Delete the specified alias.
        """
        args = arg.split()
        ikiwa len(args) == 0: rudisha
        ikiwa args[0] kwenye self.aliases:
            toa self.aliases[args[0]]

    eleza complete_unalias(self, text, line, begidx, endidx):
        rudisha [a kila a kwenye self.aliases ikiwa a.startswith(text)]

    # List of all the commands making the program resume execution.
    commands_resuming = ['do_endelea', 'do_step', 'do_next', 'do_rudisha',
                         'do_quit', 'do_jump']

    # Print a traceback starting at the top stack frame.
    # The most recently entered frame ni printed last;
    # this ni different kutoka dbx na gdb, but consistent with
    # the Python interpreter's stack trace.
    # It ni also consistent with the up/down commands (which are
    # compatible with dbx na gdb: up moves towards 'main()'
    # na down moves towards the most recent stack frame).

    eleza print_stack_trace(self):
        jaribu:
            kila frame_lineno kwenye self.stack:
                self.print_stack_entry(frame_lineno)
        tatizo KeyboardInterrupt:
            pita

    eleza print_stack_entry(self, frame_lineno, prompt_prefix=line_prefix):
        frame, lineno = frame_lineno
        ikiwa frame ni self.curframe:
            prefix = '> '
        isipokua:
            prefix = '  '
        self.message(prefix +
                     self.format_stack_entry(frame_lineno, prompt_prefix))

    # Provide help

    eleza do_help(self, arg):
        """h(elp)
        Without argument, print the list of available commands.
        With a command name kama argument, print help about that command.
        "help pdb" shows the full pdb documentation.
        "help exec" gives help on the ! command.
        """
        ikiwa sio arg:
            rudisha cmd.Cmd.do_help(self, arg)
        jaribu:
            jaribu:
                topic = getattr(self, 'help_' + arg)
                rudisha topic()
            tatizo AttributeError:
                command = getattr(self, 'do_' + arg)
        tatizo AttributeError:
            self.error('No help kila %r' % arg)
        isipokua:
            ikiwa sys.flags.optimize >= 2:
                self.error('No help kila %r; please do sio run Python with -OO '
                           'ikiwa you need command help' % arg)
                rudisha
            self.message(command.__doc__.rstrip())

    do_h = do_help

    eleza help_exec(self):
        """(!) statement
        Execute the (one-line) statement kwenye the context of the current
        stack frame.  The exclamation point can be omitted unless the
        first word of the statement resembles a debugger command.  To
        assign to a global variable you must always prefix the command
        with a 'global' command, e.g.:
        (Pdb) global list_options; list_options = ['-l']
        (Pdb)
        """
        self.message((self.help_exec.__doc__ ama '').strip())

    eleza help_pdb(self):
        help()

    # other helper functions

    eleza lookupmodule(self, filename):
        """Helper function kila koma/clear parsing -- may be overridden.

        lookupmodule() translates (possibly incomplete) file ama module name
        into an absolute file name.
        """
        ikiwa os.path.isabs(filename) na  os.path.exists(filename):
            rudisha filename
        f = os.path.join(sys.path[0], filename)
        ikiwa  os.path.exists(f) na self.canonic(f) == self.mainpyfile:
            rudisha f
        root, ext = os.path.splitext(filename)
        ikiwa ext == '':
            filename = filename + '.py'
        ikiwa os.path.isabs(filename):
            rudisha filename
        kila dirname kwenye sys.path:
            wakati os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            ikiwa os.path.exists(fullname):
                rudisha fullname
        rudisha Tupu

    eleza _runmodule(self, module_name):
        self._wait_for_mainpyfile = Kweli
        self._user_requested_quit = Uongo
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
        # The script has to run kwenye __main__ namespace (or agizas kutoka
        # __main__ will koma).
        #
        # So we clear up the __main__ na set several special variables
        # (this gets rid of pdb's globals na cleans old variables on restarts).
        agiza __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__"    : "__main__",
                                  "__file__"    : filename,
                                  "__builtins__": __builtins__,
                                 })

        # When bdb sets tracing, a number of call na line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call kila details).
        self._wait_for_mainpyfile = Kweli
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = Uongo
        with open(filename, "rb") kama fp:
            statement = "exec(compile(%r, %r, 'exec'))" % \
                        (fp.read(), self.mainpyfile)
        self.run(statement)

# Collect all command help into docstring, ikiwa sio run with -OO

ikiwa __doc__ ni sio Tupu:
    # unfortunately we can't guess this order kutoka the kundi definition
    _help_order = [
        'help', 'where', 'down', 'up', 'koma', 'tkoma', 'clear', 'disable',
        'enable', 'ignore', 'condition', 'commands', 'step', 'next', 'until',
        'jump', 'rudisha', 'retval', 'run', 'endelea', 'list', 'longlist',
        'args', 'p', 'pp', 'whatis', 'source', 'display', 'undisplay',
        'interact', 'alias', 'unalias', 'debug', 'quit',
    ]

    kila _command kwenye _help_order:
        __doc__ += getattr(Pdb, 'do_' + _command).__doc__.strip() + '\n\n'
    __doc__ += Pdb.help_exec.__doc__

    toa _help_order, _command


# Simplified interface

eleza run(statement, globals=Tupu, locals=Tupu):
    Pdb().run(statement, globals, locals)

eleza runeval(expression, globals=Tupu, locals=Tupu):
    rudisha Pdb().runeval(expression, globals, locals)

eleza runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

eleza runcall(*args, **kwds):
    rudisha Pdb().runcall(*args, **kwds)

eleza set_trace(*, header=Tupu):
    pdb = Pdb()
    ikiwa header ni sio Tupu:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)

# Post-Mortem interface

eleza post_mortem(t=Tupu):
    # handling the default
    ikiwa t ni Tupu:
        # sys.exc_info() rudishas (type, value, traceback) ikiwa an exception is
        # being handled, otherwise it rudishas Tupu
        t = sys.exc_info()[2]
    ikiwa t ni Tupu:
        ashiria ValueError("A valid traceback must be pitaed ikiwa no "
                         "exception ni being handled")

    p = Pdb()
    p.reset()
    p.interaction(Tupu, t)

eleza pm():
    post_mortem(sys.last_traceback)


# Main program kila testing

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
an executable module ama package to debug can be specified using
the -m switch.

Initial commands are read kutoka .pdbrc files kwenye your home directory
and kwenye the current directory, ikiwa they exist.  Commands supplied with
-c are executed after commands kutoka .pdbrc files.

To let the script run until an exception occurs, use "-c endelea".
To let the script run up to a given line X kwenye the debugged file, use
"-c 'until X'"."""

eleza main():
    agiza getopt

    opts, args = getopt.getopt(sys.argv[1:], 'mhc:', ['help', 'command='])

    ikiwa sio args:
        andika(_usage)
        sys.exit(2)

    commands = []
    run_as_module = Uongo
    kila opt, optarg kwenye opts:
        ikiwa opt kwenye ['-h', '--help']:
            andika(_usage)
            sys.exit()
        elikiwa opt kwenye ['-c', '--command']:
            commands.append(optarg)
        elikiwa opt kwenye ['-m']:
            run_as_module = Kweli

    mainpyfile = args[0]     # Get script filename
    ikiwa sio run_as_module na sio os.path.exists(mainpyfile):
        andika('Error:', mainpyfile, 'does sio exist')
        sys.exit(1)

    sys.argv[:] = args      # Hide "pdb.py" na pdb options kutoka argument list

    # Replace pdb's dir with script's dir kwenye front of module search path.
    ikiwa sio run_as_module:
        sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user kutoka the command line. There ni a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = Pdb()
    pdb.rcLines.extend(commands)
    wakati Kweli:
        jaribu:
            ikiwa run_as_module:
                pdb._runmodule(mainpyfile)
            isipokua:
                pdb._runscript(mainpyfile)
            ikiwa pdb._user_requested_quit:
                koma
            andika("The program finished na will be restarted")
        tatizo Restart:
            andika("Restarting", mainpyfile, "with arguments:")
            andika("\t" + " ".join(args))
        tatizo SystemExit:
            # In most cases SystemExit does sio warrant a post-mortem session.
            andika("The program exited via sys.exit(). Exit status:", end=' ')
            andika(sys.exc_info()[1])
        tatizo SyntaxError:
            traceback.print_exc()
            sys.exit(1)
        except:
            traceback.print_exc()
            andika("Uncaught exception. Entering post mortem debugging")
            andika("Running 'cont' ama 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(Tupu, t)
            andika("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")


# When invoked kama main program, invoke the debugger on a script
ikiwa __name__ == '__main__':
    agiza pdb
    pdb.main()
