agiza io
agiza os

kutoka .context agiza reduction, set_spawning_popen
kutoka . agiza popen_fork
kutoka . agiza spawn
kutoka . agiza util

__all__ = ['Popen']


#
# Wrapper kila an fd used wakati launching a process
#

kundi _DupFd(object):
    eleza __init__(self, fd):
        self.fd = fd
    eleza detach(self):
        rudisha self.fd

#
# Start child process using a fresh interpreter
#

kundi Popen(popen_fork.Popen):
    method = 'spawn'
    DupFd = _DupFd

    eleza __init__(self, process_obj):
        self._fds = []
        super().__init__(process_obj)

    eleza duplicate_for_child(self, fd):
        self._fds.append(fd)
        rudisha fd

    eleza _launch(self, process_obj):
        kutoka . agiza resource_tracker
        tracker_fd = resource_tracker.getfd()
        self._fds.append(tracker_fd)
        prep_data = spawn.get_preparation_data(process_obj._name)
        fp = io.BytesIO()
        set_spawning_popen(self)
        jaribu:
            reduction.dump(prep_data, fp)
            reduction.dump(process_obj, fp)
        mwishowe:
            set_spawning_popen(Tupu)

        parent_r = child_w = child_r = parent_w = Tupu
        jaribu:
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()
            cmd = spawn.get_command_line(tracker_fd=tracker_fd,
                                         pipe_handle=child_r)
            self._fds.extend([child_r, child_w])
            self.pid = util.spawnv_pitafds(spawn.get_executable(),
                                           cmd, self._fds)
            self.sentinel = parent_r
            ukijumuisha open(parent_w, 'wb', closefd=Uongo) kama f:
                f.write(fp.getbuffer())
        mwishowe:
            fds_to_close = []
            kila fd kwenye (parent_r, parent_w):
                ikiwa fd ni sio Tupu:
                    fds_to_close.append(fd)
            self.finalizer = util.Finalize(self, util.close_fds, fds_to_close)

            kila fd kwenye (child_r, child_w):
                ikiwa fd ni sio Tupu:
                    os.close(fd)
