"""This test case provides support for checking forking and wait behavior.

To test different wait behavior, override the wait_impl method.

We want fork1() semantics -- only the forking thread survives in the
child after a fork().

On some systems (e.g. Solaris without posix threads) we find that all
active threads survive in the child after a fork(); this is an error.
"""

agiza os, sys, time, unittest
agiza threading
agiza test.support as support


LONGSLEEP = 2
SHORTSLEEP = 0.5
NUM_THREADS = 4

kundi ForkWait(unittest.TestCase):

    eleza setUp(self):
        self._threading_key = support.threading_setup()
        self.alive = {}
        self.stop = 0
        self.threads = []

    eleza tearDown(self):
        # Stop threads
        self.stop = 1
        for thread in self.threads:
            thread.join()
        thread = None
        self.threads.clear()
        support.threading_cleanup(*self._threading_key)

    eleza f(self, id):
        while not self.stop:
            self.alive[id] = os.getpid()
            try:
                time.sleep(SHORTSLEEP)
            except OSError:
                pass

    eleza wait_impl(self, cpid):
        for i in range(10):
            # waitpid() shouldn't hang, but some of the buildbots seem to hang
            # in the forking tests.  This is an attempt to fix the problem.
            spid, status = os.waitpid(cpid, os.WNOHANG)
            ikiwa spid == cpid:
                break
            time.sleep(2 * SHORTSLEEP)

        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))

    eleza test_wait(self):
        for i in range(NUM_THREADS):
            thread = threading.Thread(target=self.f, args=(i,))
            thread.start()
            self.threads.append(thread)

        # busy-loop to wait for threads
        deadline = time.monotonic() + 10.0
        while len(self.alive) < NUM_THREADS:
            time.sleep(0.1)
            ikiwa deadline < time.monotonic():
                break

        a = sorted(self.alive.keys())
        self.assertEqual(a, list(range(NUM_THREADS)))

        prefork_lives = self.alive.copy()

        ikiwa sys.platform in ['unixware7']:
            cpid = os.fork1()
        else:
            cpid = os.fork()

        ikiwa cpid == 0:
            # Child
            time.sleep(LONGSLEEP)
            n = 0
            for key in self.alive:
                ikiwa self.alive[key] != prefork_lives[key]:
                    n += 1
            os._exit(n)
        else:
            # Parent
            self.wait_impl(cpid)
