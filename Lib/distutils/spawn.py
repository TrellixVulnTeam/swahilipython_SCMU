"""distutils.spawn

Provides the 'spawn()' function, a front-end to various platform-
specific functions kila launching another program kwenye a sub-process.
Also provides the 'find_executable()' to search the path kila a given
executable name.
"""

agiza sys
agiza os

kutoka distutils.errors agiza DistutilsPlatformError, DistutilsExecError
kutoka distutils.debug agiza DEBUG
kutoka distutils agiza log

eleza spawn(cmd, search_path=1, verbose=0, dry_run=0):
    """Run another program, specified kama a command list 'cmd', kwenye a new process.

    'cmd' ni just the argument list kila the new process, ie.
    cmd[0] ni the program to run na cmd[1:] are the rest of its arguments.
    There ni no way to run a program ukijumuisha a name different kutoka that of its
    executable.

    If 'search_path' ni true (the default), the system's executable
    search path will be used to find the program; otherwise, cmd[0]
    must be the exact path to the executable.  If 'dry_run' ni true,
    the command will sio actually be run.

    Raise DistutilsExecError ikiwa running the program fails kwenye any way; just
    rudisha on success.
    """
    # cmd ni documented kama a list, but just kwenye case some code pitaes a tuple
    # in, protect our %-formatting code against horrible death
    cmd = list(cmd)
    ikiwa os.name == 'posix':
        _spawn_posix(cmd, search_path, dry_run=dry_run)
    lasivyo os.name == 'nt':
        _spawn_nt(cmd, search_path, dry_run=dry_run)
    isipokua:
        ashiria DistutilsPlatformError(
              "don't know how to spawn programs on platform '%s'" % os.name)

eleza _nt_quote_args(args):
    """Quote command-line arguments kila DOS/Windows conventions.

    Just wraps every argument which contains blanks kwenye double quotes, na
    returns a new argument list.
    """
    # XXX this doesn't seem very robust to me -- but ikiwa the Windows guys
    # say it'll work, I guess I'll have to accept it.  (What ikiwa an arg
    # contains quotes?  What other magic characters, other than spaces,
    # have to be escaped?  Is there an escaping mechanism other than
    # quoting?)
    kila i, arg kwenye enumerate(args):
        ikiwa ' ' kwenye arg:
            args[i] = '"%s"' % arg
    rudisha args

eleza _spawn_nt(cmd, search_path=1, verbose=0, dry_run=0):
    executable = cmd[0]
    cmd = _nt_quote_args(cmd)
    ikiwa search_path:
        # either we find one ama it stays the same
        executable = find_executable(executable) ama executable
    log.info(' '.join([executable] + cmd[1:]))
    ikiwa sio dry_run:
        # spawn kila NT requires a full path to the .exe
        jaribu:
            rc = os.spawnv(os.P_WAIT, executable, cmd)
        tatizo OSError kama exc:
            # this seems to happen when the command isn't found
            ikiwa sio DEBUG:
                cmd = executable
            ashiria DistutilsExecError(
                  "command %r failed: %s" % (cmd, exc.args[-1]))
        ikiwa rc != 0:
            # na this reflects the command running but failing
            ikiwa sio DEBUG:
                cmd = executable
            ashiria DistutilsExecError(
                  "command %r failed ukijumuisha exit status %d" % (cmd, rc))

ikiwa sys.platform == 'darwin':
    _cfg_target = Tupu
    _cfg_target_split = Tupu

eleza _spawn_posix(cmd, search_path=1, verbose=0, dry_run=0):
    log.info(' '.join(cmd))
    ikiwa dry_run:
        return
    executable = cmd[0]
    exec_fn = search_path na os.execvp ama os.execv
    env = Tupu
    ikiwa sys.platform == 'darwin':
        global _cfg_target, _cfg_target_split
        ikiwa _cfg_target ni Tupu:
            kutoka distutils agiza sysconfig
            _cfg_target = sysconfig.get_config_var(
                                  'MACOSX_DEPLOYMENT_TARGET') ama ''
            ikiwa _cfg_target:
                _cfg_target_split = [int(x) kila x kwenye _cfg_target.split('.')]
        ikiwa _cfg_target:
            # ensure that the deployment target of build process ni sio less
            # than that used when the interpreter was built. This ensures
            # extension modules are built ukijumuisha correct compatibility values
            cur_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', _cfg_target)
            ikiwa _cfg_target_split > [int(x) kila x kwenye cur_target.split('.')]:
                my_msg = ('$MACOSX_DEPLOYMENT_TARGET mismatch: '
                          'now "%s" but "%s" during configure'
                                % (cur_target, _cfg_target))
                ashiria DistutilsPlatformError(my_msg)
            env = dict(os.environ,
                       MACOSX_DEPLOYMENT_TARGET=cur_target)
            exec_fn = search_path na os.execvpe ama os.execve
    pid = os.fork()
    ikiwa pid == 0: # kwenye the child
        jaribu:
            ikiwa env ni Tupu:
                exec_fn(executable, cmd)
            isipokua:
                exec_fn(executable, cmd, env)
        tatizo OSError kama e:
            ikiwa sio DEBUG:
                cmd = executable
            sys.stderr.write("unable to execute %r: %s\n"
                             % (cmd, e.strerror))
            os._exit(1)

        ikiwa sio DEBUG:
            cmd = executable
        sys.stderr.write("unable to execute %r kila unknown reasons" % cmd)
        os._exit(1)
    isipokua: # kwenye the parent
        # Loop until the child either exits ama ni terminated by a signal
        # (ie. keep waiting ikiwa it's merely stopped)
        wakati Kweli:
            jaribu:
                pid, status = os.waitpid(pid, 0)
            tatizo OSError kama exc:
                ikiwa sio DEBUG:
                    cmd = executable
                ashiria DistutilsExecError(
                      "command %r failed: %s" % (cmd, exc.args[-1]))
            ikiwa os.WIFSIGNALED(status):
                ikiwa sio DEBUG:
                    cmd = executable
                ashiria DistutilsExecError(
                      "command %r terminated by signal %d"
                      % (cmd, os.WTERMSIG(status)))
            lasivyo os.WIFEXITED(status):
                exit_status = os.WEXITSTATUS(status)
                ikiwa exit_status == 0:
                    rudisha   # hey, it succeeded!
                isipokua:
                    ikiwa sio DEBUG:
                        cmd = executable
                    ashiria DistutilsExecError(
                          "command %r failed ukijumuisha exit status %d"
                          % (cmd, exit_status))
            lasivyo os.WIFSTOPPED(status):
                endelea
            isipokua:
                ikiwa sio DEBUG:
                    cmd = executable
                ashiria DistutilsExecError(
                      "unknown error executing %r: termination status %d"
                      % (cmd, status))

eleza find_executable(executable, path=Tupu):
    """Tries to find 'executable' kwenye the directories listed kwenye 'path'.

    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename ama Tupu ikiwa sio found.
    """
    _, ext = os.path.splitext(executable)
    ikiwa (sys.platform == 'win32') na (ext != '.exe'):
        executable = executable + '.exe'

    ikiwa os.path.isfile(executable):
        rudisha executable

    ikiwa path ni Tupu:
        path = os.environ.get('PATH', Tupu)
        ikiwa path ni Tupu:
            jaribu:
                path = os.confstr("CS_PATH")
            tatizo (AttributeError, ValueError):
                # os.confstr() ama CS_PATH ni sio available
                path = os.defpath
        # bpo-35755: Don't use os.defpath ikiwa the PATH environment variable is
        # set to an empty string

    # PATH='' doesn't match, whereas PATH=':' looks kwenye the current directory
    ikiwa sio path:
        rudisha Tupu

    paths = path.split(os.pathsep)
    kila p kwenye paths:
        f = os.path.join(p, executable)
        ikiwa os.path.isfile(f):
            # the file exists, we have a shot at spawn working
            rudisha f
    rudisha Tupu
