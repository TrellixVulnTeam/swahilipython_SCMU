"""Generic interface to all dbm clones.

Use

        agiza dbm
        d = dbm.open(file, 'w', 0o666)

The returned object ni a dbm.gnu, dbm.ndbm ama dbm.dumb object, dependent on the
type of database being opened (determined by the whichdb function) kwenye the case
of an existing dbm. If the dbm does sio exist na the create ama new flag ('c'
or 'n') was specified, the dbm type will be determined by the availability of
the modules (tested kwenye the above order).

It has the following interface (key na data are strings):

        d[key] = data   # store data at key (may override data at
                        # existing key)
        data = d[key]   # retrieve data at key (ashiria KeyError ikiwa no
                        # such key)
        toa d[key]      # delete data stored at key (raises KeyError
                        # ikiwa no such key)
        flag = key kwenye d # true ikiwa the key exists
        list = d.keys() # rudisha a list of all existing keys (slow!)

Future versions may change the order kwenye which implementations are
tested kila existence, na add interfaces to other dbm-like
implementations.
"""

__all__ = ['open', 'whichdb', 'error']

agiza io
agiza os
agiza struct
agiza sys


kundi error(Exception):
    pita

_names = ['dbm.gnu', 'dbm.ndbm', 'dbm.dumb']
_defaultmod = Tupu
_modules = {}

error = (error, OSError)

jaribu:
    kutoka dbm agiza ndbm
tatizo ImportError:
    ndbm = Tupu


eleza open(file, flag='r', mode=0o666):
    """Open ama create database at path given by *file*.

    Optional argument *flag* can be 'r' (default) kila read-only access, 'w'
    kila read-write access of an existing database, 'c' kila read-write access
    to a new ama existing database, na 'n' kila read-write access to a new
    database.

    Note: 'r' na 'w' fail ikiwa the database doesn't exist; 'c' creates it
    only ikiwa it doesn't exist; na 'n' always creates a new database.
    """
    global _defaultmod
    ikiwa _defaultmod ni Tupu:
        kila name kwenye _names:
            jaribu:
                mod = __import__(name, fromlist=['open'])
            tatizo ImportError:
                endelea
            ikiwa sio _defaultmod:
                _defaultmod = mod
            _modules[name] = mod
        ikiwa sio _defaultmod:
            ashiria ImportError("no dbm clone found; tried %s" % _names)

    # guess the type of an existing database, ikiwa sio creating a new one
    result = whichdb(file) ikiwa 'n' haiko kwenye flag isipokua Tupu
    ikiwa result ni Tupu:
        # db doesn't exist ama 'n' flag was specified to create a new db
        ikiwa 'c' kwenye flag ama 'n' kwenye flag:
            # file doesn't exist na the new flag was used so use default type
            mod = _defaultmod
        isipokua:
            ashiria error[0]("db file doesn't exist; "
                           "use 'c' ama 'n' flag to create a new db")
    lasivyo result == "":
        # db type cansio be determined
        ashiria error[0]("db type could sio be determined")
    lasivyo result haiko kwenye _modules:
        ashiria error[0]("db type ni {0}, but the module ni sio "
                       "available".format(result))
    isipokua:
        mod = _modules[result]
    rudisha mod.open(file, flag, mode)


eleza whichdb(filename):
    """Guess which db package to use to open a db file.

    Return values:

    - Tupu ikiwa the database file can't be read;
    - empty string ikiwa the file can be read but can't be recognized
    - the name of the dbm submodule (e.g. "ndbm" ama "gnu") ikiwa recognized.

    Importing the given module may still fail, na opening the
    database using that module may still fail.
    """

    # Check kila ndbm first -- this has a .pag na a .dir file
    jaribu:
        f = io.open(filename + ".pag", "rb")
        f.close()
        f = io.open(filename + ".dir", "rb")
        f.close()
        rudisha "dbm.ndbm"
    tatizo OSError:
        # some dbm emulations based on Berkeley DB generate a .db file
        # some do not, but they should be caught by the bsd checks
        jaribu:
            f = io.open(filename + ".db", "rb")
            f.close()
            # guarantee we can actually open the file using dbm
            # kind of overkill, but since we are dealing ukijumuisha emulations
            # it seems like a prudent step
            ikiwa ndbm ni sio Tupu:
                d = ndbm.open(filename)
                d.close()
                rudisha "dbm.ndbm"
        tatizo OSError:
            pita

    # Check kila dumbdbm next -- this has a .dir na a .dat file
    jaribu:
        # First check kila presence of files
        os.stat(filename + ".dat")
        size = os.stat(filename + ".dir").st_size
        # dumbdbm files ukijumuisha no keys are empty
        ikiwa size == 0:
            rudisha "dbm.dumb"
        f = io.open(filename + ".dir", "rb")
        jaribu:
            ikiwa f.read(1) kwenye (b"'", b'"'):
                rudisha "dbm.dumb"
        mwishowe:
            f.close()
    tatizo OSError:
        pita

    # See ikiwa the file exists, rudisha Tupu ikiwa sio
    jaribu:
        f = io.open(filename, "rb")
    tatizo OSError:
        rudisha Tupu

    ukijumuisha f:
        # Read the start of the file -- the magic number
        s16 = f.read(16)
    s = s16[0:4]

    # Return "" ikiwa sio at least 4 bytes
    ikiwa len(s) != 4:
        rudisha ""

    # Convert to 4-byte int kwenye native byte order -- rudisha "" ikiwa impossible
    jaribu:
        (magic,) = struct.unpack("=l", s)
    tatizo struct.error:
        rudisha ""

    # Check kila GNU dbm
    ikiwa magic kwenye (0x13579ace, 0x13579acd, 0x13579acf):
        rudisha "dbm.gnu"

    # Later versions of Berkeley db hash file have a 12-byte pad kwenye
    # front of the file type
    jaribu:
        (magic,) = struct.unpack("=l", s16[-4:])
    tatizo struct.error:
        rudisha ""

    # Unknown
    rudisha ""


ikiwa __name__ == "__main__":
    kila filename kwenye sys.argv[1:]:
        andika(whichdb(filename) ama "UNKNOWN", filename)
