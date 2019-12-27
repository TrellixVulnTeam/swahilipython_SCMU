agiza test.support

# Skip test ikiwa _sqlite3 module not installed
test.support.import_module('_sqlite3')

agiza unittest
agiza sqlite3
kutoka sqlite3.test agiza (dbapi, types, userfunctions,
                                factory, transactions, hooks, regression,
                                dump, backup)

eleza load_tests(*args):
    ikiwa test.support.verbose:
        andika("test_sqlite: testing with version",
              "{!r}, sqlite_version {!r}".format(sqlite3.version,
                                                 sqlite3.sqlite_version))
    rudisha unittest.TestSuite([dbapi.suite(), types.suite(),
                               userfunctions.suite(),
                               factory.suite(), transactions.suite(),
                               hooks.suite(), regression.suite(),
                               dump.suite(),
                               backup.suite()])

ikiwa __name__ == "__main__":
    unittest.main()
