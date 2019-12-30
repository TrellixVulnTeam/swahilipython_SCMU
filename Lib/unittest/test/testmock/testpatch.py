# Copyright (C) 2007-2012 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

agiza os
agiza sys

agiza unittest
kutoka unittest.test.testmock agiza support
kutoka unittest.test.testmock.support agiza SomeClass, is_instance

kutoka test.test_importlib.util agiza uncache
kutoka unittest.mock agiza (
    NonCallableMock, CallableMixin, sentinel,
    MagicMock, Mock, NonCallableMagicMock, patch, _patch,
    DEFAULT, call, _get_target
)


builtin_string = 'builtins'

PTModule = sys.modules[__name__]
MODNAME = '%s.PTModule' % __name__


eleza _get_proxy(obj, get_only=Kweli):
    kundi Proxy(object):
        eleza __getattr__(self, name):
            rudisha getattr(obj, name)
    ikiwa sio get_only:
        eleza __setattr__(self, name, value):
            setattr(obj, name, value)
        eleza __delattr__(self, name):
            delattr(obj, name)
        Proxy.__setattr__ = __setattr__
        Proxy.__delattr__ = __delattr__
    rudisha Proxy()


# kila use kwenye the test
something  = sentinel.Something
something_else  = sentinel.SomethingElse


kundi Foo(object):
    eleza __init__(self, a): pass
    eleza f(self, a): pass
    eleza g(self): pass
    foo = 'bar'

    @staticmethod
    eleza static_method(): pass

    @classmethod
    eleza class_method(cls): pass

    kundi Bar(object):
        eleza a(self): pass

foo_name = '%s.Foo' % __name__


eleza function(a, b=Foo): pass


kundi Container(object):
    eleza __init__(self):
        self.values = {}

    eleza __getitem__(self, name):
        rudisha self.values[name]

    eleza __setitem__(self, name, value):
        self.values[name] = value

    eleza __delitem__(self, name):
        toa self.values[name]

    eleza __iter__(self):
        rudisha iter(self.values)



kundi PatchTest(unittest.TestCase):

    eleza assertNotCallable(self, obj, magic=Kweli):
        MockClass = NonCallableMagicMock
        ikiwa sio magic:
            MockClass = NonCallableMock

        self.assertRaises(TypeError, obj)
        self.assertKweli(is_instance(obj, MockClass))
        self.assertUongo(is_instance(obj, CallableMixin))


    eleza test_single_patchobject(self):
        kundi Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', sentinel.Patched)
        eleza test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")


    eleza test_patchobject_with_none(self):
        kundi Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', Tupu)
        eleza test():
            self.assertIsTupu(Something.attribute, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")


    eleza test_multiple_patchobject(self):
        kundi Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'next_attribute', sentinel.Patched2)
        eleza test():
            self.assertEqual(Something.attribute, sentinel.Patched,
                             "unpatched")
            self.assertEqual(Something.next_attribute, sentinel.Patched2,
                             "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")
        self.assertEqual(Something.next_attribute, sentinel.Original2,
                         "patch sio restored")


    eleza test_object_lookup_is_quite_lazy(self):
        global something
        original = something
        @patch('%s.something' % __name__, sentinel.Something2)
        eleza test():
            pass

        jaribu:
            something = sentinel.replacement_value
            test()
            self.assertEqual(something, sentinel.replacement_value)
        mwishowe:
            something = original


    eleza test_patch(self):
        @patch('%s.something' % __name__, sentinel.Something2)
        eleza test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")

        test()
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch sio restored")

        @patch('%s.something' % __name__, sentinel.Something2)
        @patch('%s.something_else' % __name__, sentinel.SomethingElse)
        eleza test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")
            self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                             "unpatched")

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch sio restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                         "patch sio restored")

        # Test the patching na restoring works a second time
        test()

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch sio restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                         "patch sio restored")

        mock = Mock()
        mock.return_value = sentinel.Handle
        @patch('%s.open' % builtin_string, mock)
        eleza test():
            self.assertEqual(open('filename', 'r'), sentinel.Handle,
                             "open sio patched")
        test()
        test()

        self.assertNotEqual(open, mock, "patch sio restored")


    eleza test_patch_class_attribute(self):
        @patch('%s.SomeClass.class_attribute' % __name__,
               sentinel.ClassAttribute)
        eleza test():
            self.assertEqual(PTModule.SomeClass.class_attribute,
                             sentinel.ClassAttribute, "unpatched")
        test()

        self.assertIsTupu(PTModule.SomeClass.class_attribute,
                          "patch sio restored")


    eleza test_patchobject_with_default_mock(self):
        kundi Test(object):
            something = sentinel.Original
            something2 = sentinel.Original2

        @patch.object(Test, 'something')
        eleza test(mock):
            self.assertEqual(mock, Test.something,
                             "Mock sio passed into test function")
            self.assertIsInstance(mock, MagicMock,
                            "patch ukijumuisha two arguments did sio create a mock")

        test()

        @patch.object(Test, 'something')
        @patch.object(Test, 'something2')
        eleza test(this1, this2, mock1, mock2):
            self.assertEqual(this1, sentinel.this1,
                             "Patched function didn't receive initial argument")
            self.assertEqual(this2, sentinel.this2,
                             "Patched function didn't receive second argument")
            self.assertEqual(mock1, Test.something2,
                             "Mock sio passed into test function")
            self.assertEqual(mock2, Test.something,
                             "Second Mock sio passed into test function")
            self.assertIsInstance(mock2, MagicMock,
                            "patch ukijumuisha two arguments did sio create a mock")
            self.assertIsInstance(mock2, MagicMock,
                            "patch ukijumuisha two arguments did sio create a mock")

            # A hack to test that new mocks are passed the second time
            self.assertNotEqual(outerMock1, mock1, "unexpected value kila mock1")
            self.assertNotEqual(outerMock2, mock2, "unexpected value kila mock1")
            rudisha mock1, mock2

        outerMock1 = outerMock2 = Tupu
        outerMock1, outerMock2 = test(sentinel.this1, sentinel.this2)

        # Test that executing a second time creates new mocks
        test(sentinel.this1, sentinel.this2)


    eleza test_patch_with_spec(self):
        @patch('%s.SomeClass' % __name__, spec=SomeClass)
        eleza test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertKweli(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    eleza test_patchobject_with_spec(self):
        @patch.object(SomeClass, 'class_attribute', spec=SomeClass)
        eleza test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertKweli(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    eleza test_patch_with_spec_as_list(self):
        @patch('%s.SomeClass' % __name__, spec=['wibble'])
        eleza test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertKweli(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    eleza test_patchobject_with_spec_as_list(self):
        @patch.object(SomeClass, 'class_attribute', spec=['wibble'])
        eleza test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertKweli(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    eleza test_nested_patch_with_spec_as_list(self):
        # regression test kila nested decorators
        @patch('%s.open' % builtin_string)
        @patch('%s.SomeClass' % __name__, spec=['wibble'])
        eleza test(MockSomeClass, MockOpen):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertKweli(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
        test()


    eleza test_patch_with_spec_as_boolean(self):
        @patch('%s.SomeClass' % __name__, spec=Kweli)
        eleza test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should sio  ashiria attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    eleza test_patch_object_with_spec_as_boolean(self):
        @patch.object(PTModule, 'SomeClass', spec=Kweli)
        eleza test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should sio  ashiria attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    eleza test_patch_class_acts_with_spec_is_inherited(self):
        @patch('%s.SomeClass' % __name__, spec=Kweli)
        eleza test(MockSomeClass):
            self.assertKweli(is_instance(MockSomeClass, MagicMock))
            instance = MockSomeClass()
            self.assertNotCallable(instance)
            # Should sio  ashiria attribute error
            instance.wibble

            self.assertRaises(AttributeError, lambda: instance.not_wibble)

        test()


    eleza test_patch_with_create_mocks_non_existent_attributes(self):
        @patch('%s.frooble' % builtin_string, sentinel.Frooble, create=Kweli)
        eleza test():
            self.assertEqual(frooble, sentinel.Frooble)

        test()
        self.assertRaises(NameError, lambda: frooble)


    eleza test_patchobject_with_create_mocks_non_existent_attributes(self):
        @patch.object(SomeClass, 'frooble', sentinel.Frooble, create=Kweli)
        eleza test():
            self.assertEqual(SomeClass.frooble, sentinel.Frooble)

        test()
        self.assertUongo(hasattr(SomeClass, 'frooble'))


    eleza test_patch_wont_create_by_default(self):
        ukijumuisha self.assertRaises(AttributeError):
            @patch('%s.frooble' % builtin_string, sentinel.Frooble)
            eleza test(): pass

            test()
        self.assertRaises(NameError, lambda: frooble)


    eleza test_patchobject_wont_create_by_default(self):
        ukijumuisha self.assertRaises(AttributeError):
            @patch.object(SomeClass, 'ord', sentinel.Frooble)
            eleza test(): pass
            test()
        self.assertUongo(hasattr(SomeClass, 'ord'))


    eleza test_patch_builtins_without_create(self):
        @patch(__name__+'.ord')
        eleza test_ord(mock_ord):
            mock_ord.return_value = 101
            rudisha ord('c')

        @patch(__name__+'.open')
        eleza test_open(mock_open):
            m = mock_open.return_value
            m.read.return_value = 'abcd'

            fobj = open('doesnotexists.txt')
            data = fobj.read()
            fobj.close()
            rudisha data

        self.assertEqual(test_ord(), 101)
        self.assertEqual(test_open(), 'abcd')


    eleza test_patch_with_static_methods(self):
        kundi Foo(object):
            @staticmethod
            eleza woot():
                rudisha sentinel.Static

        @patch.object(Foo, 'woot', staticmethod(lambda: sentinel.Patched))
        eleza anonymous():
            self.assertEqual(Foo.woot(), sentinel.Patched)
        anonymous()

        self.assertEqual(Foo.woot(), sentinel.Static)


    eleza test_patch_local(self):
        foo = sentinel.Foo
        @patch.object(sentinel, 'Foo', 'Foo')
        eleza anonymous():
            self.assertEqual(sentinel.Foo, 'Foo')
        anonymous()

        self.assertEqual(sentinel.Foo, foo)


    eleza test_patch_slots(self):
        kundi Foo(object):
            __slots__ = ('Foo',)

        foo = Foo()
        foo.Foo = sentinel.Foo

        @patch.object(foo, 'Foo', 'Foo')
        eleza anonymous():
            self.assertEqual(foo.Foo, 'Foo')
        anonymous()

        self.assertEqual(foo.Foo, sentinel.Foo)


    eleza test_patchobject_class_decorator(self):
        kundi Something(object):
            attribute = sentinel.Original

        kundi Foo(object):
            eleza test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Patched,
                                 "unpatched")
            eleza not_test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Original,
                                 "non-test method patched")

        Foo = patch.object(Something, 'attribute', sentinel.Patched)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")


    eleza test_patch_class_decorator(self):
        kundi Something(object):
            attribute = sentinel.Original

        kundi Foo(object):

            test_class_attr = 'whatever'

            eleza test_method(other_self, mock_something):
                self.assertEqual(PTModule.something, mock_something,
                                 "unpatched")
            eleza not_test_method(other_self):
                self.assertEqual(PTModule.something, sentinel.Something,
                                 "non-test method patched")
        Foo = patch('%s.something' % __name__)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch sio restored")


    eleza test_patchobject_twice(self):
        kundi Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'attribute', sentinel.Patched)
        eleza test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch sio restored")


    eleza test_patch_dict(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo)
        eleza test():
            foo['a'] = 3
            toa foo['initial']
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'})
        eleza test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')])
        eleza test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)


    eleza test_patch_dict_with_container_object(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo)
        eleza test():
            foo['a'] = 3
            toa foo['initial']
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'})
        eleza test():
            self.assertEqual(len(foo.values), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo.values, original)


    eleza test_patch_dict_with_clear(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo, clear=Kweli)
        eleza test():
            self.assertEqual(foo, {})
            foo['a'] = 3
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'}, clear=Kweli)
        eleza test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')], clear=Kweli)
        eleza test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)


    eleza test_patch_dict_with_container_object_and_clear(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo, clear=Kweli)
        eleza test():
            self.assertEqual(foo.values, {})
            foo['a'] = 3
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'}, clear=Kweli)
        eleza test():
            self.assertEqual(foo.values, {'a': 'b'})

        test()

        self.assertEqual(foo.values, original)


    eleza test_patch_dict_as_context_manager(self):
        foo = {'a': 'b'}
        ukijumuisha patch.dict(foo, a='c') as patched:
            self.assertEqual(patched, {'a': 'c'})
        self.assertEqual(foo, {'a': 'b'})


    eleza test_name_preserved(self):
        foo = {}

        @patch('%s.SomeClass' % __name__, object())
        @patch('%s.SomeClass' % __name__, object(), autospec=Kweli)
        @patch.object(SomeClass, object())
        @patch.dict(foo)
        eleza some_name(): pass

        self.assertEqual(some_name.__name__, 'some_name')


    eleza test_patch_with_exception(self):
        foo = {}

        @patch.dict(foo, {'a': 'b'})
        eleza test():
             ashiria NameError('Konrad')

        ukijumuisha self.assertRaises(NameError):
            test()

        self.assertEqual(foo, {})


    eleza test_patch_dict_with_string(self):
        @patch.dict('os.environ', {'konrad_delong': 'some value'})
        eleza test():
            self.assertIn('konrad_delong', os.environ)

        test()


    eleza test_patch_dict_decorator_resolution(self):
        # bpo-35512: Ensure that patch ukijumuisha a string target resolves to
        # the new dictionary during function call
        original = support.target.copy()

        @patch.dict('unittest.test.testmock.support.target', {'bar': 'BAR'})
        eleza test():
            self.assertEqual(support.target, {'foo': 'BAZ', 'bar': 'BAR'})

        jaribu:
            support.target = {'foo': 'BAZ'}
            test()
            self.assertEqual(support.target, {'foo': 'BAZ'})
        mwishowe:
            support.target = original


    eleza test_patch_spec_set(self):
        @patch('%s.SomeClass' % __name__, spec=SomeClass, spec_set=Kweli)
        eleza test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec=SomeClass, spec_set=Kweli)
        eleza test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)
        @patch('%s.SomeClass' % __name__, spec_set=Kweli)
        eleza test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec_set=Kweli)
        eleza test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)


    eleza test_spec_set_inherit(self):
        @patch('%s.SomeClass' % __name__, spec_set=Kweli)
        eleza test(MockClass):
            instance = MockClass()
            instance.z = 'foo'

        self.assertRaises(AttributeError, test)


    eleza test_patch_start_stop(self):
        original = something
        patcher = patch('%s.something' % __name__)
        self.assertIs(something, original)
        mock = patcher.start()
        jaribu:
            self.assertIsNot(mock, original)
            self.assertIs(something, mock)
        mwishowe:
            patcher.stop()
        self.assertIs(something, original)


    eleza test_stop_without_start(self):
        # bpo-36366: calling stop without start will rudisha Tupu.
        patcher = patch(foo_name, 'bar', 3)
        self.assertIsTupu(patcher.stop())


    eleza test_stop_idempotent(self):
        # bpo-36366: calling stop on an already stopped patch will rudisha Tupu.
        patcher = patch(foo_name, 'bar', 3)

        patcher.start()
        patcher.stop()
        self.assertIsTupu(patcher.stop())


    eleza test_patchobject_start_stop(self):
        original = something
        patcher = patch.object(PTModule, 'something', 'foo')
        self.assertIs(something, original)
        replaced = patcher.start()
        jaribu:
            self.assertEqual(replaced, 'foo')
            self.assertIs(something, replaced)
        mwishowe:
            patcher.stop()
        self.assertIs(something, original)


    eleza test_patch_dict_start_stop(self):
        d = {'foo': 'bar'}
        original = d.copy()
        patcher = patch.dict(d, [('spam', 'eggs')], clear=Kweli)
        self.assertEqual(d, original)

        patcher.start()
        jaribu:
            self.assertEqual(d, {'spam': 'eggs'})
        mwishowe:
            patcher.stop()
        self.assertEqual(d, original)


    eleza test_patch_dict_class_decorator(self):
        this = self
        d = {'spam': 'eggs'}
        original = d.copy()

        kundi Test(object):
            eleza test_first(self):
                this.assertEqual(d, {'foo': 'bar'})
            eleza test_second(self):
                this.assertEqual(d, {'foo': 'bar'})

        Test = patch.dict(d, {'foo': 'bar'}, clear=Kweli)(Test)
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)


    eleza test_get_only_proxy(self):
        kundi Something(object):
            foo = 'foo'
        kundi SomethingElse:
            foo = 'foo'

        kila thing kwenye Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(thing)

            @patch.object(proxy, 'foo', 'bar')
            eleza test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    eleza test_get_set_delete_proxy(self):
        kundi Something(object):
            foo = 'foo'
        kundi SomethingElse:
            foo = 'foo'

        kila thing kwenye Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(Something, get_only=Uongo)

            @patch.object(proxy, 'foo', 'bar')
            eleza test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    eleza test_patch_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch(foo_name, **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    eleza test_patch_object_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch.object(Foo, 'f', **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    eleza test_patch_dict_keyword_args(self):
        original = {'foo': 'bar'}
        copy = original.copy()

        patcher = patch.dict(original, foo=3, bar=4, baz=5)
        patcher.start()

        jaribu:
            self.assertEqual(original, dict(foo=3, bar=4, baz=5))
        mwishowe:
            patcher.stop()

        self.assertEqual(original, copy)


    eleza test_autospec(self):
        kundi Boo(object):
            eleza __init__(self, a): pass
            eleza f(self, a): pass
            eleza g(self): pass
            foo = 'bar'

            kundi Bar(object):
                eleza a(self): pass

        eleza _test(mock):
            mock(1)
            mock.assert_called_with(1)
            self.assertRaises(TypeError, mock)

        eleza _test2(mock):
            mock.f(1)
            mock.f.assert_called_with(1)
            self.assertRaises(TypeError, mock.f)

            mock.g()
            mock.g.assert_called_with()
            self.assertRaises(TypeError, mock.g, 1)

            self.assertRaises(AttributeError, getattr, mock, 'h')

            mock.foo.lower()
            mock.foo.lower.assert_called_with()
            self.assertRaises(AttributeError, getattr, mock.foo, 'bar')

            mock.Bar()
            mock.Bar.assert_called_with()

            mock.Bar.a()
            mock.Bar.a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar.a, 1)

            mock.Bar().a()
            mock.Bar().a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar().a, 1)

            self.assertRaises(AttributeError, getattr, mock.Bar, 'b')
            self.assertRaises(AttributeError, getattr, mock.Bar(), 'b')

        eleza function(mock):
            _test(mock)
            _test2(mock)
            _test2(mock(1))
            self.assertIs(mock, Foo)
            rudisha mock

        test = patch(foo_name, autospec=Kweli)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()

        module = sys.modules[__name__]
        test = patch.object(module, 'Foo', autospec=Kweli)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()


    eleza test_autospec_function(self):
        @patch('%s.function' % __name__, autospec=Kweli)
        eleza test(mock):
            function.assert_not_called()
            self.assertRaises(AssertionError, function.assert_called)
            self.assertRaises(AssertionError, function.assert_called_once)
            function(1)
            self.assertRaises(AssertionError, function.assert_not_called)
            function.assert_called_with(1)
            function.assert_called()
            function.assert_called_once()
            function(2, 3)
            function.assert_called_with(2, 3)

            self.assertRaises(TypeError, function)
            self.assertRaises(AttributeError, getattr, function, 'foo')

        test()


    eleza test_autospec_keywords(self):
        @patch('%s.function' % __name__, autospec=Kweli,
               return_value=3)
        eleza test(mock_function):
            #self.assertEqual(function.abc, 'foo')
            rudisha function(1, 2)

        result = test()
        self.assertEqual(result, 3)


    eleza test_autospec_staticmethod(self):
        ukijumuisha patch('%s.Foo.static_method' % __name__, autospec=Kweli) as method:
            Foo.static_method()
            method.assert_called_once_with()


    eleza test_autospec_classmethod(self):
        ukijumuisha patch('%s.Foo.class_method' % __name__, autospec=Kweli) as method:
            Foo.class_method()
            method.assert_called_once_with()


    eleza test_autospec_with_new(self):
        patcher = patch('%s.function' % __name__, new=3, autospec=Kweli)
        self.assertRaises(TypeError, patcher.start)

        module = sys.modules[__name__]
        patcher = patch.object(module, 'function', new=3, autospec=Kweli)
        self.assertRaises(TypeError, patcher.start)


    eleza test_autospec_with_object(self):
        kundi Bar(Foo):
            extra = []

        patcher = patch(foo_name, autospec=Bar)
        mock = patcher.start()
        jaribu:
            self.assertIsInstance(mock, Bar)
            self.assertIsInstance(mock.extra, list)
        mwishowe:
            patcher.stop()


    eleza test_autospec_inherits(self):
        FooClass = Foo
        patcher = patch(foo_name, autospec=Kweli)
        mock = patcher.start()
        jaribu:
            self.assertIsInstance(mock, FooClass)
            self.assertIsInstance(mock(3), FooClass)
        mwishowe:
            patcher.stop()


    eleza test_autospec_name(self):
        patcher = patch(foo_name, autospec=Kweli)
        mock = patcher.start()

        jaribu:
            self.assertIn(" name='Foo'", repr(mock))
            self.assertIn(" name='Foo.f'", repr(mock.f))
            self.assertIn(" name='Foo()'", repr(mock(Tupu)))
            self.assertIn(" name='Foo().f'", repr(mock(Tupu).f))
        mwishowe:
            patcher.stop()


    eleza test_tracebacks(self):
        @patch.object(Foo, 'f', object())
        eleza test():
             ashiria AssertionError
        jaribu:
            test()
        tatizo:
            err = sys.exc_info()

        result = unittest.TextTestResult(Tupu, Tupu, 0)
        traceback = result._exc_info_to_string(err, self)
        self.assertIn(' ashiria AssertionError', traceback)


    eleza test_new_callable_patch(self):
        patcher = patch(foo_name, new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        kila mock kwenye m1, m2:
            self.assertNotCallable(m1)


    eleza test_new_callable_patch_object(self):
        patcher = patch.object(Foo, 'f', new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        kila mock kwenye m1, m2:
            self.assertNotCallable(m1)


    eleza test_new_callable_keyword_arguments(self):
        kundi Bar(object):
            kwargs = Tupu
            eleza __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, arg1=1, arg2=2)
        m = patcher.start()
        jaribu:
            self.assertIs(type(m), Bar)
            self.assertEqual(Bar.kwargs, dict(arg1=1, arg2=2))
        mwishowe:
            patcher.stop()


    eleza test_new_callable_spec(self):
        kundi Bar(object):
            kwargs = Tupu
            eleza __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, spec=Bar)
        patcher.start()
        jaribu:
            self.assertEqual(Bar.kwargs, dict(spec=Bar))
        mwishowe:
            patcher.stop()

        patcher = patch(foo_name, new_callable=Bar, spec_set=Bar)
        patcher.start()
        jaribu:
            self.assertEqual(Bar.kwargs, dict(spec_set=Bar))
        mwishowe:
            patcher.stop()


    eleza test_new_callable_create(self):
        non_existent_attr = '%s.weeeee' % foo_name
        p = patch(non_existent_attr, new_callable=NonCallableMock)
        self.assertRaises(AttributeError, p.start)

        p = patch(non_existent_attr, new_callable=NonCallableMock,
                  create=Kweli)
        m = p.start()
        jaribu:
            self.assertNotCallable(m, magic=Uongo)
        mwishowe:
            p.stop()


    eleza test_new_callable_incompatible_with_new(self):
        self.assertRaises(
            ValueError, patch, foo_name, new=object(), new_callable=MagicMock
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new=object(),
            new_callable=MagicMock
        )


    eleza test_new_callable_incompatible_with_autospec(self):
        self.assertRaises(
            ValueError, patch, foo_name, new_callable=MagicMock,
            autospec=Kweli
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new_callable=MagicMock,
            autospec=Kweli
        )


    eleza test_new_callable_inherit_for_mocks(self):
        kundi MockSub(Mock):
            pass

        MockClasses = (
            NonCallableMock, NonCallableMagicMock, MagicMock, Mock, MockSub
        )
        kila Klass kwenye MockClasses:
            kila arg kwenye 'spec', 'spec_set':
                kwargs = {arg: Kweli}
                p = patch(foo_name, new_callable=Klass, **kwargs)
                m = p.start()
                jaribu:
                    instance = m.return_value
                    self.assertRaises(AttributeError, getattr, instance, 'x')
                mwishowe:
                    p.stop()


    eleza test_new_callable_inherit_non_mock(self):
        kundi NotAMock(object):
            eleza __init__(self, spec):
                self.spec = spec

        p = patch(foo_name, new_callable=NotAMock, spec=Kweli)
        m = p.start()
        jaribu:
            self.assertKweli(is_instance(m, NotAMock))
            self.assertRaises(AttributeError, getattr, m, 'return_value')
        mwishowe:
            p.stop()

        self.assertEqual(m.spec, Foo)


    eleza test_new_callable_class_decorating(self):
        test = self
        original = Foo
        kundi SomeTest(object):

            eleza _test(self, mock_foo):
                test.assertIsNot(Foo, original)
                test.assertIs(Foo, mock_foo)
                test.assertIsInstance(Foo, SomeClass)

            eleza test_two(self, mock_foo):
                self._test(mock_foo)
            eleza test_one(self, mock_foo):
                self._test(mock_foo)

        SomeTest = patch(foo_name, new_callable=SomeClass)(SomeTest)
        SomeTest().test_one()
        SomeTest().test_two()
        self.assertIs(Foo, original)


    eleza test_patch_multiple(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        patcher1 = patch.multiple(foo_name, f=1, g=2)
        patcher2 = patch.multiple(Foo, f=1, g=2)

        kila patcher kwenye patcher1, patcher2:
            patcher.start()
            jaribu:
                self.assertIs(Foo, original_foo)
                self.assertEqual(Foo.f, 1)
                self.assertEqual(Foo.g, 2)
            mwishowe:
                patcher.stop()

            self.assertIs(Foo, original_foo)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


        @patch.multiple(foo_name, f=3, g=4)
        eleza test():
            self.assertIs(Foo, original_foo)
            self.assertEqual(Foo.f, 3)
            self.assertEqual(Foo.g, 4)

        test()


    eleza test_patch_multiple_no_kwargs(self):
        self.assertRaises(ValueError, patch.multiple, foo_name)
        self.assertRaises(ValueError, patch.multiple, Foo)


    eleza test_patch_multiple_create_mocks(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        @patch.multiple(foo_name, f=DEFAULT, g=3, foo=DEFAULT)
        eleza test(f, foo):
            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertEqual(Foo.g, 3)
            self.assertIs(Foo.foo, foo)
            self.assertKweli(is_instance(f, MagicMock))
            self.assertKweli(is_instance(foo, MagicMock))

        test()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_create_mocks_different_order(self):
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.object(Foo, 'f', 3)
        patcher.attribute_name = 'f'

        other = patch.object(Foo, 'g', DEFAULT)
        other.attribute_name = 'g'
        patcher.additional_patchers = [other]

        @patcher
        eleza test(g):
            self.assertIs(Foo.g, g)
            self.assertEqual(Foo.f, 3)

        test()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_stacked_decorators(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        @patch.multiple(foo_name, f=DEFAULT)
        @patch.multiple(foo_name, foo=DEFAULT)
        @patch(foo_name + '.g')
        eleza test1(g, **kwargs):
            _test(g, **kwargs)

        @patch.multiple(foo_name, f=DEFAULT)
        @patch(foo_name + '.g')
        @patch.multiple(foo_name, foo=DEFAULT)
        eleza test2(g, **kwargs):
            _test(g, **kwargs)

        @patch(foo_name + '.g')
        @patch.multiple(foo_name, f=DEFAULT)
        @patch.multiple(foo_name, foo=DEFAULT)
        eleza test3(g, **kwargs):
            _test(g, **kwargs)

        eleza _test(g, **kwargs):
            f = kwargs.pop('f')
            foo = kwargs.pop('foo')
            self.assertUongo(kwargs)

            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertIs(Foo.g, g)
            self.assertIs(Foo.foo, foo)
            self.assertKweli(is_instance(f, MagicMock))
            self.assertKweli(is_instance(g, MagicMock))
            self.assertKweli(is_instance(foo, MagicMock))

        test1()
        test2()
        test3()
        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_create_mocks_patcher(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.multiple(foo_name, f=DEFAULT, g=3, foo=DEFAULT)

        result = patcher.start()
        jaribu:
            f = result['f']
            foo = result['foo']
            self.assertEqual(set(result), set(['f', 'foo']))

            self.assertIs(Foo, original_foo)
            self.assertIs(Foo.f, f)
            self.assertIs(Foo.foo, foo)
            self.assertKweli(is_instance(f, MagicMock))
            self.assertKweli(is_instance(foo, MagicMock))
        mwishowe:
            patcher.stop()

        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_decorating_class(self):
        test = self
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        kundi SomeTest(object):

            eleza _test(self, f, foo):
                test.assertIs(Foo, original_foo)
                test.assertIs(Foo.f, f)
                test.assertEqual(Foo.g, 3)
                test.assertIs(Foo.foo, foo)
                test.assertKweli(is_instance(f, MagicMock))
                test.assertKweli(is_instance(foo, MagicMock))

            eleza test_two(self, f, foo):
                self._test(f, foo)
            eleza test_one(self, f, foo):
                self._test(f, foo)

        SomeTest = patch.multiple(
            foo_name, f=DEFAULT, g=3, foo=DEFAULT
        )(SomeTest)

        thing = SomeTest()
        thing.test_one()
        thing.test_two()

        self.assertEqual(Foo.f, original_f)
        self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_create(self):
        patcher = patch.multiple(Foo, blam='blam')
        self.assertRaises(AttributeError, patcher.start)

        patcher = patch.multiple(Foo, blam='blam', create=Kweli)
        patcher.start()
        jaribu:
            self.assertEqual(Foo.blam, 'blam')
        mwishowe:
            patcher.stop()

        self.assertUongo(hasattr(Foo, 'blam'))


    eleza test_patch_multiple_spec_set(self):
        # ikiwa spec_set works then we can assume that spec na autospec also
        # work as the underlying machinery ni the same
        patcher = patch.multiple(Foo, foo=DEFAULT, spec_set=['a', 'b'])
        result = patcher.start()
        jaribu:
            self.assertEqual(Foo.foo, result['foo'])
            Foo.foo.a(1)
            Foo.foo.b(2)
            Foo.foo.a.assert_called_with(1)
            Foo.foo.b.assert_called_with(2)
            self.assertRaises(AttributeError, setattr, Foo.foo, 'c', Tupu)
        mwishowe:
            patcher.stop()


    eleza test_patch_multiple_new_callable(self):
        kundi Thing(object):
            pass

        patcher = patch.multiple(
            Foo, f=DEFAULT, g=DEFAULT, new_callable=Thing
        )
        result = patcher.start()
        jaribu:
            self.assertIs(Foo.f, result['f'])
            self.assertIs(Foo.g, result['g'])
            self.assertIsInstance(Foo.f, Thing)
            self.assertIsInstance(Foo.g, Thing)
            self.assertIsNot(Foo.f, Foo.g)
        mwishowe:
            patcher.stop()


    eleza test_nested_patch_failure(self):
        original_f = Foo.f
        original_g = Foo.g

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'missing', 1)
        @patch.object(Foo, 'f', 1)
        eleza thing1(): pass

        @patch.object(Foo, 'missing', 1)
        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        eleza thing2(): pass

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        @patch.object(Foo, 'missing', 1)
        eleza thing3(): pass

        kila func kwenye thing1, thing2, thing3:
            self.assertRaises(AttributeError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


    eleza test_new_callable_failure(self):
        original_f = Foo.f
        original_g = Foo.g
        original_foo = Foo.foo

        eleza crasher():
             ashiria NameError('crasher')

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'foo', new_callable=crasher)
        @patch.object(Foo, 'f', 1)
        eleza thing1(): pass

        @patch.object(Foo, 'foo', new_callable=crasher)
        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        eleza thing2(): pass

        @patch.object(Foo, 'g', 1)
        @patch.object(Foo, 'f', 1)
        @patch.object(Foo, 'foo', new_callable=crasher)
        eleza thing3(): pass

        kila func kwenye thing1, thing2, thing3:
            self.assertRaises(NameError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)
            self.assertEqual(Foo.foo, original_foo)


    eleza test_patch_multiple_failure(self):
        original_f = Foo.f
        original_g = Foo.g

        patcher = patch.object(Foo, 'f', 1)
        patcher.attribute_name = 'f'

        good = patch.object(Foo, 'g', 1)
        good.attribute_name = 'g'

        bad = patch.object(Foo, 'missing', 1)
        bad.attribute_name = 'missing'

        kila additionals kwenye [good, bad], [bad, good]:
            patcher.additional_patchers = additionals

            @patcher
            eleza func(): pass

            self.assertRaises(AttributeError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


    eleza test_patch_multiple_new_callable_failure(self):
        original_f = Foo.f
        original_g = Foo.g
        original_foo = Foo.foo

        eleza crasher():
             ashiria NameError('crasher')

        patcher = patch.object(Foo, 'f', 1)
        patcher.attribute_name = 'f'

        good = patch.object(Foo, 'g', 1)
        good.attribute_name = 'g'

        bad = patch.object(Foo, 'foo', new_callable=crasher)
        bad.attribute_name = 'foo'

        kila additionals kwenye [good, bad], [bad, good]:
            patcher.additional_patchers = additionals

            @patcher
            eleza func(): pass

            self.assertRaises(NameError, func)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)
            self.assertEqual(Foo.foo, original_foo)


    eleza test_patch_multiple_string_subclasses(self):
        Foo = type('Foo', (str,), {'fish': 'tasty'})
        foo = Foo()
        @patch.multiple(foo, fish='nearly gone')
        eleza test():
            self.assertEqual(foo.fish, 'nearly gone')

        test()
        self.assertEqual(foo.fish, 'tasty')


    @patch('unittest.mock.patch.TEST_PREFIX', 'foo')
    eleza test_patch_test_prefix(self):
        kundi Foo(object):
            thing = 'original'

            eleza foo_one(self):
                rudisha self.thing
            eleza foo_two(self):
                rudisha self.thing
            eleza test_one(self):
                rudisha self.thing
            eleza test_two(self):
                rudisha self.thing

        Foo = patch.object(Foo, 'thing', 'changed')(Foo)

        foo = Foo()
        self.assertEqual(foo.foo_one(), 'changed')
        self.assertEqual(foo.foo_two(), 'changed')
        self.assertEqual(foo.test_one(), 'original')
        self.assertEqual(foo.test_two(), 'original')


    @patch('unittest.mock.patch.TEST_PREFIX', 'bar')
    eleza test_patch_dict_test_prefix(self):
        kundi Foo(object):
            eleza bar_one(self):
                rudisha dict(the_dict)
            eleza bar_two(self):
                rudisha dict(the_dict)
            eleza test_one(self):
                rudisha dict(the_dict)
            eleza test_two(self):
                rudisha dict(the_dict)

        the_dict = {'key': 'original'}
        Foo = patch.dict(the_dict, key='changed')(Foo)

        foo =Foo()
        self.assertEqual(foo.bar_one(), {'key': 'changed'})
        self.assertEqual(foo.bar_two(), {'key': 'changed'})
        self.assertEqual(foo.test_one(), {'key': 'original'})
        self.assertEqual(foo.test_two(), {'key': 'original'})


    eleza test_patch_with_spec_mock_repr(self):
        kila arg kwenye ('spec', 'autospec', 'spec_set'):
            p = patch('%s.SomeClass' % __name__, **{arg: Kweli})
            m = p.start()
            jaribu:
                self.assertIn(" name='SomeClass'", repr(m))
                self.assertIn(" name='SomeClass.class_attribute'",
                              repr(m.class_attribute))
                self.assertIn(" name='SomeClass()'", repr(m()))
                self.assertIn(" name='SomeClass().class_attribute'",
                              repr(m().class_attribute))
            mwishowe:
                p.stop()


    eleza test_patch_nested_autospec_repr(self):
        ukijumuisha patch('unittest.test.testmock.support', autospec=Kweli) as m:
            self.assertIn(" name='support.SomeClass.wibble()'",
                          repr(m.SomeClass.wibble()))
            self.assertIn(" name='support.SomeClass().wibble()'",
                          repr(m.SomeClass().wibble()))



    eleza test_mock_calls_with_patch(self):
        kila arg kwenye ('spec', 'autospec', 'spec_set'):
            p = patch('%s.SomeClass' % __name__, **{arg: Kweli})
            m = p.start()
            jaribu:
                m.wibble()

                kalls = [call.wibble()]
                self.assertEqual(m.mock_calls, kalls)
                self.assertEqual(m.method_calls, kalls)
                self.assertEqual(m.wibble.mock_calls, [call()])

                result = m()
                kalls.append(call())
                self.assertEqual(m.mock_calls, kalls)

                result.wibble()
                kalls.append(call().wibble())
                self.assertEqual(m.mock_calls, kalls)

                self.assertEqual(result.mock_calls, [call.wibble()])
                self.assertEqual(result.wibble.mock_calls, [call()])
                self.assertEqual(result.method_calls, [call.wibble()])
            mwishowe:
                p.stop()


    eleza test_patch_imports_lazily(self):
        p1 = patch('squizz.squozz')
        self.assertRaises(ImportError, p1.start)

        ukijumuisha uncache('squizz'):
            squizz = Mock()
            sys.modules['squizz'] = squizz

            squizz.squozz = 6
            p1 = patch('squizz.squozz')
            squizz.squozz = 3
            p1.start()
            p1.stop()
        self.assertEqual(squizz.squozz, 3)

    eleza test_patch_propagates_exc_on_exit(self):
        kundi holder:
            exc_info = Tupu, Tupu, Tupu

        kundi custom_patch(_patch):
            eleza __exit__(self, etype=Tupu, val=Tupu, tb=Tupu):
                _patch.__exit__(self, etype, val, tb)
                holder.exc_info = etype, val, tb
            stop = __exit__

        eleza with_custom_patch(target):
            getter, attribute = _get_target(target)
            rudisha custom_patch(
                getter, attribute, DEFAULT, Tupu, Uongo, Tupu,
                Tupu, Tupu, {}
            )

        @with_custom_patch('squizz.squozz')
        eleza test(mock):
             ashiria RuntimeError

        ukijumuisha uncache('squizz'):
            squizz = Mock()
            sys.modules['squizz'] = squizz

            self.assertRaises(RuntimeError, test)

        self.assertIs(holder.exc_info[0], RuntimeError)
        self.assertIsNotTupu(holder.exc_info[1],
                            'exception value sio propagated')
        self.assertIsNotTupu(holder.exc_info[2],
                            'exception traceback sio propagated')


    eleza test_create_and_specs(self):
        kila kwarg kwenye ('spec', 'spec_set', 'autospec'):
            p = patch('%s.doesnotexist' % __name__, create=Kweli,
                      **{kwarg: Kweli})
            self.assertRaises(TypeError, p.start)
            self.assertRaises(NameError, lambda: doesnotexist)

            # check that spec ukijumuisha create ni innocuous ikiwa the original exists
            p = patch(MODNAME, create=Kweli, **{kwarg: Kweli})
            p.start()
            p.stop()


    eleza test_multiple_specs(self):
        original = PTModule
        kila kwarg kwenye ('spec', 'spec_set'):
            p = patch(MODNAME, autospec=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)

        kila kwarg kwenye ('spec', 'autospec'):
            p = patch(MODNAME, spec_set=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)

        kila kwarg kwenye ('spec_set', 'autospec'):
            p = patch(MODNAME, spec=0, **{kwarg: 0})
            self.assertRaises(TypeError, p.start)
            self.assertIs(PTModule, original)


    eleza test_specs_false_instead_of_none(self):
        p = patch(MODNAME, spec=Uongo, spec_set=Uongo, autospec=Uongo)
        mock = p.start()
        jaribu:
            # no spec should have been set, so attribute access should sio fail
            mock.does_not_exist
            mock.does_not_exist = 3
        mwishowe:
            p.stop()


    eleza test_falsey_spec(self):
        kila kwarg kwenye ('spec', 'autospec', 'spec_set'):
            p = patch(MODNAME, **{kwarg: 0})
            m = p.start()
            jaribu:
                self.assertRaises(AttributeError, getattr, m, 'doesnotexit')
            mwishowe:
                p.stop()


    eleza test_spec_set_true(self):
        kila kwarg kwenye ('spec', 'autospec'):
            p = patch(MODNAME, spec_set=Kweli, **{kwarg: Kweli})
            m = p.start()
            jaribu:
                self.assertRaises(AttributeError, setattr, m,
                                  'doesnotexist', 'something')
                self.assertRaises(AttributeError, getattr, m, 'doesnotexist')
            mwishowe:
                p.stop()


    eleza test_callable_spec_as_list(self):
        spec = ('__call__',)
        p = patch(MODNAME, spec=spec)
        m = p.start()
        jaribu:
            self.assertKweli(callable(m))
        mwishowe:
            p.stop()


    eleza test_not_callable_spec_as_list(self):
        spec = ('foo', 'bar')
        p = patch(MODNAME, spec=spec)
        m = p.start()
        jaribu:
            self.assertUongo(callable(m))
        mwishowe:
            p.stop()


    eleza test_patch_stopall(self):
        unlink = os.unlink
        chdir = os.chdir
        path = os.path
        patch('os.unlink', something).start()
        patch('os.chdir', something_else).start()

        @patch('os.path')
        eleza patched(mock_path):
            patch.stopall()
            self.assertIs(os.path, mock_path)
            self.assertIs(os.unlink, unlink)
            self.assertIs(os.chdir, chdir)

        patched()
        self.assertIs(os.path, path)

    eleza test_stopall_lifo(self):
        stopped = []
        kundi thing(object):
            one = two = three = Tupu

        eleza get_patch(attribute):
            kundi mypatch(_patch):
                eleza stop(self):
                    stopped.append(attribute)
                    rudisha super(mypatch, self).stop()
            rudisha mypatch(lambda: thing, attribute, Tupu, Tupu,
                           Uongo, Tupu, Tupu, Tupu, {})
        [get_patch(val).start() kila val kwenye ("one", "two", "three")]
        patch.stopall()

        self.assertEqual(stopped, ["three", "two", "one"])


    eleza test_special_attrs(self):
        eleza foo(x=0):
            """TEST"""
            rudisha x
        ukijumuisha patch.object(foo, '__defaults__', (1, )):
            self.assertEqual(foo(), 1)
        self.assertEqual(foo(), 0)

        ukijumuisha patch.object(foo, '__doc__', "FUN"):
            self.assertEqual(foo.__doc__, "FUN")
        self.assertEqual(foo.__doc__, "TEST")

        ukijumuisha patch.object(foo, '__module__', "testpatch2"):
            self.assertEqual(foo.__module__, "testpatch2")
        self.assertEqual(foo.__module__, 'unittest.test.testmock.testpatch')

        ukijumuisha patch.object(foo, '__annotations__', dict([('s', 1, )])):
            self.assertEqual(foo.__annotations__, dict([('s', 1, )]))
        self.assertEqual(foo.__annotations__, dict())

        eleza foo(*a, x=0):
            rudisha x
        ukijumuisha patch.object(foo, '__kwdefaults__', dict([('x', 1, )])):
            self.assertEqual(foo(), 1)
        self.assertEqual(foo(), 0)

    eleza test_dotted_but_module_not_loaded(self):
        # This exercises the AttributeError branch of _dot_lookup.

        # make sure it's there
        agiza unittest.test.testmock.support
        # now make sure it's not:
        ukijumuisha patch.dict('sys.modules'):
            toa sys.modules['unittest.test.testmock.support']
            toa sys.modules['unittest.test.testmock']
            toa sys.modules['unittest.test']
            toa sys.modules['unittest']

            # now make sure we can patch based on a dotted path:
            @patch('unittest.test.testmock.support.X')
            eleza test(mock):
                pass
            test()


    eleza test_invalid_target(self):
        ukijumuisha self.assertRaises(TypeError):
            patch('')


    eleza test_cant_set_kwargs_when_passing_a_mock(self):
        @patch('unittest.test.testmock.support.X', new=object(), x=1)
        eleza test(): pass
        ukijumuisha self.assertRaises(TypeError):
            test()


ikiwa __name__ == '__main__':
    unittest.main()
