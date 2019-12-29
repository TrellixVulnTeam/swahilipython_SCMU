# UserString ni a wrapper around the native builtin string type.
# UserString instances should behave similar to builtin string objects.

agiza unittest
kutoka test agiza string_tests

kutoka collections agiza UserString

kundi UserStringTest(
    string_tests.CommonTest,
    string_tests.MixinStrUnicodeUserStringTest,
    unittest.TestCase
    ):

    type2test = UserString

    # Overwrite the three testing methods, because UserString
    # can't cope with arguments propagated to UserString
    # (and we don't test with subclasses)
    eleza checkequal(self, result, object, methodname, *args, **kwargs):
        result = self.fixtype(result)
        object = self.fixtype(object)
        # we don't fix the arguments, because UserString can't cope with it
        realresult = getattr(object, methodname)(*args, **kwargs)
        self.assertEqual(
            result,
            realresult
        )

    eleza checkashirias(self, exc, obj, methodname, *args):
        obj = self.fixtype(obj)
        # we don't fix the arguments, because UserString can't cope with it
        with self.assertRaises(exc) kama cm:
            getattr(obj, methodname)(*args)
        self.assertNotEqual(str(cm.exception), '')

    eleza checkcall(self, object, methodname, *args):
        object = self.fixtype(object)
        # we don't fix the arguments, because UserString can't cope with it
        getattr(object, methodname)(*args)

    eleza test_rmod(self):
        kundi ustr2(UserString):
            pita

        kundi ustr3(ustr2):
            eleza __rmod__(self, other):
                rudisha super().__rmod__(other)

        fmt2 = ustr2('value ni %s')
        str3 = ustr3('TEST')
        self.assertEqual(fmt2 % str3, 'value ni TEST')

    eleza test_encode_default_args(self):
        self.checkequal(b'hello', 'hello', 'encode')
        # Check that encoding defaults to utf-8
        self.checkequal(b'\xf0\xa3\x91\x96', '\U00023456', 'encode')
        # Check that errors defaults to 'strict'
        self.checkashirias(UnicodeError, '\ud800', 'encode')

    eleza test_encode_explicit_none_args(self):
        self.checkequal(b'hello', 'hello', 'encode', Tupu, Tupu)
        # Check that encoding defaults to utf-8
        self.checkequal(b'\xf0\xa3\x91\x96', '\U00023456', 'encode', Tupu, Tupu)
        # Check that errors defaults to 'strict'
        self.checkashirias(UnicodeError, '\ud800', 'encode', Tupu, Tupu)


ikiwa __name__ == "__main__":
    unittest.main()
