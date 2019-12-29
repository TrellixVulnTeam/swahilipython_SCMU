# Minimal tests kila dis module

kutoka test.support agiza captured_stdout
kutoka test.bytecode_helper agiza BytecodeTestCase
agiza unittest
agiza sys
agiza dis
agiza io
agiza re
agiza types
agiza contextlib

eleza get_tb():
    eleza _error():
        jaribu:
            1 / 0
        tatizo Exception kama e:
            tb = e.__traceback__
        rudisha tb

    tb = _error()
    wakati tb.tb_next:
        tb = tb.tb_next
    rudisha tb

TRACEBACK_CODE = get_tb().tb_frame.f_code

kundi _C:
    eleza __init__(self, x):
        self.x = x == 1

    @staticmethod
    eleza sm(x):
        x = x == 1

    @classmethod
    eleza cm(cls, x):
        cls.x = x == 1

dis_c_instance_method = """\
%3d           0 LOAD_FAST                1 (x)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               2 (==)
              6 LOAD_FAST                0 (self)
              8 STORE_ATTR               0 (x)
             10 LOAD_CONST               0 (Tupu)
             12 RETURN_VALUE
""" % (_C.__init__.__code__.co_firstlineno + 1,)

dis_c_instance_method_bytes = """\
          0 LOAD_FAST                1 (1)
          2 LOAD_CONST               1 (1)
          4 COMPARE_OP               2 (==)
          6 LOAD_FAST                0 (0)
          8 STORE_ATTR               0 (0)
         10 LOAD_CONST               0 (0)
         12 RETURN_VALUE
"""

dis_c_class_method = """\
%3d           0 LOAD_FAST                1 (x)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               2 (==)
              6 LOAD_FAST                0 (cls)
              8 STORE_ATTR               0 (x)
             10 LOAD_CONST               0 (Tupu)
             12 RETURN_VALUE
""" % (_C.cm.__code__.co_firstlineno + 2,)

dis_c_static_method = """\
%3d           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               2 (==)
              6 STORE_FAST               0 (x)
              8 LOAD_CONST               0 (Tupu)
             10 RETURN_VALUE
""" % (_C.sm.__code__.co_firstlineno + 2,)

# Class disassembling info has an extra newline at end.
dis_c = """\
Disassembly of %s:
%s
Disassembly of %s:
%s
Disassembly of %s:
%s
""" % (_C.__init__.__name__, dis_c_instance_method,
       _C.cm.__name__, dis_c_class_method,
       _C.sm.__name__, dis_c_static_method)

eleza _f(a):
    andika(a)
    rudisha 1

dis_f = """\
%3d           0 LOAD_GLOBAL              0 (print)
              2 LOAD_FAST                0 (a)
              4 CALL_FUNCTION            1
              6 POP_TOP

%3d           8 LOAD_CONST               1 (1)
             10 RETURN_VALUE
""" % (_f.__code__.co_firstlineno + 1,
       _f.__code__.co_firstlineno + 2)


dis_f_co_code = """\
          0 LOAD_GLOBAL              0 (0)
          2 LOAD_FAST                0 (0)
          4 CALL_FUNCTION            1
          6 POP_TOP
          8 LOAD_CONST               1 (1)
         10 RETURN_VALUE
"""


eleza bug708901():
    kila res kwenye range(1,
                     10):
        pita

dis_bug708901 = """\
%3d           0 LOAD_GLOBAL              0 (range)
              2 LOAD_CONST               1 (1)

%3d           4 LOAD_CONST               2 (10)

%3d           6 CALL_FUNCTION            2
              8 GET_ITER
        >>   10 FOR_ITER                 4 (to 16)
             12 STORE_FAST               0 (res)

%3d          14 JUMP_ABSOLUTE           10
        >>   16 LOAD_CONST               0 (Tupu)
             18 RETURN_VALUE
""" % (bug708901.__code__.co_firstlineno + 1,
       bug708901.__code__.co_firstlineno + 2,
       bug708901.__code__.co_firstlineno + 1,
       bug708901.__code__.co_firstlineno + 3)


eleza bug1333982(x=[]):
    assert 0, ([s kila s kwenye x] +
              1)
    pita

dis_bug1333982 = """\
%3d           0 LOAD_CONST               1 (0)
              2 POP_JUMP_IF_TRUE        26
              4 LOAD_GLOBAL              0 (AssertionError)
              6 LOAD_CONST               2 (<code object <listcomp> at 0x..., file "%s", line %d>)
              8 LOAD_CONST               3 ('bug1333982.<locals>.<listcomp>')
             10 MAKE_FUNCTION            0
             12 LOAD_FAST                0 (x)
             14 GET_ITER
             16 CALL_FUNCTION            1

%3d          18 LOAD_CONST               4 (1)

%3d          20 BINARY_ADD
             22 CALL_FUNCTION            1
             24 RAISE_VARARGS            1

%3d     >>   26 LOAD_CONST               0 (Tupu)
             28 RETURN_VALUE
""" % (bug1333982.__code__.co_firstlineno + 1,
       __file__,
       bug1333982.__code__.co_firstlineno + 1,
       bug1333982.__code__.co_firstlineno + 2,
       bug1333982.__code__.co_firstlineno + 1,
       bug1333982.__code__.co_firstlineno + 3)

_BIG_LINENO_FORMAT = """\
%3d           0 LOAD_GLOBAL              0 (spam)
              2 POP_TOP
              4 LOAD_CONST               0 (Tupu)
              6 RETURN_VALUE
"""

_BIG_LINENO_FORMAT2 = """\
%4d           0 LOAD_GLOBAL              0 (spam)
               2 POP_TOP
               4 LOAD_CONST               0 (Tupu)
               6 RETURN_VALUE
"""

dis_module_expected_results = """\
Disassembly of f:
  4           0 LOAD_CONST               0 (Tupu)
              2 RETURN_VALUE

Disassembly of g:
  5           0 LOAD_CONST               0 (Tupu)
              2 RETURN_VALUE

"""

expr_str = "x + 1"

dis_expr_str = """\
  1           0 LOAD_NAME                0 (x)
              2 LOAD_CONST               0 (1)
              4 BINARY_ADD
              6 RETURN_VALUE
"""

simple_stmt_str = "x = x + 1"

dis_simple_stmt_str = """\
  1           0 LOAD_NAME                0 (x)
              2 LOAD_CONST               0 (1)
              4 BINARY_ADD
              6 STORE_NAME               0 (x)
              8 LOAD_CONST               1 (Tupu)
             10 RETURN_VALUE
"""

annot_stmt_str = """\

x: int = 1
y: fun(1)
lst[fun(0)]: int = 1
"""
# leading newline ni kila a reason (tests lineno)

dis_annot_stmt_str = """\
  2           0 SETUP_ANNOTATIONS
              2 LOAD_CONST               0 (1)
              4 STORE_NAME               0 (x)
              6 LOAD_NAME                1 (int)
              8 LOAD_NAME                2 (__annotations__)
             10 LOAD_CONST               1 ('x')
             12 STORE_SUBSCR

  3          14 LOAD_NAME                3 (fun)
             16 LOAD_CONST               0 (1)
             18 CALL_FUNCTION            1
             20 LOAD_NAME                2 (__annotations__)
             22 LOAD_CONST               2 ('y')
             24 STORE_SUBSCR

  4          26 LOAD_CONST               0 (1)
             28 LOAD_NAME                4 (lst)
             30 LOAD_NAME                3 (fun)
             32 LOAD_CONST               3 (0)
             34 CALL_FUNCTION            1
             36 STORE_SUBSCR
             38 LOAD_NAME                1 (int)
             40 POP_TOP
             42 LOAD_CONST               4 (Tupu)
             44 RETURN_VALUE
"""

compound_stmt_str = """\
x = 0
wakati 1:
    x += 1"""
# Trailing newline has been deliberately omitted

dis_compound_stmt_str = """\
  1           0 LOAD_CONST               0 (0)
              2 STORE_NAME               0 (x)

  3     >>    4 LOAD_NAME                0 (x)
              6 LOAD_CONST               1 (1)
              8 INPLACE_ADD
             10 STORE_NAME               0 (x)
             12 JUMP_ABSOLUTE            4
             14 LOAD_CONST               2 (Tupu)
             16 RETURN_VALUE
"""

dis_traceback = """\
%3d           0 SETUP_FINALLY           12 (to 14)

%3d           2 LOAD_CONST               1 (1)
              4 LOAD_CONST               2 (0)
    -->       6 BINARY_TRUE_DIVIDE
              8 POP_TOP
             10 POP_BLOCK
             12 JUMP_FORWARD            40 (to 54)

%3d     >>   14 DUP_TOP
             16 LOAD_GLOBAL              0 (Exception)
             18 COMPARE_OP              10 (exception match)
             20 POP_JUMP_IF_FALSE       52
             22 POP_TOP
             24 STORE_FAST               0 (e)
             26 POP_TOP
             28 SETUP_FINALLY           10 (to 40)

%3d          30 LOAD_FAST                0 (e)
             32 LOAD_ATTR                1 (__traceback__)
             34 STORE_FAST               1 (tb)
             36 POP_BLOCK
             38 BEGIN_FINALLY
        >>   40 LOAD_CONST               0 (Tupu)
             42 STORE_FAST               0 (e)
             44 DELETE_FAST              0 (e)
             46 END_FINALLY
             48 POP_EXCEPT
             50 JUMP_FORWARD             2 (to 54)
        >>   52 END_FINALLY

%3d     >>   54 LOAD_FAST                1 (tb)
             56 RETURN_VALUE
""" % (TRACEBACK_CODE.co_firstlineno + 1,
       TRACEBACK_CODE.co_firstlineno + 2,
       TRACEBACK_CODE.co_firstlineno + 3,
       TRACEBACK_CODE.co_firstlineno + 4,
       TRACEBACK_CODE.co_firstlineno + 5)

eleza _fstring(a, b, c, d):
    rudisha f'{a} {b:4} {c!r} {d!r:4}'

dis_fstring = """\
%3d           0 LOAD_FAST                0 (a)
              2 FORMAT_VALUE             0
              4 LOAD_CONST               1 (' ')
              6 LOAD_FAST                1 (b)
              8 LOAD_CONST               2 ('4')
             10 FORMAT_VALUE             4 (with format)
             12 LOAD_CONST               1 (' ')
             14 LOAD_FAST                2 (c)
             16 FORMAT_VALUE             2 (repr)
             18 LOAD_CONST               1 (' ')
             20 LOAD_FAST                3 (d)
             22 LOAD_CONST               2 ('4')
             24 FORMAT_VALUE             6 (repr, with format)
             26 BUILD_STRING             7
             28 RETURN_VALUE
""" % (_fstring.__code__.co_firstlineno + 1,)

eleza _g(x):
    tuma x

async eleza _ag(x):
    tuma x

async eleza _co(x):
    async kila item kwenye _ag(x):
        pita

eleza _h(y):
    eleza foo(x):
        '''funcdoc'''
        rudisha [x + z kila z kwenye y]
    rudisha foo

dis_nested_0 = """\
%3d           0 LOAD_CLOSURE             0 (y)
              2 BUILD_TUPLE              1
              4 LOAD_CONST               1 (<code object foo at 0x..., file "%s", line %d>)
              6 LOAD_CONST               2 ('_h.<locals>.foo')
              8 MAKE_FUNCTION            8 (closure)
             10 STORE_FAST               1 (foo)

%3d          12 LOAD_FAST                1 (foo)
             14 RETURN_VALUE
""" % (_h.__code__.co_firstlineno + 1,
       __file__,
       _h.__code__.co_firstlineno + 1,
       _h.__code__.co_firstlineno + 4,
)

dis_nested_1 = """%s
Disassembly of <code object foo at 0x..., file "%s", line %d>:
%3d           0 LOAD_CLOSURE             0 (x)
              2 BUILD_TUPLE              1
              4 LOAD_CONST               1 (<code object <listcomp> at 0x..., file "%s", line %d>)
              6 LOAD_CONST               2 ('_h.<locals>.foo.<locals>.<listcomp>')
              8 MAKE_FUNCTION            8 (closure)
             10 LOAD_DEREF               1 (y)
             12 GET_ITER
             14 CALL_FUNCTION            1
             16 RETURN_VALUE
""" % (dis_nested_0,
       __file__,
       _h.__code__.co_firstlineno + 1,
       _h.__code__.co_firstlineno + 3,
       __file__,
       _h.__code__.co_firstlineno + 3,
)

dis_nested_2 = """%s
Disassembly of <code object <listcomp> at 0x..., file "%s", line %d>:
%3d           0 BUILD_LIST               0
              2 LOAD_FAST                0 (.0)
        >>    4 FOR_ITER                12 (to 18)
              6 STORE_FAST               1 (z)
              8 LOAD_DEREF               0 (x)
             10 LOAD_FAST                1 (z)
             12 BINARY_ADD
             14 LIST_APPEND              2
             16 JUMP_ABSOLUTE            4
        >>   18 RETURN_VALUE
""" % (dis_nested_1,
       __file__,
       _h.__code__.co_firstlineno + 3,
       _h.__code__.co_firstlineno + 3,
)


kundi DisTests(unittest.TestCase):

    maxDiff = Tupu

    eleza get_disassembly(self, func, lasti=-1, wrapper=Kweli, **kwargs):
        # We want to test the default printing behaviour, sio the file arg
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ikiwa wrapper:
                dis.dis(func, **kwargs)
            isipokua:
                dis.disassemble(func, lasti, **kwargs)
        rudisha output.getvalue()

    eleza get_disassemble_as_string(self, func, lasti=-1):
        rudisha self.get_disassembly(func, lasti, Uongo)

    eleza strip_addresses(self, text):
        rudisha re.sub(r'\b0x[0-9A-Fa-f]+\b', '0x...', text)

    eleza do_disassembly_test(self, func, expected):
        got = self.get_disassembly(func, depth=0)
        ikiwa got != expected:
            got = self.strip_addresses(got)
        self.assertEqual(got, expected)

    eleza test_opmap(self):
        self.assertEqual(dis.opmap["NOP"], 9)
        self.assertIn(dis.opmap["LOAD_CONST"], dis.hasconst)
        self.assertIn(dis.opmap["STORE_NAME"], dis.hasname)

    eleza test_opname(self):
        self.assertEqual(dis.opname[dis.opmap["LOAD_FAST"]], "LOAD_FAST")

    eleza test_boundaries(self):
        self.assertEqual(dis.opmap["EXTENDED_ARG"], dis.EXTENDED_ARG)
        self.assertEqual(dis.opmap["STORE_NAME"], dis.HAVE_ARGUMENT)

    eleza test_widths(self):
        kila opcode, opname kwenye enumerate(dis.opname):
            ikiwa opname kwenye ('BUILD_MAP_UNPACK_WITH_CALL',
                          'BUILD_TUPLE_UNPACK_WITH_CALL'):
                endelea
            with self.subTest(opname=opname):
                width = dis._OPNAME_WIDTH
                ikiwa opcode < dis.HAVE_ARGUMENT:
                    width += 1 + dis._OPARG_WIDTH
                self.assertLessEqual(len(opname), width)

    eleza test_dis(self):
        self.do_disassembly_test(_f, dis_f)

    eleza test_bug_708901(self):
        self.do_disassembly_test(bug708901, dis_bug708901)

    eleza test_bug_1333982(self):
        # This one ni checking bytecodes generated kila an `assert` statement,
        # so fails ikiwa the tests are run with -O.  Skip this test then.
        ikiwa sio __debug__:
            self.skipTest('need asserts, run without -O')

        self.do_disassembly_test(bug1333982, dis_bug1333982)

    eleza test_big_linenos(self):
        eleza func(count):
            namespace = {}
            func = "eleza foo():\n " + "".join(["\n "] * count + ["spam\n"])
            exec(func, namespace)
            rudisha namespace['foo']

        # Test all small ranges
        kila i kwenye range(1, 300):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)

        # Test some larger ranges too
        kila i kwenye range(300, 1000, 10):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)

        kila i kwenye range(1000, 5000, 10):
            expected = _BIG_LINENO_FORMAT2 % (i + 2)
            self.do_disassembly_test(func(i), expected)

        kutoka test agiza dis_module
        self.do_disassembly_test(dis_module, dis_module_expected_results)

    eleza test_big_offsets(self):
        eleza func(count):
            namespace = {}
            func = "eleza foo(x):\n " + ";".join(["x = x + 1"] * count) + "\n rudisha x"
            exec(func, namespace)
            rudisha namespace['foo']

        eleza expected(count, w):
            s = ['''\
           %*d LOAD_FAST                0 (x)
           %*d LOAD_CONST               1 (1)
           %*d BINARY_ADD
           %*d STORE_FAST               0 (x)
''' % (w, 8*i, w, 8*i + 2, w, 8*i + 4, w, 8*i + 6)
                 kila i kwenye range(count)]
            s += ['''\

  3        %*d LOAD_FAST                0 (x)
           %*d RETURN_VALUE
''' % (w, 8*count, w, 8*count + 2)]
            s[0] = '  2' + s[0][3:]
            rudisha ''.join(s)

        kila i kwenye range(1, 5):
            self.do_disassembly_test(func(i), expected(i, 4))
        self.do_disassembly_test(func(1249), expected(1249, 4))
        self.do_disassembly_test(func(1250), expected(1250, 5))

    eleza test_disassemble_str(self):
        self.do_disassembly_test(expr_str, dis_expr_str)
        self.do_disassembly_test(simple_stmt_str, dis_simple_stmt_str)
        self.do_disassembly_test(annot_stmt_str, dis_annot_stmt_str)
        self.do_disassembly_test(compound_stmt_str, dis_compound_stmt_str)

    eleza test_disassemble_bytes(self):
        self.do_disassembly_test(_f.__code__.co_code, dis_f_co_code)

    eleza test_disassemble_class(self):
        self.do_disassembly_test(_C, dis_c)

    eleza test_disassemble_instance_method(self):
        self.do_disassembly_test(_C(1).__init__, dis_c_instance_method)

    eleza test_disassemble_instance_method_bytes(self):
        method_bytecode = _C(1).__init__.__code__.co_code
        self.do_disassembly_test(method_bytecode, dis_c_instance_method_bytes)

    eleza test_disassemble_static_method(self):
        self.do_disassembly_test(_C.sm, dis_c_static_method)

    eleza test_disassemble_class_method(self):
        self.do_disassembly_test(_C.cm, dis_c_class_method)

    eleza test_disassemble_generator(self):
        gen_func_disas = self.get_disassembly(_g)  # Generator function
        gen_disas = self.get_disassembly(_g(1))  # Generator iterator
        self.assertEqual(gen_disas, gen_func_disas)

    eleza test_disassemble_async_generator(self):
        agen_func_disas = self.get_disassembly(_ag)  # Async generator function
        agen_disas = self.get_disassembly(_ag(1))  # Async generator iterator
        self.assertEqual(agen_disas, agen_func_disas)

    eleza test_disassemble_coroutine(self):
        coro_func_disas = self.get_disassembly(_co)  # Coroutine function
        coro = _co(1)  # Coroutine object
        coro.close()  # Avoid a RuntimeWarning (never awaited)
        coro_disas = self.get_disassembly(coro)
        self.assertEqual(coro_disas, coro_func_disas)

    eleza test_disassemble_fstring(self):
        self.do_disassembly_test(_fstring, dis_fstring)

    eleza test_dis_none(self):
        jaribu:
            toa sys.last_traceback
        tatizo AttributeError:
            pita
        self.assertRaises(RuntimeError, dis.dis, Tupu)

    eleza test_dis_traceback(self):
        jaribu:
            toa sys.last_traceback
        tatizo AttributeError:
            pita

        jaribu:
            1/0
        tatizo Exception kama e:
            tb = e.__traceback__
            sys.last_traceback = tb

        tb_dis = self.get_disassemble_as_string(tb.tb_frame.f_code, tb.tb_lasti)
        self.do_disassembly_test(Tupu, tb_dis)

    eleza test_dis_object(self):
        self.assertRaises(TypeError, dis.dis, object())

    eleza test_disassemble_recursive(self):
        eleza check(expected, **kwargs):
            dis = self.get_disassembly(_h, **kwargs)
            dis = self.strip_addresses(dis)
            self.assertEqual(dis, expected)

        check(dis_nested_0, depth=0)
        check(dis_nested_1, depth=1)
        check(dis_nested_2, depth=2)
        check(dis_nested_2, depth=3)
        check(dis_nested_2, depth=Tupu)
        check(dis_nested_2)


kundi DisWithFileTests(DisTests):

    # Run the tests again, using the file arg instead of print
    eleza get_disassembly(self, func, lasti=-1, wrapper=Kweli, **kwargs):
        output = io.StringIO()
        ikiwa wrapper:
            dis.dis(func, file=output, **kwargs)
        isipokua:
            dis.disassemble(func, lasti, file=output, **kwargs)
        rudisha output.getvalue()



code_info_code_info = """\
Name:              code_info
Filename:          (.*)
Argument count:    1
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  1
Stack size:        3
Flags:             OPTIMIZED, NEWLOCALS, NOFREE
Constants:
   0: %r
Names:
   0: _format_code_info
   1: _get_code_object
Variable names:
   0: x""" % (('Formatted details of methods, functions, ama code.',)
              ikiwa sys.flags.optimize < 2 else (Tupu,))

@staticmethod
eleza tricky(a, b, /, x, y, z=Kweli, *args, c, d, e=[], **kwds):
    eleza f(c=c):
        andika(a, b, x, y, z, c, d, e, f)
    tuma a, b, x, y, z, c, d, e, f

code_info_tricky = """\
Name:              tricky
Filename:          (.*)
Argument count:    5
Positional-only arguments: 2
Kw-only arguments: 3
Number of locals:  10
Stack size:        9
Flags:             OPTIMIZED, NEWLOCALS, VARARGS, VARKEYWORDS, GENERATOR
Constants:
   0: Tupu
   1: <code object f at (.*), file "(.*)", line (.*)>
   2: 'tricky.<locals>.f'
Variable names:
   0: a
   1: b
   2: x
   3: y
   4: z
   5: c
   6: d
   7: e
   8: args
   9: kwds
Cell variables:
   0: [abedfxyz]
   1: [abedfxyz]
   2: [abedfxyz]
   3: [abedfxyz]
   4: [abedfxyz]
   5: [abedfxyz]"""
# NOTE: the order of the cell variables above depends on dictionary order!

co_tricky_nested_f = tricky.__func__.__code__.co_consts[1]

code_info_tricky_nested_f = """\
Filename:          (.*)
Argument count:    1
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  1
Stack size:        10
Flags:             OPTIMIZED, NEWLOCALS, NESTED
Constants:
   0: Tupu
Names:
   0: print
Variable names:
   0: c
Free variables:
   0: [abedfxyz]
   1: [abedfxyz]
   2: [abedfxyz]
   3: [abedfxyz]
   4: [abedfxyz]
   5: [abedfxyz]"""

code_info_expr_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 1
Names:
   0: x"""

code_info_simple_stmt_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 1
   1: Tupu
Names:
   0: x"""

code_info_compound_stmt_str = """\
Name:              <module>
Filename:          <disassembly>
Argument count:    0
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: 0
   1: 1
   2: Tupu
Names:
   0: x"""


async eleza async_def():
    await 1
    async kila a kwenye b: pita
    async with c kama d: pita

code_info_async_eleza = """\
Name:              async_def
Filename:          (.*)
Argument count:    0
Positional-only arguments: 0
Kw-only arguments: 0
Number of locals:  2
Stack size:        10
Flags:             OPTIMIZED, NEWLOCALS, NOFREE, COROUTINE
Constants:
   0: Tupu
   1: 1
Names:
   0: b
   1: c
Variable names:
   0: a
   1: d"""

kundi CodeInfoTests(unittest.TestCase):
    test_pairs = [
      (dis.code_info, code_info_code_info),
      (tricky, code_info_tricky),
      (co_tricky_nested_f, code_info_tricky_nested_f),
      (expr_str, code_info_expr_str),
      (simple_stmt_str, code_info_simple_stmt_str),
      (compound_stmt_str, code_info_compound_stmt_str),
      (async_def, code_info_async_def)
    ]

    eleza test_code_info(self):
        self.maxDiff = 1000
        kila x, expected kwenye self.test_pairs:
            self.assertRegex(dis.code_info(x), expected)

    eleza test_show_code(self):
        self.maxDiff = 1000
        kila x, expected kwenye self.test_pairs:
            with captured_stdout() kama output:
                dis.show_code(x)
            self.assertRegex(output.getvalue(), expected+"\n")
            output = io.StringIO()
            dis.show_code(x, file=output)
            self.assertRegex(output.getvalue(), expected)

    eleza test_code_info_object(self):
        self.assertRaises(TypeError, dis.code_info, object())

    eleza test_pretty_flags_no_flags(self):
        self.assertEqual(dis.pretty_flags(0), '0x0')


# Fodder kila instruction introspection tests
#   Editing any of these may require recalculating the expected output
eleza outer(a=1, b=2):
    eleza f(c=3, d=4):
        eleza inner(e=5, f=6):
            andika(a, b, c, d, e, f)
        andika(a, b, c, d)
        rudisha inner
    andika(a, b, '', 1, [], {}, "Hello world!")
    rudisha f

eleza jumpy():
    # This won't actually run (but that's OK, we only disassemble it)
    kila i kwenye range(10):
        andika(i)
        ikiwa i < 4:
            endelea
        ikiwa i > 6:
            koma
    isipokua:
        andika("I can haz else clause?")
    wakati i:
        andika(i)
        i -= 1
        ikiwa i > 6:
            endelea
        ikiwa i < 4:
            koma
    isipokua:
        andika("Who let lolcatz into this test suite?")
    jaribu:
        1 / 0
    tatizo ZeroDivisionError:
        andika("Here we go, here we go, here we go...")
    isipokua:
        with i kama dodgy:
            andika("Never reach this")
    mwishowe:
        andika("OK, now we're done")

# End fodder kila opinfo generation tests
expected_outer_line = 1
_line_offset = outer.__code__.co_firstlineno - 1
code_object_f = outer.__code__.co_consts[3]
expected_f_line = code_object_f.co_firstlineno - _line_offset
code_object_inner = code_object_f.co_consts[3]
expected_inner_line = code_object_inner.co_firstlineno - _line_offset
expected_jumpy_line = 1

# The following lines are useful to regenerate the expected results after
# either the fodder ni modified ama the bytecode generation changes
# After regeneration, update the references to code_object_f and
# code_object_inner before rerunning the tests

#_instructions = dis.get_instructions(outer, first_line=expected_outer_line)
#andika('expected_opinfo_outer = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(outer(), first_line=expected_f_line)
#andika('expected_opinfo_f = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(outer()(), first_line=expected_inner_line)
#andika('expected_opinfo_inner = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')
#_instructions = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
#andika('expected_opinfo_jumpy = [\n  ',
      #',\n  '.join(map(str, _instructions)), ',\n]', sep='')


Instruction = dis.Instruction
expected_opinfo_outer = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=8, argval=(3, 4), argrepr='(3, 4)', offset=0, starts_line=2, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=0, argval='a', argrepr='a', offset=2, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=1, argval='b', argrepr='b', offset=4, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BUILD_TUPLE', opcode=102, arg=2, argval=2, argrepr='', offset=6, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=code_object_f, argrepr=repr(code_object_f), offset=8, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='outer.<locals>.f', argrepr="'outer.<locals>.f'", offset=10, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='MAKE_FUNCTION', opcode=132, arg=9, argval=9, argrepr='defaults, closure', offset=12, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='STORE_FAST', opcode=125, arg=2, argval='f', argrepr='f', offset=14, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=16, starts_line=7, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='a', argrepr='a', offset=18, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='b', argrepr='b', offset=20, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval='', argrepr="''", offset=22, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=6, argval=1, argrepr='1', offset=24, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BUILD_LIST', opcode=103, arg=0, argval=0, argrepr='', offset=26, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BUILD_MAP', opcode=105, arg=0, argval=0, argrepr='', offset=28, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=7, argval='Hello world!', argrepr="'Hello world!'", offset=30, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=7, argval=7, argrepr='', offset=32, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=34, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=2, argval='f', argrepr='f', offset=36, starts_line=8, is_jump_target=Uongo),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Tupu, argval=Tupu, argrepr='', offset=38, starts_line=Tupu, is_jump_target=Uongo),
]

expected_opinfo_f = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval=(5, 6), argrepr='(5, 6)', offset=0, starts_line=3, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=2, argval='a', argrepr='a', offset=2, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=3, argval='b', argrepr='b', offset=4, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=0, argval='c', argrepr='c', offset=6, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CLOSURE', opcode=135, arg=1, argval='d', argrepr='d', offset=8, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BUILD_TUPLE', opcode=102, arg=4, argval=4, argrepr='', offset=10, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=code_object_inner, argrepr=repr(code_object_inner), offset=12, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='outer.<locals>.f.<locals>.inner', argrepr="'outer.<locals>.f.<locals>.inner'", offset=14, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='MAKE_FUNCTION', opcode=132, arg=9, argval=9, argrepr='defaults, closure', offset=16, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='STORE_FAST', opcode=125, arg=2, argval='inner', argrepr='inner', offset=18, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=20, starts_line=5, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=2, argval='a', argrepr='a', offset=22, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=3, argval='b', argrepr='b', offset=24, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='c', argrepr='c', offset=26, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='d', argrepr='d', offset=28, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=4, argval=4, argrepr='', offset=30, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=32, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=2, argval='inner', argrepr='inner', offset=34, starts_line=6, is_jump_target=Uongo),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Tupu, argval=Tupu, argrepr='', offset=36, starts_line=Tupu, is_jump_target=Uongo),
]

expected_opinfo_inner = [
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='print', argrepr='print', offset=0, starts_line=4, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=0, argval='a', argrepr='a', offset=2, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=1, argval='b', argrepr='b', offset=4, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=2, argval='c', argrepr='c', offset=6, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_DEREF', opcode=136, arg=3, argval='d', argrepr='d', offset=8, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='e', argrepr='e', offset=10, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=1, argval='f', argrepr='f', offset=12, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=6, argval=6, argrepr='', offset=14, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=16, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Tupu, argrepr='Tupu', offset=18, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Tupu, argval=Tupu, argrepr='', offset=20, starts_line=Tupu, is_jump_target=Uongo),
]

expected_opinfo_jumpy = [
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=0, argval='range', argrepr='range', offset=0, starts_line=3, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=10, argrepr='10', offset=2, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=4, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='GET_ITER', opcode=68, arg=Tupu, argval=Tupu, argrepr='', offset=6, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='FOR_ITER', opcode=93, arg=34, argval=44, argrepr='to 44', offset=8, starts_line=Tupu, is_jump_target=Kweli),
  Instruction(opname='STORE_FAST', opcode=125, arg=0, argval='i', argrepr='i', offset=10, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=12, starts_line=4, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=14, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=16, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=18, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=20, starts_line=5, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=4, argrepr='4', offset=22, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='COMPARE_OP', opcode=107, arg=0, argval='<', argrepr='<', offset=24, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=30, argval=30, argrepr='', offset=26, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=8, argval=8, argrepr='', offset=28, starts_line=6, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=30, starts_line=7, is_jump_target=Kweli),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=6, argrepr='6', offset=32, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='COMPARE_OP', opcode=107, arg=4, argval='>', argrepr='>', offset=34, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=8, argval=8, argrepr='', offset=36, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=38, starts_line=8, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=52, argval=52, argrepr='', offset=40, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=8, argval=8, argrepr='', offset=42, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=44, starts_line=10, is_jump_target=Kweli),
  Instruction(opname='LOAD_CONST', opcode=100, arg=4, argval='I can haz else clause?', argrepr="'I can haz else clause?'", offset=46, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=48, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=50, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=52, starts_line=11, is_jump_target=Kweli),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=94, argval=94, argrepr='', offset=54, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=56, starts_line=12, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=58, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=60, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=62, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=64, starts_line=13, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval=1, argrepr='1', offset=66, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='INPLACE_SUBTRACT', opcode=56, arg=Tupu, argval=Tupu, argrepr='', offset=68, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='STORE_FAST', opcode=125, arg=0, argval='i', argrepr='i', offset=70, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=72, starts_line=14, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=3, argval=6, argrepr='6', offset=74, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='COMPARE_OP', opcode=107, arg=4, argval='>', argrepr='>', offset=76, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=82, argval=82, argrepr='', offset=78, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=52, argval=52, argrepr='', offset=80, starts_line=15, is_jump_target=Uongo),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=82, starts_line=16, is_jump_target=Kweli),
  Instruction(opname='LOAD_CONST', opcode=100, arg=2, argval=4, argrepr='4', offset=84, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='COMPARE_OP', opcode=107, arg=0, argval='<', argrepr='<', offset=86, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=52, argval=52, argrepr='', offset=88, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=102, argval=102, argrepr='', offset=90, starts_line=17, is_jump_target=Uongo),
  Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=52, argval=52, argrepr='', offset=92, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=94, starts_line=19, is_jump_target=Kweli),
  Instruction(opname='LOAD_CONST', opcode=100, arg=6, argval='Who let lolcatz into this test suite?', argrepr="'Who let lolcatz into this test suite?'", offset=96, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=98, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=100, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='SETUP_FINALLY', opcode=122, arg=70, argval=174, argrepr='to 174', offset=102, starts_line=20, is_jump_target=Kweli),
  Instruction(opname='SETUP_FINALLY', opcode=122, arg=12, argval=118, argrepr='to 118', offset=104, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=5, argval=1, argrepr='1', offset=106, starts_line=21, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=8, argval=0, argrepr='0', offset=108, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BINARY_TRUE_DIVIDE', opcode=27, arg=Tupu, argval=Tupu, argrepr='', offset=110, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=112, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Tupu, argval=Tupu, argrepr='', offset=114, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_FORWARD', opcode=110, arg=28, argval=146, argrepr='to 146', offset=116, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='DUP_TOP', opcode=4, arg=Tupu, argval=Tupu, argrepr='', offset=118, starts_line=22, is_jump_target=Kweli),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=2, argval='ZeroDivisionError', argrepr='ZeroDivisionError', offset=120, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='COMPARE_OP', opcode=107, arg=10, argval='exception match', argrepr='exception match', offset=122, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, arg=144, argval=144, argrepr='', offset=124, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=126, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=128, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=130, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=132, starts_line=23, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=9, argval='Here we go, here we go, here we go...', argrepr="'Here we go, here we go, here we go...'", offset=134, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=136, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=138, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_EXCEPT', opcode=89, arg=Tupu, argval=Tupu, argrepr='', offset=140, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='JUMP_FORWARD', opcode=110, arg=26, argval=170, argrepr='to 170', offset=142, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='END_FINALLY', opcode=88, arg=Tupu, argval=Tupu, argrepr='', offset=144, starts_line=Tupu, is_jump_target=Kweli),
  Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='i', argrepr='i', offset=146, starts_line=25, is_jump_target=Kweli),
  Instruction(opname='SETUP_WITH', opcode=143, arg=14, argval=164, argrepr='to 164', offset=148, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='STORE_FAST', opcode=125, arg=1, argval='dodgy', argrepr='dodgy', offset=150, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=152, starts_line=26, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=10, argval='Never reach this', argrepr="'Never reach this'", offset=154, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=156, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=158, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Tupu, argval=Tupu, argrepr='', offset=160, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='BEGIN_FINALLY', opcode=53, arg=Tupu, argval=Tupu, argrepr='', offset=162, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='WITH_CLEANUP_START', opcode=81, arg=Tupu, argval=Tupu, argrepr='', offset=164, starts_line=Tupu, is_jump_target=Kweli),
  Instruction(opname='WITH_CLEANUP_FINISH', opcode=82, arg=Tupu, argval=Tupu, argrepr='', offset=166, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='END_FINALLY', opcode=88, arg=Tupu, argval=Tupu, argrepr='', offset=168, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_BLOCK', opcode=87, arg=Tupu, argval=Tupu, argrepr='', offset=170, starts_line=Tupu, is_jump_target=Kweli),
  Instruction(opname='BEGIN_FINALLY', opcode=53, arg=Tupu, argval=Tupu, argrepr='', offset=172, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_GLOBAL', opcode=116, arg=1, argval='print', argrepr='print', offset=174, starts_line=28, is_jump_target=Kweli),
  Instruction(opname='LOAD_CONST', opcode=100, arg=7, argval="OK, now we're done", argrepr='"OK, now we\'re done"', offset=176, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=178, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='POP_TOP', opcode=1, arg=Tupu, argval=Tupu, argrepr='', offset=180, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='END_FINALLY', opcode=88, arg=Tupu, argval=Tupu, argrepr='', offset=182, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Tupu, argrepr='Tupu', offset=184, starts_line=Tupu, is_jump_target=Uongo),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Tupu, argval=Tupu, argrepr='', offset=186, starts_line=Tupu, is_jump_target=Uongo),
]

# One last piece of inspect fodder to check the default line number handling
eleza simple(): pita
expected_opinfo_simple = [
  Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=Tupu, argrepr='Tupu', offset=0, starts_line=simple.__code__.co_firstlineno, is_jump_target=Uongo),
  Instruction(opname='RETURN_VALUE', opcode=83, arg=Tupu, argval=Tupu, argrepr='', offset=2, starts_line=Tupu, is_jump_target=Uongo)
]


kundi InstructionTests(BytecodeTestCase):

    eleza test_default_first_line(self):
        actual = dis.get_instructions(simple)
        self.assertEqual(list(actual), expected_opinfo_simple)

    eleza test_first_line_set_to_Tupu(self):
        actual = dis.get_instructions(simple, first_line=Tupu)
        self.assertEqual(list(actual), expected_opinfo_simple)

    eleza test_outer(self):
        actual = dis.get_instructions(outer, first_line=expected_outer_line)
        self.assertEqual(list(actual), expected_opinfo_outer)

    eleza test_nested(self):
        with captured_stdout():
            f = outer()
        actual = dis.get_instructions(f, first_line=expected_f_line)
        self.assertEqual(list(actual), expected_opinfo_f)

    eleza test_doubly_nested(self):
        with captured_stdout():
            inner = outer()()
        actual = dis.get_instructions(inner, first_line=expected_inner_line)
        self.assertEqual(list(actual), expected_opinfo_inner)

    eleza test_jumpy(self):
        actual = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
        self.assertEqual(list(actual), expected_opinfo_jumpy)

# get_instructions has its own tests above, so can rely on it to validate
# the object oriented API
kundi BytecodeTests(unittest.TestCase):
    eleza test_instantiation(self):
        # Test with function, method, code string na code object
        kila obj kwenye [_f, _C(1).__init__, "a=1", _f.__code__]:
            with self.subTest(obj=obj):
                b = dis.Bytecode(obj)
                self.assertIsInstance(b.codeobj, types.CodeType)

        self.assertRaises(TypeError, dis.Bytecode, object())

    eleza test_iteration(self):
        kila obj kwenye [_f, _C(1).__init__, "a=1", _f.__code__]:
            with self.subTest(obj=obj):
                via_object = list(dis.Bytecode(obj))
                via_generator = list(dis.get_instructions(obj))
                self.assertEqual(via_object, via_generator)

    eleza test_explicit_first_line(self):
        actual = dis.Bytecode(outer, first_line=expected_outer_line)
        self.assertEqual(list(actual), expected_opinfo_outer)

    eleza test_source_line_in_disassembly(self):
        # Use the line kwenye the source code
        actual = dis.Bytecode(simple).dis()
        actual = actual.strip().partition(" ")[0]  # extract the line no
        expected = str(simple.__code__.co_firstlineno)
        self.assertEqual(actual, expected)
        # Use an explicit first line number
        actual = dis.Bytecode(simple, first_line=350).dis()
        actual = actual.strip().partition(" ")[0]  # extract the line no
        self.assertEqual(actual, "350")

    eleza test_info(self):
        self.maxDiff = 1000
        kila x, expected kwenye CodeInfoTests.test_pairs:
            b = dis.Bytecode(x)
            self.assertRegex(b.info(), expected)

    eleza test_disassembled(self):
        actual = dis.Bytecode(_f).dis()
        self.assertEqual(actual, dis_f)

    eleza test_kutoka_traceback(self):
        tb = get_tb()
        b = dis.Bytecode.kutoka_traceback(tb)
        wakati tb.tb_next: tb = tb.tb_next

        self.assertEqual(b.current_offset, tb.tb_lasti)

    eleza test_kutoka_traceback_dis(self):
        tb = get_tb()
        b = dis.Bytecode.kutoka_traceback(tb)
        self.assertEqual(b.dis(), dis_traceback)

ikiwa __name__ == "__main__":
    unittest.main()
