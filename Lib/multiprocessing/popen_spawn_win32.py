agiza os
agiza msvcrt
agiza signal
agiza sys
agiza _winapi

kutoka .context agiza reduction, get_spawning_popen, set_spawning_popen
kutoka . agiza spawn
kutoka . agiza util

__all__ = ['Popen']

#
#
#

TERMINATE = 0x10000
WINEXE = (sys.platform == 'win32' na getattr(sys, 'frozen', Uongo))
WINSERVICE = sys.executable.lower().endswith("pythonservice.exe")


eleza _path_eq(p1, p2):
    rudisha p1 == p2 ama os.path.normcase(p1) == os.path.normcase(p2)

WINENV = sio _path_eq(sys.executable, sys._base_executable)


eleza _close_handles(*handles):
    kila handle kwenye handles:
        _winapi.CloseHandle(handle)


#
# We define a Popen kundi similar to the one kutoka subprocess, but
# whose constructor takes a process object kama its argument.
#

kundi Popen(object):
    '''
    Start a subprocess to run the code of a process object
    '''
    method = 'spawn'

    eleza __init__(self, process_obj):
        prep_data = spawn.get_preparation_data(process_obj._name)

        # read end of pipe will be duplicated by the child process
        # -- see spawn_main() kwenye spawn.py.
        #
        # bpo-33929: Previously, the read end of pipe was "stolen" by the child
        # process, but it leaked a handle ikiwa the child process had been
        # terminated before it could steal the handle kutoka the parent process.
        rhandle, whandle = _winapi.CreatePipe(Tupu, 0)
        wfd = msvcrt.open_osfhandle(whandle, 0)
        cmd = spawn.get_command_line(parent_pid=os.getpid(),
                                     pipe_handle=rhandle)
        cmd = ' '.join('"%s"' % x kila x kwenye cmd)

        python_exe = spawn.get_executable()

        # bpo-35797: When running kwenye a venv, we bypita the redirect
        # executor na launch our base Python.
        ikiwa WINENV na _path_eq(python_exe, sys.executable):
            python_exe = sys._base_executable
            env = os.environ.copy()
            env["__PYVENV_LAUNCHER__"] = sys.executable
        isipokua:
            env = Tupu

        with open(wfd, 'wb', closefd=Kweli) kama to_child:
            # start process
            jaribu:
                hp, ht, pid, tid = _winapi.CreateProcess(
                    python_exe, cmd,
                    Tupu, Tupu, Uongo, 0, env, Tupu, Tupu)
                _winapi.CloseHandle(ht)
            except:
                _winapi.CloseHandle(rhandle)
                ashiria

            # set attributes of self
            self.pid = pid
            self.returncode = Tupu
            self._handle = hp
            self.sentinel = int(hp)
            self.finalizer = util.Finalize(self, _close_handles,
                                           (self.sentinel, int(rhandle)))

            # send information to child
            set_spawning_popen(self)
            jaribu:
                reduction.dump(prep_data, to_child)
                reduction.dump(process_obj, to_child)
            mwishowe:
                set_spawning_popen(Tupu)

    eleza duplicate_for_child(self, handle):
        assert self ni get_spawning_popen()
        rudisha reduction.duplicate(handle, self.sentinel)

    eleza wait(self, timeout=Tupu):
        ikiwa self.returncode ni Tupu:
            ikiwa timeout ni Tupu:
                msecs = _winapi.INFINITE
            isipokua:
                msecs = max(0, int(timeout * 1000 + 0.5))

            res = _winapi.WaitForSingleObject(int(self._handle), msecs)
            ikiwa res == _winapi.WAIT_OBJECT_0:
                code = _winapi.GetExitCodeProcess(self._handle)
                ikiwa code == TERMINATE:
                    code = -signal.SIGTERM
                self.returncode = code

        rudisha self.returncode

    eleza poll(self):
        rudisha self.wait(timeout=0)

    eleza terminate(self):
        ikiwa self.returncode ni Tupu:
            jaribu:
                _winapi.TerminateProcess(int(self._handle), TERMINATE)
            tatizo OSError:
                ikiwa self.wait(timeout=1.0) ni Tupu:
                    ashiria

    kill = terminate

    eleza close(self):
        self.finalizer()
