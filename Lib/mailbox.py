"""Read/write support kila Maildir, mbox, MH, Babyl, na MMDF mailboxes."""

# Notes kila authors of new mailbox subclasses:
#
# Remember to fsync() changes to disk before closing a modified file
# ama returning kutoka a flush() method.  See functions _sync_flush() na
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
jaribu:
    agiza fcntl
tatizo ImportError:
    fcntl = Tupu

__all__ = ['Mailbox', 'Maildir', 'mbox', 'MH', 'Babyl', 'MMDF',
           'Message', 'MaildirMessage', 'mboxMessage', 'MHMessage',
           'BabylMessage', 'MMDFMessage', 'Error', 'NoSuchMailboxError',
           'NotEmptyError', 'ExternalClashError', 'FormatError']

linesep = os.linesep.encode('ascii')

kundi Mailbox:
    """A group of messages kwenye a particular place."""

    eleza __init__(self, path, factory=Tupu, create=Kweli):
        """Initialize a Mailbox instance."""
        self._path = os.path.abspath(os.path.expanduser(path))
        self._factory = factory

    eleza add(self, message):
        """Add message na rudisha assigned key."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza remove(self, key):
        """Remove the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza __delitem__(self, key):
        self.remove(key)

    eleza discard(self, key):
        """If the keyed message exists, remove it."""
        jaribu:
            self.remove(key)
        tatizo KeyError:
            pita

    eleza __setitem__(self, key, message):
        """Replace the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza get(self, key, default=Tupu):
        """Return the keyed message, ama default ikiwa it doesn't exist."""
        jaribu:
            rudisha self.__getitem__(key)
        tatizo KeyError:
            rudisha default

    eleza __getitem__(self, key):
        """Return the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        ikiwa sio self._factory:
            rudisha self.get_message(key)
        isipokua:
            ukijumuisha contextlib.closing(self.get_file(key)) kama file:
                rudisha self._factory(file)

    eleza get_message(self, key):
        """Return a Message representation ama ashiria a KeyError."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza get_string(self, key):
        """Return a string representation ama ashiria a KeyError.

        Uses email.message.Message to create a 7bit clean string
        representation of the message."""
        rudisha email.message_from_bytes(self.get_bytes(key)).as_string()

    eleza get_bytes(self, key):
        """Return a byte string representation ama ashiria a KeyError."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza get_file(self, key):
        """Return a file-like representation ama ashiria a KeyError."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza iterkeys(self):
        """Return an iterator over keys."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza keys(self):
        """Return a list of keys."""
        rudisha list(self.iterkeys())

    eleza itervalues(self):
        """Return an iterator over all messages."""
        kila key kwenye self.iterkeys():
            jaribu:
                value = self[key]
            tatizo KeyError:
                endelea
            tuma value

    eleza __iter__(self):
        rudisha self.itervalues()

    eleza values(self):
        """Return a list of messages. Memory intensive."""
        rudisha list(self.itervalues())

    eleza iteritems(self):
        """Return an iterator over (key, message) tuples."""
        kila key kwenye self.iterkeys():
            jaribu:
                value = self[key]
            tatizo KeyError:
                endelea
            tuma (key, value)

    eleza items(self):
        """Return a list of (key, message) tuples. Memory intensive."""
        rudisha list(self.iteritems())

    eleza __contains__(self, key):
        """Return Kweli ikiwa the keyed message exists, Uongo otherwise."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza __len__(self):
        """Return a count of messages kwenye the mailbox."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza clear(self):
        """Delete all messages."""
        kila key kwenye self.keys():
            self.discard(key)

    eleza pop(self, key, default=Tupu):
        """Delete the keyed message na rudisha it, ama default."""
        jaribu:
            result = self[key]
        tatizo KeyError:
            rudisha default
        self.discard(key)
        rudisha result

    eleza popitem(self):
        """Delete an arbitrary (key, message) pair na rudisha it."""
        kila key kwenye self.iterkeys():
            rudisha (key, self.pop(key))     # This ni only run once.
        isipokua:
            ashiria KeyError('No messages kwenye mailbox')

    eleza update(self, arg=Tupu):
        """Change the messages that correspond to certain keys."""
        ikiwa hasattr(arg, 'iteritems'):
            source = arg.iteritems()
        lasivyo hasattr(arg, 'items'):
            source = arg.items()
        isipokua:
            source = arg
        bad_key = Uongo
        kila key, message kwenye source:
            jaribu:
                self[key] = message
            tatizo KeyError:
                bad_key = Kweli
        ikiwa bad_key:
            ashiria KeyError('No message ukijumuisha key(s)')

    eleza flush(self):
        """Write any pending changes to the disk."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza lock(self):
        """Lock the mailbox."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza unlock(self):
        """Unlock the mailbox ikiwa it ni locked."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza close(self):
        """Flush na close the mailbox."""
        ashiria NotImplementedError('Method must be implemented by subclass')

    eleza _string_to_bytes(self, message):
        # If a message ni sio 7bit clean, we refuse to handle it since it
        # likely came kutoka reading invalid messages kwenye text mode, na that way
        # lies mojibake.
        jaribu:
            rudisha message.encode('ascii')
        tatizo UnicodeError:
            ashiria ValueError("String input must be ASCII-only; "
                "use bytes ama a Message instead")

    # Whether each message must end kwenye a newline
    _append_newline = Uongo

    eleza _dump_message(self, message, target, mangle_from_=Uongo):
        # This assumes the target file ni open kwenye binary mode.
        """Dump message contents to target file."""
        ikiwa isinstance(message, email.message.Message):
            buffer = io.BytesIO()
            gen = email.generator.BytesGenerator(buffer, mangle_from_, 0)
            gen.flatten(message)
            buffer.seek(0)
            data = buffer.read()
            data = data.replace(b'\n', linesep)
            target.write(data)
            ikiwa self._append_newline na sio data.endswith(linesep):
                # Make sure the message ends ukijumuisha a newline
                target.write(linesep)
        lasivyo isinstance(message, (str, bytes, io.StringIO)):
            ikiwa isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input ni deprecated, "
                    "use BytesIO instead", DeprecationWarning, 3)
                message = message.getvalue()
            ikiwa isinstance(message, str):
                message = self._string_to_bytes(message)
            ikiwa mangle_from_:
                message = message.replace(b'\nFrom ', b'\n>From ')
            message = message.replace(b'\n', linesep)
            target.write(message)
            ikiwa self._append_newline na sio message.endswith(linesep):
                # Make sure the message ends ukijumuisha a newline
                target.write(linesep)
        lasivyo hasattr(message, 'read'):
            ikiwa hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files ni deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            lastline = Tupu
            wakati Kweli:
                line = message.readline()
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                lasivyo line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                ikiwa sio line:
                    koma
                ikiwa mangle_from_ na line.startswith(b'From '):
                    line = b'>From ' + line[5:]
                line = line.replace(b'\n', linesep)
                target.write(line)
                lastline = line
            ikiwa self._append_newline na lastline na sio lastline.endswith(linesep):
                # Make sure the message ends ukijumuisha a newline
                target.write(linesep)
        isipokua:
            ashiria TypeError('Invalid message type: %s' % type(message))


kundi Maildir(Mailbox):
    """A qmail-style Maildir mailbox."""

    colon = ':'

    eleza __init__(self, dirname, factory=Tupu, create=Kweli):
        """Initialize a Maildir instance."""
        Mailbox.__init__(self, dirname, factory, create)
        self._paths = {
            'tmp': os.path.join(self._path, 'tmp'),
            'new': os.path.join(self._path, 'new'),
            'cur': os.path.join(self._path, 'cur'),
            }
        ikiwa sio os.path.exists(self._path):
            ikiwa create:
                os.mkdir(self._path, 0o700)
                kila path kwenye self._paths.values():
                    os.mkdir(path, 0o700)
            isipokua:
                ashiria NoSuchMailboxError(self._path)
        self._toc = {}
        self._toc_mtimes = {'cur': 0, 'new': 0}
        self._last_read = 0         # Records last time we read cur/new
        self._skewfactor = 0.1      # Adjust ikiwa os/fs clocks are skewing

    eleza add(self, message):
        """Add message na rudisha assigned key."""
        tmp_file = self._create_tmp()
        jaribu:
            self._dump_message(message, tmp_file)
        tatizo BaseException:
            tmp_file.close()
            os.remove(tmp_file.name)
            raise
        _sync_close(tmp_file)
        ikiwa isinstance(message, MaildirMessage):
            subdir = message.get_subdir()
            suffix = self.colon + message.get_info()
            ikiwa suffix == self.colon:
                suffix = ''
        isipokua:
            subdir = 'new'
            suffix = ''
        uniq = os.path.basename(tmp_file.name).split(self.colon)[0]
        dest = os.path.join(self._path, subdir, uniq + suffix)
        ikiwa isinstance(message, MaildirMessage):
            os.utime(tmp_file.name,
                     (os.path.getatime(tmp_file.name), message.get_date()))
        # No file modification should be done after the file ni moved to its
        # final position kwenye order to prevent race conditions ukijumuisha changes
        # kutoka other programs
        jaribu:
            jaribu:
                os.link(tmp_file.name, dest)
            tatizo (AttributeError, PermissionError):
                os.rename(tmp_file.name, dest)
            isipokua:
                os.remove(tmp_file.name)
        tatizo OSError kama e:
            os.remove(tmp_file.name)
            ikiwa e.errno == errno.EEXIST:
                ashiria ExternalClashError('Name clash ukijumuisha existing message: %s'
                                         % dest)
            isipokua:
                raise
        rudisha uniq

    eleza remove(self, key):
        """Remove the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        os.remove(os.path.join(self._path, self._lookup(key)))

    eleza discard(self, key):
        """If the keyed message exists, remove it."""
        # This overrides an inapplicable implementation kwenye the superclass.
        jaribu:
            self.remove(key)
        tatizo (KeyError, FileNotFoundError):
            pita

    eleza __setitem__(self, key, message):
        """Replace the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        old_subpath = self._lookup(key)
        temp_key = self.add(message)
        temp_subpath = self._lookup(temp_key)
        ikiwa isinstance(message, MaildirMessage):
            # temp's subdir na suffix were specified by message.
            dominant_subpath = temp_subpath
        isipokua:
            # temp's subdir na suffix were defaults kutoka add().
            dominant_subpath = old_subpath
        subdir = os.path.dirname(dominant_subpath)
        ikiwa self.colon kwenye dominant_subpath:
            suffix = self.colon + dominant_subpath.split(self.colon)[-1]
        isipokua:
            suffix = ''
        self.discard(key)
        tmp_path = os.path.join(self._path, temp_subpath)
        new_path = os.path.join(self._path, subdir, key + suffix)
        ikiwa isinstance(message, MaildirMessage):
            os.utime(tmp_path,
                     (os.path.getatime(tmp_path), message.get_date()))
        # No file modification should be done after the file ni moved to its
        # final position kwenye order to prevent race conditions ukijumuisha changes
        # kutoka other programs
        os.rename(tmp_path, new_path)

    eleza get_message(self, key):
        """Return a Message representation ama ashiria a KeyError."""
        subpath = self._lookup(key)
        ukijumuisha open(os.path.join(self._path, subpath), 'rb') kama f:
            ikiwa self._factory:
                msg = self._factory(f)
            isipokua:
                msg = MaildirMessage(f)
        subdir, name = os.path.split(subpath)
        msg.set_subdir(subdir)
        ikiwa self.colon kwenye name:
            msg.set_info(name.split(self.colon)[-1])
        msg.set_date(os.path.getmtime(os.path.join(self._path, subpath)))
        rudisha msg

    eleza get_bytes(self, key):
        """Return a bytes representation ama ashiria a KeyError."""
        ukijumuisha open(os.path.join(self._path, self._lookup(key)), 'rb') kama f:
            rudisha f.read().replace(linesep, b'\n')

    eleza get_file(self, key):
        """Return a file-like representation ama ashiria a KeyError."""
        f = open(os.path.join(self._path, self._lookup(key)), 'rb')
        rudisha _ProxyFile(f)

    eleza iterkeys(self):
        """Return an iterator over keys."""
        self._refresh()
        kila key kwenye self._toc:
            jaribu:
                self._lookup(key)
            tatizo KeyError:
                endelea
            tuma key

    eleza __contains__(self, key):
        """Return Kweli ikiwa the keyed message exists, Uongo otherwise."""
        self._refresh()
        rudisha key kwenye self._toc

    eleza __len__(self):
        """Return a count of messages kwenye the mailbox."""
        self._refresh()
        rudisha len(self._toc)

    eleza flush(self):
        """Write any pending changes to disk."""
        # Maildir changes are always written immediately, so there's nothing
        # to do.
        pita

    eleza lock(self):
        """Lock the mailbox."""
        rudisha

    eleza unlock(self):
        """Unlock the mailbox ikiwa it ni locked."""
        rudisha

    eleza close(self):
        """Flush na close the mailbox."""
        rudisha

    eleza list_folders(self):
        """Return a list of folder names."""
        result = []
        kila entry kwenye os.listdir(self._path):
            ikiwa len(entry) > 1 na entry[0] == '.' na \
               os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry[1:])
        rudisha result

    eleza get_folder(self, folder):
        """Return a Maildir instance kila the named folder."""
        rudisha Maildir(os.path.join(self._path, '.' + folder),
                       factory=self._factory,
                       create=Uongo)

    eleza add_folder(self, folder):
        """Create a folder na rudisha a Maildir instance representing it."""
        path = os.path.join(self._path, '.' + folder)
        result = Maildir(path, factory=self._factory)
        maildirfolder_path = os.path.join(path, 'maildirfolder')
        ikiwa sio os.path.exists(maildirfolder_path):
            os.close(os.open(maildirfolder_path, os.O_CREAT | os.O_WRONLY,
                0o666))
        rudisha result

    eleza remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, '.' + folder)
        kila entry kwenye os.listdir(os.path.join(path, 'new')) + \
                     os.listdir(os.path.join(path, 'cur')):
            ikiwa len(entry) < 1 ama entry[0] != '.':
                ashiria NotEmptyError('Folder contains message(s): %s' % folder)
        kila entry kwenye os.listdir(path):
            ikiwa entry != 'new' na entry != 'cur' na entry != 'tmp' na \
               os.path.isdir(os.path.join(path, entry)):
                ashiria NotEmptyError("Folder contains subdirectory '%s': %s" %
                                    (folder, entry))
        kila root, dirs, files kwenye os.walk(path, topdown=Uongo):
            kila entry kwenye files:
                os.remove(os.path.join(root, entry))
            kila entry kwenye dirs:
                os.rmdir(os.path.join(root, entry))
        os.rmdir(path)

    eleza clean(self):
        """Delete old files kwenye "tmp"."""
        now = time.time()
        kila entry kwenye os.listdir(os.path.join(self._path, 'tmp')):
            path = os.path.join(self._path, 'tmp', entry)
            ikiwa now - os.path.getatime(path) > 129600:   # 60 * 60 * 36
                os.remove(path)

    _count = 1  # This ni used to generate unique file names.

    eleza _create_tmp(self):
        """Create a file kwenye the tmp subdirectory na open na rudisha it."""
        now = time.time()
        hostname = socket.gethostname()
        ikiwa '/' kwenye hostname:
            hostname = hostname.replace('/', r'\057')
        ikiwa ':' kwenye hostname:
            hostname = hostname.replace(':', r'\072')
        uniq = "%s.M%sP%sQ%s.%s" % (int(now), int(now % 1 * 1e6), os.getpid(),
                                    Maildir._count, hostname)
        path = os.path.join(self._path, 'tmp', uniq)
        jaribu:
            os.stat(path)
        tatizo FileNotFoundError:
            Maildir._count += 1
            jaribu:
                rudisha _create_carefully(path)
            tatizo FileExistsError:
                pita

        # Fall through to here ikiwa stat succeeded ama open raised EEXIST.
        ashiria ExternalClashError('Name clash prevented file creation: %s' %
                                 path)

    eleza _refresh(self):
        """Update table of contents mapping."""
        # If it has been less than two seconds since the last _refresh() call,
        # we have to unconditionally re-read the mailbox just kwenye case it has
        # been modified, because os.path.mtime() has a 2 sec resolution kwenye the
        # most common worst case (FAT) na a 1 sec resolution typically.  This
        # results kwenye a few unnecessary re-reads when _refresh() ni called
        # multiple times kwenye that interval, but once the clock ticks over, we
        # will only re-read kama needed.  Because the filesystem might be being
        # served by an independent system ukijumuisha its own clock, we record na
        # compare ukijumuisha the mtimes kutoka the filesystem.  Because the other
        # system's clock might be skewing relative to our clock, we add an
        # extra delta to our wait.  The default ni one tenth second, but ni an
        # instance variable na so can be adjusted ikiwa dealing ukijumuisha a
        # particularly skewed ama irregular system.
        ikiwa time.time() - self._last_read > 2 + self._skewfactor:
            refresh = Uongo
            kila subdir kwenye self._toc_mtimes:
                mtime = os.path.getmtime(self._paths[subdir])
                ikiwa mtime > self._toc_mtimes[subdir]:
                    refresh = Kweli
                self._toc_mtimes[subdir] = mtime
            ikiwa sio refresh:
                rudisha
        # Refresh toc
        self._toc = {}
        kila subdir kwenye self._toc_mtimes:
            path = self._paths[subdir]
            kila entry kwenye os.listdir(path):
                p = os.path.join(path, entry)
                ikiwa os.path.isdir(p):
                    endelea
                uniq = entry.split(self.colon)[0]
                self._toc[uniq] = os.path.join(subdir, entry)
        self._last_read = time.time()

    eleza _lookup(self, key):
        """Use TOC to rudisha subpath kila given key, ama ashiria a KeyError."""
        jaribu:
            ikiwa os.path.exists(os.path.join(self._path, self._toc[key])):
                rudisha self._toc[key]
        tatizo KeyError:
            pita
        self._refresh()
        jaribu:
            rudisha self._toc[key]
        tatizo KeyError:
            ashiria KeyError('No message ukijumuisha key: %s' % key) kutoka Tupu

    # This method ni kila backward compatibility only.
    eleza next(self):
        """Return the next message kwenye a one-time iteration."""
        ikiwa sio hasattr(self, '_onetime_keys'):
            self._onetime_keys = self.iterkeys()
        wakati Kweli:
            jaribu:
                rudisha self[next(self._onetime_keys)]
            tatizo StopIteration:
                rudisha Tupu
            tatizo KeyError:
                endelea


kundi _singlefileMailbox(Mailbox):
    """A single-file mailbox."""

    eleza __init__(self, path, factory=Tupu, create=Kweli):
        """Initialize a single-file mailbox."""
        Mailbox.__init__(self, path, factory, create)
        jaribu:
            f = open(self._path, 'rb+')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ikiwa create:
                    f = open(self._path, 'wb+')
                isipokua:
                    ashiria NoSuchMailboxError(self._path)
            lasivyo e.errno kwenye (errno.EACCES, errno.EROFS):
                f = open(self._path, 'rb')
            isipokua:
                raise
        self._file = f
        self._toc = Tupu
        self._next_key = 0
        self._pending = Uongo       # No changes require rewriting the file.
        self._pending_sync = Uongo  # No need to sync the file
        self._locked = Uongo
        self._file_length = Tupu    # Used to record mailbox size

    eleza add(self, message):
        """Add message na rudisha assigned key."""
        self._lookup()
        self._toc[self._next_key] = self._append_message(message)
        self._next_key += 1
        # _append_message appends the message to the mailbox file. We
        # don't need a full rewrite + rename, sync ni enough.
        self._pending_sync = Kweli
        rudisha self._next_key - 1

    eleza remove(self, key):
        """Remove the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        self._lookup(key)
        toa self._toc[key]
        self._pending = Kweli

    eleza __setitem__(self, key, message):
        """Replace the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        self._lookup(key)
        self._toc[key] = self._append_message(message)
        self._pending = Kweli

    eleza iterkeys(self):
        """Return an iterator over keys."""
        self._lookup()
        tuma kutoka self._toc.keys()

    eleza __contains__(self, key):
        """Return Kweli ikiwa the keyed message exists, Uongo otherwise."""
        self._lookup()
        rudisha key kwenye self._toc

    eleza __len__(self):
        """Return a count of messages kwenye the mailbox."""
        self._lookup()
        rudisha len(self._toc)

    eleza lock(self):
        """Lock the mailbox."""
        ikiwa sio self._locked:
            _lock_file(self._file)
            self._locked = Kweli

    eleza unlock(self):
        """Unlock the mailbox ikiwa it ni locked."""
        ikiwa self._locked:
            _unlock_file(self._file)
            self._locked = Uongo

    eleza flush(self):
        """Write any pending changes to disk."""
        ikiwa sio self._pending:
            ikiwa self._pending_sync:
                # Messages have only been added, so syncing the file
                # ni enough.
                _sync_flush(self._file)
                self._pending_sync = Uongo
            rudisha

        # In order to be writing anything out at all, self._toc must
        # already have been generated (and presumably has been modified
        # by adding ama deleting an item).
        assert self._toc ni sio Tupu

        # Check length of self._file; ikiwa it's changed, some other process
        # has modified the mailbox since we scanned it.
        self._file.seek(0, 2)
        cur_len = self._file.tell()
        ikiwa cur_len != self._file_length:
            ashiria ExternalClashError('Size of mailbox file changed '
                                     '(expected %i, found %i)' %
                                     (self._file_length, cur_len))

        new_file = _create_temporary(self._path)
        jaribu:
            new_toc = {}
            self._pre_mailbox_hook(new_file)
            kila key kwenye sorted(self._toc.keys()):
                start, stop = self._toc[key]
                self._file.seek(start)
                self._pre_message_hook(new_file)
                new_start = new_file.tell()
                wakati Kweli:
                    buffer = self._file.read(min(4096,
                                                 stop - self._file.tell()))
                    ikiwa sio buffer:
                        koma
                    new_file.write(buffer)
                new_toc[key] = (new_start, new_file.tell())
                self._post_message_hook(new_file)
            self._file_length = new_file.tell()
        tatizo:
            new_file.close()
            os.remove(new_file.name)
            raise
        _sync_close(new_file)
        # self._file ni about to get replaced, so no need to sync.
        self._file.close()
        # Make sure the new file's mode ni the same kama the old file's
        mode = os.stat(self._path).st_mode
        os.chmod(new_file.name, mode)
        jaribu:
            os.rename(new_file.name, self._path)
        tatizo FileExistsError:
            os.remove(self._path)
            os.rename(new_file.name, self._path)
        self._file = open(self._path, 'rb+')
        self._toc = new_toc
        self._pending = Uongo
        self._pending_sync = Uongo
        ikiwa self._locked:
            _lock_file(self._file, dotlock=Uongo)

    eleza _pre_mailbox_hook(self, f):
        """Called before writing the mailbox to file f."""
        rudisha

    eleza _pre_message_hook(self, f):
        """Called before writing each message to file f."""
        rudisha

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        rudisha

    eleza close(self):
        """Flush na close the mailbox."""
        jaribu:
            self.flush()
        mwishowe:
            jaribu:
                ikiwa self._locked:
                    self.unlock()
            mwishowe:
                self._file.close()  # Sync has been done by self.flush() above.

    eleza _lookup(self, key=Tupu):
        """Return (start, stop) ama ashiria KeyError."""
        ikiwa self._toc ni Tupu:
            self._generate_toc()
        ikiwa key ni sio Tupu:
            jaribu:
                rudisha self._toc[key]
            tatizo KeyError:
                ashiria KeyError('No message ukijumuisha key: %s' % key) kutoka Tupu

    eleza _append_message(self, message):
        """Append message to mailbox na rudisha (start, stop) offsets."""
        self._file.seek(0, 2)
        before = self._file.tell()
        ikiwa len(self._toc) == 0 na sio self._pending:
            # This ni the first message, na the _pre_mailbox_hook
            # hasn't yet been called. If self._pending ni Kweli,
            # messages have been removed, so _pre_mailbox_hook must
            # have been called already.
            self._pre_mailbox_hook(self._file)
        jaribu:
            self._pre_message_hook(self._file)
            offsets = self._install_message(message)
            self._post_message_hook(self._file)
        tatizo BaseException:
            self._file.truncate(before)
            raise
        self._file.flush()
        self._file_length = self._file.tell()  # Record current length of mailbox
        rudisha offsets



kundi _mboxMMDF(_singlefileMailbox):
    """An mbox ama MMDF mailbox."""

    _mangle_from_ = Kweli

    eleza get_message(self, key):
        """Return a Message representation ama ashiria a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        from_line = self._file.readline().replace(linesep, b'')
        string = self._file.read(stop - self._file.tell())
        msg = self._message_factory(string.replace(linesep, b'\n'))
        msg.set_from(from_line[5:].decode('ascii'))
        rudisha msg

    eleza get_string(self, key, from_=Uongo):
        """Return a string representation ama ashiria a KeyError."""
        rudisha email.message_from_bytes(
            self.get_bytes(key, from_)).as_string(unixfrom=from_)

    eleza get_bytes(self, key, from_=Uongo):
        """Return a string representation ama ashiria a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        ikiwa sio from_:
            self._file.readline()
        string = self._file.read(stop - self._file.tell())
        rudisha string.replace(linesep, b'\n')

    eleza get_file(self, key, from_=Uongo):
        """Return a file-like representation ama ashiria a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        ikiwa sio from_:
            self._file.readline()
        rudisha _PartialFile(self._file, self._file.tell(), stop)

    eleza _install_message(self, message):
        """Format a message na blindly write to self._file."""
        from_line = Tupu
        ikiwa isinstance(message, str):
            message = self._string_to_bytes(message)
        ikiwa isinstance(message, bytes) na message.startswith(b'From '):
            newline = message.find(b'\n')
            ikiwa newline != -1:
                from_line = message[:newline]
                message = message[newline + 1:]
            isipokua:
                from_line = message
                message = b''
        lasivyo isinstance(message, _mboxMMDFMessage):
            author = message.get_from().encode('ascii')
            from_line = b'From ' + author
        lasivyo isinstance(message, email.message.Message):
            from_line = message.get_unixfrom()  # May be Tupu.
            ikiwa from_line ni sio Tupu:
                from_line = from_line.encode('ascii')
        ikiwa from_line ni Tupu:
            from_line = b'From MAILER-DAEMON ' + time.asctime(time.gmtime()).encode()
        start = self._file.tell()
        self._file.write(from_line + linesep)
        self._dump_message(message, self._file, self._mangle_from_)
        stop = self._file.tell()
        rudisha (start, stop)


kundi mbox(_mboxMMDF):
    """A classic mbox mailbox."""

    _mangle_from_ = Kweli

    # All messages must end kwenye a newline character, na
    # _post_message_hooks outputs an empty line between messages.
    _append_newline = Kweli

    eleza __init__(self, path, factory=Tupu, create=Kweli):
        """Initialize an mbox mailbox."""
        self._message_factory = mboxMessage
        _mboxMMDF.__init__(self, path, factory, create)

    eleza _post_message_hook(self, f):
        """Called after writing each message to file f."""
        f.write(linesep)

    eleza _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        last_was_empty = Uongo
        self._file.seek(0)
        wakati Kweli:
            line_pos = self._file.tell()
            line = self._file.readline()
            ikiwa line.startswith(b'From '):
                ikiwa len(stops) < len(starts):
                    ikiwa last_was_empty:
                        stops.append(line_pos - len(linesep))
                    isipokua:
                        # The last line before the "From " line wasn't
                        # blank, but we consider it a start of a
                        # message anyway.
                        stops.append(line_pos)
                starts.append(line_pos)
                last_was_empty = Uongo
            lasivyo sio line:
                ikiwa last_was_empty:
                    stops.append(line_pos - len(linesep))
                isipokua:
                    stops.append(line_pos)
                koma
            lasivyo line == linesep:
                last_was_empty = Kweli
            isipokua:
                last_was_empty = Uongo
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()


kundi MMDF(_mboxMMDF):
    """An MMDF mailbox."""

    eleza __init__(self, path, factory=Tupu, create=Kweli):
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
        wakati Kweli:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            ikiwa line.startswith(b'\001\001\001\001' + linesep):
                starts.append(next_pos)
                wakati Kweli:
                    line_pos = next_pos
                    line = self._file.readline()
                    next_pos = self._file.tell()
                    ikiwa line == b'\001\001\001\001' + linesep:
                        stops.append(line_pos - len(linesep))
                        koma
                    lasivyo sio line:
                        stops.append(line_pos)
                        koma
            lasivyo sio line:
                koma
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file.seek(0, 2)
        self._file_length = self._file.tell()


kundi MH(Mailbox):
    """An MH mailbox."""

    eleza __init__(self, path, factory=Tupu, create=Kweli):
        """Initialize an MH instance."""
        Mailbox.__init__(self, path, factory, create)
        ikiwa sio os.path.exists(self._path):
            ikiwa create:
                os.mkdir(self._path, 0o700)
                os.close(os.open(os.path.join(self._path, '.mh_sequences'),
                                 os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            isipokua:
                ashiria NoSuchMailboxError(self._path)
        self._locked = Uongo

    eleza add(self, message):
        """Add message na rudisha assigned key."""
        keys = self.keys()
        ikiwa len(keys) == 0:
            new_key = 1
        isipokua:
            new_key = max(keys) + 1
        new_path = os.path.join(self._path, str(new_key))
        f = _create_carefully(new_path)
        closed = Uongo
        jaribu:
            ikiwa self._locked:
                _lock_file(f)
            jaribu:
                jaribu:
                    self._dump_message(message, f)
                tatizo BaseException:
                    # Unlock na close so it can be deleted on Windows
                    ikiwa self._locked:
                        _unlock_file(f)
                    _sync_close(f)
                    closed = Kweli
                    os.remove(new_path)
                    raise
                ikiwa isinstance(message, MHMessage):
                    self._dump_sequences(message, new_key)
            mwishowe:
                ikiwa self._locked:
                    _unlock_file(f)
        mwishowe:
            ikiwa sio closed:
                _sync_close(f)
        rudisha new_key

    eleza remove(self, key):
        """Remove the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        path = os.path.join(self._path, str(key))
        jaribu:
            f = open(path, 'rb+')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ashiria KeyError('No message ukijumuisha key: %s' % key)
            isipokua:
                raise
        isipokua:
            f.close()
            os.remove(path)

    eleza __setitem__(self, key, message):
        """Replace the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        path = os.path.join(self._path, str(key))
        jaribu:
            f = open(path, 'rb+')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ashiria KeyError('No message ukijumuisha key: %s' % key)
            isipokua:
                raise
        jaribu:
            ikiwa self._locked:
                _lock_file(f)
            jaribu:
                os.close(os.open(path, os.O_WRONLY | os.O_TRUNC))
                self._dump_message(message, f)
                ikiwa isinstance(message, MHMessage):
                    self._dump_sequences(message, key)
            mwishowe:
                ikiwa self._locked:
                    _unlock_file(f)
        mwishowe:
            _sync_close(f)

    eleza get_message(self, key):
        """Return a Message representation ama ashiria a KeyError."""
        jaribu:
            ikiwa self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            isipokua:
                f = open(os.path.join(self._path, str(key)), 'rb')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ashiria KeyError('No message ukijumuisha key: %s' % key)
            isipokua:
                raise
        ukijumuisha f:
            ikiwa self._locked:
                _lock_file(f)
            jaribu:
                msg = MHMessage(f)
            mwishowe:
                ikiwa self._locked:
                    _unlock_file(f)
        kila name, key_list kwenye self.get_sequences().items():
            ikiwa key kwenye key_list:
                msg.add_sequence(name)
        rudisha msg

    eleza get_bytes(self, key):
        """Return a bytes representation ama ashiria a KeyError."""
        jaribu:
            ikiwa self._locked:
                f = open(os.path.join(self._path, str(key)), 'rb+')
            isipokua:
                f = open(os.path.join(self._path, str(key)), 'rb')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ashiria KeyError('No message ukijumuisha key: %s' % key)
            isipokua:
                raise
        ukijumuisha f:
            ikiwa self._locked:
                _lock_file(f)
            jaribu:
                rudisha f.read().replace(linesep, b'\n')
            mwishowe:
                ikiwa self._locked:
                    _unlock_file(f)

    eleza get_file(self, key):
        """Return a file-like representation ama ashiria a KeyError."""
        jaribu:
            f = open(os.path.join(self._path, str(key)), 'rb')
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENOENT:
                ashiria KeyError('No message ukijumuisha key: %s' % key)
            isipokua:
                raise
        rudisha _ProxyFile(f)

    eleza iterkeys(self):
        """Return an iterator over keys."""
        rudisha iter(sorted(int(entry) kila entry kwenye os.listdir(self._path)
                                      ikiwa entry.isdigit()))

    eleza __contains__(self, key):
        """Return Kweli ikiwa the keyed message exists, Uongo otherwise."""
        rudisha os.path.exists(os.path.join(self._path, str(key)))

    eleza __len__(self):
        """Return a count of messages kwenye the mailbox."""
        rudisha len(list(self.iterkeys()))

    eleza lock(self):
        """Lock the mailbox."""
        ikiwa sio self._locked:
            self._file = open(os.path.join(self._path, '.mh_sequences'), 'rb+')
            _lock_file(self._file)
            self._locked = Kweli

    eleza unlock(self):
        """Unlock the mailbox ikiwa it ni locked."""
        ikiwa self._locked:
            _unlock_file(self._file)
            _sync_close(self._file)
            toa self._file
            self._locked = Uongo

    eleza flush(self):
        """Write any pending changes to the disk."""
        rudisha

    eleza close(self):
        """Flush na close the mailbox."""
        ikiwa self._locked:
            self.unlock()

    eleza list_folders(self):
        """Return a list of folder names."""
        result = []
        kila entry kwenye os.listdir(self._path):
            ikiwa os.path.isdir(os.path.join(self._path, entry)):
                result.append(entry)
        rudisha result

    eleza get_folder(self, folder):
        """Return an MH instance kila the named folder."""
        rudisha MH(os.path.join(self._path, folder),
                  factory=self._factory, create=Uongo)

    eleza add_folder(self, folder):
        """Create a folder na rudisha an MH instance representing it."""
        rudisha MH(os.path.join(self._path, folder),
                  factory=self._factory)

    eleza remove_folder(self, folder):
        """Delete the named folder, which must be empty."""
        path = os.path.join(self._path, folder)
        entries = os.listdir(path)
        ikiwa entries == ['.mh_sequences']:
            os.remove(os.path.join(path, '.mh_sequences'))
        lasivyo entries == []:
            pita
        isipokua:
            ashiria NotEmptyError('Folder sio empty: %s' % self._path)
        os.rmdir(path)

    eleza get_sequences(self):
        """Return a name-to-key-list dictionary to define each sequence."""
        results = {}
        ukijumuisha open(os.path.join(self._path, '.mh_sequences'), 'r', encoding='ASCII') kama f:
            all_keys = set(self.keys())
            kila line kwenye f:
                jaribu:
                    name, contents = line.split(':')
                    keys = set()
                    kila spec kwenye contents.split():
                        ikiwa spec.isdigit():
                            keys.add(int(spec))
                        isipokua:
                            start, stop = (int(x) kila x kwenye spec.split('-'))
                            keys.update(range(start, stop + 1))
                    results[name] = [key kila key kwenye sorted(keys) \
                                         ikiwa key kwenye all_keys]
                    ikiwa len(results[name]) == 0:
                        toa results[name]
                tatizo ValueError:
                    ashiria FormatError('Invalid sequence specification: %s' %
                                      line.rstrip())
        rudisha results

    eleza set_sequences(self, sequences):
        """Set sequences using the given name-to-key-list dictionary."""
        f = open(os.path.join(self._path, '.mh_sequences'), 'r+', encoding='ASCII')
        jaribu:
            os.close(os.open(f.name, os.O_WRONLY | os.O_TRUNC))
            kila name, keys kwenye sequences.items():
                ikiwa len(keys) == 0:
                    endelea
                f.write(name + ':')
                prev = Tupu
                completing = Uongo
                kila key kwenye sorted(set(keys)):
                    ikiwa key - 1 == prev:
                        ikiwa sio completing:
                            completing = Kweli
                            f.write('-')
                    lasivyo completing:
                        completing = Uongo
                        f.write('%s %s' % (prev, key))
                    isipokua:
                        f.write(' %s' % key)
                    prev = key
                ikiwa completing:
                    f.write(str(prev) + '\n')
                isipokua:
                    f.write('\n')
        mwishowe:
            _sync_close(f)

    eleza pack(self):
        """Re-name messages to eliminate numbering gaps. Invalidates keys."""
        sequences = self.get_sequences()
        prev = 0
        changes = []
        kila key kwenye self.iterkeys():
            ikiwa key - 1 != prev:
                changes.append((key, prev + 1))
                jaribu:
                    os.link(os.path.join(self._path, str(key)),
                            os.path.join(self._path, str(prev + 1)))
                tatizo (AttributeError, PermissionError):
                    os.rename(os.path.join(self._path, str(key)),
                              os.path.join(self._path, str(prev + 1)))
                isipokua:
                    os.unlink(os.path.join(self._path, str(key)))
            prev += 1
        self._next_key = prev + 1
        ikiwa len(changes) == 0:
            rudisha
        kila name, key_list kwenye sequences.items():
            kila old, new kwenye changes:
                ikiwa old kwenye key_list:
                    key_list[key_list.index(old)] = new
        self.set_sequences(sequences)

    eleza _dump_sequences(self, message, key):
        """Inspect a new MHMessage na update sequences appropriately."""
        pending_sequences = message.get_sequences()
        all_sequences = self.get_sequences()
        kila name, key_list kwenye all_sequences.items():
            ikiwa name kwenye pending_sequences:
                key_list.append(key)
            lasivyo key kwenye key_list:
                toa key_list[key_list.index(key)]
        kila sequence kwenye pending_sequences:
            ikiwa sequence haiko kwenye all_sequences:
                all_sequences[sequence] = [key]
        self.set_sequences(all_sequences)


kundi Babyl(_singlefileMailbox):
    """An Rmail-style Babyl mailbox."""

    _special_labels = frozenset({'unseen', 'deleted', 'filed', 'answered',
                                 'forwarded', 'edited', 'resent'})

    eleza __init__(self, path, factory=Tupu, create=Kweli):
        """Initialize a Babyl mailbox."""
        _singlefileMailbox.__init__(self, path, factory, create)
        self._labels = {}

    eleza add(self, message):
        """Add message na rudisha assigned key."""
        key = _singlefileMailbox.add(self, message)
        ikiwa isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()
        rudisha key

    eleza remove(self, key):
        """Remove the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        _singlefileMailbox.remove(self, key)
        ikiwa key kwenye self._labels:
            toa self._labels[key]

    eleza __setitem__(self, key, message):
        """Replace the keyed message; ashiria KeyError ikiwa it doesn't exist."""
        _singlefileMailbox.__setitem__(self, key, message)
        ikiwa isinstance(message, BabylMessage):
            self._labels[key] = message.get_labels()

    eleza get_message(self, key):
        """Return a Message representation ama ashiria a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        wakati Kweli:
            line = self._file.readline()
            ikiwa line == b'*** EOOH ***' + linesep ama sio line:
                koma
            original_headers.write(line.replace(linesep, b'\n'))
        visible_headers = io.BytesIO()
        wakati Kweli:
            line = self._file.readline()
            ikiwa line == linesep ama sio line:
                koma
            visible_headers.write(line.replace(linesep, b'\n'))
        # Read up to the stop, ama to the end
        n = stop - self._file.tell()
        assert n >= 0
        body = self._file.read(n)
        body = body.replace(linesep, b'\n')
        msg = BabylMessage(original_headers.getvalue() + body)
        msg.set_visible(visible_headers.getvalue())
        ikiwa key kwenye self._labels:
            msg.set_labels(self._labels[key])
        rudisha msg

    eleza get_bytes(self, key):
        """Return a string representation ama ashiria a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        self._file.readline()   # Skip b'1,' line specifying labels.
        original_headers = io.BytesIO()
        wakati Kweli:
            line = self._file.readline()
            ikiwa line == b'*** EOOH ***' + linesep ama sio line:
                koma
            original_headers.write(line.replace(linesep, b'\n'))
        wakati Kweli:
            line = self._file.readline()
            ikiwa line == linesep ama sio line:
                koma
        headers = original_headers.getvalue()
        n = stop - self._file.tell()
        assert n >= 0
        data = self._file.read(n)
        data = data.replace(linesep, b'\n')
        rudisha headers + data

    eleza get_file(self, key):
        """Return a file-like representation ama ashiria a KeyError."""
        rudisha io.BytesIO(self.get_bytes(key).replace(b'\n', linesep))

    eleza get_labels(self):
        """Return a list of user-defined labels kwenye the mailbox."""
        self._lookup()
        labels = set()
        kila label_list kwenye self._labels.values():
            labels.update(label_list)
        labels.difference_update(self._special_labels)
        rudisha list(labels)

    eleza _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        next_pos = 0
        label_lists = []
        wakati Kweli:
            line_pos = next_pos
            line = self._file.readline()
            next_pos = self._file.tell()
            ikiwa line == b'\037\014' + linesep:
                ikiwa len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
                starts.append(next_pos)
                labels = [label.strip() kila label
                                        kwenye self._file.readline()[1:].split(b',')
                                        ikiwa label.strip()]
                label_lists.append(labels)
            lasivyo line == b'\037' ama line == b'\037' + linesep:
                ikiwa len(stops) < len(starts):
                    stops.append(line_pos - len(linesep))
            lasivyo sio line:
                stops.append(line_pos - len(linesep))
                koma
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
        labels = (label.encode() kila label kwenye labels)
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
        """Write message contents na rudisha (start, stop)."""
        start = self._file.tell()
        ikiwa isinstance(message, BabylMessage):
            special_labels = []
            labels = []
            kila label kwenye message.get_labels():
                ikiwa label kwenye self._special_labels:
                    special_labels.append(label)
                isipokua:
                    labels.append(label)
            self._file.write(b'1')
            kila label kwenye special_labels:
                self._file.write(b', ' + label.encode())
            self._file.write(b',,')
            kila label kwenye labels:
                self._file.write(b' ' + label.encode() + b',')
            self._file.write(linesep)
        isipokua:
            self._file.write(b'1,,' + linesep)
        ikiwa isinstance(message, email.message.Message):
            orig_buffer = io.BytesIO()
            orig_generator = email.generator.BytesGenerator(orig_buffer, Uongo, 0)
            orig_generator.flatten(message)
            orig_buffer.seek(0)
            wakati Kweli:
                line = orig_buffer.readline()
                self._file.write(line.replace(b'\n', linesep))
                ikiwa line == b'\n' ama sio line:
                    koma
            self._file.write(b'*** EOOH ***' + linesep)
            ikiwa isinstance(message, BabylMessage):
                vis_buffer = io.BytesIO()
                vis_generator = email.generator.BytesGenerator(vis_buffer, Uongo, 0)
                vis_generator.flatten(message.get_visible())
                wakati Kweli:
                    line = vis_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    ikiwa line == b'\n' ama sio line:
                        koma
            isipokua:
                orig_buffer.seek(0)
                wakati Kweli:
                    line = orig_buffer.readline()
                    self._file.write(line.replace(b'\n', linesep))
                    ikiwa line == b'\n' ama sio line:
                        koma
            wakati Kweli:
                buffer = orig_buffer.read(4096) # Buffer size ni arbitrary.
                ikiwa sio buffer:
                    koma
                self._file.write(buffer.replace(b'\n', linesep))
        lasivyo isinstance(message, (bytes, str, io.StringIO)):
            ikiwa isinstance(message, io.StringIO):
                warnings.warn("Use of StringIO input ni deprecated, "
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
            isipokua:
                self._file.write(b'*** EOOH ***' + linesep + linesep)
                self._file.write(message.replace(b'\n', linesep))
        lasivyo hasattr(message, 'readline'):
            ikiwa hasattr(message, 'buffer'):
                warnings.warn("Use of text mode files ni deprecated, "
                    "use a binary mode file instead", DeprecationWarning, 3)
                message = message.buffer
            original_pos = message.tell()
            first_pita = Kweli
            wakati Kweli:
                line = message.readline()
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + b'\n'
                lasivyo line.endswith(b'\r'):
                    line = line[:-1] + b'\n'
                self._file.write(line.replace(b'\n', linesep))
                ikiwa line == b'\n' ama sio line:
                    ikiwa first_pita:
                        first_pita = Uongo
                        self._file.write(b'*** EOOH ***' + linesep)
                        message.seek(original_pos)
                    isipokua:
                        koma
            wakati Kweli:
                line = message.readline()
                ikiwa sio line:
                    koma
                # Universal newline support.
                ikiwa line.endswith(b'\r\n'):
                    line = line[:-2] + linesep
                lasivyo line.endswith(b'\r'):
                    line = line[:-1] + linesep
                lasivyo line.endswith(b'\n'):
                    line = line[:-1] + linesep
                self._file.write(line)
        isipokua:
            ashiria TypeError('Invalid message type: %s' % type(message))
        stop = self._file.tell()
        rudisha (start, stop)


kundi Message(email.message.Message):
    """Message ukijumuisha mailbox-format-specific properties."""

    eleza __init__(self, message=Tupu):
        """Initialize a Message instance."""
        ikiwa isinstance(message, email.message.Message):
            self._become_message(copy.deepcopy(message))
            ikiwa isinstance(message, Message):
                message._explain_to(self)
        lasivyo isinstance(message, bytes):
            self._become_message(email.message_from_bytes(message))
        lasivyo isinstance(message, str):
            self._become_message(email.message_from_string(message))
        lasivyo isinstance(message, io.TextIOWrapper):
            self._become_message(email.message_from_file(message))
        lasivyo hasattr(message, "read"):
            self._become_message(email.message_from_binary_file(message))
        lasivyo message ni Tupu:
            email.message.Message.__init__(self)
        isipokua:
            ashiria TypeError('Invalid message type: %s' % type(message))

    eleza _become_message(self, message):
        """Assume the non-format-specific state of message."""
        type_specific = getattr(message, '_type_specific_attributes', [])
        kila name kwenye message.__dict__:
            ikiwa name haiko kwenye type_specific:
                self.__dict__[name] = message.__dict__[name]

    eleza _explain_to(self, message):
        """Copy format-specific state to message insofar kama possible."""
        ikiwa isinstance(message, Message):
            rudisha  # There's nothing format-specific to explain.
        isipokua:
            ashiria TypeError('Cansio convert to specified type')


kundi MaildirMessage(Message):
    """Message ukijumuisha Maildir-specific properties."""

    _type_specific_attributes = ['_subdir', '_info', '_date']

    eleza __init__(self, message=Tupu):
        """Initialize a MaildirMessage instance."""
        self._subdir = 'new'
        self._info = ''
        self._date = time.time()
        Message.__init__(self, message)

    eleza get_subdir(self):
        """Return 'new' ama 'cur'."""
        rudisha self._subdir

    eleza set_subdir(self, subdir):
        """Set subdir to 'new' ama 'cur'."""
        ikiwa subdir == 'new' ama subdir == 'cur':
            self._subdir = subdir
        isipokua:
            ashiria ValueError("subdir must be 'new' ama 'cur': %s" % subdir)

    eleza get_flags(self):
        """Return kama a string the flags that are set."""
        ikiwa self._info.startswith('2,'):
            rudisha self._info[2:]
        isipokua:
            rudisha ''

    eleza set_flags(self, flags):
        """Set the given flags na unset all others."""
        self._info = '2,' + ''.join(sorted(flags))

    eleza add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    eleza remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        ikiwa self.get_flags():
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    eleza get_date(self):
        """Return delivery date of message, kwenye seconds since the epoch."""
        rudisha self._date

    eleza set_date(self, date):
        """Set delivery date of message, kwenye seconds since the epoch."""
        jaribu:
            self._date = float(date)
        tatizo ValueError:
            ashiria TypeError("can't convert to float: %s" % date) kutoka Tupu

    eleza get_info(self):
        """Get the message's "info" kama a string."""
        rudisha self._info

    eleza set_info(self, info):
        """Set the message's "info" string."""
        ikiwa isinstance(info, str):
            self._info = info
        isipokua:
            ashiria TypeError('info must be a string: %s' % type(info))

    eleza _explain_to(self, message):
        """Copy Maildir-specific state to message insofar kama possible."""
        ikiwa isinstance(message, MaildirMessage):
            message.set_flags(self.get_flags())
            message.set_subdir(self.get_subdir())
            message.set_date(self.get_date())
        lasivyo isinstance(message, _mboxMMDFMessage):
            flags = set(self.get_flags())
            ikiwa 'S' kwenye flags:
                message.add_flag('R')
            ikiwa self.get_subdir() == 'cur':
                message.add_flag('O')
            ikiwa 'T' kwenye flags:
                message.add_flag('D')
            ikiwa 'F' kwenye flags:
                message.add_flag('F')
            ikiwa 'R' kwenye flags:
                message.add_flag('A')
            message.set_from('MAILER-DAEMON', time.gmtime(self.get_date()))
        lasivyo isinstance(message, MHMessage):
            flags = set(self.get_flags())
            ikiwa 'S' haiko kwenye flags:
                message.add_sequence('unseen')
            ikiwa 'R' kwenye flags:
                message.add_sequence('replied')
            ikiwa 'F' kwenye flags:
                message.add_sequence('flagged')
        lasivyo isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            ikiwa 'S' haiko kwenye flags:
                message.add_label('unseen')
            ikiwa 'T' kwenye flags:
                message.add_label('deleted')
            ikiwa 'R' kwenye flags:
                message.add_label('answered')
            ikiwa 'P' kwenye flags:
                message.add_label('forwarded')
        lasivyo isinstance(message, Message):
            pita
        isipokua:
            ashiria TypeError('Cansio convert to specified type: %s' %
                            type(message))


kundi _mboxMMDFMessage(Message):
    """Message ukijumuisha mbox- ama MMDF-specific properties."""

    _type_specific_attributes = ['_from']

    eleza __init__(self, message=Tupu):
        """Initialize an mboxMMDFMessage instance."""
        self.set_from('MAILER-DAEMON', Kweli)
        ikiwa isinstance(message, email.message.Message):
            unixkutoka = message.get_unixfrom()
            ikiwa unixkutoka ni sio Tupu na unixfrom.startswith('From '):
                self.set_from(unixfrom[5:])
        Message.__init__(self, message)

    eleza get_from(self):
        """Return contents of "From " line."""
        rudisha self._from

    eleza set_from(self, from_, time_=Tupu):
        """Set "From " line, formatting na appending time_ ikiwa specified."""
        ikiwa time_ ni sio Tupu:
            ikiwa time_ ni Kweli:
                time_ = time.gmtime()
            from_ += ' ' + time.asctime(time_)
        self._kutoka = from_

    eleza get_flags(self):
        """Return kama a string the flags that are set."""
        rudisha self.get('Status', '') + self.get('X-Status', '')

    eleza set_flags(self, flags):
        """Set the given flags na unset all others."""
        flags = set(flags)
        status_flags, xstatus_flags = '', ''
        kila flag kwenye ('R', 'O'):
            ikiwa flag kwenye flags:
                status_flags += flag
                flags.remove(flag)
        kila flag kwenye ('D', 'F', 'A'):
            ikiwa flag kwenye flags:
                xstatus_flags += flag
                flags.remove(flag)
        xstatus_flags += ''.join(sorted(flags))
        jaribu:
            self.replace_header('Status', status_flags)
        tatizo KeyError:
            self.add_header('Status', status_flags)
        jaribu:
            self.replace_header('X-Status', xstatus_flags)
        tatizo KeyError:
            self.add_header('X-Status', xstatus_flags)

    eleza add_flag(self, flag):
        """Set the given flag(s) without changing others."""
        self.set_flags(''.join(set(self.get_flags()) | set(flag)))

    eleza remove_flag(self, flag):
        """Unset the given string flag(s) without changing others."""
        ikiwa 'Status' kwenye self ama 'X-Status' kwenye self:
            self.set_flags(''.join(set(self.get_flags()) - set(flag)))

    eleza _explain_to(self, message):
        """Copy mbox- ama MMDF-specific state to message insofar kama possible."""
        ikiwa isinstance(message, MaildirMessage):
            flags = set(self.get_flags())
            ikiwa 'O' kwenye flags:
                message.set_subdir('cur')
            ikiwa 'F' kwenye flags:
                message.add_flag('F')
            ikiwa 'A' kwenye flags:
                message.add_flag('R')
            ikiwa 'R' kwenye flags:
                message.add_flag('S')
            ikiwa 'D' kwenye flags:
                message.add_flag('T')
            toa message['status']
            toa message['x-status']
            maybe_date = ' '.join(self.get_from().split()[-5:])
            jaribu:
                message.set_date(calendar.timegm(time.strptime(maybe_date,
                                                      '%a %b %d %H:%M:%S %Y')))
            tatizo (ValueError, OverflowError):
                pita
        lasivyo isinstance(message, _mboxMMDFMessage):
            message.set_flags(self.get_flags())
            message.set_from(self.get_from())
        lasivyo isinstance(message, MHMessage):
            flags = set(self.get_flags())
            ikiwa 'R' haiko kwenye flags:
                message.add_sequence('unseen')
            ikiwa 'A' kwenye flags:
                message.add_sequence('replied')
            ikiwa 'F' kwenye flags:
                message.add_sequence('flagged')
            toa message['status']
            toa message['x-status']
        lasivyo isinstance(message, BabylMessage):
            flags = set(self.get_flags())
            ikiwa 'R' haiko kwenye flags:
                message.add_label('unseen')
            ikiwa 'D' kwenye flags:
                message.add_label('deleted')
            ikiwa 'A' kwenye flags:
                message.add_label('answered')
            toa message['status']
            toa message['x-status']
        lasivyo isinstance(message, Message):
            pita
        isipokua:
            ashiria TypeError('Cansio convert to specified type: %s' %
                            type(message))


kundi mboxMessage(_mboxMMDFMessage):
    """Message ukijumuisha mbox-specific properties."""


kundi MHMessage(Message):
    """Message ukijumuisha MH-specific properties."""

    _type_specific_attributes = ['_sequences']

    eleza __init__(self, message=Tupu):
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
            ikiwa sio sequence kwenye self._sequences:
                self._sequences.append(sequence)
        isipokua:
            ashiria TypeError('sequence type must be str: %s' % type(sequence))

    eleza remove_sequence(self, sequence):
        """Remove sequence kutoka the list of sequences including the message."""
        jaribu:
            self._sequences.remove(sequence)
        tatizo ValueError:
            pita

    eleza _explain_to(self, message):
        """Copy MH-specific state to message insofar kama possible."""
        ikiwa isinstance(message, MaildirMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' kwenye sequences:
                message.set_subdir('cur')
            isipokua:
                message.set_subdir('cur')
                message.add_flag('S')
            ikiwa 'flagged' kwenye sequences:
                message.add_flag('F')
            ikiwa 'replied' kwenye sequences:
                message.add_flag('R')
        lasivyo isinstance(message, _mboxMMDFMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' haiko kwenye sequences:
                message.add_flag('RO')
            isipokua:
                message.add_flag('O')
            ikiwa 'flagged' kwenye sequences:
                message.add_flag('F')
            ikiwa 'replied' kwenye sequences:
                message.add_flag('A')
        lasivyo isinstance(message, MHMessage):
            kila sequence kwenye self.get_sequences():
                message.add_sequence(sequence)
        lasivyo isinstance(message, BabylMessage):
            sequences = set(self.get_sequences())
            ikiwa 'unseen' kwenye sequences:
                message.add_label('unseen')
            ikiwa 'replied' kwenye sequences:
                message.add_label('answered')
        lasivyo isinstance(message, Message):
            pita
        isipokua:
            ashiria TypeError('Cansio convert to specified type: %s' %
                            type(message))


kundi BabylMessage(Message):
    """Message ukijumuisha Babyl-specific properties."""

    _type_specific_attributes = ['_labels', '_visible']

    eleza __init__(self, message=Tupu):
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
            ikiwa label haiko kwenye self._labels:
                self._labels.append(label)
        isipokua:
            ashiria TypeError('label must be a string: %s' % type(label))

    eleza remove_label(self, label):
        """Remove label kutoka the list of labels on the message."""
        jaribu:
            self._labels.remove(label)
        tatizo ValueError:
            pita

    eleza get_visible(self):
        """Return a Message representation of visible headers."""
        rudisha Message(self._visible)

    eleza set_visible(self, visible):
        """Set the Message representation of visible headers."""
        self._visible = Message(visible)

    eleza update_visible(self):
        """Update and/or sensibly generate a set of visible headers."""
        kila header kwenye self._visible.keys():
            ikiwa header kwenye self:
                self._visible.replace_header(header, self[header])
            isipokua:
                toa self._visible[header]
        kila header kwenye ('Date', 'From', 'Reply-To', 'To', 'CC', 'Subject'):
            ikiwa header kwenye self na header haiko kwenye self._visible:
                self._visible[header] = self[header]

    eleza _explain_to(self, message):
        """Copy Babyl-specific state to message insofar kama possible."""
        ikiwa isinstance(message, MaildirMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' kwenye labels:
                message.set_subdir('cur')
            isipokua:
                message.set_subdir('cur')
                message.add_flag('S')
            ikiwa 'forwarded' kwenye labels ama 'resent' kwenye labels:
                message.add_flag('P')
            ikiwa 'answered' kwenye labels:
                message.add_flag('R')
            ikiwa 'deleted' kwenye labels:
                message.add_flag('T')
        lasivyo isinstance(message, _mboxMMDFMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' haiko kwenye labels:
                message.add_flag('RO')
            isipokua:
                message.add_flag('O')
            ikiwa 'deleted' kwenye labels:
                message.add_flag('D')
            ikiwa 'answered' kwenye labels:
                message.add_flag('A')
        lasivyo isinstance(message, MHMessage):
            labels = set(self.get_labels())
            ikiwa 'unseen' kwenye labels:
                message.add_sequence('unseen')
            ikiwa 'answered' kwenye labels:
                message.add_sequence('replied')
        lasivyo isinstance(message, BabylMessage):
            message.set_visible(self.get_visible())
            kila label kwenye self.get_labels():
                message.add_label(label)
        lasivyo isinstance(message, Message):
            pita
        isipokua:
            ashiria TypeError('Cansio convert to specified type: %s' %
                            type(message))


kundi MMDFMessage(_mboxMMDFMessage):
    """Message ukijumuisha MMDF-specific properties."""


kundi _ProxyFile:
    """A read-only wrapper of a file."""

    eleza __init__(self, f, pos=Tupu):
        """Initialize a _ProxyFile."""
        self._file = f
        ikiwa pos ni Tupu:
            self._pos = f.tell()
        isipokua:
            self._pos = pos

    eleza read(self, size=Tupu):
        """Read bytes."""
        rudisha self._read(size, self._file.read)

    eleza read1(self, size=Tupu):
        """Read bytes."""
        rudisha self._read(size, self._file.read1)

    eleza readline(self, size=Tupu):
        """Read a line."""
        rudisha self._read(size, self._file.readline)

    eleza readlines(self, sizehint=Tupu):
        """Read multiple lines."""
        result = []
        kila line kwenye self:
            result.append(line)
            ikiwa sizehint ni sio Tupu:
                sizehint -= len(line)
                ikiwa sizehint <= 0:
                    koma
        rudisha result

    eleza __iter__(self):
        """Iterate over lines."""
        wakati Kweli:
            line = self.readline()
            ikiwa sio line:
                rudisha
            tuma line

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
            jaribu:
                ikiwa hasattr(self._file, 'close'):
                    self._file.close()
            mwishowe:
                toa self._file

    eleza _read(self, size, read_method):
        """Read size bytes using read_method."""
        ikiwa size ni Tupu:
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
        ikiwa sio hasattr(self, '_file'):
            rudisha Kweli
        ikiwa sio hasattr(self._file, 'closed'):
            rudisha Uongo
        rudisha self._file.closed


kundi _PartialFile(_ProxyFile):
    """A read-only wrapper of part of a file."""

    eleza __init__(self, f, start=Tupu, stop=Tupu):
        """Initialize a _PartialFile."""
        _ProxyFile.__init__(self, f, start)
        self._start = start
        self._stop = stop

    eleza tell(self):
        """Return the position ukijumuisha respect to start."""
        rudisha _ProxyFile.tell(self) - self._start

    eleza seek(self, offset, whence=0):
        """Change position, possibly ukijumuisha respect to start ama stop."""
        ikiwa whence == 0:
            self._pos = self._start
            whence = 1
        lasivyo whence == 2:
            self._pos = self._stop
            whence = 1
        _ProxyFile.seek(self, offset, whence)

    eleza _read(self, size, read_method):
        """Read size bytes using read_method, honoring start na stop."""
        remaining = self._stop - self._pos
        ikiwa remaining <= 0:
            rudisha b''
        ikiwa size ni Tupu ama size < 0 ama size > remaining:
            size = remaining
        rudisha _ProxyFile._read(self, size, read_method)

    eleza close(self):
        # do *not* close the underlying file object kila partial files,
        # since it's global to the mailbox object
        ikiwa hasattr(self, '_file'):
            toa self._file


eleza _lock_file(f, dotlock=Kweli):
    """Lock file f using lockf na dot locking."""
    dotlock_done = Uongo
    jaribu:
        ikiwa fcntl:
            jaribu:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            tatizo OSError kama e:
                ikiwa e.errno kwenye (errno.EAGAIN, errno.EACCES, errno.EROFS):
                    ashiria ExternalClashError('lockf: lock unavailable: %s' %
                                             f.name)
                isipokua:
                    raise
        ikiwa dotlock:
            jaribu:
                pre_lock = _create_temporary(f.name + '.lock')
                pre_lock.close()
            tatizo OSError kama e:
                ikiwa e.errno kwenye (errno.EACCES, errno.EROFS):
                    rudisha  # Without write access, just skip dotlocking.
                isipokua:
                    raise
            jaribu:
                jaribu:
                    os.link(pre_lock.name, f.name + '.lock')
                    dotlock_done = Kweli
                tatizo (AttributeError, PermissionError):
                    os.rename(pre_lock.name, f.name + '.lock')
                    dotlock_done = Kweli
                isipokua:
                    os.unlink(pre_lock.name)
            tatizo FileExistsError:
                os.remove(pre_lock.name)
                ashiria ExternalClashError('dot lock unavailable: %s' %
                                         f.name)
    tatizo:
        ikiwa fcntl:
            fcntl.lockf(f, fcntl.LOCK_UN)
        ikiwa dotlock_done:
            os.remove(f.name + '.lock')
        raise

eleza _unlock_file(f):
    """Unlock file f using lockf na dot locking."""
    ikiwa fcntl:
        fcntl.lockf(f, fcntl.LOCK_UN)
    ikiwa os.path.exists(f.name + '.lock'):
        os.remove(f.name + '.lock')

eleza _create_carefully(path):
    """Create a file ikiwa it doesn't exist na open kila reading na writing."""
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o666)
    jaribu:
        rudisha open(path, 'rb+')
    mwishowe:
        os.close(fd)

eleza _create_temporary(path):
    """Create a temp file based on path na open kila reading na writing."""
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
    """Raised kila module-specific errors."""

kundi NoSuchMailboxError(Error):
    """The specified mailbox does sio exist na won't be created."""

kundi NotEmptyError(Error):
    """The specified mailbox ni sio empty na deletion was requested."""

kundi ExternalClashError(Error):
    """Another process caused an action to fail."""

kundi FormatError(Error):
    """A file appears to have an invalid format."""
