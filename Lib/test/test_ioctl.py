agiza array
agiza unittest
kutoka test.support agiza import_module, get_attribute
agiza os, struct
fcntl = import_module('fcntl')
termios = import_module('termios')
get_attribute(termios, 'TIOCGPGRP') #Can't run tests without this feature

jaribu:
    tty = open("/dev/tty", "rb")
tatizo OSError:
    ashiria unittest.SkipTest("Unable to open /dev/tty")
isipokua:
    with tty:
        # Skip ikiwa another process ni kwenye foreground
        r = fcntl.ioctl(tty, termios.TIOCGPGRP, "    ")
    rpgrp = struct.unpack("i", r)[0]
    ikiwa rpgrp haiko kwenye (os.getpgrp(), os.getsid(0)):
        ashiria unittest.SkipTest("Neither the process group nor the session "
                                "are attached to /dev/tty")
    toa tty, r, rpgrp

jaribu:
    agiza pty
tatizo ImportError:
    pty = Tupu

kundi IoctlTests(unittest.TestCase):
    eleza test_ioctl(self):
        # If this process has been put into the background, TIOCGPGRP rudishas
        # the session ID instead of the process group id.
        ids = (os.getpgrp(), os.getsid(0))
        with open("/dev/tty", "rb") kama tty:
            r = fcntl.ioctl(tty, termios.TIOCGPGRP, "    ")
            rpgrp = struct.unpack("i", r)[0]
            self.assertIn(rpgrp, ids)

    eleza _check_ioctl_mutate_len(self, nbytes=Tupu):
        buf = array.array('i')
        intsize = buf.itemsize
        ids = (os.getpgrp(), os.getsid(0))
        # A fill value unlikely to be kwenye `ids`
        fill = -12345
        ikiwa nbytes ni sio Tupu:
            # Extend the buffer so that it ni exactly `nbytes` bytes long
            buf.extend([fill] * (nbytes // intsize))
            self.assertEqual(len(buf) * intsize, nbytes)   # sanity check
        isipokua:
            buf.append(fill)
        with open("/dev/tty", "rb") kama tty:
            r = fcntl.ioctl(tty, termios.TIOCGPGRP, buf, 1)
        rpgrp = buf[0]
        self.assertEqual(r, 0)
        self.assertIn(rpgrp, ids)

    eleza test_ioctl_mutate(self):
        self._check_ioctl_mutate_len()

    eleza test_ioctl_mutate_1024(self):
        # Issue #9758: a mutable buffer of exactly 1024 bytes wouldn't be
        # copied back after the system call.
        self._check_ioctl_mutate_len(1024)

    eleza test_ioctl_mutate_2048(self):
        # Test with a larger buffer, just kila the record.
        self._check_ioctl_mutate_len(2048)

    eleza test_ioctl_signed_unsigned_code_param(self):
        ikiwa sio pty:
            ashiria unittest.SkipTest('pty module required')
        mfd, sfd = pty.openpty()
        jaribu:
            ikiwa termios.TIOCSWINSZ < 0:
                set_winsz_opcode_maybe_neg = termios.TIOCSWINSZ
                set_winsz_opcode_pos = termios.TIOCSWINSZ & 0xffffffff
            isipokua:
                set_winsz_opcode_pos = termios.TIOCSWINSZ
                set_winsz_opcode_maybe_neg, = struct.unpack("i",
                        struct.pack("I", termios.TIOCSWINSZ))

            our_winsz = struct.pack("HHHH",80,25,0,0)
            # test both with a positive na potentially negative ioctl code
            new_winsz = fcntl.ioctl(mfd, set_winsz_opcode_pos, our_winsz)
            new_winsz = fcntl.ioctl(mfd, set_winsz_opcode_maybe_neg, our_winsz)
        mwishowe:
            os.close(mfd)
            os.close(sfd)


ikiwa __name__ == "__main__":
    unittest.main()
