# subprocess - Subprocesses ukijumuisha accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>
#
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/2.4/license kila licensing details.

r"""Subprocesses ukijumuisha accessible I/O streams

This module allows you to spawn processes, connect to their
input/output/error pipes, na obtain their rudisha codes.

For a complete description of this module see the Python documentation.

Main API
========
run(...): Runs a command, waits kila it to complete, then returns a
          CompletedProcess instance.
Popen(...): A kundi kila flexibly executing a command kwenye a new process

Constants
---------
DEVNULL: Special value that indicates that os.devnull should be used
PIPE:    Special value that indicates a pipe should be created
STDOUT:  Special value that indicates that stderr should go to stdout


Older API
=========
call(...): Runs a command, waits kila it to complete, then returns
    the rudisha code.
check_call(...): Same kama call() but raises CalledProcessError()
    ikiwa rudisha code ni sio 0
check_output(...): Same kama check_call() but returns the contents of
    stdout instead of a rudisha code
getoutput(...): Runs a command kwenye the shell, waits kila it to complete,
    then returns the output
getstatusoutput(...): Runs a command kwenye the shell, waits kila it to complete,
    then returns a (exitcode, output) tuple
"""

agiza builtins
agiza errno
agiza io
agiza os
agiza time
agiza signal
agiza sys
agiza threading
agiza warnings
agiza contextlib
kutoka time agiza monotonic kama _time


__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call", "getstatusoutput",
           "getoutput", "check_output", "run", "CalledProcessError", "DEVNULL",
           "SubprocessError", "TimeoutExpired", "CompletedProcess"]
           # NOTE: We intentionally exclude list2cmdline kama it is
           # considered an internal implementation detail.  issue10838.

jaribu:
    agiza msvcrt
    agiza _winapi
    _mswindows = Kweli
tatizo ModuleNotFoundError:
    _mswindows = Uongo
    agiza _posixsubprocess
    agiza select
    agiza selectors
isipokua:
    kutoka _winapi agiza (CREATE_NEW_CONSOLE, CREATE_NEW_PROCESS_GROUP,
                         STD_INPUT_HANDLE, STD_OUTPUT_HANDLE,
                         STD_ERROR_HANDLE, SW_HIDE,
                         STARTF_USESTDHANDLES, STARTF_USESHOWWINDOW,
                         ABOVE_NORMAL_PRIORITY_CLASS, BELOW_NORMAL_PRIORITY_CLASS,
                         HIGH_PRIORITY_CLASS, IDLE_PRIORITY_CLASS,
                         NORMAL_PRIORITY_CLASS, REALTIME_PRIORITY_CLASS,
                         CREATE_NO_WINDOW, DETACHED_PROCESS,
                         CREATE_DEFAULT_ERROR_MODE, CREATE_BREAKAWAY_FROM_JOB)

    __all__.extend(["CREATE_NEW_CONSOLE", "CREATE_NEW_PROCESS_GROUP",
                    "STD_INPUT_HANDLE", "STD_OUTPUT_HANDLE",
                    "STD_ERROR_HANDLE", "SW_HIDE",
                    "STARTF_USESTDHANDLES", "STARTF_USESHOWWINDOW",
                    "STARTUPINFO",
                    "ABOVE_NORMAL_PRIORITY_CLASS", "BELOW_NORMAL_PRIORITY_CLASS",
                    "HIGH_PRIORITY_CLASS", "IDLE_PRIORITY_CLASS",
                    "NORMAL_PRIORITY_CLASS", "REALTIME_PRIORITY_CLASS",
                    "CREATE_NO_WINDOW", "DETACHED_PROCESS",
                    "CREATE_DEFAULT_ERROR_MODE", "CREATE_BREAKAWAY_FROM_JOB"])


# Exception classes used by this module.
kundi SubprocessError(Exception): pita


kundi CalledProcessError(SubprocessError):
    """Raised when run() ni called ukijumuisha check=Kweli na the process
    returns a non-zero exit status.

    Attributes:
      cmd, returncode, stdout, stderr, output
    """
    eleza __init__(self, returncode, cmd, output=Tupu, stderr=Tupu):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr

    eleza __str__(self):
        ikiwa self.returncode na self.returncode < 0:
            jaribu:
                rudisha "Command '%s' died ukijumuisha %r." % (
                        self.cmd, signal.Signals(-self.returncode))
            tatizo ValueError:
                rudisha "Command '%s' died ukijumuisha unknown signal %d." % (
                        self.cmd, -self.returncode)
        isipokua:
            rudisha "Command '%s' returned non-zero exit status %d." % (
                    self.cmd, self.returncode)

    @property
    eleza stdout(self):
        """Alias kila output attribute, to match stderr"""
        rudisha self.output

    @stdout.setter
    eleza stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout ni a transparent alias kila .output
        self.output = value


kundi TimeoutExpired(SubprocessError):
    """This exception ni raised when the timeout expires wakati waiting kila a
    child process.

    Attributes:
        cmd, output, stdout, stderr, timeout
    """
    eleza __init__(self, cmd, timeout, output=Tupu, stderr=Tupu):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output
        self.stderr = stderr

    eleza __str__(self):
        rudisha ("Command '%s' timed out after %s seconds" %
                (self.cmd, self.timeout))

    @property
    eleza stdout(self):
        rudisha self.output

    @stdout.setter
    eleza stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout ni a transparent alias kila .output
        self.output = value


ikiwa _mswindows:
    kundi STARTUPINFO:
        eleza __init__(self, *, dwFlags=0, hStdInput=Tupu, hStdOutput=Tupu,
                     hStdError=Tupu, wShowWindow=0, lpAttributeList=Tupu):
            self.dwFlags = dwFlags
            self.hStdInput = hStdInput
            self.hStdOutput = hStdOutput
            self.hStdError = hStdError
            self.wShowWindow = wShowWindow
            self.lpAttributeList = lpAttributeList ama {"handle_list": []}

        eleza copy(self):
            attr_list = self.lpAttributeList.copy()
            ikiwa 'handle_list' kwenye attr_list:
                attr_list['handle_list'] = list(attr_list['handle_list'])

            rudisha STARTUPINFO(dwFlags=self.dwFlags,
                               hStdInput=self.hStdInput,
                               hStdOutput=self.hStdOutput,
                               hStdError=self.hStdError,
                               wShowWindow=self.wShowWindow,
                               lpAttributeList=attr_list)


    kundi Handle(int):
        closed = Uongo

        eleza Close(self, CloseHandle=_winapi.CloseHandle):
            ikiwa sio self.closed:
                self.closed = Kweli
                CloseHandle(self)

        eleza Detach(self):
            ikiwa sio self.closed:
                self.closed = Kweli
                rudisha int(self)
            ashiria ValueError("already closed")

        eleza __repr__(self):
            rudisha "%s(%d)" % (self.__class__.__name__, int(self))

        __del__ = Close
isipokua:
    # When select ama poll has indicated that the file ni writable,
    # we can write up to _PIPE_BUF bytes without risk of blocking.
    # POSIX defines PIPE_BUF kama >= 512.
    _PIPE_BUF = getattr(select, 'PIPE_BUF', 512)

    # poll/select have the advantage of sio requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    ikiwa hasattr(selectors, 'PollSelector'):
        _PopenSelector = selectors.PollSelector
    isipokua:
        _PopenSelector = selectors.SelectSelector


ikiwa _mswindows:
    # On Windows we just need to close `Popen._handle` when we no longer need
    # it, so that the kernel can free it. `Popen._handle` gets closed
    # implicitly when the `Popen` instance ni finalized (see `Handle.__del__`,
    # which ni calling `CloseHandle` kama requested kwenye [1]), so there ni nothing
    # kila `_cleanup` to do.
    #
    # [1] https://docs.microsoft.com/en-us/windows/desktop/ProcThread/
    # creating-processes
    _active = Tupu

    eleza _cleanup():
        pita
isipokua:
    # This lists holds Popen instances kila which the underlying process had sio
    # exited at the time its __del__ method got called: those processes are
    # wait()ed kila synchronously kutoka _cleanup() when a new Popen object is
    # created, to avoid zombie processes.
    _active = []

    eleza _cleanup():
        ikiwa _active ni Tupu:
            rudisha
        kila inst kwenye _active[:]:
            res = inst._internal_poll(_deadstate=sys.maxsize)
            ikiwa res ni sio Tupu:
                jaribu:
                    _active.remove(inst)
                tatizo ValueError:
                    # This can happen ikiwa two threads create a new Popen instance.
                    # It's harmless that it was already removed, so ignore.
                    pita

PIPE = -1
STDOUT = -2
DEVNULL = -3


# XXX This function ni only used by multiprocessing na the test suite,
# but it's here so that it can be imported when Python ni compiled without
# threads.

eleza _optim_args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    optimization settings kwenye sys.flags."""
    args = []
    value = sys.flags.optimize
    ikiwa value > 0:
        args.append('-' + 'O' * value)
    rudisha args


eleza _args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    settings kwenye sys.flags, sys.warnoptions na sys._xoptions."""
    flag_opt_map = {
        'debug': 'd',
        # 'inspect': 'i',
        # 'interactive': 'i',
        'dont_write_bytecode': 'B',
        'no_site': 'S',
        'verbose': 'v',
        'bytes_warning': 'b',
        'quiet': 'q',
        # -O ni handled kwenye _optim_args_from_interpreter_flags()
    }
    args = _optim_args_from_interpreter_flags()
    kila flag, opt kwenye flag_opt_map.items():
        v = getattr(sys.flags, flag)
        ikiwa v > 0:
            args.append('-' + opt * v)

    ikiwa sys.flags.isolated:
        args.append('-I')
    isipokua:
        ikiwa sys.flags.ignore_environment:
            args.append('-E')
        ikiwa sys.flags.no_user_site:
            args.append('-s')

    # -W options
    warnopts = sys.warnoptions[:]
    bytes_warning = sys.flags.bytes_warning
    xoptions = getattr(sys, '_xoptions', {})
    dev_mode = ('dev' kwenye xoptions)

    ikiwa bytes_warning > 1:
        warnopts.remove("error::BytesWarning")
    lasivyo bytes_warning:
        warnopts.remove("default::BytesWarning")
    ikiwa dev_mode:
        warnopts.remove('default')
    kila opt kwenye warnopts:
        args.append('-W' + opt)

    # -X options
    ikiwa dev_mode:
        args.extend(('-X', 'dev'))
    kila opt kwenye ('faulthandler', 'tracemalloc', 'importtime',
                'showalloccount', 'showrefcount', 'utf8'):
        ikiwa opt kwenye xoptions:
            value = xoptions[opt]
            ikiwa value ni Kweli:
                arg = opt
            isipokua:
                arg = '%s=%s' % (opt, value)
            args.extend(('-X', arg))

    rudisha args


eleza call(*popenargs, timeout=Tupu, **kwargs):
    """Run command ukijumuisha arguments.  Wait kila command to complete ama
    timeout, then rudisha the returncode attribute.

    The arguments are the same kama kila the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    ukijumuisha Popen(*popenargs, **kwargs) kama p:
        jaribu:
            rudisha p.wait(timeout=timeout)
        tatizo:  # Including KeyboardInterrupt, wait handled that.
            p.kill()
            # We don't call p.wait() again kama p.__exit__ does that kila us.
            raise


eleza check_call(*popenargs, **kwargs):
    """Run command ukijumuisha arguments.  Wait kila command to complete.  If
    the exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    rudisha code kwenye the returncode attribute.

    The arguments are the same kama kila the call function.  Example:

    check_call(["ls", "-l"])
    """
    retcode = call(*popenargs, **kwargs)
    ikiwa retcode:
        cmd = kwargs.get("args")
        ikiwa cmd ni Tupu:
            cmd = popenargs[0]
        ashiria CalledProcessError(retcode, cmd)
    rudisha 0


eleza check_output(*popenargs, timeout=Tupu, **kwargs):
    r"""Run command ukijumuisha arguments na rudisha its output.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the rudisha code kwenye the returncode
    attribute na output kwenye the output attribute.

    The arguments are the same kama kila the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    b'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument ni sio allowed kama it ni used internally.
    To capture standard error kwenye the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    b'ls: non_existent_file: No such file ama directory\n'

    There ni an additional optional argument, "input", allowing you to
    pita a string to the subprocess's stdin.  If you use this argument
    you may sio also use the Popen constructor's "stdin" argument, as
    it too will be used internally.  Example:

    >>> check_output(["sed", "-e", "s/foo/bar/"],
    ...              input=b"when kwenye the course of fooman events\n")
    b'when kwenye the course of barman events\n'

    By default, all communication ni kwenye bytes, na therefore any "input"
    should be bytes, na the rudisha value will be bytes.  If kwenye text mode,
    any "input" should be a string, na the rudisha value will be a string
    decoded according to locale encoding, ama by "encoding" ikiwa set. Text mode
    ni triggered by setting any of text, encoding, errors ama universal_newlines.
    """
    ikiwa 'stdout' kwenye kwargs:
        ashiria ValueError('stdout argument sio allowed, it will be overridden.')

    ikiwa 'input' kwenye kwargs na kwargs['input'] ni Tupu:
        # Explicitly pitaing input=Tupu was previously equivalent to pitaing an
        # empty string. That ni maintained here kila backwards compatibility.
        kwargs['input'] = '' ikiwa kwargs.get('universal_newlines', Uongo) isipokua b''

    rudisha run(*popenargs, stdout=PIPE, timeout=timeout, check=Kweli,
               **kwargs).stdout


kundi CompletedProcess(object):
    """A process that has finished running.

    This ni returned by run().

    Attributes:
      args: The list ama str args pitaed to run().
      returncode: The exit code of the process, negative kila signals.
      stdout: The standard output (Tupu ikiwa sio captured).
      stderr: The standard error (Tupu ikiwa sio captured).
    """
    eleza __init__(self, args, returncode, stdout=Tupu, stderr=Tupu):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    eleza __repr__(self):
        args = ['args={!r}'.format(self.args),
                'returncode={!r}'.format(self.returncode)]
        ikiwa self.stdout ni sio Tupu:
            args.append('stdout={!r}'.format(self.stdout))
        ikiwa self.stderr ni sio Tupu:
            args.append('stderr={!r}'.format(self.stderr))
        rudisha "{}({})".format(type(self).__name__, ', '.join(args))

    eleza check_returncode(self):
        """Raise CalledProcessError ikiwa the exit code ni non-zero."""
        ikiwa self.returncode:
            ashiria CalledProcessError(self.returncode, self.args, self.stdout,
                                     self.stderr)


eleza run(*popenargs,
        input=Tupu, capture_output=Uongo, timeout=Tupu, check=Uongo, **kwargs):
    """Run command ukijumuisha arguments na rudisha a CompletedProcess instance.

    The returned instance will have attributes args, returncode, stdout na
    stderr. By default, stdout na stderr are sio captured, na those attributes
    will be Tupu. Pass stdout=PIPE and/or stderr=PIPE kwenye order to capture them.

    If check ni Kweli na the exit code was non-zero, it raises a
    CalledProcessError. The CalledProcessError object will have the rudisha code
    kwenye the returncode attribute, na output & stderr attributes ikiwa those streams
    were captured.

    If timeout ni given, na the process takes too long, a TimeoutExpired
    exception will be raised.

    There ni an optional argument "input", allowing you to
    pita bytes ama a string to the subprocess's stdin.  If you use this argument
    you may sio also use the Popen constructor's "stdin" argument, as
    it will be used internally.

    By default, all communication ni kwenye bytes, na therefore any "input" should
    be bytes, na the stdout na stderr will be bytes. If kwenye text mode, any
    "input" should be a string, na stdout na stderr will be strings decoded
    according to locale encoding, ama by "encoding" ikiwa set. Text mode is
    triggered by setting any of text, encoding, errors ama universal_newlines.

    The other arguments are the same kama kila the Popen constructor.
    """
    ikiwa input ni sio Tupu:
        ikiwa kwargs.get('stdin') ni sio Tupu:
            ashiria ValueError('stdin na input arguments may sio both be used.')
        kwargs['stdin'] = PIPE

    ikiwa capture_output:
        ikiwa kwargs.get('stdout') ni sio Tupu ama kwargs.get('stderr') ni sio Tupu:
            ashiria ValueError('stdout na stderr arguments may sio be used '
                             'ukijumuisha capture_output.')
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE

    ukijumuisha Popen(*popenargs, **kwargs) kama process:
        jaribu:
            stdout, stderr = process.communicate(input, timeout=timeout)
        tatizo TimeoutExpired kama exc:
            process.kill()
            ikiwa _mswindows:
                # Windows accumulates the output kwenye a single blocking
                # read() call run on child threads, ukijumuisha the timeout
                # being done kwenye a join() on those threads.  communicate()
                # _after_ kill() ni required to collect that na add it
                # to the exception.
                exc.stdout, exc.stderr = process.communicate()
            isipokua:
                # POSIX _communicate already populated the output so
                # far into the TimeoutExpired exception.
                process.wait()
            raise
        tatizo:  # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() kama .__exit__ does that kila us.
            raise
        retcode = process.poll()
        ikiwa check na retcode:
            ashiria CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    rudisha CompletedProcess(process.args, retcode, stdout, stderr)


eleza list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules kama the MS C runtime:

    1) Arguments are delimited by white space, which ni either a
       space ama a tab.

    2) A string surrounded by double quotation marks is
       interpreted kama a single argument, regardless of white space
       contained within.  A quoted string can be embedded kwenye an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted kama a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes ni interpreted kama a literal
       backslash.  If the number of backslashes ni odd, the last
       backslash escapes the next double quotation mark as
       described kwenye rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # ama search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = Uongo
    kila arg kwenye map(os.fsdecode, seq):
        bs_buf = []

        # Add a space to separate this argument kutoka the others
        ikiwa result:
            result.append(' ')

        needquote = (" " kwenye arg) ama ("\t" kwenye arg) ama sio arg
        ikiwa needquote:
            result.append('"')

        kila c kwenye arg:
            ikiwa c == '\\':
                # Don't know ikiwa we need to double yet.
                bs_buf.append(c)
            lasivyo c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            isipokua:
                # Normal char
                ikiwa bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, ikiwa any.
        ikiwa bs_buf:
            result.extend(bs_buf)

        ikiwa needquote:
            result.extend(bs_buf)
            result.append('"')

    rudisha ''.join(result)


# Various tools kila executing commands na looking at their output na status.
#

eleza getstatusoutput(cmd):
    """Return (exitcode, output) of executing cmd kwenye a shell.

    Execute the string 'cmd' kwenye a shell ukijumuisha 'check_output' na
    rudisha a 2-tuple (status, output). The locale encoding ni used
    to decode the output na process newlines.

    A trailing newline ni stripped kutoka the output.
    The exit status kila the command can be interpreted
    according to the rules kila the function 'wait'. Example:

    >>> agiza subprocess
    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (1, 'cat: /bin/junk: No such file ama directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (127, 'sh: /bin/junk: sio found')
    >>> subprocess.getstatusoutput('/bin/kill $$')
    (-15, '')
    """
    jaribu:
        data = check_output(cmd, shell=Kweli, text=Kweli, stderr=STDOUT)
        exitcode = 0
    tatizo CalledProcessError kama ex:
        data = ex.output
        exitcode = ex.returncode
    ikiwa data[-1:] == '\n':
        data = data[:-1]
    rudisha exitcode, data

eleza getoutput(cmd):
    """Return output (stdout ama stderr) of executing cmd kwenye a shell.

    Like getstatusoutput(), tatizo the exit status ni ignored na the rudisha
    value ni a string containing the command's output.  Example:

    >>> agiza subprocess
    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'
    """
    rudisha getstatusoutput(cmd)[1]


eleza _use_posix_spawn():
    """Check ikiwa posix_spawn() can be used kila subprocess.

    subprocess requires a posix_spawn() implementation that properly reports
    errors to the parent process, & sets errno on the following failures:

    * Process attribute actions failed.
    * File actions failed.
    * exec() failed.

    Prefer an implementation which can use vfork() kwenye some cases kila best
    performance.
    """
    ikiwa _mswindows ama sio hasattr(os, 'posix_spawn'):
        # os.posix_spawn() ni sio available
        rudisha Uongo

    ikiwa sys.platform == 'darwin':
        # posix_spawn() ni a syscall on macOS na properly reports errors
        rudisha Kweli

    # Check libc name na runtime libc version
    jaribu:
        ver = os.confstr('CS_GNU_LIBC_VERSION')
        # parse 'glibc 2.28' kama ('glibc', (2, 28))
        parts = ver.split(maxsplit=1)
        ikiwa len(parts) != 2:
            # reject unknown format
            ashiria ValueError
        libc = parts[0]
        version = tuple(map(int, parts[1].split('.')))

        ikiwa sys.platform == 'linux' na libc == 'glibc' na version >= (2, 24):
            # glibc 2.24 has a new Linux posix_spawn implementation using vfork
            # which properly reports errors to the parent process.
            rudisha Kweli
        # Note: Don't use the implementation kwenye earlier glibc because it doesn't
        # use vfork (even ikiwa glibc 2.26 added a pipe to properly report errors
        # to the parent process).
    tatizo (AttributeError, ValueError, OSError):
        # os.confstr() ama CS_GNU_LIBC_VERSION value sio available
        pita

    # By default, assume that posix_spawn() does sio properly report errors.
    rudisha Uongo


_USE_POSIX_SPAWN = _use_posix_spawn()


kundi Popen(object):
    """ Execute a child program kwenye a new process.

    For a complete description of the arguments see the Python documentation.

    Arguments:
      args: A string, ama a sequence of program arguments.

      bufsize: supplied kama the buffering argument to the open() function when
          creating the stdin/stdout/stderr pipe file objects

      executable: A replacement program to execute.

      stdin, stdout na stderr: These specify the executed programs' standard
          input, standard output na standard error file handles, respectively.

      preexec_fn: (POSIX only) An object to be called kwenye the child process
          just before the child ni executed.

      close_fds: Controls closing ama inheriting of file descriptors.

      shell: If true, the command will be executed through the shell.

      cwd: Sets the current directory before the child ni executed.

      env: Defines the environment variables kila the new process.

      text: If true, decode stdin, stdout na stderr using the given encoding
          (ikiwa set) ama the system default otherwise.

      universal_newlines: Alias of text, provided kila backwards compatibility.

      startupinfo na creationflags (Windows only)

      restore_signals (POSIX only)

      start_new_session (POSIX only)

      pita_fds (POSIX only)

      encoding na errors: Text mode encoding na error handling to use for
          file objects stdin, stdout na stderr.

    Attributes:
        stdin, stdout, stderr, pid, returncode
    """
    _child_created = Uongo  # Set here since __del__ checks it

    eleza __init__(self, args, bufsize=-1, executable=Tupu,
                 stdin=Tupu, stdout=Tupu, stderr=Tupu,
                 preexec_fn=Tupu, close_fds=Kweli,
                 shell=Uongo, cwd=Tupu, env=Tupu, universal_newlines=Tupu,
                 startupinfo=Tupu, creationflags=0,
                 restore_signals=Kweli, start_new_session=Uongo,
                 pita_fds=(), *, encoding=Tupu, errors=Tupu, text=Tupu):
        """Create new Popen instance."""
        _cleanup()
        # Held wakati anything ni calling waitpid before returncode has been
        # updated to prevent clobbering returncode ikiwa wait() ama poll() are
        # called kutoka multiple threads at once.  After acquiring the lock,
        # code must re-check self.returncode to see ikiwa another thread just
        # finished a waitpid() call.
        self._waitpid_lock = threading.Lock()

        self._input = Tupu
        self._communication_started = Uongo
        ikiwa bufsize ni Tupu:
            bufsize = -1  # Restore default
        ikiwa sio isinstance(bufsize, int):
            ashiria TypeError("bufsize must be an integer")

        ikiwa _mswindows:
            ikiwa preexec_fn ni sio Tupu:
                ashiria ValueError("preexec_fn ni sio supported on Windows "
                                 "platforms")
        isipokua:
            # POSIX
            ikiwa pita_fds na sio close_fds:
                warnings.warn("pita_fds overriding close_fds.", RuntimeWarning)
                close_fds = Kweli
            ikiwa startupinfo ni sio Tupu:
                ashiria ValueError("startupinfo ni only supported on Windows "
                                 "platforms")
            ikiwa creationflags != 0:
                ashiria ValueError("creationflags ni only supported on Windows "
                                 "platforms")

        self.args = args
        self.stdin = Tupu
        self.stdout = Tupu
        self.stderr = Tupu
        self.pid = Tupu
        self.returncode = Tupu
        self.encoding = encoding
        self.errors = errors

        # Validate the combinations of text na universal_newlines
        ikiwa (text ni sio Tupu na universal_newlines ni sio Tupu
            na bool(universal_newlines) != bool(text)):
            ashiria SubprocessError('Cansio disambiguate when both text '
                                  'and universal_newlines are supplied but '
                                  'different. Pass one ama the other.')

        # Input na output objects. The general principle ni like
        # this:
        #
        # Parent                   Child
        # ------                   -----
        # p2cwrite   ---stdin--->  p2cread
        # c2pread    <--stdout---  c2pwrite
        # errread    <--stderr---  errwrite
        #
        # On POSIX, the child objects are file descriptors.  On
        # Windows, these are Windows file handles.  The parent objects
        # are file descriptors on both platforms.  The parent objects
        # are -1 when sio using PIPEs. The child objects are -1
        # when sio redirecting.

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        # We wrap OS handles *before* launching the child, otherwise a
        # quickly terminating child could make our fds unwrappable
        # (see #8458).

        ikiwa _mswindows:
            ikiwa p2cwrite != -1:
                p2cwrite = msvcrt.open_osfhandle(p2cwrite.Detach(), 0)
            ikiwa c2pread != -1:
                c2pread = msvcrt.open_osfhandle(c2pread.Detach(), 0)
            ikiwa errread != -1:
                errread = msvcrt.open_osfhandle(errread.Detach(), 0)

        self.text_mode = encoding ama errors ama text ama universal_newlines

        # How long to resume waiting on a child after the first ^C.
        # There ni no right value kila this.  The purpose ni to be polite
        # yet remain good kila interactive users trying to exit a tool.
        self._sigint_wait_secs = 0.25  # 1/xkcd221.getRandomNumber()

        self._closed_child_pipe_fds = Uongo

        ikiwa self.text_mode:
            ikiwa bufsize == 1:
                line_buffering = Kweli
                # Use the default buffer size kila the underlying binary streams
                # since they don't support line buffering.
                bufsize = -1
            isipokua:
                line_buffering = Uongo

        jaribu:
            ikiwa p2cwrite != -1:
                self.stdin = io.open(p2cwrite, 'wb', bufsize)
                ikiwa self.text_mode:
                    self.stdin = io.TextIOWrapper(self.stdin, write_through=Kweli,
                            line_buffering=line_buffering,
                            encoding=encoding, errors=errors)
            ikiwa c2pread != -1:
                self.stdout = io.open(c2pread, 'rb', bufsize)
                ikiwa self.text_mode:
                    self.stdout = io.TextIOWrapper(self.stdout,
                            encoding=encoding, errors=errors)
            ikiwa errread != -1:
                self.stderr = io.open(errread, 'rb', bufsize)
                ikiwa self.text_mode:
                    self.stderr = io.TextIOWrapper(self.stderr,
                            encoding=encoding, errors=errors)

            self._execute_child(args, executable, preexec_fn, close_fds,
                                pita_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                restore_signals, start_new_session)
        tatizo:
            # Cleanup ikiwa the child failed starting.
            kila f kwenye filter(Tupu, (self.stdin, self.stdout, self.stderr)):
                jaribu:
                    f.close()
                tatizo OSError:
                    pita  # Ignore EBADF ama other errors.

            ikiwa sio self._closed_child_pipe_fds:
                to_close = []
                ikiwa stdin == PIPE:
                    to_close.append(p2cread)
                ikiwa stdout == PIPE:
                    to_close.append(c2pwrite)
                ikiwa stderr == PIPE:
                    to_close.append(errwrite)
                ikiwa hasattr(self, '_devnull'):
                    to_close.append(self._devnull)
                kila fd kwenye to_close:
                    jaribu:
                        ikiwa _mswindows na isinstance(fd, Handle):
                            fd.Close()
                        isipokua:
                            os.close(fd)
                    tatizo OSError:
                        pita

            raise

    @property
    eleza universal_newlines(self):
        # universal_newlines kama retained kama an alias of text_mode kila API
        # compatibility. bpo-31756
        rudisha self.text_mode

    @universal_newlines.setter
    eleza universal_newlines(self, universal_newlines):
        self.text_mode = bool(universal_newlines)

    eleza _translate_newlines(self, data, encoding, errors):
        data = data.decode(encoding, errors)
        rudisha data.replace("\r\n", "\n").replace("\r", "\n")

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, value, traceback):
        ikiwa self.stdout:
            self.stdout.close()
        ikiwa self.stderr:
            self.stderr.close()
        jaribu:  # Flushing a BufferedWriter may ashiria an error
            ikiwa self.stdin:
                self.stdin.close()
        mwishowe:
            ikiwa exc_type == KeyboardInterrupt:
                # https://bugs.python.org/issue25942
                # In the case of a KeyboardInterrupt we assume the SIGINT
                # was also already sent to our child processes.  We can't
                # block indefinitely kama that ni sio user friendly.
                # If we have sio already waited a brief amount of time kwenye
                # an interrupted .wait() ama .communicate() call, do so here
                # kila consistency.
                ikiwa self._sigint_wait_secs > 0:
                    jaribu:
                        self._wait(timeout=self._sigint_wait_secs)
                    tatizo TimeoutExpired:
                        pita
                self._sigint_wait_secs = 0  # Note that this has been done.
                rudisha  # resume the KeyboardInterrupt

            # Wait kila the process to terminate, to avoid zombies.
            self.wait()

    eleza __del__(self, _maxsize=sys.maxsize, _warn=warnings.warn):
        ikiwa sio self._child_created:
            # We didn't get to successfully create a child process.
            rudisha
        ikiwa self.returncode ni Tupu:
            # Not reading subprocess exit status creates a zombie process which
            # ni only destroyed at the parent python process exit
            _warn("subprocess %s ni still running" % self.pid,
                  ResourceWarning, source=self)
        # In case the child hasn't been waited on, check ikiwa it's done.
        self._internal_poll(_deadstate=_maxsize)
        ikiwa self.returncode ni Tupu na _active ni sio Tupu:
            # Child ni still running, keep us alive until we can wait on it.
            _active.append(self)

    eleza _get_devnull(self):
        ikiwa sio hasattr(self, '_devnull'):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        rudisha self._devnull

    eleza _stdin_write(self, input):
        ikiwa input:
            jaribu:
                self.stdin.write(input)
            tatizo BrokenPipeError:
                pita  # communicate() must ignore broken pipe errors.
            tatizo OSError kama exc:
                ikiwa exc.errno == errno.EINVAL:
                    # bpo-19612, bpo-30418: On Windows, stdin.write() fails
                    # ukijumuisha EINVAL ikiwa the child process exited ama ikiwa the child
                    # process ni still running but closed the pipe.
                    pita
                isipokua:
                    raise

        jaribu:
            self.stdin.close()
        tatizo BrokenPipeError:
            pita  # communicate() must ignore broken pipe errors.
        tatizo OSError kama exc:
            ikiwa exc.errno == errno.EINVAL:
                pita
            isipokua:
                raise

    eleza communicate(self, input=Tupu, timeout=Tupu):
        """Interact ukijumuisha process: Send data to stdin na close it.
        Read data kutoka stdout na stderr, until end-of-file is
        reached.  Wait kila process to terminate.

        The optional "input" argument should be data to be sent to the
        child process, ama Tupu, ikiwa no data should be sent to the child.
        communicate() returns a tuple (stdout, stderr).

        By default, all communication ni kwenye bytes, na therefore any
        "input" should be bytes, na the (stdout, stderr) will be bytes.
        If kwenye text mode (indicated by self.text_mode), any "input" should
        be a string, na (stdout, stderr) will be strings decoded
        according to locale encoding, ama by "encoding" ikiwa set. Text mode
        ni triggered by setting any of text, encoding, errors ama
        universal_newlines.
        """

        ikiwa self._communication_started na input:
            ashiria ValueError("Cansio send input after starting communication")

        # Optimization: If we are sio worried about timeouts, we haven't
        # started communicating, na we have one ama zero pipes, using select()
        # ama threads ni unnecessary.
        ikiwa (timeout ni Tupu na sio self._communication_started na
            [self.stdin, self.stdout, self.stderr].count(Tupu) >= 2):
            stdout = Tupu
            stderr = Tupu
            ikiwa self.stdin:
                self._stdin_write(input)
            lasivyo self.stdout:
                stdout = self.stdout.read()
                self.stdout.close()
            lasivyo self.stderr:
                stderr = self.stderr.read()
                self.stderr.close()
            self.wait()
        isipokua:
            ikiwa timeout ni sio Tupu:
                endtime = _time() + timeout
            isipokua:
                endtime = Tupu

            jaribu:
                stdout, stderr = self._communicate(input, endtime, timeout)
            tatizo KeyboardInterrupt:
                # https://bugs.python.org/issue25942
                # See the detailed comment kwenye .wait().
                ikiwa timeout ni sio Tupu:
                    sigint_timeout = min(self._sigint_wait_secs,
                                         self._remaining_time(endtime))
                isipokua:
                    sigint_timeout = self._sigint_wait_secs
                self._sigint_wait_secs = 0  # nothing isipokua should wait.
                jaribu:
                    self._wait(timeout=sigint_timeout)
                tatizo TimeoutExpired:
                    pita
                ashiria  # resume the KeyboardInterrupt

            mwishowe:
                self._communication_started = Kweli

            sts = self.wait(timeout=self._remaining_time(endtime))

        rudisha (stdout, stderr)


    eleza poll(self):
        """Check ikiwa child process has terminated. Set na rudisha returncode
        attribute."""
        rudisha self._internal_poll()


    eleza _remaining_time(self, endtime):
        """Convenience kila _communicate when computing timeouts."""
        ikiwa endtime ni Tupu:
            rudisha Tupu
        isipokua:
            rudisha endtime - _time()


    eleza _check_timeout(self, endtime, orig_timeout, stdout_seq, stderr_seq,
                       skip_check_and_raise=Uongo):
        """Convenience kila checking ikiwa a timeout has expired."""
        ikiwa endtime ni Tupu:
            rudisha
        ikiwa skip_check_and_ashiria ama _time() > endtime:
            ashiria TimeoutExpired(
                    self.args, orig_timeout,
                    output=b''.join(stdout_seq) ikiwa stdout_seq isipokua Tupu,
                    stderr=b''.join(stderr_seq) ikiwa stderr_seq isipokua Tupu)


    eleza wait(self, timeout=Tupu):
        """Wait kila child process to terminate; returns self.returncode."""
        ikiwa timeout ni sio Tupu:
            endtime = _time() + timeout
        jaribu:
            rudisha self._wait(timeout=timeout)
        tatizo KeyboardInterrupt:
            # https://bugs.python.org/issue25942
            # The first keyboard interrupt waits briefly kila the child to
            # exit under the common assumption that it also received the ^C
            # generated SIGINT na will exit rapidly.
            ikiwa timeout ni sio Tupu:
                sigint_timeout = min(self._sigint_wait_secs,
                                     self._remaining_time(endtime))
            isipokua:
                sigint_timeout = self._sigint_wait_secs
            self._sigint_wait_secs = 0  # nothing isipokua should wait.
            jaribu:
                self._wait(timeout=sigint_timeout)
            tatizo TimeoutExpired:
                pita
            ashiria  # resume the KeyboardInterrupt

    eleza _close_pipe_fds(self,
                        p2cread, p2cwrite,
                        c2pread, c2pwrite,
                        errread, errwrite):
        # self._devnull ni sio always defined.
        devnull_fd = getattr(self, '_devnull', Tupu)

        ukijumuisha contextlib.ExitStack() kama stack:
            ikiwa _mswindows:
                ikiwa p2cread != -1:
                    stack.callback(p2cread.Close)
                ikiwa c2pwrite != -1:
                    stack.callback(c2pwrite.Close)
                ikiwa errwrite != -1:
                    stack.callback(errwrite.Close)
            isipokua:
                ikiwa p2cread != -1 na p2cwrite != -1 na p2cread != devnull_fd:
                    stack.callback(os.close, p2cread)
                ikiwa c2pwrite != -1 na c2pread != -1 na c2pwrite != devnull_fd:
                    stack.callback(os.close, c2pwrite)
                ikiwa errwrite != -1 na errread != -1 na errwrite != devnull_fd:
                    stack.callback(os.close, errwrite)

            ikiwa devnull_fd ni sio Tupu:
                stack.callback(os.close, devnull_fd)

        # Prevent a double close of these handles/fds kutoka __init__ on error.
        self._closed_child_pipe_fds = Kweli

    ikiwa _mswindows:
        #
        # Windows methods
        #
        eleza _get_handles(self, stdin, stdout, stderr):
            """Construct na rudisha tuple ukijumuisha IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            ikiwa stdin ni Tupu na stdout ni Tupu na stderr ni Tupu:
                rudisha (-1, -1, -1, -1, -1, -1)

            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            ikiwa stdin ni Tupu:
                p2cread = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
                ikiwa p2cread ni Tupu:
                    p2cread, _ = _winapi.CreatePipe(Tupu, 0)
                    p2cread = Handle(p2cread)
                    _winapi.CloseHandle(_)
            lasivyo stdin == PIPE:
                p2cread, p2cwrite = _winapi.CreatePipe(Tupu, 0)
                p2cread, p2cwrite = Handle(p2cread), Handle(p2cwrite)
            lasivyo stdin == DEVNULL:
                p2cread = msvcrt.get_osfhandle(self._get_devnull())
            lasivyo isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            isipokua:
                # Assuming file-like object
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)

            ikiwa stdout ni Tupu:
                c2pwrite = _winapi.GetStdHandle(_winapi.STD_OUTPUT_HANDLE)
                ikiwa c2pwrite ni Tupu:
                    _, c2pwrite = _winapi.CreatePipe(Tupu, 0)
                    c2pwrite = Handle(c2pwrite)
                    _winapi.CloseHandle(_)
            lasivyo stdout == PIPE:
                c2pread, c2pwrite = _winapi.CreatePipe(Tupu, 0)
                c2pread, c2pwrite = Handle(c2pread), Handle(c2pwrite)
            lasivyo stdout == DEVNULL:
                c2pwrite = msvcrt.get_osfhandle(self._get_devnull())
            lasivyo isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            isipokua:
                # Assuming file-like object
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)

            ikiwa stderr ni Tupu:
                errwrite = _winapi.GetStdHandle(_winapi.STD_ERROR_HANDLE)
                ikiwa errwrite ni Tupu:
                    _, errwrite = _winapi.CreatePipe(Tupu, 0)
                    errwrite = Handle(errwrite)
                    _winapi.CloseHandle(_)
            lasivyo stderr == PIPE:
                errread, errwrite = _winapi.CreatePipe(Tupu, 0)
                errread, errwrite = Handle(errread), Handle(errwrite)
            lasivyo stderr == STDOUT:
                errwrite = c2pwrite
            lasivyo stderr == DEVNULL:
                errwrite = msvcrt.get_osfhandle(self._get_devnull())
            lasivyo isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            isipokua:
                # Assuming file-like object
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)

            rudisha (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        eleza _make_inheritable(self, handle):
            """Return a duplicate of handle, which ni inheritable"""
            h = _winapi.DuplicateHandle(
                _winapi.GetCurrentProcess(), handle,
                _winapi.GetCurrentProcess(), 0, 1,
                _winapi.DUPLICATE_SAME_ACCESS)
            rudisha Handle(h)


        eleza _filter_handle_list(self, handle_list):
            """Filter out console handles that can't be used
            kwenye lpAttributeList["handle_list"] na make sure the list
            isn't empty. This also removes duplicate handles."""
            # An handle ukijumuisha it's lowest two bits set might be a special console
            # handle that ikiwa pitaed kwenye lpAttributeList["handle_list"], will
            # cause it to fail.
            rudisha list({handle kila handle kwenye handle_list
                         ikiwa handle & 0x3 != 0x3
                         ama _winapi.GetFileType(handle) !=
                            _winapi.FILE_TYPE_CHAR})


        eleza _execute_child(self, args, executable, preexec_fn, close_fds,
                           pita_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           unused_restore_signals, unused_start_new_session):
            """Execute program (MS Windows version)"""

            assert sio pita_fds, "pita_fds sio supported on Windows."

            ikiwa isinstance(args, str):
                pita
            lasivyo isinstance(args, bytes):
                ikiwa shell:
                    ashiria TypeError('bytes args ni sio allowed on Windows')
                args = list2cmdline([args])
            lasivyo isinstance(args, os.PathLike):
                ikiwa shell:
                    ashiria TypeError('path-like args ni sio allowed when '
                                    'shell ni true')
                args = list2cmdline([args])
            isipokua:
                args = list2cmdline(args)

            ikiwa executable ni sio Tupu:
                executable = os.fsdecode(executable)

            # Process startup details
            ikiwa startupinfo ni Tupu:
                startupinfo = STARTUPINFO()
            isipokua:
                # bpo-34044: Copy STARTUPINFO since it ni modified above,
                # so the caller can reuse it multiple times.
                startupinfo = startupinfo.copy()

            use_std_handles = -1 haiko kwenye (p2cread, c2pwrite, errwrite)
            ikiwa use_std_handles:
                startupinfo.dwFlags |= _winapi.STARTF_USESTDHANDLES
                startupinfo.hStdInput = p2cread
                startupinfo.hStdOutput = c2pwrite
                startupinfo.hStdError = errwrite

            attribute_list = startupinfo.lpAttributeList
            have_handle_list = bool(attribute_list na
                                    "handle_list" kwenye attribute_list na
                                    attribute_list["handle_list"])

            # If we were given an handle_list ama need to create one
            ikiwa have_handle_list ama (use_std_handles na close_fds):
                ikiwa attribute_list ni Tupu:
                    attribute_list = startupinfo.lpAttributeList = {}
                handle_list = attribute_list["handle_list"] = \
                    list(attribute_list.get("handle_list", []))

                ikiwa use_std_handles:
                    handle_list += [int(p2cread), int(c2pwrite), int(errwrite)]

                handle_list[:] = self._filter_handle_list(handle_list)

                ikiwa handle_list:
                    ikiwa sio close_fds:
                        warnings.warn("startupinfo.lpAttributeList['handle_list'] "
                                      "overriding close_fds", RuntimeWarning)

                    # When using the handle_list we always request to inherit
                    # handles but the only handles that will be inherited are
                    # the ones kwenye the handle_list
                    close_fds = Uongo

            ikiwa shell:
                startupinfo.dwFlags |= _winapi.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = _winapi.SW_HIDE
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                args = '{} /c "{}"'.format (comspec, args)

            ikiwa cwd ni sio Tupu:
                cwd = os.fsdecode(cwd)

            sys.audit("subprocess.Popen", executable, args, cwd, env)

            # Start the process
            jaribu:
                hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                                         # no special security
                                         Tupu, Tupu,
                                         int(sio close_fds),
                                         creationflags,
                                         env,
                                         cwd,
                                         startupinfo)
            mwishowe:
                # Child ni launched. Close the parent's copy of those pipe
                # handles that only the child should have open.  You need
                # to make sure that no handles to the write end of the
                # output pipe are maintained kwenye this process ama isipokua the
                # pipe will sio close when the child process exits na the
                # ReadFile will hang.
                self._close_pipe_fds(p2cread, p2cwrite,
                                     c2pread, c2pwrite,
                                     errread, errwrite)

            # Retain the process handle, but close the thread handle
            self._child_created = Kweli
            self._handle = Handle(hp)
            self.pid = pid
            _winapi.CloseHandle(ht)

        eleza _internal_poll(self, _deadstate=Tupu,
                _WaitForSingleObject=_winapi.WaitForSingleObject,
                _WAIT_OBJECT_0=_winapi.WAIT_OBJECT_0,
                _GetExitCodeProcess=_winapi.GetExitCodeProcess):
            """Check ikiwa child process has terminated.  Returns returncode
            attribute.

            This method ni called by __del__, so it can only refer to objects
            kwenye its local scope.

            """
            ikiwa self.returncode ni Tupu:
                ikiwa _WaitForSingleObject(self._handle, 0) == _WAIT_OBJECT_0:
                    self.returncode = _GetExitCodeProcess(self._handle)
            rudisha self.returncode


        eleza _wait(self, timeout):
            """Internal implementation of wait() on Windows."""
            ikiwa timeout ni Tupu:
                timeout_millis = _winapi.INFINITE
            isipokua:
                timeout_millis = int(timeout * 1000)
            ikiwa self.returncode ni Tupu:
                # API note: Returns immediately ikiwa timeout_millis == 0.
                result = _winapi.WaitForSingleObject(self._handle,
                                                     timeout_millis)
                ikiwa result == _winapi.WAIT_TIMEOUT:
                    ashiria TimeoutExpired(self.args, timeout)
                self.returncode = _winapi.GetExitCodeProcess(self._handle)
            rudisha self.returncode


        eleza _readerthread(self, fh, buffer):
            buffer.append(fh.read())
            fh.close()


        eleza _communicate(self, input, endtime, orig_timeout):
            # Start reader threads feeding into a list hanging off of this
            # object, unless they've already been started.
            ikiwa self.stdout na sio hasattr(self, "_stdout_buff"):
                self._stdout_buff = []
                self.stdout_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stdout, self._stdout_buff))
                self.stdout_thread.daemon = Kweli
                self.stdout_thread.start()
            ikiwa self.stderr na sio hasattr(self, "_stderr_buff"):
                self._stderr_buff = []
                self.stderr_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stderr, self._stderr_buff))
                self.stderr_thread.daemon = Kweli
                self.stderr_thread.start()

            ikiwa self.stdin:
                self._stdin_write(input)

            # Wait kila the reader threads, ama time out.  If we time out, the
            # threads remain reading na the fds left open kwenye case the user
            # calls communicate again.
            ikiwa self.stdout ni sio Tupu:
                self.stdout_thread.join(self._remaining_time(endtime))
                ikiwa self.stdout_thread.is_alive():
                    ashiria TimeoutExpired(self.args, orig_timeout)
            ikiwa self.stderr ni sio Tupu:
                self.stderr_thread.join(self._remaining_time(endtime))
                ikiwa self.stderr_thread.is_alive():
                    ashiria TimeoutExpired(self.args, orig_timeout)

            # Collect the output kutoka na close both pipes, now that we know
            # both have been read successfully.
            stdout = Tupu
            stderr = Tupu
            ikiwa self.stdout:
                stdout = self._stdout_buff
                self.stdout.close()
            ikiwa self.stderr:
                stderr = self._stderr_buff
                self.stderr.close()

            # All data exchanged.  Translate lists into strings.
            ikiwa stdout ni sio Tupu:
                stdout = stdout[0]
            ikiwa stderr ni sio Tupu:
                stderr = stderr[0]

            rudisha (stdout, stderr)

        eleza send_signal(self, sig):
            """Send a signal to the process."""
            # Don't signal a process that we know has already died.
            ikiwa self.returncode ni sio Tupu:
                rudisha
            ikiwa sig == signal.SIGTERM:
                self.terminate()
            lasivyo sig == signal.CTRL_C_EVENT:
                os.kill(self.pid, signal.CTRL_C_EVENT)
            lasivyo sig == signal.CTRL_BREAK_EVENT:
                os.kill(self.pid, signal.CTRL_BREAK_EVENT)
            isipokua:
                ashiria ValueError("Unsupported signal: {}".format(sig))

        eleza terminate(self):
            """Terminates the process."""
            # Don't terminate a process that we know has already died.
            ikiwa self.returncode ni sio Tupu:
                rudisha
            jaribu:
                _winapi.TerminateProcess(self._handle, 1)
            tatizo PermissionError:
                # ERROR_ACCESS_DENIED (winerror 5) ni received when the
                # process already died.
                rc = _winapi.GetExitCodeProcess(self._handle)
                ikiwa rc == _winapi.STILL_ACTIVE:
                    raise
                self.returncode = rc

        kill = terminate

    isipokua:
        #
        # POSIX methods
        #
        eleza _get_handles(self, stdin, stdout, stderr):
            """Construct na rudisha tuple ukijumuisha IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            ikiwa stdin ni Tupu:
                pita
            lasivyo stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            lasivyo stdin == DEVNULL:
                p2cread = self._get_devnull()
            lasivyo isinstance(stdin, int):
                p2cread = stdin
            isipokua:
                # Assuming file-like object
                p2cread = stdin.fileno()

            ikiwa stdout ni Tupu:
                pita
            lasivyo stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            lasivyo stdout == DEVNULL:
                c2pwrite = self._get_devnull()
            lasivyo isinstance(stdout, int):
                c2pwrite = stdout
            isipokua:
                # Assuming file-like object
                c2pwrite = stdout.fileno()

            ikiwa stderr ni Tupu:
                pita
            lasivyo stderr == PIPE:
                errread, errwrite = os.pipe()
            lasivyo stderr == STDOUT:
                ikiwa c2pwrite != -1:
                    errwrite = c2pwrite
                isipokua: # child's stdout ni sio set, use parent's stdout
                    errwrite = sys.__stdout__.fileno()
            lasivyo stderr == DEVNULL:
                errwrite = self._get_devnull()
            lasivyo isinstance(stderr, int):
                errwrite = stderr
            isipokua:
                # Assuming file-like object
                errwrite = stderr.fileno()

            rudisha (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        eleza _posix_spawn(self, args, executable, env, restore_signals,
                         p2cread, p2cwrite,
                         c2pread, c2pwrite,
                         errread, errwrite):
            """Execute program using os.posix_spawn()."""
            ikiwa env ni Tupu:
                env = os.environ

            kwargs = {}
            ikiwa restore_signals:
                # See _Py_RestoreSignals() kwenye Python/pylifecycle.c
                sigset = []
                kila signame kwenye ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                    signum = getattr(signal, signame, Tupu)
                    ikiwa signum ni sio Tupu:
                        sigset.append(signum)
                kwargs['setsigdef'] = sigset

            file_actions = []
            kila fd kwenye (p2cwrite, c2pread, errread):
                ikiwa fd != -1:
                    file_actions.append((os.POSIX_SPAWN_CLOSE, fd))
            kila fd, fd2 kwenye (
                (p2cread, 0),
                (c2pwrite, 1),
                (errwrite, 2),
            ):
                ikiwa fd != -1:
                    file_actions.append((os.POSIX_SPAWN_DUP2, fd, fd2))
            ikiwa file_actions:
                kwargs['file_actions'] = file_actions

            self.pid = os.posix_spawn(executable, args, env, **kwargs)
            self._child_created = Kweli

            self._close_pipe_fds(p2cread, p2cwrite,
                                 c2pread, c2pwrite,
                                 errread, errwrite)

        eleza _execute_child(self, args, executable, preexec_fn, close_fds,
                           pita_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           restore_signals, start_new_session):
            """Execute program (POSIX version)"""

            ikiwa isinstance(args, (str, bytes)):
                args = [args]
            lasivyo isinstance(args, os.PathLike):
                ikiwa shell:
                    ashiria TypeError('path-like args ni sio allowed when '
                                    'shell ni true')
                args = [args]
            isipokua:
                args = list(args)

            ikiwa shell:
                # On Android the default shell ni at '/system/bin/sh'.
                unix_shell = ('/system/bin/sh' if
                          hasattr(sys, 'getandroidapilevel') isipokua '/bin/sh')
                args = [unix_shell, "-c"] + args
                ikiwa executable:
                    args[0] = executable

            ikiwa executable ni Tupu:
                executable = args[0]

            sys.audit("subprocess.Popen", executable, args, cwd, env)

            ikiwa (_USE_POSIX_SPAWN
                    na os.path.dirname(executable)
                    na preexec_fn ni Tupu
                    na sio close_fds
                    na sio pita_fds
                    na cwd ni Tupu
                    na (p2cread == -1 ama p2cread > 2)
                    na (c2pwrite == -1 ama c2pwrite > 2)
                    na (errwrite == -1 ama errwrite > 2)
                    na sio start_new_session):
                self._posix_spawn(args, executable, env, restore_signals,
                                  p2cread, p2cwrite,
                                  c2pread, c2pwrite,
                                  errread, errwrite)
                rudisha

            orig_executable = executable

            # For transferring possible exec failure kutoka child to parent.
            # Data format: "exception name:hex errno:description"
            # Pickle ni sio used; it ni complex na involves memory allocation.
            errpipe_read, errpipe_write = os.pipe()
            # errpipe_write must sio be kwenye the standard io 0, 1, ama 2 fd range.
            low_fds_to_close = []
            wakati errpipe_write < 3:
                low_fds_to_close.append(errpipe_write)
                errpipe_write = os.dup(errpipe_write)
            kila low_fd kwenye low_fds_to_close:
                os.close(low_fd)
            jaribu:
                jaribu:
                    # We must avoid complex work that could involve
                    # malloc ama free kwenye the child process to avoid
                    # potential deadlocks, thus we do all this here.
                    # na pita it to fork_exec()

                    ikiwa env ni sio Tupu:
                        env_list = []
                        kila k, v kwenye env.items():
                            k = os.fsencode(k)
                            ikiwa b'=' kwenye k:
                                ashiria ValueError("illegal environment variable name")
                            env_list.append(k + b'=' + os.fsencode(v))
                    isipokua:
                        env_list = Tupu  # Use execv instead of execve.
                    executable = os.fsencode(executable)
                    ikiwa os.path.dirname(executable):
                        executable_list = (executable,)
                    isipokua:
                        # This matches the behavior of os._execvpe().
                        executable_list = tuple(
                            os.path.join(os.fsencode(dir), executable)
                            kila dir kwenye os.get_exec_path(env))
                    fds_to_keep = set(pita_fds)
                    fds_to_keep.add(errpipe_write)
                    self.pid = _posixsubprocess.fork_exec(
                            args, executable_list,
                            close_fds, tuple(sorted(map(int, fds_to_keep))),
                            cwd, env_list,
                            p2cread, p2cwrite, c2pread, c2pwrite,
                            errread, errwrite,
                            errpipe_read, errpipe_write,
                            restore_signals, start_new_session, preexec_fn)
                    self._child_created = Kweli
                mwishowe:
                    # be sure the FD ni closed no matter what
                    os.close(errpipe_write)

                self._close_pipe_fds(p2cread, p2cwrite,
                                     c2pread, c2pwrite,
                                     errread, errwrite)

                # Wait kila exec to fail ama succeed; possibly raising an
                # exception (limited kwenye size)
                errpipe_data = bytearray()
                wakati Kweli:
                    part = os.read(errpipe_read, 50000)
                    errpipe_data += part
                    ikiwa sio part ama len(errpipe_data) > 50000:
                        koma
            mwishowe:
                # be sure the FD ni closed no matter what
                os.close(errpipe_read)

            ikiwa errpipe_data:
                jaribu:
                    pid, sts = os.waitpid(self.pid, 0)
                    ikiwa pid == self.pid:
                        self._handle_exitstatus(sts)
                    isipokua:
                        self.returncode = sys.maxsize
                tatizo ChildProcessError:
                    pita

                jaribu:
                    exception_name, hex_errno, err_msg = (
                            errpipe_data.split(b':', 2))
                    # The encoding here should match the encoding
                    # written kwenye by the subprocess implementations
                    # like _posixsubprocess
                    err_msg = err_msg.decode()
                tatizo ValueError:
                    exception_name = b'SubprocessError'
                    hex_errno = b'0'
                    err_msg = 'Bad exception data kutoka child: {!r}'.format(
                                  bytes(errpipe_data))
                child_exception_type = getattr(
                        builtins, exception_name.decode('ascii'),
                        SubprocessError)
                ikiwa issubclass(child_exception_type, OSError) na hex_errno:
                    errno_num = int(hex_errno, 16)
                    child_exec_never_called = (err_msg == "noexec")
                    ikiwa child_exec_never_called:
                        err_msg = ""
                        # The error must be kutoka chdir(cwd).
                        err_filename = cwd
                    isipokua:
                        err_filename = orig_executable
                    ikiwa errno_num != 0:
                        err_msg = os.strerror(errno_num)
                    ashiria child_exception_type(errno_num, err_msg, err_filename)
                ashiria child_exception_type(err_msg)


        eleza _handle_exitstatus(self, sts, _WIFSIGNALED=os.WIFSIGNALED,
                _WTERMSIG=os.WTERMSIG, _WIFEXITED=os.WIFEXITED,
                _WEXITSTATUS=os.WEXITSTATUS, _WIFSTOPPED=os.WIFSTOPPED,
                _WSTOPSIG=os.WSTOPSIG):
            """All callers to this function MUST hold self._waitpid_lock."""
            # This method ni called (indirectly) by __del__, so it cannot
            # refer to anything outside of its local scope.
            ikiwa _WIFSIGNALED(sts):
                self.returncode = -_WTERMSIG(sts)
            lasivyo _WIFEXITED(sts):
                self.returncode = _WEXITSTATUS(sts)
            lasivyo _WIFSTOPPED(sts):
                self.returncode = -_WSTOPSIG(sts)
            isipokua:
                # Should never happen
                ashiria SubprocessError("Unknown child exit status!")


        eleza _internal_poll(self, _deadstate=Tupu, _waitpid=os.waitpid,
                _WNOHANG=os.WNOHANG, _ECHILD=errno.ECHILD):
            """Check ikiwa child process has terminated.  Returns returncode
            attribute.

            This method ni called by __del__, so it cansio reference anything
            outside of the local scope (nor can any methods it calls).

            """
            ikiwa self.returncode ni Tupu:
                ikiwa sio self._waitpid_lock.acquire(Uongo):
                    # Something isipokua ni busy calling waitpid.  Don't allow two
                    # at once.  We know nothing yet.
                    rudisha Tupu
                jaribu:
                    ikiwa self.returncode ni sio Tupu:
                        rudisha self.returncode  # Another thread waited.
                    pid, sts = _waitpid(self.pid, _WNOHANG)
                    ikiwa pid == self.pid:
                        self._handle_exitstatus(sts)
                tatizo OSError kama e:
                    ikiwa _deadstate ni sio Tupu:
                        self.returncode = _deadstate
                    lasivyo e.errno == _ECHILD:
                        # This happens ikiwa SIGCLD ni set to be ignored ama
                        # waiting kila child processes has otherwise been
                        # disabled kila our process.  This child ni dead, we
                        # can't get the status.
                        # http://bugs.python.org/issue15756
                        self.returncode = 0
                mwishowe:
                    self._waitpid_lock.release()
            rudisha self.returncode


        eleza _try_wait(self, wait_flags):
            """All callers to this function MUST hold self._waitpid_lock."""
            jaribu:
                (pid, sts) = os.waitpid(self.pid, wait_flags)
            tatizo ChildProcessError:
                # This happens ikiwa SIGCLD ni set to be ignored ama waiting
                # kila child processes has otherwise been disabled kila our
                # process.  This child ni dead, we can't get the status.
                pid = self.pid
                sts = 0
            rudisha (pid, sts)


        eleza _wait(self, timeout):
            """Internal implementation of wait() on POSIX."""
            ikiwa self.returncode ni sio Tupu:
                rudisha self.returncode

            ikiwa timeout ni sio Tupu:
                endtime = _time() + timeout
                # Enter a busy loop ikiwa we have a timeout.  This busy loop was
                # cribbed kutoka Lib/threading.py kwenye Thread.wait() at r71065.
                delay = 0.0005 # 500 us -> initial delay of 1 ms
                wakati Kweli:
                    ikiwa self._waitpid_lock.acquire(Uongo):
                        jaribu:
                            ikiwa self.returncode ni sio Tupu:
                                koma  # Another thread waited.
                            (pid, sts) = self._try_wait(os.WNOHANG)
                            assert pid == self.pid ama pid == 0
                            ikiwa pid == self.pid:
                                self._handle_exitstatus(sts)
                                koma
                        mwishowe:
                            self._waitpid_lock.release()
                    remaining = self._remaining_time(endtime)
                    ikiwa remaining <= 0:
                        ashiria TimeoutExpired(self.args, timeout)
                    delay = min(delay * 2, remaining, .05)
                    time.sleep(delay)
            isipokua:
                wakati self.returncode ni Tupu:
                    ukijumuisha self._waitpid_lock:
                        ikiwa self.returncode ni sio Tupu:
                            koma  # Another thread waited.
                        (pid, sts) = self._try_wait(0)
                        # Check the pid na loop kama waitpid has been known to
                        # rudisha 0 even without WNOHANG kwenye odd situations.
                        # http://bugs.python.org/issue14396.
                        ikiwa pid == self.pid:
                            self._handle_exitstatus(sts)
            rudisha self.returncode


        eleza _communicate(self, input, endtime, orig_timeout):
            ikiwa self.stdin na sio self._communication_started:
                # Flush stdio buffer.  This might block, ikiwa the user has
                # been writing to .stdin kwenye an uncontrolled fashion.
                jaribu:
                    self.stdin.flush()
                tatizo BrokenPipeError:
                    pita  # communicate() must ignore BrokenPipeError.
                ikiwa sio inut:
                    jaribu:
                        self.stdin.close()
                    tatizo BrokenPipeError:
                        pita  # communicate() must ignore BrokenPipeError.

            stdout = Tupu
            stderr = Tupu

            # Only create this mapping ikiwa we haven't already.
            ikiwa sio self._communication_started:
                self._fileobj2output = {}
                ikiwa self.stdout:
                    self._fileobj2output[self.stdout] = []
                ikiwa self.stderr:
                    self._fileobj2output[self.stderr] = []

            ikiwa self.stdout:
                stdout = self._fileobj2output[self.stdout]
            ikiwa self.stderr:
                stderr = self._fileobj2output[self.stderr]

            self._save_uliza(input)

            ikiwa self._input:
                input_view = memoryview(self._input)

            ukijumuisha _PopenSelector() kama selector:
                ikiwa self.stdin na input:
                    selector.register(self.stdin, selectors.EVENT_WRITE)
                ikiwa self.stdout:
                    selector.register(self.stdout, selectors.EVENT_READ)
                ikiwa self.stderr:
                    selector.register(self.stderr, selectors.EVENT_READ)

                wakati selector.get_map():
                    timeout = self._remaining_time(endtime)
                    ikiwa timeout ni sio Tupu na timeout < 0:
                        self._check_timeout(endtime, orig_timeout,
                                            stdout, stderr,
                                            skip_check_and_raise=Kweli)
                        ashiria RuntimeError(  # Impossible :)
                            '_check_timeout(..., skip_check_and_raise=Kweli) '
                            'failed to ashiria TimeoutExpired.')

                    ready = selector.select(timeout)
                    self._check_timeout(endtime, orig_timeout, stdout, stderr)

                    # XXX Rewrite these to use non-blocking I/O on the file
                    # objects; they are no longer using C stdio!

                    kila key, events kwenye ready:
                        ikiwa key.fileobj ni self.stdin:
                            chunk = input_view[self._input_offset :
                                               self._input_offset + _PIPE_BUF]
                            jaribu:
                                self._input_offset += os.write(key.fd, chunk)
                            tatizo BrokenPipeError:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            isipokua:
                                ikiwa self._input_offset >= len(self._input):
                                    selector.unregister(key.fileobj)
                                    key.fileobj.close()
                        lasivyo key.fileobj kwenye (self.stdout, self.stderr):
                            data = os.read(key.fd, 32768)
                            ikiwa sio data:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            self._fileobj2output[key.fileobj].append(data)

            self.wait(timeout=self._remaining_time(endtime))

            # All data exchanged.  Translate lists into strings.
            ikiwa stdout ni sio Tupu:
                stdout = b''.join(stdout)
            ikiwa stderr ni sio Tupu:
                stderr = b''.join(stderr)

            # Translate newlines, ikiwa requested.
            # This also turns bytes into strings.
            ikiwa self.text_mode:
                ikiwa stdout ni sio Tupu:
                    stdout = self._translate_newlines(stdout,
                                                      self.stdout.encoding,
                                                      self.stdout.errors)
                ikiwa stderr ni sio Tupu:
                    stderr = self._translate_newlines(stderr,
                                                      self.stderr.encoding,
                                                      self.stderr.errors)

            rudisha (stdout, stderr)


        eleza _save_uliza(self, input):
            # This method ni called kutoka the _communicate_with_*() methods
            # so that ikiwa we time out wakati communicating, we can endelea
            # sending input ikiwa we retry.
            ikiwa self.stdin na self._input ni Tupu:
                self._input_offset = 0
                self._input = input
                ikiwa input ni sio Tupu na self.text_mode:
                    self._input = self._input.encode(self.stdin.encoding,
                                                     self.stdin.errors)


        eleza send_signal(self, sig):
            """Send a signal to the process."""
            # Skip signalling a process that we know has already died.
            ikiwa self.returncode ni Tupu:
                os.kill(self.pid, sig)

        eleza terminate(self):
            """Terminate the process ukijumuisha SIGTERM
            """
            self.send_signal(signal.SIGTERM)

        eleza kill(self):
            """Kill the process ukijumuisha SIGKILL
            """
            self.send_signal(signal.SIGKILL)
