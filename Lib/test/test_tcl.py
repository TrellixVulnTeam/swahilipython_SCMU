agiza unittest
agiza re
agiza subprocess
agiza sys
agiza os
kutoka test agiza support

# Skip this test ikiwa the _tkinter module wasn't built.
_tkinter = support.import_module('_tkinter')

agiza tkinter
kutoka tkinter agiza Tcl
kutoka _tkinter agiza TclError

jaribu:
    kutoka _testcapi agiza INT_MAX, PY_SSIZE_T_MAX
tatizo ImportError:
    INT_MAX = PY_SSIZE_T_MAX = sys.maxsize

tcl_version = tuple(map(int, _tkinter.TCL_VERSION.split('.')))

_tk_patchlevel = Tupu
eleza get_tk_patchlevel():
    global _tk_patchlevel
    ikiwa _tk_patchlevel ni Tupu:
        tcl = Tcl()
        patchlevel = tcl.call('info', 'patchlevel')
        m = re.fullmatch(r'(\d+)\.(\d+)([ab.])(\d+)', patchlevel)
        major, minor, releaselevel, serial = m.groups()
        major, minor, serial = int(major), int(minor), int(serial)
        releaselevel = {'a': 'alpha', 'b': 'beta', '.': 'final'}[releaselevel]
        ikiwa releaselevel == 'final':
            _tk_patchlevel = major, minor, serial, releaselevel, 0
        isipokua:
            _tk_patchlevel = major, minor, 0, releaselevel, serial
    rudisha _tk_patchlevel


kundi TkinterTest(unittest.TestCase):

    eleza testFlattenLen(self):
        # flatten(<object ukijumuisha no length>)
        self.assertRaises(TypeError, _tkinter._flatten, Kweli)


kundi TclTest(unittest.TestCase):

    eleza setUp(self):
        self.interp = Tcl()
        self.wantobjects = self.interp.tk.wantobjects()

    eleza testEval(self):
        tcl = self.interp
        tcl.eval('set a 1')
        self.assertEqual(tcl.eval('set a'),'1')

    eleza test_eval_null_in_result(self):
        tcl = self.interp
        self.assertEqual(tcl.eval('set a "a\\0b"'), 'a\x00b')

    eleza testEvalException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.eval,'set a')

    eleza testEvalException2(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.eval,'this ni wrong')

    eleza testCall(self):
        tcl = self.interp
        tcl.call('set','a','1')
        self.assertEqual(tcl.call('set','a'),'1')

    eleza testCallException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.call,'set','a')

    eleza testCallException2(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.call,'this','is','wrong')

    eleza testSetVar(self):
        tcl = self.interp
        tcl.setvar('a','1')
        self.assertEqual(tcl.eval('set a'),'1')

    eleza testSetVarArray(self):
        tcl = self.interp
        tcl.setvar('a(1)','1')
        self.assertEqual(tcl.eval('set a(1)'),'1')

    eleza testGetVar(self):
        tcl = self.interp
        tcl.eval('set a 1')
        self.assertEqual(tcl.getvar('a'),'1')

    eleza testGetVarArray(self):
        tcl = self.interp
        tcl.eval('set a(1) 1')
        self.assertEqual(tcl.getvar('a(1)'),'1')

    eleza testGetVarException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.getvar,'a')

    eleza testGetVarArrayException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.getvar,'a(1)')

    eleza testUnsetVar(self):
        tcl = self.interp
        tcl.setvar('a',1)
        self.assertEqual(tcl.eval('info exists a'),'1')
        tcl.unsetvar('a')
        self.assertEqual(tcl.eval('info exists a'),'0')

    eleza testUnsetVarArray(self):
        tcl = self.interp
        tcl.setvar('a(1)',1)
        tcl.setvar('a(2)',2)
        self.assertEqual(tcl.eval('info exists a(1)'),'1')
        self.assertEqual(tcl.eval('info exists a(2)'),'1')
        tcl.unsetvar('a(1)')
        self.assertEqual(tcl.eval('info exists a(1)'),'0')
        self.assertEqual(tcl.eval('info exists a(2)'),'1')

    eleza testUnsetVarException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.unsetvar,'a')

    eleza get_integers(self):
        integers = (0, 1, -1, 2**31-1, -2**31, 2**31, -2**31-1, 2**63-1, -2**63)
        # bignum was added kwenye Tcl 8.5, but its support ni able only since 8.5.8
        ikiwa (get_tk_patchlevel() >= (8, 6, 0, 'final') ama
            (8, 5, 8) <= get_tk_patchlevel() < (8, 6)):
            integers += (2**63, -2**63-1, 2**1000, -2**1000)
        rudisha integers

    eleza test_getint(self):
        tcl = self.interp.tk
        kila i kwenye self.get_integers():
            self.assertEqual(tcl.getint(' %d ' % i), i)
            ikiwa tcl_version >= (8, 5):
                self.assertEqual(tcl.getint(' %#o ' % i), i)
            self.assertEqual(tcl.getint((' %#o ' % i).replace('o', '')), i)
            self.assertEqual(tcl.getint(' %#x ' % i), i)
        ikiwa tcl_version < (8, 5):  # bignum was added kwenye Tcl 8.5
            self.assertRaises(TclError, tcl.getint, str(2**1000))
        self.assertEqual(tcl.getint(42), 42)
        self.assertRaises(TypeError, tcl.getint)
        self.assertRaises(TypeError, tcl.getint, '42', '10')
        self.assertRaises(TypeError, tcl.getint, b'42')
        self.assertRaises(TypeError, tcl.getint, 42.0)
        self.assertRaises(TclError, tcl.getint, 'a')
        self.assertRaises((TypeError, ValueError, TclError),
                          tcl.getint, '42\0')
        self.assertRaises((UnicodeEncodeError, ValueError, TclError),
                          tcl.getint, '42\ud800')

    eleza test_getdouble(self):
        tcl = self.interp.tk
        self.assertEqual(tcl.getdouble(' 42 '), 42.0)
        self.assertEqual(tcl.getdouble(' 42.5 '), 42.5)
        self.assertEqual(tcl.getdouble(42.5), 42.5)
        self.assertEqual(tcl.getdouble(42), 42.0)
        self.assertRaises(TypeError, tcl.getdouble)
        self.assertRaises(TypeError, tcl.getdouble, '42.5', '10')
        self.assertRaises(TypeError, tcl.getdouble, b'42.5')
        self.assertRaises(TclError, tcl.getdouble, 'a')
        self.assertRaises((TypeError, ValueError, TclError),
                          tcl.getdouble, '42.5\0')
        self.assertRaises((UnicodeEncodeError, ValueError, TclError),
                          tcl.getdouble, '42.5\ud800')

    eleza test_getboolean(self):
        tcl = self.interp.tk
        self.assertIs(tcl.getboolean('on'), Kweli)
        self.assertIs(tcl.getboolean('1'), Kweli)
        self.assertIs(tcl.getboolean(42), Kweli)
        self.assertIs(tcl.getboolean(0), Uongo)
        self.assertRaises(TypeError, tcl.getboolean)
        self.assertRaises(TypeError, tcl.getboolean, 'on', '1')
        self.assertRaises(TypeError, tcl.getboolean, b'on')
        self.assertRaises(TypeError, tcl.getboolean, 1.0)
        self.assertRaises(TclError, tcl.getboolean, 'a')
        self.assertRaises((TypeError, ValueError, TclError),
                          tcl.getboolean, 'on\0')
        self.assertRaises((UnicodeEncodeError, ValueError, TclError),
                          tcl.getboolean, 'on\ud800')

    eleza testEvalFile(self):
        tcl = self.interp
        ukijumuisha open(support.TESTFN, 'w') kama f:
            self.addCleanup(support.unlink, support.TESTFN)
            f.write("""set a 1
            set b 2
            set c [ expr $a + $b ]
            """)
        tcl.evalfile(support.TESTFN)
        self.assertEqual(tcl.eval('set a'),'1')
        self.assertEqual(tcl.eval('set b'),'2')
        self.assertEqual(tcl.eval('set c'),'3')

    eleza test_evalfile_null_in_result(self):
        tcl = self.interp
        ukijumuisha open(support.TESTFN, 'w') kama f:
            self.addCleanup(support.unlink, support.TESTFN)
            f.write("""
            set a "a\0b"
            set b "a\\0b"
            """)
        tcl.evalfile(support.TESTFN)
        self.assertEqual(tcl.eval('set a'), 'a\x00b')
        self.assertEqual(tcl.eval('set b'), 'a\x00b')

    eleza testEvalFileException(self):
        tcl = self.interp
        filename = "doesnotexists"
        jaribu:
            os.remove(filename)
        tatizo Exception kama e:
            pita
        self.assertRaises(TclError,tcl.evalfile,filename)

    eleza testPackageRequireException(self):
        tcl = self.interp
        self.assertRaises(TclError,tcl.eval,'package require DNE')

    @unittest.skipUnless(sys.platform == 'win32', 'Requires Windows')
    eleza testLoadWithUNC(self):
        # Build a UNC path kutoka the regular path.
        # Something like
        #   \\%COMPUTERNAME%\c$\python27\python.exe

        fullname = os.path.abspath(sys.executable)
        ikiwa fullname[1] != ':':
            ashiria unittest.SkipTest('Absolute path should have drive part')
        unc_name = r'\\%s\%s$\%s' % (os.environ['COMPUTERNAME'],
                                    fullname[0],
                                    fullname[3:])
        ikiwa sio os.path.exists(unc_name):
            ashiria unittest.SkipTest('Cannot connect to UNC Path')

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.unset("TCL_LIBRARY")
            stdout = subprocess.check_output(
                    [unc_name, '-c', 'agiza tkinter; andika(tkinter)'])

        self.assertIn(b'tkinter', stdout)

    eleza test_exprstring(self):
        tcl = self.interp
        tcl.call('set', 'a', 3)
        tcl.call('set', 'b', 6)
        eleza check(expr, expected):
            result = tcl.exprstring(expr)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, str)

        self.assertRaises(TypeError, tcl.exprstring)
        self.assertRaises(TypeError, tcl.exprstring, '8.2', '+6')
        self.assertRaises(TypeError, tcl.exprstring, b'8.2 + 6')
        self.assertRaises(TclError, tcl.exprstring, 'spam')
        check('', '0')
        check('8.2 + 6', '14.2')
        check('3.1 + $a', '6.1')
        check('2 + "$a.$b"', '5.6')
        check('4*[llength "6 2"]', '8')
        check('{word one} < "word $a"', '0')
        check('4*2 < 7', '0')
        check('hypot($a, 4)', '5.0')
        check('5 / 4', '1')
        check('5 / 4.0', '1.25')
        check('5 / ( [string length "abcd"] + 0.0 )', '1.25')
        check('20.0/5.0', '4.0')
        check('"0x03" > "2"', '1')
        check('[string length "a\xbd\u20ac"]', '3')
        check(r'[string length "a\xbd\u20ac"]', '3')
        check('"abc"', 'abc')
        check('"a\xbd\u20ac"', 'a\xbd\u20ac')
        check(r'"a\xbd\u20ac"', 'a\xbd\u20ac')
        check(r'"a\0b"', 'a\x00b')
        ikiwa tcl_version >= (8, 5):  # bignum was added kwenye Tcl 8.5
            check('2**64', str(2**64))

    eleza test_exprdouble(self):
        tcl = self.interp
        tcl.call('set', 'a', 3)
        tcl.call('set', 'b', 6)
        eleza check(expr, expected):
            result = tcl.exprdouble(expr)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, float)

        self.assertRaises(TypeError, tcl.exprdouble)
        self.assertRaises(TypeError, tcl.exprdouble, '8.2', '+6')
        self.assertRaises(TypeError, tcl.exprdouble, b'8.2 + 6')
        self.assertRaises(TclError, tcl.exprdouble, 'spam')
        check('', 0.0)
        check('8.2 + 6', 14.2)
        check('3.1 + $a', 6.1)
        check('2 + "$a.$b"', 5.6)
        check('4*[llength "6 2"]', 8.0)
        check('{word one} < "word $a"', 0.0)
        check('4*2 < 7', 0.0)
        check('hypot($a, 4)', 5.0)
        check('5 / 4', 1.0)
        check('5 / 4.0', 1.25)
        check('5 / ( [string length "abcd"] + 0.0 )', 1.25)
        check('20.0/5.0', 4.0)
        check('"0x03" > "2"', 1.0)
        check('[string length "a\xbd\u20ac"]', 3.0)
        check(r'[string length "a\xbd\u20ac"]', 3.0)
        self.assertRaises(TclError, tcl.exprdouble, '"abc"')
        ikiwa tcl_version >= (8, 5):  # bignum was added kwenye Tcl 8.5
            check('2**64', float(2**64))

    eleza test_exprlong(self):
        tcl = self.interp
        tcl.call('set', 'a', 3)
        tcl.call('set', 'b', 6)
        eleza check(expr, expected):
            result = tcl.exprlong(expr)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, int)

        self.assertRaises(TypeError, tcl.exprlong)
        self.assertRaises(TypeError, tcl.exprlong, '8.2', '+6')
        self.assertRaises(TypeError, tcl.exprlong, b'8.2 + 6')
        self.assertRaises(TclError, tcl.exprlong, 'spam')
        check('', 0)
        check('8.2 + 6', 14)
        check('3.1 + $a', 6)
        check('2 + "$a.$b"', 5)
        check('4*[llength "6 2"]', 8)
        check('{word one} < "word $a"', 0)
        check('4*2 < 7', 0)
        check('hypot($a, 4)', 5)
        check('5 / 4', 1)
        check('5 / 4.0', 1)
        check('5 / ( [string length "abcd"] + 0.0 )', 1)
        check('20.0/5.0', 4)
        check('"0x03" > "2"', 1)
        check('[string length "a\xbd\u20ac"]', 3)
        check(r'[string length "a\xbd\u20ac"]', 3)
        self.assertRaises(TclError, tcl.exprlong, '"abc"')
        ikiwa tcl_version >= (8, 5):  # bignum was added kwenye Tcl 8.5
            self.assertRaises(TclError, tcl.exprlong, '2**64')

    eleza test_exprboolean(self):
        tcl = self.interp
        tcl.call('set', 'a', 3)
        tcl.call('set', 'b', 6)
        eleza check(expr, expected):
            result = tcl.exprboolean(expr)
            self.assertEqual(result, expected)
            self.assertIsInstance(result, int)
            self.assertNotIsInstance(result, bool)

        self.assertRaises(TypeError, tcl.exprboolean)
        self.assertRaises(TypeError, tcl.exprboolean, '8.2', '+6')
        self.assertRaises(TypeError, tcl.exprboolean, b'8.2 + 6')
        self.assertRaises(TclError, tcl.exprboolean, 'spam')
        check('', Uongo)
        kila value kwenye ('0', 'false', 'no', 'off'):
            check(value, Uongo)
            check('"%s"' % value, Uongo)
            check('{%s}' % value, Uongo)
        kila value kwenye ('1', 'true', 'yes', 'on'):
            check(value, Kweli)
            check('"%s"' % value, Kweli)
            check('{%s}' % value, Kweli)
        check('8.2 + 6', Kweli)
        check('3.1 + $a', Kweli)
        check('2 + "$a.$b"', Kweli)
        check('4*[llength "6 2"]', Kweli)
        check('{word one} < "word $a"', Uongo)
        check('4*2 < 7', Uongo)
        check('hypot($a, 4)', Kweli)
        check('5 / 4', Kweli)
        check('5 / 4.0', Kweli)
        check('5 / ( [string length "abcd"] + 0.0 )', Kweli)
        check('20.0/5.0', Kweli)
        check('"0x03" > "2"', Kweli)
        check('[string length "a\xbd\u20ac"]', Kweli)
        check(r'[string length "a\xbd\u20ac"]', Kweli)
        self.assertRaises(TclError, tcl.exprboolean, '"abc"')
        ikiwa tcl_version >= (8, 5):  # bignum was added kwenye Tcl 8.5
            check('2**64', Kweli)

    @unittest.skipUnless(tcl_version >= (8, 5), 'requires Tcl version >= 8.5')
    eleza test_booleans(self):
        tcl = self.interp
        eleza check(expr, expected):
            result = tcl.call('expr', expr)
            ikiwa tcl.wantobjects():
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)
            isipokua:
                self.assertIn(result, (expr, str(int(expected))))
                self.assertIsInstance(result, str)
        check('true', Kweli)
        check('yes', Kweli)
        check('on', Kweli)
        check('false', Uongo)
        check('no', Uongo)
        check('off', Uongo)
        check('1 < 2', Kweli)
        check('1 > 2', Uongo)

    eleza test_expr_bignum(self):
        tcl = self.interp
        kila i kwenye self.get_integers():
            result = tcl.call('expr', str(i))
            ikiwa self.wantobjects:
                self.assertEqual(result, i)
                self.assertIsInstance(result, int)
            isipokua:
                self.assertEqual(result, str(i))
                self.assertIsInstance(result, str)
        ikiwa tcl_version < (8, 5):  # bignum was added kwenye Tcl 8.5
            self.assertRaises(TclError, tcl.call, 'expr', str(2**1000))

    eleza test_pitaing_values(self):
        eleza pitaValue(value):
            rudisha self.interp.call('set', '_', value)

        self.assertEqual(pitaValue(Kweli), Kweli ikiwa self.wantobjects isipokua '1')
        self.assertEqual(pitaValue(Uongo), Uongo ikiwa self.wantobjects isipokua '0')
        self.assertEqual(pitaValue('string'), 'string')
        self.assertEqual(pitaValue('string\u20ac'), 'string\u20ac')
        self.assertEqual(pitaValue('string\U0001f4bb'), 'string\U0001f4bb')
        self.assertEqual(pitaValue('str\x00ing'), 'str\x00ing')
        self.assertEqual(pitaValue('str\x00ing\xbd'), 'str\x00ing\xbd')
        self.assertEqual(pitaValue('str\x00ing\u20ac'), 'str\x00ing\u20ac')
        self.assertEqual(pitaValue('str\x00ing\U0001f4bb'),
                         'str\x00ing\U0001f4bb')
        self.assertEqual(pitaValue(b'str\x00ing'),
                         b'str\x00ing' ikiwa self.wantobjects isipokua 'str\x00ing')
        self.assertEqual(pitaValue(b'str\xc0\x80ing'),
                         b'str\xc0\x80ing' ikiwa self.wantobjects isipokua 'str\xc0\x80ing')
        self.assertEqual(pitaValue(b'str\xbding'),
                         b'str\xbding' ikiwa self.wantobjects isipokua 'str\xbding')
        kila i kwenye self.get_integers():
            self.assertEqual(pitaValue(i), i ikiwa self.wantobjects isipokua str(i))
        ikiwa tcl_version < (8, 5):  # bignum was added kwenye Tcl 8.5
            self.assertEqual(pitaValue(2**1000), str(2**1000))
        kila f kwenye (0.0, 1.0, -1.0, 1/3,
                  sys.float_info.min, sys.float_info.max,
                  -sys.float_info.min, -sys.float_info.max):
            ikiwa self.wantobjects:
                self.assertEqual(pitaValue(f), f)
            isipokua:
                self.assertEqual(float(pitaValue(f)), f)
        ikiwa self.wantobjects:
            f = pitaValue(float('nan'))
            self.assertNotEqual(f, f)
            self.assertEqual(pitaValue(float('inf')), float('inf'))
            self.assertEqual(pitaValue(-float('inf')), -float('inf'))
        isipokua:
            self.assertEqual(float(pitaValue(float('inf'))), float('inf'))
            self.assertEqual(float(pitaValue(-float('inf'))), -float('inf'))
            # XXX NaN representation can be sio parsable by float()
        self.assertEqual(pitaValue((1, '2', (3.4,))),
                         (1, '2', (3.4,)) ikiwa self.wantobjects isipokua '1 2 3.4')
        self.assertEqual(pitaValue(['a', ['b', 'c']]),
                         ('a', ('b', 'c')) ikiwa self.wantobjects isipokua 'a {b c}')

    eleza test_user_command(self):
        result = Tupu
        eleza testfunc(arg):
            nonlocal result
            result = arg
            rudisha arg
        self.interp.createcommand('testfunc', testfunc)
        self.addCleanup(self.interp.tk.deletecommand, 'testfunc')
        eleza check(value, expected=Tupu, *, eq=self.assertEqual):
            ikiwa expected ni Tupu:
                expected = value
            nonlocal result
            result = Tupu
            r = self.interp.call('testfunc', value)
            self.assertIsInstance(result, str)
            eq(result, expected)
            self.assertIsInstance(r, str)
            eq(r, expected)
        eleza float_eq(actual, expected):
            self.assertAlmostEqual(float(actual), expected,
                                   delta=abs(expected) * 1e-10)

        check(Kweli, '1')
        check(Uongo, '0')
        check('string')
        check('string\xbd')
        check('string\u20ac')
        check('string\U0001f4bb')
        check('')
        check(b'string', 'string')
        check(b'string\xe2\x82\xac', 'string\xe2\x82\xac')
        check(b'string\xbd', 'string\xbd')
        check(b'', '')
        check('str\x00ing')
        check('str\x00ing\xbd')
        check('str\x00ing\u20ac')
        check(b'str\x00ing', 'str\x00ing')
        check(b'str\xc0\x80ing', 'str\xc0\x80ing')
        check(b'str\xc0\x80ing\xe2\x82\xac', 'str\xc0\x80ing\xe2\x82\xac')
        kila i kwenye self.get_integers():
            check(i, str(i))
        ikiwa tcl_version < (8, 5):  # bignum was added kwenye Tcl 8.5
            check(2**1000, str(2**1000))
        kila f kwenye (0.0, 1.0, -1.0):
            check(f, repr(f))
        kila f kwenye (1/3.0, sys.float_info.min, sys.float_info.max,
                  -sys.float_info.min, -sys.float_info.max):
            check(f, eq=float_eq)
        check(float('inf'), eq=float_eq)
        check(-float('inf'), eq=float_eq)
        # XXX NaN representation can be sio parsable by float()
        check((), '')
        check((1, (2,), (3, 4), '5 6', ()), '1 2 {3 4} {5 6} {}')
        check([1, [2,], [3, 4], '5 6', []], '1 2 {3 4} {5 6} {}')

    eleza test_splitlist(self):
        splitlist = self.interp.tk.splitlist
        call = self.interp.tk.call
        self.assertRaises(TypeError, splitlist)
        self.assertRaises(TypeError, splitlist, 'a', 'b')
        self.assertRaises(TypeError, splitlist, 2)
        testcases = [
            ('2', ('2',)),
            ('', ()),
            ('{}', ('',)),
            ('""', ('',)),
            ('a\n b\t\r c\n ', ('a', 'b', 'c')),
            (b'a\n b\t\r c\n ', ('a', 'b', 'c')),
            ('a \u20ac', ('a', '\u20ac')),
            ('a \U0001f4bb', ('a', '\U0001f4bb')),
            (b'a \xe2\x82\xac', ('a', '\u20ac')),
            (b'a\xc0\x80b c\xc0\x80d', ('a\x00b', 'c\x00d')),
            ('a {b c}', ('a', 'b c')),
            (r'a b\ c', ('a', 'b c')),
            (('a', 'b c'), ('a', 'b c')),
            ('a 2', ('a', '2')),
            (('a', 2), ('a', 2)),
            ('a 3.4', ('a', '3.4')),
            (('a', 3.4), ('a', 3.4)),
            ((), ()),
            ([], ()),
            (['a', ['b', 'c']], ('a', ['b', 'c'])),
            (call('list', 1, '2', (3.4,)),
                (1, '2', (3.4,)) ikiwa self.wantobjects ama
                ('1', '2', '3.4')),
        ]
        tk_patchlevel = get_tk_patchlevel()
        ikiwa tcl_version >= (8, 5):
            ikiwa sio self.wantobjects ama tk_patchlevel < (8, 5, 5):
                # Before 8.5.5 dicts were converted to lists through string
                expected = ('12', '\u20ac', '\xe2\x82\xac', '3.4')
            isipokua:
                expected = (12, '\u20ac', b'\xe2\x82\xac', (3.4,))
            testcases += [
                (call('dict', 'create', 12, '\u20ac', b'\xe2\x82\xac', (3.4,)),
                    expected),
            ]
        dbg_info = ('want objects? %s, Tcl version: %s, Tk patchlevel: %s'
                    % (self.wantobjects, tcl_version, tk_patchlevel))
        kila arg, res kwenye testcases:
            self.assertEqual(splitlist(arg), res,
                             'arg=%a, %s' % (arg, dbg_info))
        self.assertRaises(TclError, splitlist, '{')

    eleza test_split(self):
        split = self.interp.tk.split
        call = self.interp.tk.call
        self.assertRaises(TypeError, split)
        self.assertRaises(TypeError, split, 'a', 'b')
        self.assertRaises(TypeError, split, 2)
        testcases = [
            ('2', '2'),
            ('', ''),
            ('{}', ''),
            ('""', ''),
            ('{', '{'),
            ('a\n b\t\r c\n ', ('a', 'b', 'c')),
            (b'a\n b\t\r c\n ', ('a', 'b', 'c')),
            ('a \u20ac', ('a', '\u20ac')),
            (b'a \xe2\x82\xac', ('a', '\u20ac')),
            (b'a\xc0\x80b', 'a\x00b'),
            (b'a\xc0\x80b c\xc0\x80d', ('a\x00b', 'c\x00d')),
            (b'{a\xc0\x80b c\xc0\x80d', '{a\x00b c\x00d'),
            ('a {b c}', ('a', ('b', 'c'))),
            (r'a b\ c', ('a', ('b', 'c'))),
            (('a', b'b c'), ('a', ('b', 'c'))),
            (('a', 'b c'), ('a', ('b', 'c'))),
            ('a 2', ('a', '2')),
            (('a', 2), ('a', 2)),
            ('a 3.4', ('a', '3.4')),
            (('a', 3.4), ('a', 3.4)),
            (('a', (2, 3.4)), ('a', (2, 3.4))),
            ((), ()),
            ([], ()),
            (['a', 'b c'], ('a', ('b', 'c'))),
            (['a', ['b', 'c']], ('a', ('b', 'c'))),
            (call('list', 1, '2', (3.4,)),
                (1, '2', (3.4,)) ikiwa self.wantobjects ama
                ('1', '2', '3.4')),
        ]
        ikiwa tcl_version >= (8, 5):
            ikiwa sio self.wantobjects ama get_tk_patchlevel() < (8, 5, 5):
                # Before 8.5.5 dicts were converted to lists through string
                expected = ('12', '\u20ac', '\xe2\x82\xac', '3.4')
            isipokua:
                expected = (12, '\u20ac', b'\xe2\x82\xac', (3.4,))
            testcases += [
                (call('dict', 'create', 12, '\u20ac', b'\xe2\x82\xac', (3.4,)),
                    expected),
            ]
        kila arg, res kwenye testcases:
            self.assertEqual(split(arg), res, msg=arg)

    eleza test_splitdict(self):
        splitdict = tkinter._splitdict
        tcl = self.interp.tk

        arg = '-a {1 2 3} -something foo status {}'
        self.assertEqual(splitdict(tcl, arg, Uongo),
            {'-a': '1 2 3', '-something': 'foo', 'status': ''})
        self.assertEqual(splitdict(tcl, arg),
            {'a': '1 2 3', 'something': 'foo', 'status': ''})

        arg = ('-a', (1, 2, 3), '-something', 'foo', 'status', '{}')
        self.assertEqual(splitdict(tcl, arg, Uongo),
            {'-a': (1, 2, 3), '-something': 'foo', 'status': '{}'})
        self.assertEqual(splitdict(tcl, arg),
            {'a': (1, 2, 3), 'something': 'foo', 'status': '{}'})

        self.assertRaises(RuntimeError, splitdict, tcl, '-a b -c ')
        self.assertRaises(RuntimeError, splitdict, tcl, ('-a', 'b', '-c'))

        arg = tcl.call('list',
                        '-a', (1, 2, 3), '-something', 'foo', 'status', ())
        self.assertEqual(splitdict(tcl, arg),
            {'a': (1, 2, 3) ikiwa self.wantobjects isipokua '1 2 3',
             'something': 'foo', 'status': ''})

        ikiwa tcl_version >= (8, 5):
            arg = tcl.call('dict', 'create',
                           '-a', (1, 2, 3), '-something', 'foo', 'status', ())
            ikiwa sio self.wantobjects ama get_tk_patchlevel() < (8, 5, 5):
                # Before 8.5.5 dicts were converted to lists through string
                expected = {'a': '1 2 3', 'something': 'foo', 'status': ''}
            isipokua:
                expected = {'a': (1, 2, 3), 'something': 'foo', 'status': ''}
            self.assertEqual(splitdict(tcl, arg), expected)

    eleza test_join(self):
        join = tkinter._join
        tcl = self.interp.tk
        eleza unpack(s):
            rudisha tcl.call('lindex', s, 0)
        eleza check(value):
            self.assertEqual(unpack(join([value])), value)
            self.assertEqual(unpack(join([value, 0])), value)
            self.assertEqual(unpack(unpack(join([[value]]))), value)
            self.assertEqual(unpack(unpack(join([[value, 0]]))), value)
            self.assertEqual(unpack(unpack(join([[value], 0]))), value)
            self.assertEqual(unpack(unpack(join([[value, 0], 0]))), value)
        check('')
        check('spam')
        check('sp am')
        check('sp\tam')
        check('sp\nam')
        check(' \t\n')
        check('{spam}')
        check('{sp am}')
        check('"spam"')
        check('"sp am"')
        check('{"spam"}')
        check('"{spam}"')
        check('sp\\am')
        check('"sp\\am"')
        check('"{}" "{}"')
        check('"\\')
        check('"{')
        check('"}')
        check('\n\\')
        check('\n{')
        check('\n}')
        check('\\\n')
        check('{\n')
        check('}\n')

    eleza test_new_tcl_obj(self):
        self.assertRaises(TypeError, _tkinter.Tcl_Obj)

kundi BigmemTclTest(unittest.TestCase):

    eleza setUp(self):
        self.interp = Tcl()

    @support.cpython_only
    @unittest.skipUnless(INT_MAX < PY_SSIZE_T_MAX, "needs UINT_MAX < SIZE_MAX")
    @support.bigmemtest(size=INT_MAX + 1, memuse=5, dry_run=Uongo)
    eleza test_huge_string_call(self, size):
        value = ' ' * size
        self.assertRaises(OverflowError, self.interp.call, 'string', 'index', value, 0)

    @support.cpython_only
    @unittest.skipUnless(INT_MAX < PY_SSIZE_T_MAX, "needs UINT_MAX < SIZE_MAX")
    @support.bigmemtest(size=INT_MAX + 1, memuse=2, dry_run=Uongo)
    eleza test_huge_string_builtins(self, size):
        tk = self.interp.tk
        value = '1' + ' ' * size
        self.assertRaises(OverflowError, tk.getint, value)
        self.assertRaises(OverflowError, tk.getdouble, value)
        self.assertRaises(OverflowError, tk.getboolean, value)
        self.assertRaises(OverflowError, tk.eval, value)
        self.assertRaises(OverflowError, tk.evalfile, value)
        self.assertRaises(OverflowError, tk.record, value)
        self.assertRaises(OverflowError, tk.adderrorinfo, value)
        self.assertRaises(OverflowError, tk.setvar, value, 'x', 'a')
        self.assertRaises(OverflowError, tk.setvar, 'x', value, 'a')
        self.assertRaises(OverflowError, tk.unsetvar, value)
        self.assertRaises(OverflowError, tk.unsetvar, 'x', value)
        self.assertRaises(OverflowError, tk.adderrorinfo, value)
        self.assertRaises(OverflowError, tk.exprstring, value)
        self.assertRaises(OverflowError, tk.exprlong, value)
        self.assertRaises(OverflowError, tk.exprboolean, value)
        self.assertRaises(OverflowError, tk.splitlist, value)
        self.assertRaises(OverflowError, tk.split, value)
        self.assertRaises(OverflowError, tk.createcommand, value, max)
        self.assertRaises(OverflowError, tk.deletecommand, value)

    @support.cpython_only
    @unittest.skipUnless(INT_MAX < PY_SSIZE_T_MAX, "needs UINT_MAX < SIZE_MAX")
    @support.bigmemtest(size=INT_MAX + 1, memuse=6, dry_run=Uongo)
    eleza test_huge_string_builtins2(self, size):
        # These commands require larger memory kila possible error messages
        tk = self.interp.tk
        value = '1' + ' ' * size
        self.assertRaises(OverflowError, tk.evalfile, value)
        self.assertRaises(OverflowError, tk.unsetvar, value)
        self.assertRaises(OverflowError, tk.unsetvar, 'x', value)


eleza setUpModule():
    ikiwa support.verbose:
        tcl = Tcl()
        andika('patchlevel =', tcl.call('info', 'patchlevel'))


eleza test_main():
    support.run_unittest(TclTest, TkinterTest, BigmemTclTest)

ikiwa __name__ == "__main__":
    test_main()
