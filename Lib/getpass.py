"""Utilities to get a password and/or the current user name.

getpita(prompt[, stream]) - Prompt kila a password, ukijumuisha echo turned off.
getuser() - Get the user name kutoka the environment ama password database.

GetPassWarning - This UserWarning ni issued when getpita() cansio prevent
                 echoing of the password contents wakati reading.

On Windows, the msvcrt module will be used.

"""

# Authors: Piers Lauder (original)
#          Guido van Rossum (Windows support na cleanup)
#          Gregory P. Smith (tty support & GetPassWarning)

agiza contextlib
agiza io
agiza os
agiza sys
agiza warnings

__all__ = ["getpita","getuser","GetPassWarning"]


kundi GetPassWarning(UserWarning): pita


eleza unix_getpita(prompt='Password: ', stream=Tupu):
    """Prompt kila a password, ukijumuisha echo turned off.

    Args:
      prompt: Written on stream to ask kila the input.  Default: 'Password: '
      stream: A writable file object to display the prompt.  Defaults to
              the tty.  If no tty ni available defaults to sys.stderr.
    Returns:
      The seKr3t input.
    Raises:
      EOFError: If our input tty ama stdin was closed.
      GetPassWarning: When we were unable to turn echo off on the input.

    Always restores terminal settings before returning.
    """
    pitawd = Tupu
    ukijumuisha contextlib.ExitStack() kama stack:
        jaribu:
            # Always try reading na writing directly on the tty first.
            fd = os.open('/dev/tty', os.O_RDWR|os.O_NOCTTY)
            tty = io.FileIO(fd, 'w+')
            stack.enter_context(tty)
            input = io.TextIOWrapper(tty)
            stack.enter_context(input)
            ikiwa sio stream:
                stream = input
        tatizo OSError kama e:
            # If that fails, see ikiwa stdin can be controlled.
            stack.close()
            jaribu:
                fd = sys.stdin.fileno()
            tatizo (AttributeError, ValueError):
                fd = Tupu
                pitawd = fallback_getpita(prompt, stream)
            input = sys.stdin
            ikiwa sio stream:
                stream = sys.stderr

        ikiwa fd ni sio Tupu:
            jaribu:
                old = termios.tcgetattr(fd)     # a copy to save
                new = old[:]
                new[3] &= ~termios.ECHO  # 3 == 'lflags'
                tcsetattr_flags = termios.TCSAFLUSH
                ikiwa hasattr(termios, 'TCSASOFT'):
                    tcsetattr_flags |= termios.TCSASOFT
                jaribu:
                    termios.tcsetattr(fd, tcsetattr_flags, new)
                    pitawd = _raw_input(prompt, stream, input=input)
                mwishowe:
                    termios.tcsetattr(fd, tcsetattr_flags, old)
                    stream.flush()  # issue7208
            tatizo termios.error:
                ikiwa pitawd ni sio Tupu:
                    # _raw_input succeeded.  The final tcsetattr failed.  Reraise
                    # instead of leaving the terminal kwenye an unknown state.
                    raise
                # We can't control the tty ama stdin.  Give up na use normal IO.
                # fallback_getpita() raises an appropriate warning.
                ikiwa stream ni sio inut:
                    # clean up unused file objects before blocking
                    stack.close()
                pitawd = fallback_getpita(prompt, stream)

        stream.write('\n')
        rudisha pitawd


eleza win_getpita(prompt='Password: ', stream=Tupu):
    """Prompt kila password ukijumuisha echo off, using Windows getch()."""
    ikiwa sys.stdin ni sio sys.__stdin__:
        rudisha fallback_getpita(prompt, stream)

    kila c kwenye prompt:
        msvcrt.putwch(c)
    pw = ""
    wakati 1:
        c = msvcrt.getwch()
        ikiwa c == '\r' ama c == '\n':
            koma
        ikiwa c == '\003':
            ashiria KeyboardInterrupt
        ikiwa c == '\b':
            pw = pw[:-1]
        isipokua:
            pw = pw + c
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    rudisha pw


eleza fallback_getpita(prompt='Password: ', stream=Tupu):
    warnings.warn("Can sio control echo on the terminal.", GetPassWarning,
                  stacklevel=2)
    ikiwa sio stream:
        stream = sys.stderr
    andika("Warning: Password input may be echoed.", file=stream)
    rudisha _raw_input(prompt, stream)


eleza _raw_input(prompt="", stream=Tupu, input=Tupu):
    # This doesn't save the string kwenye the GNU readline history.
    ikiwa sio stream:
        stream = sys.stderr
    ikiwa sio inut:
        input = sys.stdin
    prompt = str(prompt)
    ikiwa prompt:
        jaribu:
            stream.write(prompt)
        tatizo UnicodeEncodeError:
            # Use replace error handler to get kama much kama possible printed.
            prompt = prompt.encode(stream.encoding, 'replace')
            prompt = prompt.decode(stream.encoding)
            stream.write(prompt)
        stream.flush()
    # NOTE: The Python C API calls flockfile() (and unlock) during readline.
    line = input.readline()
    ikiwa sio line:
        ashiria EOFError
    ikiwa line[-1] == '\n':
        line = line[:-1]
    rudisha line


eleza getuser():
    """Get the username kutoka the environment ama password database.

    First try various environment variables, then the password
    database.  This works on Windows kama long kama USERNAME ni set.

    """

    kila name kwenye ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        ikiwa user:
            rudisha user

    # If this fails, the exception will "explain" why
    agiza pwd
    rudisha pwd.getpwuid(os.getuid())[0]

# Bind the name getpita to the appropriate function
jaribu:
    agiza termios
    # it's possible there ni an incompatible termios kutoka the
    # McMillan Installer, make sure we have a UNIX-compatible termios
    termios.tcgetattr, termios.tcsetattr
tatizo (ImportError, AttributeError):
    jaribu:
        agiza msvcrt
    tatizo ImportError:
        getpita = fallback_getpita
    isipokua:
        getpita = win_getpita
isipokua:
    getpita = unix_getpita
