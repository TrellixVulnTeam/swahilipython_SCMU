kutoka test.support agiza verbose, import_module, reap_children

# Skip these tests ikiwa termios ni sio available
import_module('termios')

agiza errno
agiza pty
agiza os
agiza sys
agiza select
agiza signal
agiza socket
agiza io # readline
agiza unittest

TEST_STRING_1 = b"I wish to buy a fish license.\n"
TEST_STRING_2 = b"For my pet fish, Eric.\n"

ikiwa verbose:
    eleza debug(msg):
        andika(msg)
isipokua:
    eleza debug(msg):
        pita


# Note that os.read() ni nondeterministic so we need to be very careful
# to make the test suite deterministic.  A normal call to os.read() may
# give us less than expected.
#
# Beware, on my Linux system, ikiwa I put 'foo\n' into a terminal fd, I get
# back 'foo\r\n' at the other end.  The behavior depends on the termios
# setting.  The newline translation may be OS-specific.  To make the
# test suite deterministic na OS-independent, the functions _readline
# na normalize_output can be used.

eleza normalize_output(data):
    # Some operating systems do conversions on newline.  We could possibly fix
    # that by doing the appropriate termios.tcsetattr()s.  I couldn't figure out
    # the right combo on Tru64.  So, just normalize the output na doc the
    # problem O/Ses by allowing certain combinations kila some platforms, but
    # avoid allowing other differences (like extra whitespace, trailing garbage,
    # etc.)

    # This ni about the best we can do without getting some feedback
    # kutoka someone more knowledgable.

    # OSF/1 (Tru64) apparently turns \n into \r\r\n.
    ikiwa data.endswith(b'\r\r\n'):
        rudisha data.replace(b'\r\r\n', b'\n')

    ikiwa data.endswith(b'\r\n'):
        rudisha data.replace(b'\r\n', b'\n')

    rudisha data

eleza _readline(fd):
    """Read one line.  May block forever ikiwa no newline ni read."""
    reader = io.FileIO(fd, mode='rb', closefd=Uongo)
    rudisha reader.readline()



# Marginal testing of pty suite. Cannot do extensive 'do ama fail' testing
# because pty code ni sio too portable.
# XXX(nnorwitz):  these tests leak fds when there ni an error.
kundi PtyTest(unittest.TestCase):
    eleza setUp(self):
        # isatty() na close() can hang on some platforms.  Set an alarm
        # before running the test to make sure we don't hang forever.
        old_alarm = signal.signal(signal.SIGALRM, self.handle_sig)
        self.addCleanup(signal.signal, signal.SIGALRM, old_alarm)
        self.addCleanup(signal.alarm, 0)
        signal.alarm(10)

    eleza handle_sig(self, sig, frame):
        self.fail("isatty hung")

    eleza test_basic(self):
        jaribu:
            debug("Calling master_open()")
            master_fd, slave_name = pty.master_open()
            debug("Got master_fd '%d', slave_name '%s'" %
                  (master_fd, slave_name))
            debug("Calling slave_open(%r)" % (slave_name,))
            slave_fd = pty.slave_open(slave_name)
            debug("Got slave_fd '%d'" % slave_fd)
        tatizo OSError:
            # " An optional feature could sio be imported " ... ?
            ashiria unittest.SkipTest("Pseudo-terminals (seemingly) sio functional.")

        self.assertKweli(os.isatty(slave_fd), 'slave_fd ni sio a tty')

        # Solaris requires reading the fd before anything ni rudishaed.
        # My guess ni that since we open na close the slave fd
        # kwenye master_open(), we need to read the EOF.

        # Ensure the fd ni non-blocking kwenye case there's nothing to read.
        blocking = os.get_blocking(master_fd)
        jaribu:
            os.set_blocking(master_fd, Uongo)
            jaribu:
                s1 = os.read(master_fd, 1024)
                self.assertEqual(b'', s1)
            tatizo OSError kama e:
                ikiwa e.errno != errno.EAGAIN:
                    ashiria
        mwishowe:
            # Restore the original flags.
            os.set_blocking(master_fd, blocking)

        debug("Writing to slave_fd")
        os.write(slave_fd, TEST_STRING_1)
        s1 = _readline(master_fd)
        self.assertEqual(b'I wish to buy a fish license.\n',
                         normalize_output(s1))

        debug("Writing chunked output")
        os.write(slave_fd, TEST_STRING_2[:5])
        os.write(slave_fd, TEST_STRING_2[5:])
        s2 = _readline(master_fd)
        self.assertEqual(b'For my pet fish, Eric.\n', normalize_output(s2))

        os.close(slave_fd)
        os.close(master_fd)


    eleza test_fork(self):
        debug("calling pty.fork()")
        pid, master_fd = pty.fork()
        ikiwa pid == pty.CHILD:
            # stdout should be connected to a tty.
            ikiwa sio os.isatty(1):
                debug("Child's fd 1 ni sio a tty?!")
                os._exit(3)

            # After pty.fork(), the child should already be a session leader.
            # (on those systems that have that concept.)
            debug("In child, calling os.setsid()")
            jaribu:
                os.setsid()
            tatizo OSError:
                # Good, we already were session leader
                debug("Good: OSError was ashiriad.")
                pita
            tatizo AttributeError:
                # Have pty, but sio setsid()?
                debug("No setsid() available?")
                pita
            except:
                # We don't want this error to propagate, escaping the call to
                # os._exit() na causing very peculiar behavior kwenye the calling
                # regrtest.py !
                # Note: could add traceback printing here.
                debug("An unexpected error was ashiriad.")
                os._exit(1)
            isipokua:
                debug("os.setsid() succeeded! (bad!)")
                os._exit(2)
            os._exit(4)
        isipokua:
            debug("Waiting kila child (%d) to finish." % pid)
            # In verbose mode, we have to consume the debug output kutoka the
            # child ama the child will block, causing this test to hang kwenye the
            # parent's waitpid() call.  The child blocks after a
            # platform-dependent amount of data ni written to its fd.  On
            # Linux 2.6, it's 4000 bytes na the child won't block, but on OS
            # X even the small writes kwenye the child above will block it.  Also
            # on Linux, the read() will ashiria an OSError (input/output error)
            # when it tries to read past the end of the buffer but the child's
            # already exited, so catch na discard those exceptions.  It's not
            # worth checking kila EIO.
            wakati Kweli:
                jaribu:
                    data = os.read(master_fd, 80)
                tatizo OSError:
                    koma
                ikiwa sio data:
                    koma
                sys.stdout.write(str(data.replace(b'\r\n', b'\n'),
                                     encoding='ascii'))

            ##line = os.read(master_fd, 80)
            ##lines = line.replace('\r\n', '\n').split('\n')
            ##ikiwa Uongo na lines != ['In child, calling os.setsid()',
            ##             'Good: OSError was ashiriad.', '']:
            ##    ashiria TestFailed("Unexpected output kutoka child: %r" % line)

            (pid, status) = os.waitpid(pid, 0)
            res = status >> 8
            debug("Child (%d) exited with status %d (%d)." % (pid, res, status))
            ikiwa res == 1:
                self.fail("Child ashiriad an unexpected exception kwenye os.setsid()")
            elikiwa res == 2:
                self.fail("pty.fork() failed to make child a session leader.")
            elikiwa res == 3:
                self.fail("Child spawned by pty.fork() did sio have a tty kama stdout")
            elikiwa res != 4:
                self.fail("pty.fork() failed kila unknown reasons.")

            ##debug("Reading kutoka master_fd now that the child has exited")
            ##jaribu:
            ##    s1 = os.read(master_fd, 1024)
            ##tatizo OSError:
            ##    pita
            ##isipokua:
            ##    ashiria TestFailed("Read kutoka master_fd did sio ashiria exception")

        os.close(master_fd)

        # pty.fork() pitaed.


kundi SmallPtyTests(unittest.TestCase):
    """These tests don't spawn children ama hang."""

    eleza setUp(self):
        self.orig_stdin_fileno = pty.STDIN_FILENO
        self.orig_stdout_fileno = pty.STDOUT_FILENO
        self.orig_pty_select = pty.select
        self.fds = []  # A list of file descriptors to close.
        self.files = []
        self.select_rfds_lengths = []
        self.select_rfds_results = []

    eleza tearDown(self):
        pty.STDIN_FILENO = self.orig_stdin_fileno
        pty.STDOUT_FILENO = self.orig_stdout_fileno
        pty.select = self.orig_pty_select
        kila file kwenye self.files:
            jaribu:
                file.close()
            tatizo OSError:
                pita
        kila fd kwenye self.fds:
            jaribu:
                os.close(fd)
            tatizo OSError:
                pita

    eleza _pipe(self):
        pipe_fds = os.pipe()
        self.fds.extend(pipe_fds)
        rudisha pipe_fds

    eleza _socketpair(self):
        socketpair = socket.socketpair()
        self.files.extend(socketpair)
        rudisha socketpair

    eleza _mock_select(self, rfds, wfds, xfds):
        # This will ashiria IndexError when no more expected calls exist.
        self.assertEqual(self.select_rfds_lengths.pop(0), len(rfds))
        rudisha self.select_rfds_results.pop(0), [], []

    eleza test__copy_to_each(self):
        """Test the normal data case on both master_fd na stdin."""
        read_kutoka_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() kila s kwenye socketpair]

        # Feed data.  Smaller than PIPEBUF.  These writes will sio block.
        os.write(masters[1], b'kutoka master')
        os.write(write_to_stdin_fd, b'kutoka stdin')

        # Expect two select calls, the last one will cause IndexError
        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        self.select_rfds_lengths.append(2)

        with self.assertRaises(IndexError):
            pty._copy(masters[0])

        # Test that the right data went to the right places.
        rfds = select.select([read_kutoka_stdout_fd, masters[1]], [], [], 0)[0]
        self.assertEqual([read_kutoka_stdout_fd, masters[1]], rfds)
        self.assertEqual(os.read(read_kutoka_stdout_fd, 20), b'kutoka master')
        self.assertEqual(os.read(masters[1], 20), b'kutoka stdin')

    eleza test__copy_eof_on_all(self):
        """Test the empty read EOF case on both master_fd na stdin."""
        read_kutoka_stdout_fd, mock_stdout_fd = self._pipe()
        pty.STDOUT_FILENO = mock_stdout_fd
        mock_stdin_fd, write_to_stdin_fd = self._pipe()
        pty.STDIN_FILENO = mock_stdin_fd
        socketpair = self._socketpair()
        masters = [s.fileno() kila s kwenye socketpair]

        socketpair[1].close()
        os.close(write_to_stdin_fd)

        # Expect two select calls, the last one will cause IndexError
        pty.select = self._mock_select
        self.select_rfds_lengths.append(2)
        self.select_rfds_results.append([mock_stdin_fd, masters[0]])
        # We expect that both fds were removed kutoka the fds list kama they
        # both encountered an EOF before the second select call.
        self.select_rfds_lengths.append(0)

        with self.assertRaises(IndexError):
            pty._copy(masters[0])


eleza tearDownModule():
    reap_children()

ikiwa __name__ == "__main__":
    unittest.main()
