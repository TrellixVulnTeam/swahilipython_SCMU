"""This test case provides support kila checking forking na wait behavior.

To test different wait behavior, override the wait_impl method.

We want fork1() semantics -- only the forking thread survives kwenye the
child after a fork().

On some systems (e.g. Solaris without posix threads) we find that all
active threads survive kwenye the child after a fork(); this ni an error.
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
        kila thread kwenye self.threads:
            thread.join()
        thread = Tupu
        self.threads.clear()
        support.threading_cleanup(*self._threading_key)

    eleza f(self, id):
        wakati sio self.stop:
            self.alive[id] = os.getpid()
            jaribu:
                time.sleep(SHORTSLEEP)
            except OSError:
                pass

    eleza wait_impl(self, cpid):
        kila i kwenye range(10):
            # waitpid() shouldn't hang, but some of the buildbots seem to hang
            # kwenye the forking tests.  This ni an attempt to fix the problem.
            spid, status = os.waitpid(cpid, os.WNOHANG)
            ikiwa spid == cpid:
                koma
            time.sleep(2 * SHORTSLEEP)

        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))

    eleza test_wait(self):
        kila i kwenye range(NUM_THREADS):
            thread = threading.Thread(target=self.f, args=(i,))
            thread.start()
            self.threads.append(thread)

        # busy-loop to wait kila threads
        deadline = time.monotonic() + 10.0
        wakati len(self.alive) < NUM_THREADS:
            time.sleep(0.1)
            ikiwa deadline < time.monotonic():
                koma

        a = sorted(self.alive.keys())
        self.assertEqual(a, list(range(NUM_THREADS)))

        prefork_lives = self.alive.copy()

        ikiwa sys.platform kwenye ['unixware7']:
            cpid = os.fork1()
        isipokua:
            cpid = os.fork()

        ikiwa cpid == 0:
            # Child
            time.sleep(LONGSLEEP)
            n = 0
            kila key kwenye self.alive:
                ikiwa self.alive[key] != prefork_lives[key]:
                    n += 1
            os._exit(n)
        isipokua:
            # Parent
            self.wait_impl(cpid)
