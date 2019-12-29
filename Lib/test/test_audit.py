"""Tests kila sys.audit na sys.addaudithook
"""

agiza subprocess
agiza sys
agiza unittest
kutoka test agiza support

ikiwa sio hasattr(sys, "addaudithook") ama sio hasattr(sys, "audit"):
    ashiria unittest.SkipTest("test only relevant when sys.audit ni available")

AUDIT_TESTS_PY = support.findfile("audit-tests.py")


kundi AuditTest(unittest.TestCase):
    eleza do_test(self, *args):
        ukijumuisha subprocess.Popen(
            [sys.executable, "-X utf8", AUDIT_TESTS_PY, *args],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) kama p:
            p.wait()
            sys.stdout.writelines(p.stdout)
            sys.stderr.writelines(p.stderr)
            ikiwa p.returncode:
                self.fail(''.join(p.stderr))

    eleza test_basic(self):
        self.do_test("test_basic")

    eleza test_block_add_hook(self):
        self.do_test("test_block_add_hook")

    eleza test_block_add_hook_baseexception(self):
        self.do_test("test_block_add_hook_baseexception")

    eleza test_finalize_hooks(self):
        events = []
        ukijumuisha subprocess.Popen(
            [sys.executable, "-X utf8", AUDIT_TESTS_PY, "test_finalize_hooks"],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) kama p:
            p.wait()
            kila line kwenye p.stdout:
                events.append(line.strip().partition(" "))
            sys.stderr.writelines(p.stderr)
            ikiwa p.returncode:
                self.fail(''.join(p.stderr))

        firstId = events[0][2]
        self.assertSequenceEqual(
            [
                ("Created", " ", firstId),
                ("cpython._PySys_ClearAuditHooks", " ", firstId),
            ],
            events,
        )

    eleza test_pickle(self):
        support.import_module("pickle")

        self.do_test("test_pickle")

    eleza test_monkeypatch(self):
        self.do_test("test_monkeypatch")

    eleza test_open(self):
        self.do_test("test_open", support.TESTFN)

    eleza test_cantrace(self):
        self.do_test("test_cantrace")

    eleza test_mmap(self):
        self.do_test("test_mmap")


ikiwa __name__ == "__main__":
    unittest.main()
