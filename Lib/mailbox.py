"""Read/write support for Maildir, mbox, MH, Babyl, and MMDF mailboxes."""

# Notes for authors of new mailbox subclasses:
#
# Remember to fsync() changes to disk before closing a modified file
# or returning kutoka a flush() method.  See functions _sync_flush() and
# _sync_close().

agiza os
agiza time
agiza calendar
agiza socket
agiza errno
agiza copy
agiza warnings
agiza email
agiza email.message
agiza email.generator
agiza io
agiza contextlib
try:
    agiza fcntl
except ImportError:
    fcntl = None

__all__ = ['Mailbox', 'Maildir', 'mbox', 'MH', 'Babyl', 'MMDF',
           'Message', 'MaildirMessage', 'mboxMessage', 'MHMessage',
           'BabylMessage', 'MMDFMessage', 'Error', 'NoSuchMailboxError',
           'NotEmptyError', 'ExternalClashError', 'FormatError']

linesep = os.linesep.encode('ascii')

kundi Mailbox:
    """A group of messages in a particular place."""

    eleza __init__(self, path, factory=None, create=True):
        """Initialize a Mailbox instance."""
        self._path = os.path.abspath(os.path.expanduser(path))
        self._factory = factory

    eleza add(self, message):
        """Add message and rudisha assigned key."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza remove(self, key):
        """Remove the keyed message; raise KeyError ikiwa it doesn't exist."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza __delitem__(self, key):
        self.remove(key)

    eleza discard(self, key):
        """If the keyed message exists, remove it."""
        try:
            self.remove(key)
        except KeyError:
            pass

    eleza __setitem__(self, key, message):
        """Replace the keyed message; raise KeyError ikiwa it doesn't exist."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza get(self, key, default=None):
        """Return the keyed message, or default ikiwa it doesn't exist."""
        try:
            rudisha self.__getitem__(key)
        except KeyError:
            rudisha default

    eleza __getitem__(self, key):
        """Return the keyed message; raise KeyError ikiwa it doesn't exist."""
        ikiwa not self._factory:
            rudisha self.get_message(key)
        else:
            with contextlib.closing(self.get_file(key)) as file:
                rudisha self._factory(file)

    eleza get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza get_string(self, key):
        """Return a string representation or raise a KeyError.

        Uses email.message.Message to create a 7bit clean string
        representation of the message."""
        rudisha email.message_kutoka_bytes(self.get_bytes(key)).as_string()

    eleza get_bytes(self, key):
        """Return a byte string representation or raise a KeyError."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza get_file(self, key):
        """Return a file-like representation or raise a KeyError."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza iterkeys(self):
        """Return an iterator over keys."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza keys(self):
        """Return a list of keys."""
        rudisha list(self.iterkeys())

    eleza itervalues(self):
        """Return an iterator over all messages."""
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue
            yield value

    eleza __iter__(self):
        rudisha self.itervalues()

    eleza values(self):
        """Return a list of messages. Memory intensive."""
        rudisha list(self.itervalues())

    eleza iteritems(self):
        """Return an iterator over (key, message) tuples."""
        for key in self.iterkeys():
            try:
                value = self[key]
            except KeyError:
                continue
            yield (key, value)

    eleza items(self):
        """Return a list of (key, message) tuples. Memory intensive."""
        rudisha list(self.iteritems())

    eleza __contains__(self, key):
        """Return True ikiwa the keyed message exists, False otherwise."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza __len__(self):
        """Return a count of messages in the mailbox."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza clear(self):
        """Delete all messages."""
        for key in self.keys():
            self.discard(key)

    eleza pop(self, key, default=None):
        """Delete the keyed message and rudisha it, or default."""
        try:
            result = self[key]
        except KeyError:
            rudisha default
        self.discard(key)
        rudisha result

    eleza popitem(self):
        """Delete an arbitrary (key, message) pair and rudisha it."""
        for key in self.iterkeys():
            rudisha (key, self.pop(key))     # This is only run once.
        else:
            raise KeyError('No messages in mailbox')

    eleza update(self, arg=None):
        """Change the messages that correspond to certain keys."""
        ikiwa hasattr(arg, 'iteritems'):
            source = arg.iteritems()
        elikiwa hasattr(arg, 'items'):
            source = arg.items()
        else:
            source = arg
        bad_key = False
        for key, message in source:
            try:
                self[key] = message
            except KeyError:
                bad_key = True
        ikiwa bad_key:
            raise KeyError('No message with key(s)')

    eleza flush(self):
        """Write any pending changes to the disk."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza lock(self):
        """Lock the mailbox."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza unlock(self):
        """Unlock the mailbox ikiwa it is locked."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza close(self):
        """Flush and close the mailbox."""
        raise NotImplementedError('Method must be implemented by subclass')

    eleza _string_to_bytes(self, message):
        # If a message is not 7bit clean, we refuse to handle it since it
        # likely came kutoka reading invalid messages in text mode, and that way
        # lies mojibake.
        try:
            rudisha message.encode('ascii')
        except UnicodeError:
            raise ValueError("String input must be ASCII-only; "
                "use bytes or a Message instead")

    # Whether each message must end in a newline
    _append_newline = False

    eleza _dump_message(self, message, target, mangle_kutoka_=False):
        # This assumes the target file is open in binary mode.
        """Dump message contents to target file."""
        ikiwa isinstance(message, email.message.Message):
            buffer = io.BytesIO()
            gen = email.generator.BytesGenerator(buffer, mangle_kutoka_, 0)
            gen.flatten(message)
            buffer.seek(0)
            data = buffer.read()
            data = data.replace(b'\n', linesep)
            target.write(data)
            ikiwa self._append_newline and not data.endswith(linesep):
                # Make sure the message ends with a newline
                target.write(linesep)
        elikiwa isinstance(message, (str, bytes, io.StringIO)):
            ikiwa isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input is deprecated, "
                    "use BytesIO instead", DeprecationWarning, 3)
                message = message.getvalue()
            ikiwa isinstance(message, str):
                message = self._string_to_bytes(message)
            ikiwa mangle_kutoka_:
                message = message.replace(b'\nFrom ', b'\n>From ')
            message = message.replace(b'\n', linesep)
            target.write(message)
            ikiwa self._append_newline and not message.endswith(linesep):
                # Make sure the message ends with a newline
                target.write(linesep)
        elikiwa hasattr(message, 'read'):
            ikiwa hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files is deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            lastline = None
            while True:
                line = message.readline()
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                elikiwa line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                ikiwa not line:
                    break
                ikiwa mangle_kutoka_ and line.startswith(b'From '):
                    line = b'>From ' + line[5:]
                line = line.replace(b'\n', linesep)
                target.write(line)
                lastline = line
            ikiwa self._append_newline and lastline and not lastline.endswith(linesep):
                # Make sure the message ends with a newline
                target.write(linesep)
        else:
            raise TypeError('Invalid message type: %s' % type(message))


kundi Maildir(Mailbox):
    """A qmail-style Maildir mailbox."""

    colon = ':'

    eleza __init__(self, dirname, factory=None, create=True):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, dirname, factory, create)
        self._paths = {
            'tmp': os.path.join(self._path, 'tmp'),
            'new': os.path.join(self._path, 'new'),
            'cur': os.path.join(self._path, 'cur'),
            }
        ikiwa not os.path.exists(self._path):
            ikiwa create:
                os.mkdir(self._path, 0o700)
                for path in self._paths.values():
                    os.mkdir(path, 0o700)
            else:
                raise NoSuchMailboxError(self._path)
        self._toc = {}
        self._toc_mtimes = {'cur': 0, 'new': 0}
        self._last_read = 0         # Records last time we read cur/new
        self._skewfactor = 0.1      # Adjust ikiwa os/fs clocks are skewing

    eleza add(self, message):
        """Add message and rudisha assigned key."""
        tmp_file = self._create_tmp()
        try:
            self._dump_message(message, tmp_file)
        except BaseException:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise
        _sync_close(tmp_file)
        ikiwa isinstance(message, MaildirMessage):
            subdir = message.get_subdir()
            suffix = self.colon + message.get_info()
            ikiwa suffix == self.colon:
                suffix = ''
        else:
            subdir = 'new'
            suffix = ''
        uniq = os.path.basename(tmp_file.name).split(self.colon)[0]
        dest = os.path.join(self._path, subdir, uniq + suffix)
        ikiwa isinstance(message, MaildirMessage):
            os.utime(tmp_file.name,
                     (os.path.getatime(tmp_file.name), message.get_date()))
        # No file modification should be done after the file is moved to its
        # final position in order to prevent race conditions with changes
        # kutoka other programs
        try:
            try:
                os.link(tmp_file.name, dest)
            except (AttributeError, PermissionError):
                os.rename(tmp_file.name, dest)
            else:
                os.remove(tmp_file.name)
        except OSError as e:
            os.remove(tmp_file.name)
            ikiwa e.errno == errno.EEXIST:
                raise ExternalClashError('Name clash with existing message: %s'
                                         % dest)
            else:
                raise
        rudisha uniq

    eleza remove(self, key):
        """Remove the keyed message; raise KeyError ikiwa it doesn't exist."""
        os.remove(os.path.join(self._path, self._lookup(key)))

    eleza discard(self, key):
        """If the keyed message exists, remove it."""
        # This overrides an inapplicable implementation in the superclass.
        try:
            self.remove(key)
        except (KeyError, FileNotFoundError):
            pass

    eleza __setitem__(self, key, message):
        """Replace the keyed message; raise KeyError ikiwa it doesn't exist."""
        old_subpath = self._lookup(key)
        temp_key = self.add(message)
        temp_subpath = self._lookup(temp_key)
        ikiwa isinstance(message, MaildirMessage):
            # temp's subdir and suffix were specified by message.
            dominant_subpath = temp_subpath
        else:
            # temp's subdir and suffix were defaults kutoka add().
            dominant_subpath = old_subpath
        subdir = os.path.dirname(dominant_subpath)
        ikiwa self.colon in dominant_subpath:
            suffix = self.colon + dominant_subpath.split(self.colon)[-1]
        else:
            suffix = ''
        self.discard(key)
        tmp_path = os.path.join(self._path, temp_subpath)
        new_path = os.path.join(self._path, subdir, key + suffix)
        ikiwa isinstance(message, MaildirMessage):
            os.utime(tmp_path,
                     (os.path.getatime(tmp_path), message.get_date()))
        # No file modification should be done after the file is moved to its
        # final position in order to prevent race conditions with changes
        # kutoka other programs
        os.rename(tmp_path, new_path)

    eleza get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        subpath = self._lookup(key)
        with open(os.path.join(self._path, subpath), 'rb') as f:
            ikiwa self._factory:
                msg = self._factory(f)
            else:
                msg = MaildirMessage(f)
        subdir, name = os.path.split(subpath)
        msg.set_subdir(subdir)
        ikiwa self.colon in name:
            msg.set_info(name.split(self.colon)[-1])
        msg.set_date(os.path.getmtime(os.path.join(self._path, subpath)))
        rudisha msg

    eleza get_bytes(self, key):
        """Return a bytes representation or raise a KeyError."""
        with open(os.path.join(self._path, self._lookup(key)), 'rb') as f:
            rudisha f.read().replace(linesep, b'\n')

    eleza get_file(self, key):
        """Return a file-like representation or raise a KeyError."""
        f = open(os.path.join(self._path, self._lookup(key)), 'rb')
        rudisha _ProxyFile(f)

    eleza iterkeys(self):
        """Return an iterator over keys."""
        self._refresh()
        for key in self._toc:
            try:
                self._lookup(key)
            except KeyError:
                continue
            yield key

    eleza __contains__(self, key):
        """Return True ikiwa the keyed message exists, False otherwise."""
        self._refresh()
        rudisha key in self._toc

    eleza __len__(self):
        """Return a count of messages in the mailbox."""
        self._refresh()
        rudisha len(self._toc)

    eleza flush(self):
        """Write any pending changes to disk."""
        # Maildir changes are always written immediately, so there's nothing
        # to do.
        pass

    eleza lock(self):
        """Lock the mailbox."""
        return

    eleza unlock(self):
        """Unlock the mailbox ikiwa it is locked."""
        return

    eleza close(self):
        """Flush and close the mailbox."""
        return

    eleza list_folders(self):
        """Return a list of folder names."""
        result = []
        for entry in os.listdir(self._path):
            ikiwa len(entry) > 1 and entry[0] == '.' and \
               os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry[1:])
        rudisha result

    eleza get_folder(self, folder):
        """Return a Maildir instance for the named folder."""
        rudisha Maildir(os.path.join(self._path, '.' + folder),
                       factory=self._factory,
                       create=False)

    eleza add_folder(self, folder):
        """Create a folder and rudisha a Maildir instance representing it."""
        path = os.path.join(self._path, '.' + folder)
        result = Maildir(path, factory=self._factory)
        maildirfolder_path = os.path.join(path, 'maildirfolder')
        ikiwa not os.path.exists(maildirfolder_path):
            os.close(os.open(maildirfolder_path, os.O_CREAT | os.O_WRONLY,
                0o666))
        rudisha result

    eleza remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, '.' + folder)
        for entry in os.listdir(os.path.join(path, 'new')) + \
                     os.listdir(os.path.join(path, 'cur')):
            ikiwa len(entry) < 1 or entry[0] != '.':
                raise NotEmptyError('Folder contains message(s): %s' % folder)
        for entry in os.listdir(path):
            ikiwa entry != 'new' and entry != 'cur' and entry != 'tmp' and \
               os.path.isdir(os.path.join(path, entry)):
                raise NotEmptyError("Folder contains subdirectory '%s': %s" %
                                    (folder, entry))
        for root, dirs, files in os.walk(path, topdown=False):
            for entry in files:
                os.remove(os.path.join(root, entry))
            for entry in dirs:
                os.rmdir(os.path.join(root, entry))
        os.rmdir(path)

    eleza clean(self):
        """Delete old files in "tmp"."""
        now = time.time()
        for entry in os.listdir(os.path.join(self._path, 'tmp')):
            path = os.path.join(self._path, 'tmp', entry)
            ikiwa now - os.path.getatime(path) > 129600:   # 60 * 60 * 36
                os.remove(path)

    _count = 1  # This is used to generate unique file names.

    eleza _create_tmp(self):
        """Create a file in the tmp subdirectory and open and rudisha it."""
        now = time.time()
        hostname = socket.gethostname()
        ikiwa '/' in hostname:
            hostname = hostname.replace('/', r'\057')
        ikiwa ':' in hostname:
            hostname = hostname.replace(':', r'\072')
        uniq = "%s.M%sP%sQ%s.%s" % (int(now), int(now % 1 * 1e6), os.getpid(),
                                    Maildir._count, hostname)
        path = os.path.join(self._path, 'tmp', uniq)
        try:
            os.stat(path)
        except FileNotFoundError:
            Maildir._count += 1
            try:
                rudisha _create_carefully(path)
            except FileExistsError:
                pass

        # Fall through to here ikiwa stat succeeded or open raised EEXIST.
        raise ExternalClashError('Name clash prevented file creation: %s' %
                                 path)

    eleza _refresh(self):
        """Update table of contents mapping."""
        # If it has been less than two seconds since the last _refresh() call,
        # we have to unconditionally re-read the mailbox just in case it has
        # been modified, because os.path.mtime() has a 2 sec resolution in the
        # most common worst case (FAT) and a 1 sec resolution typically.  This
        # results in a few unnecessary re-reads when _refresh() is called
        # multiple times in that interval, but once the clock ticks over, we
        # will only re-read as needed.  Because the filesystem might be being
        # served by an independent system with its own clock, we record and
        # compare with the mtimes kutoka the filesystem.  Because the other
        # system's clock might be skewing relative to our clock, we add an
        # extra delta to our wait.  The default is one tenth second, but is an
        # instance variable and so can be adjusted ikiwa dealing with a
        # particularly skewed or irregular system.
        ikiwa time.time() - self._last_read > 2 + self._skewfactor:
            refresh = False
            for subdir in self._toc_mtimes:
                mtime = os.path.getmtime(self._paths[subdir])
                ikiwa mtime > self._toc_mtimes[subdir]:
                    refresh = True
                self._toc_mtimes[subdir] = mtime
            ikiwa not refresh:
                return
        # Refresh toc
        self._toc = {}
        for subdir in self._toc_mtimes:
            path = self._paths[subdir]
            for entry in os.listdir(path):
                p = os.path.join(path, entry)
                ikiwa os.path.isdir(p):
                    continue
                uniq = entry.split(self.colon)[0]
                self._toc[uniq] = os.path.join(subdir, entry)
        self._last_read = time.time()

    eleza _lookup(self, key):
        """Use TOC to rudisha subpath for given key, or raise a KeyError."""
        try:
            ikiwa os.path.exists(os.path.join(self._path, self._toc[key])):
                rudisha self._toc[key]
        except KeyError:
            pass
        self._refresh()
        try:
            rudisha self._toc[key]
        except KeyError:
            raise KeyError('No message with key: %s' % key) kutoka None

    # This method is for backward compatibility only.
    eleza next(self):
        """Return the next message in a one-time iteration."""
        ikiwa not hasattr(self, '_onetime_keys'):
            self._onetime_keys = self.iterkeys()
        while True:
            try:
                rudisha self[next(self._onetime_keys)]
            except StopIteration:
                rudisha None
            except KeyError:
                continue


kundi _singlefileMailbox(Mailbox):
    """A single-file mailbox."""

    eleza __init__(self, path, factory=None, create=True):
        """Initialize a single-file mailbox."""
        Mailbox.__init__(self, path, factory, create)
        try:
            f = open(self._path, 'rb+')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                ikiwa create:
                    f = open(self._path, 'wb+')
                else:
                    raise NoSuchMailboxError(self._path)
            elikiwa e.errno in (errno.EACCES, errno.EROFS):
                f = open(self._path, 'rb')
            else:
                raise
        self._file = f
        self._toc = None
        self._next_key = 0
        self._pending = False       # No changes require rewriting the file.
        self._pending_sync = False  # No need to sync the file
        self._locked = False
        self._file_length = None    # Used to record mailbox size

    eleza add(self, message):
        """Add message and rudisha assigned key."""
        self._lookup()
        self._toc[self._next_key] = self._append_message(message)
        self._next_key += 1
        # _append_message appends the message to the mailbox file. We
        # don't need a full rewrite + rename, sync is enough.
        self._pending_sync = True
        rudisha self._next_key - 1

    eleza remove(self, key):
        """Remove the keyed message; raise KeyError ikiwa it doesn't exist."""
        self._lookup(key)
        del self._toc[key]
        self._pending = True

    eleza __setitem__(self, key, message):
        """Replace the keyed message; raise KeyError ikiwa it doesn't exist."""
        self._lookup(key)
        self._toc[key] = self._append_message(message)
        self._pending = True

    eleza iterkeys(self):
        """Return an iterator over keys."""
        self._lookup()
        yield kutoka self._toc.keys()

    eleza __contains__(self, key):
        """Return True ikiwa the keyed message exists, False otherwise."""
        self._lookup()
        rudisha key in self._toc

    eleza __len__(self):
        """Return a count of messages in the mailbox."""
        self._lookup()
        rudisha len(self._toc)

    eleza lock(self):
        """Lock the mailbox."""
        ikiwa not self._locked:
            _lock_file(self._file)
            self._locked = True

    eleza unlock(self):
        """Unlock the mailbox ikiwa it is locked."""
        ikiwa self._locked:
            _unlock_file(self._file)
            self._locked = False

    eleza flush(self):
        """Write any pending changes to disk."""
        ikiwa not self._pending:
            ikiwa self._pending_sync:
                # Messages have only been added, so syncing the file
                # is enough.
                _sync_flush(self._file)
                self._pending_sync = False
            return

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding or deleting an item).
        assert self._toc is not None

        # Check length of self._file; ikiwa it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        ikiwa cur_len != self._file_length:
            raise ExternalClashError('Size of mailbox file changed '
                                     '(expected %i, found %i)' %
                                     (self._file_length, cur_len))

        new_file = _create_temporary(self._path)
        try:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            for key in sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                while True:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    ikiwa not buffer:
                        break
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()
        except:
            new_file.close()
            os.remove(new_file.name)
            raise
        _sync_close(new_file)
        # self._file is about to get replaced, so no need to sync.
        self._file.close()
        # Make sure the new file's mode is the same as the old file's
        mode = os.stat(self._path).st_mode
        os.chmod(new_file.name, mode)
        try:
            os.rename(new_file.name, self._path)
        except FileExistsError:
            os.remove(self._path)
            os.rename(new_file.name, self._path)
        self._file = open(self._path, 'rb+')
        self._toc = new_toc
        self._pending = False
        self._pending_sync = False
        ikiwa self._locked:
            _lock_file(self._file, dotlock=False)

    eleza _pre_mailbox_hook(self, f):
        """Called before writing the mailbox to file f."""
        return

    eleza _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        return

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        return

    eleza close(self):
        """Flush and close the mailbox."""
        try:
            self.flush()
        finally:
            try:
                ikiwa self._locked:
                    self.unlock()
            finally:
                self._file.close()  # Sync has been done by self.flush() above.

    eleza _lookup(self, key=None):
        """Return (start, stop) or raise KeyError."""
        ikiwa self._toc is None:
            self._generate_toc()
        ikiwa key is not None:
            try:
                rudisha self._toc[key]
            except KeyError:
                raise KeyError('No message with key: %s' % key) kutoka None

    eleza _append_message(self, message):
        """Append message to mailbox and rudisha (start, stop) offsets."""
        self._file.seek(0, 2)
        before = self._file.tell()
        ikiwa len(self._toc) == 0 and not self._pending:
            # This is the first message, and the _pre_mailbox_hook
            # hasn't yet been called. If self._pending is True,
            # messages have been removed, so _pre_mailbox_hook must
            # have been called already.
            self._pre_mailbox_hook(self._file)
        try:
            self._pre_message_hook(self._file)
            offsets = self._install_message(message)
            self._post_message_hook(self._file)
        except BaseException:
            self._file.truncate(before)
            raise
        self._file.flush()
        self._file_length = self._file.tell()  # Record current length of mailbox
        rudisha offsets



kundi _mboxMMDF(_singlefileMailbox):
    """An mbox or MMDF mailbox."""

    _mangle_kutoka_ = True

    eleza get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        kutoka_line = self._file.readline().replace(linesep, b'')
        string = self._file.read(stop - self._file.tell())
        msg = self._message_factory(string.replace(linesep, b'\n'))
        msg.set_kutoka(kutoka_line[5:].decode('ascii'))
        rudisha msg

    eleza get_string(self, key, kutoka_=False):
        """Return a string representation or raise a KeyError."""
        rudisha email.message_kutoka_bytes(
            self.get_bytes(key, kutoka_)).as_string(unixkutoka=kutoka_)

    eleza get_bytes(self, key, kutoka_=False):
        """Return a string representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        ikiwa not kutoka_:
            self._file.readline()
        string = self._file.read(stop - self._file.tell())
        rudisha string.replace(linesep, b'\n')

    eleza get_file(self, key, kutoka_=False):
        """Return a file-like representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        ikiwa not kutoka_:
            self._file.readline()
        rudisha _PartialFile(self._file, self._file.tell(), stop)

    eleza _install_message(self, message):
        """Format a message and blindly write to self._file."""
        kutoka_line = None
        ikiwa isinstance(message, str):
            message = self._string_to_bytes(message)
        ikiwa isinstance(message, bytes) and message.startswith(b'From '):
            newline = message.find(b'\n')
            ikiwa newline != -1:
                kutoka_line = message[:newline]
                message = message[newline + 1:]
            else:
                kutoka_line = message
                message = b''
        elikiwa isinstance(message, _mboxMMDFMessage):
            author = message.get_kutoka().encode('ascii')
            kutoka_line = b'From ' + author
        elikiwa isinstance(message, email.message.Message):
            kutoka_line = message.get_unixkutoka()  # May be None.
            ikiwa kutoka_line is not None:
                kutoka_line = kutoka_line.encode('ascii')
        ikiwa kutoka_line is None:
            kutoka_line = b'From MAILER-DAEMON ' + time.asctime(time.gmtime()).encode()
        start = self._file.tell()
        self._file.write(kutoka_line + linesep)
        self._dump_message(message, self._file, self._mangle_kutoka_)
        stop = self._file.tell()
        rudisha (start, stop)


kundi mbox(_mboxMMDF):
    """A classic mbox mailbox."""

    _mangle_kutoka_ = True

    # All messages must end in a newline character, and
    # _post_message_hooks outputs an empty line between messages.
    _append_newline = True

    eleza __init__(self, path, factory=None, create=True):
        """Initialize an mbox mailbox."""
        self._message_factory = mboxMessage
        _mboxMMDF.__init__(self, path, factory, create)

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep)

    eleza _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        last_was_empty = False
        self._file.seek(0)
        while True:
            line_pos = self._file.tell()
            line = self._file.readline()
            ikiwa line.startswith(b'From '):
                ikiwa len(stops) < len(starts):
                    ikiwa last_was_empty:
                        stops.append(line_pos - len(linesep))
                    else:
                        # The last line before the "From " line wasn't
                        # blank, but we consider it a start of a
                        # message anyway.
                        stops.append(line_pos)
                starts.append(line_pos)
                last_was_empty = False
            elikiwa not line:
                ikiwa last_was_empty:
                    stops.append(line_pos - len(linesep))
                else:
                    stops.append(line_pos)
                break
            elikiwa line == linesep:
                last_was_empty = True
            else:
                last_was_empty = False
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()


kundi MMDF(_mboxMMDF):
    """An MMDF mailbox."""

    eleza __init__(self, path, factory=None, create=True):
        """Initialize an MMDF mailbox."""
        self._message_factory = MMDFMessage
        _mboxMMDF.__init__(self, path, factory, create)

    eleza _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        f.write(b'\001\001\001\001' + linesep)

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep + b'\001\001\001\001' + linesep)

    eleza _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        while True:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            ikiwa line.startswith(b'\001\001\001\001' + linesep):
                starts.append(next_pos)
                while True:
                    line_pos = next_pos
                    line = self._file.readline()
                    next_pos = self._file.tell()
                    ikiwa line == b'\001\001\001\001' + linesep:
                        stops.append(line_pos - len(linesep))
                        break
                    elikiwa not line:
                        stops.append(line_pos)
                        break
            elikiwa not line:
                break
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()


kundi MH(Mailbox):
    """An MH mailbox."""

    eleza __init__(self, path, factory=None, create=True):
        """Initialize an MH instance."""
        Mailbox.__init__(self, path, factory, create)
        ikiwa not os.path.exists(self._path):
            ikiwa create:
                os.mkdir(self._path, 0o700)
                os.close(os.open(os.path.join(self._path, '.mh_sequences'),
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            else:
                raise NoSuchMailboxError(self._path)
        self._locked = False

    eleza add(self, message):
        """Add message and rudisha assigned key."""
        keys = self.keys()
        ikiwa len(keys) == 0:
            new_key = 1
        else:
            new_key = max(keys) + 1
        new_path = os.path.join(self._path, str(new_key))
        f = _create_carefully(new_path)
        closed = False
        try:
            ikiwa self._locked:
                _lock_file(f)
            try:
                try:
                    self._dump_message(message, f)
                except BaseException:
                    # Unlock and close so it can be deleted on Windows
                    ikiwa self._locked:
                        _unlock_file(f)
                    _sync_close(f)
                    closed = True
                    os.remove(new_path)
                    raise
                ikiwa isinstance(message, MHMessage):
                    self._dump_sequences(message, new_key)
            finally:
                ikiwa self._locked:
                    _unlock_file(f)
        finally:
            ikiwa not closed:
                _sync_close(f)
        rudisha new_key

    eleza remove(self, key):
        """Remove the keyed message; raise KeyError ikiwa it doesn't exist."""
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        else:
            f.close()
            os.remove(path)

    eleza __setitem__(self, key, message):
        """Replace the keyed message; raise KeyError ikiwa it doesn't exist."""
        path = os.path.join(self._path, str(key))
        try:
            f = open(path, 'rb+')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        try:
            ikiwa self._locked:
                _lock_file(f)
            try:
                os.close(os.open(path, os.O_WRONLY | os.O_TRUNC))
                self._dump_message(message, f)
                ikiwa isinstance(message, MHMessage):
                    self._dump_sequences(message, key)
            finally:
                ikiwa self._locked:
                    _unlock_file(f)
        finally:
            _sync_close(f)

    eleza get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        try:
            ikiwa self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            else:
                f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        with f:
            ikiwa self._locked:
                _lock_file(f)
            try:
                msg = MHMessage(f)
            finally:
                ikiwa self._locked:
                    _unlock_file(f)
        for name, key_list in self.get_sequences().items():
            ikiwa key in key_list:
                msg.add_sequence(name)
        rudisha msg

    eleza get_bytes(self, key):
        """Return a bytes representation or raise a KeyError."""
        try:
            ikiwa self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            else:
                f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        with f:
            ikiwa self._locked:
                _lock_file(f)
            try:
                rudisha f.read().replace(linesep, b'\n')
            finally:
                ikiwa self._locked:
                    _unlock_file(f)

    eleza get_file(self, key):
        """Return a file-like representation or raise a KeyError."""
        try:
            f = open(os.path.join(self._path, str(key)), 'rb')
        except OSError as e:
            ikiwa e.errno == errno.ENOENT:
                raise KeyError('No message with key: %s' % key)
            else:
                raise
        rudisha _ProxyFile(f)

    eleza iterkeys(self):
        """Return an iterator over keys."""
        rudisha iter(sorted(int(entry) for entry in os.listdir(self._path)
                                      ikiwa entry.isdigit()))

    eleza __contains__(self, key):
        """Return True ikiwa the keyed message exists, False otherwise."""
        rudisha os.path.exists(os.path.join(self._path, str(key)))

    eleza __len__(self):
        """Return a count of messages in the mailbox."""
        rudisha len(list(self.iterkeys()))

    eleza lock(self):
        """Lock the mailbox."""
        ikiwa not self._locked:
            self._file = open(os.path.join(self._path, '.mh_sequences'), 'rb+')
            _lock_file(self._file)
            self._locked = True

    eleza unlock(self):
        """Unlock the mailbox ikiwa it is locked."""
        ikiwa self._locked:
            _unlock_file(self._file)
            _sync_close(self._file)
            del self._file
            self._locked = False

    eleza flush(self):
        """Write any pending changes to the disk."""
        return

    eleza close(self):
        """Flush and close the mailbox."""
        ikiwa self._locked:
            self.unlock()

    eleza list_folders(self):
        """Return a list of folder names."""
        result = []
        for entry in os.listdir(self._path):
            ikiwa os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry)
        rudisha result

    eleza get_folder(self, folder):
        """Return an MH instance for the named folder."""
        rudisha MH(os.path.join(self._path, folder),
                  factory=self._factory, create=False)

    eleza add_folder(self, folder):
        """Create a folder and rudisha an MH instance representing it."""
        rudisha MH(os.path.join(self._path, folder),
                  factory=self._factory)

    eleza remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, folder)
        entries = os.listdir(path)
        ikiwa entries == ['.mh_sequences']:
            os.remove(os.path.join(path, '.mh_sequences'))
        elikiwa entries == []:
            pass
        else:
            raise NotEmptyError('Folder not empty: %s' % self._path)
        os.rmdir(path)

    eleza get_sequences(self):
        """Return a name-to-key-list dictionary to define each sequence."""
        results = {}
        with open(os.path.join(self._path, '.mh_sequences'), 'r', encoding='ASCII') as f:
            all_keys = set(self.keys())
            for line in f:
                try:
                    name, contents = line.split(':')
                    keys = set()
                    for spec in contents.split():
                        ikiwa spec.isdigit():
                            keys.add(int(spec))
                        else:
                            start, stop = (int(x) for x in spec.split('-'))
                            keys.update(range(start, stop + 1))
                    results[name] = [key for key in sorted(keys) \
                                         ikiwa key in all_keys]
                    ikiwa len(results[name]) == 0:
                        del results[name]
                except ValueError:
                    raise FormatError('Invalid sequence specification: %s' %
                                      line.rstrip())
        rudisha results

    eleza set_sequences(self, sequences):
        """Set sequences using the given name-to-key-list dictionary."""
        f = open(os.path.join(self._path, '.mh_sequences'), 'r+', encoding='ASCII')
        try:
            os.close(os.open(f.name, os.O_WRONLY | os.O_TRUNC))
            for name, keys in sequences.items():
                ikiwa len(keys) == 0:
                    continue
                f.write(name + ':')
                prev = None
                completing = False
                for key in sorted(set(keys)):
                    ikiwa key - 1 == prev:
                        ikiwa not completing:
                            completing = True
                            f.write('-')
                    elikiwa completing:
                        completing = False
                        f.write('%s %s' % (prev, key))
                    else:
                        f.write(' %s' % key)
                    prev = key
                ikiwa completing:
                    f.write(str(prev) + '\n')
                else:
                    f.write('\n')
        finally:
            _sync_close(f)

    eleza pack(self):
        """Re-name messages to eliminate numbering gaps. Invalidates keys."""
        sequences = self.get_sequences()
        prev = 0
        changes = []
        for key in self.iterkeys():
            ikiwa key - 1 != prev:
                changes.append((key, prev + 1))
                try:
                    os.link(os.path.join(self._path, str(key)),
                            os.path.join(self._path, str(prev + 1)))
                except (AttributeError, PermissionError):
                    os.rename(os.path.join(self._path, str(key)),
                              os.path.join(self._path, str(prev + 1)))
                else:
                    os.unlink(os.path.join(self._path, str(key)))
            prev += 1
        self._next_key = prev + 1
        ikiwa len(changes) == 0:
            return
        for name, key_list in sequences.items():
            for old, new in changes:
                ikiwa old in key_list:
                    key_list[key_list.index(old)] = new
        self.set_sequences(sequences)

    eleza _dump_sequences(self, message, key):
        """Inspect a new MHMessage and update sequences appropriately."""
        pending_sequences = message.get_sequences()
        all_sequences = self.get_sequences()
        for name, key_list in all_sequences.items():
            ikiwa name in pending_sequences:
                key_list.append(key)
            elikiwa key in key_list:
                del key_list[key_list.index(key)]
        for sequence in pending_sequences:
            ikiwa sequence not in all_sequences:
                all_sequences[sequence] = [key]
        self.set_sequences(all_sequences)


kundi Babyl(_singlefileMailbox):
    """An Rmail-style Babyl mailbox."""

    _special_labels = frozenset({'unseen', 'deleted', 'filed', 'answered',
                                 'forwarded', 'edited', 'resent'})

    eleza __init__(self, path, factory=None, create=True):
        """Initialize a Babyl mailbox."""
        _singlefileMailbox.__init__(self, path, factory, create)
        self._labels = {}

    eleza add(self, message):
        """Add message and rudisha assigned key."""
        key = _singlefileMailbox.add(self, message)
        ikiwa isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()
        rudisha key

    eleza remove(self, key):
        """Remove the keyed message; raise KeyError ikiwa it doesn't exist."""
        _singlefileMailbox.remove(self, key)
        ikiwa key in self._labels:
            del self._labels[key]

    eleza __setitem__(self, key, message):
        """Replace the keyed message; raise KeyError ikiwa it doesn't exist."""
        _singlefileMailbox.__setitem__(self, key, message)
        ikiwa isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()

    eleza get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        while True:
            line = self._file.readline()
            ikiwa line == b'*** EOOH ***' + linesep or not line:
                break
            original_headers.write(line.replace(linesep, b'\n'))
        visible_headers = io.BytesIO()
        while True:
            line = self._file.readline()
            ikiwa line == linesep or not line:
                break
            visible_headers.write(line.replace(linesep, b'\n'))
        # Read up to the stop, or to the end
        n = stop - self._file.tell()
        assert n >= 0
        body = self._file.read(n)
        body = body.replace(linesep, b'\n')
        msg = BabylMessage(original_headers.getvalue() + body)
        msg.set_visible(visible_headers.getvalue())
        ikiwa key in self._labels:
            msg.set_labels(self._labels[key])
        rudisha msg

    eleza get_bytes(self, key):
        """Return a string representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        while True:
            line = self._file.readline()
            ikiwa line == b'*** EOOH ***' + linesep or not line:
                break
            original_headers.write(line.replace(linesep, b'\n'))
        while True:
            line = self._file.readline()
            ikiwa line == linesep or not line:
                break
        headers = original_headers.getvalue()
        n = stop - self._file.tell()
        assert n >= 0
        data = self._file.read(n)
        data = data.replace(linesep, b'\n')
        rudisha headers + data

    eleza get_file(self, key):
        """Return a file-like representation or raise a KeyError."""
        rudisha io.BytesIO(self.get_bytes(key).replace(b'\n', linesep))

    eleza get_labels(self):
        """Return a list of user-defined labels in the mailbox."""
        self._lookup()
        labels = set()
        for label_list in self._labels.values():
            labels.update(label_list)
        labels.difference_update(self._special_labels)
        rudisha list(labels)

    eleza _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        label_lists = []
        while True:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            ikiwa line == b'\037\014' + linesep:
                ikiwa len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
                starts.append(next_pos)
                labels = [label.strip() for label
                                        in self._file.readline()[1:].split(b',')
                                        ikiwa label.strip()]
                label_lists.append(labels)
            elikiwa line == b'\037' or line == b'\037' + linesep:
                ikiwa len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
            elikiwa not line:
                stops.append(line_pos - len(linesep))
                break
        self._toc = dict(enumerate(zip(starts, stops)))
        self._labels = dict(enumerate(label_lists))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()

    eleza _pre_mailbox_hook(self, f):
        """Called before writing the mailbox to file f."""
        babyl = b'BABYL OPTIONS:' + linesep
        babyl += b'Version: 5' + linesep
        labels = self.get_labels()
        labels = (label.encode() for label in labels)
        babyl += b'Labels:' + b','.join(labels) + linesep
        babyl += b'\037'
        f.write(babyl)

    eleza _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        f.write(b'\014' + linesep)

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep + b'\037')

    eleza _install_message(self, message):
        """Write message contents and rudisha (start, stop)."""
        start = self._file.tell()
        ikiwa isinstance(message, BabylMessage):
            special_labels = []
            labels = []
            for label in message.get_labels():
                ikiwa label in self._special_labels:
                    special_labels.append(label)
                else:
                    labels.append(label)
            self._file.write(b'1')
            for label in special_labels:
                self._file.write(b', ' + label.encode())
            self._file.write(b',,')
            for label in labels:
                self._file.write(b' ' + label.encode() + b',')
            self._file.write(linesep)
        else:
            self._file.write(b'1,,' + linesep)
        ikiwa isinstance(message, email.message.Message):
            orig_buffer = io.BytesIO()
            orig_generator = email.generator.BytesGenerator(orig_buffer, False, 0)
            orig_generator.flatten(message)
            orig_buffer.seek(0)
            while True:
                line = orig_buffer.readline()
                self._file.write(line.replace(b'\n', linesep))
                ikiwa line == b'\n' or not line:
                    break
            self._file.write(b'*** EOOH ***' + linesep)
            ikiwa isinstance(message, BabylMessage):
                vis_buffer = io.BytesIO()
                vis_generator = email.generator.BytesGenerator(vis_buffer, False, 0)
                vis_generator.flatten(message.get_visible())
                while True:
                    line = vis_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    ikiwa line == b'\n' or not line:
                        break
            else:
                orig_buffer.seek(0)
                while True:
                    line = orig_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    ikiwa line == b'\n' or not line:
                        break
            while True:
                buffer = orig_buffer.read(4096) # Buffer size is arbitrary.
                ikiwa not buffer:
                    break
                self._file.write(buffer.replace(b'\n', linesep))
        elikiwa isinstance(message, (bytes, str, io.StringIO)):
            ikiwa isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input is deprecated, "
                    "use BytesIO instead", DeprecationWarning, 3)
                message = message.getvalue()
            ikiwa isinstance(message, str):
                message = self._string_to_bytes(message)
            body_start = message.find(b'\n\n') + 2
            ikiwa body_start - 2 != -1:
                self._file.write(message[:body_start].replace(b'\n', linesep))
                self._file.write(b'*** EOOH ***' + linesep)
                self._file.write(message[:body_start].replace(b'\n', linesep))
                self._file.write(message[body_start:].replace(b'\n', linesep))
            else:
                self._file.write(b'*** EOOH ***' + linesep + linesep)
                self._file.write(message.replace(b'\n', linesep))
        elikiwa hasattr(message, 'readline'):
            ikiwa hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files is deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            original_pos = message.tell()
            first_pass = True
            while True:
                line = message.readline()
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                elikiwa line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                self._file.write(line.replace(b'\n', linesep))
                ikiwa line == b'\n' or not line:
                    ikiwa first_pass:
                        first_pass = False
                        self._file.write(b'*** EOOH ***' + linesep)
                        message.seek(original_pos)
                    else:
                        break
            while True:
                line = message.readline()
                ikiwa not line:
                    break
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + linesep
                elikiwa line.endswith(b'\r'):
                    line = line[:-1] + linesep
                elikiwa line.endswith(b'\n'):
                    line = line[:-1] + linesep
                self._file.write(line)
        else:
            raise TypeError('Invalid message type: %s' % type(message))
        stop = self._file.tell()
        rudisha (start, stop)


kundi Message(email.message.Message):
    """Message with mailbox-format-specific properties."""

    eleza __init__(self, message=None):
        """Initialize a Message instance."""
        ikiwa isinstance(message, email.message.Message):
            self._become_message(copy.deepcopy(message))
            ikiwa isinstance(message, Message):
                message._explain_to(self)
        elikiwa isinstance(message, bytes):
            self._become_message(email.message_kutoka_bytes(message))
        elikiwa isinstance(message, str):
            self._become_message(email.message_kutoka_string(message))
        elikiwa isinstance(message, io.TextIOWrapper):
            self._become_message(email.message_kutoka_file(message))
        elikiwa hasattr(message, "read"):
            self._become_message(email.message_kutoka_binary_file(message))
        elikiwa message is None:
            email.message.Message.__init__(self)
        else:
            raise TypeError('Invalid message type: %s' % type(message))

    eleza _become_message(self, message):
        """Assume the non-format-specific state of message."""
        type_specific = getattr(message, '_type_specific_attributes', [])
        for name in message.__dict__:
            ikiwa name not in type_specific:
                self.__dict__[name] = message.__dict__[name]

    eleza _explain_to(self, message):
        """Copy format-specific state to message insofar as possible."""
        ikiwa isinstance(message, Message):
            rudisha  # There's nothing format-specific to explain.
        else:
            raise TypeError('Cannot convert to specified type')


kundi MaildirMessage(Message):
    """Message with Maildir-specific properties."""

    _type_specific_attributes = ['_subdir', '_info', '_date']

    eleza __init__(self, message=None):
        """Initialize a MaildirMessage instance."""
        self._subdir = 'new'
        self._info = ''
        self._date = time.time()
        Message.__init__(self, message)

    eleza get_subdir(self):
        """Return 'new' or 'cur'."""
        rudisha self._subdir

    eleza set_subdir(self, subdir):
        """Set subdir to 'new' or 'cur'."""
        ikiwa subdir == 'new' or subdir == 'cur':
            self._subdir = subdir
        else:
            raise ValueError("subdir must be 'new' or 'cur': %s" % subdir)

    eleza get_flags(self):
        """Return as a string the flags that are set."""
        ikiwa self._info.startswith('2,'):
            rudisha self._info[2:]
        else:
            rudisha ''

    eleza set_flags(self, flags):
        """Set the given flags and unset all others."""
        self._info = '2,' + ''.join(sorted(flags))

    eleza add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    eleza remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        ikiwa self.get_flags():
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    eleza get_date(self):
        """Return delivery date of message, in seconds since the epoch."""
        rudisha self._date

    eleza set_date(self, date):
        """Set delivery date of message, in seconds since the epoch."""
        try:
            self._date = float(date)
        except ValueError:
            raise TypeError("can't convert to float: %s" % date) kutoka None

    eleza get_info(self):
        """Get the message's "info" as a string."""
        rudisha self._info

    eleza set_info(self, info):
        """Set the message's "info" string."""
        ikiwa isinstance(info, str):
            self._info = info
        else:
            raise TypeError('info must be a string: %s' % type(info))

    eleza _explain_to(self, message):
        """Copy Maildir-specific state to message insofar as possible."""
        ikiwa isinstance(message, MaildirMessage):
            message.set_flags(self.get_flags())
            message.set_subdir(self.get_subdir())
            message.set_date(self.get_date())
        elikiwa isinstance(message, _mboxMMDFMessage):
            flags = set(self.get_flags())
            ikiwa 'S' in flags:
                message.add_flag('R')
            ikiwa self.get_subdir() == 'cur':
                message.add_flag('O')
            ikiwa 'T' in flags:
                message.add_flag('D')
            ikiwa 'F' in flags:
                message.add_flag('F')
            ikiwa 'R' in flags:
                message.add_flag('A')
            message.set_kutoka('MAILER-DAEMON', time.gmtime(self.get_date()))
        elikiwa isinstance(message, MHMessage):
            flags = set(self.get_flags())
            ikiwa 'S' not in flags:
                message.add_sequence('unseen')
            ikiwa 'R' in flags:
                message.add_sequence('replied')
            ikiwa 'F' in flags:
                message.add_sequence('flagged')
        elikiwa isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            ikiwa 'S' not in flags:
                message.add_label('unseen')
            ikiwa 'T' in flags:
                message.add_label('deleted')
            ikiwa 'R' in flags:
                message.add_label('answered')
            ikiwa 'P' in flags:
                message.add_label('forwarded')
        elikiwa isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' %
                            type(message))


kundi _mboxMMDFMessage(Message):
    """Message with mbox- or MMDF-specific properties."""

    _type_specific_attributes = ['_kutoka']

    eleza __init__(self, message=None):
        """Initialize an mboxMMDFMessage instance."""
        self.set_kutoka('MAILER-DAEMON', True)
        ikiwa isinstance(message, email.message.Message):
            unixkutoka = message.get_unixkutoka()
            ikiwa unixkutoka is not None and unixkutoka.startswith('From '):
                self.set_kutoka(unixkutoka[5:])
        Message.__init__(self, message)

    eleza get_kutoka(self):
        """Return contents of "From " line."""
        rudisha self._kutoka

    eleza set_kutoka(self, kutoka_, time_=None):
        """Set "From " line, formatting and appending time_ ikiwa specified."""
        ikiwa time_ is not None:
            ikiwa time_ is True:
                time_ = time.gmtime()
            kutoka_ += ' ' + time.asctime(time_)
        self._kutoka = kutoka_

    eleza get_flags(self):
        """Return as a string the flags that are set."""
        rudisha self.get('Status', '') + self.get('X-Status', '')

    eleza set_flags(self, flags):
        """Set the given flags and unset all others."""
        flags = set(flags)
        status_flags, xstatus_flags = '', ''
        for flag in ('R', 'O'):
            ikiwa flag in flags:
                status_flags += flag
                flags.remove(flag)
        for flag in ('D', 'F', 'A'):
            ikiwa flag in flags:
                xstatus_flags += flag
                flags.remove(flag)
        xstatus_flags += ''.join(sorted(flags))
        try:
            self.replace_header('Status', status_flags)
        except KeyError:
            self.add_header('Status', status_flags)
        try:
            self.replace_header('X-Status', xstatus_flags)
        except KeyError:
            self.add_header('X-Status', xstatus_flags)

    eleza add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    eleza remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        ikiwa 'Status' in self or 'X-Status' in self:
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    eleza _explain_to(self, message):
        """Copy mbox- or MMDF-specific state to message insofar as possible."""
        ikiwa isinstance(message, MaildirMessage):
            flags = set(self.get_flags())
            ikiwa 'O' in flags:
                message.set_subdir('cur')
            ikiwa 'F' in flags:
                message.add_flag('F')
            ikiwa 'A' in flags:
                message.add_flag('R')
            ikiwa 'R' in flags:
                message.add_flag('S')
            ikiwa 'D' in flags:
                message.add_flag('T')
            del message['status']
            del message['x-status']
            maybe_date = ' '.join(self.get_kutoka().split()[-5:])
            try:
                message.set_date(calendar.timegm(time.strptime(maybe_date,
                                                      '%a %b %d %H:%M:%S %Y')))
            except (ValueError, OverflowError):
                pass
        elikiwa isinstance(message, _mboxMMDFMessage):
            message.set_flags(self.get_flags())
            message.set_kutoka(self.get_kutoka())
        elikiwa isinstance(message, MHMessage):
            flags = set(self.get_flags())
            ikiwa 'R' not in flags:
                message.add_sequence('unseen')
            ikiwa 'A' in flags:
                message.add_sequence('replied')
            ikiwa 'F' in flags:
                message.add_sequence('flagged')
            del message['status']
            del message['x-status']
        elikiwa isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            ikiwa 'R' not in flags:
                message.add_label('unseen')
            ikiwa 'D' in flags:
                message.add_label('deleted')
            ikiwa 'A' in flags:
                message.add_label('answered')
            del message['status']
            del message['x-status']
        elikiwa isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' %
                            type(message))


kundi mboxMessage(_mboxMMDFMessage):
    """Message with mbox-specific properties."""


kundi MHMessage(Message):
    """Message with MH-specific properties."""

    _type_specific_attributes = ['_sequences']

    eleza __init__(self, message=None):
        """Initialize an MHMessage instance."""
        self._sequences = []
        Message.__init__(self, message)

    eleza get_sequences(self):
        """Return a list of sequences that include the message."""
        rudisha self._sequences[:]

    eleza set_sequences(self, sequences):
        """Set the list of sequences that include the message."""
        self._sequences = list(sequences)

    eleza add_sequence(self, sequence):
        """Add sequence to list of sequences including the message."""
        ikiwa isinstance(sequence, str):
            ikiwa not sequence in self._sequences:
                self._sequences.append(sequence)
        else:
            raise TypeError('sequence type must be str: %s' % type(sequence))

    eleza remove_sequence(self, sequence):
        """Remove sequence kutoka the list of sequences including the message."""
        try:
            self._sequences.remove(sequence)
        except ValueError:
            pass

    eleza _explain_to(self, message):
        """Copy MH-specific state to message insofar as possible."""
        ikiwa isinstance(message, MaildirMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' in sequences:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            ikiwa 'flagged' in sequences:
                message.add_flag('F')
            ikiwa 'replied' in sequences:
                message.add_flag('R')
        elikiwa isinstance(message, _mboxMMDFMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' not in sequences:
                message.add_flag('RO')
            else:
                message.add_flag('O')
            ikiwa 'flagged' in sequences:
                message.add_flag('F')
            ikiwa 'replied' in sequences:
                message.add_flag('A')
        elikiwa isinstance(message, MHMessage):
            for sequence in self.get_sequences():
                message.add_sequence(sequence)
        elikiwa isinstance(message, BabylMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' in sequences:
                message.add_label('unseen')
            ikiwa 'replied' in sequences:
                message.add_label('answered')
        elikiwa isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' %
                            type(message))


kundi BabylMessage(Message):
    """Message with Babyl-specific properties."""

    _type_specific_attributes = ['_labels', '_visible']

    eleza __init__(self, message=None):
        """Initialize a BabylMessage instance."""
        self._labels = []
        self._visible = Message()
        Message.__init__(self, message)

    eleza get_labels(self):
        """Return a list of labels on the message."""
        rudisha self._labels[:]

    eleza set_labels(self, labels):
        """Set the list of labels on the message."""
        self._labels = list(labels)

    eleza add_label(self, label):
        """Add label to list of labels on the message."""
        ikiwa isinstance(label, str):
            ikiwa label not in self._labels:
                self._labels.append(label)
        else:
            raise TypeError('label must be a string: %s' % type(label))

    eleza remove_label(self, label):
        """Remove label kutoka the list of labels on the message."""
        try:
            self._labels.remove(label)
        except ValueError:
            pass

    eleza get_visible(self):
        """Return a Message representation of visible headers."""
        rudisha Message(self._visible)

    eleza set_visible(self, visible):
        """Set the Message representation of visible headers."""
        self._visible = Message(visible)

    eleza update_visible(self):
        """Update and/or sensibly generate a set of visible headers."""
        for header in self._visible.keys():
            ikiwa header in self:
                self._visible.replace_header(header, self[header])
            else:
                del self._visible[header]
        for header in ('Date', 'From', 'Reply-To', 'To', 'CC', 'Subject'):
            ikiwa header in self and header not in self._visible:
                self._visible[header] = self[header]

    eleza _explain_to(self, message):
        """Copy Babyl-specific state to message insofar as possible."""
        ikiwa isinstance(message, MaildirMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' in labels:
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
            ikiwa 'forwarded' in labels or 'resent' in labels:
                message.add_flag('P')
            ikiwa 'answered' in labels:
                message.add_flag('R')
            ikiwa 'deleted' in labels:
                message.add_flag('T')
        elikiwa isinstance(message, _mboxMMDFMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' not in labels:
                message.add_flag('RO')
            else:
                message.add_flag('O')
            ikiwa 'deleted' in labels:
                message.add_flag('D')
            ikiwa 'answered' in labels:
                message.add_flag('A')
        elikiwa isinstance(message, MHMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' in labels:
                message.add_sequence('unseen')
            ikiwa 'answered' in labels:
                message.add_sequence('replied')
        elikiwa isinstance(message, BabylMessage):
            message.set_visible(self.get_visible())
            for label in self.get_labels():
                message.add_label(label)
        elikiwa isinstance(message, Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' %
                            type(message))


kundi MMDFMessage(_mboxMMDFMessage):
    """Message with MMDF-specific properties."""


kundi _ProxyFile:
    """A read-only wrapper of a file."""

    eleza __init__(self, f, pos=None):
        """Initialize a _ProxyFile."""
        self._file = f
        ikiwa pos is None:
            self._pos = f.tell()
        else:
            self._pos = pos

    eleza read(self, size=None):
        """Read bytes."""
        rudisha self._read(size, self._file.read)

    eleza read1(self, size=None):
        """Read bytes."""
        rudisha self._read(size, self._file.read1)

    eleza readline(self, size=None):
        """Read a line."""
        rudisha self._read(size, self._file.readline)

    eleza readlines(self, sizehint=None):
        """Read multiple lines."""
        result = []
        for line in self:
            result.append(line)
            ikiwa sizehint is not None:
                sizehint -= len(line)
                ikiwa sizehint <= 0:
                    break
        rudisha result

    eleza __iter__(self):
        """Iterate over lines."""
        while True:
            line = self.readline()
            ikiwa not line:
                return
            yield line

    eleza tell(self):
        """Return the position."""
        rudisha self._pos

    eleza seek(self, offset, whence=0):
        """Change position."""
        ikiwa whence == 1:
            self._file.seek(self._pos)
        self._file.seek(offset, whence)
        self._pos = self._file.tell()

    eleza close(self):
        """Close the file."""
        ikiwa hasattr(self, '_file'):
            try:
                ikiwa hasattr(self._file, 'close'):
                    self._file.close()
            finally:
                del self._file

    eleza _read(self, size, read_method):
        """Read size bytes using read_method."""
        ikiwa size is None:
            size = -1
        self._file.seek(self._pos)
        result = read_method(size)
        self._pos = self._file.tell()
        rudisha result

    eleza __enter__(self):
        """Context management protocol support."""
        rudisha self

    eleza __exit__(self, *exc):
        self.close()

    eleza readable(self):
        rudisha self._file.readable()

    eleza writable(self):
        rudisha self._file.writable()

    eleza seekable(self):
        rudisha self._file.seekable()

    eleza flush(self):
        rudisha self._file.flush()

    @property
    eleza closed(self):
        ikiwa not hasattr(self, '_file'):
            rudisha True
        ikiwa not hasattr(self._file, 'closed'):
            rudisha False
        rudisha self._file.closed


kundi _PartialFile(_ProxyFile):
    """A read-only wrapper of part of a file."""

    eleza __init__(self, f, start=None, stop=None):
        """Initialize a _PartialFile."""
        _ProxyFile.__init__(self, f, start)
        self._start = start
        self._stop = stop

    eleza tell(self):
        """Return the position with respect to start."""
        rudisha _ProxyFile.tell(self) - self._start

    eleza seek(self, offset, whence=0):
        """Change position, possibly with respect to start or stop."""
        ikiwa whence == 0:
            self._pos = self._start
            whence = 1
        elikiwa whence == 2:
            self._pos = self._stop
            whence = 1
        _ProxyFile.seek(self, offset, whence)

    eleza _read(self, size, read_method):
        """Read size bytes using read_method, honoring start and stop."""
        remaining = self._stop - self._pos
        ikiwa remaining <= 0:
            rudisha b''
        ikiwa size is None or size < 0 or size > remaining:
            size = remaining
        rudisha _ProxyFile._read(self, size, read_method)

    eleza close(self):
        # do *not* close the underlying file object for partial files,
        # since it's global to the mailbox object
        ikiwa hasattr(self, '_file'):
            del self._file


eleza _lock_file(f, dotlock=True):
    """Lock file f using lockf and dot locking."""
    dotlock_done = False
    try:
        ikiwa fcntl:
            try:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as e:
                ikiwa e.errno in (errno.EAGAIN, errno.EACCES, errno.EROFS):
                    raise ExternalClashError('lockf: lock unavailable: %s' %
                                             f.name)
                else:
                    raise
        ikiwa dotlock:
            try:
                pre_lock = _create_temporary(f.name + '.lock')
                pre_lock.close()
            except OSError as e:
                ikiwa e.errno in (errno.EACCES, errno.EROFS):
                    rudisha  # Without write access, just skip dotlocking.
                else:
                    raise
            try:
                try:
                    os.link(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
                except (AttributeError, PermissionError):
                    os.rename(pre_lock.name, f.name + '.lock')
                    dotlock_done = True
                else:
                    os.unlink(pre_lock.name)
            except FileExistsError:
                os.remove(pre_lock.name)
                raise ExternalClashError('dot lock unavailable: %s' %
                                         f.name)
    except:
        ikiwa fcntl:
            fcntl.lockf(f, fcntl.LOCK_UN)
        ikiwa dotlock_done:
            os.remove(f.name + '.lock')
        raise

eleza _unlock_file(f):
    """Unlock file f using lockf and dot locking."""
    ikiwa fcntl:
        fcntl.lockf(f, fcntl.LOCK_UN)
    ikiwa os.path.exists(f.name + '.lock'):
        os.remove(f.name + '.lock')

eleza _create_carefully(path):
    """Create a file ikiwa it doesn't exist and open for reading and writing."""
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o666)
    try:
        rudisha open(path, 'rb+')
    finally:
        os.close(fd)

eleza _create_temporary(path):
    """Create a temp file based on path and open for reading and writing."""
    rudisha _create_carefully('%s.%s.%s.%s' % (path, int(time.time()),
                                              socket.gethostname(),
                                              os.getpid()))

eleza _sync_flush(f):
    """Ensure changes to file f are physically on disk."""
    f.flush()
    ikiwa hasattr(os, 'fsync'):
        os.fsync(f.fileno())

eleza _sync_close(f):
    """Close file f, ensuring all changes are physically on disk."""
    _sync_flush(f)
    f.close()


kundi Error(Exception):
    """Raised for module-specific errors."""

kundi NoSuchMailboxError(Error):
    """The specified mailbox does not exist and won't be created."""

kundi NotEmptyError(Error):
    """The specified mailbox is not empty and deletion was requested."""

kundi ExternalClashError(Error):
    """Another process caused an action to fail."""

kundi FormatError(Error):
    """A file appears to have an invalid format."""
