"""A generic kundi to build line-oriented command interpreters.

Interpreters constructed ukijumuisha this kundi obey the following conventions:

1. End of file on input ni processed kama the command 'EOF'.
2. A command ni parsed out of each line by collecting the prefix composed
   of characters kwenye the identchars member.
3. A command `foo' ni dispatched to a method 'do_foo()'; the do_ method
   ni pitaed a single argument consisting of the remainder of the line.
4. Typing an empty line repeats the last command.  (Actually, it calls the
   method `emptyline', which may be overridden kwenye a subclass.)
5. There ni a predefined `help' method.  Given an argument `topic', it
   calls the command `help_topic'.  With no arguments, it lists all topics
   ukijumuisha defined help_ functions, broken into up to three topics; documented
   commands, miscellaneous help topics, na undocumented commands.
6. The command '?' ni a synonym kila `help'.  The command '!' ni a synonym
   kila `shell', ikiwa a do_shell method exists.
7. If completion ni enabled, completing commands will be done automatically,
   na completing of commands args ni done by calling complete_foo() with
   arguments text, line, begidx, endidx.  text ni string we are matching
   against, all returned matches must begin ukijumuisha it.  line ni the current
   input line (lstripped), begidx na endidx are the beginning na end
   indexes of the text being matched, which could be used to provide
   different completion depending upon which position the argument ni in.

The `default' method may be overridden to intercept commands kila which there
is no do_ method.

The `completedefault' method may be overridden to intercept completions for
commands that have no complete_ method.

The data member `self.ruler' sets the character used to draw separator lines
in the help messages.  If empty, no ruler line ni drawn.  It defaults to "=".

If the value of `self.intro' ni nonempty when the cmdloop method ni called,
it ni printed out on interpreter startup.  This value may be overridden
via an optional argument to the cmdloop() method.

The data members `self.doc_header', `self.misc_header', na
`self.undoc_header' set the headers used kila the help function's
listings of documented functions, miscellaneous topics, na undocumented
functions respectively.
"""

agiza string, sys

__all__ = ["Cmd"]

PROMPT = '(Cmd) '
IDENTCHARS = string.ascii_letters + string.digits + '_'

kundi Cmd:
    """A simple framework kila writing line-oriented command interpreters.

    These are often useful kila test harnesses, administrative tools, na
    prototypes that will later be wrapped kwenye a more sophisticated interface.

    A Cmd instance ama subkundi instance ni a line-oriented interpreter
    framework.  There ni no good reason to instantiate Cmd itself; rather,
    it's useful kama a superkundi of an interpreter kundi you define yourself
    kwenye order to inherit Cmd's methods na encapsulate action methods.

    """
    prompt = PROMPT
    identchars = IDENTCHARS
    ruler = '='
    lastcmd = ''
    intro = Tupu
    doc_leader = ""
    doc_header = "Documented commands (type help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"
    use_rawinput = 1

    eleza __init__(self, completekey='tab', stdin=Tupu, stdout=Tupu):
        """Instantiate a line-oriented interpreter framework.

        The optional argument 'completekey' ni the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        sio Tupu na the readline module ni available, command completion
        ni done automatically. The optional arguments stdin na stdout
        specify alternate input na output file objects; ikiwa sio specified,
        sys.stdin na sys.stdout are used.

        """
        ikiwa stdin ni sio Tupu:
            self.stdin = stdin
        isipokua:
            self.stdin = sys.stdin
        ikiwa stdout ni sio Tupu:
            self.stdout = stdout
        isipokua:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey

    eleza cmdloop(self, intro=Tupu):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, na dispatch to action methods, pitaing them
        the remainder of the line kama argument.

        """

        self.preloop()
        ikiwa self.use_rawinput na self.completekey:
            jaribu:
                agiza readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            tatizo ImportError:
                pita
        jaribu:
            ikiwa intro ni sio Tupu:
                self.intro = intro
            ikiwa self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = Tupu
            wakati sio stop:
                ikiwa self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                isipokua:
                    ikiwa self.use_rawinput:
                        jaribu:
                            line = uliza(self.prompt)
                        tatizo EOFError:
                            line = 'EOF'
                    isipokua:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        ikiwa sio len(line):
                            line = 'EOF'
                        isipokua:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        mwishowe:
            ikiwa self.use_rawinput na self.completekey:
                jaribu:
                    agiza readline
                    readline.set_completer(self.old_completer)
                tatizo ImportError:
                    pita


    eleza precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt ni generated na issued.

        """
        rudisha line

    eleza postcmd(self, stop, line):
        """Hook method executed just after a command dispatch ni finished."""
        rudisha stop

    eleza preloop(self):
        """Hook method executed once when the cmdloop() method ni called."""
        pita

    eleza postloop(self):
        """Hook method executed once when the cmdloop() method ni about to
        return.

        """
        pita

    eleza parseline(self, line):
        """Parse the line into a command name na a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' na 'args' may be Tupu ikiwa the line couldn't be parsed.
        """
        line = line.strip()
        ikiwa sio line:
            rudisha Tupu, Tupu, line
        lasivyo line[0] == '?':
            line = 'help ' + line[1:]
        lasivyo line[0] == '!':
            ikiwa hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            isipokua:
                rudisha Tupu, Tupu, line
        i, n = 0, len(line)
        wakati i < n na line[i] kwenye self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        rudisha cmd, arg, line

    eleza onecmd(self, line):
        """Interpret the argument kama though it had been typed kwenye response
        to the prompt.

        This may be overridden, but should sio normally need to be;
        see the precmd() na postcmd() methods kila useful execution hooks.
        The rudisha value ni a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        ikiwa sio line:
            rudisha self.emptyline()
        ikiwa cmd ni Tupu:
            rudisha self.default(line)
        self.lastcmd = line
        ikiwa line == 'EOF' :
            self.lastcmd = ''
        ikiwa cmd == '':
            rudisha self.default(line)
        isipokua:
            jaribu:
                func = getattr(self, 'do_' + cmd)
            tatizo AttributeError:
                rudisha self.default(line)
            rudisha func(arg)

    eleza emptyline(self):
        """Called when an empty line ni entered kwenye response to the prompt.

        If this method ni sio overridden, it repeats the last nonempty
        command entered.

        """
        ikiwa self.lastcmd:
            rudisha self.onecmd(self.lastcmd)

    eleza default(self, line):
        """Called on an input line when the command prefix ni sio recognized.

        If this method ni sio overridden, it prints an error message na
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)

    eleza completedefault(self, *ignored):
        """Method called to complete an input line when no command-specific
        complete_*() method ni available.

        By default, it returns an empty list.

        """
        rudisha []

    eleza completenames(self, text, *ignored):
        dotext = 'do_'+text
        rudisha [a[3:] kila a kwenye self.get_names() ikiwa a.startswith(dotext)]

    eleza complete(self, text, state):
        """Return the next possible completion kila 'text'.

        If a command has sio been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        ikiwa state == 0:
            agiza readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            ikiwa begidx>0:
                cmd, args, foo = self.parseline(line)
                ikiwa cmd == '':
                    compfunc = self.completedefault
                isipokua:
                    jaribu:
                        compfunc = getattr(self, 'complete_' + cmd)
                    tatizo AttributeError:
                        compfunc = self.completedefault
            isipokua:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        jaribu:
            rudisha self.completion_matches[state]
        tatizo IndexError:
            rudisha Tupu

    eleza get_names(self):
        # This method used to pull kwenye base kundi attributes
        # at a time dir() didn't do it yet.
        rudisha dir(self.__class__)

    eleza complete_help(self, *args):
        commands = set(self.completenames(*args))
        topics = set(a[5:] kila a kwenye self.get_names()
                     ikiwa a.startswith('help_' + args[0]))
        rudisha list(commands | topics)

    eleza do_help(self, arg):
        'List available commands ukijumuisha "help" ama detailed help ukijumuisha "help cmd".'
        ikiwa arg:
            # XXX check arg syntax
            jaribu:
                func = getattr(self, 'help_' + arg)
            tatizo AttributeError:
                jaribu:
                    doc=getattr(self, 'do_' + arg).__doc__
                    ikiwa doc:
                        self.stdout.write("%s\n"%str(doc))
                        rudisha
                tatizo AttributeError:
                    pita
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                rudisha
            func()
        isipokua:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            kila name kwenye names:
                ikiwa name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates ikiwa routines overridden
            prevname = ''
            kila name kwenye names:
                ikiwa name[:3] == 'do_':
                    ikiwa name == prevname:
                        endelea
                    prevname = name
                    cmd=name[3:]
                    ikiwa cmd kwenye help:
                        cmds_doc.append(cmd)
                        toa help[cmd]
                    lasivyo getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    isipokua:
                        cmds_undoc.append(cmd)
            self.stdout.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  list(help.keys()),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

    eleza print_topics(self, header, cmds, cmdlen, maxcol):
        ikiwa cmds:
            self.stdout.write("%s\n"%str(header))
            ikiwa self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.stdout.write("\n")

    eleza columnize(self, list, displaywidth=80):
        """Display a list of strings kama a compact set of columns.

        Each column ni only kama wide kama necessary.
        Columns are separated by two spaces (one was sio legible enough).
        """
        ikiwa sio list:
            self.stdout.write("<empty>\n")
            rudisha

        nonstrings = [i kila i kwenye range(len(list))
                        ikiwa sio isinstance(list[i], str)]
        ikiwa nonstrings:
            ashiria TypeError("list[i] sio a string kila i kwenye %s"
                            % ", ".join(map(str, nonstrings)))
        size = len(list)
        ikiwa size == 1:
            self.stdout.write('%s\n'%str(list[0]))
            rudisha
        # Try every row count kutoka 1 upwards
        kila nrows kwenye range(1, len(list)):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -2
            kila col kwenye range(ncols):
                colwidth = 0
                kila row kwenye range(nrows):
                    i = row + nrows*col
                    ikiwa i >= size:
                        koma
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                ikiwa totwidth > displaywidth:
                    koma
            ikiwa totwidth <= displaywidth:
                koma
        isipokua:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        kila row kwenye range(nrows):
            texts = []
            kila col kwenye range(ncols):
                i = row + nrows*col
                ikiwa i >= size:
                    x = ""
                isipokua:
                    x = list[i]
                texts.append(x)
            wakati texts na sio texts[-1]:
                toa texts[-1]
            kila col kwenye range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.stdout.write("%s\n"%str("  ".join(texts)))
