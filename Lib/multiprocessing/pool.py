#
# Module providing the `Pool` kundi kila managing a process pool
#
# multiprocessing/pool.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = ['Pool', 'ThreadPool']

#
# Imports
#

agiza collections
agiza itertools
agiza os
agiza queue
agiza threading
agiza time
agiza traceback
agiza warnings
kutoka queue agiza Empty

# If threading ni available then ThreadPool should be provided.  Therefore
# we avoid top-level imports which are liable to fail on some systems.
kutoka . agiza util
kutoka . agiza get_context, TimeoutError
kutoka .connection agiza wait

#
# Constants representing the state of a pool
#

INIT = "INIT"
RUN = "RUN"
CLOSE = "CLOSE"
TERMINATE = "TERMINATE"

#
# Miscellaneous
#

job_counter = itertools.count()

eleza mapstar(args):
    rudisha list(map(*args))

eleza starmapstar(args):
    rudisha list(itertools.starmap(args[0], args[1]))

#
# Hack to embed stringification of remote traceback kwenye local traceback
#

kundi RemoteTraceback(Exception):
    eleza __init__(self, tb):
        self.tb = tb
    eleza __str__(self):
        rudisha self.tb

kundi ExceptionWithTraceback:
    eleza __init__(self, exc, tb):
        tb = traceback.format_exception(type(exc), exc, tb)
        tb = ''.join(tb)
        self.exc = exc
        self.tb = '\n"""\n%s"""' % tb
    eleza __reduce__(self):
        rudisha rebuild_exc, (self.exc, self.tb)

eleza rebuild_exc(exc, tb):
    exc.__cause__ = RemoteTraceback(tb)
    rudisha exc

#
# Code run by worker processes
#

kundi MaybeEncodingError(Exception):
    """Wraps possible unpickleable errors, so they can be
    safely sent through the socket."""

    eleza __init__(self, exc, value):
        self.exc = repr(exc)
        self.value = repr(value)
        super(MaybeEncodingError, self).__init__(self.exc, self.value)

    eleza __str__(self):
        rudisha "Error sending result: '%s'. Reason: '%s'" % (self.value,
                                                             self.exc)

    eleza __repr__(self):
        rudisha "<%s: %s>" % (self.__class__.__name__, self)


eleza worker(inqueue, outqueue, initializer=Tupu, initargs=(), maxtasks=Tupu,
           wrap_exception=Uongo):
    ikiwa (maxtasks ni sio Tupu) na sio (isinstance(maxtasks, int)
                                       na maxtasks >= 1):
         ashiria AssertionError("Maxtasks {!r} ni sio valid".format(maxtasks))
    put = outqueue.put
    get = inqueue.get
    ikiwa hasattr(inqueue, '_writer'):
        inqueue._writer.close()
        outqueue._reader.close()

    ikiwa initializer ni sio Tupu:
        initializer(*initargs)

    completed = 0
    wakati maxtasks ni Tupu ama (maxtasks na completed < maxtasks):
        jaribu:
            task = get()
        except (EOFError, OSError):
            util.debug('worker got EOFError ama OSError -- exiting')
            koma

        ikiwa task ni Tupu:
            util.debug('worker got sentinel -- exiting')
            koma

        job, i, func, args, kwds = task
        jaribu:
            result = (Kweli, func(*args, **kwds))
        except Exception as e:
            ikiwa wrap_exception na func ni sio _helper_reraises_exception:
                e = ExceptionWithTraceback(e, e.__traceback__)
            result = (Uongo, e)
        jaribu:
            put((job, i, result))
        except Exception as e:
            wrapped = MaybeEncodingError(e, result[1])
            util.debug("Possible encoding error wakati sending result: %s" % (
                wrapped))
            put((job, i, (Uongo, wrapped)))

        task = job = result = func = args = kwds = Tupu
        completed += 1
    util.debug('worker exiting after %d tasks' % completed)

eleza _helper_reraises_exception(ex):
    'Pickle-able helper function kila use by _guarded_task_generation.'
     ashiria ex

#
# Class representing a process pool
#

kundi _PoolCache(dict):
    """
    Class that implements a cache kila the Pool kundi that will notify
    the pool management threads every time the cache ni emptied. The
    notification ni done by the use of a queue that ni provided when
    instantiating the cache.
    """
    eleza __init__(self, /, *args, notifier=Tupu, **kwds):
        self.notifier = notifier
        super().__init__(*args, **kwds)

    eleza __delitem__(self, item):
        super().__delitem__(item)

        # Notify that the cache ni empty. This ni important because the
        # pool keeps maintaining workers until the cache gets drained. This
        # eliminates a race condition kwenye which a task ni finished after the
        # the pool's _handle_workers method has enter another iteration of the
        # loop. In this situation, the only event that can wake up the pool
        # ni the cache to be emptied (no more tasks available).
        ikiwa sio self:
            self.notifier.put(Tupu)

kundi Pool(object):
    '''
    Class which supports an async version of applying functions to arguments.
    '''
    _wrap_exception = Kweli

    @staticmethod
    eleza Process(ctx, *args, **kwds):
        rudisha ctx.Process(*args, **kwds)

    eleza __init__(self, processes=Tupu, initializer=Tupu, initargs=(),
                 maxtasksperchild=Tupu, context=Tupu):
        # Attributes initialized early to make sure that they exist in
        # __del__() ikiwa __init__() raises an exception
        self._pool = []
        self._state = INIT

        self._ctx = context ama get_context()
        self._setup_queues()
        self._taskqueue = queue.SimpleQueue()
        # The _change_notifier queue exist to wake up self._handle_workers()
        # when the cache (self._cache) ni empty ama when there ni a change in
        # the _state variable of the thread that runs _handle_workers.
        self._change_notifier = self._ctx.SimpleQueue()
        self._cache = _PoolCache(notifier=self._change_notifier)
        self._maxtasksperchild = maxtasksperchild
        self._initializer = initializer
        self._initargs = initargs

        ikiwa processes ni Tupu:
            processes = os.cpu_count() ama 1
        ikiwa processes < 1:
             ashiria ValueError("Number of processes must be at least 1")

        ikiwa initializer ni sio Tupu na sio callable(initializer):
             ashiria TypeError('initializer must be a callable')

        self._processes = processes
        jaribu:
            self._repopulate_pool()
        except Exception:
            kila p kwenye self._pool:
                ikiwa p.exitcode ni Tupu:
                    p.terminate()
            kila p kwenye self._pool:
                p.join()
            raise

        sentinels = self._get_sentinels()

        self._worker_handler = threading.Thread(
            target=Pool._handle_workers,
            args=(self._cache, self._taskqueue, self._ctx, self.Process,
                  self._processes, self._pool, self._inqueue, self._outqueue,
                  self._initializer, self._initargs, self._maxtasksperchild,
                  self._wrap_exception, sentinels, self._change_notifier)
            )
        self._worker_handler.daemon = Kweli
        self._worker_handler._state = RUN
        self._worker_handler.start()


        self._task_handler = threading.Thread(
            target=Pool._handle_tasks,
            args=(self._taskqueue, self._quick_put, self._outqueue,
                  self._pool, self._cache)
            )
        self._task_handler.daemon = Kweli
        self._task_handler._state = RUN
        self._task_handler.start()

        self._result_handler = threading.Thread(
            target=Pool._handle_results,
            args=(self._outqueue, self._quick_get, self._cache)
            )
        self._result_handler.daemon = Kweli
        self._result_handler._state = RUN
        self._result_handler.start()

        self._terminate = util.Finalize(
            self, self._terminate_pool,
            args=(self._taskqueue, self._inqueue, self._outqueue, self._pool,
                  self._change_notifier, self._worker_handler, self._task_handler,
                  self._result_handler, self._cache),
            exitpriority=15
            )
        self._state = RUN

    # Copy globals as function locals to make sure that they are available
    # during Python shutdown when the Pool ni destroyed.
    eleza __del__(self, _warn=warnings.warn, RUN=RUN):
        ikiwa self._state == RUN:
            _warn(f"unclosed running multiprocessing pool {self!r}",
                  ResourceWarning, source=self)
            ikiwa getattr(self, '_change_notifier', Tupu) ni sio Tupu:
                self._change_notifier.put(Tupu)

    eleza __repr__(self):
        cls = self.__class__
        rudisha (f'<{cls.__module__}.{cls.__qualname__} '
                f'state={self._state} '
                f'pool_size={len(self._pool)}>')

    eleza _get_sentinels(self):
        task_queue_sentinels = [self._outqueue._reader]
        self_notifier_sentinels = [self._change_notifier._reader]
        rudisha [*task_queue_sentinels, *self_notifier_sentinels]

    @staticmethod
    eleza _get_worker_sentinels(workers):
        rudisha [worker.sentinel kila worker in
                workers ikiwa hasattr(worker, "sentinel")]

    @staticmethod
    eleza _join_exited_workers(pool):
        """Cleanup after any worker processes which have exited due to reaching
        their specified lifetime.  Returns Kweli ikiwa any workers were cleaned up.
        """
        cleaned = Uongo
        kila i kwenye reversed(range(len(pool))):
            worker = pool[i]
            ikiwa worker.exitcode ni sio Tupu:
                # worker exited
                util.debug('cleaning up worker %d' % i)
                worker.join()
                cleaned = Kweli
                toa pool[i]
        rudisha cleaned

    eleza _repopulate_pool(self):
        rudisha self._repopulate_pool_static(self._ctx, self.Process,
                                            self._processes,
                                            self._pool, self._inqueue,
                                            self._outqueue, self._initializer,
                                            self._initargs,
                                            self._maxtasksperchild,
                                            self._wrap_exception)

    @staticmethod
    eleza _repopulate_pool_static(ctx, Process, processes, pool, inqueue,
                                outqueue, initializer, initargs,
                                maxtasksperchild, wrap_exception):
        """Bring the number of pool processes up to the specified number,
        kila use after reaping workers which have exited.
        """
        kila i kwenye range(processes - len(pool)):
            w = Process(ctx, target=worker,
                        args=(inqueue, outqueue,
                              initializer,
                              initargs, maxtasksperchild,
                              wrap_exception))
            w.name = w.name.replace('Process', 'PoolWorker')
            w.daemon = Kweli
            w.start()
            pool.append(w)
            util.debug('added worker')

    @staticmethod
    eleza _maintain_pool(ctx, Process, processes, pool, inqueue, outqueue,
                       initializer, initargs, maxtasksperchild,
                       wrap_exception):
        """Clean up any exited workers na start replacements kila them.
        """
        ikiwa Pool._join_exited_workers(pool):
            Pool._repopulate_pool_static(ctx, Process, processes, pool,
                                         inqueue, outqueue, initializer,
                                         initargs, maxtasksperchild,
                                         wrap_exception)

    eleza _setup_queues(self):
        self._inqueue = self._ctx.SimpleQueue()
        self._outqueue = self._ctx.SimpleQueue()
        self._quick_put = self._inqueue._writer.send
        self._quick_get = self._outqueue._reader.recv

    eleza _check_running(self):
        ikiwa self._state != RUN:
             ashiria ValueError("Pool sio running")

    eleza apply(self, func, args=(), kwds={}):
        '''
        Equivalent of `func(*args, **kwds)`.
        Pool must be running.
        '''
        rudisha self.apply_async(func, args, kwds).get()

    eleza map(self, func, iterable, chunksize=Tupu):
        '''
        Apply `func` to each element kwenye `iterable`, collecting the results
        kwenye a list that ni returned.
        '''
        rudisha self._map_async(func, iterable, mapstar, chunksize).get()

    eleza starmap(self, func, iterable, chunksize=Tupu):
        '''
        Like `map()` method but the elements of the `iterable` are expected to
        be iterables as well na will be unpacked as arguments. Hence
        `func` na (a, b) becomes func(a, b).
        '''
        rudisha self._map_async(func, iterable, starmapstar, chunksize).get()

    eleza starmap_async(self, func, iterable, chunksize=Tupu, callback=Tupu,
            error_callback=Tupu):
        '''
        Asynchronous version of `starmap()` method.
        '''
        rudisha self._map_async(func, iterable, starmapstar, chunksize,
                               callback, error_callback)

    eleza _guarded_task_generation(self, result_job, func, iterable):
        '''Provides a generator of tasks kila imap na imap_unordered with
        appropriate handling kila iterables which throw exceptions during
        iteration.'''
        jaribu:
            i = -1
            kila i, x kwenye enumerate(iterable):
                tuma (result_job, i, func, (x,), {})
        except Exception as e:
            tuma (result_job, i+1, _helper_reraises_exception, (e,), {})

    eleza imap(self, func, iterable, chunksize=1):
        '''
        Equivalent of `map()` -- can be MUCH slower than `Pool.map()`.
        '''
        self._check_running()
        ikiwa chunksize == 1:
            result = IMapIterator(self)
            self._taskqueue.put(
                (
                    self._guarded_task_generation(result._job, func, iterable),
                    result._set_length
                ))
            rudisha result
        isipokua:
            ikiwa chunksize < 1:
                 ashiria ValueError(
                    "Chunksize must be 1+, sio {0:n}".format(
                        chunksize))
            task_batches = Pool._get_tasks(func, iterable, chunksize)
            result = IMapIterator(self)
            self._taskqueue.put(
                (
                    self._guarded_task_generation(result._job,
                                                  mapstar,
                                                  task_batches),
                    result._set_length
                ))
            rudisha (item kila chunk kwenye result kila item kwenye chunk)

    eleza imap_unordered(self, func, iterable, chunksize=1):
        '''
        Like `imap()` method but ordering of results ni arbitrary.
        '''
        self._check_running()
        ikiwa chunksize == 1:
            result = IMapUnorderedIterator(self)
            self._taskqueue.put(
                (
                    self._guarded_task_generation(result._job, func, iterable),
                    result._set_length
                ))
            rudisha result
        isipokua:
            ikiwa chunksize < 1:
                 ashiria ValueError(
                    "Chunksize must be 1+, sio {0!r}".format(chunksize))
            task_batches = Pool._get_tasks(func, iterable, chunksize)
            result = IMapUnorderedIterator(self)
            self._taskqueue.put(
                (
                    self._guarded_task_generation(result._job,
                                                  mapstar,
                                                  task_batches),
                    result._set_length
                ))
            rudisha (item kila chunk kwenye result kila item kwenye chunk)

    eleza apply_async(self, func, args=(), kwds={}, callback=Tupu,
            error_callback=Tupu):
        '''
        Asynchronous version of `apply()` method.
        '''
        self._check_running()
        result = ApplyResult(self, callback, error_callback)
        self._taskqueue.put(([(result._job, 0, func, args, kwds)], Tupu))
        rudisha result

    eleza map_async(self, func, iterable, chunksize=Tupu, callback=Tupu,
            error_callback=Tupu):
        '''
        Asynchronous version of `map()` method.
        '''
        rudisha self._map_async(func, iterable, mapstar, chunksize, callback,
            error_callback)

    eleza _map_async(self, func, iterable, mapper, chunksize=Tupu, callback=Tupu,
            error_callback=Tupu):
        '''
        Helper function to implement map, starmap na their async counterparts.
        '''
        self._check_running()
        ikiwa sio hasattr(iterable, '__len__'):
            iterable = list(iterable)

        ikiwa chunksize ni Tupu:
            chunksize, extra = divmod(len(iterable), len(self._pool) * 4)
            ikiwa extra:
                chunksize += 1
        ikiwa len(iterable) == 0:
            chunksize = 0

        task_batches = Pool._get_tasks(func, iterable, chunksize)
        result = MapResult(self, chunksize, len(iterable), callback,
                           error_callback=error_callback)
        self._taskqueue.put(
            (
                self._guarded_task_generation(result._job,
                                              mapper,
                                              task_batches),
                Tupu
            )
        )
        rudisha result

    @staticmethod
    eleza _wait_for_updates(sentinels, change_notifier, timeout=Tupu):
        wait(sentinels, timeout=timeout)
        wakati sio change_notifier.empty():
            change_notifier.get()

    @classmethod
    eleza _handle_workers(cls, cache, taskqueue, ctx, Process, processes,
                        pool, inqueue, outqueue, initializer, initargs,
                        maxtasksperchild, wrap_exception, sentinels,
                        change_notifier):
        thread = threading.current_thread()

        # Keep maintaining workers until the cache gets drained, unless the pool
        # ni terminated.
        wakati thread._state == RUN ama (cache na thread._state != TERMINATE):
            cls._maintain_pool(ctx, Process, processes, pool, inqueue,
                               outqueue, initializer, initargs,
                               maxtasksperchild, wrap_exception)

            current_sentinels = [*cls._get_worker_sentinels(pool), *sentinels]

            cls._wait_for_updates(current_sentinels, change_notifier)
        # send sentinel to stop workers
        taskqueue.put(Tupu)
        util.debug('worker handler exiting')

    @staticmethod
    eleza _handle_tasks(taskqueue, put, outqueue, pool, cache):
        thread = threading.current_thread()

        kila taskseq, set_length kwenye iter(taskqueue.get, Tupu):
            task = Tupu
            jaribu:
                # iterating taskseq cannot fail
                kila task kwenye taskseq:
                    ikiwa thread._state != RUN:
                        util.debug('task handler found thread._state != RUN')
                        koma
                    jaribu:
                        put(task)
                    except Exception as e:
                        job, idx = task[:2]
                        jaribu:
                            cache[job]._set(idx, (Uongo, e))
                        except KeyError:
                            pass
                isipokua:
                    ikiwa set_length:
                        util.debug('doing set_length()')
                        idx = task[1] ikiwa task isipokua -1
                        set_length(idx + 1)
                    endelea
                koma
            mwishowe:
                task = taskseq = job = Tupu
        isipokua:
            util.debug('task handler got sentinel')

        jaribu:
            # tell result handler to finish when cache ni empty
            util.debug('task handler sending sentinel to result handler')
            outqueue.put(Tupu)

            # tell workers there ni no more work
            util.debug('task handler sending sentinel to workers')
            kila p kwenye pool:
                put(Tupu)
        except OSError:
            util.debug('task handler got OSError when sending sentinels')

        util.debug('task handler exiting')

    @staticmethod
    eleza _handle_results(outqueue, get, cache):
        thread = threading.current_thread()

        wakati 1:
            jaribu:
                task = get()
            except (OSError, EOFError):
                util.debug('result handler got EOFError/OSError -- exiting')
                return

            ikiwa thread._state != RUN:
                assert thread._state == TERMINATE, "Thread sio kwenye TERMINATE"
                util.debug('result handler found thread._state=TERMINATE')
                koma

            ikiwa task ni Tupu:
                util.debug('result handler got sentinel')
                koma

            job, i, obj = task
            jaribu:
                cache[job]._set(i, obj)
            except KeyError:
                pass
            task = job = obj = Tupu

        wakati cache na thread._state != TERMINATE:
            jaribu:
                task = get()
            except (OSError, EOFError):
                util.debug('result handler got EOFError/OSError -- exiting')
                return

            ikiwa task ni Tupu:
                util.debug('result handler ignoring extra sentinel')
                endelea
            job, i, obj = task
            jaribu:
                cache[job]._set(i, obj)
            except KeyError:
                pass
            task = job = obj = Tupu

        ikiwa hasattr(outqueue, '_reader'):
            util.debug('ensuring that outqueue ni sio full')
            # If we don't make room available kwenye outqueue then
            # attempts to add the sentinel (Tupu) to outqueue may
            # block.  There ni guaranteed to be no more than 2 sentinels.
            jaribu:
                kila i kwenye range(10):
                    ikiwa sio outqueue._reader.poll():
                        koma
                    get()
            except (OSError, EOFError):
                pass

        util.debug('result handler exiting: len(cache)=%s, thread._state=%s',
              len(cache), thread._state)

    @staticmethod
    eleza _get_tasks(func, it, size):
        it = iter(it)
        wakati 1:
            x = tuple(itertools.islice(it, size))
            ikiwa sio x:
                return
            tuma (func, x)

    eleza __reduce__(self):
         ashiria NotImplementedError(
              'pool objects cannot be passed between processes ama pickled'
              )

    eleza close(self):
        util.debug('closing pool')
        ikiwa self._state == RUN:
            self._state = CLOSE
            self._worker_handler._state = CLOSE
            self._change_notifier.put(Tupu)

    eleza terminate(self):
        util.debug('terminating pool')
        self._state = TERMINATE
        self._worker_handler._state = TERMINATE
        self._change_notifier.put(Tupu)
        self._terminate()

    eleza join(self):
        util.debug('joining pool')
        ikiwa self._state == RUN:
             ashiria ValueError("Pool ni still running")
        elikiwa self._state sio kwenye (CLOSE, TERMINATE):
             ashiria ValueError("In unknown state")
        self._worker_handler.join()
        self._task_handler.join()
        self._result_handler.join()
        kila p kwenye self._pool:
            p.join()

    @staticmethod
    eleza _help_stuff_finish(inqueue, task_handler, size):
        # task_handler may be blocked trying to put items on inqueue
        util.debug('removing tasks kutoka inqueue until task handler finished')
        inqueue._rlock.acquire()
        wakati task_handler.is_alive() na inqueue._reader.poll():
            inqueue._reader.recv()
            time.sleep(0)

    @classmethod
    eleza _terminate_pool(cls, taskqueue, inqueue, outqueue, pool, change_notifier,
                        worker_handler, task_handler, result_handler, cache):
        # this ni guaranteed to only be called once
        util.debug('finalizing pool')

        worker_handler._state = TERMINATE
        task_handler._state = TERMINATE

        util.debug('helping task handler/workers to finish')
        cls._help_stuff_finish(inqueue, task_handler, len(pool))

        ikiwa (not result_handler.is_alive()) na (len(cache) != 0):
             ashiria AssertionError(
                "Cannot have cache ukijumuisha result_hander sio alive")

        result_handler._state = TERMINATE
        change_notifier.put(Tupu)
        outqueue.put(Tupu)                  # sentinel

        # We must wait kila the worker handler to exit before terminating
        # workers because we don't want workers to be restarted behind our back.
        util.debug('joining worker handler')
        ikiwa threading.current_thread() ni sio worker_handler:
            worker_handler.join()

        # Terminate workers which haven't already finished.
        ikiwa pool na hasattr(pool[0], 'terminate'):
            util.debug('terminating workers')
            kila p kwenye pool:
                ikiwa p.exitcode ni Tupu:
                    p.terminate()

        util.debug('joining task handler')
        ikiwa threading.current_thread() ni sio task_handler:
            task_handler.join()

        util.debug('joining result handler')
        ikiwa threading.current_thread() ni sio result_handler:
            result_handler.join()

        ikiwa pool na hasattr(pool[0], 'terminate'):
            util.debug('joining pool workers')
            kila p kwenye pool:
                ikiwa p.is_alive():
                    # worker has sio yet exited
                    util.debug('cleaning up worker %d' % p.pid)
                    p.join()

    eleza __enter__(self):
        self._check_running()
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

#
# Class whose instances are returned by `Pool.apply_async()`
#

kundi ApplyResult(object):

    eleza __init__(self, pool, callback, error_callback):
        self._pool = pool
        self._event = threading.Event()
        self._job = next(job_counter)
        self._cache = pool._cache
        self._callback = callback
        self._error_callback = error_callback
        self._cache[self._job] = self

    eleza ready(self):
        rudisha self._event.is_set()

    eleza successful(self):
        ikiwa sio self.ready():
             ashiria ValueError("{0!r} sio ready".format(self))
        rudisha self._success

    eleza wait(self, timeout=Tupu):
        self._event.wait(timeout)

    eleza get(self, timeout=Tupu):
        self.wait(timeout)
        ikiwa sio self.ready():
             ashiria TimeoutError
        ikiwa self._success:
            rudisha self._value
        isipokua:
             ashiria self._value

    eleza _set(self, i, obj):
        self._success, self._value = obj
        ikiwa self._callback na self._success:
            self._callback(self._value)
        ikiwa self._error_callback na sio self._success:
            self._error_callback(self._value)
        self._event.set()
        toa self._cache[self._job]
        self._pool = Tupu

AsyncResult = ApplyResult       # create alias -- see #17805

#
# Class whose instances are returned by `Pool.map_async()`
#

kundi MapResult(ApplyResult):

    eleza __init__(self, pool, chunksize, length, callback, error_callback):
        ApplyResult.__init__(self, pool, callback,
                             error_callback=error_callback)
        self._success = Kweli
        self._value = [Tupu] * length
        self._chunksize = chunksize
        ikiwa chunksize <= 0:
            self._number_left = 0
            self._event.set()
            toa self._cache[self._job]
        isipokua:
            self._number_left = length//chunksize + bool(length % chunksize)

    eleza _set(self, i, success_result):
        self._number_left -= 1
        success, result = success_result
        ikiwa success na self._success:
            self._value[i*self._chunksize:(i+1)*self._chunksize] = result
            ikiwa self._number_left == 0:
                ikiwa self._callback:
                    self._callback(self._value)
                toa self._cache[self._job]
                self._event.set()
                self._pool = Tupu
        isipokua:
            ikiwa sio success na self._success:
                # only store first exception
                self._success = Uongo
                self._value = result
            ikiwa self._number_left == 0:
                # only consider the result ready once all jobs are done
                ikiwa self._error_callback:
                    self._error_callback(self._value)
                toa self._cache[self._job]
                self._event.set()
                self._pool = Tupu

#
# Class whose instances are returned by `Pool.imap()`
#

kundi IMapIterator(object):

    eleza __init__(self, pool):
        self._pool = pool
        self._cond = threading.Condition(threading.Lock())
        self._job = next(job_counter)
        self._cache = pool._cache
        self._items = collections.deque()
        self._index = 0
        self._length = Tupu
        self._unsorted = {}
        self._cache[self._job] = self

    eleza __iter__(self):
        rudisha self

    eleza next(self, timeout=Tupu):
        ukijumuisha self._cond:
            jaribu:
                item = self._items.popleft()
            except IndexError:
                ikiwa self._index == self._length:
                    self._pool = Tupu
                     ashiria StopIteration kutoka Tupu
                self._cond.wait(timeout)
                jaribu:
                    item = self._items.popleft()
                except IndexError:
                    ikiwa self._index == self._length:
                        self._pool = Tupu
                         ashiria StopIteration kutoka Tupu
                     ashiria TimeoutError kutoka Tupu

        success, value = item
        ikiwa success:
            rudisha value
         ashiria value

    __next__ = next                    # XXX

    eleza _set(self, i, obj):
        ukijumuisha self._cond:
            ikiwa self._index == i:
                self._items.append(obj)
                self._index += 1
                wakati self._index kwenye self._unsorted:
                    obj = self._unsorted.pop(self._index)
                    self._items.append(obj)
                    self._index += 1
                self._cond.notify()
            isipokua:
                self._unsorted[i] = obj

            ikiwa self._index == self._length:
                toa self._cache[self._job]
                self._pool = Tupu

    eleza _set_length(self, length):
        ukijumuisha self._cond:
            self._length = length
            ikiwa self._index == self._length:
                self._cond.notify()
                toa self._cache[self._job]
                self._pool = Tupu

#
# Class whose instances are returned by `Pool.imap_unordered()`
#

kundi IMapUnorderedIterator(IMapIterator):

    eleza _set(self, i, obj):
        ukijumuisha self._cond:
            self._items.append(obj)
            self._index += 1
            self._cond.notify()
            ikiwa self._index == self._length:
                toa self._cache[self._job]
                self._pool = Tupu

#
#
#

kundi ThreadPool(Pool):
    _wrap_exception = Uongo

    @staticmethod
    eleza Process(ctx, *args, **kwds):
        kutoka .dummy agiza Process
        rudisha Process(*args, **kwds)

    eleza __init__(self, processes=Tupu, initializer=Tupu, initargs=()):
        Pool.__init__(self, processes, initializer, initargs)

    eleza _setup_queues(self):
        self._inqueue = queue.SimpleQueue()
        self._outqueue = queue.SimpleQueue()
        self._quick_put = self._inqueue.put
        self._quick_get = self._outqueue.get

    eleza _get_sentinels(self):
        rudisha [self._change_notifier._reader]

    @staticmethod
    eleza _get_worker_sentinels(workers):
        rudisha []

    @staticmethod
    eleza _help_stuff_finish(inqueue, task_handler, size):
        # drain inqueue, na put sentinels at its head to make workers finish
        jaribu:
            wakati Kweli:
                inqueue.get(block=Uongo)
        except queue.Empty:
            pass
        kila i kwenye range(size):
            inqueue.put(Tupu)

    eleza _wait_for_updates(self, sentinels, change_notifier, timeout):
        time.sleep(timeout)
