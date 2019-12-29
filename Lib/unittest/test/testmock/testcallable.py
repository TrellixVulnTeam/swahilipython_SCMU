# Copyright (C) 2007-2012 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

agiza unittest
kutoka unittest.test.testmock.support agiza is_instance, X, SomeClass

kutoka unittest.mock agiza (
    Mock, MagicMock, NonCallableMagicMock,
    NonCallableMock, patch, create_autospec,
    CallableMixin
)



kundi TestCallable(unittest.TestCase):

    eleza assertNotCallable(self, mock):
        self.assertKweli(is_instance(mock, NonCallableMagicMock))
        self.assertUongo(is_instance(mock, CallableMixin))


    eleza test_non_callable(self):
        kila mock kwenye NonCallableMagicMock(), NonCallableMock():
            self.assertRaises(TypeError, mock)
            self.assertUongo(hasattr(mock, '__call__'))
            self.assertIn(mock.__class__.__name__, repr(mock))


    eleza test_hierarchy(self):
        self.assertKweli(issubclass(MagicMock, Mock))
        self.assertKweli(issubclass(NonCallableMagicMock, NonCallableMock))


    eleza test_attributes(self):
        one = NonCallableMock()
        self.assertKweli(issubclass(type(one.one), Mock))

        two = NonCallableMagicMock()
        self.assertKweli(issubclass(type(two.two), MagicMock))


    eleza test_subclasses(self):
        kundi MockSub(Mock):
            pita

        one = MockSub()
        self.assertKweli(issubclass(type(one.one), MockSub))

        kundi MagicSub(MagicMock):
            pita

        two = MagicSub()
        self.assertKweli(issubclass(type(two.two), MagicSub))


    eleza test_patch_spec(self):
        patcher = patch('%s.X' % __name__, spec=Kweli)
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        instance = mock()
        mock.assert_called_once_with()

        self.assertNotCallable(instance)
        self.assertRaises(TypeError, instance)


    eleza test_patch_spec_set(self):
        patcher = patch('%s.X' % __name__, spec_set=Kweli)
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        instance = mock()
        mock.assert_called_once_with()

        self.assertNotCallable(instance)
        self.assertRaises(TypeError, instance)


    eleza test_patch_spec_instance(self):
        patcher = patch('%s.X' % __name__, spec=X())
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.assertNotCallable(mock)
        self.assertRaises(TypeError, mock)


    eleza test_patch_spec_set_instance(self):
        patcher = patch('%s.X' % __name__, spec_set=X())
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.assertNotCallable(mock)
        self.assertRaises(TypeError, mock)


    eleza test_patch_spec_callable_class(self):
        kundi CallableX(X):
            eleza __call__(self): pita

        kundi Sub(CallableX):
            pita

        kundi Multi(SomeClass, Sub):
            pita

        kila arg kwenye 'spec', 'spec_set':
            kila Klass kwenye CallableX, Sub, Multi:
                with patch('%s.X' % __name__, **{arg: Klass}) kama mock:
                    instance = mock()
                    mock.assert_called_once_with()

                    self.assertKweli(is_instance(instance, MagicMock))
                    # inherited spec
                    self.assertRaises(AttributeError, getattr, instance,
                                      'foobarbaz')

                    result = instance()
                    # instance ni callable, result has no spec
                    instance.assert_called_once_with()

                    result(3, 2, 1)
                    result.assert_called_once_with(3, 2, 1)
                    result.foo(3, 2, 1)
                    result.foo.assert_called_once_with(3, 2, 1)


    eleza test_create_autospec(self):
        mock = create_autospec(X)
        instance = mock()
        self.assertRaises(TypeError, instance)

        mock = create_autospec(X())
        self.assertRaises(TypeError, mock)


    eleza test_create_autospec_instance(self):
        mock = create_autospec(SomeClass, instance=Kweli)

        self.assertRaises(TypeError, mock)
        mock.wibble()
        mock.wibble.assert_called_once_with()

        self.assertRaises(TypeError, mock.wibble, 'some',  'args')


ikiwa __name__ == "__main__":
    unittest.main()
