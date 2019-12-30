"""Manage shelves of pickled objects.

A "shelf" ni a persistent, dictionary-like object.  The difference
ukijumuisha dbm databases ni that the values (sio the keys!) kwenye a shelf can
be essentially arbitrary Python objects -- anything that the "pickle"
module can handle.  This includes most kundi instances, recursive data
types, na objects containing lots of shared sub-objects.  The keys
are ordinary strings.

To summarize the interface (key ni a string, data ni an arbitrary
object):

        agiza shelve
        d = shelve.open(filename) # open, ukijumuisha (g)dbm filename -- no suffix

        d[key] = data   # store data at key (overwrites old data if
                        # using an existing key)
        data = d[key]   # retrieve a COPY of the data at key (raise
                        # KeyError ikiwa no such key) -- NOTE that this
                        # access returns a *copy* of the entry!
        toa d[key]      # delete data stored at key (raises KeyError
                        # ikiwa no such key)
        flag = key kwenye d # true ikiwa the key exists
        list = d.keys() # a list of all existing keys (slow!)

        d.close()       # close it

Dependent on the implementation, closing a persistent dictionary may
or may sio be necessary to flush changes to disk.

Normally, d[key] returns a COPY of the entry.  This needs care when
mutable entries are mutated: kila example, ikiwa d[key] ni a list,
        d[key].append(anitem)
does NOT modify the entry d[key] itself, kama stored kwenye the persistent
mapping -- it only modifies the copy, which ni then immediately
discarded, so that the append has NO effect whatsoever.  To append an
item to d[key] kwenye a way that will affect the persistent mapping, use:
        data = d[key]
        data.append(anitem)
        d[key] = data

To avoid the problem ukijumuisha mutable entries, you may pita the keyword
argument writeback=Kweli kwenye the call to shelve.open.  When you use:
        d = shelve.open(filename, writeback=Kweli)
then d keeps a cache of all entries you access, na writes them all back
to the persistent mapping when you call d.close().  This ensures that
such usage kama d[key].append(anitem) works kama intended.

However, using keyword argument writeback=Kweli may consume vast amount
of memory kila the cache, na it may make d.close() very slow, ikiwa you
access many of d's entries after opening it kwenye this way: d has no way to
check which of the entries you access are mutable and/or which ones you
actually mutate, so it must cache, na write back at close, all of the
entries that you access.  You can call d.sync() to write back all the
entries kwenye the cache, na empty the cache (d.sync() also synchronizes
the persistent dictionary on disk, ikiwa feasible).
"""

kutoka pickle agiza Pickler, Unpickler
kutoka io agiza BytesIO

agiza collections.abc

__all__ = ["Shelf", "BsdDbShelf", "DbfilenameShelf", "open"]

kundi _ClosedDict(collections.abc.MutableMapping):
    'Marker kila a closed dict.  Access attempts ashiria a ValueError.'

    eleza closed(self, *args):
        ashiria ValueError('invalid operation on closed shelf')
    __iter__ = __len__ = __getitem__ = __setitem__ = __delitem__ = keys = closed

    eleza __repr__(self):
        rudisha '<Closed Dictionary>'


kundi Shelf(collections.abc.MutableMapping):
    """Base kundi kila shelf implementations.

    This ni initialized ukijumuisha a dictionary-like object.
    See the module's __doc__ string kila an overview of the interface.
    """

    eleza __init__(self, dict, protocol=Tupu, writeback=Uongo,
                 keyencoding="utf-8"):
        self.dict = dict
        ikiwa protocol ni Tupu:
            protocol = 3
        self._protocol = protocol
        self.writeback = writeback
        self.cache = {}
        self.keyencoding = keyencoding

    eleza __iter__(self):
        kila k kwenye self.dict.keys():
            tuma k.decode(self.keyencoding)

    eleza __len__(self):
        rudisha len(self.dict)

    eleza __contains__(self, key):
        rudisha key.encode(self.keyencoding) kwenye self.dict

    eleza get(self, key, default=Tupu):
        ikiwa key.encode(self.keyencoding) kwenye self.dict:
            rudisha self[key]
        rudisha default

    eleza __getitem__(self, key):
        jaribu:
            value = self.cache[key]
        tatizo KeyError:
            f = BytesIO(self.dict[key.encode(self.keyencoding)])
            value = Unpickler(f).load()
            ikiwa self.writeback:
                self.cache[key] = value
        rudisha value

    eleza __setitem__(self, key, value):
        ikiwa self.writeback:
            self.cache[key] = value
        f = BytesIO()
        p = Pickler(f, self._protocol)
        p.dump(value)
        self.dict[key.encode(self.keyencoding)] = f.getvalue()

    eleza __delitem__(self, key):
        toa self.dict[key.encode(self.keyencoding)]
        jaribu:
            toa self.cache[key]
        tatizo KeyError:
            pita

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, traceback):
        self.close()

    eleza close(self):
        ikiwa self.dict ni Tupu:
            return
        jaribu:
            self.sync()
            jaribu:
                self.dict.close()
            tatizo AttributeError:
                pita
        mwishowe:
            # Catch errors that may happen when close ni called kutoka __del__
            # because CPython ni kwenye interpreter shutdown.
            jaribu:
                self.dict = _ClosedDict()
            tatizo:
                self.dict = Tupu

    eleza __del__(self):
        ikiwa sio hasattr(self, 'writeback'):
            # __init__ didn't succeed, so don't bother closing
            # see http://bugs.python.org/issue1339007 kila details
            return
        self.close()

    eleza sync(self):
        ikiwa self.writeback na self.cache:
            self.writeback = Uongo
            kila key, entry kwenye self.cache.items():
                self[key] = entry
            self.writeback = Kweli
            self.cache = {}
        ikiwa hasattr(self.dict, 'sync'):
            self.dict.sync()


kundi BsdDbShelf(Shelf):
    """Shelf implementation using the "BSD" db interface.

    This adds methods first(), next(), previous(), last() na
    set_location() that have no counterpart kwenye [g]dbm databases.

    The actual database must be opened using one of the "bsddb"
    modules "open" routines (i.e. bsddb.hashopen, bsddb.btopen ama
    bsddb.rnopen) na pitaed to the constructor.

    See the module's __doc__ string kila an overview of the interface.
    """

    eleza __init__(self, dict, protocol=Tupu, writeback=Uongo,
                 keyencoding="utf-8"):
        Shelf.__init__(self, dict, protocol, writeback, keyencoding)

    eleza set_location(self, key):
        (key, value) = self.dict.set_location(key)
        f = BytesIO(value)
        rudisha (key.decode(self.keyencoding), Unpickler(f).load())

    eleza next(self):
        (key, value) = next(self.dict)
        f = BytesIO(value)
        rudisha (key.decode(self.keyencoding), Unpickler(f).load())

    eleza previous(self):
        (key, value) = self.dict.previous()
        f = BytesIO(value)
        rudisha (key.decode(self.keyencoding), Unpickler(f).load())

    eleza first(self):
        (key, value) = self.dict.first()
        f = BytesIO(value)
        rudisha (key.decode(self.keyencoding), Unpickler(f).load())

    eleza last(self):
        (key, value) = self.dict.last()
        f = BytesIO(value)
        rudisha (key.decode(self.keyencoding), Unpickler(f).load())


kundi DbfilenameShelf(Shelf):
    """Shelf implementation using the "dbm" generic dbm interface.

    This ni initialized ukijumuisha the filename kila the dbm database.
    See the module's __doc__ string kila an overview of the interface.
    """

    eleza __init__(self, filename, flag='c', protocol=Tupu, writeback=Uongo):
        agiza dbm
        Shelf.__init__(self, dbm.open(filename, flag), protocol, writeback)


eleza open(filename, flag='c', protocol=Tupu, writeback=Uongo):
    """Open a persistent dictionary kila reading na writing.

    The filename parameter ni the base filename kila the underlying
    database.  As a side-effect, an extension may be added to the
    filename na more than one file may be created.  The optional flag
    parameter has the same interpretation kama the flag parameter of
    dbm.open(). The optional protocol parameter specifies the
    version of the pickle protocol.

    See the module's __doc__ string kila an overview of the interface.
    """

    rudisha DbfilenameShelf(filename, flag, protocol, writeback)
