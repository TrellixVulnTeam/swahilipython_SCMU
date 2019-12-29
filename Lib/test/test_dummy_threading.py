kutoka test agiza support
agiza unittest
agiza dummy_threading kama _threading
agiza time

kundi DummyThreadingTestCase(unittest.TestCase):

    kundi TestThread(_threading.Thread):

        eleza run(self):
            global running
            global sema
            global mutex
            # Uncomment ikiwa testing another module, such kama the real 'threading'
            # module.
            #delay = random.random() * 2
            delay = 0
            ikiwa support.verbose:
                andika('task', self.name, 'will run for', delay, 'sec')
            sema.acquire()
            mutex.acquire()
            running += 1
            ikiwa support.verbose:
                andika(running, 'tasks are running')
            mutex.release()
            time.sleep(delay)
            ikiwa support.verbose:
                andika('task', self.name, 'done')
            mutex.acquire()
            running -= 1
            ikiwa support.verbose:
                andika(self.name, 'is finished.', running, 'tasks are running')
            mutex.release()
            sema.release()

    eleza setUp(self):
        self.numtasks = 10
        global sema
        sema = _threading.BoundedSemaphore(value=3)
        global mutex
        mutex = _threading.RLock()
        global running
        running = 0
        self.threads = []

    eleza test_tasks(self):
        kila i kwenye range(self.numtasks):
            t = self.TestThread(name="<thread %d>"%i)
            self.threads.append(t)
            t.start()

        ikiwa support.verbose:
            andika('waiting kila all tasks to complete')
        kila t kwenye self.threads:
            t.join()
        ikiwa support.verbose:
            andika('all tasks done')

ikiwa __name__ == '__main__':
    unittest.main()
