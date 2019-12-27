# subprocess - Subprocesses with accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>
#
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/2.4/license for licensing details.

r"""Subprocesses with accessible I/O streams

This module allows you to spawn processes, connect to their
input/output/error pipes, and obtain their rudisha codes.

For a complete description of this module see the Python documentation.

Main API
========
run(...): Runs a command, waits for it to complete, then returns a
          CompletedProcess instance.
Popen(...): A kundi for flexibly executing a command in a new process

Constants
---------
DEVNULL: Special value that indicates that os.devnull should be used
PIPE:    Special value that indicates a pipe should be created
STDOUT:  Special value that indicates that stderr should go to stdout


Older API
=========
call(...): Runs a command, waits for it to complete, then returns
    the rudisha code.
check_call(...): Same as call() but raises CalledProcessError()
    ikiwa rudisha code is not 0
check_output(...): Same as check_call() but returns the contents of
    stdout instead of a rudisha code
getoutput(...): Runs a command in the shell, waits for it to complete,
    then returns the output
getstatusoutput(...): Runs a command in the shell, waits for it to complete,
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
kutoka time agiza monotonic as _time


__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call", "getstatusoutput",
           "getoutput", "check_output", "run", "CalledProcessError", "DEVNULL",
           "SubprocessError", "TimeoutExpired", "CompletedProcess"]
           # NOTE: We intentionally exclude list2cmdline as it is
           # considered an internal implementation detail.  issue10838.

try:
    agiza msvcrt
    agiza _winapi
    _mswindows = True
except ModuleNotFoundError:
    _mswindows = False
    agiza _posixsubprocess
    agiza select
    agiza selectors
else:
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
kundi SubprocessError(Exception): pass


kundi CalledProcessError(SubprocessError):
    """Raised when run() is called with check=True and the process
    returns a non-zero exit status.

    Attributes:
      cmd, returncode, stdout, stderr, output
    """
    eleza __init__(self, returncode, cmd, output=None, stderr=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr

    eleza __str__(self):
        ikiwa self.returncode and self.returncode < 0:
            try:
                rudisha "Command '%s' died with %r." % (
                        self.cmd, signal.Signals(-self.returncode))
            except ValueError:
                rudisha "Command '%s' died with unknown signal %d." % (
                        self.cmd, -self.returncode)
        else:
            rudisha "Command '%s' returned non-zero exit status %d." % (
                    self.cmd, self.returncode)

    @property
    eleza stdout(self):
        """Alias for output attribute, to match stderr"""
        rudisha self.output

    @stdout.setter
    eleza stdout(self, value):
        # There's no obvious reason to set this, but allow it anyway so
        # .stdout is a transparent alias for .output
        self.output = value


kundi TimeoutExpired(SubprocessError):
    """This exception is raised when the timeout expires while waiting for a
    child process.

    Attributes:
        cmd, output, stdout, stderr, timeout
    """
    eleza __init__(self, cmd, timeout, output=None, stderr=None):
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
        # .stdout is a transparent alias for .output
        self.output = value


ikiwa _mswindows:
    kundi STARTUPINFO:
        eleza __init__(self, *, dwFlags=0, hStdInput=None, hStdOutput=None,
                     hStdError=None, wShowWindow=0, lpAttributeList=None):
            self.dwFlags = dwFlags
            self.hStdInput = hStdInput
            self.hStdOutput = hStdOutput
            self.hStdError = hStdError
            self.wShowWindow = wShowWindow
            self.lpAttributeList = lpAttributeList or {"handle_list": []}

        eleza copy(self):
            attr_list = self.lpAttributeList.copy()
            ikiwa 'handle_list' in attr_list:
                attr_list['handle_list'] = list(attr_list['handle_list'])

            rudisha STARTUPINFO(dwFlags=self.dwFlags,
                               hStdInput=self.hStdInput,
                               hStdOutput=self.hStdOutput,
                               hStdError=self.hStdError,
                               wShowWindow=self.wShowWindow,
                               lpAttributeList=attr_list)


    kundi Handle(int):
        closed = False

        eleza Close(self, CloseHandle=_winapi.CloseHandle):
            ikiwa not self.closed:
                self.closed = True
                CloseHandle(self)

        eleza Detach(self):
            ikiwa not self.closed:
                self.closed = True
                rudisha int(self)
            raise ValueError("already closed")

        eleza __repr__(self):
            rudisha "%s(%d)" % (self.__class__.__name__, int(self))

        __del__ = Close
else:
    # When select or poll has indicated that the file is writable,
    # we can write up to _PIPE_BUF bytes without risk of blocking.
    # POSIX defines PIPE_BUF as >= 512.
    _PIPE_BUF = getattr(select, 'PIPE_BUF', 512)

    # poll/select have the advantage of not requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    ikiwa hasattr(selectors, 'PollSelector'):
        _PopenSelector = selectors.PollSelector
    else:
        _PopenSelector = selectors.SelectSelector


ikiwa _mswindows:
    # On Windows we just need to close `Popen._handle` when we no longer need
    # it, so that the kernel can free it. `Popen._handle` gets closed
    # implicitly when the `Popen` instance is finalized (see `Handle.__del__`,
    # which is calling `CloseHandle` as requested in [1]), so there is nothing
    # for `_cleanup` to do.
    #
    # [1] https://docs.microsoft.com/en-us/windows/desktop/ProcThread/
    # creating-processes
    _active = None

    eleza _cleanup():
        pass
else:
    # This lists holds Popen instances for which the underlying process had not
    # exited at the time its __del__ method got called: those processes are
    # wait()ed for synchronously kutoka _cleanup() when a new Popen object is
    # created, to avoid zombie processes.
    _active = []

    eleza _cleanup():
        ikiwa _active is None:
            return
        for inst in _active[:]:
            res = inst._internal_poll(_deadstate=sys.maxsize)
            ikiwa res is not None:
                try:
                    _active.remove(inst)
                except ValueError:
                    # This can happen ikiwa two threads create a new Popen instance.
                    # It's harmless that it was already removed, so ignore.
                    pass

PIPE = -1
STDOUT = -2
DEVNULL = -3


# XXX This function is only used by multiprocessing and the test suite,
# but it's here so that it can be imported when Python is compiled without
# threads.

eleza _optim_args_kutoka_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    optimization settings in sys.flags."""
    args = []
    value = sys.flags.optimize
    ikiwa value > 0:
        args.append('-' + 'O' * value)
    rudisha args


eleza _args_kutoka_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    settings in sys.flags, sys.warnoptions and sys._xoptions."""
    flag_opt_map = {
        'debug': 'd',
        # 'inspect': 'i',
        # 'interactive': 'i',
        'dont_write_bytecode': 'B',
        'no_site': 'S',
        'verbose': 'v',
        'bytes_warning': 'b',
        'quiet': 'q',
        # -O is handled in _optim_args_kutoka_interpreter_flags()
    }
    args = _optim_args_kutoka_interpreter_flags()
    for flag, opt in flag_opt_map.items():
        v = getattr(sys.flags, flag)
        ikiwa v > 0:
            args.append('-' + opt * v)

    ikiwa sys.flags.isolated:
        args.append('-I')
    else:
        ikiwa sys.flags.ignore_environment:
            args.append('-E')
        ikiwa sys.flags.no_user_site:
            args.append('-s')

    # -W options
    warnopts = sys.warnoptions[:]
    bytes_warning = sys.flags.bytes_warning
    xoptions = getattr(sys, '_xoptions', {})
    dev_mode = ('dev' in xoptions)

    ikiwa bytes_warning > 1:
        warnopts.remove("error::BytesWarning")
    elikiwa bytes_warning:
        warnopts.remove("default::BytesWarning")
    ikiwa dev_mode:
        warnopts.remove('default')
    for opt in warnopts:
        args.append('-W' + opt)

    # -X options
    ikiwa dev_mode:
        args.extend(('-X', 'dev'))
    for opt in ('faulthandler', 'tracemalloc', 'agizatime',
                'showalloccount', 'showrefcount', 'utf8'):
        ikiwa opt in xoptions:
            value = xoptions[opt]
            ikiwa value is True:
                arg = opt
            else:
                arg = '%s=%s' % (opt, value)
            args.extend(('-X', arg))

    rudisha args


eleza call(*popenargs, timeout=None, **kwargs):
    """Run command with arguments.  Wait for command to complete or
    timeout, then rudisha the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    with Popen(*popenargs, **kwargs) as p:
        try:
            rudisha p.wait(timeout=timeout)
        except:  # Including KeyboardInterrupt, wait handled that.
            p.kill()
            # We don't call p.wait() again as p.__exit__ does that for us.
            raise


eleza check_call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete.  If
    the exit code was zero then return, otherwise raise
    CalledProcessError.  The CalledProcessError object will have the
    rudisha code in the returncode attribute.

    The arguments are the same as for the call function.  Example:

    check_call(["ls", "-l"])
    """
    retcode = call(*popenargs, **kwargs)
    ikiwa retcode:
        cmd = kwargs.get("args")
        ikiwa cmd is None:
            cmd = popenargs[0]
        raise CalledProcessError(retcode, cmd)
    rudisha 0


eleza check_output(*popenargs, timeout=None, **kwargs):
    r"""Run command with arguments and rudisha its output.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the rudisha code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    b'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    b'ls: non_existent_file: No such file or directory\n'

    There is an additional optional argument, "input", allowing you to
    pass a string to the subprocess's stdin.  If you use this argument
    you may not also use the Popen constructor's "stdin" argument, as
    it too will be used internally.  Example:

    >>> check_output(["sed", "-e", "s/foo/bar/"],
    ...              input=b"when in the course of fooman events\n")
    b'when in the course of barman events\n'

    By default, all communication is in bytes, and therefore any "input"
    should be bytes, and the rudisha value will be bytes.  If in text mode,
    any "input" should be a string, and the rudisha value will be a string
    decoded according to locale encoding, or by "encoding" ikiwa set. Text mode
    is triggered by setting any of text, encoding, errors or universal_newlines.
    """
    ikiwa 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')

    ikiwa 'input' in kwargs and kwargs['input'] is None:
        # Explicitly passing input=None was previously equivalent to passing an
        # empty string. That is maintained here for backwards compatibility.
        kwargs['input'] = '' ikiwa kwargs.get('universal_newlines', False) else b''

    rudisha run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
               **kwargs).stdout


kundi CompletedProcess(object):
    """A process that has finished running.

    This is returned by run().

    Attributes:
      args: The list or str args passed to run().
      returncode: The exit code of the process, negative for signals.
      stdout: The standard output (None ikiwa not captured).
      stderr: The standard error (None ikiwa not captured).
    """
    eleza __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    eleza __repr__(self):
        args = ['args={!r}'.format(self.args),
                'returncode={!r}'.format(self.returncode)]
        ikiwa self.stdout is not None:
            args.append('stdout={!r}'.format(self.stdout))
        ikiwa self.stderr is not None:
            args.append('stderr={!r}'.format(self.stderr))
        rudisha "{}({})".format(type(self).__name__, ', '.join(args))

    eleza check_returncode(self):
        """Raise CalledProcessError ikiwa the exit code is non-zero."""
        ikiwa self.returncode:
            raise CalledProcessError(self.returncode, self.args, self.stdout,
                                     self.stderr)


eleza run(*popenargs,
        input=None, capture_output=False, timeout=None, check=False, **kwargs):
    """Run command with arguments and rudisha a CompletedProcess instance.

    The returned instance will have attributes args, returncode, stdout and
    stderr. By default, stdout and stderr are not captured, and those attributes
    will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.

    If check is True and the exit code was non-zero, it raises a
    CalledProcessError. The CalledProcessError object will have the rudisha code
    in the returncode attribute, and output & stderr attributes ikiwa those streams
    were captured.

    If timeout is given, and the process takes too long, a TimeoutExpired
    exception will be raised.

    There is an optional argument "input", allowing you to
    pass bytes or a string to the subprocess's stdin.  If you use this argument
    you may not also use the Popen constructor's "stdin" argument, as
    it will be used internally.

    By default, all communication is in bytes, and therefore any "input" should
    be bytes, and the stdout and stderr will be bytes. If in text mode, any
    "input" should be a string, and stdout and stderr will be strings decoded
    according to locale encoding, or by "encoding" ikiwa set. Text mode is
    triggered by setting any of text, encoding, errors or universal_newlines.

    The other arguments are the same as for the Popen constructor.
    """
    ikiwa input is not None:
        ikiwa kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = PIPE

    ikiwa capture_output:
        ikiwa kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError('stdout and stderr arguments may not be used '
                             'with capture_output.')
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE

    with Popen(*popenargs, **kwargs) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except TimeoutExpired as exc:
            process.kill()
            ikiwa _mswindows:
                # Windows accumulates the output in a single blocking
                # read() call run on child threads, with the timeout
                # being done in a join() on those threads.  communicate()
                # _after_ kill() is required to collect that and add it
                # to the exception.
                exc.stdout, exc.stderr = process.communicate()
            else:
                # POSIX _communicate already populated the output so
                # far into the TimeoutExpired exception.
                process.wait()
            raise
        except:  # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            raise
        retcode = process.poll()
        ikiwa check and retcode:
            raise CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    rudisha CompletedProcess(process.args, retcode, stdout, stderr)


eleza list2cmdline(seq):
    """
    Translate a sequence of arguments into a command line
    string, using the same rules as the MS C runtime:

    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.
    """

    # See
    # http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    # or search http://msdn.microsoft.com for
    # "Parsing C++ Command-Line Arguments"
    result = []
    needquote = False
    for arg in map(os.fsdecode, seq):
        bs_buf = []

        # Add a space to separate this argument kutoka the others
        ikiwa result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        ikiwa needquote:
            result.append('"')

        for c in arg:
            ikiwa c == '\\':
                # Don't know ikiwa we need to double yet.
                bs_buf.append(c)
            elikiwa c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
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


# Various tools for executing commands and looking at their output and status.
#

eleza getstatusoutput(cmd):
    """Return (exitcode, output) of executing cmd in a shell.

    Execute the string 'cmd' in a shell with 'check_output' and
    rudisha a 2-tuple (status, output). The locale encoding is used
    to decode the output and process newlines.

    A trailing newline is stripped kutoka the output.
    The exit status for the command can be interpreted
    according to the rules for the function 'wait'. Example:

    >>> agiza subprocess
    >>> subprocess.getstatusoutput('ls /bin/ls')
    (0, '/bin/ls')
    >>> subprocess.getstatusoutput('cat /bin/junk')
    (1, 'cat: /bin/junk: No such file or directory')
    >>> subprocess.getstatusoutput('/bin/junk')
    (127, 'sh: /bin/junk: not found')
    >>> subprocess.getstatusoutput('/bin/kill $$')
    (-15, '')
    """
    try:
        data = check_output(cmd, shell=True, text=True, stderr=STDOUT)
        exitcode = 0
    except CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    ikiwa data[-1:] == '\n':
        data = data[:-1]
    rudisha exitcode, data

eleza getoutput(cmd):
    """Return output (stdout or stderr) of executing cmd in a shell.

    Like getstatusoutput(), except the exit status is ignored and the return
    value is a string containing the command's output.  Example:

    >>> agiza subprocess
    >>> subprocess.getoutput('ls /bin/ls')
    '/bin/ls'
    """
    rudisha getstatusoutput(cmd)[1]


eleza _use_posix_spawn():
    """Check ikiwa posix_spawn() can be used for subprocess.

    subprocess requires a posix_spawn() implementation that properly reports
    errors to the parent process, & sets errno on the following failures:

    * Process attribute actions failed.
    * File actions failed.
    * exec() failed.

    Prefer an implementation which can use vfork() in some cases for best
    performance.
    """
    ikiwa _mswindows or not hasattr(os, 'posix_spawn'):
        # os.posix_spawn() is not available
        rudisha False

    ikiwa sys.platform == 'darwin':
        # posix_spawn() is a syscall on macOS and properly reports errors
        rudisha True

    # Check libc name and runtime libc version
    try:
        ver = os.confstr('CS_GNU_LIBC_VERSION')
        # parse 'glibc 2.28' as ('glibc', (2, 28))
        parts = ver.split(maxsplit=1)
        ikiwa len(parts) != 2:
            # reject unknown format
            raise ValueError
        libc = parts[0]
        version = tuple(map(int, parts[1].split('.')))

        ikiwa sys.platform == 'linux' and libc == 'glibc' and version >= (2, 24):
            # glibc 2.24 has a new Linux posix_spawn implementation using vfork
            # which properly reports errors to the parent process.
            rudisha True
        # Note: Don't use the implementation in earlier glibc because it doesn't
        # use vfork (even ikiwa glibc 2.26 added a pipe to properly report errors
        # to the parent process).
    except (AttributeError, ValueError, OSError):
        # os.confstr() or CS_GNU_LIBC_VERSION value not available
        pass

    # By default, assume that posix_spawn() does not properly report errors.
    rudisha False


_USE_POSIX_SPAWN = _use_posix_spawn()


kundi Popen(object):
    """ Execute a child program in a new process.

    For a complete description of the arguments see the Python documentation.

    Arguments:
      args: A string, or a sequence of program arguments.

      bufsize: supplied as the buffering argument to the open() function when
          creating the stdin/stdout/stderr pipe file objects

      executable: A replacement program to execute.

      stdin, stdout and stderr: These specify the executed programs' standard
          input, standard output and standard error file handles, respectively.

      preexec_fn: (POSIX only) An object to be called in the child process
          just before the child is executed.

      close_fds: Controls closing or inheriting of file descriptors.

      shell: If true, the command will be executed through the shell.

      cwd: Sets the current directory before the child is executed.

      env: Defines the environment variables for the new process.

      text: If true, decode stdin, stdout and stderr using the given encoding
          (ikiwa set) or the system default otherwise.

      universal_newlines: Alias of text, provided for backwards compatibility.

      startupinfo and creationflags (Windows only)

      restore_signals (POSIX only)

      start_new_session (POSIX only)

      pass_fds (POSIX only)

      encoding and errors: Text mode encoding and error handling to use for
          file objects stdin, stdout and stderr.

    Attributes:
        stdin, stdout, stderr, pid, returncode
    """
    _child_created = False  # Set here since __del__ checks it

    eleza __init__(self, args, bufsize=-1, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=True,
                 shell=False, cwd=None, env=None, universal_newlines=None,
                 startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False,
                 pass_fds=(), *, encoding=None, errors=None, text=None):
        """Create new Popen instance."""
        _cleanup()
        # Held while anything is calling waitpid before returncode has been
        # updated to prevent clobbering returncode ikiwa wait() or poll() are
        # called kutoka multiple threads at once.  After acquiring the lock,
        # code must re-check self.returncode to see ikiwa another thread just
        # finished a waitpid() call.
        self._waitpid_lock = threading.Lock()

        self._input = None
        self._communication_started = False
        ikiwa bufsize is None:
            bufsize = -1  # Restore default
        ikiwa not isinstance(bufsize, int):
            raise TypeError("bufsize must be an integer")

        ikiwa _mswindows:
            ikiwa preexec_fn is not None:
                raise ValueError("preexec_fn is not supported on Windows "
                                 "platforms")
        else:
            # POSIX
            ikiwa pass_fds and not close_fds:
                warnings.warn("pass_fds overriding close_fds.", RuntimeWarning)
                close_fds = True
            ikiwa startupinfo is not None:
                raise ValueError("startupinfo is only supported on Windows "
                                 "platforms")
            ikiwa creationflags != 0:
                raise ValueError("creationflags is only supported on Windows "
                                 "platforms")

        self.args = args
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.encoding = encoding
        self.errors = errors

        # Validate the combinations of text and universal_newlines
        ikiwa (text is not None and universal_newlines is not None
            and bool(universal_newlines) != bool(text)):
            raise SubprocessError('Cannot disambiguate when both text '
                                  'and universal_newlines are supplied but '
                                  'different. Pass one or the other.')

        # Input and output objects. The general principle is like
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
        # are -1 when not using PIPEs. The child objects are -1
        # when not redirecting.

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

        self.text_mode = encoding or errors or text or universal_newlines

        # How long to resume waiting on a child after the first ^C.
        # There is no right value for this.  The purpose is to be polite
        # yet remain good for interactive users trying to exit a tool.
        self._sigint_wait_secs = 0.25  # 1/xkcd221.getRandomNumber()

        self._closed_child_pipe_fds = False

        ikiwa self.text_mode:
            ikiwa bufsize == 1:
                line_buffering = True
                # Use the default buffer size for the underlying binary streams
                # since they don't support line buffering.
                bufsize = -1
            else:
                line_buffering = False

        try:
            ikiwa p2cwrite != -1:
                self.stdin = io.open(p2cwrite, 'wb', bufsize)
                ikiwa self.text_mode:
                    self.stdin = io.TextIOWrapper(self.stdin, write_through=True,
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
                                pass_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                restore_signals, start_new_session)
        except:
            # Cleanup ikiwa the child failed starting.
            for f in filter(None, (self.stdin, self.stdout, self.stderr)):
                try:
                    f.close()
                except OSError:
                    pass  # Ignore EBADF or other errors.

            ikiwa not self._closed_child_pipe_fds:
                to_close = []
                ikiwa stdin == PIPE:
                    to_close.append(p2cread)
                ikiwa stdout == PIPE:
                    to_close.append(c2pwrite)
                ikiwa stderr == PIPE:
                    to_close.append(errwrite)
                ikiwa hasattr(self, '_devnull'):
                    to_close.append(self._devnull)
                for fd in to_close:
                    try:
                        ikiwa _mswindows and isinstance(fd, Handle):
                            fd.Close()
                        else:
                            os.close(fd)
                    except OSError:
                        pass

            raise

    @property
    eleza universal_newlines(self):
        # universal_newlines as retained as an alias of text_mode for API
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
        try:  # Flushing a BufferedWriter may raise an error
            ikiwa self.stdin:
                self.stdin.close()
        finally:
            ikiwa exc_type == KeyboardInterrupt:
                # https://bugs.python.org/issue25942
                # In the case of a KeyboardInterrupt we assume the SIGINT
                # was also already sent to our child processes.  We can't
                # block indefinitely as that is not user friendly.
                # If we have not already waited a brief amount of time in
                # an interrupted .wait() or .communicate() call, do so here
                # for consistency.
                ikiwa self._sigint_wait_secs > 0:
                    try:
                        self._wait(timeout=self._sigint_wait_secs)
                    except TimeoutExpired:
                        pass
                self._sigint_wait_secs = 0  # Note that this has been done.
                rudisha  # resume the KeyboardInterrupt

            # Wait for the process to terminate, to avoid zombies.
            self.wait()

    eleza __del__(self, _maxsize=sys.maxsize, _warn=warnings.warn):
        ikiwa not self._child_created:
            # We didn't get to successfully create a child process.
            return
        ikiwa self.returncode is None:
            # Not reading subprocess exit status creates a zombie process which
            # is only destroyed at the parent python process exit
            _warn("subprocess %s is still running" % self.pid,
                  ResourceWarning, source=self)
        # In case the child hasn't been waited on, check ikiwa it's done.
        self._internal_poll(_deadstate=_maxsize)
        ikiwa self.returncode is None and _active is not None:
            # Child is still running, keep us alive until we can wait on it.
            _active.append(self)

    eleza _get_devnull(self):
        ikiwa not hasattr(self, '_devnull'):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        rudisha self._devnull

    eleza _stdin_write(self, input):
        ikiwa input:
            try:
                self.stdin.write(input)
            except BrokenPipeError:
                pass  # communicate() must ignore broken pipe errors.
            except OSError as exc:
                ikiwa exc.errno == errno.EINVAL:
                    # bpo-19612, bpo-30418: On Windows, stdin.write() fails
                    # with EINVAL ikiwa the child process exited or ikiwa the child
                    # process is still running but closed the pipe.
                    pass
                else:
                    raise

        try:
            self.stdin.close()
        except BrokenPipeError:
            pass  # communicate() must ignore broken pipe errors.
        except OSError as exc:
            ikiwa exc.errno == errno.EINVAL:
                pass
            else:
                raise

    eleza communicate(self, input=None, timeout=None):
        """Interact with process: Send data to stdin and close it.
        Read data kutoka stdout and stderr, until end-of-file is
        reached.  Wait for process to terminate.

        The optional "input" argument should be data to be sent to the
        child process, or None, ikiwa no data should be sent to the child.
        communicate() returns a tuple (stdout, stderr).

        By default, all communication is in bytes, and therefore any
        "input" should be bytes, and the (stdout, stderr) will be bytes.
        If in text mode (indicated by self.text_mode), any "input" should
        be a string, and (stdout, stderr) will be strings decoded
        according to locale encoding, or by "encoding" ikiwa set. Text mode
        is triggered by setting any of text, encoding, errors or
        universal_newlines.
        """

        ikiwa self._communication_started and input:
            raise ValueError("Cannot send input after starting communication")

        # Optimization: If we are not worried about timeouts, we haven't
        # started communicating, and we have one or zero pipes, using select()
        # or threads is unnecessary.
        ikiwa (timeout is None and not self._communication_started and
            [self.stdin, self.stdout, self.stderr].count(None) >= 2):
            stdout = None
            stderr = None
            ikiwa self.stdin:
                self._stdin_write(input)
            elikiwa self.stdout:
                stdout = self.stdout.read()
                self.stdout.close()
            elikiwa self.stderr:
                stderr = self.stderr.read()
                self.stderr.close()
            self.wait()
        else:
            ikiwa timeout is not None:
                endtime = _time() + timeout
            else:
                endtime = None

            try:
                stdout, stderr = self._communicate(input, endtime, timeout)
            except KeyboardInterrupt:
                # https://bugs.python.org/issue25942
                # See the detailed comment in .wait().
                ikiwa timeout is not None:
                    sigint_timeout = min(self._sigint_wait_secs,
                                         self._remaining_time(endtime))
                else:
                    sigint_timeout = self._sigint_wait_secs
                self._sigint_wait_secs = 0  # nothing else should wait.
                try:
                    self._wait(timeout=sigint_timeout)
                except TimeoutExpired:
                    pass
                raise  # resume the KeyboardInterrupt

            finally:
                self._communication_started = True

            sts = self.wait(timeout=self._remaining_time(endtime))

        rudisha (stdout, stderr)


    eleza poll(self):
        """Check ikiwa child process has terminated. Set and rudisha returncode
        attribute."""
        rudisha self._internal_poll()


    eleza _remaining_time(self, endtime):
        """Convenience for _communicate when computing timeouts."""
        ikiwa endtime is None:
            rudisha None
        else:
            rudisha endtime - _time()


    eleza _check_timeout(self, endtime, orig_timeout, stdout_seq, stderr_seq,
                       skip_check_and_raise=False):
        """Convenience for checking ikiwa a timeout has expired."""
        ikiwa endtime is None:
            return
        ikiwa skip_check_and_raise or _time() > endtime:
            raise TimeoutExpired(
                    self.args, orig_timeout,
                    output=b''.join(stdout_seq) ikiwa stdout_seq else None,
                    stderr=b''.join(stderr_seq) ikiwa stderr_seq else None)


    eleza wait(self, timeout=None):
        """Wait for child process to terminate; returns self.returncode."""
        ikiwa timeout is not None:
            endtime = _time() + timeout
        try:
            rudisha self._wait(timeout=timeout)
        except KeyboardInterrupt:
            # https://bugs.python.org/issue25942
            # The first keyboard interrupt waits briefly for the child to
            # exit under the common assumption that it also received the ^C
            # generated SIGINT and will exit rapidly.
            ikiwa timeout is not None:
                sigint_timeout = min(self._sigint_wait_secs,
                                     self._remaining_time(endtime))
            else:
                sigint_timeout = self._sigint_wait_secs
            self._sigint_wait_secs = 0  # nothing else should wait.
            try:
                self._wait(timeout=sigint_timeout)
            except TimeoutExpired:
                pass
            raise  # resume the KeyboardInterrupt

    eleza _close_pipe_fds(self,
                        p2cread, p2cwrite,
                        c2pread, c2pwrite,
                        errread, errwrite):
        # self._devnull is not always defined.
        devnull_fd = getattr(self, '_devnull', None)

        with contextlib.ExitStack() as stack:
            ikiwa _mswindows:
                ikiwa p2cread != -1:
                    stack.callback(p2cread.Close)
                ikiwa c2pwrite != -1:
                    stack.callback(c2pwrite.Close)
                ikiwa errwrite != -1:
                    stack.callback(errwrite.Close)
            else:
                ikiwa p2cread != -1 and p2cwrite != -1 and p2cread != devnull_fd:
                    stack.callback(os.close, p2cread)
                ikiwa c2pwrite != -1 and c2pread != -1 and c2pwrite != devnull_fd:
                    stack.callback(os.close, c2pwrite)
                ikiwa errwrite != -1 and errread != -1 and errwrite != devnull_fd:
                    stack.callback(os.close, errwrite)

            ikiwa devnull_fd is not None:
                stack.callback(os.close, devnull_fd)

        # Prevent a double close of these handles/fds kutoka __init__ on error.
        self._closed_child_pipe_fds = True

    ikiwa _mswindows:
        #
        # Windows methods
        #
        eleza _get_handles(self, stdin, stdout, stderr):
            """Construct and rudisha tuple with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            ikiwa stdin is None and stdout is None and stderr is None:
                rudisha (-1, -1, -1, -1, -1, -1)

            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            ikiwa stdin is None:
                p2cread = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
                ikiwa p2cread is None:
                    p2cread, _ = _winapi.CreatePipe(None, 0)
                    p2cread = Handle(p2cread)
                    _winapi.CloseHandle(_)
            elikiwa stdin == PIPE:
                p2cread, p2cwrite = _winapi.CreatePipe(None, 0)
                p2cread, p2cwrite = Handle(p2cread), Handle(p2cwrite)
            elikiwa stdin == DEVNULL:
                p2cread = msvcrt.get_osfhandle(self._get_devnull())
            elikiwa isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            else:
                # Assuming file-like object
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)

            ikiwa stdout is None:
                c2pwrite = _winapi.GetStdHandle(_winapi.STD_OUTPUT_HANDLE)
                ikiwa c2pwrite is None:
                    _, c2pwrite = _winapi.CreatePipe(None, 0)
                    c2pwrite = Handle(c2pwrite)
                    _winapi.CloseHandle(_)
            elikiwa stdout == PIPE:
                c2pread, c2pwrite = _winapi.CreatePipe(None, 0)
                c2pread, c2pwrite = Handle(c2pread), Handle(c2pwrite)
            elikiwa stdout == DEVNULL:
                c2pwrite = msvcrt.get_osfhandle(self._get_devnull())
            elikiwa isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            else:
                # Assuming file-like object
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)

            ikiwa stderr is None:
                errwrite = _winapi.GetStdHandle(_winapi.STD_ERROR_HANDLE)
                ikiwa errwrite is None:
                    _, errwrite = _winapi.CreatePipe(None, 0)
                    errwrite = Handle(errwrite)
                    _winapi.CloseHandle(_)
            elikiwa stderr == PIPE:
                errread, errwrite = _winapi.CreatePipe(None, 0)
                errread, errwrite = Handle(errread), Handle(errwrite)
            elikiwa stderr == STDOUT:
                errwrite = c2pwrite
            elikiwa stderr == DEVNULL:
                errwrite = msvcrt.get_osfhandle(self._get_devnull())
            elikiwa isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            else:
                # Assuming file-like object
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)

            rudisha (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


        eleza _make_inheritable(self, handle):
            """Return a duplicate of handle, which is inheritable"""
            h = _winapi.DuplicateHandle(
                _winapi.GetCurrentProcess(), handle,
                _winapi.GetCurrentProcess(), 0, 1,
                _winapi.DUPLICATE_SAME_ACCESS)
            rudisha Handle(h)


        eleza _filter_handle_list(self, handle_list):
            """Filter out console handles that can't be used
            in lpAttributeList["handle_list"] and make sure the list
            isn't empty. This also removes duplicate handles."""
            # An handle with it's lowest two bits set might be a special console
            # handle that ikiwa passed in lpAttributeList["handle_list"], will
            # cause it to fail.
            rudisha list({handle for handle in handle_list
                         ikiwa handle & 0x3 != 0x3
                         or _winapi.GetFileType(handle) !=
                            _winapi.FILE_TYPE_CHAR})


        eleza _execute_child(self, args, executable, preexec_fn, close_fds,
                           pass_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           unused_restore_signals, unused_start_new_session):
            """Execute program (MS Windows version)"""

            assert not pass_fds, "pass_fds not supported on Windows."

            ikiwa isinstance(args, str):
                pass
            elikiwa isinstance(args, bytes):
                ikiwa shell:
                    raise TypeError('bytes args is not allowed on Windows')
                args = list2cmdline([args])
            elikiwa isinstance(args, os.PathLike):
                ikiwa shell:
                    raise TypeError('path-like args is not allowed when '
                                    'shell is true')
                args = list2cmdline([args])
            else:
                args = list2cmdline(args)

            ikiwa executable is not None:
                executable = os.fsdecode(executable)

            # Process startup details
            ikiwa startupinfo is None:
                startupinfo = STARTUPINFO()
            else:
                # bpo-34044: Copy STARTUPINFO since it is modified above,
                # so the caller can reuse it multiple times.
                startupinfo = startupinfo.copy()

            use_std_handles = -1 not in (p2cread, c2pwrite, errwrite)
            ikiwa use_std_handles:
                startupinfo.dwFlags |= _winapi.STARTF_USESTDHANDLES
                startupinfo.hStdInput = p2cread
                startupinfo.hStdOutput = c2pwrite
                startupinfo.hStdError = errwrite

            attribute_list = startupinfo.lpAttributeList
            have_handle_list = bool(attribute_list and
                                    "handle_list" in attribute_list and
                                    attribute_list["handle_list"])

            # If we were given an handle_list or need to create one
            ikiwa have_handle_list or (use_std_handles and close_fds):
                ikiwa attribute_list is None:
                    attribute_list = startupinfo.lpAttributeList = {}
                handle_list = attribute_list["handle_list"] = \
                    list(attribute_list.get("handle_list", []))

                ikiwa use_std_handles:
                    handle_list += [int(p2cread), int(c2pwrite), int(errwrite)]

                handle_list[:] = self._filter_handle_list(handle_list)

                ikiwa handle_list:
                    ikiwa not close_fds:
                        warnings.warn("startupinfo.lpAttributeList['handle_list'] "
                                      "overriding close_fds", RuntimeWarning)

                    # When using the handle_list we always request to inherit
                    # handles but the only handles that will be inherited are
                    # the ones in the handle_list
                    close_fds = False

            ikiwa shell:
                startupinfo.dwFlags |= _winapi.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = _winapi.SW_HIDE
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                args = '{} /c "{}"'.format (comspec, args)

            ikiwa cwd is not None:
                cwd = os.fsdecode(cwd)

            sys.audit("subprocess.Popen", executable, args, cwd, env)

            # Start the process
            try:
                hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                                         # no special security
                                         None, None,
                                         int(not close_fds),
                                         creationflags,
                                         env,
                                         cwd,
                                         startupinfo)
            finally:
                # Child is launched. Close the parent's copy of those pipe
                # handles that only the child should have open.  You need
                # to make sure that no handles to the write end of the
                # output pipe are maintained in this process or else the
                # pipe will not close when the child process exits and the
                # ReadFile will hang.
                self._close_pipe_fds(p2cread, p2cwrite,
                                     c2pread, c2pwrite,
                                     errread, errwrite)

            # Retain the process handle, but close the thread handle
            self._child_created = True
            self._handle = Handle(hp)
            self.pid = pid
            _winapi.CloseHandle(ht)

        eleza _internal_poll(self, _deadstate=None,
                _WaitForSingleObject=_winapi.WaitForSingleObject,
                _WAIT_OBJECT_0=_winapi.WAIT_OBJECT_0,
                _GetExitCodeProcess=_winapi.GetExitCodeProcess):
            """Check ikiwa child process has terminated.  Returns returncode
            attribute.

            This method is called by __del__, so it can only refer to objects
            in its local scope.

            """
            ikiwa self.returncode is None:
                ikiwa _WaitForSingleObject(self._handle, 0) == _WAIT_OBJECT_0:
                    self.returncode = _GetExitCodeProcess(self._handle)
            rudisha self.returncode


        eleza _wait(self, timeout):
            """Internal implementation of wait() on Windows."""
            ikiwa timeout is None:
                timeout_millis = _winapi.INFINITE
            else:
                timeout_millis = int(timeout * 1000)
            ikiwa self.returncode is None:
                # API note: Returns immediately ikiwa timeout_millis == 0.
                result = _winapi.WaitForSingleObject(self._handle,
                                                     timeout_millis)
                ikiwa result == _winapi.WAIT_TIMEOUT:
                    raise TimeoutExpired(self.args, timeout)
                self.returncode = _winapi.GetExitCodeProcess(self._handle)
            rudisha self.returncode


        eleza _readerthread(self, fh, buffer):
            buffer.append(fh.read())
            fh.close()


        eleza _communicate(self, input, endtime, orig_timeout):
            # Start reader threads feeding into a list hanging off of this
            # object, unless they've already been started.
            ikiwa self.stdout and not hasattr(self, "_stdout_buff"):
                self._stdout_buff = []
                self.stdout_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stdout, self._stdout_buff))
                self.stdout_thread.daemon = True
                self.stdout_thread.start()
            ikiwa self.stderr and not hasattr(self, "_stderr_buff"):
                self._stderr_buff = []
                self.stderr_thread = \
                        threading.Thread(target=self._readerthread,
                                         args=(self.stderr, self._stderr_buff))
                self.stderr_thread.daemon = True
                self.stderr_thread.start()

            ikiwa self.stdin:
                self._stdin_write(input)

            # Wait for the reader threads, or time out.  If we time out, the
            # threads remain reading and the fds left open in case the user
            # calls communicate again.
            ikiwa self.stdout is not None:
                self.stdout_thread.join(self._remaining_time(endtime))
                ikiwa self.stdout_thread.is_alive():
                    raise TimeoutExpired(self.args, orig_timeout)
            ikiwa self.stderr is not None:
                self.stderr_thread.join(self._remaining_time(endtime))
                ikiwa self.stderr_thread.is_alive():
                    raise TimeoutExpired(self.args, orig_timeout)

            # Collect the output kutoka and close both pipes, now that we know
            # both have been read successfully.
            stdout = None
            stderr = None
            ikiwa self.stdout:
                stdout = self._stdout_buff
                self.stdout.close()
            ikiwa self.stderr:
                stderr = self._stderr_buff
                self.stderr.close()

            # All data exchanged.  Translate lists into strings.
            ikiwa stdout is not None:
                stdout = stdout[0]
            ikiwa stderr is not None:
                stderr = stderr[0]

            rudisha (stdout, stderr)

        eleza send_signal(self, sig):
            """Send a signal to the process."""
            # Don't signal a process that we know has already died.
            ikiwa self.returncode is not None:
                return
            ikiwa sig == signal.SIGTERM:
                self.terminate()
            elikiwa sig == signal.CTRL_C_EVENT:
                os.kill(self.pid, signal.CTRL_C_EVENT)
            elikiwa sig == signal.CTRL_BREAK_EVENT:
                os.kill(self.pid, signal.CTRL_BREAK_EVENT)
            else:
                raise ValueError("Unsupported signal: {}".format(sig))

        eleza terminate(self):
            """Terminates the process."""
            # Don't terminate a process that we know has already died.
            ikiwa self.returncode is not None:
                return
            try:
                _winapi.TerminateProcess(self._handle, 1)
            except PermissionError:
                # ERROR_ACCESS_DENIED (winerror 5) is received when the
                # process already died.
                rc = _winapi.GetExitCodeProcess(self._handle)
                ikiwa rc == _winapi.STILL_ACTIVE:
                    raise
                self.returncode = rc

        kill = terminate

    else:
        #
        # POSIX methods
        #
        eleza _get_handles(self, stdin, stdout, stderr):
            """Construct and rudisha tuple with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            ikiwa stdin is None:
                pass
            elikiwa stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            elikiwa stdin == DEVNULL:
                p2cread = self._get_devnull()
            elikiwa isinstance(stdin, int):
                p2cread = stdin
            else:
                # Assuming file-like object
                p2cread = stdin.fileno()

            ikiwa stdout is None:
                pass
            elikiwa stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            elikiwa stdout == DEVNULL:
                c2pwrite = self._get_devnull()
            elikiwa isinstance(stdout, int):
                c2pwrite = stdout
            else:
                # Assuming file-like object
                c2pwrite = stdout.fileno()

            ikiwa stderr is None:
                pass
            elikiwa stderr == PIPE:
                errread, errwrite = os.pipe()
            elikiwa stderr == STDOUT:
                ikiwa c2pwrite != -1:
                    errwrite = c2pwrite
                else: # child's stdout is not set, use parent's stdout
                    errwrite = sys.__stdout__.fileno()
            elikiwa stderr == DEVNULL:
                errwrite = self._get_devnull()
            elikiwa isinstance(stderr, int):
                errwrite = stderr
            else:
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
            ikiwa env is None:
                env = os.environ

            kwargs = {}
            ikiwa restore_signals:
                # See _Py_RestoreSignals() in Python/pylifecycle.c
                sigset = []
                for signame in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                    signum = getattr(signal, signame, None)
                    ikiwa signum is not None:
                        sigset.append(signum)
                kwargs['setsigdef'] = sigset

            file_actions = []
            for fd in (p2cwrite, c2pread, errread):
                ikiwa fd != -1:
                    file_actions.append((os.POSIX_SPAWN_CLOSE, fd))
            for fd, fd2 in (
                (p2cread, 0),
                (c2pwrite, 1),
                (errwrite, 2),
            ):
                ikiwa fd != -1:
                    file_actions.append((os.POSIX_SPAWN_DUP2, fd, fd2))
            ikiwa file_actions:
                kwargs['file_actions'] = file_actions

            self.pid = os.posix_spawn(executable, args, env, **kwargs)
            self._child_created = True

            self._close_pipe_fds(p2cread, p2cwrite,
                                 c2pread, c2pwrite,
                                 errread, errwrite)

        eleza _execute_child(self, args, executable, preexec_fn, close_fds,
                           pass_fds, cwd, env,
                           startupinfo, creationflags, shell,
                           p2cread, p2cwrite,
                           c2pread, c2pwrite,
                           errread, errwrite,
                           restore_signals, start_new_session):
            """Execute program (POSIX version)"""

            ikiwa isinstance(args, (str, bytes)):
                args = [args]
            elikiwa isinstance(args, os.PathLike):
                ikiwa shell:
                    raise TypeError('path-like args is not allowed when '
                                    'shell is true')
                args = [args]
            else:
                args = list(args)

            ikiwa shell:
                # On Android the default shell is at '/system/bin/sh'.
                unix_shell = ('/system/bin/sh' if
                          hasattr(sys, 'getandroidapilevel') else '/bin/sh')
                args = [unix_shell, "-c"] + args
                ikiwa executable:
                    args[0] = executable

            ikiwa executable is None:
                executable = args[0]

            sys.audit("subprocess.Popen", executable, args, cwd, env)

            ikiwa (_USE_POSIX_SPAWN
                    and os.path.dirname(executable)
                    and preexec_fn is None
                    and not close_fds
                    and not pass_fds
                    and cwd is None
                    and (p2cread == -1 or p2cread > 2)
                    and (c2pwrite == -1 or c2pwrite > 2)
                    and (errwrite == -1 or errwrite > 2)
                    and not start_new_session):
                self._posix_spawn(args, executable, env, restore_signals,
                                  p2cread, p2cwrite,
                                  c2pread, c2pwrite,
                                  errread, errwrite)
                return

            orig_executable = executable

            # For transferring possible exec failure kutoka child to parent.
            # Data format: "exception name:hex errno:description"
            # Pickle is not used; it is complex and involves memory allocation.
            errpipe_read, errpipe_write = os.pipe()
            # errpipe_write must not be in the standard io 0, 1, or 2 fd range.
            low_fds_to_close = []
            while errpipe_write < 3:
                low_fds_to_close.append(errpipe_write)
                errpipe_write = os.dup(errpipe_write)
            for low_fd in low_fds_to_close:
                os.close(low_fd)
            try:
                try:
                    # We must avoid complex work that could involve
                    # malloc or free in the child process to avoid
                    # potential deadlocks, thus we do all this here.
                    # and pass it to fork_exec()

                    ikiwa env is not None:
                        env_list = []
                        for k, v in env.items():
                            k = os.fsencode(k)
                            ikiwa b'=' in k:
                                raise ValueError("illegal environment variable name")
                            env_list.append(k + b'=' + os.fsencode(v))
                    else:
                        env_list = None  # Use execv instead of execve.
                    executable = os.fsencode(executable)
                    ikiwa os.path.dirname(executable):
                        executable_list = (executable,)
                    else:
                        # This matches the behavior of os._execvpe().
                        executable_list = tuple(
                            os.path.join(os.fsencode(dir), executable)
                            for dir in os.get_exec_path(env))
                    fds_to_keep = set(pass_fds)
                    fds_to_keep.add(errpipe_write)
                    self.pid = _posixsubprocess.fork_exec(
                            args, executable_list,
                            close_fds, tuple(sorted(map(int, fds_to_keep))),
                            cwd, env_list,
                            p2cread, p2cwrite, c2pread, c2pwrite,
                            errread, errwrite,
                            errpipe_read, errpipe_write,
                            restore_signals, start_new_session, preexec_fn)
                    self._child_created = True
                finally:
                    # be sure the FD is closed no matter what
                    os.close(errpipe_write)

                self._close_pipe_fds(p2cread, p2cwrite,
                                     c2pread, c2pwrite,
                                     errread, errwrite)

                # Wait for exec to fail or succeed; possibly raising an
                # exception (limited in size)
                errpipe_data = bytearray()
                while True:
                    part = os.read(errpipe_read, 50000)
                    errpipe_data += part
                    ikiwa not part or len(errpipe_data) > 50000:
                        break
            finally:
                # be sure the FD is closed no matter what
                os.close(errpipe_read)

            ikiwa errpipe_data:
                try:
                    pid, sts = os.waitpid(self.pid, 0)
                    ikiwa pid == self.pid:
                        self._handle_exitstatus(sts)
                    else:
                        self.returncode = sys.maxsize
                except ChildProcessError:
                    pass

                try:
                    exception_name, hex_errno, err_msg = (
                            errpipe_data.split(b':', 2))
                    # The encoding here should match the encoding
                    # written in by the subprocess implementations
                    # like _posixsubprocess
                    err_msg = err_msg.decode()
                except ValueError:
                    exception_name = b'SubprocessError'
                    hex_errno = b'0'
                    err_msg = 'Bad exception data kutoka child: {!r}'.format(
                                  bytes(errpipe_data))
                child_exception_type = getattr(
                        builtins, exception_name.decode('ascii'),
                        SubprocessError)
                ikiwa issubclass(child_exception_type, OSError) and hex_errno:
                    errno_num = int(hex_errno, 16)
                    child_exec_never_called = (err_msg == "noexec")
                    ikiwa child_exec_never_called:
                        err_msg = ""
                        # The error must be kutoka chdir(cwd).
                        err_filename = cwd
                    else:
                        err_filename = orig_executable
                    ikiwa errno_num != 0:
                        err_msg = os.strerror(errno_num)
                    raise child_exception_type(errno_num, err_msg, err_filename)
                raise child_exception_type(err_msg)


        eleza _handle_exitstatus(self, sts, _WIFSIGNALED=os.WIFSIGNALED,
                _WTERMSIG=os.WTERMSIG, _WIFEXITED=os.WIFEXITED,
                _WEXITSTATUS=os.WEXITSTATUS, _WIFSTOPPED=os.WIFSTOPPED,
                _WSTOPSIG=os.WSTOPSIG):
            """All callers to this function MUST hold self._waitpid_lock."""
            # This method is called (indirectly) by __del__, so it cannot
            # refer to anything outside of its local scope.
            ikiwa _WIFSIGNALED(sts):
                self.returncode = -_WTERMSIG(sts)
            elikiwa _WIFEXITED(sts):
                self.returncode = _WEXITSTATUS(sts)
            elikiwa _WIFSTOPPED(sts):
                self.returncode = -_WSTOPSIG(sts)
            else:
                # Should never happen
                raise SubprocessError("Unknown child exit status!")


        eleza _internal_poll(self, _deadstate=None, _waitpid=os.waitpid,
                _WNOHANG=os.WNOHANG, _ECHILD=errno.ECHILD):
            """Check ikiwa child process has terminated.  Returns returncode
            attribute.

            This method is called by __del__, so it cannot reference anything
            outside of the local scope (nor can any methods it calls).

            """
            ikiwa self.returncode is None:
                ikiwa not self._waitpid_lock.acquire(False):
                    # Something else is busy calling waitpid.  Don't allow two
                    # at once.  We know nothing yet.
                    rudisha None
                try:
                    ikiwa self.returncode is not None:
                        rudisha self.returncode  # Another thread waited.
                    pid, sts = _waitpid(self.pid, _WNOHANG)
                    ikiwa pid == self.pid:
                        self._handle_exitstatus(sts)
                except OSError as e:
                    ikiwa _deadstate is not None:
                        self.returncode = _deadstate
                    elikiwa e.errno == _ECHILD:
                        # This happens ikiwa SIGCLD is set to be ignored or
                        # waiting for child processes has otherwise been
                        # disabled for our process.  This child is dead, we
                        # can't get the status.
                        # http://bugs.python.org/issue15756
                        self.returncode = 0
                finally:
                    self._waitpid_lock.release()
            rudisha self.returncode


        eleza _try_wait(self, wait_flags):
            """All callers to this function MUST hold self._waitpid_lock."""
            try:
                (pid, sts) = os.waitpid(self.pid, wait_flags)
            except ChildProcessError:
                # This happens ikiwa SIGCLD is set to be ignored or waiting
                # for child processes has otherwise been disabled for our
                # process.  This child is dead, we can't get the status.
                pid = self.pid
                sts = 0
            rudisha (pid, sts)


        eleza _wait(self, timeout):
            """Internal implementation of wait() on POSIX."""
            ikiwa self.returncode is not None:
                rudisha self.returncode

            ikiwa timeout is not None:
                endtime = _time() + timeout
                # Enter a busy loop ikiwa we have a timeout.  This busy loop was
                # cribbed kutoka Lib/threading.py in Thread.wait() at r71065.
                delay = 0.0005 # 500 us -> initial delay of 1 ms
                while True:
                    ikiwa self._waitpid_lock.acquire(False):
                        try:
                            ikiwa self.returncode is not None:
                                break  # Another thread waited.
                            (pid, sts) = self._try_wait(os.WNOHANG)
                            assert pid == self.pid or pid == 0
                            ikiwa pid == self.pid:
                                self._handle_exitstatus(sts)
                                break
                        finally:
                            self._waitpid_lock.release()
                    remaining = self._remaining_time(endtime)
                    ikiwa remaining <= 0:
                        raise TimeoutExpired(self.args, timeout)
                    delay = min(delay * 2, remaining, .05)
                    time.sleep(delay)
            else:
                while self.returncode is None:
                    with self._waitpid_lock:
                        ikiwa self.returncode is not None:
                            break  # Another thread waited.
                        (pid, sts) = self._try_wait(0)
                        # Check the pid and loop as waitpid has been known to
                        # rudisha 0 even without WNOHANG in odd situations.
                        # http://bugs.python.org/issue14396.
                        ikiwa pid == self.pid:
                            self._handle_exitstatus(sts)
            rudisha self.returncode


        eleza _communicate(self, input, endtime, orig_timeout):
            ikiwa self.stdin and not self._communication_started:
                # Flush stdio buffer.  This might block, ikiwa the user has
                # been writing to .stdin in an uncontrolled fashion.
                try:
                    self.stdin.flush()
                except BrokenPipeError:
                    pass  # communicate() must ignore BrokenPipeError.
                ikiwa not input:
                    try:
                        self.stdin.close()
                    except BrokenPipeError:
                        pass  # communicate() must ignore BrokenPipeError.

            stdout = None
            stderr = None

            # Only create this mapping ikiwa we haven't already.
            ikiwa not self._communication_started:
                self._fileobj2output = {}
                ikiwa self.stdout:
                    self._fileobj2output[self.stdout] = []
                ikiwa self.stderr:
                    self._fileobj2output[self.stderr] = []

            ikiwa self.stdout:
                stdout = self._fileobj2output[self.stdout]
            ikiwa self.stderr:
                stderr = self._fileobj2output[self.stderr]

            self._save_input(input)

            ikiwa self._input:
                input_view = memoryview(self._input)

            with _PopenSelector() as selector:
                ikiwa self.stdin and input:
                    selector.register(self.stdin, selectors.EVENT_WRITE)
                ikiwa self.stdout:
                    selector.register(self.stdout, selectors.EVENT_READ)
                ikiwa self.stderr:
                    selector.register(self.stderr, selectors.EVENT_READ)

                while selector.get_map():
                    timeout = self._remaining_time(endtime)
                    ikiwa timeout is not None and timeout < 0:
                        self._check_timeout(endtime, orig_timeout,
                                            stdout, stderr,
                                            skip_check_and_raise=True)
                        raise RuntimeError(  # Impossible :)
                            '_check_timeout(..., skip_check_and_raise=True) '
                            'failed to raise TimeoutExpired.')

                    ready = selector.select(timeout)
                    self._check_timeout(endtime, orig_timeout, stdout, stderr)

                    # XXX Rewrite these to use non-blocking I/O on the file
                    # objects; they are no longer using C stdio!

                    for key, events in ready:
                        ikiwa key.fileobj is self.stdin:
                            chunk = input_view[self._input_offset :
                                               self._input_offset + _PIPE_BUF]
                            try:
                                self._input_offset += os.write(key.fd, chunk)
                            except BrokenPipeError:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            else:
                                ikiwa self._input_offset >= len(self._input):
                                    selector.unregister(key.fileobj)
                                    key.fileobj.close()
                        elikiwa key.fileobj in (self.stdout, self.stderr):
                            data = os.read(key.fd, 32768)
                            ikiwa not data:
                                selector.unregister(key.fileobj)
                                key.fileobj.close()
                            self._fileobj2output[key.fileobj].append(data)

            self.wait(timeout=self._remaining_time(endtime))

            # All data exchanged.  Translate lists into strings.
            ikiwa stdout is not None:
                stdout = b''.join(stdout)
            ikiwa stderr is not None:
                stderr = b''.join(stderr)

            # Translate newlines, ikiwa requested.
            # This also turns bytes into strings.
            ikiwa self.text_mode:
                ikiwa stdout is not None:
                    stdout = self._translate_newlines(stdout,
                                                      self.stdout.encoding,
                                                      self.stdout.errors)
                ikiwa stderr is not None:
                    stderr = self._translate_newlines(stderr,
                                                      self.stderr.encoding,
                                                      self.stderr.errors)

            rudisha (stdout, stderr)


        eleza _save_input(self, input):
            # This method is called kutoka the _communicate_with_*() methods
            # so that ikiwa we time out while communicating, we can continue
            # sending input ikiwa we retry.
            ikiwa self.stdin and self._input is None:
                self._input_offset = 0
                self._input = input
                ikiwa input is not None and self.text_mode:
                    self._input = self._input.encode(self.stdin.encoding,
                                                     self.stdin.errors)


        eleza send_signal(self, sig):
            """Send a signal to the process."""
            # Skip signalling a process that we know has already died.
            ikiwa self.returncode is None:
                os.kill(self.pid, sig)

        eleza terminate(self):
            """Terminate the process with SIGTERM
            """
            self.send_signal(signal.SIGTERM)

        eleza kill(self):
            """Kill the process with SIGKILL
            """
            self.send_signal(signal.SIGKILL)
