#-*- coding: iso-8859-1 -*-
# pysqlite2/test/userfunctions.py: tests kila user-defined functions and
#                                  aggregates.
#
# Copyright (C) 2005-2007 Gerhard Häring <gh@ghaering.de>
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
agiza unittest.mock
agiza sqlite3 kama sqlite

eleza func_rudishatext():
    rudisha "foo"
eleza func_rudishaunicode():
    rudisha "bar"
eleza func_rudishaint():
    rudisha 42
eleza func_rudishafloat():
    rudisha 3.14
eleza func_rudishanull():
    rudisha Tupu
eleza func_rudishablob():
    rudisha b"blob"
eleza func_rudishalonglong():
    rudisha 1<<31
eleza func_ashiriaexception():
    5/0

eleza func_isstring(v):
    rudisha type(v) ni str
eleza func_isint(v):
    rudisha type(v) ni int
eleza func_isfloat(v):
    rudisha type(v) ni float
eleza func_isnone(v):
    rudisha type(v) ni type(Tupu)
eleza func_isblob(v):
    rudisha isinstance(v, (bytes, memoryview))
eleza func_islonglong(v):
    rudisha isinstance(v, int) na v >= 1<<31

eleza func(*args):
    rudisha len(args)

kundi AggrNoStep:
    eleza __init__(self):
        pita

    eleza finalize(self):
        rudisha 1

kundi AggrNoFinalize:
    eleza __init__(self):
        pita

    eleza step(self, x):
        pita

kundi AggrExceptionInInit:
    eleza __init__(self):
        5/0

    eleza step(self, x):
        pita

    eleza finalize(self):
        pita

kundi AggrExceptionInStep:
    eleza __init__(self):
        pita

    eleza step(self, x):
        5/0

    eleza finalize(self):
        rudisha 42

kundi AggrExceptionInFinalize:
    eleza __init__(self):
        pita

    eleza step(self, x):
        pita

    eleza finalize(self):
        5/0

kundi AggrCheckType:
    eleza __init__(self):
        self.val = Tupu

    eleza step(self, whichType, val):
        theType = {"str": str, "int": int, "float": float, "Tupu": type(Tupu),
                   "blob": bytes}
        self.val = int(theType[whichType] ni type(val))

    eleza finalize(self):
        rudisha self.val

kundi AggrCheckTypes:
    eleza __init__(self):
        self.val = 0

    eleza step(self, whichType, *vals):
        theType = {"str": str, "int": int, "float": float, "Tupu": type(Tupu),
                   "blob": bytes}
        kila val kwenye vals:
            self.val += int(theType[whichType] ni type(val))

    eleza finalize(self):
        rudisha self.val

kundi AggrSum:
    eleza __init__(self):
        self.val = 0.0

    eleza step(self, val):
        self.val += val

    eleza finalize(self):
        rudisha self.val

kundi FunctionTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")

        self.con.create_function("rudishatext", 0, func_rudishatext)
        self.con.create_function("rudishaunicode", 0, func_rudishaunicode)
        self.con.create_function("rudishaint", 0, func_rudishaint)
        self.con.create_function("rudishafloat", 0, func_rudishafloat)
        self.con.create_function("rudishanull", 0, func_rudishanull)
        self.con.create_function("rudishablob", 0, func_rudishablob)
        self.con.create_function("rudishalonglong", 0, func_rudishalonglong)
        self.con.create_function("ashiriaexception", 0, func_ashiriaexception)

        self.con.create_function("isstring", 1, func_isstring)
        self.con.create_function("isint", 1, func_isint)
        self.con.create_function("isfloat", 1, func_isfloat)
        self.con.create_function("isnone", 1, func_isnone)
        self.con.create_function("isblob", 1, func_isblob)
        self.con.create_function("islonglong", 1, func_islonglong)
        self.con.create_function("spam", -1, func)

    eleza tearDown(self):
        self.con.close()

    eleza CheckFuncErrorOnCreate(self):
        with self.assertRaises(sqlite.OperationalError):
            self.con.create_function("bla", -100, lambda x: 2*x)

    eleza CheckFuncRefCount(self):
        eleza getfunc():
            eleza f():
                rudisha 1
            rudisha f
        f = getfunc()
        globals()["foo"] = f
        # self.con.create_function("reftest", 0, getfunc())
        self.con.create_function("reftest", 0, f)
        cur = self.con.cursor()
        cur.execute("select reftest()")

    eleza CheckFuncReturnText(self):
        cur = self.con.cursor()
        cur.execute("select rudishatext()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), str)
        self.assertEqual(val, "foo")

    eleza CheckFuncReturnUnicode(self):
        cur = self.con.cursor()
        cur.execute("select rudishaunicode()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), str)
        self.assertEqual(val, "bar")

    eleza CheckFuncReturnInt(self):
        cur = self.con.cursor()
        cur.execute("select rudishaint()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), int)
        self.assertEqual(val, 42)

    eleza CheckFuncReturnFloat(self):
        cur = self.con.cursor()
        cur.execute("select rudishafloat()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), float)
        ikiwa val < 3.139 ama val > 3.141:
            self.fail("wrong value")

    eleza CheckFuncReturnNull(self):
        cur = self.con.cursor()
        cur.execute("select rudishanull()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), type(Tupu))
        self.assertEqual(val, Tupu)

    eleza CheckFuncReturnBlob(self):
        cur = self.con.cursor()
        cur.execute("select rudishablob()")
        val = cur.fetchone()[0]
        self.assertEqual(type(val), bytes)
        self.assertEqual(val, b"blob")

    eleza CheckFuncReturnLongLong(self):
        cur = self.con.cursor()
        cur.execute("select rudishalonglong()")
        val = cur.fetchone()[0]
        self.assertEqual(val, 1<<31)

    eleza CheckFuncException(self):
        cur = self.con.cursor()
        with self.assertRaises(sqlite.OperationalError) kama cm:
            cur.execute("select ashiriaexception()")
            cur.fetchone()
        self.assertEqual(str(cm.exception), 'user-defined function ashiriad exception')

    eleza CheckParamString(self):
        cur = self.con.cursor()
        cur.execute("select isstring(?)", ("foo",))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckParamInt(self):
        cur = self.con.cursor()
        cur.execute("select isint(?)", (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute("select isfloat(?)", (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckParamTupu(self):
        cur = self.con.cursor()
        cur.execute("select isnone(?)", (Tupu,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute("select isblob(?)", (memoryview(b"blob"),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckParamLongLong(self):
        cur = self.con.cursor()
        cur.execute("select islonglong(?)", (1<<42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAnyArguments(self):
        cur = self.con.cursor()
        cur.execute("select spam(?, ?)", (1, 2))
        val = cur.fetchone()[0]
        self.assertEqual(val, 2)

    eleza CheckFuncNonDeterministic(self):
        mock = unittest.mock.Mock(rudisha_value=Tupu)
        self.con.create_function("deterministic", 0, mock, deterministic=Uongo)
        self.con.execute("select deterministic() = deterministic()")
        self.assertEqual(mock.call_count, 2)

    @unittest.skipIf(sqlite.sqlite_version_info < (3, 8, 3), "deterministic parameter sio supported")
    eleza CheckFuncDeterministic(self):
        mock = unittest.mock.Mock(rudisha_value=Tupu)
        self.con.create_function("deterministic", 0, mock, deterministic=Kweli)
        self.con.execute("select deterministic() = deterministic()")
        self.assertEqual(mock.call_count, 1)

    @unittest.skipIf(sqlite.sqlite_version_info >= (3, 8, 3), "SQLite < 3.8.3 needed")
    eleza CheckFuncDeterministicNotSupported(self):
        with self.assertRaises(sqlite.NotSupportedError):
            self.con.create_function("deterministic", 0, int, deterministic=Kweli)

    eleza CheckFuncDeterministicKeywordOnly(self):
        with self.assertRaises(TypeError):
            self.con.create_function("deterministic", 0, int, Kweli)


kundi AggregateTests(unittest.TestCase):
    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        cur = self.con.cursor()
        cur.execute("""
            create table test(
                t text,
                i integer,
                f float,
                n,
                b blob
                )
            """)
        cur.execute("insert into test(t, i, f, n, b) values (?, ?, ?, ?, ?)",
            ("foo", 5, 3.14, Tupu, memoryview(b"blob"),))

        self.con.create_aggregate("nostep", 1, AggrNoStep)
        self.con.create_aggregate("nofinalize", 1, AggrNoFinalize)
        self.con.create_aggregate("excInit", 1, AggrExceptionInInit)
        self.con.create_aggregate("excStep", 1, AggrExceptionInStep)
        self.con.create_aggregate("excFinalize", 1, AggrExceptionInFinalize)
        self.con.create_aggregate("checkType", 2, AggrCheckType)
        self.con.create_aggregate("checkTypes", -1, AggrCheckTypes)
        self.con.create_aggregate("mysum", 1, AggrSum)

    eleza tearDown(self):
        #self.cur.close()
        #self.con.close()
        pita

    eleza CheckAggrErrorOnCreate(self):
        with self.assertRaises(sqlite.OperationalError):
            self.con.create_function("bla", -100, AggrSum)

    eleza CheckAggrNoStep(self):
        cur = self.con.cursor()
        with self.assertRaises(AttributeError) kama cm:
            cur.execute("select nostep(t) kutoka test")
        self.assertEqual(str(cm.exception), "'AggrNoStep' object has no attribute 'step'")

    eleza CheckAggrNoFinalize(self):
        cur = self.con.cursor()
        with self.assertRaises(sqlite.OperationalError) kama cm:
            cur.execute("select nofinalize(t) kutoka test")
            val = cur.fetchone()[0]
        self.assertEqual(str(cm.exception), "user-defined aggregate's 'finalize' method ashiriad error")

    eleza CheckAggrExceptionInInit(self):
        cur = self.con.cursor()
        with self.assertRaises(sqlite.OperationalError) kama cm:
            cur.execute("select excInit(t) kutoka test")
            val = cur.fetchone()[0]
        self.assertEqual(str(cm.exception), "user-defined aggregate's '__init__' method ashiriad error")

    eleza CheckAggrExceptionInStep(self):
        cur = self.con.cursor()
        with self.assertRaises(sqlite.OperationalError) kama cm:
            cur.execute("select excStep(t) kutoka test")
            val = cur.fetchone()[0]
        self.assertEqual(str(cm.exception), "user-defined aggregate's 'step' method ashiriad error")

    eleza CheckAggrExceptionInFinalize(self):
        cur = self.con.cursor()
        with self.assertRaises(sqlite.OperationalError) kama cm:
            cur.execute("select excFinalize(t) kutoka test")
            val = cur.fetchone()[0]
        self.assertEqual(str(cm.exception), "user-defined aggregate's 'finalize' method ashiriad error")

    eleza CheckAggrCheckParamStr(self):
        cur = self.con.cursor()
        cur.execute("select checkType('str', ?)", ("foo",))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAggrCheckParamInt(self):
        cur = self.con.cursor()
        cur.execute("select checkType('int', ?)", (42,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAggrCheckParamsInt(self):
        cur = self.con.cursor()
        cur.execute("select checkTypes('int', ?, ?)", (42, 24))
        val = cur.fetchone()[0]
        self.assertEqual(val, 2)

    eleza CheckAggrCheckParamFloat(self):
        cur = self.con.cursor()
        cur.execute("select checkType('float', ?)", (3.14,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAggrCheckParamTupu(self):
        cur = self.con.cursor()
        cur.execute("select checkType('Tupu', ?)", (Tupu,))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAggrCheckParamBlob(self):
        cur = self.con.cursor()
        cur.execute("select checkType('blob', ?)", (memoryview(b"blob"),))
        val = cur.fetchone()[0]
        self.assertEqual(val, 1)

    eleza CheckAggrCheckAggrSum(self):
        cur = self.con.cursor()
        cur.execute("delete kutoka test")
        cur.executemany("insert into test(i) values (?)", [(10,), (20,), (30,)])
        cur.execute("select mysum(i) kutoka test")
        val = cur.fetchone()[0]
        self.assertEqual(val, 60)

kundi AuthorizerTests(unittest.TestCase):
    @staticmethod
    eleza authorizer_cb(action, arg1, arg2, dbname, source):
        ikiwa action != sqlite.SQLITE_SELECT:
            rudisha sqlite.SQLITE_DENY
        ikiwa arg2 == 'c2' ama arg1 == 't2':
            rudisha sqlite.SQLITE_DENY
        rudisha sqlite.SQLITE_OK

    eleza setUp(self):
        self.con = sqlite.connect(":memory:")
        self.con.executescript("""
            create table t1 (c1, c2);
            create table t2 (c1, c2);
            insert into t1 (c1, c2) values (1, 2);
            insert into t2 (c1, c2) values (4, 5);
            """)

        # For our security test:
        self.con.execute("select c2 kutoka t2")

        self.con.set_authorizer(self.authorizer_cb)

    eleza tearDown(self):
        pita

    eleza test_table_access(self):
        with self.assertRaises(sqlite.DatabaseError) kama cm:
            self.con.execute("select * kutoka t2")
        self.assertIn('prohibited', str(cm.exception))

    eleza test_column_access(self):
        with self.assertRaises(sqlite.DatabaseError) kama cm:
            self.con.execute("select c2 kutoka t1")
        self.assertIn('prohibited', str(cm.exception))

kundi AuthorizerRaiseExceptionTests(AuthorizerTests):
    @staticmethod
    eleza authorizer_cb(action, arg1, arg2, dbname, source):
        ikiwa action != sqlite.SQLITE_SELECT:
            ashiria ValueError
        ikiwa arg2 == 'c2' ama arg1 == 't2':
            ashiria ValueError
        rudisha sqlite.SQLITE_OK

kundi AuthorizerIllegalTypeTests(AuthorizerTests):
    @staticmethod
    eleza authorizer_cb(action, arg1, arg2, dbname, source):
        ikiwa action != sqlite.SQLITE_SELECT:
            rudisha 0.0
        ikiwa arg2 == 'c2' ama arg1 == 't2':
            rudisha 0.0
        rudisha sqlite.SQLITE_OK

kundi AuthorizerLargeIntegerTests(AuthorizerTests):
    @staticmethod
    eleza authorizer_cb(action, arg1, arg2, dbname, source):
        ikiwa action != sqlite.SQLITE_SELECT:
            rudisha 2**32
        ikiwa arg2 == 'c2' ama arg1 == 't2':
            rudisha 2**32
        rudisha sqlite.SQLITE_OK


eleza suite():
    function_suite = unittest.makeSuite(FunctionTests, "Check")
    aggregate_suite = unittest.makeSuite(AggregateTests, "Check")
    authorizer_suite = unittest.makeSuite(AuthorizerTests)
    rudisha unittest.TestSuite((
            function_suite,
            aggregate_suite,
            authorizer_suite,
            unittest.makeSuite(AuthorizerRaiseExceptionTests),
            unittest.makeSuite(AuthorizerIllegalTypeTests),
            unittest.makeSuite(AuthorizerLargeIntegerTests),
        ))

eleza test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

ikiwa __name__ == "__main__":
    test()
