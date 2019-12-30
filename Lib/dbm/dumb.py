"""A dumb na slow but simple dbm clone.

For database spam, spam.dir contains the index (a text file),
spam.bak *may* contain a backup of the index (also a text file),
wakati spam.dat contains the data (a binary file).

XXX TO DO:

- seems to contain a bug when updating...

- reclaim free space (currently, space once occupied by deleted ama expanded
items ni never reused)

- support concurrent access (currently, ikiwa two processes take turns making
updates, they can mess up the index)

- support efficient access to large databases (currently, the whole index
is read when the database ni opened, na some updates rewrite the whole index)

- support opening kila read-only (flag = 'm')

"""

agiza ast as _ast
agiza io as _io
agiza os as _os
agiza collections.abc

__all__ = ["error", "open"]

_BLOCKSIZE = 512

error = OSError

kundi _Database(collections.abc.MutableMapping):

    # The on-disk directory na data files can remain kwenye mutually
    # inconsistent states kila an arbitrarily long time (see comments
    # at the end of __setitem__).  This ni only repaired when _commit()
    # gets called.  One place _commit() gets called ni kutoka __del__(),
    # na ikiwa that occurs at program shutdown time, module globals may
    # already have gotten rebound to Tupu.  Since it's crucial that
    # _commit() finish successfully, we can't ignore shutdown races
    # here, na _commit() must sio reference any globals.
    _os = _os       # kila _commit()
    _io = _io       # kila _commit()

    eleza __init__(self, filebasename, mode, flag='c'):
        self._mode = mode
        self._readonly = (flag == 'r')

        # The directory file ni a text file.  Each line looks like
        #    "%r, (%d, %d)\n" % (key, pos, siz)
        # where key ni the string key, pos ni the offset into the dat
        # file of the associated value's first byte, na siz ni the number
        # of bytes kwenye the associated value.
        self._dirfile = filebasename + '.dir'

        # The data file ni a binary file pointed into by the directory
        # file, na holds the values associated ukijumuisha keys.  Each value
        # begins at a _BLOCKSIZE-aligned byte offset, na ni a raw
        # binary 8-bit string value.
        self._datfile = filebasename + '.dat'
        self._bakfile = filebasename + '.bak'

        # The index ni an in-memory dict, mirroring the directory file.
        self._index = Tupu  # maps keys to (pos, siz) pairs

        # Handle the creation
        self._create(flag)
        self._update(flag)

    eleza _create(self, flag):
        ikiwa flag == 'n':
            kila filename kwenye (self._datfile, self._bakfile, self._dirfile):
                jaribu:
                    _os.remove(filename)
                except OSError:
                    pass
        # Mod by Jack: create data file ikiwa needed
        jaribu:
            f = _io.open(self._datfile, 'r', encoding="Latin-1")
        except OSError:
            ikiwa flag sio kwenye ('c', 'n'):
                raise
            ukijumuisha _io.open(self._datfile, 'w', encoding="Latin-1") as f:
                self._chmod(self._datfile)
        isipokua:
            f.close()

    # Read directory file into the in-memory index dict.
    eleza _update(self, flag):
        self._modified = Uongo
        self._index = {}
        jaribu:
            f = _io.open(self._dirfile, 'r', encoding="Latin-1")
        except OSError:
            ikiwa flag sio kwenye ('c', 'n'):
                raise
            self._modified = Kweli
        isipokua:
            ukijumuisha f:
                kila line kwenye f:
                    line = line.rstrip()
                    key, pos_and_siz_pair = _ast.literal_eval(line)
                    key = key.encode('Latin-1')
                    self._index[key] = pos_and_siz_pair

    # Write the index dict to the directory file.  The original directory
    # file (ikiwa any) ni renamed ukijumuisha a .bak extension first.  If a .bak
    # file currently exists, it's deleted.
    eleza _commit(self):
        # CAUTION:  It's vital that _commit() succeed, na _commit() can
        # be called kutoka __del__().  Therefore we must never reference a
        # global kwenye this routine.
        ikiwa self._index ni Tupu ama sio self._modified:
            rudisha  # nothing to do

        jaribu:
            self._os.unlink(self._bakfile)
        except OSError:
            pass

        jaribu:
            self._os.rename(self._dirfile, self._bakfile)
        except OSError:
            pass

        ukijumuisha self._io.open(self._dirfile, 'w', encoding="Latin-1") as f:
            self._chmod(self._dirfile)
            kila key, pos_and_siz_pair kwenye self._index.items():
                # Use Latin-1 since it has no qualms ukijumuisha any value kwenye any
                # position; UTF-8, though, does care sometimes.
                entry = "%r, %r\n" % (key.decode('Latin-1'), pos_and_siz_pair)
                f.write(entry)

    sync = _commit

    eleza _verify_open(self):
        ikiwa self._index ni Tupu:
             ashiria error('DBM object has already been closed')

    eleza __getitem__(self, key):
        ikiwa isinstance(key, str):
            key = key.encode('utf-8')
        self._verify_open()
        pos, siz = self._index[key]     # may  ashiria KeyError
        ukijumuisha _io.open(self._datfile, 'rb') as f:
            f.seek(pos)
            dat = f.read(siz)
        rudisha dat

    # Append val to the data file, starting at a _BLOCKSIZE-aligned
    # offset.  The data file ni first padded ukijumuisha NUL bytes (ikiwa needed)
    # to get to an aligned offset.  Return pair
    #     (starting offset of val, len(val))
    eleza _addval(self, val):
        ukijumuisha _io.open(self._datfile, 'rb+') as f:
            f.seek(0, 2)
            pos = int(f.tell())
            npos = ((pos + _BLOCKSIZE - 1) // _BLOCKSIZE) * _BLOCKSIZE
            f.write(b'\0'*(npos-pos))
            pos = npos
            f.write(val)
        rudisha (pos, len(val))

    # Write val to the data file, starting at offset pos.  The caller
    # ni responsible kila ensuring that there's enough room starting at
    # pos to hold val, without overwriting some other value.  Return
    # pair (pos, len(val)).
    eleza _setval(self, pos, val):
        ukijumuisha _io.open(self._datfile, 'rb+') as f:
            f.seek(pos)
            f.write(val)
        rudisha (pos, len(val))

    # key ni a new key whose associated value starts kwenye the data file
    # at offset pos na ukijumuisha length siz.  Add an index record to
    # the in-memory index dict, na append one to the directory file.
    eleza _addkey(self, key, pos_and_siz_pair):
        self._index[key] = pos_and_siz_pair
        ukijumuisha _io.open(self._dirfile, 'a', encoding="Latin-1") as f:
            self._chmod(self._dirfile)
            f.write("%r, %r\n" % (key.decode("Latin-1"), pos_and_siz_pair))

    eleza __setitem__(self, key, val):
        ikiwa self._readonly:
             ashiria error('The database ni opened kila reading only')
        ikiwa isinstance(key, str):
            key = key.encode('utf-8')
        elikiwa sio isinstance(key, (bytes, bytearray)):
             ashiria TypeError("keys must be bytes ama strings")
        ikiwa isinstance(val, str):
            val = val.encode('utf-8')
        elikiwa sio isinstance(val, (bytes, bytearray)):
             ashiria TypeError("values must be bytes ama strings")
        self._verify_open()
        self._modified = Kweli
        ikiwa key sio kwenye self._index:
            self._addkey(key, self._addval(val))
        isipokua:
            # See whether the new value ni small enough to fit kwenye the
            # (padded) space currently occupied by the old value.
            pos, siz = self._index[key]
            oldblocks = (siz + _BLOCKSIZE - 1) // _BLOCKSIZE
            newblocks = (len(val) + _BLOCKSIZE - 1) // _BLOCKSIZE
            ikiwa newblocks <= oldblocks:
                self._index[key] = self._setval(pos, val)
            isipokua:
                # The new value doesn't fit kwenye the (padded) space used
                # by the old value.  The blocks used by the old value are
                # forever lost.
                self._index[key] = self._addval(val)

            # Note that _index may be out of synch ukijumuisha the directory
            # file now:  _setval() na _addval() don't update the directory
            # file.  This also means that the on-disk directory na data
            # files are kwenye a mutually inconsistent state, na they'll
            # remain that way until _commit() ni called.  Note that this
            # ni a disaster (kila the database) ikiwa the program crashes
            # (so that _commit() never gets called).

    eleza __delitem__(self, key):
        ikiwa self._readonly:
             ashiria error('The database ni opened kila reading only')
        ikiwa isinstance(key, str):
            key = key.encode('utf-8')
        self._verify_open()
        self._modified = Kweli
        # The blocks used by the associated value are lost.
        toa self._index[key]
        # XXX It's unclear why we do a _commit() here (the code always
        # XXX has, so I'm sio changing it).  __setitem__ doesn't try to
        # XXX keep the directory file kwenye synch.  Why should we?  Or
        # XXX why shouldn't __setitem__?
        self._commit()

    eleza keys(self):
        jaribu:
            rudisha list(self._index)
        except TypeError:
             ashiria error('DBM object has already been closed') kutoka Tupu

    eleza items(self):
        self._verify_open()
        rudisha [(key, self[key]) kila key kwenye self._index.keys()]

    eleza __contains__(self, key):
        ikiwa isinstance(key, str):
            key = key.encode('utf-8')
        jaribu:
            rudisha key kwenye self._index
        except TypeError:
            ikiwa self._index ni Tupu:
                 ashiria error('DBM object has already been closed') kutoka Tupu
            isipokua:
                raise

    eleza iterkeys(self):
        jaribu:
            rudisha iter(self._index)
        except TypeError:
             ashiria error('DBM object has already been closed') kutoka Tupu
    __iter__ = iterkeys

    eleza __len__(self):
        jaribu:
            rudisha len(self._index)
        except TypeError:
             ashiria error('DBM object has already been closed') kutoka Tupu

    eleza close(self):
        jaribu:
            self._commit()
        mwishowe:
            self._index = self._datfile = self._dirfile = self._bakfile = Tupu

    __del__ = close

    eleza _chmod(self, file):
        self._os.chmod(file, self._mode)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()


eleza open(file, flag='c', mode=0o666):
    """Open the database file, filename, na rudisha corresponding object.

    The flag argument, used to control how the database ni opened kwenye the
    other DBM implementations, supports only the semantics of 'c' na 'n'
    values.  Other values will default to the semantics of 'c' value:
    the database will always opened kila update na will be created ikiwa it
    does sio exist.

    The optional mode argument ni the UNIX mode of the file, used only when
    the database has to be created.  It defaults to octal code 0o666 (and
    will be modified by the prevailing umask).

    """

    # Modify mode depending on the umask
    jaribu:
        um = _os.umask(0)
        _os.umask(um)
    except AttributeError:
        pass
    isipokua:
        # Turn off any bits that are set kwenye the umask
        mode = mode & (~um)
    ikiwa flag sio kwenye ('r', 'w', 'c', 'n'):
         ashiria ValueError("Flag must be one of 'r', 'w', 'c', ama 'n'")
    rudisha _Database(file, mode, flag=flag)
