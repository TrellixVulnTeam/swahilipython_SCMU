#!/usr/bin/env python3

"""
Support Eiffel-style preconditions na postconditions kila functions.

An example kila Python metaclasses.
"""

agiza unittest
kutoka types agiza FunctionType kama function

kundi EiffelBaseMetaClass(type):

    eleza __new__(meta, name, bases, dict):
        meta.convert_methods(dict)
        rudisha super(EiffelBaseMetaClass, meta).__new__(
            meta, name, bases, dict)

    @classmethod
    eleza convert_methods(cls, dict):
        """Replace functions kwenye dict ukijumuisha EiffelMethod wrappers.

        The dict ni modified kwenye place.

        If a method ends kwenye _pre ama _post, it ni removed kutoka the dict
        regardless of whether there ni a corresponding method.
        """
        # find methods ukijumuisha pre ama post conditions
        methods = []
        kila k, v kwenye dict.items():
            ikiwa k.endswith('_pre') ama k.endswith('_post'):
                assert isinstance(v, function)
            lasivyo isinstance(v, function):
                methods.append(k)
        kila m kwenye methods:
            pre = dict.get("%s_pre" % m)
            post = dict.get("%s_post" % m)
            ikiwa pre ama post:
                dict[m] = cls.make_eiffel_method(dict[m], pre, post)


kundi EiffelMetaClass1(EiffelBaseMetaClass):
    # an implementation of the "eiffel" meta kundi that uses nested functions

    @staticmethod
    eleza make_eiffel_method(func, pre, post):
        eleza method(self, *args, **kwargs):
            ikiwa pre:
                pre(self, *args, **kwargs)
            rv = func(self, *args, **kwargs)
            ikiwa post:
                post(self, rv, *args, **kwargs)
            rudisha rv

        ikiwa func.__doc__:
            method.__doc__ = func.__doc__

        rudisha method


kundi EiffelMethodWrapper:

    eleza __init__(self, inst, descr):
        self._inst = inst
        self._descr = descr

    eleza __call__(self, *args, **kwargs):
        rudisha self._descr.callmethod(self._inst, args, kwargs)


kundi EiffelDescriptor:

    eleza __init__(self, func, pre, post):
        self._func = func
        self._pre = pre
        self._post = post

        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    eleza __get__(self, obj, cls=Tupu):
        rudisha EiffelMethodWrapper(obj, self)

    eleza callmethod(self, inst, args, kwargs):
        ikiwa self._pre:
            self._pre(inst, *args, **kwargs)
        x = self._func(inst, *args, **kwargs)
        ikiwa self._post:
            self._post(inst, x, *args, **kwargs)
        rudisha x


kundi EiffelMetaClass2(EiffelBaseMetaClass):
    # an implementation of the "eiffel" meta kundi that uses descriptors

    make_eiffel_method = EiffelDescriptor


kundi Tests(unittest.TestCase):

    eleza testEiffelMetaClass1(self):
        self._test(EiffelMetaClass1)

    eleza testEiffelMetaClass2(self):
        self._test(EiffelMetaClass2)

    eleza _test(self, metaclass):
        kundi Eiffel(metaclass=metaclass):
            pita

        kundi Test(Eiffel):
            eleza m(self, arg):
                """Make it a little larger"""
                rudisha arg + 1

            eleza m2(self, arg):
                """Make it a little larger"""
                rudisha arg + 1

            eleza m2_pre(self, arg):
                assert arg > 0

            eleza m2_post(self, result, arg):
                assert result > arg

        kundi Sub(Test):
            eleza m2(self, arg):
                rudisha arg**2

            eleza m2_post(self, Result, arg):
                super(Sub, self).m2_post(Result, arg)
                assert Result < 100

        t = Test()
        self.assertEqual(t.m(1), 2)
        self.assertEqual(t.m2(1), 2)
        self.assertRaises(AssertionError, t.m2, 0)

        s = Sub()
        self.assertRaises(AssertionError, s.m2, 1)
        self.assertRaises(AssertionError, s.m2, 10)
        self.assertEqual(s.m2(5), 25)


ikiwa __name__ == "__main__":
    unittest.main()
