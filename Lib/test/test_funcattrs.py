agiza types
agiza unittest


eleza global_function():
    eleza inner_function():
        kundi LocalClass:
            pita
        global inner_global_function
        eleza inner_global_function():
            eleza inner_function2():
                pita
            rudisha inner_function2
        rudisha LocalClass
    rudisha lambda: inner_function


kundi FuncAttrsTest(unittest.TestCase):
    eleza setUp(self):
        kundi F:
            eleza a(self):
                pita
        eleza b():
            rudisha 3
        self.fi = F()
        self.F = F
        self.b = b

    eleza cannot_set_attr(self, obj, name, value, exceptions):
        jaribu:
            setattr(obj, name, value)
        tatizo exceptions:
            pita
        isipokua:
            self.fail("shouldn't be able to set %s to %r" % (name, value))
        jaribu:
            delattr(obj, name)
        tatizo exceptions:
            pita
        isipokua:
            self.fail("shouldn't be able to toa %s" % name)


kundi FunctionPropertiesTest(FuncAttrsTest):
    # Include the external setUp method that ni common to all tests
    eleza test_module(self):
        self.assertEqual(self.b.__module__, __name__)

    eleza test_dir_includes_correct_attrs(self):
        self.b.known_attr = 7
        self.assertIn('known_attr', dir(self.b),
            "set attributes haiko kwenye dir listing of method")
        # Test on underlying function object of method
        self.F.a.known_attr = 7
        self.assertIn('known_attr', dir(self.fi.a), "set attribute on function "
                     "implementations, should show up kwenye next dir")

    eleza test_duplicate_function_equality(self):
        # Body of `duplicate' ni the exact same kama self.b
        eleza duplicate():
            'my docstring'
            rudisha 3
        self.assertNotEqual(self.b, duplicate)

    eleza test_copying___code__(self):
        eleza test(): pita
        self.assertEqual(test(), Tupu)
        test.__code__ = self.b.__code__
        self.assertEqual(test(), 3) # self.b always rudishas 3, arbitrarily

    eleza test___globals__(self):
        self.assertIs(self.b.__globals__, globals())
        self.cannot_set_attr(self.b, '__globals__', 2,
                             (AttributeError, TypeError))

    eleza test___closure__(self):
        a = 12
        eleza f(): andika(a)
        c = f.__closure__
        self.assertIsInstance(c, tuple)
        self.assertEqual(len(c), 1)
        # don't have a type object handy
        self.assertEqual(c[0].__class__.__name__, "cell")
        self.cannot_set_attr(f, "__closure__", c, AttributeError)

    eleza test_cell_new(self):
        cell_obj = types.CellType(1)
        self.assertEqual(cell_obj.cell_contents, 1)

        cell_obj = types.CellType()
        msg = "shouldn't be able to read an empty cell"
        with self.assertRaises(ValueError, msg=msg):
            cell_obj.cell_contents

    eleza test_empty_cell(self):
        eleza f(): andika(a)
        jaribu:
            f.__closure__[0].cell_contents
        tatizo ValueError:
            pita
        isipokua:
            self.fail("shouldn't be able to read an empty cell")
        a = 12

    eleza test_set_cell(self):
        a = 12
        eleza f(): rudisha a
        c = f.__closure__
        c[0].cell_contents = 9
        self.assertEqual(c[0].cell_contents, 9)
        self.assertEqual(f(), 9)
        self.assertEqual(a, 9)
        toa c[0].cell_contents
        jaribu:
            c[0].cell_contents
        tatizo ValueError:
            pita
        isipokua:
            self.fail("shouldn't be able to read an empty cell")
        with self.assertRaises(NameError):
            f()
        with self.assertRaises(UnboundLocalError):
            andika(a)

    eleza test___name__(self):
        self.assertEqual(self.b.__name__, 'b')
        self.b.__name__ = 'c'
        self.assertEqual(self.b.__name__, 'c')
        self.b.__name__ = 'd'
        self.assertEqual(self.b.__name__, 'd')
        # __name__ na __name__ must be a string
        self.cannot_set_attr(self.b, '__name__', 7, TypeError)
        # __name__ must be available when kwenye restricted mode. Exec will ashiria
        # AttributeError ikiwa __name__ ni sio available on f.
        s = """eleza f(): pita\nf.__name__"""
        exec(s, {'__builtins__': {}})
        # Test on methods, too
        self.assertEqual(self.fi.a.__name__, 'a')
        self.cannot_set_attr(self.fi.a, "__name__", 'a', AttributeError)

    eleza test___qualname__(self):
        # PEP 3155
        self.assertEqual(self.b.__qualname__, 'FuncAttrsTest.setUp.<locals>.b')
        self.assertEqual(FuncAttrsTest.setUp.__qualname__, 'FuncAttrsTest.setUp')
        self.assertEqual(global_function.__qualname__, 'global_function')
        self.assertEqual(global_function().__qualname__,
                         'global_function.<locals>.<lambda>')
        self.assertEqual(global_function()().__qualname__,
                         'global_function.<locals>.inner_function')
        self.assertEqual(global_function()()().__qualname__,
                         'global_function.<locals>.inner_function.<locals>.LocalClass')
        self.assertEqual(inner_global_function.__qualname__, 'inner_global_function')
        self.assertEqual(inner_global_function().__qualname__, 'inner_global_function.<locals>.inner_function2')
        self.b.__qualname__ = 'c'
        self.assertEqual(self.b.__qualname__, 'c')
        self.b.__qualname__ = 'd'
        self.assertEqual(self.b.__qualname__, 'd')
        # __qualname__ must be a string
        self.cannot_set_attr(self.b, '__qualname__', 7, TypeError)

    eleza test___code__(self):
        num_one, num_two = 7, 8
        eleza a(): pita
        eleza b(): rudisha 12
        eleza c(): rudisha num_one
        eleza d(): rudisha num_two
        eleza e(): rudisha num_one, num_two
        kila func kwenye [a, b, c, d, e]:
            self.assertEqual(type(func.__code__), types.CodeType)
        self.assertEqual(c(), 7)
        self.assertEqual(d(), 8)
        d.__code__ = c.__code__
        self.assertEqual(c.__code__, d.__code__)
        self.assertEqual(c(), 7)
        # self.assertEqual(d(), 7)
        jaribu:
            b.__code__ = c.__code__
        tatizo ValueError:
            pita
        isipokua:
            self.fail("__code__ with different numbers of free vars should "
                      "not be possible")
        jaribu:
            e.__code__ = d.__code__
        tatizo ValueError:
            pita
        isipokua:
            self.fail("__code__ with different numbers of free vars should "
                      "not be possible")

    eleza test_blank_func_defaults(self):
        self.assertEqual(self.b.__defaults__, Tupu)
        toa self.b.__defaults__
        self.assertEqual(self.b.__defaults__, Tupu)

    eleza test_func_default_args(self):
        eleza first_func(a, b):
            rudisha a+b
        eleza second_func(a=1, b=2):
            rudisha a+b
        self.assertEqual(first_func.__defaults__, Tupu)
        self.assertEqual(second_func.__defaults__, (1, 2))
        first_func.__defaults__ = (1, 2)
        self.assertEqual(first_func.__defaults__, (1, 2))
        self.assertEqual(first_func(), 3)
        self.assertEqual(first_func(3), 5)
        self.assertEqual(first_func(3, 5), 8)
        toa second_func.__defaults__
        self.assertEqual(second_func.__defaults__, Tupu)
        jaribu:
            second_func()
        tatizo TypeError:
            pita
        isipokua:
            self.fail("__defaults__ does sio update; deleting it does sio "
                      "remove requirement")


kundi InstancemethodAttrTest(FuncAttrsTest):

    eleza test___class__(self):
        self.assertEqual(self.fi.a.__self__.__class__, self.F)
        self.cannot_set_attr(self.fi.a, "__class__", self.F, TypeError)

    eleza test___func__(self):
        self.assertEqual(self.fi.a.__func__, self.F.a)
        self.cannot_set_attr(self.fi.a, "__func__", self.F.a, AttributeError)

    eleza test___self__(self):
        self.assertEqual(self.fi.a.__self__, self.fi)
        self.cannot_set_attr(self.fi.a, "__self__", self.fi, AttributeError)

    eleza test___func___non_method(self):
        # Behavior should be the same when a method ni added via an attr
        # assignment
        self.fi.id = types.MethodType(id, self.fi)
        self.assertEqual(self.fi.id(), id(self.fi))
        # Test usage
        jaribu:
            self.fi.id.unknown_attr
        tatizo AttributeError:
            pita
        isipokua:
            self.fail("using unknown attributes should ashiria AttributeError")
        # Test assignment na deletion
        self.cannot_set_attr(self.fi.id, 'unknown_attr', 2, AttributeError)


kundi ArbitraryFunctionAttrTest(FuncAttrsTest):
    eleza test_set_attr(self):
        self.b.known_attr = 7
        self.assertEqual(self.b.known_attr, 7)
        jaribu:
            self.fi.a.known_attr = 7
        tatizo AttributeError:
            pita
        isipokua:
            self.fail("setting attributes on methods should ashiria error")

    eleza test_delete_unknown_attr(self):
        jaribu:
            toa self.b.unknown_attr
        tatizo AttributeError:
            pita
        isipokua:
            self.fail("deleting unknown attribute should ashiria TypeError")

    eleza test_unset_attr(self):
        kila func kwenye [self.b, self.fi.a]:
            jaribu:
                func.non_existent_attr
            tatizo AttributeError:
                pita
            isipokua:
                self.fail("using unknown attributes should ashiria "
                          "AttributeError")


kundi FunctionDictsTest(FuncAttrsTest):
    eleza test_setting_dict_to_invalid(self):
        self.cannot_set_attr(self.b, '__dict__', Tupu, TypeError)
        kutoka collections agiza UserDict
        d = UserDict({'known_attr': 7})
        self.cannot_set_attr(self.fi.a.__func__, '__dict__', d, TypeError)

    eleza test_setting_dict_to_valid(self):
        d = {'known_attr': 7}
        self.b.__dict__ = d
        # Test assignment
        self.assertIs(d, self.b.__dict__)
        # ... na on all the different ways of referencing the method's func
        self.F.a.__dict__ = d
        self.assertIs(d, self.fi.a.__func__.__dict__)
        self.assertIs(d, self.fi.a.__dict__)
        # Test value
        self.assertEqual(self.b.known_attr, 7)
        self.assertEqual(self.b.__dict__['known_attr'], 7)
        # ... na again, on all the different method's names
        self.assertEqual(self.fi.a.__func__.known_attr, 7)
        self.assertEqual(self.fi.a.known_attr, 7)

    eleza test_delete___dict__(self):
        jaribu:
            toa self.b.__dict__
        tatizo TypeError:
            pita
        isipokua:
            self.fail("deleting function dictionary should ashiria TypeError")

    eleza test_unassigned_dict(self):
        self.assertEqual(self.b.__dict__, {})

    eleza test_func_as_dict_key(self):
        value = "Some string"
        d = {}
        d[self.b] = value
        self.assertEqual(d[self.b], value)


kundi FunctionDocstringTest(FuncAttrsTest):
    eleza test_set_docstring_attr(self):
        self.assertEqual(self.b.__doc__, Tupu)
        docstr = "A test method that does nothing"
        self.b.__doc__ = docstr
        self.F.a.__doc__ = docstr
        self.assertEqual(self.b.__doc__, docstr)
        self.assertEqual(self.fi.a.__doc__, docstr)
        self.cannot_set_attr(self.fi.a, "__doc__", docstr, AttributeError)

    eleza test_delete_docstring(self):
        self.b.__doc__ = "The docstring"
        toa self.b.__doc__
        self.assertEqual(self.b.__doc__, Tupu)


eleza cell(value):
    """Create a cell containing the given value."""
    eleza f():
        andika(a)
    a = value
    rudisha f.__closure__[0]

eleza empty_cell(empty=Kweli):
    """Create an empty cell."""
    eleza f():
        andika(a)
    # the intent of the following line ni simply "ikiwa Uongo:";  it's
    # spelt this way to avoid the danger that a future optimization
    # might simply remove an "ikiwa Uongo:" code block.
    ikiwa sio empty:
        a = 1729
    rudisha f.__closure__[0]


kundi CellTest(unittest.TestCase):
    eleza test_comparison(self):
        # These tests are here simply to exercise the comparison code;
        # their presence should sio be interpreted kama providing any
        # guarantees about the semantics (or even existence) of cell
        # comparisons kwenye future versions of CPython.
        self.assertKweli(cell(2) < cell(3))
        self.assertKweli(empty_cell() < cell('saturday'))
        self.assertKweli(empty_cell() == empty_cell())
        self.assertKweli(cell(-36) == cell(-36.0))
        self.assertKweli(cell(Kweli) > empty_cell())


kundi StaticMethodAttrsTest(unittest.TestCase):
    eleza test_func_attribute(self):
        eleza f():
            pita

        c = classmethod(f)
        self.assertKweli(c.__func__ ni f)

        s = staticmethod(f)
        self.assertKweli(s.__func__ ni f)


kundi BuiltinFunctionPropertiesTest(unittest.TestCase):
    # XXX Not sure where this should really go since I can't find a
    # test module specifically kila builtin_function_or_method.

    eleza test_builtin__qualname__(self):
        agiza time

        # builtin function:
        self.assertEqual(len.__qualname__, 'len')
        self.assertEqual(time.time.__qualname__, 'time')

        # builtin classmethod:
        self.assertEqual(dict.kutokakeys.__qualname__, 'dict.kutokakeys')
        self.assertEqual(float.__getformat__.__qualname__,
                         'float.__getformat__')

        # builtin staticmethod:
        self.assertEqual(str.maketrans.__qualname__, 'str.maketrans')
        self.assertEqual(bytes.maketrans.__qualname__, 'bytes.maketrans')

        # builtin bound instance method:
        self.assertEqual([1, 2, 3].append.__qualname__, 'list.append')
        self.assertEqual({'foo': 'bar'}.pop.__qualname__, 'dict.pop')


ikiwa __name__ == "__main__":
    unittest.main()
