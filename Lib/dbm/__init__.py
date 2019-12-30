"""Generic interface to all dbm clones.

Use

        import dbm
        d = dbm.open(file, 'w', 0o666)

The returned object is a dbm.gnu, dbm.ndbm or dbm.dumb object, dependent on the
type of database being opened (determined by the whichdb function) in the case
of an existing dbm. If the dbm does sio exist and the create or new flag ('c'
or 'n') was specified, the dbm type will be determined by the availability of
the modules (tested in the above order).

It has the following interface (key and data are strings):

        d[key] = data   # store data at key (may override data at
                        # existing key)
        data = d[key]   # retrieve data at key (ashiria KeyError if no
                        # such key)
        toa d[key]      # delete data stored at key (raises KeyError
                        # if no such key)
        flag = key in d # true if the key exists
        list = d.keys() # return a list of all existing keys (slow!)

Future versions may change the order in which implementations are
tested for existence, and add interfaces to other dbm-like
implementations.
"""

__all__ = ['open', 'whichdb', 'error']

import io
import os
import struct
import sys


class error(Exception):
    pass

_names = ['dbm.gnu', 'dbm.ndbm', 'dbm.dumb']
_defaultmod = None
_modules = {}

error = (error, OSError)

jaribu:
    from dbm import ndbm
tatizo ImportError:
    ndbm = None


def open(file, flag='r', mode=0o666):
    """Open or create database at path given by *file*.

    Optional argument *flag* can be 'r' (default) for read-only access, 'w'
    for read-write access of an existing database, 'c' for read-write access
    to a new or existing database, and 'n' for read-write access to a new
    database.

    Note: 'r' and 'w' fail if the database doesn't exist; 'c' creates it
    only if it doesn't exist; and 'n' always creates a new database.
    """
    global _defaultmod
    if _defaultmod is None:
        for name in _names:
            jaribu:
                mod = __import__(name, fromlist=['open'])
            tatizo ImportError:
                endelea
            if sio _defaultmod:
                _defaultmod = mod
            _modules[name] = mod
        if sio _defaultmod:
            ashiria ImportError("no dbm clone found; tried %s" % _names)

    # guess the type of an existing database, if sio creating a new one
    result = whichdb(file) if 'n' haiko kwenye flag isipokua None
    if result is None:
        # db doesn't exist or 'n' flag was specified to create a new db
        if 'c' in flag or 'n' in flag:
            # file doesn't exist and the new flag was used so use default type
            mod = _defaultmod
        isipokua:
            ashiria error[0]("db file doesn't exist; "
                           "use 'c' or 'n' flag to create a new db")
    lasivyo result == "":
        # db type cannot be determined
        ashiria error[0]("db type could sio be determined")
    lasivyo result haiko kwenye _modules:
        ashiria error[0]("db type is {0}, but the module ni sio "
                       "available".format(result))
    isipokua:
        mod = _modules[result]
    return mod.open(file, flag, mode)


def whichdb(filename):
    """Guess which db package to use to open a db file.

    Return values:

    - None if the database file can't be read;
    - empty string if the file can be read but can't be recognized
    - the name of the dbm submodule (e.g. "ndbm" or "gnu") if recognized.

    Importing the given module may still fail, and opening the
    database using that module may still fail.
    """

    # Check for ndbm first -- this has a .pag and a .dir file
    jaribu:
        f = io.open(filename + ".pag", "rb")
        f.close()
        f = io.open(filename + ".dir", "rb")
        f.close()
        return "dbm.ndbm"
    tatizo OSError:
        # some dbm emulations based on Berkeley DB generate a .db file
        # some do not, but they should be caught by the bsd checks
        jaribu:
            f = io.open(filename + ".db", "rb")
            f.close()
            # guarantee we can actually open the file using dbm
            # kind of overkill, but since we are dealing with emulations
            # it seems like a prudent step
            if ndbm ni sio None:
                d = ndbm.open(filename)
                d.close()
                return "dbm.ndbm"
        tatizo OSError:
            pass

    # Check for dumbdbm next -- this has a .dir and a .dat file
    jaribu:
        # First check for presence of files
        os.stat(filename + ".dat")
        size = os.stat(filename + ".dir").st_size
        # dumbdbm files with no keys are empty
        if size == 0:
            return "dbm.dumb"
        f = io.open(filename + ".dir", "rb")
        jaribu:
            if f.read(1) in (b"'", b'"'):
                return "dbm.dumb"
        mwishowe:
            f.close()
    tatizo OSError:
        pass

    # See if the file exists, return None if not
    jaribu:
        f = io.open(filename, "rb")
    tatizo OSError:
        return None

    with f:
        # Read the start of the file -- the magic number
        s16 = f.read(16)
    s = s16[0:4]

    # Return "" if sio at least 4 bytes
    if len(s) != 4:
        return ""

    # Convert to 4-byte int in native byte order -- return "" if impossible
    jaribu:
        (magic,) = struct.unpack("=l", s)
    tatizo struct.error:
        return ""

    # Check for GNU dbm
    if magic in (0x13579ace, 0x13579acd, 0x13579acf):
        return "dbm.gnu"

    # Later versions of Berkeley db hash file have a 12-byte pad in
    # front of the file type
    jaribu:
        (magic,) = struct.unpack("=l", s16[-4:])
    tatizo struct.error:
        return ""

    # Unknown
    return ""


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        print(whichdb(filename) ama "UNKNOWN", filename)
