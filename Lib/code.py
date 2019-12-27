"""Utilities needed to emulate Python's interactive interpreter.

"""

# Inspired by similar code by Jeff Epler and Fredrik Lundh.


agiza sys
agiza traceback
kutoka codeop agiza CommandCompiler, compile_command

__all__ = ["InteractiveInterpreter", "InteractiveConsole", "interact",
           "compile_command"]

kundi InteractiveInterpreter:
    """Base kundi for InteractiveConsole.

    This kundi deals with parsing and interpreter state (the user's
    namespace); it doesn't deal with input buffering or prompting or
    input file naming (the filename is always passed in explicitly).

    """

    eleza __init__(self, locals=None):
        """Constructor.

        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary with key "__name__" set to "__console__" and key
        "__doc__" set to None.

        """
        ikiwa locals is None:
            locals = {"__name__": "__console__", "__doc__": None}
        self.locals = locals
        self.compile = CommandCompiler()

    eleza runsource(self, source, filename="<input>", symbol="single"):
        """Compile and run some source in the interpreter.

        Arguments are as for compile_command().

        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.

        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.

        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.runcode() (which
        also handles run-time exceptions, except for SystemExit).

        The rudisha value is True in case 2, False in the other cases (unless
        an exception is raised).  The rudisha value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.

        """
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            rudisha False

        ikiwa code is None:
            # Case 2
            rudisha True

        # Case 3
        self.runcode(code)
        rudisha False

    eleza runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        """
        try:
            exec(code, self.locals)
        except SystemExit:
            raise
        except:
            self.showtraceback()

    eleza showsyntaxerror(self, filename=None):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename is given, it is stuffed in the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading kutoka a string).

        The output is written by self.write(), below.

        """
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        ikiwa filename and type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value.args
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        ikiwa sys.excepthook is sys.__excepthook__:
            lines = traceback.format_exception_only(type, value)
            self.write(''.join(lines))
        else:
            # If someone has set sys.excepthook, we let that take precedence
            # over self.write
            sys.excepthook(type, value, tb)

    eleza showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code.

        The output is written by self.write(), below.

        """
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        try:
            lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
            ikiwa sys.excepthook is sys.__excepthook__:
                self.write(''.join(lines))
            else:
                # If someone has set sys.excepthook, we let that take precedence
                # over self.write
                sys.excepthook(ei[0], ei[1], last_tb)
        finally:
            last_tb = ei = None

    eleza write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subkundi may
        replace this with a different implementation.

        """
        sys.stderr.write(data)


kundi InteractiveConsole(InteractiveInterpreter):
    """Closely emulate the behavior of the interactive Python interpreter.

    This kundi builds on InteractiveInterpreter and adds prompting
    using the familiar sys.ps1 and sys.ps2, and input buffering.

    """

    eleza __init__(self, locals=None, filename="<console>"):
        """Constructor.

        The optional locals argument will be passed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up in tracebacks.

        """
        InteractiveInterpreter.__init__(self, locals)
        self.filename = filename
        self.resetbuffer()

    eleza resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    eleza interact(self, banner=None, exitmsg=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specifies the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current kundi name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).

        The optional exitmsg argument specifies the exit message
        printed when exiting. Pass the empty string to suppress
        printing an exit message. If exitmsg is not given or None,
        a default message is printed.

        """
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        ikiwa banner is None:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        elikiwa banner:
            self.write("%s\n" % str(banner))
        more = 0
        while 1:
            try:
                ikiwa more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0
        ikiwa exitmsg is None:
            self.write('now exiting %s...\n' % self.__class__.__name__)
        elikiwa exitmsg != '':
            self.write('%s\n' % exitmsg)

    eleza push(self, line):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 ikiwa more input is required, 0 ikiwa the line was dealt
        with in some way (this is the same as runsource()).

        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        ikiwa not more:
            self.resetbuffer()
        rudisha more

    eleza raw_input(self, prompt=""):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        input(); a subkundi may replace this with a different
        implementation.

        """
        rudisha input(prompt)



eleza interact(banner=None, readfunc=None, local=None, exitmsg=None):
    """Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to agiza the
    readline module to enable GNU readline ikiwa it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- ikiwa not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()
    exitmsg -- passed to InteractiveConsole.interact()

    """
    console = InteractiveConsole(local)
    ikiwa readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            agiza readline
        except ImportError:
            pass
    console.interact(banner, exitmsg)


ikiwa __name__ == "__main__":
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', action='store_true',
                       help="don't print version and copyright messages")
    args = parser.parse_args()
    ikiwa args.q or sys.flags.quiet:
        banner = ''
    else:
        banner = None
    interact(banner)
