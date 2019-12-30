#
# Module which supports allocation of memory kutoka an mmap
#
# multiprocessing/heap.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

agiza bisect
kutoka collections agiza defaultdict
agiza mmap
agiza os
agiza sys
agiza tempfile
agiza threading

kutoka .context agiza reduction, assert_spawning
kutoka . agiza util

__all__ = ['BufferWrapper']

#
# Inheritable kundi which wraps an mmap, na kutoka which blocks can be allocated
#

ikiwa sys.platform == 'win32':

    agiza _winapi

    kundi Arena(object):
        """
        A shared memory area backed by anonymous memory (Windows).
        """

        _rand = tempfile._RandomNameSequence()

        eleza __init__(self, size):
            self.size = size
            kila i kwenye range(100):
                name = 'pym-%d-%s' % (os.getpid(), next(self._rand))
                buf = mmap.mmap(-1, size, tagname=name)
                ikiwa _winapi.GetLastError() == 0:
                    koma
                # We have reopened a preexisting mmap.
                buf.close()
            isipokua:
                ashiria FileExistsError('Cansio find name kila new mmap')
            self.name = name
            self.buffer = buf
            self._state = (self.size, self.name)

        eleza __getstate__(self):
            assert_spawning(self)
            rudisha self._state

        eleza __setstate__(self, state):
            self.size, self.name = self._state = state
            # Reopen existing mmap
            self.buffer = mmap.mmap(-1, self.size, tagname=self.name)
            # XXX Temporarily preventing buildbot failures wakati determining
            # XXX the correct long-term fix. See issue 23060
            #assert _winapi.GetLastError() == _winapi.ERROR_ALREADY_EXISTS

isipokua:

    kundi Arena(object):
        """
        A shared memory area backed by a temporary file (POSIX).
        """

        ikiwa sys.platform == 'linux':
            _dir_candidates = ['/dev/shm']
        isipokua:
            _dir_candidates = []

        eleza __init__(self, size, fd=-1):
            self.size = size
            self.fd = fd
            ikiwa fd == -1:
                # Arena ni created anew (ikiwa fd != -1, it means we're coming
                # kutoka rebuild_arena() below)
                self.fd, name = tempfile.mkstemp(
                     prefix='pym-%d-'%os.getpid(),
                     dir=self._choose_dir(size))
                os.unlink(name)
                util.Finalize(self, os.close, (self.fd,))
                os.ftruncate(self.fd, size)
            self.buffer = mmap.mmap(self.fd, self.size)

        eleza _choose_dir(self, size):
            # Choose a non-storage backed directory ikiwa possible,
            # to improve performance
            kila d kwenye self._dir_candidates:
                st = os.statvfs(d)
                ikiwa st.f_bavail * st.f_frsize >= size:  # enough free space?
                    rudisha d
            rudisha util.get_temp_dir()

    eleza reduce_arena(a):
        ikiwa a.fd == -1:
            ashiria ValueError('Arena ni unpicklable because '
                             'forking was enabled when it was created')
        rudisha rebuild_arena, (a.size, reduction.DupFd(a.fd))

    eleza rebuild_arena(size, dupfd):
        rudisha Arena(size, dupfd.detach())

    reduction.register(Arena, reduce_arena)

#
# Class allowing allocation of chunks of memory kutoka arenas
#

kundi Heap(object):

    # Minimum malloc() alignment
    _alignment = 8

    _DISCARD_FREE_SPACE_LARGER_THAN = 4 * 1024 ** 2  # 4 MB
    _DOUBLE_ARENA_SIZE_UNTIL = 4 * 1024 ** 2

    eleza __init__(self, size=mmap.PAGESIZE):
        self._lastpid = os.getpid()
        self._lock = threading.Lock()
        # Current arena allocation size
        self._size = size
        # A sorted list of available block sizes kwenye arenas
        self._lengths = []

        # Free block management:
        # - map each block size to a list of `(Arena, start, stop)` blocks
        self._len_to_seq = {}
        # - map `(Arena, start)` tuple to the `(Arena, start, stop)` block
        #   starting at that offset
        self._start_to_block = {}
        # - map `(Arena, stop)` tuple to the `(Arena, start, stop)` block
        #   ending at that offset
        self._stop_to_block = {}

        # Map arenas to their `(Arena, start, stop)` blocks kwenye use
        self._allocated_blocks = defaultdict(set)
        self._arenas = []

        # List of pending blocks to free - see comment kwenye free() below
        self._pending_free_blocks = []

        # Statistics
        self._n_mallocs = 0
        self._n_frees = 0

    @staticmethod
    eleza _roundup(n, alignment):
        # alignment must be a power of 2
        mask = alignment - 1
        rudisha (n + mask) & ~mask

    eleza _new_arena(self, size):
        # Create a new arena ukijumuisha at least the given *size*
        length = self._roundup(max(self._size, size), mmap.PAGESIZE)
        # We carve larger na larger arenas, kila efficiency, until we
        # reach a large-ish size (roughly L3 cache-sized)
        ikiwa self._size < self._DOUBLE_ARENA_SIZE_UNTIL:
            self._size *= 2
        util.info('allocating a new mmap of length %d', length)
        arena = Arena(length)
        self._arenas.append(arena)
        rudisha (arena, 0, length)

    eleza _discard_arena(self, arena):
        # Possibly delete the given (unused) arena
        length = arena.size
        # Reusing an existing arena ni faster than creating a new one, so
        # we only reclaim space ikiwa it's large enough.
        ikiwa length < self._DISCARD_FREE_SPACE_LARGER_THAN:
            rudisha
        blocks = self._allocated_blocks.pop(arena)
        assert sio blocks
        toa self._start_to_block[(arena, 0)]
        toa self._stop_to_block[(arena, length)]
        self._arenas.remove(arena)
        seq = self._len_to_seq[length]
        seq.remove((arena, 0, length))
        ikiwa sio seq:
            toa self._len_to_seq[length]
            self._lengths.remove(length)

    eleza _malloc(self, size):
        # returns a large enough block -- it might be much larger
        i = bisect.bisect_left(self._lengths, size)
        ikiwa i == len(self._lengths):
            rudisha self._new_arena(size)
        isipokua:
            length = self._lengths[i]
            seq = self._len_to_seq[length]
            block = seq.pop()
            ikiwa sio seq:
                toa self._len_to_seq[length], self._lengths[i]

        (arena, start, stop) = block
        toa self._start_to_block[(arena, start)]
        toa self._stop_to_block[(arena, stop)]
        rudisha block

    eleza _add_free_block(self, block):
        # make block available na try to merge ukijumuisha its neighbours kwenye the arena
        (arena, start, stop) = block

        jaribu:
            prev_block = self._stop_to_block[(arena, start)]
        tatizo KeyError:
            pita
        isipokua:
            start, _ = self._absorb(prev_block)

        jaribu:
            next_block = self._start_to_block[(arena, stop)]
        tatizo KeyError:
            pita
        isipokua:
            _, stop = self._absorb(next_block)

        block = (arena, start, stop)
        length = stop - start

        jaribu:
            self._len_to_seq[length].append(block)
        tatizo KeyError:
            self._len_to_seq[length] = [block]
            bisect.insort(self._lengths, length)

        self._start_to_block[(arena, start)] = block
        self._stop_to_block[(arena, stop)] = block

    eleza _absorb(self, block):
        # deregister this block so it can be merged ukijumuisha a neighbour
        (arena, start, stop) = block
        toa self._start_to_block[(arena, start)]
        toa self._stop_to_block[(arena, stop)]

        length = stop - start
        seq = self._len_to_seq[length]
        seq.remove(block)
        ikiwa sio seq:
            toa self._len_to_seq[length]
            self._lengths.remove(length)

        rudisha start, stop

    eleza _remove_allocated_block(self, block):
        arena, start, stop = block
        blocks = self._allocated_blocks[arena]
        blocks.remove((start, stop))
        ikiwa sio blocks:
            # Arena ni entirely free, discard it kutoka this process
            self._discard_arena(arena)

    eleza _free_pending_blocks(self):
        # Free all the blocks kwenye the pending list - called ukijumuisha the lock held.
        wakati Kweli:
            jaribu:
                block = self._pending_free_blocks.pop()
            tatizo IndexError:
                koma
            self._add_free_block(block)
            self._remove_allocated_block(block)

    eleza free(self, block):
        # free a block returned by malloc()
        # Since free() can be called asynchronously by the GC, it could happen
        # that it's called wakati self._lock ni held: kwenye that case,
        # self._lock.acquire() would deadlock (issue #12352). To avoid that, a
        # trylock ni used instead, na ikiwa the lock can't be acquired
        # immediately, the block ni added to a list of blocks to be freed
        # synchronously sometimes later kutoka malloc() ama free(), by calling
        # _free_pending_blocks() (appending na retrieving kutoka a list ni sio
        # strictly thread-safe but under CPython it's atomic thanks to the GIL).
        ikiwa os.getpid() != self._lastpid:
            ashiria ValueError(
                "My pid ({0:n}) ni sio last pid {1:n}".format(
                    os.getpid(),self._lastpid))
        ikiwa sio self._lock.acquire(Uongo):
            # can't acquire the lock right now, add the block to the list of
            # pending blocks to free
            self._pending_free_blocks.append(block)
        isipokua:
            # we hold the lock
            jaribu:
                self._n_frees += 1
                self._free_pending_blocks()
                self._add_free_block(block)
                self._remove_allocated_block(block)
            mwishowe:
                self._lock.release()

    eleza malloc(self, size):
        # rudisha a block of right size (possibly rounded up)
        ikiwa size < 0:
            ashiria ValueError("Size {0:n} out of range".format(size))
        ikiwa sys.maxsize <= size:
            ashiria OverflowError("Size {0:n} too large".format(size))
        ikiwa os.getpid() != self._lastpid:
            self.__init__()                     # reinitialize after fork
        ukijumuisha self._lock:
            self._n_mallocs += 1
            # allow pending blocks to be marked available
            self._free_pending_blocks()
            size = self._roundup(max(size, 1), self._alignment)
            (arena, start, stop) = self._malloc(size)
            real_stop = start + size
            ikiwa real_stop < stop:
                # ikiwa the returned block ni larger than necessary, mark
                # the remainder available
                self._add_free_block((arena, real_stop, stop))
            self._allocated_blocks[arena].add((start, real_stop))
            rudisha (arena, start, real_stop)

#
# Class wrapping a block allocated out of a Heap -- can be inherited by child process
#

kundi BufferWrapper(object):

    _heap = Heap()

    eleza __init__(self, size):
        ikiwa size < 0:
            ashiria ValueError("Size {0:n} out of range".format(size))
        ikiwa sys.maxsize <= size:
            ashiria OverflowError("Size {0:n} too large".format(size))
        block = BufferWrapper._heap.malloc(size)
        self._state = (block, size)
        util.Finalize(self, BufferWrapper._heap.free, args=(block,))

    eleza create_memoryview(self):
        (arena, start, stop), size = self._state
        rudisha memoryview(arena.buffer)[start:start+size]
