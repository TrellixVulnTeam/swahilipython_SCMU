"""This test checks kila correct fork() behavior.
"""

agiza _imp kama imp
agiza os
agiza signal
agiza sys
agiza threading
agiza time
agiza unittest

kutoka test.fork_wait agiza ForkWait
kutoka test.support agiza reap_children, get_attribute, verbose


# Skip test ikiwa fork does sio exist.
get_attribute(os, 'fork')

kundi ForkTest(ForkWait):
    eleza wait_impl(self, cpid):
        deadline = time.monotonic() + 10.0
        wakati time.monotonic() <= deadline:
            # waitpid() shouldn't hang, but some of the buildbots seem to hang
            # kwenye the forking tests.  This ni an attempt to fix the problem.
            spid, status = os.waitpid(cpid, os.WNOHANG)
            ikiwa spid == cpid:
                koma
            time.sleep(0.1)

        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))

    eleza test_threaded_import_lock_fork(self):
        """Check fork() kwenye main thread works wakati a subthread ni doing an import"""
        import_started = threading.Event()
        fake_module_name = "fake test module"
        partial_module = "partial"
        complete_module = "complete"
        eleza importer():
            imp.acquire_lock()
            sys.modules[fake_module_name] = partial_module
            import_started.set()
            time.sleep(0.01) # Give the other thread time to try na acquire.
            sys.modules[fake_module_name] = complete_module
            imp.release_lock()
        t = threading.Thread(target=importer)
        t.start()
        import_started.wait()
        pid = os.fork()
        jaribu:
            # PyOS_BeforeFork should have waited kila the agiza to complete
            # before forking, so the child can recreate the agiza lock
            # correctly, but also won't see a partially initialised module
            ikiwa sio pid:
                m = __import__(fake_module_name)
                ikiwa m == complete_module:
                    os._exit(0)
                isipokua:
                    ikiwa verbose > 1:
                        andika("Child encountered partial module")
                    os._exit(1)
            isipokua:
                t.join()
                # Exitcode 1 means the child got a partial module (bad.) No
                # exitcode (but a hang, which manifests kama 'got pid 0')
                # means the child deadlocked (also bad.)
                self.wait_impl(pid)
        mwishowe:
            jaribu:
                os.kill(pid, signal.SIGKILL)
            tatizo OSError:
                pita


    eleza test_nested_import_lock_fork(self):
        """Check fork() kwenye main thread works wakati the main thread ni doing an import"""
        # Issue 9573: this used to trigger RuntimeError kwenye the child process
        eleza fork_with_import_lock(level):
            release = 0
            in_child = Uongo
            jaribu:
                jaribu:
                    kila i kwenye range(level):
                        imp.acquire_lock()
                        release += 1
                    pid = os.fork()
                    in_child = sio pid
                mwishowe:
                    kila i kwenye range(release):
                        imp.release_lock()
            tatizo RuntimeError:
                ikiwa in_child:
                    ikiwa verbose > 1:
                        andika("RuntimeError kwenye child")
                    os._exit(1)
                raise
            ikiwa in_child:
                os._exit(0)
            self.wait_impl(pid)

        # Check this works ukijumuisha various levels of nested
        # agiza kwenye the main thread
        kila level kwenye range(5):
            fork_with_import_lock(level)


eleza tearDownModule():
    reap_children()

ikiwa __name__ == "__main__":
    unittest.main()
