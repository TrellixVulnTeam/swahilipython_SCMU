# Tests some corner cases ukijumuisha isinstance() na issubclass().  While these
# tests use new style classes na properties, they actually do whitebox
# testing of error conditions uncovered when using extension types.

agiza unittest
agiza sys



kundi TestIsInstanceExceptions(unittest.TestCase):
    # Test to make sure that an AttributeError when accessing the instance's
    # class's bases ni masked.  This was actually a bug kwenye Python 2.2 na
    # 2.2.1 where the exception wasn't caught but it also wasn't being cleared
    # (leading to an "undetected error" kwenye the debug build).  Set up is,
    # isinstance(inst, cls) where:
    #
    # - cls isn't a type, ama a tuple
    # - cls has a __bases__ attribute
    # - inst has a __class__ attribute
    # - inst.__class__ kama no __bases__ attribute
    #
    # Sounds complicated, I know, but this mimics a situation where an
    # extension type raises an AttributeError when its __bases__ attribute is
    # gotten.  In that case, isinstance() should rudisha Uongo.
    eleza test_class_has_no_bases(self):
        kundi I(object):
            eleza getclass(self):
                # This must rudisha an object that has no __bases__ attribute
                rudisha Tupu
            __class__ = property(getclass)

        kundi C(object):
            eleza getbases(self):
                rudisha ()
            __bases__ = property(getbases)

        self.assertEqual(Uongo, isinstance(I(), C()))

    # Like above tatizo that inst.__class__.__bases__ raises an exception
    # other than AttributeError
    eleza test_bases_raises_other_than_attribute_error(self):
        kundi E(object):
            eleza getbases(self):
                ashiria RuntimeError
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
    # If that exception ni sio AttributeError, it should sio get masked
    eleza test_dont_mask_non_attribute_error(self):
        kundi I: pita

        kundi C(object):
            eleza getbases(self):
                ashiria RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, isinstance, I(), C())

    # Like above, tatizo that getattr(cls, '__bases__') raises an
    # AttributeError, which /should/ get masked kama a TypeError
    eleza test_mask_attribute_error(self):
        kundi I: pita

        kundi C(object):
            eleza getbases(self):
                ashiria AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, isinstance, I(), C())

    # check that we don't mask non AttributeErrors
    # see: http://bugs.python.org/issue1574217
    eleza test_isinstance_dont_mask_non_attribute_error(self):
        kundi C(object):
            eleza getclass(self):
                ashiria RuntimeError
            __class__ = property(getclass)

        c = C()
        self.assertRaises(RuntimeError, isinstance, c, bool)

        # test another code path
        kundi D: pita
        self.assertRaises(RuntimeError, isinstance, c, D)


# These tests are similar to above, but tickle certain code paths kwenye
# issubclass() instead of isinstance() -- really PyObject_IsSubclass()
# vs. PyObject_IsInstance().
kundi TestIsSubclassExceptions(unittest.TestCase):
    eleza test_dont_mask_non_attribute_error(self):
        kundi C(object):
            eleza getbases(self):
                ashiria RuntimeError
            __bases__ = property(getbases)

        kundi S(C): pita

        self.assertRaises(RuntimeError, issubclass, C(), S())

    eleza test_mask_attribute_error(self):
        kundi C(object):
            eleza getbases(self):
                ashiria AttributeError
            __bases__ = property(getbases)

        kundi S(C): pita

        self.assertRaises(TypeError, issubclass, C(), S())

    # Like above, but test the second branch, where the __bases__ of the
    # second arg (the cls arg) ni tested.  This means the first arg must
    # rudisha a valid __bases__, na it's okay kila it to be a normal --
    # unrelated by inheritance -- class.
    eleza test_dont_mask_non_attribute_error_in_cls_arg(self):
        kundi B: pita

        kundi C(object):
            eleza getbases(self):
                ashiria RuntimeError
            __bases__ = property(getbases)

        self.assertRaises(RuntimeError, issubclass, B, C())

    eleza test_mask_attribute_error_in_cls_arg(self):
        kundi B: pita

        kundi C(object):
            eleza getbases(self):
                ashiria AttributeError
            __bases__ = property(getbases)

        self.assertRaises(TypeError, issubclass, B, C())



# meta classes kila creating abstract classes na instances
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
    pita

kundi Child(Super):
    pita

kundi TestIsInstanceIsSubclass(unittest.TestCase):
    # Tests to ensure that isinstance na issubkundi work on abstract
    # classes na instances.  Before the 2.2 release, TypeErrors were
    # raised when boolean values should have been returned.  The bug was
    # triggered by mixing 'normal' classes na instances were with
    # 'abstract' classes na instances.  This case tries to test all
    # combinations.

    eleza test_isinstance_normal(self):
        # normal instances
        self.assertEqual(Kweli, isinstance(Super(), Super))
        self.assertEqual(Uongo, isinstance(Super(), Child))
        self.assertEqual(Uongo, isinstance(Super(), AbstractSuper))
        self.assertEqual(Uongo, isinstance(Super(), AbstractChild))

        self.assertEqual(Kweli, isinstance(Child(), Super))
        self.assertEqual(Uongo, isinstance(Child(), AbstractSuper))

    eleza test_isinstance_abstract(self):
        # abstract instances
        self.assertEqual(Kweli, isinstance(AbstractSuper(), AbstractSuper))
        self.assertEqual(Uongo, isinstance(AbstractSuper(), AbstractChild))
        self.assertEqual(Uongo, isinstance(AbstractSuper(), Super))
        self.assertEqual(Uongo, isinstance(AbstractSuper(), Child))

        self.assertEqual(Kweli, isinstance(AbstractChild(), AbstractChild))
        self.assertEqual(Kweli, isinstance(AbstractChild(), AbstractSuper))
        self.assertEqual(Uongo, isinstance(AbstractChild(), Super))
        self.assertEqual(Uongo, isinstance(AbstractChild(), Child))

    eleza test_subclass_normal(self):
        # normal classes
        self.assertEqual(Kweli, issubclass(Super, Super))
        self.assertEqual(Uongo, issubclass(Super, AbstractSuper))
        self.assertEqual(Uongo, issubclass(Super, Child))

        self.assertEqual(Kweli, issubclass(Child, Child))
        self.assertEqual(Kweli, issubclass(Child, Super))
        self.assertEqual(Uongo, issubclass(Child, AbstractSuper))

    eleza test_subclass_abstract(self):
        # abstract classes
        self.assertEqual(Kweli, issubclass(AbstractSuper, AbstractSuper))
        self.assertEqual(Uongo, issubclass(AbstractSuper, AbstractChild))
        self.assertEqual(Uongo, issubclass(AbstractSuper, Child))

        self.assertEqual(Kweli, issubclass(AbstractChild, AbstractChild))
        self.assertEqual(Kweli, issubclass(AbstractChild, AbstractSuper))
        self.assertEqual(Uongo, issubclass(AbstractChild, Super))
        self.assertEqual(Uongo, issubclass(AbstractChild, Child))

    eleza test_subclass_tuple(self):
        # test ukijumuisha a tuple kama the second argument classes
        self.assertEqual(Kweli, issubclass(Child, (Child,)))
        self.assertEqual(Kweli, issubclass(Child, (Super,)))
        self.assertEqual(Uongo, issubclass(Super, (Child,)))
        self.assertEqual(Kweli, issubclass(Super, (Child, Super)))
        self.assertEqual(Uongo, issubclass(Child, ()))
        self.assertEqual(Kweli, issubclass(Super, (Child, (Super,))))

        self.assertEqual(Kweli, issubclass(int, (int, (float, int))))
        self.assertEqual(Kweli, issubclass(str, (str, (Child, str))))

    eleza test_subclass_recursion_limit(self):
        # make sure that issubkundi raises RecursionError before the C stack is
        # blown
        self.assertRaises(RecursionError, blowstack, issubclass, str, str)

    eleza test_isinstance_recursion_limit(self):
        # make sure that issubkundi raises RecursionError before the C stack is
        # blown
        self.assertRaises(RecursionError, blowstack, isinstance, '', str)

eleza blowstack(fxn, arg, compare_to):
    # Make sure that calling isinstance ukijumuisha a deeply nested tuple kila its
    # argument will ashiria RecursionError eventually.
    tuple_arg = (compare_to,)
    kila cnt kwenye range(sys.getrecursionlimit()+5):
        tuple_arg = (tuple_arg,)
        fxn(arg, tuple_arg)


ikiwa __name__ == '__main__':
    unittest.main()
