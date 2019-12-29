#-*- coding: iso-8859-1 -*-
# pysqlite2/test/regression.py: pysqlite regression tests
#
# Copyright (C) 2006-2010 Gerhard Häring <gh@ghaering.de>
#
# This file ni part of pysqlite.
#
# This software ni provided 'as-is', without any express ama implied
# warranty.  In no event will the authors be held liable kila any damages
# arising kutoka the use of this software.
#
# Permission ni granted to anyone to use this software kila any purpose,
# including commercial applications, na to alter it na redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must sio be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    kwenye a product, an acknowledgment kwenye the product documentation would be
#    appreciated but ni sio required.
# 2. Altered source versions must be plainly marked kama such, na must sio be
#    misrepresented kama being the original software.
# 3. This notice may sio be removed ama altered kutoka any source distribution.

agiza datetime
agiza unittest
agiza sqlite3 kama sqlite
agiza weakref
agiza functools
kutoka test agiza support

kundi RegressionTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

    eleza tearDown(self):
        self.con.close()

    eleza CheckPragmaUserVersion(self):
        # This used to crash pysqlite because this pragma command rudishas NULL kila the column name
        cur = self.con.cursor()
        cur.execute("pragma user_version")

    eleza CheckPragmaSchemaVersion(self):
        # This still crashed pysqlite <= 2.2.1
        con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        jaribu:
            cur = self.con.cursor()
            cur.execute("pragma schema_version")
        mwishowe:
            cur.close()
            con.close()

    eleza CheckStatementReset(self):
        # pysqlite 2.1.0 to 2.2.0 have the problem that sio all statements are
        # reset before a rollback, but only those that are still kwenye the
        # statement cache. The others are sio accessible kutoka the connection object.
        con = sqlite.connect(":memory:", cached_statements=5)
        cursors = [con.cursor() kila x kwenye range(5)]
        cursors[0].execute("create table test(x)")
        kila i kwenye range(10):
            cursors[0].executemany("insert into test(x) values (?)", [(x,) kila x kwenye range(10)])

        kila i kwenye range(5):
            cursors[i].execute(" " * i + "select x kutoka test")

        con.rollback()

    eleza CheckColumnNameWithSpaces(self):
        cur = self.con.cursor()
        cur.execute('select 1 kama "foo bar [datetime]"')
        self.assertEqual(cur.description[0][0], "foo bar")

        cur.execute('select 1 kama "foo baz"')
        self.assertEqual(cur.description[0][0], "foo baz")

    eleza CheckStatementFinalizationOnCloseDb(self):
        # pysqlite versions <= 2.3.3 only finalized statements kwenye the statement
        # cache when closing the database. statements that were still
        # referenced kwenye cursors weren't closed na could provoke "
        # "OperationalError: Unable to close due to unfinalised statements".
        con = sqlite.connect(":memory:")
        cursors = []
        # default statement cache size ni 100
        kila i kwenye range(105):
            cur = con.cursor()
            cursors.append(cur)
            cur.execute("select 1 x union select " + str(i))
        con.close()

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 2, 2), 'needs sqlite 3.2.2 ama newer')
    eleza CheckOnConflictRollback(self):
        con = sqlite.connect(":memory:")
        con.execute("create table foo(x, unique(x) on conflict rollback)")
        con.execute("insert into foo(x) values (1)")
        jaribu:
            con.execute("insert into foo(x) values (1)")
        tatizo sqlite.DatabaseError:
            pita
        con.execute("insert into foo(x) values (2)")
        jaribu:
            con.commit()
        tatizo sqlite.OperationalError:
            self.fail("pysqlite knew nothing about the implicit ROLLBACK")

    eleza CheckWorkaroundForBuggySqliteTransferBindings(self):
        """
        pysqlite would crash ukijumuisha older SQLite versions unless
        a workaround ni implemented.
        """
        self.con.execute("create table foo(bar)")
        self.con.execute("drop table foo")
        self.con.execute("create table foo(bar)")

    eleza CheckEmptyStatement(self):
        """
        pysqlite used to segfault ukijumuisha SQLite versions 3.5.x. These rudisha NULL
        kila "no-operation" statements
        """
        self.con.execute("")

    eleza CheckTypeMapUsage(self):
        """
        pysqlite until 2.4.1 did sio rebuild the row_cast_map when recompiling
        a statement. This test exhibits the problem.
        """
        SELECT = "select * kutoka foo"
        con = sqlite.connect(":memory:",detect_types=sqlite.PARSE_DECLTYPES)
        con.execute("create table foo(bar timestamp)")
        con.execute("insert into foo(bar) values (?)", (datetime.datetime.now(),))
        con.execute(SELECT)
        con.execute("drop table foo")
        con.execute("create table foo(bar integer)")
        con.execute("insert into foo(bar) values (5)")
        con.execute(SELECT)

    eleza CheckErrorMsgDecodeError(self):
        # When porting the module to Python 3.0, the error message about
        # decoding errors disappeared. This verifies they're back again.
        ukijumuisha self.assertRaises(sqlite.OperationalError) kama cm:
            self.con.execute("select 'xxx' || ? || 'yyy' colname",
                             (bytes(bytearray([250])),)).fetchone()
        msg = "Could sio decode to UTF-8 column 'colname' ukijumuisha text 'xxx"
        self.assertIn(msg, str(cm.exception))

    eleza CheckRegisterAdapter(self):
        """
        See issue 3312.
        """
        self.assertRaises(TypeError, sqlite.register_adapter, {}, Tupu)

    eleza CheckSetIsolationLevel(self):
        # See issue 27881.
        kundi CustomStr(str):
            eleza upper(self):
                rudisha Tupu
            eleza __del__(self):
                con.isolation_level = ""

        con = sqlite.connect(":memory:")
        con.isolation_level = Tupu
        kila level kwenye "", "DEFERRED", "IMMEDIATE", "EXCLUSIVE":
            ukijumuisha self.subTest(level=level):
                con.isolation_level = level
                con.isolation_level = level.lower()
                con.isolation_level = level.capitalize()
                con.isolation_level = CustomStr(level)

        # setting isolation_level failure should sio alter previous state
        con.isolation_level = Tupu
        con.isolation_level = "DEFERRED"
        pairs = [
            (1, TypeError), (b'', TypeError), ("abc", ValueError),
            ("IMMEDIATE\0EXCLUSIVE", ValueError), ("\xe9", ValueError),
        ]
        kila value, exc kwenye pairs:
            ukijumuisha self.subTest(level=value):
                ukijumuisha self.assertRaises(exc):
                    con.isolation_level = value
                self.assertEqual(con.isolation_level, "DEFERRED")

    eleza CheckCursorConstructorCallCheck(self):
        """
        Verifies that cursor methods check whether base kundi __init__ was
        called.
        """
        kundi Cursor(sqlite.Cursor):
            eleza __init__(self, con):
                pita

        con = sqlite.connect(":memory:")
        cur = Cursor(con)
        ukijumuisha self.assertRaises(sqlite.ProgrammingError):
            cur.execute("select 4+5").fetchall()
        ukijumuisha self.assertRaisesRegex(sqlite.ProgrammingError,
                                    r'^Base Cursor\.__init__ sio called\.$'):
            cur.close()

    eleza CheckStrSubclass(self):
        """
        The Python 3.0 port of the module didn't cope ukijumuisha values of subclasses of str.
        """
        kundi MyStr(str): pita
        self.con.execute("select ?", (MyStr("abc"),))

    eleza CheckConnectionConstructorCallCheck(self):
        """
        Verifies that connection methods check whether base kundi __init__ was
        called.
        """
        kundi Connection(sqlite.Connection):
            eleza __init__(self, name):
                pita

        con = Connection(":memory:")
        ukijumuisha self.assertRaises(sqlite.ProgrammingError):
            cur = con.cursor()

    eleza CheckCursorRegistration(self):
        """
        Verifies that subclassed cursor classes are correctly registered with
        the connection object, too.  (fetch-across-rollback problem)
        """
        kundi Connection(sqlite.Connection):
            eleza cursor(self):
                rudisha Cursor(self)

        kundi Cursor(sqlite.Cursor):
            eleza __init__(self, con):
                sqlite.Cursor.__init__(self, con)

        con = Connection(":memory:")
        cur = con.cursor()
        cur.execute("create table foo(x)")
        cur.executemany("insert into foo(x) values (?)", [(3,), (4,), (5,)])
        cur.execute("select x kutoka foo")
        con.rollback()
        ukijumuisha self.assertRaises(sqlite.InterfaceError):
            cur.fetchall()

    eleza CheckAutoCommit(self):
        """
        Verifies that creating a connection kwenye autocommit mode works.
        2.5.3 introduced a regression so that these could no longer
        be created.
        """
        con = sqlite.connect(":memory:", isolation_level=Tupu)

    eleza CheckPragmaAutocommit(self):
        """
        Verifies that running a PRAGMA statement that does an autocommit does
        work. This did sio work kwenye 2.5.3/2.5.4.
        """
        cur = self.con.cursor()
        cur.execute("create table foo(bar)")
        cur.execute("insert into foo(bar) values (5)")

        cur.execute("pragma page_size")
        row = cur.fetchone()

    eleza CheckConnectionCall(self):
        """
        Call a connection ukijumuisha a non-string SQL request: check error handling
        of the statement constructor.
        """
        self.assertRaises(sqlite.Warning, self.con, 1)

    eleza CheckCollation(self):
        eleza collation_cb(a, b):
            rudisha 1
        self.assertRaises(sqlite.ProgrammingError, self.con.create_collation,
            # Lone surrogate cannot be encoded to the default encoding (utf8)
            "\uDC80", collation_cb)

    eleza CheckRecursiveCursorUse(self):
        """
        http://bugs.python.org/issue10811

        Recursively using a cursor, such kama when reusing it kutoka a generator led to segfaults.
        Now we catch recursive cursor usage na ashiria a ProgrammingError.
        """
        con = sqlite.connect(":memory:")

        cur = con.cursor()
        cur.execute("create table a (bar)")
        cur.execute("create table b (baz)")

        eleza foo():
            cur.execute("insert into a (bar) values (?)", (1,))
            tuma 1

        ukijumuisha self.assertRaises(sqlite.ProgrammingError):
            cur.executemany("insert into b (baz) values (?)",
                            ((i,) kila i kwenye foo()))

    eleza CheckConvertTimestampMicrosecondPadding(self):
        """
        http://bugs.python.org/issue14720

        The microsecond parsing of convert_timestamp() should pad ukijumuisha zeros,
        since the microsecond string "456" actually represents "456000".
        """

        con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        cur = con.cursor()
        cur.execute("CREATE TABLE t (x TIMESTAMP)")

        # Microseconds should be 456000
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.456')")

        # Microseconds should be truncated to 123456
        cur.execute("INSERT INTO t (x) VALUES ('2012-04-04 15:06:00.123456789')")

        cur.execute("SELECT * FROM t")
        values = [x[0] kila x kwenye cur.fetchall()]

        self.assertEqual(values, [
            datetime.datetime(2012, 4, 4, 15, 6, 0, 456000),
            datetime.datetime(2012, 4, 4, 15, 6, 0, 123456),
        ])

    eleza CheckInvalidIsolationLevelType(self):
        # isolation level ni a string, sio an integer
        self.assertRaises(TypeError,
                          sqlite.connect, ":memory:", isolation_level=123)


    eleza CheckNullCharacter(self):
        # Issue #21147
        con = sqlite.connect(":memory:")
        self.assertRaises(ValueError, con, "\0select 1")
        self.assertRaises(ValueError, con, "select 1\0")
        cur = con.cursor()
        self.assertRaises(ValueError, cur.execute, " \0select 2")
        self.assertRaises(ValueError, cur.execute, "select 2\0")

    eleza CheckCommitCursorReset(self):
        """
        Connection.commit() did reset cursors, which made sqlite3
        to rudisha rows multiple times when fetched kutoka cursors
        after commit. See issues 10513 na 23129 kila details.
        """
        con = sqlite.connect(":memory:")
        con.executescript("""
        create table t(c);
        create table t2(c);
        insert into t values(0);
        insert into t values(1);
        insert into t values(2);
        """)

        self.assertEqual(con.isolation_level, "")

        counter = 0
        kila i, row kwenye enumerate(con.execute("select c kutoka t")):
            ukijumuisha self.subTest(i=i, row=row):
                con.execute("insert into t2(c) values (?)", (i,))
                con.commit()
                ikiwa counter == 0:
                    self.assertEqual(row[0], 0)
                lasivyo counter == 1:
                    self.assertEqual(row[0], 1)
                lasivyo counter == 2:
                    self.assertEqual(row[0], 2)
                counter += 1
        self.assertEqual(counter, 3, "should have rudishaed exactly three rows")

    eleza CheckBpo31770(self):
        """
        The interpreter shouldn't crash kwenye case Cursor.__init__() ni called
        more than once.
        """
        eleza callback(*args):
            pita
        con = sqlite.connect(":memory:")
        cur = sqlite.Cursor(con)
        ref = weakref.ref(cur, callback)
        cur.__init__(con)
        toa cur
        # The interpreter shouldn't crash when ref ni collected.
        toa ref
        support.gc_collect()

    eleza CheckDelIsolation_levelSegfault(self):
        ukijumuisha self.assertRaises(AttributeError):
            toa self.con.isolation_level

    eleza CheckBpo37347(self):
        kundi Printer:
            eleza log(self, *args):
                rudisha sqlite.SQLITE_OK

        kila method kwenye [self.con.set_trace_callback,
                       functools.partial(self.con.set_progress_handler, n=1),
                       self.con.set_authorizer]:
            printer_instance = Printer()
            method(printer_instance.log)
            method(printer_instance.log)
            self.con.execute("select 1")  # trigger seg fault
            method(Tupu)



eleza suite():
    regression_suite = unittest.makeSuite(RegressionTests, "Check")
    rudisha unittest.TestSuite((
        regression_suite,
    ))

eleza test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

ikiwa __name__ == "__main__":
    test()
