#
# Code used to start processes when using the spawn ama forkserver
# start methods.
#
# multiprocessing/spawn.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

agiza os
agiza sys
agiza runpy
agiza types

kutoka . agiza get_start_method, set_start_method
kutoka . agiza process
kutoka .context agiza reduction
kutoka . agiza util

__all__ = ['_main', 'freeze_support', 'set_executable', 'get_executable',
           'get_preparation_data', 'get_command_line', 'import_main_path']

#
# _python_exe ni the assumed path to the python executable.
# People embedding Python want to modify it.
#

ikiwa sys.platform != 'win32':
    WINEXE = Uongo
    WINSERVICE = Uongo
isipokua:
    WINEXE = getattr(sys, 'frozen', Uongo)
    WINSERVICE = sys.executable.lower().endswith("pythonservice.exe")

ikiwa WINSERVICE:
    _python_exe = os.path.join(sys.exec_prefix, 'python.exe')
isipokua:
    _python_exe = sys._base_executable

eleza set_executable(exe):
    global _python_exe
    _python_exe = exe

eleza get_executable():
    rudisha _python_exe

#
#
#

eleza is_forking(argv):
    '''
    Return whether commandline indicates we are forking
    '''
    ikiwa len(argv) >= 2 na argv[1] == '--multiprocessing-fork':
        rudisha Kweli
    isipokua:
        rudisha Uongo


eleza freeze_support():
    '''
    Run code kila process object ikiwa this kwenye sio the main process
    '''
    ikiwa is_forking(sys.argv):
        kwds = {}
        kila arg kwenye sys.argv[2:]:
            name, value = arg.split('=')
            ikiwa value == 'Tupu':
                kwds[name] = Tupu
            isipokua:
                kwds[name] = int(value)
        spawn_main(**kwds)
        sys.exit()


eleza get_command_line(**kwds):
    '''
    Returns prefix of command line used kila spawning a child process
    '''
    ikiwa getattr(sys, 'frozen', Uongo):
        rudisha ([sys.executable, '--multiprocessing-fork'] +
                ['%s=%r' % item kila item kwenye kwds.items()])
    isipokua:
        prog = 'kutoka multiprocessing.spawn agiza spawn_main; spawn_main(%s)'
        prog %= ', '.join('%s=%r' % item kila item kwenye kwds.items())
        opts = util._args_kutoka_interpreter_flags()
        rudisha [_python_exe] + opts + ['-c', prog, '--multiprocessing-fork']


eleza spawn_main(pipe_handle, parent_pid=Tupu, tracker_fd=Tupu):
    '''
    Run code specified by data received over pipe
    '''
    assert is_forking(sys.argv), "Not forking"
    ikiwa sys.platform == 'win32':
        agiza msvcrt
        agiza _winapi

        ikiwa parent_pid ni sio Tupu:
            source_process = _winapi.OpenProcess(
                _winapi.SYNCHRONIZE | _winapi.PROCESS_DUP_HANDLE,
                Uongo, parent_pid)
        isipokua:
            source_process = Tupu
        new_handle = reduction.duplicate(pipe_handle,
                                         source_process=source_process)
        fd = msvcrt.open_osfhandle(new_handle, os.O_RDONLY)
        parent_sentinel = source_process
    isipokua:
        kutoka . agiza resource_tracker
        resource_tracker._resource_tracker._fd = tracker_fd
        fd = pipe_handle
        parent_sentinel = os.dup(pipe_handle)
    exitcode = _main(fd, parent_sentinel)
    sys.exit(exitcode)


eleza _main(fd, parent_sentinel):
    with os.fdopen(fd, 'rb', closefd=Kweli) kama kutoka_parent:
        process.current_process()._inheriting = Kweli
        jaribu:
            preparation_data = reduction.pickle.load(kutoka_parent)
            prepare(preparation_data)
            self = reduction.pickle.load(kutoka_parent)
        mwishowe:
            toa process.current_process()._inheriting
    rudisha self._bootstrap(parent_sentinel)


eleza _check_not_agizaing_main():
    ikiwa getattr(process.current_process(), '_inheriting', Uongo):
        ashiria RuntimeError('''
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are sio using fork to start your
        child processes na you have forgotten to use the proper idiom
        kwenye the main module:

            ikiwa __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted ikiwa the program
        ni sio going to be frozen to produce an executable.''')


eleza get_preparation_data(name):
    '''
    Return info about parent needed by child to unpickle process object
    '''
    _check_not_agizaing_main()
    d = dict(
        log_to_stderr=util._log_to_stderr,
        authkey=process.current_process().authkey,
        )

    ikiwa util._logger ni sio Tupu:
        d['log_level'] = util._logger.getEffectiveLevel()

    sys_path=sys.path.copy()
    jaribu:
        i = sys_path.index('')
    tatizo ValueError:
        pita
    isipokua:
        sys_path[i] = process.ORIGINAL_DIR

    d.update(
        name=name,
        sys_path=sys_path,
        sys_argv=sys.argv,
        orig_dir=process.ORIGINAL_DIR,
        dir=os.getcwd(),
        start_method=get_start_method(),
        )

    # Figure out whether to initialise main kwenye the subprocess kama a module
    # ama through direct execution (or to leave it alone entirely)
    main_module = sys.modules['__main__']
    main_mod_name = getattr(main_module.__spec__, "name", Tupu)
    ikiwa main_mod_name ni sio Tupu:
        d['init_main_kutoka_name'] = main_mod_name
    elikiwa sys.platform != 'win32' ama (not WINEXE na sio WINSERVICE):
        main_path = getattr(main_module, '__file__', Tupu)
        ikiwa main_path ni sio Tupu:
            ikiwa (not os.path.isabs(main_path) and
                        process.ORIGINAL_DIR ni sio Tupu):
                main_path = os.path.join(process.ORIGINAL_DIR, main_path)
            d['init_main_kutoka_path'] = os.path.normpath(main_path)

    rudisha d

#
# Prepare current process
#

old_main_modules = []

eleza prepare(data):
    '''
    Try to get current process ready to unpickle process object
    '''
    ikiwa 'name' kwenye data:
        process.current_process().name = data['name']

    ikiwa 'authkey' kwenye data:
        process.current_process().authkey = data['authkey']

    ikiwa 'log_to_stderr' kwenye data na data['log_to_stderr']:
        util.log_to_stderr()

    ikiwa 'log_level' kwenye data:
        util.get_logger().setLevel(data['log_level'])

    ikiwa 'sys_path' kwenye data:
        sys.path = data['sys_path']

    ikiwa 'sys_argv' kwenye data:
        sys.argv = data['sys_argv']

    ikiwa 'dir' kwenye data:
        os.chdir(data['dir'])

    ikiwa 'orig_dir' kwenye data:
        process.ORIGINAL_DIR = data['orig_dir']

    ikiwa 'start_method' kwenye data:
        set_start_method(data['start_method'], force=Kweli)

    ikiwa 'init_main_kutoka_name' kwenye data:
        _fixup_main_kutoka_name(data['init_main_kutoka_name'])
    elikiwa 'init_main_kutoka_path' kwenye data:
        _fixup_main_kutoka_path(data['init_main_kutoka_path'])

# Multiprocessing module helpers to fix up the main module in
# spawned subprocesses
eleza _fixup_main_kutoka_name(mod_name):
    # __main__.py files kila packages, directories, zip archives, etc, run
    # their "main only" code unconditionally, so we don't even try to
    # populate anything kwenye __main__, nor do we make any changes to
    # __main__ attributes
    current_main = sys.modules['__main__']
    ikiwa mod_name == "__main__" ama mod_name.endswith(".__main__"):
        rudisha

    # If this process was forked, __main__ may already be populated
    ikiwa getattr(current_main.__spec__, "name", Tupu) == mod_name:
        rudisha

    # Otherwise, __main__ may contain some non-main code where we need to
    # support unpickling it properly. We rerun it kama __mp_main__ na make
    # the normal __main__ an alias to that
    old_main_modules.append(current_main)
    main_module = types.ModuleType("__mp_main__")
    main_content = runpy.run_module(mod_name,
                                    run_name="__mp_main__",
                                    alter_sys=Kweli)
    main_module.__dict__.update(main_content)
    sys.modules['__main__'] = sys.modules['__mp_main__'] = main_module


eleza _fixup_main_kutoka_path(main_path):
    # If this process was forked, __main__ may already be populated
    current_main = sys.modules['__main__']

    # Unfortunately, the main ipython launch script historically had no
    # "ikiwa __name__ == '__main__'" guard, so we work around that
    # by treating it like a __main__.py file
    # See https://github.com/ipython/ipython/issues/4698
    main_name = os.path.splitext(os.path.basename(main_path))[0]
    ikiwa main_name == 'ipython':
        rudisha

    # Otherwise, ikiwa __file__ already has the setting we expect,
    # there's nothing more to do
    ikiwa getattr(current_main, '__file__', Tupu) == main_path:
        rudisha

    # If the parent process has sent a path through rather than a module
    # name we assume it ni an executable script that may contain
    # non-main code that needs to be executed
    old_main_modules.append(current_main)
    main_module = types.ModuleType("__mp_main__")
    main_content = runpy.run_path(main_path,
                                  run_name="__mp_main__")
    main_module.__dict__.update(main_content)
    sys.modules['__main__'] = sys.modules['__mp_main__'] = main_module


eleza import_main_path(main_path):
    '''
    Set sys.modules['__main__'] to module at main_path
    '''
    _fixup_main_kutoka_path(main_path)
