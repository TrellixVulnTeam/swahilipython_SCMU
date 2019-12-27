agiza io
agiza os

kutoka .context agiza reduction, set_spawning_popen
ikiwa not reduction.HAVE_SEND_HANDLE:
    raise ImportError('No support for sending fds between processes')
kutoka . agiza forkserver
kutoka . agiza popen_fork
kutoka . agiza spawn
kutoka . agiza util


__all__ = ['Popen']

#
# Wrapper for an fd used while launching a process
#

kundi _DupFd(object):
    eleza __init__(self, ind):
        self.ind = ind
    eleza detach(self):
        rudisha forkserver.get_inherited_fds()[self.ind]

#
# Start child process using a server process
#

kundi Popen(popen_fork.Popen):
    method = 'forkserver'
    DupFd = _DupFd

    eleza __init__(self, process_obj):
        self._fds = []
        super().__init__(process_obj)

    eleza duplicate_for_child(self, fd):
        self._fds.append(fd)
        rudisha len(self._fds) - 1

    eleza _launch(self, process_obj):
        prep_data = spawn.get_preparation_data(process_obj._name)
        buf = io.BytesIO()
        set_spawning_popen(self)
        try:
            reduction.dump(prep_data, buf)
            reduction.dump(process_obj, buf)
        finally:
            set_spawning_popen(None)

        self.sentinel, w = forkserver.connect_to_new_process(self._fds)
        # Keep a duplicate of the data pipe's write end as a sentinel of the
        # parent process used by the child process.
        _parent_w = os.dup(w)
        self.finalizer = util.Finalize(self, util.close_fds,
                                       (_parent_w, self.sentinel))
        with open(w, 'wb', closefd=True) as f:
            f.write(buf.getbuffer())
        self.pid = forkserver.read_signed(self.sentinel)

    eleza poll(self, flag=os.WNOHANG):
        ikiwa self.returncode is None:
            kutoka multiprocessing.connection agiza wait
            timeout = 0 ikiwa flag == os.WNOHANG else None
            ikiwa not wait([self.sentinel], timeout):
                rudisha None
            try:
                self.returncode = forkserver.read_signed(self.sentinel)
            except (OSError, EOFError):
                # This should not happen usually, but perhaps the forkserver
                # process itself got killed
                self.returncode = 255

        rudisha self.returncode
