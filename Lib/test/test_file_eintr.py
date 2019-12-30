# Written to test interrupted system calls interfering ukijumuisha our many buffered
# IO implementations.  http://bugs.python.org/issue12268
#
# It was suggested that this code could be merged into test_io na the tests
# made to work using the same method as the existing signal tests kwenye test_io.
# I was unable to get single process tests using alarm ama setitimer that way
# to reproduce the EINTR problems.  This process based test suite reproduces
# the problems prior to the issue12268 patch reliably on Linux na OSX.
#  - gregory.p.smith

agiza os
agiza select
agiza signal
agiza subprocess
agiza sys
agiza time
agiza unittest

# Test agiza all of the things we're about to try testing up front.
agiza _io
agiza _pyio


@unittest.skipUnless(os.name == 'posix', 'tests requires a posix system.')
kundi TestFileIOSignalInterrupt:
    eleza setUp(self):
        self._process = Tupu

    eleza tearDown(self):
        ikiwa self._process na self._process.poll() ni Tupu:
            jaribu:
                self._process.kill()
            except OSError:
                pass

    eleza _generate_infile_setup_code(self):
        """Returns the infile = ... line of code kila the reader process.

        subclasseses should override this to test different IO objects.
        """
        rudisha ('agiza %s as io ;'
                'infile = io.FileIO(sys.stdin.fileno(), "rb")' %
                self.modname)

    eleza fail_with_process_info(self, why, stdout=b'', stderr=b'',
                               communicate=Kweli):
        """A common way to cleanup na fail ukijumuisha useful debug output.

        Kills the process ikiwa it ni still running, collects remaining output
        na fails the test ukijumuisha an error message including the output.

        Args:
            why: Text to go after "Error kutoka IO process" kwenye the message.
            stdout, stderr: standard output na error kutoka the process so
                far to include kwenye the error message.
            communicate: bool, when Kweli we call communicate() on the process
                after killing it to gather additional output.
        """
        ikiwa self._process.poll() ni Tupu:
            time.sleep(0.1)  # give it time to finish printing the error.
            jaribu:
                self._process.terminate()  # Ensure it dies.
            except OSError:
                pass
        ikiwa communicate:
            stdout_end, stderr_end = self._process.communicate()
            stdout += stdout_end
            stderr += stderr_end
        self.fail('Error kutoka IO process %s:\nSTDOUT:\n%sSTDERR:\n%s\n' %
                  (why, stdout.decode(), stderr.decode()))

    eleza _test_reading(self, data_to_write, read_and_verify_code):
        """Generic buffered read method test harness to validate EINTR behavior.

        Also validates that Python signal handlers are run during the read.

        Args:
            data_to_write: String to write to the child process kila reading
                before sending it a signal, confirming the signal was handled,
                writing a final newline na closing the infile pipe.
            read_and_verify_code: Single "line" of code to read kutoka a file
                object named 'infile' na validate the result.  This will be
                executed as part of a python subprocess fed data_to_write.
        """
        infile_setup_code = self._generate_infile_setup_code()
        # Total pipe IO kwenye this function ni smaller than the minimum posix OS
        # pipe buffer size of 512 bytes.  No writer should block.
        assert len(data_to_write) < 512, 'data_to_write must fit kwenye pipe buf.'

        # Start a subprocess to call our read method wakati handling a signal.
        self._process = subprocess.Popen(
                [sys.executable, '-u', '-c',
                 'agiza signal, sys ;'
                 'signal.signal(signal.SIGINT, '
                               'lambda s, f: sys.stderr.write("$\\n")) ;'
                 + infile_setup_code + ' ;' +
                 'sys.stderr.write("Worm Sign!\\n") ;'
                 + read_and_verify_code + ' ;' +
                 'infile.close()'
                ],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        # Wait kila the signal handler to be installed.
        worm_sign = self._process.stderr.read(len(b'Worm Sign!\n'))
        ikiwa worm_sign != b'Worm Sign!\n':  # See also, Dune by Frank Herbert.
            self.fail_with_process_info('wakati awaiting a sign',
                                        stderr=worm_sign)
        self._process.stdin.write(data_to_write)

        signals_sent = 0
        rlist = []
        # We don't know when the read_and_verify_code kwenye our child ni actually
        # executing within the read system call we want to interrupt.  This
        # loop waits kila a bit before sending the first signal to increase
        # the likelihood of that.  Implementations without correct EINTR
        # na signal handling usually fail this test.
        wakati sio rlist:
            rlist, _, _ = select.select([self._process.stderr], (), (), 0.05)
            self._process.send_signal(signal.SIGINT)
            signals_sent += 1
            ikiwa signals_sent > 200:
                self._process.kill()
                self.fail('reader process failed to handle our signals.')
        # This assumes anything unexpected that writes to stderr will also
        # write a newline.  That ni true of the traceback printing code.
        signal_line = self._process.stderr.readline()
        ikiwa signal_line != b'$\n':
            self.fail_with_process_info('wakati awaiting signal',
                                        stderr=signal_line)

        # We append a newline to our input so that a readline call can
        # end on its own before the EOF ni seen na so that we're testing
        # the read call that was interrupted by a signal before the end of
        # the data stream has been reached.
        stdout, stderr = self._process.communicate(input=b'\n')
        ikiwa self._process.returncode:
            self.fail_with_process_info(
                    'exited rc=%d' % self._process.returncode,
                    stdout, stderr, communicate=Uongo)
        # PASS!

    # String format kila the read_and_verify_code used by read methods.
    _READING_CODE_TEMPLATE = (
            'got = infile.{read_method_name}() ;'
            'expected = {expected!r} ;'
            'assert got == expected, ('
                    '"{read_method_name} returned wrong data.\\n"'
                    '"got data %r\\nexpected %r" % (got, expected))'
            )

    eleza test_readline(self):
        """readline() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello, world!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readline',
                        expected=b'hello, world!\n'))

    eleza test_readlines(self):
        """readlines() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readlines',
                        expected=[b'hello\n', b'world!\n']))

    eleza test_readall(self):
        """readall() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readall',
                        expected=b'hello\nworld!\n'))
        # read() ni the same thing as readall().
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected=b'hello\nworld!\n'))


kundi CTestFileIOSignalInterrupt(TestFileIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

kundi PyTestFileIOSignalInterrupt(TestFileIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


kundi TestBufferedIOSignalInterrupt(TestFileIOSignalInterrupt):
    eleza _generate_infile_setup_code(self):
        """Returns the infile = ... line of code to make a BufferedReader."""
        rudisha ('agiza %s as io ;infile = io.open(sys.stdin.fileno(), "rb") ;'
                'assert isinstance(infile, io.BufferedReader)' %
                self.modname)

    eleza test_readall(self):
        """BufferedReader.read() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected=b'hello\nworld!\n'))

kundi CTestBufferedIOSignalInterrupt(TestBufferedIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

kundi PyTestBufferedIOSignalInterrupt(TestBufferedIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


kundi TestTextIOSignalInterrupt(TestFileIOSignalInterrupt):
    eleza _generate_infile_setup_code(self):
        """Returns the infile = ... line of code to make a TextIOWrapper."""
        rudisha ('agiza %s as io ;'
                'infile = io.open(sys.stdin.fileno(), "rt", newline=Tupu) ;'
                'assert isinstance(infile, io.TextIOWrapper)' %
                self.modname)

    eleza test_readline(self):
        """readline() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello, world!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readline',
                        expected='hello, world!\n'))

    eleza test_readlines(self):
        """readlines() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello\r\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='readlines',
                        expected=['hello\n', 'world!\n']))

    eleza test_readall(self):
        """read() must handle signals na sio lose data."""
        self._test_reading(
                data_to_write=b'hello\nworld!',
                read_and_verify_code=self._READING_CODE_TEMPLATE.format(
                        read_method_name='read',
                        expected="hello\nworld!\n"))

kundi CTestTextIOSignalInterrupt(TestTextIOSignalInterrupt, unittest.TestCase):
    modname = '_io'

kundi PyTestTextIOSignalInterrupt(TestTextIOSignalInterrupt, unittest.TestCase):
    modname = '_pyio'


ikiwa __name__ == '__main__':
    unittest.main()
