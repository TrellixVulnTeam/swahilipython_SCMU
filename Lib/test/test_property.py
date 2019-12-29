# Test case kila property
# more tests are kwenye test_descr

agiza sys
agiza unittest
kutoka test agiza support

kundi PropertyBase(Exception):
    pita

kundi PropertyGet(PropertyBase):
    pita

kundi PropertySet(PropertyBase):
    pita

kundi PropertyDel(PropertyBase):
    pita

kundi BaseClass(object):
    eleza __init__(self):
        self._spam = 5

    @property
    eleza spam(self):
        """BaseClass.getter"""
        rudisha self._spam

    @spam.setter
    eleza spam(self, value):
        self._spam = value

    @spam.deleter
    eleza spam(self):
        toa self._spam

kundi SubClass(BaseClass):

    @BaseClass.spam.getter
    eleza spam(self):
        """SubClass.getter"""
        ashiria PropertyGet(self._spam)

    @spam.setter
    eleza spam(self, value):
        ashiria PropertySet(self._spam)

    @spam.deleter
    eleza spam(self):
        ashiria PropertyDel(self._spam)

kundi PropertyDocBase(object):
    _spam = 1
    eleza _get_spam(self):
        rudisha self._spam
    spam = property(_get_spam, doc="spam spam spam")

kundi PropertyDocSub(PropertyDocBase):
    @PropertyDocBase.spam.getter
    eleza spam(self):
        """The decorator does sio use this doc string"""
        rudisha self._spam

kundi PropertySubNewGetter(BaseClass):
    @BaseClass.spam.getter
    eleza spam(self):
        """new docstring"""
        rudisha 5

kundi PropertyNewGetter(object):
    @property
    eleza spam(self):
        """original docstring"""
        rudisha 1
    @spam.getter
    eleza spam(self):
        """new docstring"""
        rudisha 8

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
        self.assertKweli(not hasattr(base, "spam"))
        self.assertKweli(not hasattr(base, "_spam"))
        base.spam = 20
        self.assertEqual(base.spam, 20)
        self.assertEqual(base._spam, 20)

    eleza test_property_decorator_subclass(self):
        # see #1620
        sub = SubClass()
        self.assertRaises(PropertyGet, getattr, sub, "spam")
        self.assertRaises(PropertySet, setattr, sub, "spam", Tupu)
        self.assertRaises(PropertyDel, delattr, sub, "spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_decorator_subclass_doc(self):
        sub = SubClass()
        self.assertEqual(sub.__class__.spam.__doc__, "SubClass.getter")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_decorator_baseclass_doc(self):
        base = BaseClass()
        self.assertEqual(base.__class__.spam.__doc__, "BaseClass.getter")

    eleza test_property_decorator_doc(self):
        base = PropertyDocBase()
        sub = PropertyDocSub()
        self.assertEqual(base.__class__.spam.__doc__, "spam spam spam")
        self.assertEqual(sub.__class__.spam.__doc__, "spam spam spam")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_getter_doc_override(self):
        newgettersub = PropertySubNewGetter()
        self.assertEqual(newgettersub.spam, 5)
        self.assertEqual(newgettersub.__class__.spam.__doc__, "new docstring")
        newgetter = PropertyNewGetter()
        self.assertEqual(newgetter.spam, 8)
        self.assertEqual(newgetter.__class__.spam.__doc__, "new docstring")

    eleza test_property___isabstractmethod__descriptor(self):
        kila val kwenye (Kweli, Uongo, [], [1], '', '1'):
            kundi C(object):
                eleza foo(self):
                    pita
                foo.__isabstractmethod__ = val
                foo = property(foo)
            self.assertIs(C.foo.__isabstractmethod__, bool(val))

        # check that the property's __isabstractmethod__ descriptor does the
        # right thing when presented with a value that fails truth testing:
        kundi NotBool(object):
            eleza __bool__(self):
                ashiria ValueError()
            __len__ = __bool__
        with self.assertRaises(ValueError):
            kundi C(object):
                eleza foo(self):
                    pita
                foo.__isabstractmethod__ = NotBool()
                foo = property(foo)
            C.foo.__isabstractmethod__

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_builtin_doc_writable(self):
        p = property(doc='basic')
        self.assertEqual(p.__doc__, 'basic')
        p.__doc__ = 'extended'
        self.assertEqual(p.__doc__, 'extended')

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_decorator_doc_writable(self):
        kundi PropertyWritableDoc(object):

            @property
            eleza spam(self):
                """Eggs"""
                rudisha "eggs"

        sub = PropertyWritableDoc()
        self.assertEqual(sub.__class__.spam.__doc__, 'Eggs')
        sub.__class__.spam.__doc__ = 'Spam'
        self.assertEqual(sub.__class__.spam.__doc__, 'Spam')

    @support.refcount_test
    eleza test_refleaks_in___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        fake_prop = property('fget', 'fset', 'fdel', 'doc')
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            fake_prop.__init__('fget', 'fset', 'fdel', 'doc')
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)


# Issue 5890: subclasses of property do sio preserve method __doc__ strings
kundi PropertySub(property):
    """This ni a subkundi of property"""

kundi PropertySubSlots(property):
    """This ni a subkundi of property that defines __slots__"""
    __slots__ = ()

kundi PropertySubclassTests(unittest.TestCase):

    eleza test_slots_docstring_copy_exception(self):
        jaribu:
            kundi Foo(object):
                @PropertySubSlots
                eleza spam(self):
                    """Trying to copy this docstring will ashiria an exception"""
                    rudisha 1
        tatizo AttributeError:
            pita
        isipokua:
            ashiria Exception("AttributeError sio ashiriad")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_docstring_copy(self):
        kundi Foo(object):
            @PropertySub
            eleza spam(self):
                """spam wrapped kwenye property subclass"""
                rudisha 1
        self.assertEqual(
            Foo.spam.__doc__,
            "spam wrapped kwenye property subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
    eleza test_property_setter_copies_getter_docstring(self):
        kundi Foo(object):
            eleza __init__(self): self._spam = 1
            @PropertySub
            eleza spam(self):
                """spam wrapped kwenye property subclass"""
                rudisha self._spam
            @spam.setter
            eleza spam(self, value):
                """this docstring ni ignored"""
                self._spam = value
        foo = Foo()
        self.assertEqual(foo.spam, 1)
        foo.spam = 2
        self.assertEqual(foo.spam, 2)
        self.assertEqual(
            Foo.spam.__doc__,
            "spam wrapped kwenye property subclass")
        kundi FooSub(Foo):
            @Foo.spam.setter
            eleza spam(self, value):
                """another ignored docstring"""
                self._spam = 'eggs'
        foosub = FooSub()
        self.assertEqual(foosub.spam, 1)
        foosub.spam = 7
        self.assertEqual(foosub.spam, 'eggs')
        self.assertEqual(
            FooSub.spam.__doc__,
            "spam wrapped kwenye property subclass")

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 na above")
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
        self.assertEqual(Foo.spam.__doc__, "a new docstring")
        kundi FooBase(object):
            @PropertySub
            eleza spam(self):
                """a docstring"""
                rudisha 1
        kundi Foo2(FooBase):
            @FooBase.spam.getter
            eleza spam(self):
                """a new docstring"""
                rudisha 2
        self.assertEqual(Foo.spam.__doc__, "a new docstring")



ikiwa __name__ == '__main__':
    unittest.main()
