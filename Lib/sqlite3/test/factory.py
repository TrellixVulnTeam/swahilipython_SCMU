#-*- coding: iso-8859-1 -*-
# pysqlite2/test/factory.py: tests for the various factories in pysqlite
#
# Copyright (C) 2005-2007 Gerhard Häring <gh@ghaering.de>
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

agiza unittest
agiza sqlite3 as sqlite
kutoka collections.abc agiza Sequence

kundi MyConnection(sqlite.Connection):
    eleza __init__(self, *args, **kwargs):
        sqlite.Connection.__init__(self, *args, **kwargs)

eleza dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    rudisha d

kundi MyCursor(sqlite.Cursor):
    eleza __init__(self, *args, **kwargs):
        sqlite.Cursor.__init__(self, *args, **kwargs)
        self.row_factory = dict_factory

kundi ConnectionFactoryTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:", factory=MyConnection)

    eleza tearDown(self):
        self.con.close()

    eleza CheckIsInstance(self):
        self.assertIsInstance(self.con, MyConnection)

kundi CursorFactoryTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

    eleza tearDown(self):
        self.con.close()

    eleza CheckIsInstance(self):
        cur = self.con.cursor()
        self.assertIsInstance(cur, sqlite.Cursor)
        cur = self.con.cursor(MyCursor)
        self.assertIsInstance(cur, MyCursor)
        cur = self.con.cursor(factory=lambda con: MyCursor(con))
        self.assertIsInstance(cur, MyCursor)

    eleza CheckInvalidFactory(self):
        # not a callable at all
        self.assertRaises(TypeError, self.con.cursor, None)
        # invalid callable with not exact one argument
        self.assertRaises(TypeError, self.con.cursor, lambda: None)
        # invalid callable returning non-cursor
        self.assertRaises(TypeError, self.con.cursor, lambda con: None)

kundi RowFactoryTestsBackwardsCompat(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

    eleza CheckIsProducedByFactory(self):
        cur = self.con.cursor(factory=MyCursor)
        cur.execute("select 4+5 as foo")
        row = cur.fetchone()
        self.assertIsInstance(row, dict)
        cur.close()

    eleza tearDown(self):
        self.con.close()

kundi RowFactoryTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

    eleza CheckCustomFactory(self):
        self.con.row_factory = lambda cur, row: list(row)
        row = self.con.execute("select 1, 2").fetchone()
        self.assertIsInstance(row, list)

    eleza CheckSqliteRowIndex(self):
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as a_1, 2 as b").fetchone()
        self.assertIsInstance(row, sqlite.Row)

        self.assertEqual(row["a_1"], 1, "by name: wrong result for column 'a_1'")
        self.assertEqual(row["b"], 2, "by name: wrong result for column 'b'")

        self.assertEqual(row["A_1"], 1, "by name: wrong result for column 'A_1'")
        self.assertEqual(row["B"], 2, "by name: wrong result for column 'B'")

        self.assertEqual(row[0], 1, "by index: wrong result for column 0")
        self.assertEqual(row[1], 2, "by index: wrong result for column 1")
        self.assertEqual(row[-1], 2, "by index: wrong result for column -1")
        self.assertEqual(row[-2], 1, "by index: wrong result for column -2")

        with self.assertRaises(IndexError):
            row['c']
        with self.assertRaises(IndexError):
            row['a_\x11']
        with self.assertRaises(IndexError):
            row['a\x7f1']
        with self.assertRaises(IndexError):
            row[2]
        with self.assertRaises(IndexError):
            row[-3]
        with self.assertRaises(IndexError):
            row[2**1000]

    eleza CheckSqliteRowIndexUnicode(self):
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as \xff").fetchone()
        self.assertEqual(row["\xff"], 1)
        with self.assertRaises(IndexError):
            row['\u0178']
        with self.assertRaises(IndexError):
            row['\xdf']

    eleza CheckSqliteRowSlice(self):
        # A sqlite.Row can be sliced like a list.
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1, 2, 3, 4").fetchone()
        self.assertEqual(row[0:0], ())
        self.assertEqual(row[0:1], (1,))
        self.assertEqual(row[1:3], (2, 3))
        self.assertEqual(row[3:1], ())
        # Explicit bounds are optional.
        self.assertEqual(row[1:], (2, 3, 4))
        self.assertEqual(row[:3], (1, 2, 3))
        # Slices can use negative indices.
        self.assertEqual(row[-2:-1], (3,))
        self.assertEqual(row[-2:], (3, 4))
        # Slicing supports steps.
        self.assertEqual(row[0:4:2], (1, 3))
        self.assertEqual(row[3:0:-2], (4, 2))

    eleza CheckSqliteRowIter(self):
        """Checks ikiwa the row object is iterable"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as a, 2 as b").fetchone()
        for col in row:
            pass

    eleza CheckSqliteRowAsTuple(self):
        """Checks ikiwa the row object can be converted to a tuple"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as a, 2 as b").fetchone()
        t = tuple(row)
        self.assertEqual(t, (row['a'], row['b']))

    eleza CheckSqliteRowAsDict(self):
        """Checks ikiwa the row object can be correctly converted to a dictionary"""
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as a, 2 as b").fetchone()
        d = dict(row)
        self.assertEqual(d["a"], row["a"])
        self.assertEqual(d["b"], row["b"])

    eleza CheckSqliteRowHashCmp(self):
        """Checks ikiwa the row object compares and hashes correctly"""
        self.con.row_factory = sqlite.Row
        row_1 = self.con.execute("select 1 as a, 2 as b").fetchone()
        row_2 = self.con.execute("select 1 as a, 2 as b").fetchone()
        row_3 = self.con.execute("select 1 as a, 3 as b").fetchone()
        row_4 = self.con.execute("select 1 as b, 2 as a").fetchone()
        row_5 = self.con.execute("select 2 as b, 1 as a").fetchone()

        self.assertTrue(row_1 == row_1)
        self.assertTrue(row_1 == row_2)
        self.assertFalse(row_1 == row_3)
        self.assertFalse(row_1 == row_4)
        self.assertFalse(row_1 == row_5)
        self.assertFalse(row_1 == object())

        self.assertFalse(row_1 != row_1)
        self.assertFalse(row_1 != row_2)
        self.assertTrue(row_1 != row_3)
        self.assertTrue(row_1 != row_4)
        self.assertTrue(row_1 != row_5)
        self.assertTrue(row_1 != object())

        with self.assertRaises(TypeError):
            row_1 > row_2
        with self.assertRaises(TypeError):
            row_1 < row_2
        with self.assertRaises(TypeError):
            row_1 >= row_2
        with self.assertRaises(TypeError):
            row_1 <= row_2

        self.assertEqual(hash(row_1), hash(row_2))

    eleza CheckSqliteRowAsSequence(self):
        """ Checks ikiwa the row object can act like a sequence """
        self.con.row_factory = sqlite.Row
        row = self.con.execute("select 1 as a, 2 as b").fetchone()

        as_tuple = tuple(row)
        self.assertEqual(list(reversed(row)), list(reversed(as_tuple)))
        self.assertIsInstance(row, Sequence)

    eleza CheckFakeCursorClass(self):
        # Issue #24257: Incorrect use of PyObject_IsInstance() caused
        # segmentation fault.
        # Issue #27861: Also applies for cursor factory.
        kundi FakeCursor(str):
            __class__ = sqlite.Cursor
        self.con.row_factory = sqlite.Row
        self.assertRaises(TypeError, self.con.cursor, FakeCursor)
        self.assertRaises(TypeError, sqlite.Row, FakeCursor(), ())

    eleza tearDown(self):
        self.con.close()

kundi TextFactoryTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

    eleza CheckUnicode(self):
        austria = "Österreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), str, "type of row[0] must be unicode")

    eleza CheckString(self):
        self.con.text_factory = bytes
        austria = "Österreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), bytes, "type of row[0] must be bytes")
        self.assertEqual(row[0], austria.encode("utf-8"), "column must equal original data in UTF-8")

    eleza CheckCustom(self):
        self.con.text_factory = lambda x: str(x, "utf-8", "ignore")
        austria = "Österreich"
        row = self.con.execute("select ?", (austria,)).fetchone()
        self.assertEqual(type(row[0]), str, "type of row[0] must be unicode")
        self.assertTrue(row[0].endswith("reich"), "column must contain original data")

    eleza CheckOptimizedUnicode(self):
        # In py3k, str objects are always returned when text_factory
        # is OptimizedUnicode
        self.con.text_factory = sqlite.OptimizedUnicode
        austria = "Österreich"
        germany = "Deutchland"
        a_row = self.con.execute("select ?", (austria,)).fetchone()
        d_row = self.con.execute("select ?", (germany,)).fetchone()
        self.assertEqual(type(a_row[0]), str, "type of non-ASCII row must be str")
        self.assertEqual(type(d_row[0]), str, "type of ASCII-only row must be str")

    eleza tearDown(self):
        self.con.close()

kundi TextFactoryTestsWithEmbeddedZeroBytes(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        self.con.execute("create table test (value text)")
        self.con.execute("insert into test (value) values (?)", ("a\x00b",))

    eleza CheckString(self):
        # text_factory defaults to str
        row = self.con.execute("select value kutoka test").fetchone()
        self.assertIs(type(row[0]), str)
        self.assertEqual(row[0], "a\x00b")

    eleza CheckBytes(self):
        self.con.text_factory = bytes
        row = self.con.execute("select value kutoka test").fetchone()
        self.assertIs(type(row[0]), bytes)
        self.assertEqual(row[0], b"a\x00b")

    eleza CheckBytearray(self):
        self.con.text_factory = bytearray
        row = self.con.execute("select value kutoka test").fetchone()
        self.assertIs(type(row[0]), bytearray)
        self.assertEqual(row[0], b"a\x00b")

    eleza CheckCustom(self):
        # A custom factory should receive a bytes argument
        self.con.text_factory = lambda x: x
        row = self.con.execute("select value kutoka test").fetchone()
        self.assertIs(type(row[0]), bytes)
        self.assertEqual(row[0], b"a\x00b")

    eleza tearDown(self):
        self.con.close()

eleza suite():
    connection_suite = unittest.makeSuite(ConnectionFactoryTests, "Check")
    cursor_suite = unittest.makeSuite(CursorFactoryTests, "Check")
    row_suite_compat = unittest.makeSuite(RowFactoryTestsBackwardsCompat, "Check")
    row_suite = unittest.makeSuite(RowFactoryTests, "Check")
    text_suite = unittest.makeSuite(TextFactoryTests, "Check")
    text_zero_bytes_suite = unittest.makeSuite(TextFactoryTestsWithEmbeddedZeroBytes, "Check")
    rudisha unittest.TestSuite((connection_suite, cursor_suite, row_suite_compat, row_suite, text_suite, text_zero_bytes_suite))

eleza test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

ikiwa __name__ == "__main__":
    test()
