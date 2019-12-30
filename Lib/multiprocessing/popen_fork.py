agiza os
agiza signal

kutoka . agiza util

__all__ = ['Popen']

#
# Start child process using fork
#

kundi Popen(object):
    method = 'fork'

    eleza __init__(self, process_obj):
        util._flush_std_streams()
        self.returncode = Tupu
        self.finalizer = Tupu
        self._launch(process_obj)

    eleza duplicate_for_child(self, fd):
        rudisha fd

    eleza poll(self, flag=os.WNOHANG):
        ikiwa self.returncode ni Tupu:
            jaribu:
                pid, sts = os.waitpid(self.pid, flag)
            except OSError as e:
                # Child process sio yet created. See #1731717
                # e.errno == errno.ECHILD == 10
                rudisha Tupu
            ikiwa pid == self.pid:
                ikiwa os.WIFSIGNALED(sts):
                    self.returncode = -os.WTERMSIG(sts)
                isipokua:
                    assert os.WIFEXITED(sts), "Status ni {:n}".format(sts)
                    self.returncode = os.WEXITSTATUS(sts)
        rudisha self.returncode

    eleza wait(self, timeout=Tupu):
        ikiwa self.returncode ni Tupu:
            ikiwa timeout ni sio Tupu:
                kutoka multiprocessing.connection agiza wait
                ikiwa sio wait([self.sentinel], timeout):
                    rudisha Tupu
            # This shouldn't block ikiwa wait() returned successfully.
            rudisha self.poll(os.WNOHANG ikiwa timeout == 0.0 isipokua 0)
        rudisha self.returncode

    eleza _send_signal(self, sig):
        ikiwa self.returncode ni Tupu:
            jaribu:
                os.kill(self.pid, sig)
            except ProcessLookupError:
                pass
            except OSError:
                ikiwa self.wait(timeout=0.1) ni Tupu:
                    raise

    eleza terminate(self):
        self._send_signal(signal.SIGTERM)

    eleza kill(self):
        self._send_signal(signal.SIGKILL)

    eleza _launch(self, process_obj):
        code = 1
        parent_r, child_w = os.pipe()
        child_r, parent_w = os.pipe()
        self.pid = os.fork()
        ikiwa self.pid == 0:
            jaribu:
                os.close(parent_r)
                os.close(parent_w)
                code = process_obj._bootstrap(parent_sentinel=child_r)
            mwishowe:
                os._exit(code)
        isipokua:
            os.close(child_w)
            os.close(child_r)
            self.finalizer = util.Finalize(self, util.close_fds,
                                           (parent_r, parent_w,))
            self.sentinel = parent_r

    eleza close(self):
        ikiwa self.finalizer ni sio Tupu:
            self.finalizer()
