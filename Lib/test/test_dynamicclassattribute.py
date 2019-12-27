# Test case for DynamicClassAttribute
# more tests are in test_descr

agiza abc
agiza sys
agiza unittest
kutoka types agiza DynamicClassAttribute

kundi PropertyBase(Exception):
    pass

kundi PropertyGet(PropertyBase):
    pass

kundi PropertySet(PropertyBase):
    pass

kundi PropertyDel(PropertyBase):
    pass

kundi BaseClass(object):
    eleza __init__(self):
        self._spam = 5

    @DynamicClassAttribute
    eleza spam(self):
        """BaseClass.getter"""
        rudisha self._spam

    @spam.setter
    eleza spam(self, value):
        self._spam = value

    @spam.deleter
    eleza spam(self):
        del self._spam

kundi SubClass(BaseClass):

    spam = BaseClass.__dict__['spam']

    @spam.getter
    eleza spam(self):
        """SubClass.getter"""
        raise PropertyGet(self._spam)

    @spam.setter
    eleza spam(self, value):
        raise PropertySet(self._spam)

    @spam.deleter
    eleza spam(self):
        raise PropertyDel(self._spam)

kundi PropertyDocBase(object):
    _spam = 1
    eleza _get_spam(self):
        rudisha self._spam
    spam = DynamicClassAttribute(_get_spam, doc="spam spam spam")

kundi PropertyDocSub(PropertyDocBase):
    spam = PropertyDocBase.__dict__['spam']
    @spam.getter
    eleza spam(self):
        """The decorator does not use this doc string"""
        rudisha self._spam

kundi PropertySubNewGetter(BaseClass):
    spam = BaseClass.__dict__['spam']
    @spam.getter
    eleza spam(self):
        """new docstring"""
        rudisha 5

kundi PropertyNewGetter(object):
    @DynamicClassAttribute
    eleza spam(self):
        """original docstring"""
        rudisha 1
    @spam.getter
    eleza spam(self):
        """new docstring"""
        rudisha 8

kundi ClassWithAbstractVirtualProperty(metaclass=abc.ABCMeta):
    @DynamicClassAttribute
    @abc.abstractmethod
    eleza color():
        pass

kundi ClassWithPropertyAbstractVirtual(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    @DynamicClassAttribute
    eleza color():
        pass

kundi PropertyTests(unittest.TestCase):
    eleza test_property_decorator_baseclass(self):
        # see #1620
        base = BaseClass()
        self.assertEqual(base.spam, 5)
        self.assertEqual(base._spam, 5)
        base.spam = 10
        self.assertEqual(base.spam, 10)
        self.assertEqual(base._spam, 10)
        delattr(base, "spam")
        self.assertTrue(not hasattr(base, "spam"))
        self.assertTrue(not hasattr(base, "_spam"))
        base.spam = 20
        self.assertEqual(base.spam, 20)
        self.assertEqual(base._spam, 20)

    eleza test_property_decorator_subclass(self):
        # see #1620
        sub = SubClass()
        self.assertRaises(PropertyGet, getattr, sub, "spam")
        self.assertRaises(PropertySet, setattr, sub, "spam", None)
        self.assertRaises(PropertyDel, delattr, sub, "spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_property_decorator_subclass_doc(self):
        sub = SubClass()
        self.assertEqual(sub.__class__.__dict__['spam'].__doc__, "SubClass.getter")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_property_decorator_baseclass_doc(self):
        base = BaseClass()
        self.assertEqual(base.__class__.__dict__['spam'].__doc__, "BaseClass.getter")

    eleza test_property_decorator_doc(self):
        base = PropertyDocBase()
        sub = PropertyDocSub()
        self.assertEqual(base.__class__.__dict__['spam'].__doc__, "spam spam spam")
        self.assertEqual(sub.__class__.__dict__['spam'].__doc__, "spam spam spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_property_getter_doc_override(self):
        newgettersub = PropertySubNewGetter()
        self.assertEqual(newgettersub.spam, 5)
        self.assertEqual(newgettersub.__class__.__dict__['spam'].__doc__, "new docstring")
        newgetter = PropertyNewGetter()
        self.assertEqual(newgetter.spam, 8)
        self.assertEqual(newgetter.__class__.__dict__['spam'].__doc__, "new docstring")

    eleza test_property___isabstractmethod__descriptor(self):
        for val in (True, False, [], [1], '', '1'):
            kundi C(object):
                eleza foo(self):
                    pass
                foo.__isabstractmethod__ = val
                foo = DynamicClassAttribute(foo)
            self.assertIs(C.__dict__['foo'].__isabstractmethod__, bool(val))

        # check that the DynamicClassAttribute's __isabstractmethod__ descriptor does the
        # right thing when presented with a value that fails truth testing:
        kundi NotBool(object):
            eleza __bool__(self):
                raise ValueError()
            __len__ = __bool__
        with self.assertRaises(ValueError):
            kundi C(object):
                eleza foo(self):
                    pass
                foo.__isabstractmethod__ = NotBool()
                foo = DynamicClassAttribute(foo)

    eleza test_abstract_virtual(self):
        self.assertRaises(TypeError, ClassWithAbstractVirtualProperty)
        self.assertRaises(TypeError, ClassWithPropertyAbstractVirtual)
        kundi APV(ClassWithPropertyAbstractVirtual):
            pass
        self.assertRaises(TypeError, APV)
        kundi AVP(ClassWithAbstractVirtualProperty):
            pass
        self.assertRaises(TypeError, AVP)
        kundi Okay1(ClassWithAbstractVirtualProperty):
            @DynamicClassAttribute
            eleza color(self):
                rudisha self._color
            eleza __init__(self):
                self._color = 'cyan'
        with self.assertRaises(AttributeError):
            Okay1.color
        self.assertEqual(Okay1().color, 'cyan')
        kundi Okay2(ClassWithAbstractVirtualProperty):
            @DynamicClassAttribute
            eleza color(self):
                rudisha self._color
            eleza __init__(self):
                self._color = 'magenta'
        with self.assertRaises(AttributeError):
            Okay2.color
        self.assertEqual(Okay2().color, 'magenta')


# Issue 5890: subclasses of DynamicClassAttribute do not preserve method __doc__ strings
kundi PropertySub(DynamicClassAttribute):
    """This is a subkundi of DynamicClassAttribute"""

kundi PropertySubSlots(DynamicClassAttribute):
    """This is a subkundi of DynamicClassAttribute that defines __slots__"""
    __slots__ = ()

kundi PropertySubclassTests(unittest.TestCase):

    @unittest.skipIf(hasattr(PropertySubSlots, '__doc__'),
            "__doc__ is already present, __slots__ will have no effect")
    eleza test_slots_docstring_copy_exception(self):
        try:
            kundi Foo(object):
                @PropertySubSlots
                eleza spam(self):
                    """Trying to copy this docstring will raise an exception"""
                    rudisha 1
                andika('\n',spam.__doc__)
        except AttributeError:
            pass
        else:
            raise Exception("AttributeError not raised")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_docstring_copy(self):
        kundi Foo(object):
            @PropertySub
            eleza spam(self):
                """spam wrapped in DynamicClassAttribute subclass"""
                rudisha 1
        self.assertEqual(
            Foo.__dict__['spam'].__doc__,
            "spam wrapped in DynamicClassAttribute subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_property_setter_copies_getter_docstring(self):
        kundi Foo(object):
            eleza __init__(self): self._spam = 1
            @PropertySub
            eleza spam(self):
                """spam wrapped in DynamicClassAttribute subclass"""
                rudisha self._spam
            @spam.setter
            eleza spam(self, value):
                """this docstring is ignored"""
                self._spam = value
        foo = Foo()
        self.assertEqual(foo.spam, 1)
        foo.spam = 2
        self.assertEqual(foo.spam, 2)
        self.assertEqual(
            Foo.__dict__['spam'].__doc__,
            "spam wrapped in DynamicClassAttribute subclass")
        kundi FooSub(Foo):
            spam = Foo.__dict__['spam']
            @spam.setter
            eleza spam(self, value):
                """another ignored docstring"""
                self._spam = 'eggs'
        foosub = FooSub()
        self.assertEqual(foosub.spam, 1)
        foosub.spam = 7
        self.assertEqual(foosub.spam, 'eggs')
        self.assertEqual(
            FooSub.__dict__['spam'].__doc__,
            "spam wrapped in DynamicClassAttribute subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_property_new_getter_new_docstring(self):

        kundi Foo(object):
            @PropertySub
            eleza spam(self):
                """a docstring"""
                rudisha 1
            @spam.getter
            eleza spam(self):
                """a new docstring"""
                rudisha 2
        self.assertEqual(Foo.__dict__['spam'].__doc__, "a new docstring")
        kundi FooBase(object):
            @PropertySub
            eleza spam(self):
                """a docstring"""
                rudisha 1
        kundi Foo2(FooBase):
            spam = FooBase.__dict__['spam']
            @spam.getter
            eleza spam(self):
                """a new docstring"""
                rudisha 2
        self.assertEqual(Foo.__dict__['spam'].__doc__, "a new docstring")



ikiwa __name__ == '__main__':
    unittest.main()
