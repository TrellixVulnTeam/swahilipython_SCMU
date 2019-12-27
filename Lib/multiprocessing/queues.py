#
# Module implementing queues
#
# multiprocessing/queues.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['Queue', 'SimpleQueue', 'JoinableQueue']

agiza sys
agiza os
agiza threading
agiza collections
agiza time
agiza weakref
agiza errno

kutoka queue agiza Empty, Full

agiza _multiprocessing

kutoka . agiza connection
kutoka . agiza context
_ForkingPickler = context.reduction.ForkingPickler

kutoka .util agiza debug, info, Finalize, register_after_fork, is_exiting

#
# Queue type using a pipe, buffer and thread
#

kundi Queue(object):

    eleza __init__(self, maxsize=0, *, ctx):
        ikiwa maxsize <= 0:
            # Can raise ImportError (see issues #3770 and #23400)
            kutoka .synchronize agiza SEM_VALUE_MAX as maxsize
        self._maxsize = maxsize
        self._reader, self._writer = connection.Pipe(duplex=False)
        self._rlock = ctx.Lock()
        self._opid = os.getpid()
        ikiwa sys.platform == 'win32':
            self._wlock = None
        else:
            self._wlock = ctx.Lock()
        self._sem = ctx.BoundedSemaphore(maxsize)
        # For use by concurrent.futures
        self._ignore_epipe = False

        self._after_fork()

        ikiwa sys.platform != 'win32':
            register_after_fork(self, Queue._after_fork)

    eleza __getstate__(self):
        context.assert_spawning(self)
        rudisha (self._ignore_epipe, self._maxsize, self._reader, self._writer,
                self._rlock, self._wlock, self._sem, self._opid)

    eleza __setstate__(self, state):
        (self._ignore_epipe, self._maxsize, self._reader, self._writer,
         self._rlock, self._wlock, self._sem, self._opid) = state
        self._after_fork()

    eleza _after_fork(self):
        debug('Queue._after_fork()')
        self._notempty = threading.Condition(threading.Lock())
        self._buffer = collections.deque()
        self._thread = None
        self._jointhread = None
        self._joincancelled = False
        self._closed = False
        self._close = None
        self._send_bytes = self._writer.send_bytes
        self._recv_bytes = self._reader.recv_bytes
        self._poll = self._reader.poll

    eleza put(self, obj, block=True, timeout=None):
        ikiwa self._closed:
            raise ValueError(f"Queue {self!r} is closed")
        ikiwa not self._sem.acquire(block, timeout):
            raise Full

        with self._notempty:
            ikiwa self._thread is None:
                self._start_thread()
            self._buffer.append(obj)
            self._notempty.notify()

    eleza get(self, block=True, timeout=None):
        ikiwa self._closed:
            raise ValueError(f"Queue {self!r} is closed")
        ikiwa block and timeout is None:
            with self._rlock:
                res = self._recv_bytes()
            self._sem.release()
        else:
            ikiwa block:
                deadline = time.monotonic() + timeout
            ikiwa not self._rlock.acquire(block, timeout):
                raise Empty
            try:
                ikiwa block:
                    timeout = deadline - time.monotonic()
                    ikiwa not self._poll(timeout):
                        raise Empty
                elikiwa not self._poll():
                    raise Empty
                res = self._recv_bytes()
                self._sem.release()
            finally:
                self._rlock.release()
        # unserialize the data after having released the lock
        rudisha _ForkingPickler.loads(res)

    eleza qsize(self):
        # Raises NotImplementedError on Mac OSX because of broken sem_getvalue()
        rudisha self._maxsize - self._sem._semlock._get_value()

    eleza empty(self):
        rudisha not self._poll()

    eleza full(self):
        rudisha self._sem._semlock._is_zero()

    eleza get_nowait(self):
        rudisha self.get(False)

    eleza put_nowait(self, obj):
        rudisha self.put(obj, False)

    eleza close(self):
        self._closed = True
        try:
            self._reader.close()
        finally:
            close = self._close
            ikiwa close:
                self._close = None
                close()

    eleza join_thread(self):
        debug('Queue.join_thread()')
        assert self._closed, "Queue {0!r} not closed".format(self)
        ikiwa self._jointhread:
            self._jointhread()

    eleza cancel_join_thread(self):
        debug('Queue.cancel_join_thread()')
        self._joincancelled = True
        try:
            self._jointhread.cancel()
        except AttributeError:
            pass

    eleza _start_thread(self):
        debug('Queue._start_thread()')

        # Start thread which transfers data kutoka buffer to pipe
        self._buffer.clear()
        self._thread = threading.Thread(
            target=Queue._feed,
            args=(self._buffer, self._notempty, self._send_bytes,
                  self._wlock, self._writer.close, self._ignore_epipe,
                  self._on_queue_feeder_error, self._sem),
            name='QueueFeederThread'
        )
        self._thread.daemon = True

        debug('doing self._thread.start()')
        self._thread.start()
        debug('... done self._thread.start()')

        ikiwa not self._joincancelled:
            self._jointhread = Finalize(
                self._thread, Queue._finalize_join,
                [weakref.ref(self._thread)],
                exitpriority=-5
                )

        # Send sentinel to the thread queue object when garbage collected
        self._close = Finalize(
            self, Queue._finalize_close,
            [self._buffer, self._notempty],
            exitpriority=10
            )

    @staticmethod
    eleza _finalize_join(twr):
        debug('joining queue thread')
        thread = twr()
        ikiwa thread is not None:
            thread.join()
            debug('... queue thread joined')
        else:
            debug('... queue thread already dead')

    @staticmethod
    eleza _finalize_close(buffer, notempty):
        debug('telling queue thread to quit')
        with notempty:
            buffer.append(_sentinel)
            notempty.notify()

    @staticmethod
    eleza _feed(buffer, notempty, send_bytes, writelock, close, ignore_epipe,
              onerror, queue_sem):
        debug('starting thread to feed data to pipe')
        nacquire = notempty.acquire
        nrelease = notempty.release
        nwait = notempty.wait
        bpopleft = buffer.popleft
        sentinel = _sentinel
        ikiwa sys.platform != 'win32':
            wacquire = writelock.acquire
            wrelease = writelock.release
        else:
            wacquire = None

        while 1:
            try:
                nacquire()
                try:
                    ikiwa not buffer:
                        nwait()
                finally:
                    nrelease()
                try:
                    while 1:
                        obj = bpopleft()
                        ikiwa obj is sentinel:
                            debug('feeder thread got sentinel -- exiting')
                            close()
                            return

                        # serialize the data before acquiring the lock
                        obj = _ForkingPickler.dumps(obj)
                        ikiwa wacquire is None:
                            send_bytes(obj)
                        else:
                            wacquire()
                            try:
                                send_bytes(obj)
                            finally:
                                wrelease()
                except IndexError:
                    pass
            except Exception as e:
                ikiwa ignore_epipe and getattr(e, 'errno', 0) == errno.EPIPE:
                    return
                # Since this runs in a daemon thread the resources it uses
                # may be become unusable while the process is cleaning up.
                # We ignore errors which happen after the process has
                # started to cleanup.
                ikiwa is_exiting():
                    info('error in queue thread: %s', e)
                    return
                else:
                    # Since the object has not been sent in the queue, we need
                    # to decrease the size of the queue. The error acts as
                    # ikiwa the object had been silently removed kutoka the queue
                    # and this step is necessary to have a properly working
                    # queue.
                    queue_sem.release()
                    onerror(e, obj)

    @staticmethod
    eleza _on_queue_feeder_error(e, obj):
        """
        Private API hook called when feeding data in the background thread
        raises an exception.  For overriding by concurrent.futures.
        """
        agiza traceback
        traceback.print_exc()


_sentinel = object()

#
# A queue type which also supports join() and task_done() methods
#
# Note that ikiwa you do not call task_done() for each finished task then
# eventually the counter's semaphore may overflow causing Bad Things
# to happen.
#

kundi JoinableQueue(Queue):

    eleza __init__(self, maxsize=0, *, ctx):
        Queue.__init__(self, maxsize, ctx=ctx)
        self._unfinished_tasks = ctx.Semaphore(0)
        self._cond = ctx.Condition()

    eleza __getstate__(self):
        rudisha Queue.__getstate__(self) + (self._cond, self._unfinished_tasks)

    eleza __setstate__(self, state):
        Queue.__setstate__(self, state[:-2])
        self._cond, self._unfinished_tasks = state[-2:]

    eleza put(self, obj, block=True, timeout=None):
        ikiwa self._closed:
            raise ValueError(f"Queue {self!r} is closed")
        ikiwa not self._sem.acquire(block, timeout):
            raise Full

        with self._notempty, self._cond:
            ikiwa self._thread is None:
                self._start_thread()
            self._buffer.append(obj)
            self._unfinished_tasks.release()
            self._notempty.notify()

    eleza task_done(self):
        with self._cond:
            ikiwa not self._unfinished_tasks.acquire(False):
                raise ValueError('task_done() called too many times')
            ikiwa self._unfinished_tasks._semlock._is_zero():
                self._cond.notify_all()

    eleza join(self):
        with self._cond:
            ikiwa not self._unfinished_tasks._semlock._is_zero():
                self._cond.wait()

#
# Simplified Queue type -- really just a locked pipe
#

kundi SimpleQueue(object):

    eleza __init__(self, *, ctx):
        self._reader, self._writer = connection.Pipe(duplex=False)
        self._rlock = ctx.Lock()
        self._poll = self._reader.poll
        ikiwa sys.platform == 'win32':
            self._wlock = None
        else:
            self._wlock = ctx.Lock()

    eleza empty(self):
        rudisha not self._poll()

    eleza __getstate__(self):
        context.assert_spawning(self)
        rudisha (self._reader, self._writer, self._rlock, self._wlock)

    eleza __setstate__(self, state):
        (self._reader, self._writer, self._rlock, self._wlock) = state
        self._poll = self._reader.poll

    eleza get(self):
        with self._rlock:
            res = self._reader.recv_bytes()
        # unserialize the data after having released the lock
        rudisha _ForkingPickler.loads(res)

    eleza put(self, obj):
        # serialize the data before acquiring the lock
        obj = _ForkingPickler.dumps(obj)
        ikiwa self._wlock is None:
            # writes to a message oriented win32 pipe are atomic
            self._writer.send_bytes(obj)
        else:
            with self._wlock:
                self._writer.send_bytes(obj)
