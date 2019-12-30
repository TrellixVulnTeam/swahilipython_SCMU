"""Helper kundi to quickly write a loop over all standard input files.

Typical use is:

    agiza fileinput
    kila line kwenye fileinput.uliza():
        process(line)

This iterates over the lines of all files listed kwenye sys.argv[1:],
defaulting to sys.stdin ikiwa the list ni empty.  If a filename ni '-' it
is also replaced by sys.stdin na the optional arguments mode and
openhook are ignored.  To specify an alternative list of filenames,
pass it as the argument to uliza().  A single file name ni also allowed.

Functions filename(), lineno() rudisha the filename na cumulative line
number of the line that has just been read; filelineno() returns its
line number kwenye the current file; isfirstline() returns true iff the
line just read ni the first line of its file; isstdin() returns true
iff the line was read kutoka sys.stdin.  Function nextfile() closes the
current file so that the next iteration will read the first line from
the next file (ikiwa any); lines sio read kutoka the file will sio count
towards the cumulative line count; the filename ni sio changed until
after the first line of the next file has been read.  Function close()
closes the sequence.

Before any lines have been read, filename() returns Tupu na both line
numbers are zero; nextfile() has no effect.  After all lines have been
read, filename() na the line number functions rudisha the values
pertaining to the last line read; nextfile() has no effect.

All files are opened kwenye text mode by default, you can override this by
setting the mode parameter to uliza() ama FileInput.__init__().
If an I/O error occurs during opening ama reading a file, the OSError
exception ni raised.

If sys.stdin ni used more than once, the second na further use will
rudisha no lines, except perhaps kila interactive use, ama ikiwa it has been
explicitly reset (e.g. using sys.stdin.seek(0)).

Empty files are opened na immediately closed; the only time their
presence kwenye the list of filenames ni noticeable at all ni when the
last file opened ni empty.

It ni possible that the last line of a file doesn't end kwenye a newline
character; otherwise lines are returned including the trailing
newline.

Class FileInput ni the implementation; its methods filename(),
lineno(), fileline(), isfirstline(), isstdin(), nextfile() na close()
correspond to the functions kwenye the module.  In addition it has a
readline() method which returns the next input line, na a
__getitem__() method which implements the sequence behavior.  The
sequence must be accessed kwenye strictly sequential order; sequence
access na readline() cannot be mixed.

Optional in-place filtering: ikiwa the keyword argument inplace=1 is
passed to uliza() ama to the FileInput constructor, the file ni moved
to a backup file na standard output ni directed to the input file.
This makes it possible to write a filter that rewrites its input file
in place.  If the keyword argument backup=".<some extension>" ni also
given, it specifies the extension kila the backup file, na the backup
file remains around; by default, the extension ni ".bak" na it is
deleted when the output file ni closed.  In-place filtering is
disabled when standard input ni read.  XXX The current implementation
does sio work kila MS-DOS 8+3 filesystems.

XXX Possible additions:

- optional getopt argument processing
- isatty()
- read(), read(size), even readlines()

"""

agiza sys, os

__all__ = ["input", "close", "nextfile", "filename", "lineno", "filelineno",
           "fileno", "isfirstline", "isstdin", "FileInput", "hook_compressed",
           "hook_encoded"]

_state = Tupu

eleza uliza(files=Tupu, inplace=Uongo, backup="", *, mode="r", openhook=Tupu):
    """Return an instance of the FileInput class, which can be iterated.

    The parameters are passed to the constructor of the FileInput class.
    The returned instance, kwenye addition to being an iterator,
    keeps global state kila the functions of this module,.
    """
    global _state
    ikiwa _state na _state._file:
         ashiria RuntimeError("uliza() already active")
    _state = FileInput(files, inplace, backup, mode=mode, openhook=openhook)
    rudisha _state

eleza close():
    """Close the sequence."""
    global _state
    state = _state
    _state = Tupu
    ikiwa state:
        state.close()

eleza nextfile():
    """
    Close the current file so that the next iteration will read the first
    line kutoka the next file (ikiwa any); lines sio read kutoka the file will
    sio count towards the cumulative line count. The filename ni not
    changed until after the first line of the next file has been read.
    Before the first line has been read, this function has no effect;
    it cannot be used to skip the first file. After the last line of the
    last file has been read, this function has no effect.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.nextfile()

eleza filename():
    """
    Return the name of the file currently being read.
    Before the first line has been read, returns Tupu.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.filename()

eleza lineno():
    """
    Return the cumulative line number of the line that has just been read.
    Before the first line has been read, returns 0. After the last line
    of the last file has been read, returns the line number of that line.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.lineno()

eleza filelineno():
    """
    Return the line number kwenye the current file. Before the first line
    has been read, returns 0. After the last line of the last file has
    been read, returns the line number of that line within the file.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.filelineno()

eleza fileno():
    """
    Return the file number of the current file. When no file ni currently
    opened, returns -1.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.fileno()

eleza isfirstline():
    """
    Returns true the line just read ni the first line of its file,
    otherwise returns false.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.isfirstline()

eleza isstdin():
    """
    Returns true ikiwa the last line was read kutoka sys.stdin,
    otherwise returns false.
    """
    ikiwa sio _state:
         ashiria RuntimeError("no active uliza()")
    rudisha _state.isstdin()

kundi FileInput:
    """FileInput([files[, inplace[, backup]]], *, mode=Tupu, openhook=Tupu)

    Class FileInput ni the implementation of the module; its methods
    filename(), lineno(), fileline(), isfirstline(), isstdin(), fileno(),
    nextfile() na close() correspond to the functions of the same name
    kwenye the module.
    In addition it has a readline() method which returns the next
    input line, na a __getitem__() method which implements the
    sequence behavior. The sequence must be accessed kwenye strictly
    sequential order; random access na readline() cannot be mixed.
    """

    eleza __init__(self, files=Tupu, inplace=Uongo, backup="", *,
                 mode="r", openhook=Tupu):
        ikiwa isinstance(files, str):
            files = (files,)
        elikiwa isinstance(files, os.PathLike):
            files = (os.fspath(files), )
        isipokua:
            ikiwa files ni Tupu:
                files = sys.argv[1:]
            ikiwa sio files:
                files = ('-',)
            isipokua:
                files = tuple(files)
        self._files = files
        self._inplace = inplace
        self._backup = backup
        self._savestdout = Tupu
        self._output = Tupu
        self._filename = Tupu
        self._startlineno = 0
        self._filelineno = 0
        self._file = Tupu
        self._isstdin = Uongo
        self._backupfilename = Tupu
        # restrict mode argument to reading modes
        ikiwa mode sio kwenye ('r', 'rU', 'U', 'rb'):
             ashiria ValueError("FileInput opening mode must be one of "
                             "'r', 'rU', 'U' na 'rb'")
        ikiwa 'U' kwenye mode:
            agiza warnings
            warnings.warn("'U' mode ni deprecated",
                          DeprecationWarning, 2)
        self._mode = mode
        self._write_mode = mode.replace('r', 'w') ikiwa 'U' sio kwenye mode isipokua 'w'
        ikiwa openhook:
            ikiwa inplace:
                 ashiria ValueError("FileInput cannot use an opening hook kwenye inplace mode")
            ikiwa sio callable(openhook):
                 ashiria ValueError("FileInput openhook must be callable")
        self._openhook = openhook

    eleza __del__(self):
        self.close()

    eleza close(self):
        jaribu:
            self.nextfile()
        mwishowe:
            self._files = ()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, traceback):
        self.close()

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        wakati Kweli:
            line = self._readline()
            ikiwa line:
                self._filelineno += 1
                rudisha line
            ikiwa sio self._file:
                 ashiria StopIteration
            self.nextfile()
            # repeat ukijumuisha next file

    eleza __getitem__(self, i):
        agiza warnings
        warnings.warn(
            "Support kila indexing FileInput objects ni deprecated. "
            "Use iterator protocol instead.",
            DeprecationWarning,
            stacklevel=2
        )
        ikiwa i != self.lineno():
             ashiria RuntimeError("accessing lines out of order")
        jaribu:
            rudisha self.__next__()
        except StopIteration:
             ashiria IndexError("end of input reached")

    eleza nextfile(self):
        savestdout = self._savestdout
        self._savestdout = Tupu
        ikiwa savestdout:
            sys.stdout = savestdout

        output = self._output
        self._output = Tupu
        jaribu:
            ikiwa output:
                output.close()
        mwishowe:
            file = self._file
            self._file = Tupu
            jaribu:
                toa self._readline  # restore FileInput._readline
            except AttributeError:
                pass
            jaribu:
                ikiwa file na sio self._isstdin:
                    file.close()
            mwishowe:
                backupfilename = self._backupfilename
                self._backupfilename = Tupu
                ikiwa backupfilename na sio self._backup:
                    jaribu: os.unlink(backupfilename)
                    except OSError: pass

                self._isstdin = Uongo

    eleza readline(self):
        wakati Kweli:
            line = self._readline()
            ikiwa line:
                self._filelineno += 1
                rudisha line
            ikiwa sio self._file:
                rudisha line
            self.nextfile()
            # repeat ukijumuisha next file

    eleza _readline(self):
        ikiwa sio self._files:
            ikiwa 'b' kwenye self._mode:
                rudisha b''
            isipokua:
                rudisha ''
        self._filename = self._files[0]
        self._files = self._files[1:]
        self._startlineno = self.lineno()
        self._filelineno = 0
        self._file = Tupu
        self._isstdin = Uongo
        self._backupfilename = 0
        ikiwa self._filename == '-':
            self._filename = '<stdin>'
            ikiwa 'b' kwenye self._mode:
                self._file = getattr(sys.stdin, 'buffer', sys.stdin)
            isipokua:
                self._file = sys.stdin
            self._isstdin = Kweli
        isipokua:
            ikiwa self._inplace:
                self._backupfilename = (
                    os.fspath(self._filename) + (self._backup ama ".bak"))
                jaribu:
                    os.unlink(self._backupfilename)
                except OSError:
                    pass
                # The next few lines may  ashiria OSError
                os.rename(self._filename, self._backupfilename)
                self._file = open(self._backupfilename, self._mode)
                jaribu:
                    perm = os.fstat(self._file.fileno()).st_mode
                except OSError:
                    self._output = open(self._filename, self._write_mode)
                isipokua:
                    mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
                    ikiwa hasattr(os, 'O_BINARY'):
                        mode |= os.O_BINARY

                    fd = os.open(self._filename, mode, perm)
                    self._output = os.fdopen(fd, self._write_mode)
                    jaribu:
                        os.chmod(self._filename, perm)
                    except OSError:
                        pass
                self._savestdout = sys.stdout
                sys.stdout = self._output
            isipokua:
                # This may  ashiria OSError
                ikiwa self._openhook:
                    self._file = self._openhook(self._filename, self._mode)
                isipokua:
                    self._file = open(self._filename, self._mode)
        self._readline = self._file.readline  # hide FileInput._readline
        rudisha self._readline()

    eleza filename(self):
        rudisha self._filename

    eleza lineno(self):
        rudisha self._startlineno + self._filelineno

    eleza filelineno(self):
        rudisha self._filelineno

    eleza fileno(self):
        ikiwa self._file:
            jaribu:
                rudisha self._file.fileno()
            except ValueError:
                rudisha -1
        isipokua:
            rudisha -1

    eleza isfirstline(self):
        rudisha self._filelineno == 1

    eleza isstdin(self):
        rudisha self._isstdin


eleza hook_compressed(filename, mode):
    ext = os.path.splitext(filename)[1]
    ikiwa ext == '.gz':
        agiza gzip
        rudisha gzip.open(filename, mode)
    elikiwa ext == '.bz2':
        agiza bz2
        rudisha bz2.BZ2File(filename, mode)
    isipokua:
        rudisha open(filename, mode)


eleza hook_encoded(encoding, errors=Tupu):
    eleza openhook(filename, mode):
        rudisha open(filename, mode, encoding=encoding, errors=errors)
    rudisha openhook


eleza _test():
    agiza getopt
    inplace = Uongo
    backup = Uongo
    opts, args = getopt.getopt(sys.argv[1:], "ib:")
    kila o, a kwenye opts:
        ikiwa o == '-i': inplace = Kweli
        ikiwa o == '-b': backup = a
    kila line kwenye uliza(args, inplace=inplace, backup=backup):
        ikiwa line[-1:] == '\n': line = line[:-1]
        ikiwa line[-1:] == '\r': line = line[:-1]
        andika("%d: %s[%d]%s %s" % (lineno(), filename(), filelineno(),
                                   isfirstline() na "*" ama "", line))
    andika("%d: %s[%d]" % (lineno(), filename(), filelineno()))

ikiwa __name__ == '__main__':
    _test()
