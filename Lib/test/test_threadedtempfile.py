"""
Create na delete FILES_PER_THREAD temp files (via tempfile.TemporaryFile)
in each of NUM_THREADS threads, recording the number of successes and
failures.  A failure ni a bug kwenye tempfile, na may be due to:

+ Trying to create more than one tempfile ukijumuisha the same name.
+ Trying to delete a tempfile that doesn't still exist.
+ Something we've never seen before.

By default, NUM_THREADS == 20 na FILES_PER_THREAD == 50.  This ni enough to
create about 150 failures per run under Win98SE kwenye 2.0, na runs pretty
quickly. Guido reports needing to boost FILES_PER_THREAD to 500 before
provoking a 2.0 failure under Linux.
"""

agiza tempfile

kutoka test.support agiza start_threads
agiza unittest
agiza io
agiza threading
kutoka traceback agiza print_exc


NUM_THREADS = 20
FILES_PER_THREAD = 50


startEvent = threading.Event()


kundi TempFileGreedy(threading.Thread):
    error_count = 0
    ok_count = 0

    eleza run(self):
        self.errors = io.StringIO()
        startEvent.wait()
        kila i kwenye range(FILES_PER_THREAD):
            jaribu:
                f = tempfile.TemporaryFile("w+b")
                f.close()
            tatizo:
                self.error_count += 1
                print_exc(file=self.errors)
            isipokua:
                self.ok_count += 1


kundi ThreadedTempFileTest(unittest.TestCase):
    eleza test_main(self):
        threads = [TempFileGreedy() kila i kwenye range(NUM_THREADS)]
        ukijumuisha start_threads(threads, startEvent.set):
            pass
        ok = sum(t.ok_count kila t kwenye threads)
        errors = [str(t.name) + str(t.errors.getvalue())
                  kila t kwenye threads ikiwa t.error_count]

        msg = "Errors: errors %d ok %d\n%s" % (len(errors), ok,
            '\n'.join(errors))
        self.assertEqual(errors, [], msg)
        self.assertEqual(ok, NUM_THREADS * FILES_PER_THREAD)

ikiwa __name__ == "__main__":
    unittest.main()
