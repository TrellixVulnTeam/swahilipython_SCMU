#-*- coding: iso-8859-1 -*-
# pysqlite2/test/types.py: tests for type conversion and detection
#
# Copyright (C) 2005 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising kutoka the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered kutoka any source distribution.

agiza datetime
agiza unittest
agiza sqlite3 as sqlite
try:
    agiza zlib
except ImportError:
    zlib = None


kundi SqliteTypeTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(i integer, s varchar, f number, b blob)")

    eleza tearDown(self):
        self.cur.close()
        self.con.close()

    eleza CheckString(self):
        self.cur.execute("insert into test(s) values (?)", ("Österreich",))
        self.cur.execute("select s kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "Österreich")

    eleza CheckSmallInt(self):
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    eleza CheckLargeInt(self):
        num = 2**40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    eleza CheckFloat(self):
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    eleza CheckBlob(self):
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(b) values (?)", (val,))
        self.cur.execute("select b kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    eleza CheckUnicodeExecute(self):
        self.cur.execute("select 'Österreich'")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "Österreich")

kundi DeclTypesTests(unittest.TestCase):
    kundi Foo:
        eleza __init__(self, _val):
            ikiwa isinstance(_val, bytes):
                # sqlite3 always calls __init__ with a bytes created kutoka a
                # UTF-8 string when __conform__ was used to store the object.
                _val = _val.decode('utf-8')
            self.val = _val

        eleza __eq__(self, other):
            ikiwa not isinstance(other, DeclTypesTests.Foo):
                rudisha NotImplemented
            rudisha self.val == other.val

        eleza __conform__(self, protocol):
            ikiwa protocol is sqlite.PrepareProtocol:
                rudisha self.val
            else:
                rudisha None

        eleza __str__(self):
            rudisha "<%s>" % self.val

    kundi BadConform:
        eleza __init__(self, exc):
            self.exc = exc
        eleza __conform__(self, protocol):
            raise self.exc

    eleza setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(i int, s str, f float, b bool, u unicode, foo foo, bin blob, n1 number, n2 number(5), bad bad)")

        # override float, make them always rudisha the same number
        sqlite.converters["FLOAT"] = lambda x: 47.2

        # and implement two custom ones
        sqlite.converters["BOOL"] = lambda x: bool(int(x))
        sqlite.converters["FOO"] = DeclTypesTests.Foo
        sqlite.converters["BAD"] = DeclTypesTests.BadConform
        sqlite.converters["WRONG"] = lambda x: "WRONG"
        sqlite.converters["NUMBER"] = float

    eleza tearDown(self):
        del sqlite.converters["FLOAT"]
        del sqlite.converters["BOOL"]
        del sqlite.converters["FOO"]
        del sqlite.converters["BAD"]
        del sqlite.converters["WRONG"]
        del sqlite.converters["NUMBER"]
        self.cur.close()
        self.con.close()

    eleza CheckString(self):
        # default
        self.cur.execute("insert into test(s) values (?)", ("foo",))
        self.cur.execute('select s as "s [WRONG]" kutoka test')
        row = self.cur.fetchone()
        self.assertEqual(row[0], "foo")

    eleza CheckSmallInt(self):
        # default
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    eleza CheckLargeInt(self):
        # default
        num = 2**40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    eleza CheckFloat(self):
        # custom
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 47.2)

    eleza CheckBool(self):
        # custom
        self.cur.execute("insert into test(b) values (?)", (False,))
        self.cur.execute("select b kutoka test")
        row = self.cur.fetchone()
        self.assertIs(row[0], False)

        self.cur.execute("delete kutoka test")
        self.cur.execute("insert into test(b) values (?)", (True,))
        self.cur.execute("select b kutoka test")
        row = self.cur.fetchone()
        self.assertIs(row[0], True)

    eleza CheckUnicode(self):
        # default
        val = "\xd6sterreich"
        self.cur.execute("insert into test(u) values (?)", (val,))
        self.cur.execute("select u kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    eleza CheckFoo(self):
        val = DeclTypesTests.Foo("bla")
        self.cur.execute("insert into test(foo) values (?)", (val,))
        self.cur.execute("select foo kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    eleza CheckErrorInConform(self):
        val = DeclTypesTests.BadConform(TypeError)
        with self.assertRaises(sqlite.InterfaceError):
            self.cur.execute("insert into test(bad) values (?)", (val,))
        with self.assertRaises(sqlite.InterfaceError):
            self.cur.execute("insert into test(bad) values (:val)", {"val": val})

        val = DeclTypesTests.BadConform(KeyboardInterrupt)
        with self.assertRaises(KeyboardInterrupt):
            self.cur.execute("insert into test(bad) values (?)", (val,))
        with self.assertRaises(KeyboardInterrupt):
            self.cur.execute("insert into test(bad) values (:val)", {"val": val})

    eleza CheckUnsupportedSeq(self):
        kundi Bar: pass
        val = Bar()
        with self.assertRaises(sqlite.InterfaceError):
            self.cur.execute("insert into test(f) values (?)", (val,))

    eleza CheckUnsupportedDict(self):
        kundi Bar: pass
        val = Bar()
        with self.assertRaises(sqlite.InterfaceError):
            self.cur.execute("insert into test(f) values (:val)", {"val": val})

    eleza CheckBlob(self):
        # default
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(bin) values (?)", (val,))
        self.cur.execute("select bin kutoka test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    eleza CheckNumber1(self):
        self.cur.execute("insert into test(n1) values (5)")
        value = self.cur.execute("select n1 kutoka test").fetchone()[0]
        # ikiwa the converter is not used, it's an int instead of a float
        self.assertEqual(type(value), float)

    eleza CheckNumber2(self):
        """Checks whether converter names are cut off at '(' characters"""
        self.cur.execute("insert into test(n2) values (5)")
        value = self.cur.execute("select n2 kutoka test").fetchone()[0]
        # ikiwa the converter is not used, it's an int instead of a float
        self.assertEqual(type(value), float)

kundi ColNamesTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(x foo)")

        sqlite.converters["FOO"] = lambda x: "[%s]" % x.decode("ascii")
        sqlite.converters["BAR"] = lambda x: "<%s>" % x.decode("ascii")
        sqlite.converters["EXC"] = lambda x: 5/0
        sqlite.converters["B1B1"] = lambda x: "MARKER"

    eleza tearDown(self):
        del sqlite.converters["FOO"]
        del sqlite.converters["BAR"]
        del sqlite.converters["EXC"]
        del sqlite.converters["B1B1"]
        self.cur.close()
        self.con.close()

    eleza CheckDeclTypeNotUsed(self):
        """
        Assures that the declared type is not used when PARSE_DECLTYPES
        is not set.
        """
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute("select x kutoka test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "xxx")

    eleza CheckNone(self):
        self.cur.execute("insert into test(x) values (?)", (None,))
        self.cur.execute("select x kutoka test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, None)

    eleza CheckColName(self):
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute('select x as "x [bar]" kutoka test')
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "<xxx>")

        # Check ikiwa the stripping of colnames works. Everything after the first
        # whitespace should be stripped.
        self.assertEqual(self.cur.description[0][0], "x")

    eleza CheckCaseInConverterName(self):
        self.cur.execute("select 'other' as \"x [b1b1]\"")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "MARKER")

    eleza CheckCursorDescriptionNoRow(self):
        """
        cursor.description should at least provide the column name(s), even if
        no row returned.
        """
        self.cur.execute("select * kutoka test where 0 = 1")
        self.assertEqual(self.cur.description[0][0], "x")

    eleza CheckCursorDescriptionInsert(self):
        self.cur.execute("insert into test values (1)")
        self.assertIsNone(self.cur.description)


@unittest.skipIf(sqlite.sqlite_version_info < (3, 8, 3), "CTEs not supported")
kundi CommonTableExpressionTests(unittest.TestCase):

    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(x foo)")

    eleza tearDown(self):
        self.cur.close()
        self.con.close()

    eleza CheckCursorDescriptionCTESimple(self):
        self.cur.execute("with one as (select 1) select * kutoka one")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "1")

    eleza CheckCursorDescriptionCTESMultipleColumns(self):
        self.cur.execute("insert into test values(1)")
        self.cur.execute("insert into test values(2)")
        self.cur.execute("with testCTE as (select * kutoka test) select * kutoka testCTE")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")

    eleza CheckCursorDescriptionCTE(self):
        self.cur.execute("insert into test values (1)")
        self.cur.execute("with bar as (select * kutoka test) select * kutoka test where x = 1")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")
        self.cur.execute("with bar as (select * kutoka test) select * kutoka test where x = 2")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")


kundi ObjectAdaptationTests(unittest.TestCase):
    eleza cast(obj):
        rudisha float(obj)
    cast = staticmethod(cast)

    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        try:
            del sqlite.adapters[int]
        except:
            pass
        sqlite.register_adapter(int, ObjectAdaptationTests.cast)
        self.cur = self.con.cursor()

    eleza tearDown(self):
        del sqlite.adapters[(int, sqlite.PrepareProtocol)]
        self.cur.close()
        self.con.close()

    eleza CheckCasterIsUsed(self):
        self.cur.execute("select ?", (4,))
        val = self.cur.fetchone()[0]
        self.assertEqual(type(val), float)

@unittest.skipUnless(zlib, "requires zlib")
kundi BinaryConverterTests(unittest.TestCase):
    eleza convert(s):
        rudisha zlib.decompress(s)
    convert = staticmethod(convert)

    eleza setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_COLNAMES)
        sqlite.register_converter("bin", BinaryConverterTests.convert)

    eleza tearDown(self):
        self.con.close()

    eleza CheckBinaryInputForConverter(self):
        testdata = b"abcdefg" * 10
        result = self.con.execute('select ? as "x [bin]"', (memoryview(zlib.compress(testdata)),)).fetchone()[0]
        self.assertEqual(testdata, result)

kundi DateTimeTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:", detect_types=sqlite.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(d date, ts timestamp)")

    eleza tearDown(self):
        self.cur.close()
        self.con.close()

    eleza CheckSqliteDate(self):
        d = sqlite.Date(2004, 2, 14)
        self.cur.execute("insert into test(d) values (?)", (d,))
        self.cur.execute("select d kutoka test")
        d2 = self.cur.fetchone()[0]
        self.assertEqual(d, d2)

    eleza CheckSqliteTimestamp(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts kutoka test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 1),
                     'the date functions are available on 3.1 or later')
    eleza CheckSqlTimestamp(self):
        now = datetime.datetime.utcnow()
        self.cur.execute("insert into test(ts) values (current_timestamp)")
        self.cur.execute("select ts kutoka test")
        ts = self.cur.fetchone()[0]
        self.assertEqual(type(ts), datetime.datetime)
        self.assertEqual(ts.year, now.year)

    eleza CheckDateTimeSubSeconds(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0, 500000)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts kutoka test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    eleza CheckDateTimeSubSecondsFloatingPoint(self):
        ts = sqlite.Timestamp(2004, 2, 14, 7, 15, 0, 510241)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts kutoka test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

eleza suite():
    sqlite_type_suite = unittest.makeSuite(SqliteTypeTests, "Check")
    decltypes_type_suite = unittest.makeSuite(DeclTypesTests, "Check")
    colnames_type_suite = unittest.makeSuite(ColNamesTests, "Check")
    adaptation_suite = unittest.makeSuite(ObjectAdaptationTests, "Check")
    bin_suite = unittest.makeSuite(BinaryConverterTests, "Check")
    date_suite = unittest.makeSuite(DateTimeTests, "Check")
    cte_suite = unittest.makeSuite(CommonTableExpressionTests, "Check")
    rudisha unittest.TestSuite((sqlite_type_suite, decltypes_type_suite, colnames_type_suite, adaptation_suite, bin_suite, date_suite, cte_suite))

eleza test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

ikiwa __name__ == "__main__":
    test()
