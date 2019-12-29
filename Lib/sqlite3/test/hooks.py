#-*- coding: iso-8859-1 -*-
# pysqlite2/test/hooks.py: tests kila various SQLite-specific hooks
#
# Copyright (C) 2006-2007 Gerhard Häring <gh@ghaering.de>
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

agiza unittest
agiza sqlite3 kama sqlite

kutoka test.support agiza TESTFN, unlink

kundi CollationTests(unittest.TestCase):
    eleza CheckCreateCollationNotString(self):
        con = sqlite.connect(":memory:")
        with self.assertRaises(TypeError):
            con.create_collation(Tupu, lambda x, y: (x > y) - (x < y))

    eleza CheckCreateCollationNotCallable(self):
        con = sqlite.connect(":memory:")
        with self.assertRaises(TypeError) kama cm:
            con.create_collation("X", 42)
        self.assertEqual(str(cm.exception), 'parameter must be callable')

    eleza CheckCreateCollationNotAscii(self):
        con = sqlite.connect(":memory:")
        with self.assertRaises(sqlite.ProgrammingError):
            con.create_collation("collä", lambda x, y: (x > y) - (x < y))

    eleza CheckCreateCollationBadUpper(self):
        kundi BadUpperStr(str):
            eleza upper(self):
                rudisha Tupu
        con = sqlite.connect(":memory:")
        mycoll = lambda x, y: -((x > y) - (x < y))
        con.create_collation(BadUpperStr("mycoll"), mycoll)
        result = con.execute("""
            select x kutoka (
            select 'a' kama x
            union
            select 'b' kama x
            ) order by x collate mycoll
            """).fetchall()
        self.assertEqual(result[0][0], 'b')
        self.assertEqual(result[1][0], 'a')

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 2, 1),
                     'old SQLite versions crash on this test')
    eleza CheckCollationIsUsed(self):
        eleza mycoll(x, y):
            # reverse order
            rudisha -((x > y) - (x < y))

        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", mycoll)
        sql = """
            select x kutoka (
            select 'a' kama x
            union
            select 'b' kama x
            union
            select 'c' kama x
            ) order by x collate mycoll
            """
        result = con.execute(sql).fetchall()
        self.assertEqual(result, [('c',), ('b',), ('a',)],
                         msg='the expected order was sio rudishaed')

        con.create_collation("mycoll", Tupu)
        with self.assertRaises(sqlite.OperationalError) kama cm:
            result = con.execute(sql).fetchall()
        self.assertEqual(str(cm.exception), 'no such collation sequence: mycoll')

    eleza CheckCollationReturnsLargeInteger(self):
        eleza mycoll(x, y):
            # reverse order
            rudisha -((x > y) - (x < y)) * 2**32
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", mycoll)
        sql = """
            select x kutoka (
            select 'a' kama x
            union
            select 'b' kama x
            union
            select 'c' kama x
            ) order by x collate mycoll
            """
        result = con.execute(sql).fetchall()
        self.assertEqual(result, [('c',), ('b',), ('a',)],
                         msg="the expected order was sio rudishaed")

    eleza CheckCollationRegisterTwice(self):
        """
        Register two different collation functions under the same name.
        Verify that the last one ni actually used.
        """
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", lambda x, y: (x > y) - (x < y))
        con.create_collation("mycoll", lambda x, y: -((x > y) - (x < y)))
        result = con.execute("""
            select x kutoka (select 'a' kama x union select 'b' kama x) order by x collate mycoll
            """).fetchall()
        self.assertEqual(result[0][0], 'b')
        self.assertEqual(result[1][0], 'a')

    eleza CheckDeregisterCollation(self):
        """
        Register a collation, then deregister it. Make sure an error ni ashiriad ikiwa we try
        to use it.
        """
        con = sqlite.connect(":memory:")
        con.create_collation("mycoll", lambda x, y: (x > y) - (x < y))
        con.create_collation("mycoll", Tupu)
        with self.assertRaises(sqlite.OperationalError) kama cm:
            con.execute("select 'a' kama x union select 'b' kama x order by x collate mycoll")
        self.assertEqual(str(cm.exception), 'no such collation sequence: mycoll')

kundi ProgressTests(unittest.TestCase):
    eleza CheckProgressHandlerUsed(self):
        """
        Test that the progress handler ni invoked once it ni set.
        """
        con = sqlite.connect(":memory:")
        progress_calls = []
        eleza progress():
            progress_calls.append(Tupu)
            rudisha 0
        con.set_progress_handler(progress, 1)
        con.execute("""
            create table foo(a, b)
            """)
        self.assertKweli(progress_calls)


    eleza CheckOpcodeCount(self):
        """
        Test that the opcode argument ni respected.
        """
        con = sqlite.connect(":memory:")
        progress_calls = []
        eleza progress():
            progress_calls.append(Tupu)
            rudisha 0
        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        curs.execute("""
            create table foo (a, b)
            """)
        first_count = len(progress_calls)
        progress_calls = []
        con.set_progress_handler(progress, 2)
        curs.execute("""
            create table bar (a, b)
            """)
        second_count = len(progress_calls)
        self.assertGreaterEqual(first_count, second_count)

    eleza CheckCancelOperation(self):
        """
        Test that rudishaing a non-zero value stops the operation kwenye progress.
        """
        con = sqlite.connect(":memory:")
        eleza progress():
            rudisha 1
        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        self.assertRaises(
            sqlite.OperationalError,
            curs.execute,
            "create table bar (a, b)")

    eleza CheckClearHandler(self):
        """
        Test that setting the progress handler to Tupu clears the previously set handler.
        """
        con = sqlite.connect(":memory:")
        action = 0
        eleza progress():
            nonlocal action
            action = 1
            rudisha 0
        con.set_progress_handler(progress, 1)
        con.set_progress_handler(Tupu, 1)
        con.execute("select 1 union select 2 union select 3").fetchall()
        self.assertEqual(action, 0, "progress handler was sio cleared")

kundi TraceCallbackTests(unittest.TestCase):
    eleza CheckTraceCallbackUsed(self):
        """
        Test that the trace callback ni invoked once it ni set.
        """
        con = sqlite.connect(":memory:")
        traced_statements = []
        eleza trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.execute("create table foo(a, b)")
        self.assertKweli(traced_statements)
        self.assertKweli(any("create table foo" kwenye stmt kila stmt kwenye traced_statements))

    eleza CheckClearTraceCallback(self):
        """
        Test that setting the trace callback to Tupu clears the previously set callback.
        """
        con = sqlite.connect(":memory:")
        traced_statements = []
        eleza trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.set_trace_callback(Tupu)
        con.execute("create table foo(a, b)")
        self.assertUongo(traced_statements, "trace callback was sio cleared")

    eleza CheckUnicodeContent(self):
        """
        Test that the statement can contain unicode literals.
        """
        unicode_value = '\xf6\xe4\xfc\xd6\xc4\xdc\xdf\u20ac'
        con = sqlite.connect(":memory:")
        traced_statements = []
        eleza trace(statement):
            traced_statements.append(statement)
        con.set_trace_callback(trace)
        con.execute("create table foo(x)")
        # Can't execute bound parameters kama their values don't appear
        # kwenye traced statements before SQLite 3.6.21
        # (cf. http://www.sqlite.org/draft/releaselog/3_6_21.html)
        con.execute('insert into foo(x) values ("%s")' % unicode_value)
        con.commit()
        self.assertKweli(any(unicode_value kwenye stmt kila stmt kwenye traced_statements),
                        "Unicode data %s garbled kwenye trace callback: %s"
                        % (ascii(unicode_value), ', '.join(map(ascii, traced_statements))))

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 3, 9), "sqlite3_prepare_v2 ni sio available")
    eleza CheckTraceCallbackContent(self):
        # set_trace_callback() shouldn't produce duplicate content (bpo-26187)
        traced_statements = []
        eleza trace(statement):
            traced_statements.append(statement)

        queries = ["create table foo(x)",
                   "insert into foo(x) values(1)"]
        self.addCleanup(unlink, TESTFN)
        con1 = sqlite.connect(TESTFN, isolation_level=Tupu)
        con2 = sqlite.connect(TESTFN)
        con1.set_trace_callback(trace)
        cur = con1.cursor()
        cur.execute(queries[0])
        con2.execute("create table bar(x)")
        cur.execute(queries[1])
        self.assertEqual(traced_statements, queries)


eleza suite():
    collation_suite = unittest.makeSuite(CollationTests, "Check")
    progress_suite = unittest.makeSuite(ProgressTests, "Check")
    trace_suite = unittest.makeSuite(TraceCallbackTests, "Check")
    rudisha unittest.TestSuite((collation_suite, progress_suite, trace_suite))

eleza test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

ikiwa __name__ == "__main__":
    test()
