'''
Tests kila fileinput module.
Nick Mathewson
'''
agiza os
agiza sys
agiza re
agiza fileinput
agiza collections
agiza builtins
agiza tempfile
agiza unittest

jaribu:
    agiza bz2
tatizo ImportError:
    bz2 = Tupu
jaribu:
    agiza gzip
tatizo ImportError:
    gzip = Tupu

kutoka io agiza BytesIO, StringIO
kutoka fileinput agiza FileInput, hook_encoded
kutoka pathlib agiza Path

kutoka test.support agiza verbose, TESTFN, check_warnings
kutoka test.support agiza unlink kama safe_unlink
kutoka test agiza support
kutoka unittest agiza mock


# The fileinput module has 2 interfaces: the FileInput kundi which does
# all the work, na a few functions (input, etc.) that use a global _state
# variable.

kundi BaseTests:
    # Write a content (str ama bytes) to temp file, na rudisha the
    # temp file's name.
    eleza writeTmp(self, content, *, mode='w'):  # opening kwenye text mode ni the default
        fd, name = tempfile.mkstemp()
        self.addCleanup(support.unlink, name)
        with open(fd, mode) kama f:
            f.write(content)
        rudisha name

kundi LineReader:

    eleza __init__(self):
        self._linesread = []

    @property
    eleza linesread(self):
        jaribu:
            rudisha self._linesread[:]
        mwishowe:
            self._linesread = []

    eleza openhook(self, filename, mode):
        self.it = iter(filename.splitlines(Kweli))
        rudisha self

    eleza readline(self, size=Tupu):
        line = next(self.it, '')
        self._linesread.append(line)
        rudisha line

    eleza readlines(self, hint=-1):
        lines = []
        size = 0
        wakati Kweli:
            line = self.readline()
            ikiwa sio line:
                rudisha lines
            lines.append(line)
            size += len(line)
            ikiwa size >= hint:
                rudisha lines

    eleza close(self):
        pita

kundi BufferSizesTests(BaseTests, unittest.TestCase):
    eleza test_buffer_sizes(self):

        t1 = self.writeTmp(''.join("Line %s of file 1\n" % (i+1) kila i kwenye range(15)))
        t2 = self.writeTmp(''.join("Line %s of file 2\n" % (i+1) kila i kwenye range(10)))
        t3 = self.writeTmp(''.join("Line %s of file 3\n" % (i+1) kila i kwenye range(5)))
        t4 = self.writeTmp(''.join("Line %s of file 4\n" % (i+1) kila i kwenye range(1)))

        pat = re.compile(r'LINE (\d+) OF FILE (\d+)')

        ikiwa verbose:
            andika('1. Simple iteration')
        fi = FileInput(files=(t1, t2, t3, t4))
        lines = list(fi)
        fi.close()
        self.assertEqual(len(lines), 31)
        self.assertEqual(lines[4], 'Line 5 of file 1\n')
        self.assertEqual(lines[30], 'Line 1 of file 4\n')
        self.assertEqual(fi.lineno(), 31)
        self.assertEqual(fi.filename(), t4)

        ikiwa verbose:
            andika('2. Status variables')
        fi = FileInput(files=(t1, t2, t3, t4))
        s = "x"
        wakati s na s != 'Line 6 of file 2\n':
            s = fi.readline()
        self.assertEqual(fi.filename(), t2)
        self.assertEqual(fi.lineno(), 21)
        self.assertEqual(fi.filelineno(), 6)
        self.assertUongo(fi.isfirstline())
        self.assertUongo(fi.isstdin())

        ikiwa verbose:
            andika('3. Nextfile')
        fi.nextfile()
        self.assertEqual(fi.readline(), 'Line 1 of file 3\n')
        self.assertEqual(fi.lineno(), 22)
        fi.close()

        ikiwa verbose:
            andika('4. Stdin')
        fi = FileInput(files=(t1, t2, t3, t4, '-'))
        savestdin = sys.stdin
        jaribu:
            sys.stdin = StringIO("Line 1 of stdin\nLine 2 of stdin\n")
            lines = list(fi)
            self.assertEqual(len(lines), 33)
            self.assertEqual(lines[32], 'Line 2 of stdin\n')
            self.assertEqual(fi.filename(), '<stdin>')
            fi.nextfile()
        mwishowe:
            sys.stdin = savestdin

        ikiwa verbose:
            andika('5. Boundary conditions')
        fi = FileInput(files=(t1, t2, t3, t4))
        self.assertEqual(fi.lineno(), 0)
        self.assertEqual(fi.filename(), Tupu)
        fi.nextfile()
        self.assertEqual(fi.lineno(), 0)
        self.assertEqual(fi.filename(), Tupu)

        ikiwa verbose:
            andika('6. Inplace')
        savestdout = sys.stdout
        jaribu:
            fi = FileInput(files=(t1, t2, t3, t4), inplace=1)
            kila line kwenye fi:
                line = line[:-1].upper()
                andika(line)
            fi.close()
        mwishowe:
            sys.stdout = savestdout

        fi = FileInput(files=(t1, t2, t3, t4))
        kila line kwenye fi:
            self.assertEqual(line[-1], '\n')
            m = pat.match(line[:-1])
            self.assertNotEqual(m, Tupu)
            self.assertEqual(int(m.group(1)), fi.filelineno())
        fi.close()

kundi UnconditionallyRaise:
    eleza __init__(self, exception_type):
        self.exception_type = exception_type
        self.invoked = Uongo
    eleza __call__(self, *args, **kwargs):
        self.invoked = Kweli
        ashiria self.exception_type()

kundi FileInputTests(BaseTests, unittest.TestCase):

    eleza test_zero_byte_files(self):
        t1 = self.writeTmp("")
        t2 = self.writeTmp("")
        t3 = self.writeTmp("The only line there is.\n")
        t4 = self.writeTmp("")
        fi = FileInput(files=(t1, t2, t3, t4))

        line = fi.readline()
        self.assertEqual(line, 'The only line there is.\n')
        self.assertEqual(fi.lineno(), 1)
        self.assertEqual(fi.filelineno(), 1)
        self.assertEqual(fi.filename(), t3)

        line = fi.readline()
        self.assertUongo(line)
        self.assertEqual(fi.lineno(), 1)
        self.assertEqual(fi.filelineno(), 0)
        self.assertEqual(fi.filename(), t4)
        fi.close()

    eleza test_files_that_dont_end_with_newline(self):
        t1 = self.writeTmp("A\nB\nC")
        t2 = self.writeTmp("D\nE\nF")
        fi = FileInput(files=(t1, t2))
        lines = list(fi)
        self.assertEqual(lines, ["A\n", "B\n", "C", "D\n", "E\n", "F"])
        self.assertEqual(fi.filelineno(), 3)
        self.assertEqual(fi.lineno(), 6)

##     eleza test_unicode_filenames(self):
##         # XXX A unicode string ni always rudishaed by writeTmp.
##         #     So ni this needed?
##         t1 = self.writeTmp("A\nB")
##         encoding = sys.getfilesystemencoding()
##         ikiwa encoding ni Tupu:
##             encoding = 'ascii'
##         fi = FileInput(files=str(t1, encoding))
##         lines = list(fi)
##         self.assertEqual(lines, ["A\n", "B"])

    eleza test_fileno(self):
        t1 = self.writeTmp("A\nB")
        t2 = self.writeTmp("C\nD")
        fi = FileInput(files=(t1, t2))
        self.assertEqual(fi.fileno(), -1)
        line = next(fi)
        self.assertNotEqual(fi.fileno(), -1)
        fi.nextfile()
        self.assertEqual(fi.fileno(), -1)
        line = list(fi)
        self.assertEqual(fi.fileno(), -1)

    eleza test_opening_mode(self):
        jaribu:
            # invalid mode, should ashiria ValueError
            fi = FileInput(mode="w")
            self.fail("FileInput should reject invalid mode argument")
        tatizo ValueError:
            pita
        # try opening kwenye universal newline mode
        t1 = self.writeTmp(b"A\nB\r\nC\rD", mode="wb")
        with check_warnings(('', DeprecationWarning)):
            fi = FileInput(files=t1, mode="U")
        with check_warnings(('', DeprecationWarning)):
            lines = list(fi)
        self.assertEqual(lines, ["A\n", "B\n", "C\n", "D"])

    eleza test_stdin_binary_mode(self):
        with mock.patch('sys.stdin') kama m_stdin:
            m_stdin.buffer = BytesIO(b'spam, bacon, sausage, na spam')
            fi = FileInput(files=['-'], mode='rb')
            lines = list(fi)
            self.assertEqual(lines, [b'spam, bacon, sausage, na spam'])

    eleza test_detached_stdin_binary_mode(self):
        orig_stdin = sys.stdin
        jaribu:
            sys.stdin = BytesIO(b'spam, bacon, sausage, na spam')
            self.assertUongo(hasattr(sys.stdin, 'buffer'))
            fi = FileInput(files=['-'], mode='rb')
            lines = list(fi)
            self.assertEqual(lines, [b'spam, bacon, sausage, na spam'])
        mwishowe:
            sys.stdin = orig_stdin

    eleza test_file_opening_hook(self):
        jaribu:
            # cannot use openhook na inplace mode
            fi = FileInput(inplace=1, openhook=lambda f, m: Tupu)
            self.fail("FileInput should ashiria ikiwa both inplace "
                             "and openhook arguments are given")
        tatizo ValueError:
            pita
        jaribu:
            fi = FileInput(openhook=1)
            self.fail("FileInput should check openhook kila being callable")
        tatizo ValueError:
            pita

        kundi CustomOpenHook:
            eleza __init__(self):
                self.invoked = Uongo
            eleza __call__(self, *args):
                self.invoked = Kweli
                rudisha open(*args)

        t = self.writeTmp("\n")
        custom_open_hook = CustomOpenHook()
        with FileInput([t], openhook=custom_open_hook) kama fi:
            fi.readline()
        self.assertKweli(custom_open_hook.invoked, "openhook sio invoked")

    eleza test_readline(self):
        with open(TESTFN, 'wb') kama f:
            f.write(b'A\nB\r\nC\r')
            # Fill TextIOWrapper buffer.
            f.write(b'123456789\n' * 1000)
            # Issue #20501: readline() shouldn't read whole file.
            f.write(b'\x80')
        self.addCleanup(safe_unlink, TESTFN)

        with FileInput(files=TESTFN,
                       openhook=hook_encoded('ascii')) kama fi:
            jaribu:
                self.assertEqual(fi.readline(), 'A\n')
                self.assertEqual(fi.readline(), 'B\n')
                self.assertEqual(fi.readline(), 'C\n')
            tatizo UnicodeDecodeError:
                self.fail('Read to end of file')
            with self.assertRaises(UnicodeDecodeError):
                # Read to the end of file.
                list(fi)
            self.assertEqual(fi.readline(), '')
            self.assertEqual(fi.readline(), '')

    eleza test_readline_binary_mode(self):
        with open(TESTFN, 'wb') kama f:
            f.write(b'A\nB\r\nC\rD')
        self.addCleanup(safe_unlink, TESTFN)

        with FileInput(files=TESTFN, mode='rb') kama fi:
            self.assertEqual(fi.readline(), b'A\n')
            self.assertEqual(fi.readline(), b'B\r\n')
            self.assertEqual(fi.readline(), b'C\rD')
            # Read to the end of file.
            self.assertEqual(fi.readline(), b'')
            self.assertEqual(fi.readline(), b'')

    eleza test_inplace_binary_write_mode(self):
        temp_file = self.writeTmp(b'Initial text.', mode='wb')
        with FileInput(temp_file, mode='rb', inplace=Kweli) kama fobj:
            line = fobj.readline()
            self.assertEqual(line, b'Initial text.')
            # andika() cannot be used with files opened kwenye binary mode.
            sys.stdout.write(b'New line.')
        with open(temp_file, 'rb') kama f:
            self.assertEqual(f.read(), b'New line.')

    eleza test_context_manager(self):
        t1 = self.writeTmp("A\nB\nC")
        t2 = self.writeTmp("D\nE\nF")
        with FileInput(files=(t1, t2)) kama fi:
            lines = list(fi)
        self.assertEqual(lines, ["A\n", "B\n", "C", "D\n", "E\n", "F"])
        self.assertEqual(fi.filelineno(), 3)
        self.assertEqual(fi.lineno(), 6)
        self.assertEqual(fi._files, ())

    eleza test_close_on_exception(self):
        t1 = self.writeTmp("")
        jaribu:
            with FileInput(files=t1) kama fi:
                ashiria OSError
        tatizo OSError:
            self.assertEqual(fi._files, ())

    eleza test_empty_files_list_specified_to_constructor(self):
        with FileInput(files=[]) kama fi:
            self.assertEqual(fi._files, ('-',))

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test__getitem__(self):
        """Tests invoking FileInput.__getitem__() with the current
           line number"""
        t = self.writeTmp("line1\nline2\n")
        with FileInput(files=[t]) kama fi:
            retval1 = fi[0]
            self.assertEqual(retval1, "line1\n")
            retval2 = fi[1]
            self.assertEqual(retval2, "line2\n")

    eleza test__getitem___deprecation(self):
        t = self.writeTmp("line1\nline2\n")
        with self.assertWarnsRegex(DeprecationWarning,
                                   r'Use iterator protocol instead'):
            with FileInput(files=[t]) kama fi:
                self.assertEqual(fi[0], "line1\n")

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test__getitem__invalid_key(self):
        """Tests invoking FileInput.__getitem__() with an index unequal to
           the line number"""
        t = self.writeTmp("line1\nline2\n")
        with FileInput(files=[t]) kama fi:
            with self.assertRaises(RuntimeError) kama cm:
                fi[1]
        self.assertEqual(cm.exception.args, ("accessing lines out of order",))

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test__getitem__eof(self):
        """Tests invoking FileInput.__getitem__() with the line number but at
           end-of-input"""
        t = self.writeTmp('')
        with FileInput(files=[t]) kama fi:
            with self.assertRaises(IndexError) kama cm:
                fi[0]
        self.assertEqual(cm.exception.args, ("end of input reached",))

    eleza test_nextfile_oserror_deleting_backup(self):
        """Tests invoking FileInput.nextfile() when the attempt to delete
           the backup file would ashiria OSError.  This error ni expected to be
           silently ignored"""

        os_unlink_orig = os.unlink
        os_unlink_replacement = UnconditionallyRaise(OSError)
        jaribu:
            t = self.writeTmp("\n")
            self.addCleanup(support.unlink, t + '.bak')
            with FileInput(files=[t], inplace=Kweli) kama fi:
                next(fi) # make sure the file ni opened
                os.unlink = os_unlink_replacement
                fi.nextfile()
        mwishowe:
            os.unlink = os_unlink_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertKweli(os_unlink_replacement.invoked,
                        "os.unlink() was sio invoked")

    eleza test_readline_os_fstat_ashirias_OSError(self):
        """Tests invoking FileInput.readline() when os.fstat() ashirias OSError.
           This exception should be silently discarded."""

        os_fstat_orig = os.fstat
        os_fstat_replacement = UnconditionallyRaise(OSError)
        jaribu:
            t = self.writeTmp("\n")
            with FileInput(files=[t], inplace=Kweli) kama fi:
                os.fstat = os_fstat_replacement
                fi.readline()
        mwishowe:
            os.fstat = os_fstat_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertKweli(os_fstat_replacement.invoked,
                        "os.fstat() was sio invoked")

    eleza test_readline_os_chmod_ashirias_OSError(self):
        """Tests invoking FileInput.readline() when os.chmod() ashirias OSError.
           This exception should be silently discarded."""

        os_chmod_orig = os.chmod
        os_chmod_replacement = UnconditionallyRaise(OSError)
        jaribu:
            t = self.writeTmp("\n")
            with FileInput(files=[t], inplace=Kweli) kama fi:
                os.chmod = os_chmod_replacement
                fi.readline()
        mwishowe:
            os.chmod = os_chmod_orig

        # sanity check to make sure that our test scenario was actually hit
        self.assertKweli(os_chmod_replacement.invoked,
                        "os.fstat() was sio invoked")

    eleza test_fileno_when_ValueError_ashiriad(self):
        kundi FilenoRaisesValueError(UnconditionallyRaise):
            eleza __init__(self):
                UnconditionallyRaise.__init__(self, ValueError)
            eleza fileno(self):
                self.__call__()

        unconditionally_ashiria_ValueError = FilenoRaisesValueError()
        t = self.writeTmp("\n")
        with FileInput(files=[t]) kama fi:
            file_backup = fi._file
            jaribu:
                fi._file = unconditionally_ashiria_ValueError
                result = fi.fileno()
            mwishowe:
                fi._file = file_backup # make sure the file gets cleaned up

        # sanity check to make sure that our test scenario was actually hit
        self.assertKweli(unconditionally_ashiria_ValueError.invoked,
                        "_file.fileno() was sio invoked")

        self.assertEqual(result, -1, "fileno() should rudisha -1")

    eleza test_readline_buffering(self):
        src = LineReader()
        with FileInput(files=['line1\nline2', 'line3\n'],
                       openhook=src.openhook) kama fi:
            self.assertEqual(src.linesread, [])
            self.assertEqual(fi.readline(), 'line1\n')
            self.assertEqual(src.linesread, ['line1\n'])
            self.assertEqual(fi.readline(), 'line2')
            self.assertEqual(src.linesread, ['line2'])
            self.assertEqual(fi.readline(), 'line3\n')
            self.assertEqual(src.linesread, ['', 'line3\n'])
            self.assertEqual(fi.readline(), '')
            self.assertEqual(src.linesread, [''])
            self.assertEqual(fi.readline(), '')
            self.assertEqual(src.linesread, [])

    eleza test_iteration_buffering(self):
        src = LineReader()
        with FileInput(files=['line1\nline2', 'line3\n'],
                       openhook=src.openhook) kama fi:
            self.assertEqual(src.linesread, [])
            self.assertEqual(next(fi), 'line1\n')
            self.assertEqual(src.linesread, ['line1\n'])
            self.assertEqual(next(fi), 'line2')
            self.assertEqual(src.linesread, ['line2'])
            self.assertEqual(next(fi), 'line3\n')
            self.assertEqual(src.linesread, ['', 'line3\n'])
            self.assertRaises(StopIteration, next, fi)
            self.assertEqual(src.linesread, [''])
            self.assertRaises(StopIteration, next, fi)
            self.assertEqual(src.linesread, [])

    eleza test_pathlib_file(self):
        t1 = Path(self.writeTmp("Pathlib file."))
        with FileInput(t1) kama fi:
            line = fi.readline()
            self.assertEqual(line, 'Pathlib file.')
            self.assertEqual(fi.lineno(), 1)
            self.assertEqual(fi.filelineno(), 1)
            self.assertEqual(fi.filename(), os.fspath(t1))

    eleza test_pathlib_file_inplace(self):
        t1 = Path(self.writeTmp('Pathlib file.'))
        with FileInput(t1, inplace=Kweli) kama fi:
            line = fi.readline()
            self.assertEqual(line, 'Pathlib file.')
            andika('Modified %s' % line)
        with open(t1) kama f:
            self.assertEqual(f.read(), 'Modified Pathlib file.\n')


kundi MockFileInput:
    """A kundi that mocks out fileinput.FileInput kila use during unit tests"""

    eleza __init__(self, files=Tupu, inplace=Uongo, backup="", *,
                 mode="r", openhook=Tupu):
        self.files = files
        self.inplace = inplace
        self.backup = backup
        self.mode = mode
        self.openhook = openhook
        self._file = Tupu
        self.invocation_counts = collections.defaultdict(lambda: 0)
        self.rudisha_values = {}

    eleza close(self):
        self.invocation_counts["close"] += 1

    eleza nextfile(self):
        self.invocation_counts["nextfile"] += 1
        rudisha self.rudisha_values["nextfile"]

    eleza filename(self):
        self.invocation_counts["filename"] += 1
        rudisha self.rudisha_values["filename"]

    eleza lineno(self):
        self.invocation_counts["lineno"] += 1
        rudisha self.rudisha_values["lineno"]

    eleza filelineno(self):
        self.invocation_counts["filelineno"] += 1
        rudisha self.rudisha_values["filelineno"]

    eleza fileno(self):
        self.invocation_counts["fileno"] += 1
        rudisha self.rudisha_values["fileno"]

    eleza isfirstline(self):
        self.invocation_counts["isfirstline"] += 1
        rudisha self.rudisha_values["isfirstline"]

    eleza isstdin(self):
        self.invocation_counts["isstdin"] += 1
        rudisha self.rudisha_values["isstdin"]

kundi BaseFileInputGlobalMethodsTest(unittest.TestCase):
    """Base kundi kila unit tests kila the global function of
       the fileinput module."""

    eleza setUp(self):
        self._orig_state = fileinput._state
        self._orig_FileInput = fileinput.FileInput
        fileinput.FileInput = MockFileInput

    eleza tearDown(self):
        fileinput.FileInput = self._orig_FileInput
        fileinput._state = self._orig_state

    eleza assertExactlyOneInvocation(self, mock_file_input, method_name):
        # assert that the method with the given name was invoked once
        actual_count = mock_file_input.invocation_counts[method_name]
        self.assertEqual(actual_count, 1, method_name)
        # assert that no other unexpected methods were invoked
        actual_total_count = len(mock_file_input.invocation_counts)
        self.assertEqual(actual_total_count, 1)

kundi Test_fileinput_input(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.input()"""

    eleza test_state_is_not_Tupu_and_state_file_is_not_Tupu(self):
        """Tests invoking fileinput.input() when fileinput._state ni sio Tupu
           na its _file attribute ni also sio Tupu.  Expect RuntimeError to
           be ashiriad with a meaningful error message na kila fileinput._state
           to *not* be modified."""
        instance = MockFileInput()
        instance._file = object()
        fileinput._state = instance
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.input()
        self.assertEqual(("input() already active",), cm.exception.args)
        self.assertIs(instance, fileinput._state, "fileinput._state")

    eleza test_state_is_not_Tupu_and_state_file_is_Tupu(self):
        """Tests invoking fileinput.input() when fileinput._state ni sio Tupu
           but its _file attribute *is* Tupu.  Expect it to create na rudisha
           a new fileinput.FileInput object with all method parameters pitaed
           explicitly to the __init__() method; also ensure that
           fileinput._state ni set to the rudishaed instance."""
        instance = MockFileInput()
        instance._file = Tupu
        fileinput._state = instance
        self.do_test_call_input()

    eleza test_state_is_Tupu(self):
        """Tests invoking fileinput.input() when fileinput._state ni Tupu
           Expect it to create na rudisha a new fileinput.FileInput object
           with all method parameters pitaed explicitly to the __init__()
           method; also ensure that fileinput._state ni set to the rudishaed
           instance."""
        fileinput._state = Tupu
        self.do_test_call_input()

    eleza do_test_call_input(self):
        """Tests that fileinput.input() creates a new fileinput.FileInput
           object, pitaing the given parameters unmodified to
           fileinput.FileInput.__init__().  Note that this test depends on the
           monkey patching of fileinput.FileInput done by setUp()."""
        files = object()
        inplace = object()
        backup = object()
        mode = object()
        openhook = object()

        # call fileinput.input() with different values kila each argument
        result = fileinput.input(files=files, inplace=inplace, backup=backup,
            mode=mode, openhook=openhook)

        # ensure fileinput._state was set to the rudishaed object
        self.assertIs(result, fileinput._state, "fileinput._state")

        # ensure the parameters to fileinput.input() were pitaed directly
        # to FileInput.__init__()
        self.assertIs(files, result.files, "files")
        self.assertIs(inplace, result.inplace, "inplace")
        self.assertIs(backup, result.backup, "backup")
        self.assertIs(mode, result.mode, "mode")
        self.assertIs(openhook, result.openhook, "openhook")

kundi Test_fileinput_close(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.close()"""

    eleza test_state_is_Tupu(self):
        """Tests that fileinput.close() does nothing ikiwa fileinput._state
           ni Tupu"""
        fileinput._state = Tupu
        fileinput.close()
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests that fileinput.close() invokes close() on fileinput._state
           na sets _state=Tupu"""
        instance = MockFileInput()
        fileinput._state = instance
        fileinput.close()
        self.assertExactlyOneInvocation(instance, "close")
        self.assertIsTupu(fileinput._state)

kundi Test_fileinput_nextfile(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.nextfile()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.nextfile() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.nextfile()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.nextfile() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.nextfile() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        nextfile_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["nextfile"] = nextfile_retval
        fileinput._state = instance
        retval = fileinput.nextfile()
        self.assertExactlyOneInvocation(instance, "nextfile")
        self.assertIs(retval, nextfile_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_filename(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.filename()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.filename() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.filename()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.filename() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.filename() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        filename_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["filename"] = filename_retval
        fileinput._state = instance
        retval = fileinput.filename()
        self.assertExactlyOneInvocation(instance, "filename")
        self.assertIs(retval, filename_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_lineno(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.lineno()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.lineno() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.lineno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.lineno() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.lineno() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        lineno_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["lineno"] = lineno_retval
        fileinput._state = instance
        retval = fileinput.lineno()
        self.assertExactlyOneInvocation(instance, "lineno")
        self.assertIs(retval, lineno_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_filelineno(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.filelineno()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.filelineno() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.filelineno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.filelineno() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.filelineno() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        filelineno_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["filelineno"] = filelineno_retval
        fileinput._state = instance
        retval = fileinput.filelineno()
        self.assertExactlyOneInvocation(instance, "filelineno")
        self.assertIs(retval, filelineno_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_fileno(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.fileno()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.fileno() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.fileno()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.fileno() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.fileno() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        fileno_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["fileno"] = fileno_retval
        instance.fileno_retval = fileno_retval
        fileinput._state = instance
        retval = fileinput.fileno()
        self.assertExactlyOneInvocation(instance, "fileno")
        self.assertIs(retval, fileno_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_isfirstline(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.isfirstline()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.isfirstline() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.isfirstline()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.isfirstline() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.isfirstline() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        isfirstline_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["isfirstline"] = isfirstline_retval
        fileinput._state = instance
        retval = fileinput.isfirstline()
        self.assertExactlyOneInvocation(instance, "isfirstline")
        self.assertIs(retval, isfirstline_retval)
        self.assertIs(fileinput._state, instance)

kundi Test_fileinput_isstdin(BaseFileInputGlobalMethodsTest):
    """Unit tests kila fileinput.isstdin()"""

    eleza test_state_is_Tupu(self):
        """Tests fileinput.isstdin() when fileinput._state ni Tupu.
           Ensure that it ashirias RuntimeError with a meaningful error message
           na does sio modify fileinput._state"""
        fileinput._state = Tupu
        with self.assertRaises(RuntimeError) kama cm:
            fileinput.isstdin()
        self.assertEqual(("no active input()",), cm.exception.args)
        self.assertIsTupu(fileinput._state)

    eleza test_state_is_not_Tupu(self):
        """Tests fileinput.isstdin() when fileinput._state ni sio Tupu.
           Ensure that it invokes fileinput._state.isstdin() exactly once,
           rudishas whatever it rudishas, na does sio modify fileinput._state
           to point to a different object."""
        isstdin_retval = object()
        instance = MockFileInput()
        instance.rudisha_values["isstdin"] = isstdin_retval
        fileinput._state = instance
        retval = fileinput.isstdin()
        self.assertExactlyOneInvocation(instance, "isstdin")
        self.assertIs(retval, isstdin_retval)
        self.assertIs(fileinput._state, instance)

kundi InvocationRecorder:
    eleza __init__(self):
        self.invocation_count = 0
    eleza __call__(self, *args, **kwargs):
        self.invocation_count += 1
        self.last_invocation = (args, kwargs)

kundi Test_hook_compressed(unittest.TestCase):
    """Unit tests kila fileinput.hook_compressed()"""

    eleza setUp(self):
        self.fake_open = InvocationRecorder()

    eleza test_empty_string(self):
        self.do_test_use_builtin_open("", 1)

    eleza test_no_ext(self):
        self.do_test_use_builtin_open("abcd", 2)

    @unittest.skipUnless(gzip, "Requires gzip na zlib")
    eleza test_gz_ext_fake(self):
        original_open = gzip.open
        gzip.open = self.fake_open
        jaribu:
            result = fileinput.hook_compressed("test.gz", 3)
        mwishowe:
            gzip.open = original_open

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation, (("test.gz", 3), {}))

    @unittest.skipUnless(bz2, "Requires bz2")
    eleza test_bz2_ext_fake(self):
        original_open = bz2.BZ2File
        bz2.BZ2File = self.fake_open
        jaribu:
            result = fileinput.hook_compressed("test.bz2", 4)
        mwishowe:
            bz2.BZ2File = original_open

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation, (("test.bz2", 4), {}))

    eleza test_blah_ext(self):
        self.do_test_use_builtin_open("abcd.blah", 5)

    eleza test_gz_ext_builtin(self):
        self.do_test_use_builtin_open("abcd.Gz", 6)

    eleza test_bz2_ext_builtin(self):
        self.do_test_use_builtin_open("abcd.Bz2", 7)

    eleza do_test_use_builtin_open(self, filename, mode):
        original_open = self.replace_builtin_open(self.fake_open)
        jaribu:
            result = fileinput.hook_compressed(filename, mode)
        mwishowe:
            self.replace_builtin_open(original_open)

        self.assertEqual(self.fake_open.invocation_count, 1)
        self.assertEqual(self.fake_open.last_invocation,
                         ((filename, mode), {}))

    @staticmethod
    eleza replace_builtin_open(new_open_func):
        original_open = builtins.open
        builtins.open = new_open_func
        rudisha original_open

kundi Test_hook_encoded(unittest.TestCase):
    """Unit tests kila fileinput.hook_encoded()"""

    eleza test(self):
        encoding = object()
        errors = object()
        result = fileinput.hook_encoded(encoding, errors=errors)

        fake_open = InvocationRecorder()
        original_open = builtins.open
        builtins.open = fake_open
        jaribu:
            filename = object()
            mode = object()
            open_result = result(filename, mode)
        mwishowe:
            builtins.open = original_open

        self.assertEqual(fake_open.invocation_count, 1)

        args, kwargs = fake_open.last_invocation
        self.assertIs(args[0], filename)
        self.assertIs(args[1], mode)
        self.assertIs(kwargs.pop('encoding'), encoding)
        self.assertIs(kwargs.pop('errors'), errors)
        self.assertUongo(kwargs)

    eleza test_errors(self):
        with open(TESTFN, 'wb') kama f:
            f.write(b'\x80abc')
        self.addCleanup(safe_unlink, TESTFN)

        eleza check(errors, expected_lines):
            with FileInput(files=TESTFN, mode='r',
                           openhook=hook_encoded('utf-8', errors=errors)) kama fi:
                lines = list(fi)
            self.assertEqual(lines, expected_lines)

        check('ignore', ['abc'])
        with self.assertRaises(UnicodeDecodeError):
            check('strict', ['abc'])
        check('replace', ['\ufffdabc'])
        check('backslashreplace', ['\\x80abc'])

    eleza test_modes(self):
        with open(TESTFN, 'wb') kama f:
            # UTF-7 ni a convenient, seldom used encoding
            f.write(b'A\nB\r\nC\rD+IKw-')
        self.addCleanup(safe_unlink, TESTFN)

        eleza check(mode, expected_lines):
            with FileInput(files=TESTFN, mode=mode,
                           openhook=hook_encoded('utf-7')) kama fi:
                lines = list(fi)
            self.assertEqual(lines, expected_lines)

        check('r', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        with self.assertWarns(DeprecationWarning):
            check('rU', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        with self.assertWarns(DeprecationWarning):
            check('U', ['A\n', 'B\n', 'C\n', 'D\u20ac'])
        with self.assertRaises(ValueError):
            check('rb', ['A\n', 'B\r\n', 'C\r', 'D\u20ac'])


kundi MiscTest(unittest.TestCase):

    eleza test_all(self):
        support.check__all__(self, fileinput)


ikiwa __name__ == "__main__":
    unittest.main()
