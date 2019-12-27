# Tests some corner cases with isinstance() and issubclass().  While these
# tests use new style classes and properties, they actually do whitebox
# testing of error conditions uncovered when using extension types.

agiza unittest
agiza sys



kundi TestIsInstanceExceptions(unittest.TestCase):
    # Test to make sure that an AttributeError when accessing the instance's
    # class's bases is masked.  This was actually a bug in Python 2.2 and
    # 2.2.1 where the exception wasn't caught but it also wasn't being cleared
    # (leading to an "undetected error" in the debug build).  Set up is,
    # isinstance(inst, cls) where:
    #
    # - cls isn't a type, or a tuple
    # - cls has a __bases__ attribute
    # - inst has a __class__ attribute
    # - inst.__class__ as no __bases__ attribute
    #
    # Sounds complicated, I know, but this mimics a situation where an
    # extension type raises an AttributeError when its __bases__ attribute is
    # gotten.  In that case, isinstance() should rudisha False.
    eleza test_class_has_no_bases(self):
        kundi I(object):
            eleza getclass(self):
                # This must rudisha an object that has no __bases__ attribute
                rudisha None
            __class__ = property(getclass)

        kundi C(object):
            eleza getbases(self):
                rudisha ()
            __bases__ = property(getbases)

        self.assertEqual(False, isinstance(I(), C()))

    # Like above except that inst.__class__.__bases__ raises an exception
    # other than AttributeError
    eleza test_bases_raises_other_than_attribute_error(self):
        kundi E(object):
            eleza getbases(self):
                raise RuntimeError
            __bases__ = property(getbases)

        kundi I(object):
            eleza getclass(self):
                rudisha E()
            __class__ = property(getclass)

        kundi C(object):
            eleza getbases(self):
                rudisha ()
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, isinstance, I(), C())

    # Here's a situation where getattr(cls, '__bases__') raises an exception.
    # If that exception is not AttributeError, it should not get masked
    eleza test_dont_mask_non_attribute_error(self):
        kundi I: pass

        kundi C(object):
            eleza getbases(self):
                raise RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, isinstance, I(), C())

    # Like above, except that getattr(cls, '__bases__') raises an
    # AttributeError, which /should/ get masked as a TypeError
    eleza test_mask_attribute_error(self):
        kundi I: pass

        kundi C(object):
            eleza getbases(self):
                raise AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, isinstance, I(), C())

    # check that we don't mask non AttributeErrors
    # see: http://bugs.python.org/issue1574217
    eleza test_isinstance_dont_mask_non_attribute_error(self):
        kundi C(object):
            eleza getclass(self):
                raise RuntimeError
            __class__ = property(getclass)

        c = C()
        self.assertRaises(RuntimeError, isinstance, c, bool)

        # test another code path
        kundi D: pass
        self.assertRaises(RuntimeError, isinstance, c, D)


# These tests are similar to above, but tickle certain code paths in
# issubclass() instead of isinstance() -- really PyObject_IsSubclass()
# vs. PyObject_IsInstance().
kundi TestIsSubclassExceptions(unittest.TestCase):
    eleza test_dont_mask_non_attribute_error(self):
        kundi C(object):
            eleza getbases(self):
                raise RuntimeError
            __bases__ = property(getbases)

        kundi S(C): pass

        self.assertRaises(RuntimeError, issubclass, C(), S())

    eleza test_mask_attribute_error(self):
        kundi C(object):
            eleza getbases(self):
                raise AttributeError
            __bases__ = property(getbases)

        kundi S(C): pass

        self.assertRaises(TypeError, issubclass, C(), S())

    # Like above, but test the second branch, where the __bases__ of the
    # second arg (the cls arg) is tested.  This means the first arg must
    # rudisha a valid __bases__, and it's okay for it to be a normal --
    # unrelated by inheritance -- class.
    eleza test_dont_mask_non_attribute_error_in_cls_arg(self):
        kundi B: pass

        kundi C(object):
            eleza getbases(self):
                raise RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, issubclass, B, C())

    eleza test_mask_attribute_error_in_cls_arg(self):
        kundi B: pass

        kundi C(object):
            eleza getbases(self):
                raise AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, issubclass, B, C())



# meta classes for creating abstract classes and instances
kundi AbstractClass(object):
    eleza __init__(self, bases):
        self.bases = bases

    eleza getbases(self):
        rudisha self.bases
    __bases__ = property(getbases)

    eleza __call__(self):
        rudisha AbstractInstance(self)

kundi AbstractInstance(object):
    eleza __init__(self, klass):
        self.klass = klass

    eleza getclass(self):
        rudisha self.klass
    __class__ = property(getclass)

# abstract classes
AbstractSuper = AbstractClass(bases=())

AbstractChild = AbstractClass(bases=(AbstractSuper,))

# normal classes
kundi Super:
    pass

kundi Child(Super):
    pass

kundi TestIsInstanceIsSubclass(unittest.TestCase):
    # Tests to ensure that isinstance and issubkundi work on abstract
    # classes and instances.  Before the 2.2 release, TypeErrors were
    # raised when boolean values should have been returned.  The bug was
    # triggered by mixing 'normal' classes and instances were with
    # 'abstract' classes and instances.  This case tries to test all
    # combinations.

    eleza test_isinstance_normal(self):
        # normal instances
        self.assertEqual(True, isinstance(Super(), Super))
        self.assertEqual(False, isinstance(Super(), Child))
        self.assertEqual(False, isinstance(Super(), AbstractSuper))
        self.assertEqual(False, isinstance(Super(), AbstractChild))

        self.assertEqual(True, isinstance(Child(), Super))
        self.assertEqual(False, isinstance(Child(), AbstractSuper))

    eleza test_isinstance_abstract(self):
        # abstract instances
        self.assertEqual(True, isinstance(AbstractSuper(), AbstractSuper))
        self.assertEqual(False, isinstance(AbstractSuper(), AbstractChild))
        self.assertEqual(False, isinstance(AbstractSuper(), Super))
        self.assertEqual(False, isinstance(AbstractSuper(), Child))

        self.assertEqual(True, isinstance(AbstractChild(), AbstractChild))
        self.assertEqual(True, isinstance(AbstractChild(), AbstractSuper))
        self.assertEqual(False, isinstance(AbstractChild(), Super))
        self.assertEqual(False, isinstance(AbstractChild(), Child))

    eleza test_subclass_normal(self):
        # normal classes
        self.assertEqual(True, issubclass(Super, Super))
        self.assertEqual(False, issubclass(Super, AbstractSuper))
        self.assertEqual(False, issubclass(Super, Child))

        self.assertEqual(True, issubclass(Child, Child))
        self.assertEqual(True, issubclass(Child, Super))
        self.assertEqual(False, issubclass(Child, AbstractSuper))

    eleza test_subclass_abstract(self):
        # abstract classes
        self.assertEqual(True, issubclass(AbstractSuper, AbstractSuper))
        self.assertEqual(False, issubclass(AbstractSuper, AbstractChild))
        self.assertEqual(False, issubclass(AbstractSuper, Child))

        self.assertEqual(True, issubclass(AbstractChild, AbstractChild))
        self.assertEqual(True, issubclass(AbstractChild, AbstractSuper))
        self.assertEqual(False, issubclass(AbstractChild, Super))
        self.assertEqual(False, issubclass(AbstractChild, Child))

    eleza test_subclass_tuple(self):
        # test with a tuple as the second argument classes
        self.assertEqual(True, issubclass(Child, (Child,)))
        self.assertEqual(True, issubclass(Child, (Super,)))
        self.assertEqual(False, issubclass(Super, (Child,)))
        self.assertEqual(True, issubclass(Super, (Child, Super)))
        self.assertEqual(False, issubclass(Child, ()))
        self.assertEqual(True, issubclass(Super, (Child, (Super,))))

        self.assertEqual(True, issubclass(int, (int, (float, int))))
        self.assertEqual(True, issubclass(str, (str, (Child, str))))

    eleza test_subclass_recursion_limit(self):
        # make sure that issubkundi raises RecursionError before the C stack is
        # blown
        self.assertRaises(RecursionError, blowstack, issubclass, str, str)

    eleza test_isinstance_recursion_limit(self):
        # make sure that issubkundi raises RecursionError before the C stack is
        # blown
        self.assertRaises(RecursionError, blowstack, isinstance, '', str)

eleza blowstack(fxn, arg, compare_to):
    # Make sure that calling isinstance with a deeply nested tuple for its
    # argument will raise RecursionError eventually.
    tuple_arg = (compare_to,)
    for cnt in range(sys.getrecursionlimit()+5):
        tuple_arg = (tuple_arg,)
        fxn(arg, tuple_arg)


ikiwa __name__ == '__main__':
    unittest.main()
