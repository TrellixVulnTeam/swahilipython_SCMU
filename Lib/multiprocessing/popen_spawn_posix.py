agiza io
agiza os

kutoka .context agiza reduction, set_spawning_popen
kutoka . agiza popen_fork
kutoka . agiza spawn
kutoka . agiza util

__all__ = ['Popen']


#
# Wrapper for an fd used while launching a process
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
        try:
            reduction.dump(prep_data, fp)
            reduction.dump(process_obj, fp)
        finally:
            set_spawning_popen(None)

        parent_r = child_w = child_r = parent_w = None
        try:
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()
            cmd = spawn.get_command_line(tracker_fd=tracker_fd,
                                         pipe_handle=child_r)
            self._fds.extend([child_r, child_w])
            self.pid = util.spawnv_passfds(spawn.get_executable(),
                                           cmd, self._fds)
            self.sentinel = parent_r
            with open(parent_w, 'wb', closefd=False) as f:
                f.write(fp.getbuffer())
        finally:
            fds_to_close = []
            for fd in (parent_r, parent_w):
                ikiwa fd is not None:
                    fds_to_close.append(fd)
            self.finalizer = util.Finalize(self, util.close_fds, fds_to_close)

            for fd in (child_r, child_w):
                ikiwa fd is not None:
                    os.close(fd)
