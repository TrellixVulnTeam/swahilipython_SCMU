# Test to see ikiwa openpty works. (But don't worry ikiwa it isn't available.)

agiza os, unittest

ikiwa sio hasattr(os, "openpty"):
    ashiria unittest.SkipTest("os.openpty() sio available.")


kundi OpenptyTest(unittest.TestCase):
    eleza test(self):
        master, slave = os.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        ikiwa sio os.isatty(slave):
            self.fail("Slave-end of pty ni sio a terminal.")

        os.write(slave, b'Ping!')
        self.assertEqual(os.read(master, 1024), b'Ping!')

ikiwa __name__ == '__main__':
    unittest.main()
