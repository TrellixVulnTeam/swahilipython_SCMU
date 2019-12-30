agiza os
agiza unittest

GLOBAL_VAR = Tupu

kundi NamedExpressionInvalidTest(unittest.TestCase):

    eleza test_named_expression_invalid_01(self):
        code = """x := 0"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_02(self):
        code = """x = y := 0"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_03(self):
        code = """y := f(x)"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_04(self):
        code = """y0 = y1 := f(x)"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_06(self):
        code = """((a, b) := (1, 2))"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "cannot use named assignment ukijumuisha tuple"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_07(self):
        code = """eleza spam(a = b := 42): pass"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_08(self):
        code = """eleza spam(a: b := 42 = 5): pass"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_09(self):
        code = """spam(a=b := 'c')"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_10(self):
        code = """spam(x = y := f(x))"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_11(self):
        code = """spam(a=1, b := 2)"""

        ukijumuisha self.assertRaisesRegex(SyntaxError,
            "positional argument follows keyword argument"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_12(self):
        code = """spam(a=1, (b := 2))"""

        ukijumuisha self.assertRaisesRegex(SyntaxError,
            "positional argument follows keyword argument"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_13(self):
        code = """spam(a=1, (b := 2))"""

        ukijumuisha self.assertRaisesRegex(SyntaxError,
            "positional argument follows keyword argument"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_14(self):
        code = """(x := lambda: y := 1)"""

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_15(self):
        code = """(lambda: x := 1)"""

        ukijumuisha self.assertRaisesRegex(SyntaxError,
            "cannot use named assignment ukijumuisha lambda"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_16(self):
        code = "[i + 1 kila i kwenye i := [1,2]]"

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_17(self):
        code = "[i := 0, j := 1 kila i, j kwenye [(1, 2), (3, 4)]]"

        ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_in_class_body(self):
        code = """kundi Foo():
            [(42, 1 + ((( j := i )))) kila i kwenye range(5)]
        """

        ukijumuisha self.assertRaisesRegex(SyntaxError,
            "assignment expression within a comprehension cannot be used kwenye a kundi body"):
            exec(code, {}, {})

    eleza test_named_expression_invalid_rebinding_comprehension_iteration_variable(self):
        cases = [
            ("Local reuse", 'i', "[i := 0 kila i kwenye range(5)]"),
            ("Nested reuse", 'j', "[[(j := 0) kila i kwenye range(5)] kila j kwenye range(5)]"),
            ("Reuse inner loop target", 'j', "[(j := 0) kila i kwenye range(5) kila j kwenye range(5)]"),
            ("Unpacking reuse", 'i', "[i := 0 kila i, j kwenye [(0, 1)]]"),
            ("Reuse kwenye loop condition", 'i', "[i+1 kila i kwenye range(5) ikiwa (i := 0)]"),
            ("Unreachable reuse", 'i', "[Uongo ama (i:=0) kila i kwenye range(5)]"),
            ("Unreachable nested reuse", 'i',
                "[(i, j) kila i kwenye range(5) kila j kwenye range(5) ikiwa Kweli ama (i:=10)]"),
        ]
        kila case, target, code kwenye cases:
            msg = f"assignment expression cannot rebind comprehension iteration variable '{target}'"
            ukijumuisha self.subTest(case=case):
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(code, {}, {})

    eleza test_named_expression_invalid_rebinding_comprehension_inner_loop(self):
        cases = [
            ("Inner reuse", 'j', "[i kila i kwenye range(5) ikiwa (j := 0) kila j kwenye range(5)]"),
            ("Inner unpacking reuse", 'j', "[i kila i kwenye range(5) ikiwa (j := 0) kila j, k kwenye [(0, 1)]]"),
        ]
        kila case, target, code kwenye cases:
            msg = f"comprehension inner loop cannot rebind assignment expression target '{target}'"
            ukijumuisha self.subTest(case=case):
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(code, {}) # Module scope
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(code, {}, {}) # Class scope
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(f"lambda: {code}", {}) # Function scope

    eleza test_named_expression_invalid_comprehension_iterable_expression(self):
        cases = [
            ("Top level", "[i kila i kwenye (i := range(5))]"),
            ("Inside tuple", "[i kila i kwenye (2, 3, i := range(5))]"),
            ("Inside list", "[i kila i kwenye [2, 3, i := range(5)]]"),
            ("Different name", "[i kila i kwenye (j := range(5))]"),
            ("Lambda expression", "[i kila i kwenye (lambda:(j := range(5)))()]"),
            ("Inner loop", "[i kila i kwenye range(5) kila j kwenye (i := range(5))]"),
            ("Nested comprehension", "[i kila i kwenye [j kila j kwenye (k := range(5))]]"),
            ("Nested comprehension condition", "[i kila i kwenye [j kila j kwenye range(5) ikiwa (j := Kweli)]]"),
            ("Nested comprehension body", "[i kila i kwenye [(j := Kweli) kila j kwenye range(5)]]"),
        ]
        msg = "assignment expression cannot be used kwenye a comprehension iterable expression"
        kila case, code kwenye cases:
            ukijumuisha self.subTest(case=case):
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(code, {}) # Module scope
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(code, {}, {}) # Class scope
                ukijumuisha self.assertRaisesRegex(SyntaxError, msg):
                    exec(f"lambda: {code}", {}) # Function scope


kundi NamedExpressionAssignmentTest(unittest.TestCase):

    eleza test_named_expression_assignment_01(self):
        (a := 10)

        self.assertEqual(a, 10)

    eleza test_named_expression_assignment_02(self):
        a = 20
        (a := a)

        self.assertEqual(a, 20)

    eleza test_named_expression_assignment_03(self):
        (total := 1 + 2)

        self.assertEqual(total, 3)

    eleza test_named_expression_assignment_04(self):
        (info := (1, 2, 3))

        self.assertEqual(info, (1, 2, 3))

    eleza test_named_expression_assignment_05(self):
        (x := 1, 2)

        self.assertEqual(x, 1)

    eleza test_named_expression_assignment_06(self):
        (z := (y := (x := 0)))

        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(z, 0)

    eleza test_named_expression_assignment_07(self):
        (loc := (1, 2))

        self.assertEqual(loc, (1, 2))

    eleza test_named_expression_assignment_08(self):
        ikiwa spam := "eggs":
            self.assertEqual(spam, "eggs")
        isipokua: self.fail("variable was sio assigned using named expression")

    eleza test_named_expression_assignment_09(self):
        ikiwa Kweli na (spam := Kweli):
            self.assertKweli(spam)
        isipokua: self.fail("variable was sio assigned using named expression")

    eleza test_named_expression_assignment_10(self):
        ikiwa (match := 10) == 10:
            pass
        isipokua: self.fail("variable was sio assigned using named expression")

    eleza test_named_expression_assignment_11(self):
        eleza spam(a):
            rudisha a
        input_data = [1, 2, 3]
        res = [(x, y, x/y) kila x kwenye input_data ikiwa (y := spam(x)) > 0]

        self.assertEqual(res, [(1, 1, 1.0), (2, 2, 1.0), (3, 3, 1.0)])

    eleza test_named_expression_assignment_12(self):
        eleza spam(a):
            rudisha a
        res = [[y := spam(x), x/y] kila x kwenye range(1, 5)]

        self.assertEqual(res, [[1, 1.0], [2, 1.0], [3, 1.0], [4, 1.0]])

    eleza test_named_expression_assignment_13(self):
        length = len(lines := [1, 2])

        self.assertEqual(length, 2)
        self.assertEqual(lines, [1,2])

    eleza test_named_expression_assignment_14(self):
        """
        Where all variables are positive integers, na a ni at least as large
        as the n'th root of x, this algorithm returns the floor of the n'th
        root of x (and roughly doubling the number of accurate bits per
        iteration):
        """
        a = 9
        n = 2
        x = 3

        wakati a > (d := x // a**(n-1)):
            a = ((n-1)*a + d) // n

        self.assertEqual(a, 1)

    eleza test_named_expression_assignment_15(self):
        wakati a := Uongo:
            pass  # This will sio run

        self.assertEqual(a, Uongo)

    eleza test_named_expression_assignment_16(self):
        a, b = 1, 2
        fib = {(c := a): (a := b) + (b := a + c) - b kila __ kwenye range(6)}
        self.assertEqual(fib, {1: 2, 2: 3, 3: 5, 5: 8, 8: 13, 13: 21})


kundi NamedExpressionScopeTest(unittest.TestCase):

    eleza test_named_expression_scope_01(self):
        code = """eleza spam():
    (a := 5)
andika(a)"""

        ukijumuisha self.assertRaisesRegex(NameError, "name 'a' ni sio defined"):
            exec(code, {}, {})

    eleza test_named_expression_scope_02(self):
        total = 0
        partial_sums = [total := total + v kila v kwenye range(5)]

        self.assertEqual(partial_sums, [0, 1, 3, 6, 10])
        self.assertEqual(total, 10)

    eleza test_named_expression_scope_03(self):
        containsOne = any((lastNum := num) == 1 kila num kwenye [1, 2, 3])

        self.assertKweli(containsOne)
        self.assertEqual(lastNum, 1)

    eleza test_named_expression_scope_04(self):
        eleza spam(a):
            rudisha a
        res = [[y := spam(x), x/y] kila x kwenye range(1, 5)]

        self.assertEqual(y, 4)

    eleza test_named_expression_scope_05(self):
        eleza spam(a):
            rudisha a
        input_data = [1, 2, 3]
        res = [(x, y, x/y) kila x kwenye input_data ikiwa (y := spam(x)) > 0]

        self.assertEqual(res, [(1, 1, 1.0), (2, 2, 1.0), (3, 3, 1.0)])
        self.assertEqual(y, 3)

    eleza test_named_expression_scope_06(self):
        res = [[spam := i kila i kwenye range(3)] kila j kwenye range(2)]

        self.assertEqual(res, [[0, 1, 2], [0, 1, 2]])
        self.assertEqual(spam, 2)

    eleza test_named_expression_scope_07(self):
        len(lines := [1, 2])

        self.assertEqual(lines, [1, 2])

    eleza test_named_expression_scope_08(self):
        eleza spam(a):
            rudisha a

        eleza eggs(b):
            rudisha b * 2

        res = [spam(a := eggs(b := h)) kila h kwenye range(2)]

        self.assertEqual(res, [0, 2])
        self.assertEqual(a, 2)
        self.assertEqual(b, 1)

    eleza test_named_expression_scope_09(self):
        eleza spam(a):
            rudisha a

        eleza eggs(b):
            rudisha b * 2

        res = [spam(a := eggs(a := h)) kila h kwenye range(2)]

        self.assertEqual(res, [0, 2])
        self.assertEqual(a, 2)

    eleza test_named_expression_scope_10(self):
        res = [b := [a := 1 kila i kwenye range(2)] kila j kwenye range(2)]

        self.assertEqual(res, [[1, 1], [1, 1]])
        self.assertEqual(a, 1)
        self.assertEqual(b, [1, 1])

    eleza test_named_expression_scope_11(self):
        res = [j := i kila i kwenye range(5)]

        self.assertEqual(res, [0, 1, 2, 3, 4])
        self.assertEqual(j, 4)

    eleza test_named_expression_scope_17(self):
        b = 0
        res = [b := i + b kila i kwenye range(5)]

        self.assertEqual(res, [0, 1, 3, 6, 10])
        self.assertEqual(b, 10)

    eleza test_named_expression_scope_18(self):
        eleza spam(a):
            rudisha a

        res = spam(b := 2)

        self.assertEqual(res, 2)
        self.assertEqual(b, 2)

    eleza test_named_expression_scope_19(self):
        eleza spam(a):
            rudisha a

        res = spam((b := 2))

        self.assertEqual(res, 2)
        self.assertEqual(b, 2)

    eleza test_named_expression_scope_20(self):
        eleza spam(a):
            rudisha a

        res = spam(a=(b := 2))

        self.assertEqual(res, 2)
        self.assertEqual(b, 2)

    eleza test_named_expression_scope_21(self):
        eleza spam(a, b):
            rudisha a + b

        res = spam(c := 2, b=1)

        self.assertEqual(res, 3)
        self.assertEqual(c, 2)

    eleza test_named_expression_scope_22(self):
        eleza spam(a, b):
            rudisha a + b

        res = spam((c := 2), b=1)

        self.assertEqual(res, 3)
        self.assertEqual(c, 2)

    eleza test_named_expression_scope_23(self):
        eleza spam(a, b):
            rudisha a + b

        res = spam(b=(c := 2), a=1)

        self.assertEqual(res, 3)
        self.assertEqual(c, 2)

    eleza test_named_expression_scope_24(self):
        a = 10
        eleza spam():
            nonlocal a
            (a := 20)
        spam()

        self.assertEqual(a, 20)

    eleza test_named_expression_scope_25(self):
        ns = {}
        code = """a = 10
eleza spam():
    global a
    (a := 20)
spam()"""

        exec(code, ns, {})

        self.assertEqual(ns["a"], 20)

    eleza test_named_expression_variable_reuse_in_comprehensions(self):
        # The compiler ni expected to  ashiria syntax error kila comprehension
        # iteration variables, but should be fine ukijumuisha rebinding of other
        # names (e.g. globals, nonlocals, other assignment expressions)

        # The cases are all defined to produce the same expected result
        # Each comprehension ni checked at both function scope na module scope
        rebinding = "[x := i kila i kwenye range(3) ikiwa (x := i) ama sio x]"
        filter_ref = "[x := i kila i kwenye range(3) ikiwa x ama sio x]"
        body_ref = "[x kila i kwenye range(3) ikiwa (x := i) ama sio x]"
        nested_ref = "[j kila i kwenye range(3) ikiwa x ama sio x kila j kwenye range(3) ikiwa (x := i)][:-3]"
        cases = [
            ("Rebind global", f"x = 1; result = {rebinding}"),
            ("Rebind nonlocal", f"result, x = (lambda x=1: ({rebinding}, x))()"),
            ("Filter global", f"x = 1; result = {filter_ref}"),
            ("Filter nonlocal", f"result, x = (lambda x=1: ({filter_ref}, x))()"),
            ("Body global", f"x = 1; result = {body_ref}"),
            ("Body nonlocal", f"result, x = (lambda x=1: ({body_ref}, x))()"),
            ("Nested global", f"x = 1; result = {nested_ref}"),
            ("Nested nonlocal", f"result, x = (lambda x=1: ({nested_ref}, x))()"),
        ]
        kila case, code kwenye cases:
            ukijumuisha self.subTest(case=case):
                ns = {}
                exec(code, ns)
                self.assertEqual(ns["x"], 2)
                self.assertEqual(ns["result"], [0, 1, 2])

    eleza test_named_expression_global_scope(self):
        sentinel = object()
        global GLOBAL_VAR
        eleza f():
            global GLOBAL_VAR
            [GLOBAL_VAR := sentinel kila _ kwenye range(1)]
            self.assertEqual(GLOBAL_VAR, sentinel)
        jaribu:
            f()
            self.assertEqual(GLOBAL_VAR, sentinel)
        mwishowe:
            GLOBAL_VAR = Tupu

    eleza test_named_expression_global_scope_no_global_keyword(self):
        sentinel = object()
        eleza f():
            GLOBAL_VAR = Tupu
            [GLOBAL_VAR := sentinel kila _ kwenye range(1)]
            self.assertEqual(GLOBAL_VAR, sentinel)
        f()
        self.assertEqual(GLOBAL_VAR, Tupu)

    eleza test_named_expression_nonlocal_scope(self):
        sentinel = object()
        eleza f():
            nonlocal_var = Tupu
            eleza g():
                nonlocal nonlocal_var
                [nonlocal_var := sentinel kila _ kwenye range(1)]
            g()
            self.assertEqual(nonlocal_var, sentinel)
        f()

    eleza test_named_expression_nonlocal_scope_no_nonlocal_keyword(self):
        sentinel = object()
        eleza f():
            nonlocal_var = Tupu
            eleza g():
                [nonlocal_var := sentinel kila _ kwenye range(1)]
            g()
            self.assertEqual(nonlocal_var, Tupu)
        f()


ikiwa __name__ == "__main__":
    unittest.main()
