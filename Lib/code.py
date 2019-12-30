"""Utilities needed to emulate Python's interactive interpreter.

"""

# Inspired by similar code by Jeff Epler na Fredrik Lundh.


agiza sys
agiza traceback
kutoka codeop agiza CommandCompiler, compile_command

__all__ = ["InteractiveInterpreter", "InteractiveConsole", "interact",
           "compile_command"]

kundi InteractiveInterpreter:
    """Base kundi kila InteractiveConsole.

    This kundi deals ukijumuisha parsing na interpreter state (the user's
    namespace); it doesn't deal ukijumuisha input buffering ama prompting ama
    input file naming (the filename ni always pitaed kwenye explicitly).

    """

    eleza __init__(self, locals=Tupu):
        """Constructor.

        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary ukijumuisha key "__name__" set to "__console__" na key
        "__doc__" set to Tupu.

        """
        ikiwa locals ni Tupu:
            locals = {"__name__": "__console__", "__doc__": Tupu}
        self.locals = locals
        self.compile = CommandCompiler()

    eleza runsource(self, source, filename="<input>", symbol="single"):
        """Compile na run some source kwenye the interpreter.

        Arguments are kama kila compile_command().

        One several things can happen:

        1) The input ni incorrect; compile_command() raised an
        exception (SyntaxError ama OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.

        2) The input ni incomplete, na more input ni required;
        compile_command() returned Tupu.  Nothing happens.

        3) The input ni complete; compile_command() returned a code
        object.  The code ni executed by calling self.runcode() (which
        also handles run-time exceptions, tatizo kila SystemExit).

        The rudisha value ni Kweli kwenye case 2, Uongo kwenye the other cases (unless
        an exception ni raised).  The rudisha value can be used to
        decide whether to use sys.ps1 ama sys.ps2 to prompt the next
        line.

        """
        jaribu:
            code = self.compile(source, filename, symbol)
        tatizo (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            rudisha Uongo

        ikiwa code ni Tupu:
            # Case 2
            rudisha Kweli

        # Case 3
        self.runcode(code)
        rudisha Uongo

    eleza runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() ni called to
        display a traceback.  All exceptions are caught except
        SystemExit, which ni reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere kwenye this code, na may sio always be caught.  The
        caller should be prepared to deal ukijumuisha it.

        """
        jaribu:
            exec(code, self.locals)
        tatizo SystemExit:
            raise
        tatizo:
            self.showtraceback()

    eleza showsyntaxerror(self, filename=Tupu):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename ni given, it ni stuffed kwenye the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading kutoka a string).

        The output ni written by self.write(), below.

        """
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        ikiwa filename na type ni SyntaxError:
            # Work hard to stuff the correct filename kwenye the exception
            jaribu:
                msg, (dummy_filename, lineno, offset, line) = value.args
            tatizo ValueError:
                # Not the format we expect; leave it alone
                pita
            isipokua:
                # Stuff kwenye the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        ikiwa sys.excepthook ni sys.__excepthook__:
            lines = traceback.format_exception_only(type, value)
            self.write(''.join(lines))
        isipokua:
            # If someone has set sys.excepthook, we let that take precedence
            # over self.write
            sys.excepthook(type, value, tb)

    eleza showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it ni our own code.

        The output ni written by self.write(), below.

        """
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        jaribu:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
            ikiwa sys.excepthook ni sys.__excepthook__:
                self.write(''.join(lines))
            isipokua:
                # If someone has set sys.excepthook, we let that take precedence
                # over self.write
                sys.excepthook(ei[0], ei[1], last_tb)
        mwishowe:
            last_tb = ei = Tupu

    eleza write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subkundi may
        replace this ukijumuisha a different implementation.

        """
        sys.stderr.write(data)


kundi InteractiveConsole(InteractiveInterpreter):
    """Closely emulate the behavior of the interactive Python interpreter.

    This kundi builds on InteractiveInterpreter na adds prompting
    using the familiar sys.ps1 na sys.ps2, na input buffering.

    """

    eleza __init__(self, locals=Tupu, filename="<console>"):
        """Constructor.

        The optional locals argument will be pitaed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up kwenye tracebacks.

        """
        InteractiveInterpreter.__init__(self, locals)
        self.filename = filename
        self.resetbuffer()

    eleza resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    eleza interact(self, banner=Tupu, exitmsg=Tupu):
        """Closely emulate the interactive Python console.

        The optional banner argument specifies the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current kundi name kwenye parentheses (so kama not
        to confuse this ukijumuisha the real interpreter -- since it's so
        close!).

        The optional exitmsg argument specifies the exit message
        printed when exiting. Pass the empty string to suppress
        printing an exit message. If exitmsg ni sio given ama Tupu,
        a default message ni printed.

        """
        jaribu:
            sys.ps1
        tatizo AttributeError:
            sys.ps1 = ">>> "
        jaribu:
            sys.ps2
        tatizo AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" ama "license" kila more information.'
        ikiwa banner ni Tupu:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        lasivyo banner:
            self.write("%s\n" % str(banner))
        more = 0
        wakati 1:
            jaribu:
                ikiwa more:
                    prompt = sys.ps2
                isipokua:
                    prompt = sys.ps1
                jaribu:
                    line = self.raw_uliza(prompt)
                tatizo EOFError:
                    self.write("\n")
                    koma
                isipokua:
                    more = self.push(line)
            tatizo KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0
        ikiwa exitmsg ni Tupu:
            self.write('now exiting %s...\n' % self.__class__.__name__)
        lasivyo exitmsg != '':
            self.write('%s\n' % exitmsg)

    eleza push(self, line):
        """Push a line to the interpreter.

        The line should sio have a trailing newline; it may have
        internal newlines.  The line ni appended to a buffer na the
        interpreter's runsource() method ni called ukijumuisha the
        concatenated contents of the buffer kama source.  If this
        indicates that the command was executed ama invalid, the buffer
        ni reset; otherwise, the command ni incomplete, na the buffer
        ni left kama it was after the line was appended.  The return
        value ni 1 ikiwa more input ni required, 0 ikiwa the line was dealt
        ukijumuisha kwenye some way (this ni the same kama runsource()).

        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        ikiwa sio more:
            self.resetbuffer()
        rudisha more

    eleza raw_uliza(self, prompt=""):
        """Write a prompt na read a line.

        The returned line does sio include the trailing newline.
        When the user enters the EOF key sequence, EOFError ni raised.

        The base implementation uses the built-in function
        uliza(); a subkundi may replace this ukijumuisha a different
        implementation.

        """
        rudisha uliza(prompt)



eleza interact(banner=Tupu, readfunc=Tupu, local=Tupu, exitmsg=Tupu):
    """Closely emulate the interactive Python interpreter.

    This ni a backwards compatible interface to the InteractiveConsole
    class.  When readfunc ni sio specified, it attempts to agiza the
    readline module to enable GNU readline ikiwa it ni available.

    Arguments (all optional, all default to Tupu):

    banner -- pitaed to InteractiveConsole.interact()
    readfunc -- ikiwa sio Tupu, replaces InteractiveConsole.raw_uliza()
    local -- pitaed to InteractiveInterpreter.__init__()
    exitmsg -- pitaed to InteractiveConsole.interact()

    """
    console = InteractiveConsole(local)
    ikiwa readfunc ni sio Tupu:
        console.raw_input = readfunc
    isipokua:
        jaribu:
            agiza readline
        tatizo ImportError:
            pita
    console.interact(banner, exitmsg)


ikiwa __name__ == "__main__":
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true',
                       help="don't print version na copyright messages")
    args = parser.parse_args()
    ikiwa args.q ama sys.flags.quiet:
        banner = ''
    isipokua:
        banner = Tupu
    interact(banner)
