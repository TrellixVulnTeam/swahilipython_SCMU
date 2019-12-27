# Test to see ikiwa openpty works. (But don't worry ikiwa it isn't available.)

agiza os, unittest

ikiwa not hasattr(os, "openpty"):
    raise unittest.SkipTest("os.openpty() not available.")


kundi OpenptyTest(unittest.TestCase):
    eleza test(self):
        master, slave = os.openpty()
        self.addCleanup(os.close, master)
        self.addCleanup(os.close, slave)
        ikiwa not os.isatty(slave):
            self.fail("Slave-end of pty is not a terminal.")

        os.write(slave, b'Ping!')
        self.assertEqual(os.read(master, 1024), b'Ping!')

ikiwa __name__ == '__main__':
    unittest.main()
